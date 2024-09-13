from .imports import *
from .funcs import *
from flask import Blueprint

chat = Blueprint("chat", __name__)


@chat.route("/chat/")
@login_required
def __chatIndex():
  fl = fetch_json("static/jsons/friend_list.json")
  if not current_user.id in fl:
    fl[current_user.id] = []
    fl.supd()
  if not "current_room" in session:
    session["current_room"] = fl[current_user.id][0][0] if len(
      fl[current_user.id]) > 0 else None

  db = fetch_db(f'static/jsons/dbs/main.db')
  unreadl = dict()
  for i in fl[current_user.id]:
    db.cs.execute(
      f'''select count(*) from msg{i[0]} where status='unread' and author!='{current_user.id}' '''
    )
    unreadl[i[0]] = db.cs.fetchone()[0]
    db.cs.execute(
      f'''select content from msg{i[0]} order by date desc,time desc limit 1'''
    )
    result = db.cs.fetchone()
    fl[current_user.id][fl[current_user.id].index(
      i)][2] = result[0] if result else "上次傳送的訊息"
  fl.supd()

  return render_template(
    "chatIndex.html",
    header=render_template("header.html"),
    footer=render_template("footer.html"),
    fl=fl[current_user.id],
    fln={i[1]: i[3]
         for i in fl[current_user.id]},
    ffl=session.get("ffl", ([
      j for i in fl[fl[current_user.id][0][1]] for j in i
      if current_user.id == i[1]
    ]) if len(fl[current_user.id]) else []),
    users=fetch_users(),
    cl={
      i: j
      for i, j in fetch_users().items()
      if j.get("class") == current_user.clas and not i == current_user.id
      and not i in [j[1] for i in fl.values() for j in i]
    },
    unreadl=unreadl,
    rl=[i[0] for i in fl[current_user.id]])


@chat.route("/chat/msg")
@login_required
def __chat():
  id = request.args.get("id")
  if not id and not id == 0: abort(404)
  fl = fetch_json("static/jsons/friend_list.json")
  if not id in [i[0] for i in fl[current_user.id]]: abort(404)
  if not current_user.id in fl:
    fl[current_user.id] = []
    fl.supd()
  session["current_room"] = id
  c = 0
  for i in fl[current_user.id]:
    if id == i[0]:
      c = fl[current_user.id].index(i)
      break

  db = fetch_db(f'static/jsons/dbs/main.db')
  db.cs.execute(
    f'''update msg{id} set status='read' where status != 'read' ''')
  db.db.commit()
  db.cs.execute(f'''select * from msg{id} order by date,time''')
  msgs = list(db.cs.fetchall())
  db.close()
  session["ffl"] = [
    k for i in fl.values() for j in i for k in j
    if j[0] == id and current_user.id in j
  ]
  return render_template("chat.html",
                         header=render_template("header.html"),
                         footer=render_template("footer.html"),
                         fl=fl[current_user.id],
                         ffl=session.get("ffl", ([
                           j for i in fl[fl[current_user.id][c][1]] for j in i
                           if current_user.id == i[1]
                         ]) if len(fl[current_user.id]) else []),
                         ind=c,
                         users=fetch_users(),
                         msgs=msgs)


@chat.route("/chat/change_name", methods=["post"])
@login_required
def __change_name():
  form = request.form.to_dict()
  if not "ind" in form or not "newName" in form:
    abort(400)
  fl = fetch_json("static/jsons/friend_list.json")
  id = fl[current_user.id][int(form["ind"])][0]
  fl[current_user.id][int(form["ind"])][3] = form["newName"]
  if id.startswith("g"):
    for i in fl[fl[current_user.id][int(form["ind"])][1]]:
      i[3] = form["newName"]
    for i in [j[1] for j in fl[fl[current_user.id][int(form["ind"])][1]]]:
      for j in fl[i]:
        if id in j:
          j[3] = form["newName"]
  fl.supd()

  return "OK"


