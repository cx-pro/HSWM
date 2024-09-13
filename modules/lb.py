from .imports import *
from .funcs import *
from flask import Blueprint
from .user import User

lb = Blueprint("lb", __name__)


@lb.route("/linebot", methods=['POST'])
def callback():
  signature = request.headers['X-Line-Signature']
  body = request.get_data(as_text=True)
  try:
    handler.handle(body, signature)
  except InvalidSignatureError:
    print(
      "Invalid signature. Please check your channel access token/channel secret."
    )
    abort(400)
  return 'OK'


def __get_data(filename: str):
  return fetch_json(f"static/jsons/{filename}.json")


@lb.route("/login_success")
def __login_success():
  return render_template("log_success.html",
                         t1="綁定成功！",
                         t2="可關閉此頁面回到機器人再次呼叫選單",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"))


@lb.route("/line_login", methods=["get", "post"])
def __line_login():
  userid = request.args.get("user_id")
  session["next"] = "/login_success"
  warn = dict()
  if current_user.is_authenticated:
    logins = __get_data("login")
    logins[userid] = {
      "role": "asistnt" if current_user.is_asistnt else current_user.role,
      "username": current_user.id
    }

    logins.supd()
    return redirect("/login_success")
  if request.method.lower() == "post":
    try:
      if request.form["reimg"] == "換下一張":
        return render_template(
          "line_login.html",
          header=render_template("header.html"),
          footer=render_template("footer.html"),
          # path=captcha(),
          user="",
          pswd="",
          captcha="",
          vu=request.form["user"],
          vp=request.form["pswd"])
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
        if not jdata.get(
            request.form["user"]) and not request.form["user"] in emails:
          warn["user"] = "無此帳號"
        else:
          username = request.form["user"] if not request.form[
            "user"] in emails else emails[request.form["user"]]
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
        vp="")
    else:
      user = User()
      user.id = username
      remember = request.form.get("remember", False)
      re = True if remember == "True" else False
      email = fetch_json("static/jsons/email.json").KVSwap()[user.id]
      mail2(
        email, "登入通知",
        f"在{get_today('%Y年%m月%d日 %H時%M分')} (24小時制)時，\n有人從位置{get_ip(request)}登入您的帳號，\n若並非您進行此操作，敬請盡速變更密碼。"
      )
      login_user(user, re)
      logins = __get_data("login")
      logins[userid] = {
        "role": "asistnt" if current_user.is_asistnt else current_user.role,
        "username": current_user.id
      }

      logins.supd()
      try:
        os.remove("static/captchas/%s.png" % session["captcha"])
      except:
        None
      session["user_pic"] = User.users[user.id]["avatar"]
      return redirect("/login_success")
  return render_template(
    "line_login.html",
    header=render_template("header.html"),
    footer=render_template("footer.html"),
    # path=captcha(),
    warn=warn,
    userid=userid)


@lb.route("/line_logout", methods=["get", "post"])
def __logout():
  userid = request.args.get("user_id")
  if request.method.lower() == "post":
    if current_user.is_authenticated: logout_user()
    s = session.get("dark")
    session.clear()
    session["dark"] = s
    logins = __get_data("login")
    try:
      del logins[userid]
    except KeyError:
      None
    logins.supd()
    return render_template("log_success.html",
                           t1="綁定解除成功！",
                           t2="可關閉此頁面回到機器人再次呼叫選單",
                           header=render_template("header.html"),
                           footer=render_template("footer.html"))
  return render_template("line_logout.html",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"),
                         userid=userid)


