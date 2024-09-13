from .imports import *


class notify:

  @staticmethod
  def set(message, id=""):
    if not session.get("notifications"): session["notifications"] = dict()
    if id:
      if isinstance(message, list):
        raise TypeError(
          "Argument 'message' must be str when argument 'id' is given.")
      session["notifications"][id] = message
      re = id
    else:
      if isinstance(message, str):
        ind = str(uuid.uuid4())
        while ind in session["notifications"]:
          ind = str(uuid.uuid4())
        session["notifications"][ind] = message
        re = ind
      else:
        re = []
        for msg in message:
          ind = str(uuid.uuid4())
          while ind in session["notifications"]:
            ind = str(uuid.uuid4())
          session["notifications"][ind] = message
          re.append(ind)
    session["notification_set"] = True
    return re

  @staticmethod
  def delete(mID=None):
    if not session.get("notifications"): return
    if not mID: session["notifications"].clear()
    if mID in session["notifications"]: del session["notifications"][mID]


class fetch_db():

  def __init__(self, path):
    self.db = sqlite3.connect(path)
    self.cs = self.db.cursor()

  def rdb(self, path):
    self.cs.close()
    self.db.close()
    self.db = sqlite3.connect(path)
    self.cs = self.db.cursor()

  def close(self):
    self.cs.close()
    self.db.close()


def write_json(path, data):
  with open(path, mode="wb") as wf:
    fcntl.flock(wf, fcntl.LOCK_EX)
    wf.write(orjson.dumps(data))
    fcntl.flock(wf, fcntl.LOCK_UN)
    wf.close()


class fetch_list(list):

  def __init__(self, path):
    self._path = path
    if os.path.exists(path):
      with open(path, mode="rb") as f:
        re = orjson.loads(f.read())
        f.close()
      self._data = re
      super().__init__(re)
    else:
      write_json(path, [])
      super().__init__([])

  def KVSwap(self):
    return None

  def supd(self):
    write_json(self._path, list(self))

  def upd(self, data):
    self._data = data
    self.clear()
    for i in data:
      self.append(i)
    write_json(self._path, data)

  @property
  def is_dict(self):
    return False

  @property
  def maxKey(self):
    return -1


class fetch_json(dict):

  def __init__(self, path, **kwargs):
    self._path = path
    if os.path.exists(path):
      with open(path, mode="rb") as f:
        re = orjson.loads(f.read())
        f.close()
      self._data = re
      super().__init__(re, **kwargs)
    else:
      write_json(path, {})
      super().__init__({}, **kwargs)

  def KVSwap(self):
    return {j: i for i, j in self._data.items()}

  def supd(self):
    write_json(self._path, dict(self.items()))

  def upd(self, data):
    self._data = data
    self.clear()
    for k, v in data.items():
      self[k] = v
    write_json(self._path, self._data)

  @property
  def is_dict(self):
    return True

  @property
  def maxKey(self):
    kl = list(self.keys())
    f = True
    for i in kl:
      if not i.isdigit(): f = False
    if f:
      kl = list(map(int, kl))
    return max(kl) if kl else -1



class fetch_users(fetch_json):

  def __init__(self, **kwargs):
    super().__init__("static/jsons/account.json", **kwargs)


def get_today(format: str = "%a"):
  return datetime.datetime.utcnow().replace(
    tzinfo=datetime.timezone.utc).astimezone(
      datetime.timezone(datetime.timedelta(hours=8))).strftime(format).upper()


def week_dates():
  return [
    j.strftime("%d") for j in [
      i for i in calen.monthdatescalendar(int(get_today(
        "%Y")), int(get_today("%m"))) if datetime.datetime.strptime(
          get_today("%Y-%m-%d"), "%Y-%m-%d").date() in i
    ][0]
  ]


weekdays = {
  "Sun": "星期日",
  "Mon": "星期一",
  "Tue": "星期二",
  "Wed": "星期三",
  "Thu": "星期四",
  "Fri": "星期五",
  "Sat": "星期六"
}

course_l = [
  "早自習", "第一節", "第二節", "第三節", "第四節", "午  休", "第五節", "第六節", "第七節", "第八節", "第九節"
]
date_l = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
last_index = -1
# with open("main.json",encoding="utf8") as f:
#     data=json.load(f)
#     f.close()
maps = dict()
for i in course_l:
  maps[i] = dict()
  for j in date_l:
    last_index += 1
    maps[i][j] = last_index
