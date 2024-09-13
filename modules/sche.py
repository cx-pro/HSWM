from .imports import *
from .funcs import *
from flask import Blueprint

sche = Blueprint("sche", __name__)

Users = fetch_users()


@sche.route("/sche/calendar")
@login_required
def __calendar():
  user = current_user
  year = request.args.get("y")
  month = request.args.get("m")
  if not year: year = str(int(get_today("%Y")))
  if not month: month = str(int(get_today("%m")))
  if not current_user.is_student: return redirect("/")
  data = fetch_json(f"static/jsons/tasks/{user.clas}.json")
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

  return render_template("scalendar.html",
                         y=year,
                         m=month,
                         tks=tks,
                         task=data1,
                         cls=user.clas,
                         todaya={i.upper(): j
                                 for i, j in weekdays.items()}[get_today()],
                         today=get_today("%Y-%m-%d"))


@sche.route("/sche/")
@sche.route("/sche/schedule")
def __schedule():
  if not current_user.is_student:
    print(current_user.is_student)
    print(current_user.is_qrcUser)
    return redirect("/")
  task = dict()
  for i in cls_id:
    for j in i:
      task[j] = False
  if current_user.clas:
    data0 = fetch_json(f"static/jsons/tasks/{current_user.clas}.json")
  else:
    return render_template("error.html",
                           content="您目前沒有班級喔，若有錯誤請回報管理員",
                           header=render_template("header.html"),
                           footer=render_template("footer.html"))
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
    for j in range(len(i)):
      i[j] = "" if task[i[j]] else "hidden"
    task_bools.append(i)
  return render_template("schedule.html",
                         l=zip(day, day_bools),
                         cls=zip(cls, cls_id, task_bools),
                         header=render_template("header.html"),
                         footer=render_template("footer.html"),
                         week_date=week_dates,
                         days=day)


@sche.route("/sche/task")
@login_required
def __task():
  id = request.args.get("id")
  user = current_user
  if not id:
    return render_template("error.html",
                           content="連結錯誤",
                           header=render_template("header.html"),
                           footer=render_template("footer.html"))
  if not current_user.is_student: return redirect("/")
  if current_user.clas:
    try:
      content = fetch_json(f"static/jsons/tasks/{current_user.clas}.json")[
        str(id)]
    except KeyError:
      return render_template("error.html",
                             content="連結錯誤",
                             header=render_template("header.html"),
                             footer=render_template("footer.html"))
    files_map = list()
    for i in content.values():
      if "files" in i:
        for j in i["files"]:
          print(get_extension(j))
          if imghdr.what(j) or get_extension(j) in imgs_files:
            files_map.append(j)
    return render_template("task.html",
                           content=content.items(),
                           id=id,
                           header=render_template("header.html"),
                           footer=render_template("footer.html"),
                           Users=fetch_users(),
                           filem=files_map)
  return render_template("error.html",
                         content="您目前沒有班級喔，若有錯誤請回報管理員",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"))


@sche.route("/sche/content<int:id>_<int:id2>")
@login_required
def __contnt(id, id2):
  user = current_user
  if not current_user.is_student: return redirect("/")
  if current_user.clas:
    try:
      content = fetch_json(f"static/jsons/tasks/{current_user.clas}.json")[
        str(id)][str(id2)]
      content["content"] = content["content"].replace("\n", "<br>")
    except KeyError:
      return render_template("error.html",
                             content="連結錯誤",
                             header=render_template("header.html"),
                             footer=render_template("footer.html"))
    return render_template("contnt.html",
                           data=content,
                           id=id,
                           header=render_template("header.html"),
                           footer=render_template("footer.html"),
                           Users=Users)
  return render_template("error.html",
                         content="您目前沒有班級喔，若有錯誤請回報管理員",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"))


@sche.route("/sche/member")
@login_required
def __students():
  user = current_user
  if not current_user.is_student: return redirect("/")
  data0 = fetch_users()
  data = {
    i: j
    for i, j in dict(
      sorted(data0.items(), key=lambda x: x[1].get("number", "0"))).items()
    if j.get("class") == user.clas
  }
  sp = fetch_json("static/jsons/sp.json")
  emails = fetch_json("static/jsons/email.json").KVSwap()
  return render_template("students.html",
                         data=data,
                         sp=sp,
                         emails=emails,
                         header=render_template("header.html"),
                         footer=render_template("footer.html"))
