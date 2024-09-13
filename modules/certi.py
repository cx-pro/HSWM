from .imports import *
from .funcs import *
from flask import Blueprint

certi = Blueprint("certi", __name__)


@certi.route("/certi/certificate", methods=["get", "post"])
def __certificate():
  value = dict()
  value["科別"] = ""
  value["年"] = ""
  value["班"] = ""
  value["學生"] = ""
  value["獎項"] = ""
  value["處室簡稱"] = ""
  value["文號"] = ""
  value["日期"] = ""
  user = current_user
  uid=user.id if user.is_authenticated else user.certi_id

  if (not current_user.is_teacher) and current_user.is_authenticated: return redirect("/")
  if request.method.lower() == "post":
    file = request.files.get('multid')
    if file:
      form = request.form.to_dict()
      file.save("static/ods/" + secure_filename(file.filename))
      session["uploaded_multid"] = "static/ods/" + secure_filename(
        file.filename)
      sheets = pyexcel_ods3.get_data(session["uploaded_multid"])
      if not sheets.get("資料"):
        return render_template("redirects.html",
                               link="/certi/certificate",
                               letter="資料格式錯誤")
      else:
        data = sheets.get("資料")
        jdata = fetch_json(f"static/jsons/pdfs/{uid}.json")
        for fdata in data:
          if data.index(fdata) == 0: continue
          if len(fdata) == 0: continue
          if not len(fdata) == 7:
            return render_template("redirects.html",
                                   link="/certi/certificate",
                                   letter="資料格式錯誤")
          filename = pdf({
            i: j
            for i, j in zip(["科別", "年", "班", "學生", "獎項", "處室簡稱", "文號","日期"], fdata)
          },uid) if not form.get("no-back", False) else pdfp({
            i: j
            for i, j in zip(["科別", "年", "班", "學生", "獎項", "處室簡稱", "文號","日期"], fdata)
          },uid)
          os.rename(filename, f"static/pdfs/{filename}")
          ind = (max(list(map(int, jdata.keys()))) + 1) if jdata else 0

          pdf_data={"time": get_today("%Y-%m-%d"), "filename": filename}
          if not user.is_authenticated:
            pdf_data["user_ip"]=get_ip(request)
          jdata[str(ind)] = pdf_data
        jdata.supd()
        os.remove(session.get("uploaded_multid"))
        
        uids=fetch_list(f"static/jsons/anonymous_pdf.json")
        uids.append(uid)
        uids.supd()

        return redirect("/certi/")

    else:
      fdata = request.form.to_dict()
      j2 = value.keys()
      if not fdata.get("科別"):
        value["科別"] = "此欄不得為空"
      if not fdata.get("年"):
        value["年"] = "此欄不得為空"
      if not fdata.get("班"):
        value["班"] = "此欄不得為空"
      if not fdata.get("學生"):
        value["學生"] = "此欄不得為空"
      if not fdata.get("獎項"):
        value["獎項"] = "此欄不得為空"
      if not fdata.get("處室簡稱"):
        value["處室簡稱"] = "此欄不得為空"
      if not fdata.get("文號"):
        value["文號"] = "此欄不得為空"
      if not fdata.get("日期"):
        value["文號"] = "此欄不得為空"
      if "此欄不得為空" in value.values():
        return render_template("certi.html",
                               value=value,
                               header=render_template("header.html"),
                               footer=render_template("footer.html"))
      filename = pdf(fdata,uid) if (not fdata.get("no-back", False)) and user.is_authenticated else pdfp(fdata,uid)
      os.rename(filename, f"static/pdfs/{filename}")
      pdf_data={"time": get_today("%Y-%m-%d"), "filename": filename}
      if not user.is_authenticated:
        pdf_data["user_ip"]=get_ip(request)
      wdata = dict()
      wdata["0"] = pdf_data

      jdata = fetch_json(f"static/jsons/pdfs/{uid}.json")
      if not jdata:
        jdata.upd(wdata)
      else:
        km = max([int(i) for i in jdata.keys()]) + 1
        jdata[str(km)] = wdata["0"]
        jdata.supd()
        
      uids=fetch_list(f"static/jsons/anonymous_pdf.json")
      uids.append(uid)
      uids.supd()

      return render_template("pdfr.html",
                             link="/pdfs/" + filename,
                             header=render_template("header.html"),
                             footer=render_template("footer.html"))

  return render_template("certi.html",
                         value=value,
                         header=render_template("header.html"),
                         footer=render_template("footer.html"))


@certi.route("/certi/",methods=["post","get"])
@certi.route("/certi/pdfl",methods=["post","get"])
def __pdfl():
  user = current_user
  if (not user.is_teacher) and user.is_authenticated:
    return redirect("/")
  if request.method.lower()=="post":
    uid=request.form.get("uid","")
    if not uid:
      return render_template("redirects.html",
                              link="/certi/pdfl",
                              letter="未輸入序號")
    uids=fetch_list(f"static/jsons/anonymous_pdf.json")
    if not uid in uids:
      return render_template("redirects.html",
                              link="/certi/pdfl",
                              letter="序號不存在")
    user.certi_id=uid
    

    
      
  uid=user.id if current_user.is_authenticated else user.certi_id
    
  cd = fetch_json(f"static/jsons/pdfs/{uid}.json")
  for key, value in cd.items():
    filename = value["filename"]
    cd[key]["filename"] = filename[:len(uid)]
  data = fetch_json(f"static/jsons/pdfs/{uid}.json")

  return render_template("pdfl.html",
                         data=data,
                         c=not uid in [i["filename"] for i in cd.values()],
                         header=render_template("header.html"),
                         footer=render_template("footer.html"))


@certi.route("/certi/dc", methods=["get", "post"])
def __dc():
  id = request.args.get("id")
  user = current_user
  uid=user.id if user.is_authenticated else user.certi_id
  if request.method.lower() == "post":
    data = fetch_json(f"static/jsons/pdfs/{uid}.json")
    if not str(id) in data: return redirect("/certi/")
    os.remove(f"static/pdfs/{data[str(id)]['filename']}")
    del data[str(id)]
    data.supd()
    return redirect("/certi/pdfl")
  return render_template("dc.html",
                         id=id,
                         header=render_template("header.html"),
                         footer=render_template("footer.html"))


@certi.route("/certi/multi_data")
def __multi_data_download():
  return send_from_directory("static/ods/example/", "example.ods")
