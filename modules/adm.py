from .imports import *
from .funcs import *
from flask import Blueprint
from .user import User

adm = Blueprint("adm", __name__)


@adm.route("/adm/")
@login_required
def __index():
  user = current_user
  if not user.is_admin:
    return redirect("/")
  return render_template("admin_index.html",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"),
                         l=[
                           i for i in sorted(os.listdir("static/jsons"))
                           if not os.path.isdir("static/jsons/" + i)
                         ])


@adm.route("/adm/files", methods=["post", "get"])
@fresh_login_required
def __files():
  if not current_user.is_admin:
    return "Access denied.", 403
  name = request.args.get("p", "static/jsons").replace("//", "/")
  if not name.startswith("static/jsons"):
    return redirect("/files")
  if request.method.lower() == "post":
    pass
  return render_template("files.html",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"),
                         files=[
                           (i, os.path.isdir(f"{name}/{i}"),
                            f"/files?p={name}/{i}"
                            if os.path.isdir(f"{name}/{i}") else f"{name}/{i}")
                           for i in sorted(os.listdir(name))
                         ],
                         p=name.split("/"))


@adm.route("/adm/db", methods=["post", "get"])
@fresh_login_required
def __dbManager():
  if not current_user.is_admin:
    return "Access denied.", 403
  table = request.args.get("table")
  dbt0 = request.args.get("db")
  if False: abort(400)
  dbt = dbt0[-dbt0[::-1].find("/"):]
  if not dbt in os.listdir("static/jsons/dbs/"):
    return "File Not Found.", 400
  db = fetch_db(f"static/jsons/dbs/{dbt}")
  rowc = -1
  rsql = ""
  sql = """SELECT name FROM sqlite_master  
  WHERE type='table';""" if not table else f"""select * from {table}"""
  if request.method.lower() == "post":
    if not "cmd" in request.form: abort(400)
    lcmd = request.form["cmd"].lower()
    f = False
    for i in ["delete", "insert", "update", "replace"]:
      if i in lcmd:
        f = True
        break

    if f:
      try:
        db.cs.execute(request.form["cmd"])
      except sqlite3.OperationalError as e:
        return render_template("dbManager.html",
                               header=render_template("header.html"),
                               footer=render_template("footer.html"),
                               sql=request.form["cmd"],
                               err=str(e))
      db.db.commit()
      rowc = db.cs.rowcount
    else:
      sql = request.form["cmd"]
    rsql = request.form["cmd"]

  db.cs.execute(sql)
  return render_template("dbManager.html",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"),
                         data=db.cs.fetchall(),
                         description=[i[0] for i in db.cs.description],
                         sql=rsql,
                         rowc=rowc,
                         err=None)


@adm.route("/adm/tcode", methods=["post", "get"])
@fresh_login_required
def __tcode_manage():
  if not current_user.is_admin:
    return "Access denied.", 403
  data = fetch_json(f"static/jsons/tcode.json")
  return render_template("tcodeIndex.html",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"),
                         data=data)