day = [
  "星期一<br />MON", "星期二<br />TUE", "星期三<br />WED", "星期四<br />THU",
  "星期五<br />FRI", "星期六<br />SAT", "星期日<br />SUN"
]
day_bools = [
  "green"
  if get_today() in i else "red" if "SUN" in i or "SAT" in i else "black"
  for i in day
]
cls0 = [
  "早自習<br />07:30～08:10", "第一節<br />08:10～09:00", "第二節<br />09:10～10:00",
  "第三節<br />10:10～11:00", "第四節<br />11:10～12:00", "午  休",
  "第五節<br />13:20～14:10", "第六節<br />14:15～15:05", "第七節<br />15:25～16:15",
  "第八節<br />16:20～17:10", "第九節<br />17:15～18:05"
]
cls = [
  "早自習", "第一節", "第二節", "第三節", "第四節", "午  休", "第五節", "第六節", "第七節", "第八節", "第九節"
]

cls_id = [list(range(i, i + 7)) for i in range(0, 77, 7)]


def captcha():
  try:
    os.remove("static/captchas/%s.png" % session["captcha"])
  except:
    None
  font_path = "static/arial.ttf"
  number = 5
  size = (100, 30)
  bgcolor = (255, 255, 255)
  draw_line = False

  cap_string = "123456789qwertyuiopasdfghjkzxcvbnml"

  x_start = 2
  y = 0
  width, height = size
  image = Image.new('RGBA', (width, height), bgcolor)
  font = ImageFont.truetype(font_path, 25)
  drawpen = ImageDraw.Draw(image)
  cap = {"captcha_text": ""}

  def random_pick():
    ans = rd.choice(cap_string)
    cap["captcha_text"] += ans
    return ans

  for i in range(number):
    x = x_start + i * int(width / (number))
    fontcolor = (rd.randint(0, 255), rd.randint(0, 255), rd.randint(0, 255))
    drawpen.text((x, y), text=random_pick(), font=font, fill=fontcolor)
  path = "static/captchas/%s.png" % cap["captcha_text"]
  session["captcha"] = cap["captcha_text"]
  image.save(path)
  return path


def get_extension(s: str):
  return s[-s[::-1].find("."):]


#-----------------------------
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def mailto(address: str, mode: int, args: tuple):
  if address.endswith("@demo.com"):return
  title = "帳號" if mode == 0 else "密碼" if mode == 1 else "帳密"
  content = MIMEMultipart()  #建立MIMEMultipart物件
  content["subject"] = f"高中職小幫手｜登入協助 — {title}"  #郵件標題
  content["from"] = "ksvcs13web@gmail.com"  #寄件者
  content["to"] = address  #收件者
  if mode == 0:
    emails = fetch_json("static/jsons/email.json")
    ct = "使用者帳號 → " + emails[
      args[0]] + "\n若您並未申請以上動作，請立即前往變更密碼。\n~~~~~~~~~~本郵件由系統發出，請勿回覆~~~~~~~~~~"
  elif mode == 1:
    emails = fetch_json("static/jsons/email.json")
    pswdr = "qwertyoiupasdfghlkjzxcvbnm" + "qwertyoiupasdfghlkjzxcvbnm".upper(
    ) + "123465789"
    pswd = ""
    for i in range(10):
      pswd += rd.choice(pswdr)
    ct = "使用者密碼已重置 → " + pswd + "\n請盡快使用新的密碼登入並變更您的密碼\n若您並未申請以上動作，請立即前往變更密碼。\n~~~~~~~~~~本郵件由系統發出，請勿回覆~~~~~~~~~~"
    accounts = fetch_users()
    accounts[emails[args[0]]]["password"] = generate_password_hash(pswd)
    accounts.supd()
    session["__password"] = accounts[emails[args[0]]]["password"]
    del accounts
  elif mode == 2:
    fgups = fetch_json("static/jsons/fgup.json")
    ct = f"""請求待審核...\n以下是使用者的請求內容:\n-----使用者電子信箱：{address}-----\n使用者請求內容：\n{fgups[address]['請求內容']}\n~~~~~~~本郵件由系統發出，請勿回覆~~~~~~~"""

  accounts = fetch_users()
  content.attach(MIMEText("""您的登入資訊如下：
  {}""".format(ct)))  #郵件內容
  admins = list()
  for name, value in accounts.items():
    if value.get("role") == "adm": admins.append(name)
  email_data = fetch_json("static/jsons/email.json")
  email_data2 = dict()
  for e, u in email_data.items():
    email_data2[u] = e
  mails = {i: email_data2[i] for i in admins}
  with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
    smtp.ehlo()  # 驗證SMTP伺服器
    smtp.starttls()  # 建立加密傳輸
    smtp.login("ksvcs13web@gmail.com", os.environ['gmail_key'])  # 登入寄件者gmail
    smtp.send_message(content)  # 寄送郵件
    if mode == 2:
      for admin, addr in mails.items():
        content = MIMEMultipart()  #建立MIMEMultipart物件
        content["subject"] = f"高中職小幫手｜登入協助 — {title}"  #郵件標題
        content["from"] = "ksvcs13web@gmail.com"  #寄件者
        content["to"] = addr  #收件者
        content.attach(
          MIMEText(f"""{admin}您好，使用者申請重設帳密：
    {ct}\n~~~~~~~~~~本郵件由系統發出，請勿回覆~~~~~~~~~~"""))
        smtp.send_message(content)
    smtp.close()



