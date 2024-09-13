from .imports import *
from .funcs import *
from flask import Blueprint

api = Blueprint("api", __name__)


@api.route("/api/get", methods=["get"])
def __get():
  user = current_user
  args = request.args
  access_api = args.get("api")
  if access_api == "notification":
    notify = fetch_json("static/jsons/notifications.json")
    signed_device = fetch_json("static/jsons/signed_device.json")
    signed_devices = dict()
    for k, v in signed_device.items():
      for j in v:
        signed_devices[j] = k
    gu = args.get("user", args.get("deviceId"))
    if not (gu in notify or gu in signed_devices):
      return abort(400)
    return json.dumps([{
      "title": i["title"],
      "content": i["content"]
    } for i in notify[gu if not gu in signed_devices else signed_devices[gu]]
                       if i["stat"] == "unsend"],
                      ensure_ascii=False)

  elif access_api == "functions":
    return render_template("functions.html")

  elif access_api == "notify_page":
    notify = fetch_json("static/jsons/notifications.json")
    return render_template("noti_page.html",
                           notifications=[] if not user.is_authenticated
                           or not user.id in notify else notify[user.id])
  elif access_api == "Cauthen":
    if not request.args.get("deviceId"):
      return "missing argument(s) or argument empty", 400
    signed_device = fetch_json("static/jsons/signed_device.json")
    signed_devices = dict()
    for k, v in signed_device.items():
      for j in v:
        signed_devices[j] = k
    return "True" if args.get("deviceId") in signed_devices else "False"
  abort(400)


@api.route("/api/post", methods=["post"])
def __post():
  if not request.args.get("deviceId") or not request.form.get("token"):
    return "missing argument(s) or argument empty", 400
  data = fetch_json("static/jsons/FCMToken.json")
  data[request.args["deviceId"]] = request.form["token"]
  data.supd()
  return "OK"
