from .imports import *
from .funcs import *
from flask import Blueprint
from .user import User

tskn = Blueprint("tskn", __name__)


@tskn.route("/tskn/")
@tskn.route("/tskn/classes")
@login_required
def __classes():
  user = current_user

  if not user.is_teacher and not user.is_asistnt: return redirect("/")
  if user.is_asistnt: return redirect(f"/tskn/class{user.clas}")
  return render_template("classes.html",
                         classes=user.classes,
                         header=render_template("header.html"),
                         footer=render_template("footer.html"),
                         Users=User.refresh_users())


@tskn.route("/tskn/calendar<c>")
@login_required
def __calendar(c):
  user = current_user
  year = request.args.get("y")
  month = request.args.get("m")
  if not year: year = str(int(get_today("%Y")))
  if not month: month = str(int(get_today("%m")))
  if not user.is_teacher and not user.is_asistnt:
    return render_template("redirects.html",
                           link="/",
                           letter="非教師身分，重新導向至首頁",
                           header=render_template("header.html"),
                           footer=render_template("footer.html"),
                           Users=User.refresh_users())
  if user.is_teacher and c in user.classes and f"{c}.json" in os.listdir(
      "static/jsons/tasks/"):
    data = fetch_json(f"static/jsons/tasks/{c}.json")
  elif user.is_asistnt and c == user.clas:
    data = fetch_json(f"static/jsons/tasks/{c}.json")
  else:
    return render_template("error.html",
                           content="發生錯誤!若有問題請回報管理員",
                           header=render_template("header.html"),
                           footer=render_template("footer.html"),
                           Users=User.refresh_users())
  dl = dict()
  mds = list(calen.itermonthdates(int(year), int(month)))
  data1 = {}
  for k1, v1 in data.items():
    for k2, v2 in v1.items():
      if datetime.datetime.strptime(v2["end_date"], "%Y-%m-%d").date() in mds:
        if not v2["end_date"] in dl: dl[v2["end_date"]] = list()
        dl[v2["end_date"]].append(f"{k1}-{k2}")
        data1[f"{k1}-{k2}"] = v2
  tks = []
  for i in mds:
    if datetime.datetime.strftime(i, "%Y-%m-%d") in dl:
      tks.append((datetime.datetime.strftime(i, "%Y-%m-%d"),
                  dl[datetime.datetime.strftime(i, "%Y-%m-%d")]))
    else:
      tks.append([datetime.datetime.strftime(i, "%Y-%m-%d")])

  return render_template("calendar.html",
                         y=year,
                         m=month,
                         tks=tks,
                         task=data1,
                         cls=c,
                         todaya={i.upper(): j
                                 for i, j in weekdays.items()}[get_today()],
                         today=get_today("%Y-%m-%d"))


@tskn.route("/tskn/class<c>")
@login_required
def __tasking(c):
  user = current_user
  if not user.is_teacher and not user.is_asistnt:
    return render_template("redirects.html",
                           link="/",
                           letter="非教師身分，重新導向至首頁",
                           header=render_template("header.html"),
                           footer=render_template("footer.html"),
                           Users=User.refresh_users())
  task = dict()
  for i in cls_id:
    for j in i:
      task[j] = False
  if user.is_teacher and c in user.classes and f"{c}.json" in os.listdir(
      "static/jsons/tasks/"):
    data0 = fetch_json(f"static/jsons/tasks/{c}.json")
  elif user.is_asistnt and c == user.clas:
    data0 = fetch_json(f"static/jsons/tasks/{c}.json")
  else:
    return render_template("error.html",
                           content="發生錯誤!若有問題請回報管理員",
                           header=render_template("header.html"),
                           footer=render_template("footer.html"),
                           Users=User.refresh_users())
  data = dict()
  for k1, v1 in data0.items():
    for k2, v2 in v1.items():
      if v2["end_date"].split("-")[-1] in week_dates():
        if not k1 in data:
          data[k1] = dict()
        data[k1][k2] = v2
  for key in data.keys():
    task[int(key)] = True
  task_bools = list()
  cls_id2 = [list(range(i, i + 7)) for i in range(0, 77, 7)]
  for i in cls_id2:
    for j in range(7):
      i[j] = "" if task[i[j]] else "hidden"
    task_bools.append(i)
  return render_template("scheduling.html",
                         l=zip(day, day_bools),
                         cls=zip(cls, cls_id, task_bools),
                         next=c,
                         header=render_template("header.html"),
                         footer=render_template("footer.html"),
                         Users=User.refresh_users(),
                         week_date=week_dates,
                         days=day)