def mail(address: str, title: str, ct: str):
  if address.endswith("@demo.com"):return
  content = MIMEMultipart()  #建立MIMEMultipart物件
  content["subject"] = f"高中職小幫手｜{title}"  #郵件標題
  content["from"] = "ksvcs13web@gmail.com"  #寄件者
  content["to"] = address  #收件者
  content.attach(
    MIMEText("""您的登入協助申請回覆如下：\n
  {}\n~~~~~~~~~~本郵件由系統發出，請勿回覆~~~~~~~~~~""".format(ct)))  #郵件內容
  with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
    smtp.ehlo()  # 驗證SMTP伺服器
    smtp.starttls()  # 建立加密傳輸
    smtp.login("ksvcs13web@gmail.com", os.environ['gmail_key'])  # 登入寄件者gmail
    smtp.send_message(content)  # 寄送郵件


def get_ip(request):
  return request.environ['REMOTE_ADDR'] if request.environ.get('HTTP_X_FORWARDED_FOR') is None else request.environ['HTTP_X_FORWARDED_FOR']


def mail2(address: str, title: str, ct: str):
  if address.endswith("@demo.com"):return
  content = MIMEMultipart()  #建立MIMEMultipart物件
  content["subject"] = f"高中職小幫手｜{title}"  #郵件標題
  content["from"] = "ksvcs13web@gmail.com"  #寄件者
  content["to"] = address  #收件者
  content.attach(
    MIMEText("""{}\n~~~~~~~~~~本郵件由系統發出，請勿回覆~~~~~~~~~~""".format(ct)))  #郵件內容
  with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
    smtp.ehlo()  # 驗證SMTP伺服器
    smtp.starttls()  # 建立加密傳輸
    smtp.login("ksvcs13web@gmail.com", os.environ['gmail_key'])  # 登入寄件者gmail
    smtp.send_message(content)  # 寄送郵件


def htmail(address: str, title: str, ct: str):
  if address.endswith("@demo.com"):return
  content = MIMEMultipart()  #建立MIMEMultipart物件
  content["subject"] = f"高中職小幫手｜{title}"  #郵件標題
  content["from"] = "ksvcs13web@gmail.com"  #寄件者
  content["to"] = address  #收件者
  content.attach(MIMEText(ct, "html"))  #郵件內容
  with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
    smtp.ehlo()  # 驗證SMTP伺服器
    smtp.starttls()  # 建立加密傳輸
    smtp.login("ksvcs13web@gmail.com", os.environ['gmail_key'])  # 登入寄件者gmail
    smtp.send_message(content)  # 寄送郵件


def get_filename(path):
  while "/" in path:
    path = path[path.find("/") + 1:]
  return path


