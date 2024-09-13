from gevent import monkey
monkey.patch_all()
import jinja2
from modules.funcs import *
from modules.imports import *


from modules.user import User
from modules.user import AnonymousUser
from modules.sche import sche
from modules.tskn import tskn
from modules.certi import certi
from modules.qa import qa
from modules.lb import lb
from modules.tools import tools
from modules.adm import adm
from modules.clsm import clsm
from modules.api import api
from modules.chat import chat
from modules.food import food
from modules.study import study
from modules.grade import grade
# from modules.exam import exam
app = Flask(__name__)
default_app = firebase_admin.initialize_app()

# print(privatekey("private.pem").key, publickey("public.pem").key)


def _get_access_token():
  """Retrieve a valid access token that can be used to authorize requests.

  :return: Access token.
  """
  credentials = service_account.Credentials.from_service_account_file(
    'service-account.json',
    scopes=["https://www.googleapis.com/auth/firebase.messaging"])
  request = grequests.Request()
  credentials.refresh(request)
  return credentials.token


# google_auth_needs["headers"] = {
#   'Authorization': 'Bearer ' + _get_access_token(),
#   'Content-Type': 'application/json; UTF-8',
# }

app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=90)

defaults = jinja2.defaults.DEFAULT_NAMESPACE
defaults["zip"] = zip
defaults["len"] = len
defaults["get_today"] = get_today
defaults["find"] = str().find
defaults["startswith"] = str().startswith
defaults["str"] = str
defaults["list"] = list
defaults["int"] = int
defaults["max"] = max
defaults["get_filename"] = get_filename
defaults["isinstance"] = isinstance
defaults["rd"] = rd
app.config["SECRET_KEY"] = os.urandom(999)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"
login_manager.login_view = '__login'
login_manager.refresh_view = '__login'
login_manager.REMEMBER_COOKIE_HTTPONLY = True
login_manager.REMEMBER_COOKIE_REFRESH_EACH_REQUEST = True
app.register_blueprint(sche, url_perfix="/sche")
app.register_blueprint(tskn, url_perfix="/tskn")
app.register_blueprint(certi, url_perfix="/certi")
app.register_blueprint(qa, url_perfix="/qa")
app.register_blueprint(lb, url_perfix="/")
app.register_blueprint(tools, url_perfix="/tools")
app.register_blueprint(adm, url_perfix="/adm")
app.register_blueprint(clsm, url_perfix="/clsm")
app.register_blueprint(chat, url_perfix="/chat")
app.register_blueprint(api, url_perfix="/api")
app.register_blueprint(food, url_perfix="/food")
app.register_blueprint(study, url_perfix="/study")
app.register_blueprint(grade, url_perfix="/grade")
# app.register_blueprint(exam, url_perfix="/exam")

socketio = SocketIO(app, async_mode='gevent')
socketio=SocketIO(app)

@login_manager.user_loader
def uloader(user0):
  User.refresh_users()
  if user0 not in User.users:
    return

  user = User()
  user.id = user0
  return user


@login_manager.request_loader
def rloader(r):
  User.refresh_users()
  user0 = r.form.get('user_id')
  if user0 not in User.users:
    return
  user = User()
  user.id = user0
  user.is_authenticated = r.form['password'] == User.users[user0]

  return user


login_manager.anonymous_user = AnonymousUser


@app.route("/google751910ed0ffb7d0c.html")
def google_authing():
  return render_template("google751910ed0ffb7d0c.html")


@app.route("/test")
def test():
  return render_template("test.html")


# @app.route("/auth",methods=["post"])
# def __auth():
#   req=request.form.to_dict()
#   returns={"stat":False}
#   ctx,token,Csign,Tsign=req["ctx"],req["_token"],req["C-signature"],req["T-signature"]
#   if rsa.verify(ctx, Csign, os.environ["AUTH_PUBLIC_KEY"]) and rsa.verify(token, Tsign, os.environ["AUTH_PUBLIC_KEY"]):
#     dctx = rsa.decrypt(ctx, os.environ["AUTH_PRIVATE_KEY"]).decode('utf8')
#     dtoken = rsa.decrypt(token, os.environ["AUTH_PRIVATE_KEY"]).decode('utf8')
#     tokens=fetch_local_json("static/jsons/tokens.json")
#     sdata=tokens[dtoken]
#     if sdata["_ctx"]==dctx and sdata["_token"]==dtoken:
#       returns["stat"]=True
#       returns["_re"]=generate_password_hash(dtoken)
#     else:
#       returns["message"]="Token and Context local data verify failed."
#   else:
#     returns["message"]="Context and Token verification failed."

#   return jsonify(returns)


@app.route("/schqrc", methods=["post"])
def __schqrc():
  if not "cls" in request.form: abort(400)
  name = request.form["cls"]
  if not name + ".png" in os.listdir("static/qrcode/"):
    url = f"https://hswm.up.railway.app/cls?cls={request.form['cls']}"
    qrc = qrcode.make(url)
    qrc.save(f"static/qrcode/{name}.png")
  return render_template("qrcoder.html",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"),
                         link=f"static/qrcode/{name}.png")