@tskn.route("/tskn/edit", methods=["get", "post"])
@login_required
def __edit():
  id = request.args.get("id")
  ems = session.pop("ems", "")
  c = request.args.get("class")
  user = current_user
  if not user.is_teacher and not user.is_asistnt:
    return render_template("redirects.html",
                           link="/index",
                           letter="非教師身分，重新導向至首頁",
                           header=render_template("header.html"),
                           footer=render_template("footer.html"),
                           Users=User.refresh_users())
  if (not c) or ((not id) and (not id == 0)):
    return render_template("redirects.html",
                           link=request.referrer,
                           letter="連結錯誤!重新導向至前頁",
                           header=render_template("header.html"),
                           footer=render_template("footer.html"),
                           Users=User.refresh_users())
  if user.is_teacher and not c in user.classes or user.is_asistnt and c != user.clas:
    return render_template("redirects.html",
                           link=request.referrer,
                           letter="您沒有指導這個班級!重新導向至前頁",
                           header=render_template("header.html"),
                           footer=render_template("footer.html"),
                           Users=User.refresh_users())
  jdata = fetch_json(f"static/jsons/tasks/{c}.json")
  jdata0 = deepcopy(jdata)
  files_map = list()
  for i in jdata[str(id)].values():
    if "files" in i:
      for j in i["files"]:
        if imghdr.what(j) or get_extension(j) in imgs_files:
          files_map.append(j)

  #for a, b in jdata.items():
  #  for key, value in b.items():
  #    value["start_time"] = get_today(format="%Y-%m-%d %H:%M:%S")
  if request.method.lower() == "post":
    edit = request.form.to_dict().copy()
    User.refresh_users()
    if "tasker" in jdata0[str(id)][edit["index"]]:
      if jdata0[str(id)][edit["index"]]["tasker"] != user.id:
        return render_template("edit.html",
                               id=id,
                               cls=c,
                               items=jdata[str(id)].items(),
                               message="非該作業指派人",
                               header=render_template("header.html"),
                               footer=render_template("footer.html"),
                               Users=fetch_users(),
                               filem=files_map)
    if "delete_file" in edit:
      if not edit["delete_file"]:
        return render_template("edit.html",
                               id=id,
                               cls=c,
                               items=jdata[str(id)].items(),
                               message="發生錯誤，請通知管理員",
                               header=render_template("header.html"),
                               footer=render_template("footer.html"),
                               Users=fetch_users(),
                               filem=files_map)
      pos0, path = edit["delete_file"].split("@")
      c, id, ind = pos0.split("-")
      if path in jdata[id][str(ind)].get("files"):
        try:
          os.remove(path)
        except:
          None
        jdata[id][str(ind)]["files"].remove(path)
        write_json(f"static/jsons/tasks/{c}.json", jdata)
      return redirect(request.full_path)

    for i in edit.keys():
      if not edit[i]:
        return render_template("edit.html",
                               id=id,
                               cls=c,
                               items=jdata[str(id)].items(),
                               message="不得有資料為空",
                               header=render_template("header.html"),
                               footer=render_template("footer.html"),
                               Users=User.refresh_users(),
                               filem=files_map)
    pvalue = deepcopy(edit)
    del pvalue["index"]
    pvalue["start_time"] = get_today(format="%Y-%m-%d %H:%M")
    pvalue["tasker"] = user.id
    if "files" in jdata[str(id)][edit["index"]]:
      pvalue["files"] = jdata[str(id)][edit["index"]]["files"]
    day = weekdays[datetime.datetime.strptime(edit["end_date"],
                                              "%Y-%m-%d").strftime("%a")]
    id = str(maps[edit["end_time"]][day])
    m = edit["index"]
    files = request.files.getlist("uploaded_files")
    if files[-1].filename:
      for file in files:
        if not c in os.listdir("static/files/") and not os.path.exists(
            f"static/files/{c}"):
          os.mkdir(f"static/files/{c}")
        if not id in os.listdir(f"static/files/{c}") and not os.path.exists(
            f"static/files/{c}/{id}"):
          os.mkdir(f"static/files/{c}/{id}")
        if not m in os.listdir(
            f"static/files/{c}/{id}") and not os.path.exists(
              f"static/files/{c}/{id}/{m}"):
          os.mkdir(f"static/files/{c}/{id}/{m}")
        filename = f"static/files/{c}/{id}/{m}/{secure_filename(file.filename)}"
        curename = secure_filename(file.filename)
        if jdata[str(id)][edit["index"]].get("files"):
          if curename in os.listdir(f"static/files/{c}/{id}/{m}/"):
            return render_template("edit.html",
                                   id=id,
                                   cls=c,
                                   items=jdata[str(id)].items(),
                                   message="檔案已存在",
                                   header=render_template("header.html"),
                                   footer=render_template("footer.html"),
                                   Users=User.refresh_users(),
                                   filem=files_map)
        file.save(filename)
        if not "files" in pvalue:
          pvalue["files"] = []
        pvalue["files"].append(filename)
    data = deepcopy(jdata0)
    del data[str(request.args.get("id"))][edit["index"]]
    if not str(id) in data:
      data[str(id)] = dict()
    ind = edit["index"] if int(
      edit["index"]) >= len(data[str(id)]) + 1 else len(data[str(id)]) + 1
    data[str(id)][str(ind)] = pvalue
    write_json(f"static/jsons/tasks/{c}.json", data)

    signed_device = fetch_json("static/jsons/signed_device.json")
    FCMToken = fetch_json("static/jsons/FCMToken.json")
    account = fetch_users()
    notifications = fetch_json("static/jsons/notifications.json")
    tokens = []
    cal = [
      k for k, v in account.items()
      if v.get("class") == c and v.get("settings", dict()).get("HM-notify")
    ]
    for uName, dIDL in signed_device.items():
      if uName in cal:
        if not uName in notifications:
          notifications[uName] = []
        notifications[uName].insert(
          0, {
            "title": "作業更新 - " + data[str(id)][str(ind)]["title"],
            "content": pvalue["content"],
            "stat": "unsend",
            "link": f"/sche/task?id={id}#{ind}",
            "time": get_today("%Y-%m-%d %H:%M"),
            "bg-color": "bg-info-subtle",
            "icon": "bi-calendar3"
          })
        for i in dIDL:
          if FCMToken.get(i): tokens.append(FCMToken[i])

    notifications.supd()

    if len(pvalue.get("files", [])) > 0:
      image = f"https://hswm.up.railway.app/" + pvalue["files"][0]
      messaging.send_multicast(
        messaging.MulticastMessage(
          tokens,
          android=messaging.AndroidConfig(
            notification=messaging.AndroidNotification(
              title="作業更新 - " + data[str(id)][str(ind)]["title"],
              body=pvalue["content"],
              image=image),
            collapse_key="HsWM1060060422")))
    else:
      messaging.send_multicast(
        messaging.MulticastMessage(
          tokens,
          android=messaging.AndroidConfig(
            notification=messaging.AndroidNotification(
              title="作業更新 - " + data[str(id)][str(ind)]["title"],
              body=pvalue["content"]),
            collapse_key="HsWM1060060422")))
    return redirect(url_for("tskn.__edit") + f"?class={c}&id={id}")
  try:
    items = jdata[str(id)].items()
  except KeyError:
    return redirect(url_for("tskn.__add", c=c))

  return render_template("edit.html",
                         id=id,
                         cls=c,
                         items=items,
                         message=ems,
                         header=render_template("header.html"),
                         footer=render_template("footer.html"),
                         Users=User.refresh_users(),
                         filem=files_map)