@chat.route("/chat/adds", methods=["post"])
@login_required
def __adds():
  form = request.form.to_dict()
  tar = request.args.get("tar")
  if not tar: abort(400)
  else:
    fl = fetch_json("static/jsons/friend_list.json")
    users = fetch_users()
    if not form.get("username") in users and not "members" in form:
      abort(400)
    if tar == "friend":
      ind = 0
      for i in fl.values():
        for j in i:
          if j[0].startswith("g"): continue
          if int(j[0]) > ind: ind = int(j[0])
      ind = str(ind + 1)
      if not current_user.id in fl: fl[current_user.id] = []
      if not form["username"] in fl: fl[form["username"]] = []
      fl[current_user.id].append([
        ind, form["username"], "上次傳送的訊息...",
        users[form["username"]]["fullname"], 0
      ])
      fl[form["username"]].append(
        [f"{ind}", current_user.id, "上次傳送的訊息...", current_user.fullname, 0])
    elif tar == "group":
      ind = 0
      for i in fl.values():
        for j in i:
          if not j[0].startswith("g"): continue
          if int(j[0][1:]) > ind: ind = int(j[0][1:])
      ind = str(ind + 1)
      fl[f"group-chat{ind}"] = []
      l = [f"g{ind}", f"group-chat{ind}", "上次傳送的訊息...", form["name"], 0]
      fl[current_user.id].append(l)
      for i in json.loads(form["members"]):
        fl[i].append(l)
        fl[f"group-chat{ind}"].append(
          [f"g{ind}", i, "上次傳送的訊息...", form["name"], 0])
      fl[f"group-chat{ind}"].append(
        [f"g{ind}", current_user.id, "上次傳送的訊息...", form["name"], 0])
      ind = f"g{ind}"

    else:
      abort(400)

    db = fetch_db(f'static/jsons/dbs/main.db')
    db.cs.execute(f'''CREATE TABLE IF NOT EXISTS msg{ind}
             (id integer primary key,content text,author text,date text,time text,status text)'''
                  )
    db.close()
    fl.supd()
  return "OK"


@chat.route("/chat/clear", methods=["post"])
@login_required
def __clear():
  id = request.args.get("id")
  db = fetch_db("static/jsons/dbs/main.db")

  db.cs.execute(f"""SELECT count(name) FROM sqlite_master  
  WHERE type='table' and name= 'msg{id}' ;""")
  if db.cs.fetchone()[0]:
    db.cs.execute(f"""delete from msg{id} """)
    db.db.commit()
  db.close()
  return "OK"


@chat.route("/chat/save")
@login_required
def __save():
  id = request.args.get("id")
  fl = fetch_json("static/jsons/friend_list.json")

  c = 0
  for i in fl[current_user.id]:
    if id == i[0]:
      c = fl[current_user.id].index(i)
      break
  db = fetch_db("static/jsons/dbs/main.db")
  db.cs.execute(f"""SELECT count(name) FROM sqlite_master  
  WHERE type='table' and name= 'msg{id}' ;""")

  if db.cs.fetchone()[0]:
    db.cs.execute(f"""select * from msg{id} order by date,time""")
    fn = f"{secure_filename(uuid.uuid4().hex)}.html"
    with open(f"static/archived/{fn}", mode="w") as wf:
      fcntl.flock(wf, fcntl.LOCK_EX)
      wf.write(
        render_template("archived.html",
                        header=render_template("header.html"),
                        footer=render_template("footer.html"),
                        fl=fl[current_user.id],
                        ffl=session.get("ffl", [
                          j for i in fl[fl[current_user.id][c][1]]
                          for j in i if current_user.id == i[1]
                        ]),
                        ind=c,
                        users=fetch_users(),
                        msgs=db.cs.fetchall()))
      fcntl.flock(wf, fcntl.LOCK_UN)
      wf.close()
    db.close()
    return send_from_directory("static/archived", fn, as_attachment=True)
  return "OK"


@chat.route("/chat/glm")
@login_required
def __get_last_msg():
  if not request.args.get("id"): abort(400)
  fl = fetch_json("static/jsons/friend_list.json")
  if not request.args.get("id") in [i[0] for i in fl[current_user.id]]:
    abort(404)
  db = fetch_db("static/jsons/dbs/main.db")
  db.cs.execute(
    f'''select content from msg{request.args.get("id")} order by date desc,time desc limit 1'''
  )
  return jsonify(msg=db.cs.fetchone()[0])
