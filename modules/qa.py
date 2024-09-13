from .imports import *
from .funcs import *
from flask import Blueprint

qa = Blueprint("qa", __name__)


@qa.route("/qa")
def __qaredirect():
  if not session.get("user_pic"):
    session["user_pic"] = "profile_pics/default/Default_Avatar.webp"
  return redirect("/qa/")


@qa.route("/qa/")
@qa.route("/qa/index")
def __qai():
  if not session.get("user_pic"):
    session["user_pic"] = "profile_pics/default/Default_Avatar.webp"
  return render_template("qai.html",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"))


@qa.route("/qa/qas")
def __qahash():
  if not session.get("user_pic"):
    session["user_pic"] = "profile_pics/default/Default_Avatar.webp"
  data = fetch_json("static/jsons/qas.json")
  classes = list(sorted(list(set([i["cls"] for i in data.values()]))))
  classes.insert(0, "全部")
  return render_template("qas.html",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"),
                         classes=classes)


def check_permission(d: list):
  try:
    if "*" in d:
      return True
    elif current_user.is_teacher:
      for i in d:
        if i in current_user.classes:
          return True
    elif current_user.is_student:
      return current_user.clas in d
  except AttributeError:
    None
  return False


def __rmid(d: dict):
  del d["id"]
  return d


@qa.route("/qa/<name>")
def __qaall(name):
  data0 = fetch_json("static/jsons/qas.json")
  l = list(set([i["cls"] for i in data0.values()]))
  if name == "全部":
    data = data0
  else:
    data = {i: j for i, j in data0.items() if j["cls"] == name}
  if name in l:
    l = [name]
  data1 = dict()
  for k in l:
    for i, j in data.items():
      if j["cls"] == k:
        j["id"] = i
        data1[i] = j
      elif k == "其他" and j["cls"] not in l[:-1]:
        j["id"] = i
        data1[i] = j

  data2 = {
    nid: __rmid(value)
    for nid, value in {
      n["id"]: n
      for k, n in dict(
        reversed(
          sorted(list({j["date"] + i: j
                       for i, j in data1.items()}.items())))).items()
    }.items() if check_permission(value["restricted"])
  }

  return render_template(f"全部.html", data=data2)


@qa.route("/qa/q<id>")
def __qacontnt(id):
  data = fetch_json("static/jsons/qas.json")[id]

  def check_permission(d: list):
    try:
      if "*" in d:
        return True
      elif current_user.is_teacher:
        for i in d:
          if i in current_user.classes:
            return True
      elif current_user.is_student:
        return current_user.clas in d
    except AttributeError:
      None
    return False

  if not check_permission(data["restricted"]):
    return render_template("redirects.html",
                           link="/qa/qas",
                           letter="此問題為私人狀態，權限不足。若此訊息不該出現，請洽問題發布者。",
                           header=render_template("header.html"),
                           footer=render_template("footer.html"))
  data["replys"] = list(
    dict(
      reversed(
        sorted(
          list({
            i["date"] + str(data["replys"].index(i)): i
            for i in data["replys"]
          }.items())))).values())
  files_map = list()
  for i in data["files"]:
    if imghdr.what(i) or get_extension(i) in imgs_files:
      files_map.append(i)
  return render_template("qcontnt.html",
                         data=data,
                         id=id,
                         header=render_template("header.html"),
                         footer=render_template("footer.html"),
                         filem=files_map)


@qa.route("/qa/describe")
def __describe():
  return render_template("describe.html")


@qa.route("/qa/search", methods=["post", "get"])
def __search():
  data = fetch_json("static/jsons/qas.json")
  id = request.args.get("id")
  if id in data:
    return render_template("全部.html", data={id: data[id]})
  search0 = request.form.get("search").lower()
  searchs = search0.split()
  data2 = dict()
  queue = list()
  for search in searchs:
    for key, value in data.items():
      for i in [
          value["title"], value["content"], value["cls"],
        [i["content"] for i in value["replys"]]
      ]:
        if (not isinstance(i, list)) and (search
                                          in i.lower()) and (not key in queue):
          queue.append(key)
        elif isinstance(i, list):
          for j in i:
            if search in j.lower() and (not key in queue):
              queue.append(key)

  if queue:
    data2 = {
      i: data[i]
      for i in set(queue) if check_permission(data[i]["restricted"])
    }
  return render_template("全部.html", data=data2)


def __get_max(d: dict):
  biggest = 0
  for i, j in d.items:
    if int(i) > biggest: biggest = int(i)
  return str(biggest + 1)()


@qa.route("/qa/add", methods=["get", "post"])
@login_required
def __add():
  m = {"stu": "學生", "tch": "教師", "adm": "管理員"}
  user = current_user
  ex = {
    "title": "",
    "content": "",
    "author": "",
    "user": "",
    "date": "",
    "cls": "",
    "replys": [],
    "files": [],
    "restricted": []
  }
  if request.method.lower() == "post":
    form = request.form.to_dict()
    msg = list()
    if not form.get("title"):
      msg.append("標題不可為空")
    if not form.get("content"):
      msg.append("內容不可為空")
    if not form.get("cls"):
      msg.append("類別不可為空")
    if form.get("cls") == "other" and not form.get("other"):
      msg.append("請輸入「其他」欄位")
    if msg:
      return render_template("qadd.html", msg=msg)
    q = ex
    accs = fetch_users()
    user1 = current_user.id
    author = "匿名" + m[accs[current_user.id]["role"]]
    if form.get("anonymous") == "false":
      user1 = current_user.id
      author = accs[current_user.id]["fullname"]
    q["title"] = form.get("title")
    q["content"] = form.get("content")
    q["cls"] = form.get("cls") if form.get("cls") != "other" else form.get(
      "other")
    q["date"] = get_today("%Y-%m-%d")
    q["user"] = user1
    q["author"] = author
    q["restricted"] = request.form.getlist(
      "restricted") if request.form.getlist("restricted") else ["*"]
    jdata = fetch_json("static/jsons/qas.json")

    id = __get_max(jdata)
    files = request.files.getlist("qfiles")
    if files[-1].filename:
      for file in files:
        if not id in os.listdir("static/qfiles/"):
          os.mkdir(f"static/qfiles/{id}")
        filename = f"static/qfiles/{id}/{secure_filename(file.filename)}"
        file.save(filename)
        q["files"].append(filename)
    jdata[id] = q
    jdata.supd()
    return redirect(f"/qa/qas?defa=/qa/search?id={id}")
  data = fetch_json("static/jsons/qas.json")
  classes = list([i["cls"] for i in data.values()])
  for i in ["國文", "英文", "數學", "社會", "自然"]:
    if not i in classes:
      classes.append(i)
  return render_template("qadd.html", classes=sorted(set(classes)))


@qa.route("/qa/mys")
@login_required
def __mys():
  user = current_user
  data0 = fetch_json("static/jsons/qas.json")
  data = {i: j for i, j in data0.items() if j["user"] == user.id}
  return render_template("mys.html", data=data)


@qa.route("/qa/mysq")
@login_required
def __mysq():
  user = current_user
  if not user.is_teacher:
    return redirect("/qa/qas")
  data0 = fetch_json("static/jsons/qas.json")
  users = fetch_users()
  data = {
    i: j
    for i, j in data0.items() if users[j["user"]].get("class") in user.classes
  }
  return render_template("mysq.html", data=data, users=users)


@qa.route("/qa/e<id>", methods=["get", "post"])
@login_required
def __qedit(id):
  user = current_user
  data = fetch_json("static/jsons/qas.json")
  if request.method.lower() == "post":
    if request.form.get("delete_file"):
      file = request.form.get("delete_file")
      if file in data[id]["files"]:
        os.remove(file)
        data[id]["files"].remove(file)
        data.supd()
      return ""
    form = request.form.to_dict()
    warn = list()
    if not form.get("title"):
      warn.append("標題不可為空")
    if not form.get("content"):
      warn.append("內容不可為空")
    if warn:
      data[id]["title"] = form.get("title")
      data[id]["content"] = form.get("content")
      data[id]["cls"] = form.get("cls")
      data[id]["date"] = get_today("%Y-%m-%d")
      return render_template("qedit.html", data=data[id], id=id, warn=warn)
    data = fetch_json("static/jsons/qas.json")
    data[id]["title"] = form.get("title")
    data[id]["content"] = form.get("content")
    data[id]["cls"] = form.get(
      "cls") if not form.get("cls") == "other" else form.get("other")
    data[id]["date"] = get_today("%Y-%m-%d")
    files = request.files.getlist("uploaded_files")
    if files[-1].filename:
      for file in files:
        if not id in os.listdir("static/qfiles/"):
          os.mkdir(f"static/qfiles/{id}")
        filename = f"static/qfiles/{id}/{secure_filename(file.filename)}"
        if not secure_filename(
            file.filename) in os.listdir(f"static/qfiles/{id}"):
          file.save(filename)
          data[id]["files"].append(filename)
    data.supd()
    return redirect("/qa/qas?defa=/qa/mys")

  files_map = list()
  for i in data[id]["files"]:
    if imghdr.what(i) or get_extension(i) in imgs_files:
      files_map.append(i)
  return render_template("qedit.html",
                         data=data[id],
                         id=id,
                         filem=files_map,
                         classes=list(set([i["cls"] for i in data.values()])))


@qa.route("/qa/d<id>", methods=["post"])
@login_required
def __d(id):
  user = current_user
  data = fetch_json("static/jsons/qas.json")
  if os.path.exists(f"static/qfiles/{id}"):
    for i in os.listdir(f"static/qfiles/{id}"):
      os.remove(f"static/qfiles/{id}/{i}")
    os.rmdir(f"static/qfiles/{id}")
  del data[id]
  data.supd()
  data = fetch_json("static/jsons/qas.json")
  return render_template(
    "mys.html", data={i: j
                      for i, j in data.items() if j["user"] == user.id})


@qa.route("/qa/set_s", methods=["post"])
def set_s():
  session["dark"] = request.form.get("mode")
  if current_user.is_qrcUser:
    old_set = current_user.settings
    old_set["theme"] = request.form.get("mode")
    current_user.settings = old_set
    return "OK"
  if current_user.is_authenticated:
    if current_user.settings:
      if not current_user.settings.get("theme") == request.form.get("mode"):
        users = fetch_json("static/jsons/account.json")
        users[current_user.id]["settings"]["theme"] = request.form.get("mode")
        users.supd()
  return ""


@qa.route("/qa/reply<id>", methods=["post"])
@login_required
def __reply(id):
  user = current_user
  form = request.form.to_dict()
  data = fetch_json("static/jsons/qas.json")
  users = fetch_users()
  data[id]["replys"].append({
    "author": users[user.id]["fullname"],
    "content": form.get("reply"),
    "date": get_today("%Y-%m-%d"),
    "user": user.id
  })
  data.supd()
  return "OK"


@qa.route("/qa/myreply", methods=["get"])
@login_required
def __myreply():
  user = current_user
  data = fetch_json("static/jsons/qas.json")
  replys = dict()
  for b, j in data.items():
    for k in j["replys"]:
      i = k["date"]
      if not k["user"] == current_user.id:
        continue
      if not i in replys.keys():
        replys[i] = list()
      k["id"] = b
      replys[i].append(k)
  return render_template("reply.html",
                         data=dict(reversed(sorted(list(
                           replys.items())))).items(),
                         data2=data)


@qa.route("/qa/mysr", methods=["get"])
@login_required
def __mysr():
  user = current_user
  if not user.is_teacher:
    return redirect("/qa/qas")
  data = fetch_json("static/jsons/qas.json")
  users = fetch_users()
  replys = dict()
  for b, j in data.items():
    for k in j["replys"]:
      i = k["date"]
      if not users[k["user"]].get("class") in user.classes:
        continue
      if not i in replys.keys():
        replys[i] = list()
      k["id"] = b
      replys[i].append(k)
  return render_template("mysr.html",
                         data=dict(reversed(sorted(list(
                           replys.items())))).items(),
                         data2=data,
                         users=users)


@qa.route("/qa/rq<id>", methods=["post"])
@login_required
def __rq(id):
  data = fetch_json("static/jsons/qas.json")
  ri = request.form.get("ri")
  c = request.form.get("content")
  reported = request.form.get("reported")
  rq = fetch_json("static/jsons/rq.json")
  if ri:
    ind = id + "-" + ri
    if not ind in rq.keys():
      rq[ind] = list()
    rq[ind].append({
      "date": get_today("%Y-%m-%d"),
      "content": c,
      "user": current_user.id,
      "reported": reported
    })
  else:
    ind = id
    if not ind in rq.keys():
      rq[ind] = list()
    rq[ind].append({
      "date": get_today("%Y-%m-%d"),
      "content": c,
      "user": current_user.id,
      "reported": reported
    })
  rq.supd()
  return "檢舉成功"


@qa.route("/qa/reported")
@login_required
def __reported():
  user = current_user
  if not user.is_teacher:
    return redirect("/qa/qas")
  data = fetch_json("static/jsons/rq.json")
  qas = fetch_json("static/jsons/qas.json")
  users = fetch_users()
  for k1, v1 in data.items():
    for v2 in v1:
      if users[data[k1][v1.index(v2)]["user"]].get("class") in user.classes:
        continue
      del data[k1][v1.index(v2)]
  return render_template("reported.html", data=data, users=users)


@qa.route("/qa/redit<id>", methods=["post"])
@login_required
def __redit(id: str):
  ind = int(request.args.get("index"))
  if not ind and ind != 0:
    return redirect(request.referer)
  data = fetch_json(f"static/jsons/qas.json")
  if not data[id]["replys"][ind]["user"] == current_user.id:
    return redirect("/qa/qas")
  data[id]["replys"][ind]["content"] = request.form.get("content")
  data[id]["replys"][ind]["date"] = get_today("%Y-%m-%d")
  data.supd()
  return "OK"


@qa.route("/qa/rdel<id>", methods=["post"])
@login_required
def __rdel(id: str):
  ind = int(request.args.get("index"))
  if not ind and ind != 0:
    return redirect("/qa/qas")
  data = fetch_json(f"static/jsons/qas.json")
  if not data[id]["replys"][ind]["user"] == current_user.id:
    return redirect("/qa/qas")
  del data[id]["replys"][ind]
  data.supd()
  return "OK"


@qa.route("/qa/rate")
@login_required
def __rating():
  user = current_user
  cls = user.classes or [request.args.get("cls")]
  if not user.is_teacher:
    return redirect("/qa/qas")
  data = fetch_json("static/jsons/qas.json")
  users = fetch_users()
  replys = dict()
  for b, j in data.items():
    for k in j["replys"]:
      i = k["date"]
      if (not users[k["user"]]["role"]
          == "stu") or (not users[k["user"]].get("class") in user.classes
                        or not users[k["user"]].get("class") in cls):
        continue
      if not i in replys:
        replys[i] = []
      k["id"] = b
      replys[i].append(k)
  data3 = {
    i: j["sum"]
    for i, j in sorted(fetch_json("static/jsons/sp.json").items(),
                       key=lambda x: x[1]["sum"],
                       reverse=True) if users[i].get("class") in cls
  }

  return render_template("rate.html",
                         data=dict(sorted(replys.items(), reverse=True)),
                         data2=data,
                         users=users,
                         data3=data3)


@qa.route("/qa/padd<id>-<ind>", methods=["post"])
@login_required
def __padd(id, ind):
  user = current_user
  if not user.is_teacher: return redirect("/qa/qas")
  if not (request.form.get("reason") != "" and request.form.get("count")):
    abort(422)
    return
  data = fetch_json("static/jsons/sp.json")
  qas = fetch_json("static/jsons/qas.json")
  print(data[qas[id]["user"]]["sum"])
  data[qas[id]["user"]]["sum"] += int(request.form.get("count"))
  data[qas[id]["user"]]["entry"].append({
    "change":
    int(request.form.get("count")),
    "reason":
    request.form.get("reason"),
    "time":
    get_today("%Y-%m-%d %H:%M:%S")
  })
  data.supd()
  return "ok"