#------------------------
def pdf(strs: dict,user:str):
  filename = user + ".pdf"
  i = 0
  flag = False
  for j in os.listdir("static/pdfs/"):
    if not j.startswith(user): continue
    fli = j.split(".")
    if "(" in fli[0] and ")" in fli[0]:
      fl = fli[0][fli[0].find("(") + 1:fli[0].find(")")]
      flag = True
    else:
      fl = fli[0][-1]
    try:
      fl = int(fl)
    except:
      None
    if flag:
      i = fl + 1
    else:
      i = 1
    fs = fli[0]
    if flag: fs = fli[0][:fli[0].find("(")]
    if i == 0: i = ""
    filename = f"{fs}({str(i)}).{fli[1]}"
  canvas1 = canvas.Canvas(filename=filename, pagesize=A4)
  canvas1.setFont("kaiub", 50)
  canvas1.drawImage("static/pdf/pdf_back.jpg",
                    0,
                    0,
                    preserveAspectRatio=True,
                    anchor="c",
                    width=A4[0],
                    height=A4[1])
  canvas1.drawCentredString(A4[0] / 2, A4[1] * 77.1 / 100, "獎  狀")
  canvas1.setFontSize(22)
  y, m, d = strs["日期"].split("-")
  y = list(str(int(y) - 1911))
  y1 = y[0]
  y2 = y[1]
  y3 = y[2]
  canvas1.drawCentredString(A4[0] / 2, A4[1] * 80 / 696,
                            f"中 華 民 國  {y1} {y2} {y3}  年  {m}  月  {d}  日")
  canvas1.setFont("kaiu", 12)
  canvas1.drawRightString(A4[0] * 85 / 100, A4[1] * 74 / 100,
                          f"高市雄商({strs['處室簡稱']})字第 {strs['文號']} 號")
  canvas1.setFont("kaiu", 28)
  科別 = strs["科別"]
  年 = strs["年"]
  班 = strs["班"]
  學生 = strs["學生"]
  獎項 = strs["獎項"]
  canvas1.drawCentredString(A4[0] / 2, A4[1] * 46 / 70, f"{科別}科{年}年{班}班{學生}同學")
  canvas1.drawCentredString(A4[0] / 2, A4[1] * 42 / 70, f"榮獲{y1+y2+y3}學年度{獎項}")
  canvas1.drawCentredString(A4[0] / 2, A4[1] * 38 / 70, f"堪為表率  值得嘉許")
  canvas1.drawCentredString(A4[0] / 2, A4[1] * 34 / 70, f"特頒此狀  以資鼓勵")
  canvas1.save()
  return filename


def pdfp(strs: dict,user:str):
  filename = user + ".pdf"
  i = 0
  flag = False
  for j in os.listdir("static/pdfs/"):
    if not j.startswith(user): continue
    fli = j.split(".")
    if "(" in fli[0] and ")" in fli[0]:
      fl = fli[0][fli[0].find("(") + 1:fli[0].find(")")]
      flag = True
    else:
      fl = fli[0][-1]
    try:
      fl = int(fl)
    except:
      None
    if flag:
      i = fl + 1
    else:
      i = 1
    fs = fli[0]
    if flag: fs = fli[0][:fli[0].find("(")]
    if i == 0: i = ""
    filename = f"{fs}({str(i)}).{fli[1]}"
  canvas1 = canvas.Canvas(filename=filename, pagesize=A4)
  canvas1.setFont("kaiub", 50)
  # canvas1.drawImage("static/pdf/pdf_back.jpg",
  #                   0,
  #                   0,
  #                   preserveAspectRatio=True,
  #                   anchor="c",
  #                   width=A4[0],
  #                   height=A4[1])
  canvas1.drawCentredString(A4[0] / 2, A4[1] * 77.1 / 100, "獎  狀")
  canvas1.setFontSize(22)
  y, m, d = strs["日期"].split("-")
  y=str(int(y)-1911)
  y1 = y[0]
  y2 = y[1]
  y3 = y[2]
  canvas1.drawCentredString(A4[0] / 2, A4[1] * 80 / 696,
                            f"中 華 民 國  {y1} {y2} {y3}  年  {m}  月  {d}  日")
  canvas1.setFont("kaiu", 12)
  canvas1.drawRightString(A4[0] * 85 / 100, A4[1] * 74 / 100,
                          f"高市雄商({strs['處室簡稱']})字第 {strs['文號']} 號")
  canvas1.setFont("kaiu", 28)
  科別 = strs["科別"]
  年 = strs["年"]
  班 = strs["班"]
  學生 = strs["學生"]
  獎項 = strs["獎項"]
  canvas1.drawCentredString(A4[0] / 2, A4[1] * 46 / 70, f"{科別}科{年}年{班}班{學生}同學")
  canvas1.drawCentredString(A4[0] / 2, A4[1] * 42 / 70, f"榮獲{y1+y2+y3}學年度{獎項}")
  canvas1.drawCentredString(A4[0] / 2, A4[1] * 38 / 70, f"堪為表率  值得嘉許")
  canvas1.drawCentredString(A4[0] / 2, A4[1] * 34 / 70, f"特頒此狀  以資鼓勵")
  canvas1.save()
  return filename
