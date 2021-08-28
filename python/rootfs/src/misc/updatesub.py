import re

from src.db_function import check_exist, insert, retrieve, update
from src.timefn.timestamp import get_timestamp


async def update_submonth(username: str, rawdata: str):
    submonth = 0
    try:
        submonth = int(re.search("(?<=subscriber/)([0-9]+)", rawdata)[0])
    except Exception:
        return
    if submonth > 0:
        if check_exist(username):
            userdata = retrieve(username)
            if userdata["submonth"] != submonth:
                userdata["submonth"] = submonth
                update(userdata)
                print(f"[INFO] [{get_timestamp()}] Update {username} submonth to {submonth} months")
        else:
            userdata = {
                "username": username,
                "coin": 0,
                "watchtime": 0,
                "submonth": submonth
            }
            insert(userdata)
            print(f"[INFO] [{get_timestamp()}] Insert {username} with submonth {submonth} months")
