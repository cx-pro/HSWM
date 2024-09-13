from .imports import *
from .funcs import *


class User(UserMixin):
  users = fetch_users()
  _id = None

  @property
  def is_qrcUser(self):
    return False

  @property
  def avatar(self):
    self.refresh_users()
    return self.users[self.id]["avatar"]

  @property
  def http_avatar(self):
    self.refresh_users()
    return ("https://hswm.up.railway.app/static/"
            if not self.users[self.id]["avatar"].startswith("http") else
            "") + self.users[self.id]["avatar"]

  def get_id(self):
    try:
      return self.id
    except AttributeError:
      return False

  @property
  def id(self):
    return self._id

  @id.setter
  def id(self, val):
    self.refresh_users()
    self._id = val
    self._password = self.users[self._id]["password"]

  def __init__(self):
    self._id = None
    self.refresh_users()

  @property
  def __is_authenticated(self):
    self.refresh_users()
    return self._password == self.users[self.get_id()]["password"]

  @property
  def password(self):
    return self._password

  @password.setter
  def password(self, val):
    self._password = val

  @classmethod
  def refresh_users(cls):
    with open("static/jsons/account.json") as f:
      cls.users = json.load(f)
      f.close()
    return cls.users

  @property
  def is_admin(self):
    self.refresh_users()
    if self.users[self.id]["role"] == "adm": return True
    return False

  @property
  def is_student(self):
    self.refresh_users()
    if self.users[self.id]["role"] == "stu": return True
    return False

  @property
  def is_teacher(self):
    self.refresh_users()
    if self.users[self.id]["role"] == "tch": return True
    return False

  @property
  def clas(self):
    self.refresh_users()
    _clas = ""
    if self.is_student:
      _clas = self.users[self.id]["class"]
    return _clas

  @property
  def fullname(self):
    self.refresh_users()
    return self.users[self.id]["fullname"]

  @property
  def classes(self):
    self.refresh_users()
    _clas = list()
    if self.is_teacher:
      _clas = self.users[self.id]["classes"]
    return _clas

  @property
  def is_asistnt(self):
    self.refresh_users()
    fl = False
    if self.users.get(self.id).get("asistnt"):
      fl = True
    return fl

  @property
  def asists(self):
    self.refresh_users()
    _asis = list()
    if self.is_asistnt:
      _asis = self.users.get(self.id).get("asistnt")
    return _asis

  @property
  def role(self):
    self.refresh_users()
    return self.users[self.id]["role"]

  @property
  def email(self):
    self.refresh_users()
    return fetch_json("static/jsons/email.json").KVSwap()[current_user.id]

  @property
  def settings(self):
    self.refresh_users()
    return self.users[self.id].get("settings", False)


class AnonymousUser(AnonymousUserMixin):

  users = {"Unauthorized": fetch_users()["Unauthorized"]}

  def __init__(self):
    self._is_qrcUser = session.get("_is_qrcUser",False)
    self._clas = session.get("_clas")
    self._classes = session.get("_classes",[])
    self._editable = session.get("_editable",False)
    self._settings = session.get("_settings",{})
    self.id = "Unauthorized"
    session["_certi_id"]=session.get("_certi_id",str(uuid.uuid4()))
    self._certi_id=session["_certi_id"]

  @property
  def is_asistnt(self):
    return False

  @property
  def avatar(self):
    return "profile_pics/default/Default_Avatar.svg"

  @property
  def settings(self):
    return self._settings

  @property
  def clas(self):
    return self._clas

  @clas.setter
  def clas(self, val):
    self._clas = val
    session["_clas"] = val

  @property
  def classes(self):
    return self._classes

  @clas.setter
  def classes(self, val):
    self._classes = [val]
    session["_classes"] = [val]

  @property
  def is_authenticated(self):
    return self.is_qrcUser

  @property
  def is_qrcUser(self):
    return self._is_qrcUser or False

  @is_qrcUser.setter
  def is_qrcUser(self, val):
    self._is_qrcUser = val
    session["_is_qrcUser"] = val

  @property
  def editable(self):
    return self._editable or False

  @editable.setter
  def editable(self, val):
    self._editable = val
    session["_editable"] = val

  @property
  def is_student(self):
    return (self.clas and self.is_qrcUser)

  @property
  def is_teacher(self):
    return self.is_qrcUser and self.clas and self.editable

  @property
  def certi_id(self):
    return self._certi_id
  
  @certi_id.setter
  def certi_id(self,val):
    session["_certi_id"]=val
    self._certi_id=val
