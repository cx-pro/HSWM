from .imports import *
from .funcs import *
from flask import Blueprint

grade = Blueprint("grade", __name__)


@grade.route("/grade/")
@login_required
def __index():
  data = fetch_json(f"static/jsons/grades/{current_user.id}.json")
  dl = dict()
  for i in data.values():
    l = list(i["data"].values())
    s = sum(l)
    le = len(l)
    if le == 0: continue
    dl[i["title"]] = {"sum": s, "length": le, "avg": s / le}
  return render_template("gindex.html",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"),
                         gl=data.items(),
                         dl=dl)


@grade.route("/grade/post", methods=["post"])
@login_required
def __post():
  if not "method" in request.form:
    abort(400)
  method = request.form["method"]
  if method == "add":
    data = fetch_json(f"static/jsons/grades/{current_user.id}.json")
    ind = str(int(data.maxKey) + 1)
    lind = str(int(ind) - 1)
    if lind in data:
      if not data[lind].get("data"):
        ind = lind
    data[ind] = {"id": ind, "title": "點按以編輯", "data": dict()}
    data.supd()
    return "OK"
  elif method == "add-grade":
    if not "id" in request.form:
      abort(400)
    id = request.form["id"]
    data = fetch_json(f"static/jsons/grades/{current_user.id}.json")
    if not id in data: abort(400)
    data[id]["title"] = request.form["title"] or "未命名成績單"
    form = request.form.to_dict()
    del form["id"], form["title"], form["method"]
    for k, v in form.items():
      if not v.isdigit(): continue
      data[id]["data"][k] = float(v)
    data.supd()
    return "OK"
  elif method == "del-grade":
    if not "id" in request.form: abort(400)
    id = request.form["id"]
    data = fetch_json(f"static/jsons/grades/{current_user.id}.json")
    if not id in data: abort(400)
    del data[id]
    data.supd()
    return "OK"
  elif method == "edit-grade":
    if not "id" in request.form: abort(400)
    id = request.form["id"]
    data = fetch_json(f"static/jsons/grades/{current_user.id}.json")
    if not id in data: abort(400)
    data[id]["title"] = request.form["title"] or "未命名成績單"
    form = request.form.to_dict()
    del form["id"], form["title"], form["method"]
    for k, v in form.items():
      if not v.isdigit(): continue
      data[id]["data"][k] = float(v)
    data.supd()
    return "OK"
  abort(400)


@grade.route("/grade/sheet")
@login_required
def __sheet():
  id = request.args.get("id")
  data = fetch_json(f"static/jsons/grades/{current_user.id}.json")
  if not id in data:
    abort(400)
  return render_template("gradeSheet.html",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"),
                         data=data[id])
