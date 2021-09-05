import re

from src.db_function import upsert, retrieve
from src.timefn.timestamp import get_timestamp


async def update_submonth(username: str, rawdata: str):
    submonth = 0
    try:
        submonth = int(re.search("(?<=subscriber/)([0-9]+)", rawdata)[0])
    except Exception:
        return
    if submonth > 0:
        userdata = retrieve(username)
        if userdata:
            if userdata["Sub_Month"] != submonth:
                userdata["Sub_Month"] = submonth
                upsert(userdata)
                print(f"[INFO] [{get_timestamp()}] Update {username} submonth to {submonth} months")
        else:
            userdata = {}
            userdata["User_Name"] = username.lower()
            userdata["Sub_Month"] = submonth
            upsert(userdata)
            print(f"[INFO] [{get_timestamp()}] Insert {username} with submonth {submonth} months")
