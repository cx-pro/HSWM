from .imports import *
from .funcs import *
from flask import Blueprint

food = Blueprint("food", __name__)


@food.route("/food/")
def __index():
  result = fetch_json("static/jsons/vote_result.json")
  rrm = {k: len(v) for k, v in result.items()}
  rmax = max(list(rrm.values()))
  rml = [k for k, v in rrm.items() if v == rmax]
  return render_template("foodIndex.html",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"),
                         sech=render_template("sech.html"),
                         rmax=rmax,
                         rml=rml,
                         menu_list=list(os.listdir("static/menu_images")))


@food.route("/food/order", methods=["post", "get"])
def __order():
  data = fetch_json("static/jsons/foods.json")
  settings = fetch_json("static/jsons/food_settings.json")
  if request.method.lower() == "post":
    id = request.args.get("id")
    if not id: abort(400)
    if not id in data: data[id] = {}
    for k, v in request.form.to_dict().items():
      if not k in data[id]:
        data[id][k] = 0
      data[id][k] += int(v)
    data.supd()
    return render_template("foodOrderComplete.html",
                           header=render_template("header.html"),
                           footer=render_template("footer.html"),
                           sech=render_template("sech.html"))
  dl = []
  for v in data.values():
    for k1 in v.keys():
      if not k1 in dl: dl.append(k1)
  return render_template("foodOrder.html",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"),
                         sech=render_template("sech.html"),
                         dl=dl,
                         cut=settings["cut"])


@food.route("/food/induce", methods=["post", "get"])
def __induce():
  if request.method.lower() == "post":
    if request.form["pswd"] != "clear": return redirect("/food/induce")
    write_json("static/jsons/foods.json", {})
    return redirect("/food/induce")
  data = fetch_json("static/jsons/foods.json")
  summary = dict()
  for k1, v1 in data.items():
    for k2, v2 in v1.items():
      if not k2 in summary: summary[k2] = 0
      summary[k2] += v2
  stk = list(map(str, sorted(map(int, list(data.keys())))))
  return render_template("foodInduce.html",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"),
                         sech=render_template("sech.html"),
                         summary=summary,
                         data=data,
                         stk=stk)


@food.route("/food/vote", methods=["post", "get"])
def __vote():
  settings = fetch_json("static/jsons/food_settings.json")
  data = fetch_list("static/jsons/vote.json")
  result = fetch_json("static/jsons/vote_result.json")
  if request.method.lower() == "post":
    form = request.form.to_dict()
    if not "num" in form and "name" in form:
      name = request.form["name"]
      if not name in data:
        data.append(name)
        result[name] = []

        data.supd()
        result.supd()
      return "OK"
    elif "checknum" in form:
      l = []
      for i in result.values():
        for j in i:
          l.append(j)
      if request.form["checknum"] in l:
        return "T"
      return "F"
    else:
      name = request.form["name"]
      result[name].append(str(int(request.form["num"])))

      result.supd()
      return render_template("foodVoteComplete.html",
                             header=render_template("header.html"),
                             footer=render_template("footer.html"),
                             sech=render_template("sech.html"))
  return render_template("foodVote.html",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"),
                         sech=render_template("sech.html"),
                         data=sorted(data),
                         settings=settings,
                         result={i: result[i]
                                 for i in data})


@food.route("/food/settings", methods=["post", "get"])
def __vote_settings():
  settings = fetch_json("static/jsons/food_settings.json")

  if request.method.lower() == "post":
    form = request.form.to_dict()
    if "pswd" in form:
      result = fetch_json("static/jsons/vote_result.json")
      for k in result.keys():
        result[k] = []
      result.supd()
    elif "title" in form:
      settings["title"] = form["title"]
      settings.supd()
    elif "order" in form and "mode" in form:
      if form["order"] == "check":
        settings["cut"] = True if form["mode"] == "stop" else False
        settings.supd()
    elif "vote" in form and "mode" in form:
      if form["vote"] == "check":
        settings["vote_cut"] = True if form["mode"] == "stop" else False
        settings.supd()
    else:
      files = request.files.getlist("files")
      if files[-1].filename:
        for fn in os.listdir("static/menu_images"):
          os.remove("static/menu_images/" + fn)
        for file in files:
          file.save(f"static/menu_images/{secure_filename(file.filename)}")
  return render_template("vote_settings.html",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"),
                         sech=render_template("sech.html"),
                         settings=settings)
