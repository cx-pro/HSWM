#### generator ####
from modules.funcs import write_json
import shutil
import orjson
import os
dirs = ["static"]
worked = []


def rdir(d: str):
    dirs = [d]
    worked.append(d)
    for i in os.listdir(d):
        nd = f"{d}/{i}"
        if os.path.isdir(nd):
            if not i in dirs:
                dirs.append(nd)
            if not nd in worked:
                rdir(nd)


#### //generator ####


dirs = ['static', 'static/js', 'static/css', 'static/images', 'static/dependences', 'static/dependences/others', 'static/qfiles', 'static/pdfs', 'static/audios', 'static/pics', 'static/jsons', 'static/jsons/pdfs', 'static/jsons/selfCalendar',
        'static/jsons/dbs', 'static/jsons/tasks', 'static/jsons/grades', 'static/pdf', 'static/fonts', 'static/files', 'static/archived', 'static/menu_images', 'static/qrcode', 'static/ods', 'static/ods/example', 'static/profile_pics', 'static/profile_pics/default']


def clearUserData():
    for p in [f"{i}/{j}" for i in dirs for j in os.listdir(i) if i.startswith("static/jsons") and os.path.isfile(f"{i}/{j}") and j.endswith(".json") or j.endswith(".db")]:
        if (p.endswith(".db")):
            os.remove(p)
            continue
        with open(p, "rb") as f:
            d = orjson.loads(f.read())
            d.clear()
            f.close()
        if p.endswith("account.json"):
            d = {
                "teacher001": {"avatar": "profile_pics/default/Default_Avatar.svg", "fullname": "測試用教師帳號", "role": "tch", "number": "123456", "intro": "測試用教師帳號，禁止用於其他用途。", "password": "pbkdf2:sha256:260000$0BzmT6uuAq4WBC5A$1b8a015e614b0309f000ce7f75626cd2f763604c0fe59544259dc13ca79b4ff2", "course": "測試科", "classes": ["313", "206", "215"], "settings": {"index_mode": "default", "theme": "light", "sche_mode": "cal"}},
                "stu001": {"fullname": "測試學生", "department": "測試科", "intro": "介紹", "class": "123", "avatar": "profile_pics/default/Default_Avatar.svg", "password": "pbkdf2:sha256:260000$RVBBjLSgWC3bmnDd$1b436f4154c1335f4ee1319e34ca782728ff5022f872603293acd2a471304d59", "role": "stu", "asistnt": [], "number": "000001"},
                "administrator": {"fullname": "預設管理員", "intro": "網站預設管理員", "avatar": "profile_pics/default/Default_Avatar.svg", "password": "pbkdf2:sha256:260000$omzt829V8oKc7VBn$f500696711934cc46c4576b9ec315db5d0921815bebb15f974e986ef62646ddf", "role": "adm", "settings": {"sche_mode": "sche", "theme": "light"}}
            }
        write_json(p, d)

    for i in ["archived", "files", "pdfs", "qfiles", "menu_images"]:
        p = f"static/{i}"
        shutil.rmtree(p)
        os.mkdir(p)
    p1, p2 = "static/ods/", "static/profile_pics/"
    for p in [p1+i for i in os.listdir(p1)]+[p2+i for i in os.listdir(p2)]:
        if os.path.isdir(p):
            continue
        os.remove(p)


if __name__ == "__main__":
    clearUserData()
