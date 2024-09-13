from .imports import *
from .funcs import *
from flask import Blueprint
from .user import User

study = Blueprint("study", __name__)


@study.route("/study/", methods=["post", "get"])
def __index():
  if request.method.lower() == "post":
    data = fetch_json("static/jsons/study.json")
    data["main"].append({
      "urls": json.loads(request.form["url"]),
      "summary": request.form["summary"]
    })
    data.supd()
    session["msg"] = "傳送成功"
  return render_template("studyIndex.html",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"))