@tskn.route("/tskn/add<c>", methods=["get", "post"])
@login_required
def __add(c):
  user = current_user
  if not user.is_teacher and not user.is_asistnt:
    return render_template("redirects.html",
                           link="/index",
                           letter="非教師身分，重新導向至首頁",
                           header=render_template("header.html"),
                           footer=render_template("footer.html"),
                           Users=User.refresh_users())
  if not c:
    return render_template("redirects.html",
                           link=request.referrer,
                           letter="連結錯誤!重新導向至前頁",
                           header=render_template("header.html"),
                           footer=render_template("footer.html"),
                           Users=User.refresh_users())
  if user.is_teacher and not c in user.classes or user.is_asistnt and c != user.clas:
    return render_template("redirects.html",
                           link=request.referrer,
                           letter="您沒有指導這個班級!重新導向至前頁",
                           header=render_template("header.html"),
                           footer=render_template("footer.html"),
                           Users=User.refresh_users())

  value = dict()
  value["start_time"] = get_today(format="%Y-%m-%d %H:%M")
  value["tasker"] = user.id
  if request.method.lower() == "post":
    rvalue = request.form.to_dict()
    if not (rvalue.get("end_date") and rvalue.get("end_time")
            and rvalue.get("content") and rvalue.get("title")):

      value = {
        "start_time": get_today(format="%Y-%m-%d %H:%M"),
        "tasker": user.id,
        "end_date": rvalue.get("end_date"),
        "end_time": rvalue.get("end_time"),
        "content": rvalue.get("content"),
        "title": rvalue.get("title")
      }
      return render_template("add.html",
                             cls=c,
                             value=value,
                             message="資料輸入不完全，請填寫完畢後再送出。",
                             header=render_template("header.html"),
                             footer=render_template("footer.html"),
                             Users=User.refresh_users())
    pvalue = deepcopy(rvalue)
    del pvalue["index"]
    pvalue["start_time"] = value["start_time"]
    pvalue["end_date"] = rvalue["end_date"]
    pvalue["end_time"] = rvalue["end_time"]
    pvalue["content"] = rvalue["content"]
    pvalue["title"] = rvalue["title"]
    pvalue["tasker"] = user.id
    jdata = fetch_json(f"static/jsons/tasks/{c}.json")
    day = weekdays[datetime.datetime.strptime(rvalue["end_date"],
                                              "%Y-%m-%d").strftime("%a")]
    id = str(maps[rvalue["end_time"]][day])
    m = max([int(i) for i in jdata.get(str(id), {"-1": "123"})]) + 1
    files = request.files.getlist("uploaded_files")
    if files[-1].filename:
      for file in files:
        if not c in os.listdir("static/files/") and not os.path.exists(
            f"static/files/{c}"):
          os.mkdir(f"static/files/{c}")
        if not id in os.listdir(f"static/files/{c}") and not os.path.exists(
            f"static/files/{c}/{id}"):
          os.mkdir(f"static/files/{c}/{id}")
        if not m in os.listdir(
            f"static/files/{c}/{id}") and not os.path.exists(
              f"static/files/{c}/{id}/{m}"):
          os.mkdir(f"static/files/{c}/{id}/{m}")
        filename = f"static/files/{c}/{id}/{m}/{secure_filename(file.filename)}"
        file.save(filename)
        if not "files" in pvalue:
          pvalue["files"] = []
        pvalue["files"].append(filename)
    if str(id) in jdata.keys():
      jdata[str(id)][str(m)] = pvalue
    else:
      jdata[str(id)] = dict()
      jdata[str(id)][str(m)] = pvalue
    jdata.supd()

    # scheduler = setScheduler()
    # scheduler.add_job(lambda: messaging.send_all([
    #     messaging.Message(notification=messaging.Notification(
    #       title=i.get("title"), body=i.get("body")),
    #                       token=i.get("token"))
    #     for i in pendingMsg[request.form.get("key")]
    #   ]),
    #                     'date',
    #                     run_date=request.form.get("time"))
    # scheduler.start()
    signed_device = fetch_json("static/jsons/signed_device.json")
    FCMToken = fetch_json("static/jsons/FCMToken.json")
    account = fetch_users()
    notifications = fetch_json("static/jsons/notifications.json")
    tokens = []
    cal = [
      k for k, v in account.items()
      if v.get("class") == c and v.get("settings", dict()).get("HM-notify")
    ]
    for uName, dIDL in signed_device.items():
      if uName in cal:
        if not uName in notifications:
          notifications[uName] = []
        notifications[uName].insert(
          0, {
            "title": "新作業 - " + pvalue["title"],
            "content": pvalue["content"],
            "stat": "unsend",
            "link": f"/sche/task?id={id}#{m}",
            "time": get_today("%Y-%m-%d %H:%M"),
            "bg-color": "bg-info-subtle",
            "icon": "bi-calendar3"
          })
        for i in dIDL:
          if FCMToken.get(i): tokens.append(FCMToken[i])

    notifications.supd()

    if files[-1].filename:
      image = f"https://hswm.up.railway.app/static/files/{c}/{id}/{m}/{secure_filename(files[-1].filename)}"
      messaging.send_multicast(
        messaging.MulticastMessage(
          tokens,
          android=messaging.AndroidConfig(
            notification=messaging.AndroidNotification(title="新作業 - " +
                                                       pvalue["title"],
                                                       body=pvalue["content"],
                                                       image=image),
            collapse_key="HsWM1060060422")))
    else:
      messaging.send_multicast(
        messaging.MulticastMessage(
          tokens,
          android=messaging.AndroidConfig(
            notification=messaging.AndroidNotification(title="新作業 - " +
                                                       pvalue["title"],
                                                       body=pvalue["content"]),
            collapse_key="HsWM1060060422")))
    return redirect(url_for("tskn.__edit") + f"?class={c}&id={id}#{id}-{m}")
  return render_template("add.html",
                         cls=c,
                         value=value,
                         message="",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"),
                         Users=User.refresh_users())