@handler.add(PostbackEvent)
def handle_postback(event):
  flexs = __get_data("flexs")
  login = __get_data("login")
  users = __get_data("account")
  recive = event.postback.data
  userid = event.source.user_id
  if recive == "login":
    rp = flexs["flex_login"]
    rp["body"]["contents"][0]["action"]["uri"] += userid
    line_bot_api.reply_message(event.reply_token,
                               FlexSendMessage(alt_text="按此登入", contents=rp))

  elif recive == "logout":
    rp = flexs["flex_logout"]
    rp["body"]["contents"][0]["action"]["uri"] += userid
    line_bot_api.reply_message(event.reply_token,
                               FlexSendMessage(alt_text="按此登出", contents=rp))

  elif recive == "view_task":
    if not userid in login:
      rp = flexs["flex_login"]
      rp["body"]["contents"][0]["action"]["uri"] += userid
      rp["body"]["contents"][0]["action"]["label"] = "請先登入"
      line_bot_api.reply_message(event.reply_token,
                                 FlexSendMessage(alt_text="請先登入", contents=rp))
      return
    if userid in login:
      clas = users[login[userid]["username"]].get("class")
      if not clas:
        line_bot_api.reply_message(event.reply_token,
                                   TextSendMessage(text="您沒有班級。若有錯誤請回報管理員。"))
        return
      tasks = __get_data(f"tasks/{clas}")
      task_list = flexs["tasks"]
      task0 = flexs["task"]
      task = deepcopy(task0)
      task["hero"]["contents"][0]["text"] = "說明"
      task["body"]["contents"][0]["contents"][0]["text"] = "本處僅顯示最多前8項作業"
      task["body"]["contents"][0]["contents"][1][
        "text"] = "建議按下方按鈕前往行事曆\n查看完整內容"
      task["body"]["contents"][0]["contents"][1]["wrap"] = True
      task["body"]["contents"][0]["contents"][2]["text"] = "若查無作業則僅顯示此二說明"
      task["body"]["contents"][1]["contents"][0]["text"] = "系統"
      task["footer"]["contents"][0]["action"]["label"] = f"前往行事曆"
      task["footer"]["contents"][0]["action"]["uri"] += f"?user_id={userid}"
      task_list["contents"].append(task)
      task = deepcopy(task0)
      task["hero"]["contents"][0]["text"] = "範例"
      task["body"]["contents"][0]["contents"][0]["text"] = "開始日期 時間"
      task["body"]["contents"][0]["contents"][2]["text"] = "結束日期 節數"
      task["body"]["contents"][1]["contents"][0]["text"] = "作業指派人"
      task["footer"]["contents"][0]["action"]["type"] = "postback"
      task["footer"]["contents"][0]["action"]["data"] = " "
      task["footer"]["contents"][0]["action"]["label"] = f"按此可看內容(範例)"
      task_list["contents"].append(task)

      tasks1 = deepcopy(tasks)
      data1 = dict()
      for k1, v1 in tasks1.items():
        for k2, v2 in v1.items():
          v2["url"] = f"{k1}_{k2}"
          data1[v2["end_date"] + k2] = v2
      latest_task = {
        n["url"]: n
        for k, n in dict(sorted(list(data1.items()))).items()
      }
      for k1, v2 in list(latest_task.items())[:8]:
        task = deepcopy(task0)
        task["hero"]["contents"][0]["text"] = v2["title"]
        task["body"]["contents"][0]["contents"][0]["text"] = v2["start_time"]
        task["body"]["contents"][0]["contents"][2][
          "text"] = f'{v2["end_date"]} {v2["end_time"]}'
        task["body"]["contents"][1]["contents"][0]["text"] = users[
          v2["tasker"]]["fullname"]
        task["footer"]["contents"][0]["action"][
          "uri"] += f"content{k1}?user_id={userid}"
        task_list["contents"].append(task)

      line_bot_api.reply_message(
        event.reply_token, FlexSendMessage(alt_text="工作列表",
                                           contents=task_list))

  elif recive == "ask":
    if not userid in login:
      rp = flexs["flex_login"]
      rp["body"]["contents"][0]["action"]["uri"] += userid
      rp["body"]["contents"][0]["action"]["label"] = "請先登入"
      line_bot_api.reply_message(event.reply_token,
                                 FlexSendMessage(alt_text="請先登入", contents=rp))
      return
    rp = flexs["flex_logout"]
    rp["body"]["contents"][0]["action"][
      "uri"] = "https://hswm.up.railway.app/qa/qas?defa=add&user_id=" + userid
    rp["body"]["contents"][0]["action"]["label"] = "按此發問"
    line_bot_api.reply_message(event.reply_token,
                               FlexSendMessage(alt_text="按此發問", contents=rp))

  elif recive == "add_task":
    if not userid in login:
      rp = flexs["flex_login"]
      rp["body"]["contents"][0]["action"]["uri"] += userid
      rp["body"]["contents"][0]["action"]["label"] = "請先登入"
      line_bot_api.reply_message(event.reply_token,
                                 FlexSendMessage(alt_text="請先登入", contents=rp))
      return
    classes = flexs["classes"]
    cls0 = flexs["class"]
    users = __get_data("account")
    if login[userid]["role"] == "asistnt":
      l = [users[login[userid]["username"]]["class"]]
    else:
      l = users[login[userid]["username"]]["classes"]
    for i in l:
      cls = deepcopy(cls0)
      cls["hero"]["contents"][0]["text"] = i
      cls["footer"]["contents"][0]["action"]["uri"] += i + "?user_id=" + userid
      classes["contents"].append(cls)
    line_bot_api.reply_message(
      event.reply_token, FlexSendMessage(alt_text="班級列表", contents=classes))
  elif recive == "add_certi":
    if not userid in login:
      rp = flexs["flex_login"]
      rp["body"]["contents"][0]["action"]["uri"] += userid
      rp["body"]["contents"][0]["action"]["label"] = "請先登入"
      line_bot_api.reply_message(event.reply_token,
                                 FlexSendMessage(alt_text="請先登入", contents=rp))
      return
    rp = flexs["flex_logout"]
    rp["body"]["contents"][0]["action"][
      "uri"] = "https://hswm.up.railway.app/certi/certificate?user_id=" + userid
    rp["body"]["contents"][0]["action"]["label"] = "按此新增獎狀"
    line_bot_api.reply_message(event.reply_token,
                               FlexSendMessage(alt_text="按此新增獎狀", contents=rp))


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
  recive = event.message.text

  reply_type, reply_content = Lreply(recive.lower(), event)
  if reply_type == "chat":
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
  elif reply_type == "flex":
    line_bot_api.reply_message(
      event.reply_token,
      FlexSendMessage(alt_text="圖文訊息", contents=reply_content))


def Lreply(rc, event):
  user = event.source.user_id
  kword = __get_data("kword")
  flexs = __get_data("flexs")
  login = __get_data("login")
  reply = __get_data("reply")
  if rc in kword:
    rc = kword[rc]
  rt = "reply"
  r = reply.get(rc,
                "非常抱歉，小幫手沒辦法辨識您的需求，建議輸入 [選單]/[menu] 或按下圖文選單上的選單字樣，再選擇您需要的功能。")
  if r.startswith("flex_"):
    rt = "flex"
    if r.startswith("flex_menu"):
      r = flexs["flex_menu"]
      user_data = login.get(user)
      role = ""
      if user_data: role = user_data["role"]
      if role: r = flexs[f"flex_menu_{role}"]
    else:
      r = flexs[r]
  return (rt, r)
