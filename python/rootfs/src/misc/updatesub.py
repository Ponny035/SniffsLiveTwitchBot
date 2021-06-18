import re

from src.db_function import DBManager
from src.timefn.timestamp import get_timestamp


db = DBManager()


async def update_submonth(username, rawdata):
    submonth = 0
    try:
        submonth = int(re.search("(?<=subscriber/)([0-9]+)", rawdata)[0])
    except Exception:
        return
    if submonth > 0:
        if db.check_exist(username):
            userdata = db.retrieve(username)
            userdata["submonth"] = submonth
            db.update(userdata)
            print(f"[INFO] [{get_timestamp()}] Update {username} submonth to {submonth} months")
        else:
            userdata = {
                "username": username,
                "coin": 0,
                "watchtime": 0,
                "submonth": submonth
            }
            db.insert(userdata)
            print(f"[INFO] [{get_timestamp()}] Insert {username} with submonth {submonth} months")