@tskn.route("/tskn/del<int:id>", methods=["get", "post"])
@login_required
def __del(id):
  user = current_user
  c = request.args.get("class")
  k = request.args.get("key")
  if not user.is_teacher and not user.is_asistnt:
    return render_template("redirects.html",
                           link="/index",
                           letter="非教師身分，重新導向至首頁",
                           header=render_template("header.html"),
                           footer=render_template("footer.html"),
                           Users=User.refresh_users())
  if (not c) or ((not id) and (not id == 0)):
    return render_template("redirects.html",
                           link=request.referrer,
                           letter="連結錯誤!重新導向至前頁",
                           header=render_template("header.html"),
                           footer=render_template("footer.html"),
                           Users=User.refresh_users())
  if user.is_teacher and not c in user.classes or user.is_asistnt and c != user.clas:

    return render_template("redirects.html",
                           link=request.referrer,
                           letter="您沒有指導這個班級!重新導向至前頁",
                           header=render_template("header.html"),
                           footer=render_template("footer.html"),
                           Users=User.refresh_users())
  if request.method.lower() == "post":
    data = fetch_json(f"static/jsons/tasks/{c}.json")
    User.refresh_users()
    if "tasker" in data[str(id)][str(k)]:
      if data[str(id)][str(k)]["tasker"] != user.id:
        session["ems"] = "非該作業指派人"
        return redirect(f"/tskn/edit{id}?class={c}")
    if data[str(id)][str(k)].get("files"):
      for i in data[str(id)][str(k)]["files"]:
        try:
          os.remove(i)
        except:
          None
    signed_device = fetch_json("static/jsons/signed_device.json")
    FCMToken = fetch_json("static/jsons/FCMToken.json")
    account = fetch_users()
    notifications = fetch_json("static/jsons/notifications.json")
    tokens = []
    cal = [
      k for k, v in account.items()
      if v.get("class") == c and v.get("settings", dict()).get("HM-notify")
    ]
    for uName, dIDL in signed_device.items():
      if uName in cal:
        if not uName in notifications:
          notifications[uName] = []
        notifications[uName].insert(
          0, {
            "title": "作業更新 - " + data[str(id)][k]["title"],
            "content": "--已刪除",
            "stat": "unsend",
            "link": "",
            "time": get_today("%Y-%m-%d %H:%M"),
            "bg-color": "bg-info-subtle",
            "icon": "bi-calendar3"
          })
        for i in dIDL:
          if FCMToken.get(i): tokens.append(FCMToken[i])

    notifications.supd()

    if len(data[str(id)][k].get("files", [])) > 0:
      image = f"https://hswm.up.railway.app/" + data[str(
        id)][k]["files"][0]
      messaging.send_multicast(
        messaging.MulticastMessage(
          tokens,
          android=messaging.AndroidConfig(
            notification=messaging.AndroidNotification(
              title="作業更新 - " + data[str(id)][k]["title"],
              body="--已刪除",
              image=image),
            collapse_key="HsWM1060060422")))
    else:
      messaging.send_multicast(
        messaging.MulticastMessage(
          tokens,
          android=messaging.AndroidConfig(
            notification=messaging.AndroidNotification(
              title="作業更新 - " + data[str(id)][k]["title"], body="--已刪除"),
            collapse_key="HsWM1060060422")))
    del data[str(id)][str(k)]
    if len(data[str(id)]) == 0: del data[str(id)]
    data.supd()

    return redirect(f"/tskn/class{c}")
  return render_template("tdl.html",
                         id=id,
                         cls=c,
                         key=k,
                         header=render_template("header.html"),
                         footer=render_template("footer.html"),
                         Users=User.refresh_users())


