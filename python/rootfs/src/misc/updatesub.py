import re

from src.db_function import upsert
from src.misc import alldata
from src.timefn.timestamp import get_timestamp


async def update_submonth(username: str, rawdata: str):
    submonth = 0
    try:
        submonth = int(re.search("(?<=subscriber/)([0-9]+)", rawdata)[0])
    except Exception:
        return
    if submonth > 0:
        try:
            userdata = next((userdata for userdata in alldata.allusers_stats if userdata["User_Name"] == username), None)
        except TypeError:
            userdata = None
        if userdata:
            if userdata["Sub_Month"] != submonth:
                userdata["Sub_Month"] = submonth
                upsert(userdata)
                print(f"[INFO] [{get_timestamp()}] Update {username} submonth to {submonth} months")
        else:
            userdata = {}
            userdata["User_Name"] = username.lower()
            userdata["Coin"] = 0
            userdata["Watch_Time"] = 0
            userdata["Sub_Month"] = submonth
            alldata.allusers_stats.append(userdata)
            upsert(userdata)
            print(f"[INFO] [{get_timestamp()}] Insert {username} with submonth {submonth} months")
