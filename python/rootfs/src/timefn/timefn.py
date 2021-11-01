from datetime import datetime

from twitchio.ext import routines

from src.coin.coin import payday
from src.db_function import bulk_upsert
from src.misc import alldata
from .timestamp import get_timestamp, sec_to_hms


# coin var
coin_join_before_live: int = 5
watchtime_to_point: int = 60


async def activate_point_system():
    if alldata.channel_live:
        usernames = alldata.get_users_list()
        if usernames is not None and len(usernames) > 0:
            payday(coin_join_before_live)
            for username in usernames:
                user_join_part("join", username.lower(), alldata.channel_live_on)
    else:
        update_user_watchtime(True)
        await alldata.sync_db()


def user_join_part(status: str, username: str, timestamp: datetime):
    try:
        if alldata.watchtime_session[username]["status"] != status:
            alldata.watchtime_session[username]["status"] = status
            if status == "join":
                alldata.watchtime_session[username]["join_on"] = timestamp
            elif status == "part":
                alldata.watchtime_session[username]["part_on"] = timestamp
                update_user_watchtime()
    except KeyError:
        alldata.watchtime_session[username] = {}
        alldata.watchtime_session[username]["status"] = status
        if status == "join":
            alldata.watchtime_session[username]["join_on"] = timestamp
        elif status == "part":
            alldata.watchtime_session[username]["part_on"] = timestamp
            update_user_watchtime()


def update_user_watchtime(force=False):
    if alldata.channel_live and alldata.watchtime_session != {}:
        for user_stat in alldata.watchtime_session.values():
            now = get_timestamp()
            if user_stat["status"] == "join":
                try:
                    user_stat["watchtime_session"] = int((now - max(user_stat["join_on"], alldata.channel_live_on)).total_seconds())
                except TypeError:
                    pass
            else:
                try:
                    user_stat["watchtime_session"] = int((user_stat["part_on"] - max(user_stat["join_on"], alldata.channel_live_on)).total_seconds())
                except TypeError:
                    pass
    if force and alldata.watchtime_session != {}:
        for user_stat in alldata.watchtime_session.values():
            now = get_timestamp()
            if user_stat["status"] == "join":
                try:
                    user_stat["watchtime_session"] = int((now - max(user_stat["join_on"], alldata.channel_live_on)).total_seconds())
                except TypeError:
                    pass
            else:
                try:
                    user_stat["watchtime_session"] = int((user_stat["part_on"] - max(user_stat["join_on"], alldata.channel_live_on)).total_seconds())
                except TypeError:
                    pass
    if (not alldata.channel_live) and (alldata.watchtime_session != {}):
        print(f"[_LOG] [{get_timestamp()}] Write Watchtime to DB")
        bulk_userdatas = []
        for username, user_stat in alldata.watchtime_session.items():
            try:
                if user_stat["watchtime_session"] != 0:
                    userdata = next((userdata for userdata in alldata.allusers_stats if userdata["User_Name"] == username), None)
                    if userdata:
                        userdata["Watch_Time"] += int(user_stat["watchtime_session"])
                    else:
                        userdata = {}
                        userdata["User_Name"] = username.lower()
                        userdata["Coin"] = 0
                        userdata["Watch_Time"] = int(user_stat["watchtime_session"])
                        userdata["Sub_Month"] = 0
                        alldata.allusers_stats.append(userdata)
                    bulk_userdatas.append(userdata)
            except Exception as msg:
                print(f"[_LOG] Write Watchtime Error {msg}")
        bulk_upsert(bulk_userdatas)
        print(f"[_LOG] [{get_timestamp()}] Write Watchtime Success")
        alldata.watchtime_session = {}


@routines.routine(minutes=watchtime_to_point)
async def add_point_by_watchtime():
    update_user_watchtime()
    bulk_userdatas = []
    for username, user_stat in alldata.watchtime_session.items():
        time_to_point = watchtime_to_point * 60
        try:
            session = user_stat["watchtime_session"]
        except KeyError:
            session = 0
        try:
            redeem = user_stat["watchtime_redeem"]
        except KeyError:
            redeem = 0
        point_to_add = int((session - redeem) / time_to_point)
        redeem += point_to_add * time_to_point
        user_stat["watchtime_redeem"] = redeem
        if point_to_add > 0:
            userdata = next((userdata for userdata in alldata.allusers_stats if userdata["User_Name"] == username), None)
            if userdata:
                userdata["Coin"] += point_to_add
            else:
                userdata = {}
                userdata["Usser_Name"] = username.lower()
                userdata["Coin"] = point_to_add
                userdata["Watch_Time"] = 0
                userdata["Sub_Month"] = 0
                alldata.allusers_stats.append(userdata)
            bulk_userdatas.append(userdata)
            print(f"[COIN] [{get_timestamp()}] User: {username} receive(deduct) {point_to_add} sniffscoin")
    bulk_upsert(bulk_userdatas)


@add_point_by_watchtime.error
async def add_point_by_watchtime_error(error: Exception):
    print(f"[_ERR] [{get_timestamp()}] ROUTINES: Watchtime System Error with {error}")


async def get_user_watchtime(username: str, send_message):
    if alldata.channel_live:
        update_user_watchtime()
    try:
        session = alldata.watchtime_session[username]["watchtime_session"]
    except KeyError:
        session = 0
    userdata = next((userdata for userdata in alldata.allusers_stats if userdata["User_Name"] == username), None)
    past = 0
    if userdata:
        past = userdata["Watch_Time"]
    watchtime = past + session
    watchtime_dhms = sec_to_hms(watchtime)
    if any(time > 0 for time in watchtime_dhms):
        response_string = f"@{username} ดูไลฟ์มาแล้ว"
        if watchtime_dhms[0] > 0:
            response_string += f" {watchtime_dhms[0]} วัน"
        if watchtime_dhms[1] > 0:
            response_string += f" {watchtime_dhms[1]} ชั่วโมง"
        if watchtime_dhms[2] > 0:
            response_string += f" {watchtime_dhms[2]} นาที"
        if watchtime_dhms[3] > 0:
            response_string += f" {watchtime_dhms[3]} วินาที"
        response_string += " sniffsHeart sniffsHeart sniffsHeart"
        await send_message(response_string)
    else:
        await send_message(f"@{username} เพิ่งมาดู @{alldata.CHANNELS} สิน้าาาาา sniffsAH")
    print(f"[TIME] [{get_timestamp()}] Watchtime checked by {username}: {watchtime_dhms[0]} day {watchtime_dhms[1]} hours {watchtime_dhms[2]} mins {watchtime_dhms[3]} secs")
