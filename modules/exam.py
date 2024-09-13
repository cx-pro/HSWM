from .imports import *
from .funcs import *
from flask import Blueprint

exam = Blueprint("exam", __name__)


@exam.route("/exam/")
@login_required
def __index():
  data = fetch_json("static/jsons/exams.json")
  return render_template("exam.html",
                         data=data,
                         header=render_template("header.html"),
                         footer=render_template("footer.html"))


@exam.route("/exam/view")
@login_required
def __view():
  token = request.args.get("token")
  data = fetch_json("static/jsons/exams.json")
  if not token or not token in data: return redirect("/exam/?msg=連結錯誤")
  return render_template("exam_view.html",
                         data=data[token],
                         header=render_template("header.html"),
                         footer=render_template("footer.html"))


@exam.route("/exam/create", methods=["post", "get"])
@login_required
def __create():
  user=current_user
  if not user.is_teacher:
    return redirect("/exam/?msg=權限不足")
  if request.method.lower() == "post":
    session["exam-create-DATA-HTML"] = request.form.get("HTML")
    session["exam-create-DATA-undos"] = request.form.get("undos")
    session["exam-create-DATA-dos"] = request.form.get("dos")
    session["exam-create-DATA-max"] = request.form.get("max")
    return "OK"
  return render_template("exam_create.html",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"))