@tskn.route("/tskn/students<c>", methods=["post", "get"])
@login_required
def __students(c):
  user = current_user
  if not user.is_teacher:
    return render_template("redirects.html",
                           link=request.referrer,
                           letter="非教師身分，重新導向至前頁",
                           header=render_template("header.html"),
                           footer=render_template("footer.html"),
                           Users=User.refresh_users())
  if not c:
    return render_template("redirects.html",
                           link=request.referrer,
                           letter="連結錯誤!重新導向至前頁",
                           header=render_template("header.html"),
                           footer=render_template("footer.html"),
                           Users=User.refresh_users())
  if user.is_teacher and not c in user.classes or user.is_asistnt and c != user.clas:
    return render_template("redirects.html",
                           link=request.referrer,
                           letter="您沒有指導這個班級!重新導向至前頁",
                           header=render_template("header.html"),
                           footer=render_template("footer.html"),
                           Users=User.refresh_users())
  data0 = fetch_users()
  data01 = dict(
    sorted(
      {j["number"]: {
        i: j
      }
       for i, j in data0.items() if j.get("class") == c}.items()))
  data = dict()
  for j in data01.values():
    for i, k in j.items():
      data[i] = k

  # data = {i: j for i, j in data0.items() if j.get("class") == c}
  sp = fetch_json("static/jsons/sp.json")
  emails = fetch_json("static/jsons/email.json").KVSwap()
  if request.method.lower() == "post":
    if not request.form.get("set") or not request.args.get("stu"):
      return " "
    stu = request.args.get("stu")
    if request.form.get("set") == "true":
      if not user.id in data0[stu]["asistnt"]:
        data0[stu]["asistnt"].append(user.id)
        data0.supd()
    elif request.form.get("set") == "false":
      if user.id in data0[stu]["asistnt"]:
        data0[stu]["asistnt"].remove(user.id)
        data0.supd()

    return "OK"

  if request.args.get("stu"):
    re = data0.get(request.args.get("stu")).get("asistnt")
    return jsonify({"result": True if user.id in re else False})
  return render_template("students.html",
                         data=data,
                         cls=c,
                         sp=sp,
                         emails=emails,
                         header=render_template("header.html"),
                         footer=render_template("footer.html"),
                         Users=User.refresh_users())
