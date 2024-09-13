from .imports import *
from .funcs import *
from flask import Blueprint
from .user import User

clsm = Blueprint("clsm", __name__)


@clsm.route("/clsm/")
@login_required
def __index():
  user = current_user
  if not user.is_teacher:
    return redirect("/")
  l0 = fetch_users()
  return render_template("classManage.html",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"),
                         l=l0[user.id]["classes"])


@clsm.route("/clsm/create_class", methods=["post", "get"])
@login_required
def __create_class():
  user = current_user
  if not user.is_teacher and not user.is_asistnt:
    return render_template("redirects.html",
                           link="/",
                           letter="非教師身分，重新導向至首頁",
                           header=render_template("header.html"),
                           footer=render_template("footer.html"),
                           Users=Users)
  codes = fetch_json("static/jsons/code.json")
  if request.method.lower() == "post":
    form = request.form.to_dict()
    warn = ""
    if not form.get("cls"): warn = "未輸入班級號"
    elif not form.get("dep"): warn = "未選擇班級科別"
    elif form.get("dep") == "other" and not form["other"]: warn = "未填寫其他"
    elif form["cls"] in codes:
      warn = "班級已存在，請查看下方清單或使用瀏覽器搜尋功能"
    if warn:
      return render_template("create_class.html",
                             header=render_template("header.html"),
                             footer=render_template("footer.html"),
                             cls=codes.items(),
                             des=[i["department"] for i in codes.values()],
                             warn=warn,
                             Users=User.users)

    code = str(uuid.uuid4())[:8]
    dep = form.get("dep")
    if dep == "other":
      dep = form["other"]
    codes[code] = {
      "class": form["cls"],
      "department": dep,
      "year": str(int(get_today("%Y")) - 1911),
      "adder": user.id
    }
    users = fetch_users()
    if not form["cls"] in users[user.id]["classes"]:
      users[user.id]["classes"].append(form["cls"])
    users.supd()
    codes.supd()
    write_json(f"static/jsons/tasks/{form['cls']}.json", {})
    session["msg"] = f"已新增班級{form['cls']}，代碼{code}"
    return redirect("/")
  User.refresh_users()
  return render_template("create_class.html",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"),
                         cls=codes.items(),
                         des=set(i["department"] for i in codes.values()),
                         warn="",
                         Users=User.users)


# @clsm.route("/clsm/create_tcode", methods=["post", "get"])
# @login_required
# def __create_tcode():
#   user = current_user
#   if not user.is_teacher and not user.is_asistnt:
#     return render_template("redirects.html",
#                            link="/",
#                            letter="非管理員身分，重新導向至首頁",
#                            header=render_template("header.html"),
#                            footer=render_template("footer.html"),
#                            Users=Users)
#   codes = fetch_json("static/jsons/tcode.json")
#   if request.method.lower() == "post":
#     form = request.form.to_dict()
#     warn = ""
#     if not form.get("dep"): warn = "未選擇教師科別"
#     elif form.get("dep") == "other" and not form["other"]: warn = "未填寫其他"
#     elif form["cls"] in codes:
#       warn = "班級已存在，請查看下方清單或使用瀏覽器搜尋功能"
#     if warn:
#       return render_template("create_class.html",
#                              header=render_template("header.html"),
#                              footer=render_template("footer.html"),
#                              cls=codes.items(),
#                              des=[i["department"] for i in codes.values()],
#                              warn=warn)

#     code = str(uuid.uuid4())[:8]
#     dep = form.get("dep")
#     if dep == "other":
#       dep = form["other"]
#     codes[code] = {
#       "class": form["cls"],
#       "department": dep,
#       "year": str(int(get_today("%Y")) - 1911),
#       "adder": user.id
#     }
#     users = fetch_users()
#     if not form["cls"] in users[user.id]["classes"]:
#       users[user.id]["classes"].append(form["cls"])
#     with open("static/jsons/account.json", mode="w") as wf:
#       fcntl.flock(wf, fcntl.LOCK_EX)
#       json.dump(users, wf, indent=2)
#       fcntl.flock(wf, fcntl.LOCK_UN)
#       wf.close()
#     with open("static/jsons/code.json", mode="w") as wf:
#       fcntl.flock(wf, fcntl.LOCK_EX)
#       json.dump(codes, wf, indent=2)
#       fcntl.flock(wf, fcntl.LOCK_UN)
#       wf.close()
#     with open(f"static/jsons/tasks/{form['cls']}.json", mode="w") as wf:
#       fcntl.flock(wf, fcntl.LOCK_EX)
#       json.dump({}, wf, indent=2)
#       fcntl.flock(wf, fcntl.LOCK_UN)
#       wf.close()
#     session["msg"] = f"已新增班級{form['cls']}，代碼{code}"
#     return redirect("/")
#   User.refresh_users()
#   return render_template("create_class.html",
#                          header=render_template("header.html"),
#                          footer=render_template("footer.html"),
#                          cls=codes.items(),
#                          des=[i["department"] for i in codes.values()],
#                          warn="",
#                          Users=User.users)


@clsm.route("/clsm/class<c>", methods=["post", "get"])
@login_required
def __clsManage(c):
  user = current_user
  if not user.is_teacher:
    notify.set("非教師身分", "forbidden_reason")
    return redirect("/")
  if not c in user.classes:
    notify.set(f"您尚未加入班級 {c}", "forbidden_reason")
    return redirect("/clsm/")
  codes = fetch_json("static/jsons/code.json")
  adders = {i["class"]: i["adder"] for i in codes.values()}
  cls_code = {i["class"]: k for k, i in codes.items()}
  if not c in adders:
    notify.set("找不到該班級", "forbidden_reason")
    return redirect("/clsm/")
  cls_sche = fetch_json(f"static/jsons/tasks/{c}.json")
  users = fetch_users()
  if request.method.lower() == "post":
    form = request.form.to_dict()
    new = form["new"]
    if not new:
      notify.set("請填寫新班級名稱", "data_error")
      return redirect(f"/clsm/class{c}")
    for fn in os.listdir("static/jsons/tasks/"):
      if f"{new}.json" == fn:
        notify.set("該班已存在", "data_error")
        return redirect(f"/clsm/class{c}")
    codes[cls_code[c]]["class"] = new
    os.rename(f"static/jsons/tasks/{c}.json", f"static/jsons/tasks/{new}.json")
    users = fetch_users()
    for uid, u in users.items():
      if u.get("class") == c: users[uid]["class"] = new
      elif c in u.get("classes", []):
        users[uid]["classes"][users[uid]["classes"].index(c)] = new
    users.supd()
    codes.supd()
    if c in os.listdir("static/files"):
      os.rename(f"static/files/{c}", f"static/files/{new}")
    return redirect(f"/clsm/class{new}")

  return render_template(
    "clsManage.html",
    header=render_template("header.html"),
    footer=render_template("footer.html"),
    cls=c,
    cls_sche=cls_sche,
    tchrs=sorted([(j, i) for j, i in users.items()
                  if i.get("role") == "tch" and c in i.get("classes")],
                 key=lambda x: x[1].get("fullname")),
    stus=sorted([(j, i) for j, i in users.items()
                 if i.get("role") == "stu" and c == i.get("class")],
                key=lambda x: x[1].get("number")))