@app.route("/cls", methods=["post", "get"])
def __cls_redirect():
  cls = request.args.get("cls")
  if f"{cls}.json" in os.listdir("static/jsons/tasks"):
    if current_user.is_qrcUser:
      return redirect(
        f"/tskn/class{cls}" if current_user.editable else "/sche/")
    if request.method.lower() == "post":
      if not "role" in request.form: abort(400)
      if not current_user.is_qrcUser and not current_user.is_authenticated:
        current_user.is_qrcUser = True
        current_user.clas = cls
        current_user.editable = True if request.form.get(
          "role") == "tch" else False
        print(current_user.clas, current_user.is_qrcUser,
              current_user.editable, current_user.is_teacher,
              current_user.is_student, current_user.is_authenticated)
        return redirect(
          f"/tskn/class{cls}" if current_user.editable else "/sche/")

    return render_template("cls.html",
                           header=render_template("header.html"),
                           footer=render_template("footer.html"),
                           cls=cls)
  return render_template('error.html',
                         content=f"找不到該班級，若此錯誤非預期發生，請洽管理員。",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"))


@app.route("/testdwn")
def testdwn():
  return send_from_directory(os.path.join(app.root_path, 'static/'),
                             '計時器.html')


@app.errorhandler(404)
def page_not_found(e):
  return render_template('404.html',
                         header=render_template("header.html"),
                         footer=render_template("footer.html")), 404


logging.basicConfig(filename='static/jsons/errors.log', level=logging.ERROR)


@app.errorhandler(Exception)
def handle_error(error):
  if str(getattr(error, 'code', 500)).startswith("4"):
    return render_template(
      'error.html',
      content=f"發生錯誤，狀態代碼:{str(getattr(error, 'code', 500))}，若此錯誤非預期發生，請洽管理員。",
      header=render_template("header.html"),
      footer=render_template("footer.html")), getattr(error, 'code', 500)
  # 使用 logging 記錄器寫入錯誤訊息
  em = '\n--------------------\n發生錯誤:\n%s\n%s\n--------------------\n' % (
    get_today("%Y-%m-%dT%H-%M-%S"), error)
  logging.exception(em)
  print(em)
  db = fetch_db("static/jsons/dbs/error.db")
  db.cs.execute('''CREATE TABLE IF NOT EXISTS main
             (id integer primary key,
             path text,
             status_code integer,
             content text,
             datetime text)''')
  db.cs.execute(f'''INSERT INTO main VALUES(null,
             '{request.full_path if request.args else request.path}',
             {getattr(error, 'code', 500)},
             '{json.dumps(em).replace('"',"＂").replace("'","’")}',
             '{get_today("%Y-%m-%d %H:%M:%S")}')''')
  db.db.commit()
  db.close()
  mail2("0chenshyi0@gmail.com", "使用者發生問題", "%s" % em)
  return render_template("error.html",
                         content="發生錯誤，請通知管理員，並告知錯誤發生時間，謝謝。",
                         header=render_template("header.html"),
                         footer=render_template("footer.html")), 500


@app.after_request
def after_requesting(response):
  if not request.path.startswith("/static/dependences/"):
    now = get_today("%Y-%m-%d %H:%M:%S")
    tp = f"[{get_ip(request)}] -{now}-  -  {response.status_code}  - {request.method} -  ----  {request.full_path if request.args else request.path}"
    # db = fetch_db("static/jsons/dbs/console.db")
    # db.cs.execute('''CREATE TABLE IF NOT EXISTS main
    #            (id integer primary key,
    #            ip text,
    #            path text,
    #            status_code integer,
    #            method text,
    #            datetime text)''')
    # db.cs.execute('''select count(*) from main''')
    # c = db.cs.fetchone()[0]
    # if int(c) > 1000:
    #   db.cs.execute("delete from main")
    #   db.db.commit()
    # db.cs.execute(f'''INSERT INTO main VALUES(null,
    #            '{get_ip(request)}',
    #            '{request.full_path if request.args else request.path}',
    #            {response.status_code},
    #            '{request.method}',
    #            '{now}')''')
    # db.db.commit()
    # db.close()
  else:
    tp = "Requested: dependences"
  tp != lp[0] and print(tp)
  lp[0] = tp
  return response


@app.before_request
def __before_requesting():
  User.refresh_users()
  session["DEMO"]=True if os.environ.get("DEMO")=="true" else False
  if session.get("notification_set"):
    session["notification_set"] = False
  else:
    notify.delete()
  if request.path.startswith("/static/jsons/"): abort(403)

  if not session.get("user_id") and request.args.get("user_id"):
    session["user_id"] = request.args.get("user_id")
  if not current_user.is_authenticated:
    if request.args.get("deviceId"):

      signed_device = fetch_json("static/jsons/signed_device.json")
      exsigned_device = dict()
      for k1, v1 in signed_device.items():
        for j in v1:
          exsigned_device[j] = k1
      if request.args.get("deviceId") in exsigned_device:
        user = User()
        user.id = exsigned_device[request.args.get("deviceId")]
        if not current_user.is_authenticated: login_user(user, fresh=False)
    elif request.args.get("user_id"):
      login = fetch_json("static/jsons/login.json")
      if request.args.get("user_id") in login or session.get(
          "user_id") in login:
        user = User()
        user.id = login[request.args.get("user_id")]["username"]
        if not current_user.is_authenticated: login_user(user, fresh=False)

  if not session.get("user_pic"):
    session["user_pic"] = "profile_pics/default/Default_Avatar.webp"
  if current_user.is_authenticated and current_user.settings:
    session["dark"] = current_user.settings.get("theme", "light")
  elif not session.get("dark"):
    session["dark"] = "light"


@app.route("/policy")
def __polocy():
  return render_template("policy.html",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"))


@app.route("/usage")
def __usage():
  return render_template("usage.html",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"))


@app.route("/about")
def __about():
  return render_template("about.html",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"))


@app.route("/material")
def __material():
  return render_template("material.html",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"))


@app.route("/wfile", methods=['post', "get"])
@fresh_login_required
def __write_to_file():
  if not current_user.is_admin:
    return "Access denied.", 403
  if not (request.form.get("data") and request.form.get("file")):
    print(request.form["data"], type(request.form["data"]))
    return "missing argument(s)", 400
  with open(request.form.get("file"), mode="w") as wf:
    fcntl.flock(wf, fcntl.LOCK_EX)
    json.dump(json.loads(request.form["data"]), wf, indent=2)
    fcntl.flock(wf, fcntl.LOCK_UN)
    wf.close()
  return "OK"


@app.route("/file_reader", methods=["get"])
@fresh_login_required
def __privatejsons():
  if not current_user.is_admin:
    return "Access denied.", 403
  name = request.args.get("p")
  with open(name) as f:
    data = f.read()
    f.close()
  return render_template("readjson.html",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"),
                         data=data)


@app.route('/favicon.ico')
def favicon():
  return send_from_directory(os.path.join(app.root_path, 'static/pics'),
                             'favicon.ico')


@app.route("/google_callback", methods=["post", "get"])
def __google_callback():

  if request.method.lower() == "post":
    try:
      id_info = id_token.verify_oauth2_token(request.form.get("credential"),
                                             grequests.Request(),
                                             os.environ["GOOGLE_CLIENT_ID"])
      userid = id_info['sub']
    except ValueError:
      # Invalid token
      return render_template("redirects.html",
                             link="/login",
                             letter="登入失敗，重新導向登入頁‧‧‧",
                             header=render_template("header.html"),
                             footer=render_template("footer.html"))

    email = id_info.get("email")
    fullname = id_info.get("name")
    avatar = id_info.get("picture")
    emails = fetch_json("static/jsons/email.json")
    if email in emails:
      user = User()
      user.id = emails[email]
      mail2(
        email, "登入通知",
        f"在{get_today('%Y年%m月%d日 %H時%M分')} (24小時制)時，\n有人從位置{get_ip(request)}登入您的帳號，\n若並非您進行此操作，敬請盡速變更密碼。"
      )
      login_user(user)
      if request.args.get("deviceId"):
        username = emails[email]
        signed_device = fetch_json("static/jsons/signed_device.json")
        FCMToken = fetch_json("static/jsons/FCMToken.json")
        devices = []
        for i in signed_device.values():
          for j in i:
            devices.append(j)
        if not request.args.get("deviceId") in devices:
          if not username in signed_device:
            signed_device[username] = []
          signed_device[username].append(request.args.get("deviceId"))
          signed_device.supd()
        else:
          session["msg"] = "此裝置已有其他綁定。"
      session['google_id'] = id_info.get('sub')
      session['name'] = id_info.get('name')
      if session.get("user_id"):
        login = fetch_json("static/jsons/login.json")
        login[session.get("user_id")] = {
          "role": user.role if not user.is_asistnt else "asistnt",
          "username": user.id
        }
        login.supd()

    else:
      session["user_info"] = {
        "email": email,
        "fullname": fullname,
        "avatar": avatar
      }
      return redirect("/register3")
  return redirect(request.args.get("next", "/"))


@app.route("/index_calendar", methods=["post", "get"])
@login_required
def __index_calendar():
  year = request.args.get("y")
  month = request.args.get("m")
  date = request.args.get("date")
  if request.method.lower() == "post":
    print(request.form.to_dict())
    method = request.form.get("method")
    if method == "add":
      data = fetch_json(f"static/jsons/selfCalendar/{current_user.id}.json")
      if not "main" in data: data["main"] = dict()
      ind = str(max(list(map(int, data["main"].keys())) or [-1]) + 1)
      datetimelist = request.form.get("end_datetime").split("T")
      data["main"][ind] = {
        "title": request.form.get("title"),
        "content": request.form.get("content"),
        "start_time": get_today("%Y-%m-%d %H:%M"),
        "end_date": datetimelist[0],
        "end_time": datetimelist[1]
      }
      data.supd()
      return "OK"
    elif method == "edit":
      data = fetch_json(f"static/jsons/selfCalendar/{current_user.id}.json")
      ind = request.form.get("ind")
      datetimelist = request.form.get("end_datetime").split("T")
      data["main"][ind] = {
        "title": request.form.get("title"),
        "content": request.form.get("content"),
        "start_time": get_today("%Y-%m-%d %H:%M"),
        "end_date": datetimelist[0],
        "end_time": datetimelist[1]
      }
      data.supd()
      return "OK"
    elif method == "del":
      data = fetch_json(f"static/jsons/selfCalendar/{current_user.id}.json")
      ind = request.form.get("ind")
      del data["main"][ind]
      data.supd()
      return "OK"

  if not date:
    if not year: year = str(int(get_today("%Y")))
    if not month: month = str(int(get_today("%m")))
    mds = list(calen.itermonthdates(int(year), int(month)))
  else:
    datelist = date.split("-")
    year = datelist[0]
    month = datelist[1]
    mds = [datetime.datetime.strptime(date, "%Y-%m-%d").date()]

  dl = dict()
  data1 = {}
  datalist = [f"static/jsons/selfCalendar/{current_user.id}.json"]

  if current_user.is_teacher:
    for i in current_user.classes:
      datalist.append(f"static/jsons/tasks/{i}.json")
  else:
    datalist.append(f"static/jsons/tasks/{current_user.clas}.json")

  for fn in datalist:
    for k1, v1 in fetch_json(fn).items():
      for k2, v2 in v1.items():
        if datetime.datetime.strptime(v2["end_date"],
                                      "%Y-%m-%d").date() in mds:
          if not v2["end_date"] in dl: dl[v2["end_date"]] = list()
          if not f"{k1}-{k2}" in data1: data1[f"{k1}-{k2}"] = list()
          dl[v2["end_date"]].append(f"{k1}-{k2}")
          data1[f"{k1}-{k2}"].append(v2)

  tks = []

  for i in mds:
    sfd = datetime.datetime.strftime(i, "%Y-%m-%d")
    tks.append((sfd, dl[sfd]) if sfd in dl else [sfd])

  if date:
    files_map = list()
    for i in data1.values():
      for j in i:
        if "files" in j:
          for k in j["files"]:
            if imghdr.what(k) or get_extension(k) in imgs_files:
              files_map.append(k)

    return render_template("index_cal_date.html",
                           tks=tks,
                           data=data1,
                           date=date,
                           datelist=datelist,
                           users=fetch_users(),
                           filem=files_map)

  return render_template("index_calendar.html",
                         tks=tks,
                         data=data1,
                         m=month,
                         y=year,
                         todaya={i.upper(): j
                                 for i, j in weekdays.items()}[get_today()])


@app.route("/index_task", methods=["post", "get"])
@login_required
def __index_task():
  user = current_user
  if user.is_student:
    data = (user.clas, fetch_json(f"static/jsons/tasks/{user.clas}.json"))
  elif user.is_teacher:
    data = list()
    User.refresh_users()
    for c in user.classes:
      data.append((c, fetch_json(f"static/jsons/tasks/{c}.json")))
  else:
    return ""
  if request.method.lower() == "post":
    dones = fetch_json("static/jsons/done.json")
    if not user.id in dones:
      dones[user.id] = []
    if request.form.get("pos"):
      if not request.form.get("pos") in dones[user.id]:
        dones[user.id].append(request.form.get("pos"))
      else:
        dones[user.id].remove(request.form.get("pos"))
      dones.supd()

  tasks0 = list()
  tasks1 = list()
  tasks2 = list()

  def get_day(day: str, m: int):
    dl = day.split("-")
    dl[2] = f"{int(dl[2]) + m:02d}"
    return "-".join(dl)

  ml = [get_day(get_today("%Y-%m-%d"), i) for i in range(-1, 2)]
  if isinstance(data, list):
    for c, i in data:
      for k1, v1 in i.items():
        for k2, v2 in v1.items():
          if v2["end_date"] in ml:
            if v2["end_date"] == ml[0]:
              tasks0.append((f"{c}-{k1}-{k2}", v2))
            if v2["end_date"] == ml[1]:
              tasks1.append((f"{c}-{k1}-{k2}", v2))
            if v2["end_date"] == ml[2]:
              tasks2.append((f"{c}-{k1}-{k2}", v2))
  else:
    for k1, v1 in data[1].items():
      for k2, v2 in v1.items():
        if v2["end_date"] in ml:
          if v2["end_date"] == ml[0]:
            tasks0.append((f"{data[0]}-{k1}-{k2}", v2))
          if v2["end_date"] == ml[1]:
            tasks1.append((f"{data[0]}-{k1}-{k2}", v2))
          if v2["end_date"] == ml[2]:
            tasks2.append((f"{data[0]}-{k1}-{k2}", v2))
  dones = fetch_json("static/jsons/done.json")
  if user.id in dones:
    for i in dones[user.id]:
      c, id, ind = i.split('-')
      data = fetch_json(f"static/jsons/tasks/{c}.json")
      try:
        if data[id][ind]["end_date"] not in ml:
          del dones[user.id][dones[user.id].index(i)]
        del data
      except KeyError:
        del dones[user.id][dones[user.id].index(i)]
    dones.supd()
  return render_template("index_task.html",
                         tasks0=tasks0,
                         tasks1=tasks1,
                         tasks2=tasks2,
                         dones=dones[user.id] if user.id in dones else [])


@app.route("/", methods=["post", "get"])
@app.route("/index", methods=["post", "get"])
def __index():
  if request.method.lower() == "post":
    if current_user.is_authenticated:
      email = current_user.email
    else:
      email = request.form.get("email")
    r = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if not re.fullmatch(r, email):
      return "請輸入有效的Email", 403

    fgups = fetch_json("static/jsons/fgup.json")
    fgups[email] = {
      "time": get_today("%Y-%m-%d %H:%M"),
      "請求內容": request.form.get("content"),
      "stat": "pending"
    }

    fgups.supd()
  return render_template("index.html",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"))


@app.route("/settings", methods=["get", "post"])
@fresh_login_required
def __settings():
  user = current_user
  warn = dict()
  users = fetch_json("static/jsons/account.json")
  emails = fetch_json("static/jsons/email.json")
  tcodes = fetch_json("static/jsons/tcode.json")
  signed_device = fetch_json("static/jsons/signed_device.json")
  if request.method.lower() == "post":
    form = request.form.to_dict()
    codes = fetch_json("static/jsons/code.json")
    if form.get("role") in codes:
      users[user.id].pop("course", "")
      users[user.id].pop("classes", "")
      users[user.id]["department"] = codes[form["role"]]["department"]
      users[user.id]["class"] = codes[form["role"]]["class"]
      users[user.id]["role"] = "stu"
      users[user.id]["asistnt"] = []
      session["msgs"] = [
        f"已變更身分為 {users[user.id]['department']} {users[user.id]['class']} 學生"
      ]

    elif form.get("role") in tcodes:
      users[user.id].pop("department", "")
      users[user.id].pop("class", "")
      users[user.id].pop("asistnt", "")
      users[user.id]["course"] = tcodes[form["role"]]
      users[user.id]["classes"] = []
      users[user.id]["role"] = "tch"
      write_json(f"static/jsons/pdfs/{user.id}.json", {})
      session["msgs"] = [f"已變更身分為 {users[user.id]['course']} 教師"]

    elif form.get("classes") in codes and user.role == "tch":
      if not codes[form.get("classes")]["class"] in user.classes:
        users[user.id]["classes"].append(codes[form.get("classes")]["class"])
        session["msgs"] = [f"已加入班級 {codes[form.get('classes')]['class']}"]
      else:
        session["msgs"] = [f"已經是 {codes[form.get('classes')]['class']} 之教師"]
    elif form.get("mode"):
      if not users[user.id].get("settings"):
        users[user.id]["settings"] = dict()
      users[user.id]["settings"]["sche_mode"] = form.get("mode")
    elif form.get("index_mode"):
      if not users[user.id].get("settings"):
        users[user.id]["settings"] = dict()
      users[user.id]["settings"]["index_mode"] = form.get("index_mode")

    users.supd()
    return redirect("/settings")

  return render_template("settings.html",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"),
                         warn=warn,
                         userinfo=users[user.id],
                         email={j: i
                                for i, j in emails.items()}[user.id],
                         devices=signed_device.get(user.id, []))


@app.route("/recap", methods=["post"])
def __recap():
  return captcha()


@app.route("/user_settings", methods=["get", "post"])
@login_required
def __user_settings():
  if request.method.lower() == "post":
    acc = fetch_users()
    for k, v in request.form.to_dict().items():
      acc[current_user.id]["settings"][
        k] = True if v == "true" else False if v == "false" else v
    acc.supd()
  return jsonify(current_user.settings)


@app.route("/verify", methods=["post"])
@fresh_login_required
def __verify():
  user = current_user
  if current_user.id in ["stu001","teacher001"]:return jsonify(text="測試帳號不得變更電子郵件、名稱及密碼。"), 403
  r = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
  if request.form.get("email"):
    emails = fetch_json("static/jsons/email.json")
    if re.fullmatch(r, request.form.get("email")) and not request.form.get(
        "email", "") in emails:
      session["verify"] = str(uuid.uuid4())[:6]
      session["new_email"] = request.form.get("email")
      mail2(request.form.get("email"), "電子信箱變更驗證",
            f"您變更電子信箱的6碼驗證碼為:\n{session['verify']}")
      return "OK"

  elif request.form.get("verify"):
    if request.form.get("verify") == session.get("verify") and session.get(
        "new_email"):
      emails = {j: i for i, j in fetch_json("static/jsons/email.json")}
      old_email = emails[current_user.id]
      emails[current_user.id] = session["new_email"]
      remails = {j: i for i, j in emails.items()}
      remails.supd()
      tokens = fetch_json("static/jsons/tokens.json")
      token = str(uuid.uuid4())
      tokens[token] = {
        "recover": "email",
        "email": old_email,
        "user": current_user.id
      }
      tokens.supd()
      htmail(
        old_email, "電子信箱變更通知",
        render_template(
          "htmail.html",
          content=
          f"您的電子信箱已變更為:<br>{session.pop('new_email')}<br>若並非您執行此操作，請點擊<a href='https://hswm.up.railway.app/recover?token={token}' target='_blank'>此處</a>，盡速復原。<br>或複製以下網址並貼上至瀏覽器進行復原: https://hswm.up.railway.app/recover?token={token}"
        ))
      return "OK"
  elif request.form.get("old"):
    if not (request.form.get("new") and request.form.get("new2")):
      return jsonify(text="資料未輸入完全"), 400
    if not request.form.get("new") == request.form.get("new2"):
      return jsonify(text="兩次輸入的新密碼不同"), 400
    user.refresh_users()
    if not check_password_hash(user.users[user.id]["password"],
                               request.form.get("old")):
      return jsonify(text="原密碼錯誤"), 400
    users = fetch_users()
    users[user.id]["password"] = generate_password_hash(
      request.form.get("new"))
    users.supd()
    tokens = fetch_json("static/jsons/tokens.json")
    token = str(uuid.uuid4())
    tokens[token] = {"recover": "password", "user": current_user.id}
    tokens.supd()
    htmail(
      user.email, "密碼變更通知",
      render_template(
        "htmail.html",
        content=
        f"您的密碼已變更<br>若並非您執行此操作，請點擊<a href='https://hswm.up.railway.app/recover?token={token}' target='_blank'>此處</a>，盡速復原。<br>或複製以下網址並貼上至瀏覽器進行復原: https://hswm.up.railway.app/recover?token={token}"
      ))
    logout_user()
    return "OK"
  elif request.form.get("fullname"):
    users = fetch_users()
    users[current_user.id]["fullname"] = request.form.get("fullname")
    users.supd()
    return "OK"
  # print(json.dumps(request.form.to_dict(), indent=2, ensure_ascii=False))
  abort(400)


@app.route("/recover")
def __recover():
  token = request.args.get("token")
  tokens = fetch_json("static/jsons/tokens.json")

  if not token or not token in tokens:
    return render_template("redirects.html",
                           link="/",
                           letter="網址錯誤，有問題請洽管理員。",
                           header=render_template("header.html"),
                           footer=render_template("footer.html"))

  username = tokens[token]["user"]
  recover = tokens[token]["recover"]

  reversed_emails = {
    j: i
    for i, j in fetch_json("static/jsons/email.json").items()
  }
  if recover == "email":
    if username in reversed_emails:
      reversed_emails[username] = tokens[token]["email"]
      reversed_emails.upd({j: i for i, j in reversed_emails.items()})
      tokens = fetch_json("static/jsons/tokens.json")
      del tokens[token]
      tokens.supd()
      return render_template("redirects.html",
                             link="/settings",
                             letter="電子郵件回復完成，敬請盡速變更密碼。",
                             header=render_template("header.html"),
                             footer=render_template("footer.html"))

  elif recover == "password":
    mailto(reversed_emails[username], 1, (reversed_emails[username], username))
    current_user.password = session.get("password")
    reversed_emails.upd({j: i for i, j in reversed_emails.items()})
    tokens = fetch_json("static/jsons/tokens.json")
    del tokens[token]
    tokens.supd()
    return render_template("redirects.html",
                           link="/",
                           letter="已自動變更您的密碼，並傳送至您的電子信箱。",
                           header=render_template("header.html"),
                           footer=render_template("footer.html"))

  return render_template("redirects.html",
                         link="/",
                         letter="網址參數錯誤，有問題請洽管理員。",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"))


@app.route("/reporter", methods=["get", "post"])
def __reporter():
  if request.method.lower() == "post":
    return render_template("reporter.html",
                           header=render_template("header.html"),
                           mode=True)
  return render_template("reporter.html",
                         header=render_template("header.html"),
                         mode=False)


@app.route("/register", methods=["get", "post"])
def __register():
  warn = dict()
  if request.method.lower() == "post":
    form = request.form.to_dict()
    mapp = {"user": "帳號", "pswd": "密碼", "pswd2": "密碼確認", "email": "電子郵件"}
    r = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    for i, j in form.items():
      if not j:
        warn[i] = f"請輸入{mapp[i]}"
    if warn:
      return render_template(
        "register.html",
        header=render_template("header.html"),
        footer=render_template("footer.html"),
        # path=captcha(),
        warn=warn)
    if not form["pswd"] == form["pswd2"]:
      warn["pswd"] = "兩次輸入的密碼不一致"
    if not re.fullmatch(r, form["email"]):
      warn["email"] = "請輸入有效的Email"
    account = fetch_users()
    email = fetch_json("static/jsons/email.json")
    if form["user"] in account:
      warn["user"] = "使用者名稱已存在"
    if form["email"] in email:
      warn["user"] = "電子郵件已被使用"
    if not request.form["g-recaptcha-response"]:
      warn["g-recaptcha-response"] = "Google Recaptcha 未驗證"
    if warn == {}:
      res = requests.post('https://www.google.com/recaptcha/api/siteverify',
                          data={
                            'secret':
                            '6LeT8uskAAAAAOFOqbFBwhHpVbaXq_tg09i-BQQi',
                            "response": request.form["g-recaptcha-response"]
                          }).json()
      if not res["success"]:
        warn["g-recaptcha-response"] = "Google Recaptcha 驗證失敗"
    if warn:
      return render_template(
        "register.html",
        header=render_template("header.html"),
        footer=render_template("footer.html"),
        # path=captcha(),
        warn=warn)
    else:
      session["email_auth"] = "請輸入傳送至您電子信箱的6碼驗證碼"
      authen = str(uuid.uuid4().hex)[:6]
      mail2(form["email"], "信箱驗證信", f"您的電子郵件驗證碼為：\n{authen}")
      session["authen"] = authen

    session["user_info"] = {
      "email": form["email"],
      "username": form["user"],
      "password": generate_password_hash(form["pswd"])
    }
    return redirect("/register2")
  return render_template(
    "register.html",
    header=render_template("header.html"),
    footer=render_template("footer.html"),
    # path=captcha(),
    warn=warn)


@app.route("/register2", methods=["get", "post"])
def __register2():
  warn = dict()
  if not session.get("user_info"):
    return redirect("/register")
  if request.method.lower() == "post":
    form = request.form.to_dict()
    mapp = {
      "fullname": "全名",
      "number": "學號",
      "code": "班級代碼",
      "authen": "信箱驗證碼"
    }
    for i, j in form.items():
      if not j and not (i == "code" or i == "tcode"):
        if i == "number" and form["tcode"]: continue
        warn[i] = f"請輸入{mapp[i]}"
    if warn:
      return render_template(
        "register2.html",
        header=render_template("header.html"),
        footer=render_template("footer.html"),
        # path=captcha(),
        warn=warn)
    codes = fetch_json("static/jsons/code.json")
    tcodes = fetch_json("static/jsons/tcode.json")
    if form["code"] and not form["code"] in codes:
      warn["code"] = "班級代碼不存在。若不該如此，請洽管理員"
    elif form["tcode"] and not form["tcode"] in tcodes:
      warn["tcode"] = "教師代碼不存在。若不該如此，請洽管理員"
    if not form["authen"] == session.get("authen"):
      warn["authen"] = "信箱驗證碼錯誤"
    if not request.form["g-recaptcha-response"]:
      warn["g-recaptcha-response"] = "Google Recaptcha 未驗證"
    if warn == {}:
      res = requests.post('https://www.google.com/recaptcha/api/siteverify',
                          data={
                            'secret':
                            '6LeT8uskAAAAAOFOqbFBwhHpVbaXq_tg09i-BQQi',
                            "response": request.form["g-recaptcha-response"]
                          }).json()
      if not res["success"]:
        warn["g-recaptcha-response"] = "Google Recaptcha 驗證失敗"
    if warn:
      return render_template(
        "register2.html",
        header=render_template("header.html"),
        footer=render_template("footer.html"),
        # path=captcha(),
        warn=warn)

    userinfo = session["user_info"]
    if form["code"]:
      userinfo["class"] = codes[form["code"]]["class"]
      userinfo["department"] = codes[form["code"]]["department"]
      userinfo["role"] = "stu"
    elif form["tcode"]:
      userinfo["classes"] = []
      userinfo["role"] = "tch"
      userinfo["course"] = tcodes[form["tcode"]]
    else:
      userinfo["role"] = None

    userinfo["fullname"] = form["fullname"]
    userinfo["number"] = form["number"]
    userinfo["intro"] = "介紹"
    userinfo["avatar"] = "profile_pics/default/Default_Avatar.svg"
    userinfo["asistnt"] = []
    username = userinfo.pop("username")
    email = userinfo.pop("email")
    account = fetch_users()
    emails = fetch_json("static/jsons/email.json")
    account[username] = userinfo
    emails[email] = username
    account.supd()
    emails.supd()
    user = User()
    user.id = username
    User.refresh_users()
    login_user(user)
    sp = fetch_json("static/jsons/sp.json")
    sp[username] = {
      "sum":
      100,
      "entry": [{
        "change": 100,
        "reason": "註冊",
        "time": get_today("%Y-%m-%d %H:%M:%S")
      }]
    }
    sp.supd()
    session["msg"] = "註冊成功"
    return redirect("/")

  return render_template(
    "register2.html",
    header=render_template("header.html"),
    footer=render_template("footer.html"),
    # path=captcha(),
    warn=warn)


@app.route("/register3", methods=["get", "post"])
def __register3():
  warn = dict()
  if not session.get("user_info"):
    return redirect("/register")
  if request.method.lower() == "post":
    form = request.form.to_dict()
    mapp = {
      "fullname": "全名",
      "number": "學號",
      "code": "班級代碼",
      "pswd": "密碼",
      "pswd2": "密碼確認"
    }
    for i, j in form.items():
      if not j and not (i == "code" or i == "tcode"):
        if i == "number" and form["tcode"]: continue
        warn[i] = f"請輸入{mapp[i]}"
    if warn:
      return render_template(
        "register3.html",
        header=render_template("header.html"),
        footer=render_template("footer.html"),
        # path=captcha(),
        warn=warn)
    if not form["pswd"] == form["pswd2"]:
      warn["pswd"] = "兩次輸入的密碼不一致"
    codes = fetch_json("static/jsons/code.json")
    tcodes = fetch_json("static/jsons/tcode.json")
    if form["code"] and not form["code"] in codes:
      warn["code"] = "班級代碼不存在。若不該如此，請洽管理員"
    elif form["tcode"] and not form["tcode"] in tcodes:
      warn["tcode"] = "教師代碼不存在。若不該如此，請洽管理員"
    if not request.form["g-recaptcha-response"]:
      warn["g-recaptcha-response"] = "Google Recaptcha 未驗證"
    if warn == {}:
      res = requests.post('https://www.google.com/recaptcha/api/siteverify',
                          data={
                            'secret':
                            '6LeT8uskAAAAAOFOqbFBwhHpVbaXq_tg09i-BQQi',
                            "response": request.form["g-recaptcha-response"]
                          }).json()
      if not res["success"]:
        warn["g-recaptcha-response"] = "Google Recaptcha 驗證失敗"
    if warn:
      return render_template(
        "register3.html",
        header=render_template("header.html"),
        footer=render_template("footer.html"),
        # path=captcha(),
        warn=warn)
    userinfo = session["user_info"]
    if form["code"]:
      userinfo["class"] = codes[form["code"]]["class"]
      userinfo["department"] = codes[form["code"]]["department"]
      userinfo["role"] = "stu"
    elif form["tcode"]:
      userinfo["classes"] = []
      userinfo["role"] = "tch"
      userinfo["course"] = tcodes[form["tcode"]]
    else:
      userinfo["role"] = None
    userinfo["number"] = form["number"]
    userinfo["intro"] = "介紹"
    userinfo["avatar"] = userinfo.get(
      "avatar", "profile_pics/default/Default_Avatar.svg")
    userinfo["asistnt"] = []
    userinfo["password"] = generate_password_hash(form["pswd"])
    userinfo["username"] = userinfo["email"]
    username = userinfo.pop("email")
    del userinfo["username"]
    account = fetch_users()
    emails = fetch_json("static/jsons/email.json")
    account[username] = userinfo
    emails[username] = username
    account.supd()
    emails.supd()
    user = User()
    user.id = username
    User.refresh_users()
    login_user(user)
    sp = fetch_json("static/jsons/sp.json")
    sp[username] = {
      "sum":
      100,
      "entry": [{
        "change": 100,
        "reason": "註冊",
        "time": get_today("%Y-%m-%d %H:%M:%S")
      }]
    }
    sp.supd()
    session["msg"] = "註冊成功"
    return redirect("/")

  return render_template(
    "register3.html",
    header=render_template("header.html"),
    footer=render_template("footer.html"),
    # path=captcha(),
    warn=warn)


@app.route("/login", methods=["GET", "POST"])
def __login():
  if session.get("user_info"): del session["user_info"]
  warn = dict()
  if current_user:
    if current_user.is_authenticated:
      return redirect("/")
  next = request.args.get('next', "/")
  if next: session["next"] = next
  if request.method.lower() == "post":
    try:
      if request.form["reimg"] == "換下一張":
        return render_template(
          "login.html",
          header=render_template("header.html"),
          footer=render_template("footer.html"),
          # path=captcha(),
          user="",
          pswd="",
          captcha="",
          vu=request.form["user"],
          vp=request.form["pswd"],
          next=next if next else '/')
    except:
      None
    # try:
    #   cap = session.get("captcha")
    # except:
    #   warn["captcha"] = "非常抱歉！系統錯誤，請重新驗證！"
    #   return render_template("login.html",
    #                          header=render_template("header.html"),
    #                          footer=render_template("footer.html"),
    #                          # path=captcha(),
    #                          warn=warn,
    #                          vu=request.form["user"],
    #                          vp=request.form["pswd"],
    #                          next=next if next else '/')
    if not request.form["user"]:
      warn["user"] = "帳號不可為空"
    if not request.form["pswd"]:
      warn["pswd"] = "密碼不可為空"
    if not request.form["g-recaptcha-response"]:
      warn["g-recaptcha-response"] = "Google Recaptcha 未驗證"
    if warn == {}:
      re = requests.post('https://www.google.com/recaptcha/api/siteverify',
                         data={
                           'secret':
                           '6LeT8uskAAAAAOFOqbFBwhHpVbaXq_tg09i-BQQi',
                           "response": request.form["g-recaptcha-response"]
                         }).json()
      if not re["success"]:
        warn["g-recaptcha-response"] = "Google Recaptcha 驗證失敗"
      else:
        jdata = fetch_users()
        emails = fetch_json("static/jsons/email.json")
        if not request.form["user"] in jdata and not request.form[
            "user"] in emails:
          warn["user"] = "無此帳號"
        else:
          username = request.form["user"] if request.form[
            "user"] in jdata else emails[request.form["user"]]
          if not check_password_hash(jdata[username]["password"],
                                     request.form["pswd"]):
            warn["pswd"] = "密碼錯誤"
    if warn:
      return render_template(
        "login.html",
        header=render_template("header.html"),
        footer=render_template("footer.html"),
        # path=captcha(),
        warn=warn,
        vu=request.form["user"],
        vp="",
        next=next if next else '/')
    else:
      user = User()
      user.id = username
      remember = request.form.get("remember", False)
      re = True if remember == "True" else False
      email = {j: i
               for i, j in fetch_json("static/jsons/email.json").items()
               }[user.id]
      mail2(
        email, "登入通知",
        f"在{get_today('%Y年%m月%d日 %H時%M分')} (24小時制)時，\n有人從位置{get_ip(request)}登入您的帳號，\n若並非您進行此操作，敬請盡速變更密碼。"
      )
      login_user(user, re)
      try:
        os.remove("static/captchas/%s.png" % session["captcha"])
      except:
        None
      next = request.args.get('next', "/")
      session["user_pic"] = User.users[user.id]["avatar"]
      if request.args.get("deviceId") and request.form.get("rDevice", False):
        signed_device = fetch_json("static/jsons/signed_device.json")
        devices = []
        for i in signed_device.values():
          for j in i:
            devices.append(j)
        if not request.args.get("deviceId") in devices:
          if not username in signed_device:
            signed_device[username] = []
          signed_device[username].append(request.args.get("deviceId"))
          signed_device.supd()
        else:
          session["msg"] = "此裝置已有其他綁定。"
      return redirect(next)
  return render_template(
    "login.html",
    header=render_template("header.html"),
    footer=render_template("footer.html"),
    # path=captcha(),
    warn=warn,
    vu="",
    vp="",
    next=next if next else '/')


@app.route("/login_help")
def __login_help():

  return render_template("login_help.html",
                         content="<h2>↑請點選需求之登入幫助↑</h2>",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"))


@app.route("/notifications", methods=["get", "post"])
@login_required
def __notifications():
  notify = fetch_json("static/jsons/notifications.json")
  if request.method.lower() == "post" and request.form.get("index"):
    if request.form.get("index") != "*":
      del notify[current_user.id][int(request.form.get("index"))]
    else:
      notify[current_user.id] = []

    notify.supd()
    return "OK"
  return render_template("notifications.html",
                         notifications=[] if not current_user.id in notify else
                         notify[current_user.id],
                         header=render_template("header.html"),
                         footer=render_template("footer.html"))


@app.route("/help<int:id>", methods=["GET", "POST"])
def __help(id):

  warn = {"email": False, "username": False, "password": False}
  trans = {0: "username", 1: "password", 2: "both"}
  emails = fetch_json("static/jsons/email.json")
  accounts = fetch_users()
  if request.method.lower() == "post":
    if id == 0:
      if not request.form.get("email") in emails.keys():
        warn["email"] = True
      else:
        if not request.form.get("password") == accounts.get(
            emails.get(request.form.get("email"))).get("password"):
          warn["password"] = True
      if not request.form["password"]:
        warn["password"] = True

    elif id == 1:
      if not request.form.get("email") in emails.keys():
        warn["email"] = True
      else:
        if not request.form.get("username") == emails[request.form.get(
            "email")]:
          warn["username"] = True
    elif id == 2:
      if not request.form.get("email") in emails.keys():
        warn["email"] = True
    if True in warn.values():

      return render_template(
        "login_help.html",
        content=render_template(
          f"{trans[id]}.html",
          warn=("display" if warn["email"] else "none",
                "display" if warn["username"] else "none",
                "display" if warn["password"] else "none")),
        header=render_template("header.html"),
        footer=render_template("footer.html"))
    if id == 0:
      mailto(request.form.get("email"), id,
             (request.form.get("email"), request.form["password"]))
    elif id == 1:
      mailto(request.form.get("email"), id,
             (request.form.get("email"), request.form.get("username")))
    elif id == 2:
      data = fetch_json("static/jsons/fgup.json")
      with open("static/jsons/fgup.json", mode="w") as f:
        data[request.form.get("email")] = {
          "time": get_today("%Y-%m-%d %H:%M"),
          "請求內容": request.form["auth"],
          "stat": "pending"
        }
        f.write(json.dumps(data))
        f.close()
      mailto(request.form.get("email"), 2, ())
      return render_template(
        "header.html"
      ) + "<h3 class='text-center'>提出申請成功。</h3><br><a href='/'><button type='button' class='btn btn-lg btn-primary' style='width:30%;margin-left:35%;'>回首頁</button></a>" + render_template(
        "footer.html")

    return render_template(
      "header.html"
    ) + "<h3 class='text-center'>已嘗試寄出登入相關資料至您的電子郵件信箱，若幾分鐘內信件未出現在收件匣內，請查看垃圾郵件匣，或請連絡管理員。</h3><br><a href='/'><button type='button' class='btn btn-lg btn-primary' style='width:30%;margin-left:35%;'>回首頁</button></a>" + render_template(
      "footer.html")
  return render_template("login_help.html",
                         content=render_template(f"{trans[id]}.html",
                                                 warn=("none", "none",
                                                       "none")),
                         header=render_template("header.html"),
                         footer=render_template("footer.html"))


@app.route("/clear_captchas", methods=["POST", "GET"])
def __clear_captchas():

  if request.method.lower() == "post":
    if request.form["pswd"] == "2248":
      for i in os.listdir("static/captchas/"):
        os.remove(f"static/captchas/{i}")
      return render_template("redirects.html",
                             link="/",
                             letter="清除成功，重新導向首頁‧‧‧",
                             header=render_template("header.html"),
                             footer=render_template("footer.html"))
    else:
      return render_template("header.html") + """
          <h1>輸入清除密碼</h1>
          <form action="/clear_captchas" method="post">
          <input type="password" name="pswd">
          <div style="color:red;">密碼錯誤</div>
          <input type="submit" value="送出清除請求">
          </form>
          """
  return render_template("header.html") + """
          <h1>輸入清除密碼</h1>
          <form action="/clear_captchas" method="post">
          <input type="password" name="pswd">
          <input type="submit" value="送出清除請求">
          </form>
          """


@app.route("/profile", methods=["get", "post"])
@login_required
def __profile():
  user = current_user
  users = fetch_users()
  userinfo = users[user.id]
  points = None
  try:
    points = fetch_json("static/jsons/sp.json")[user.id]["sum"]
  except:
    None
  if request.method.lower() == "post":
    ava = request.files.get("pfile")
    if not ava:
      return redirect("/profile")
    if not userinfo["avatar"].startswith("http") and not userinfo[
        "avatar"] == "profile_pics/default/Default_Avatar.svg":
      os.remove("static/" + userinfo["avatar"])
    ava_path = f"profile_pics/{secure_filename(user.id+'.'+get_extension(ava.filename))}"
    ava.save("static/" + ava_path)
    users[user.id]["avatar"] = ava_path
    users.supd()
    return redirect("/profile")
  return render_template("profile.html",
                         userinfo=userinfo,
                         header=render_template("header.html"),
                         footer=render_template("footer.html"),
                         user_id=user.id,
                         points=points,
                         users=users)


@app.route("/pentry")
@login_required
def __pentry():
  user = current_user
  if not user.is_student: return redirect("/")
  entry = fetch_json("static/jsons/sp.json")[user.id]["entry"]
  return render_template("pentry.html",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"),
                         entry=entry)


# @app.route("/p<name>")
# def __pname(name):
#   return redirect("/@" + name)


@app.route("/@<name>")
def __atname(name):
  users = fetch_users()
  if not name in users.keys():
    session["msg"] = "查無個人檔案"
    return redirect("/")

  userinfo = users[name]
  fl = []
  if current_user.is_authenticated:
    fl = [
      i[1]
      for i in fetch_json("static/jsons/friend_list.json")[current_user.id]
    ]
  return render_template("profile.html",
                         userinfo=userinfo,
                         header=render_template("header.html"),
                         footer=render_template("footer.html"),
                         user_id=name,
                         users=users,
                         fl=fl)


@app.route("/pedit", methods=["post"])
@login_required
def __pedit():
  user = current_user
  data = fetch_users()
  data[user.id]["intro"] = request.form.get("content", "")
  data.supd()
  return data[user.id]["intro"]


@app.route("/rs", methods=["post"])
def __rs():
  if request.form.get("key") in session:
    del session[request.form.get("key")]
  return "ok"


@app.route("/logout", methods=["get", "post"])
@login_required
def __logout():
  if request.method.lower() == "post":
    if request.args.get("deviceId"):
      signed_device = fetch_json("static/jsons/signed_device.json")
      if current_user.id in signed_device:
        if request.args.get("deviceId") in signed_device[current_user.id]:
          signed_device[current_user.id].remove(request.args.get("deviceId"))
          signed_device.supd()
    logout_user()
    s = session.get("dark")
    session.clear()
    session["dark"] = s
    return render_template(
      "redirects.html",
      link="/",
      letter="已登出<h2 style='text-align:center;'>祝您有個美好的一天</h2>",
      header=render_template("header.html"),
      footer=render_template("footer.html"))
  return render_template("logout.html",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"))


@app.route("/fgupr", methods=["get", "post"])
@login_required
def __fgupr():
  user = current_user
  em = request.args.get("email")
  if not user.is_admin:
    return redirect("/")
  m = {"solved": "已完成", "processing": "處理中", "pending": "等待中"}
  data = fetch_json("static/jsons/fgup.json")
  for key, value in data.items():
    value["stat"] = m[value["stat"]]
    if value[
        "請求內容"] == "~~\u8eab\u5206\u8b49\u660e\u8cc7\u6599~~\r\n\u5982\u5168\u540d\u3001\u73ed\u7d1a\u3001\u79d1\u5225\u3001\u6559\u5c0e\u73ed\u7d1a(\u50c5\u6559\u5e2b)\u7b49\u3002\r\n    " or not value[
          "請求內容"]:
      value["請求內容"] = "無"
    if em: break
    if value["請求內容"]:
      if len(value["請求內容"]) >= 10:
        value["請求內容"] = value["請求內容"][:7] + "..."
      else:
        value["請求內容"] = value["請求內容"] + "..."
  if em:
    if request.method.lower() == "post":
      if request.form.get("submit") == "確認":
        data1 = fetch_json("static/jsons/fgup.json")
        del data1[em]
        data1.supd()
        return redirect("/fgupr")
      elif request.form.get("submit") == "送出":
        data1 = fetch_json("static/jsons/fgup.json")
        mail(em, "帳密重設申請回覆", request.form.get("reply"))
        data1[em]["stat"] = "solved"
        data1.supd()
        return render_template("redirects.html",
                               link="/fgupr",
                               letter="已送出回覆，並變更狀態",
                               header=render_template("header.html"),
                               footer=render_template("footer.html"))
      elif request.form.get("submit") == "確認變更":
        data = fetch_json("static/jsons/fgup.json")
        data[em]["stat"] = request.form.get("stat")
        data.supd()
        return render_template("redirects.html",
                               link="/fgupr",
                               letter="已變更狀態",
                               header=render_template("header.html"),
                               footer=render_template("footer.html"))

    data0 = fetch_json("static/jsons/fgup.json")

    em = request.args.get("email")
    if em in data0.keys():
      udata = data0[em]
      udata["stat"] = m[udata["stat"]]
      udata["請求內容"] = udata["請求內容"].replace("\n", "<br>")
    else:
      return redirect("/fgupr")
    return render_template("fgupc.html",
                           data=udata,
                           email=em,
                           header=render_template("header.html"),
                           footer=render_template("footer.html"))
  return render_template("fgupr.html",
                         datas=data.items(),
                         header=render_template("header.html"),
                         footer=render_template("footer.html"))


@app.route("/pdfs/<filename>")
def __file(filename):
  if not (filename.startswith(current_user.id) or filename.startswith(current_user.certi_id)): return redirect("/")
  return send_from_directory(os.path.join(app.root_path, 'static/pdfs'),
                             filename)


@app.route("/setSession", methods=["post"])
def __setSession():
  session[request.form.get('key')] = request.form.get('val')
  return "OK"


@socketio.on('message')
def handle_message(data):
  fl = fetch_json("static/jsons/friend_list.json")
  signed_device = fetch_json("static/jsons/signed_device.json")
  recipient = data['recipient']
  message = data['message']
  socketio.emit('message', {
    "msg":
    message,
    "sender":
    current_user.id,
    "time":
    get_today('%H:%M'),
    "date":
    get_today('%Y-%m-%d'),
    "avatar":
    current_user.avatar if f"{current_user.avatar}".startswith("http") else
    f"/static/{current_user.avatar}",
    "recipient":
    recipient
  },
                room=recipient)
  socketio.emit("unread", {"recipient": recipient},
                include_self=False,
                broadcast=True)

  db = fetch_db(f'static/jsons/dbs/main.db')
  db.cs.execute(
    f'''INSERT INTO msg{recipient} VALUES(null,'{message}','{current_user.id}','{get_today("%Y-%m-%d")}','{get_today("%H:%M:%S")}','unread')'''
  )
  db.db.commit()
  db.close()
  l = [j[1] for i in fl.values() for j in i if j[0] == recipient]
  notifications = fetch_json("static/jsons/notifications.json")
  users = fetch_users()
  for i in l:
    if not i in signed_device:
      signed_device[i] = []
    if not i in users: continue
    if i == current_user.id or not users[i].get("settings", {}).get(
        "NMSG-Notify", True):
      continue
    if not i in notifications:
      notifications[i] = []
    notifications[i].insert(
      0, {
        "title": "您有新訊息",
        "content": message,
        "stat": "unsend",
        "link": f"/chat/",
        "time": get_today("%Y-%m-%d %H:%M"),
        "bg-color": "bg-info-subtle",
        "icon": "bi-chat-left"
      })

  notifications.supd()
  signed_device.supd()
  fl.supd()

  messaging.send_multicast(
    messaging.MulticastMessage([
      j for k in l for j in signed_device[k] if k and not k == current_user.id
    ],
                               android=messaging.AndroidConfig(
                                 notification=messaging.AndroidNotification(
                                   title="您有新訊息", body=message),
                                 collapse_key="HsWM1060060422")))


@socketio.on('connect')
def connect():
  session["last_room"] = session.get("current_room", "*")
  join_room(session.get("current_room", "*"))


@socketio.on('disconnect')
def disconnect():
  leave_room(session.get("last_room", "*"))


compress = Compress()
compress.init_app(app)

if __name__=="__main__":
  # app.run(host="0.0.0.0", port=8080, debug=True)
  from dirs import dirs
  for i in dirs:
    if not os.path.exists(i):
      try:
        os.mkdir(i)
        print(f"dir made: {i}")
      except Exception as e:
        print(f"error occurred when making dir: {i}\n\nERROR:{e}")
    else:print(f"dir checked: {i}")

  http_server = WSGIServer(('0.0.0.0', int(os.environ.get("PORT",3000))),
                         app,
                         handler_class=WebSocketHandler,
                         log=sys.stdout)

  try:
    db = fetch_db("static/jsons/dbs/console.db")
    db.cs.execute("select count(*) from main")
    if int(db.cs.fetchone()[0]) > 1000:
      os.remove("static/jsons/dbs/console.db")
  except Exception as e:
    print("db deleting Error:", e)
  try:
    db = fetch_db("static/jsons/dbs/error.db")
    db.cs.execute("select count(*) from main")
    if int(db.cs.fetchone()[0]) > 1000:
      os.remove("static/jsons/dbs/error.db")
  except Exception as e:
    print("db deleting Error:", e)
  print("server_start:" + get_today("%Y-%m-%d@%H:%M:%S") + "\n\n" + "=" * 10)
  # socketio.emit('reload')
  # print("all_user_reloaded")

  http_server.serve_forever()
