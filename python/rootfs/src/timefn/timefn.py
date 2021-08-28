from datetime import datetime

from twitchio.ext import routines

from src.coin.coin import add_coin
from src.db_function import check_exist, insert, retrieve, update
from .timestamp import get_timestamp, sec_to_hms


# init var
channel_live: bool = False
channel_live_on: datetime = None
watchtime_session: dict = {}

# coin var
coin_join_before_live: int = 5
watchtime_to_point: int = 60


async def activate_point_system(live, starttime=None, usernames=None):
    global channel_live
    global channel_live_on
    global watchtime_session
    channel_live = live
    if (live) and (starttime is not None):
        channel_live_on = starttime
        if usernames is not None:
            for username in usernames:
                user_join_part("join", username.lower(), channel_live_on)
                add_coin(username.lower(), coin_join_before_live)
    else:
        update_user_watchtime(True)


def user_join_part(status: str, username: str, timestamp: datetime):
    global watchtime_session
    try:
        if watchtime_session[username]["status"] != status:
            watchtime_session[username]["status"] = status
            if status == "join":
                watchtime_session[username]["join_on"] = timestamp
            elif status == "part":
                watchtime_session[username]["part_on"] = timestamp
                update_user_watchtime()
    except KeyError:
        watchtime_session[username] = {}
        watchtime_session[username]["status"] = status
        if status == "join":
            watchtime_session[username]["join_on"] = timestamp
        elif status == "part":
            watchtime_session[username]["part_on"] = timestamp
            update_user_watchtime()


def update_user_watchtime(force=False):
    global watchtime_session
    if channel_live and watchtime_session != {}:
        for user_stat in watchtime_session.values():
            now = get_timestamp()
            if user_stat["status"] == "join":
                user_stat["watchtime_session"] = int((now - max(user_stat["join_on"], channel_live_on)).total_seconds())
            else:
                user_stat["watchtime_session"] = int((user_stat["part_on"] - max(user_stat["join_on"], channel_live_on)).total_seconds())
    if force and watchtime_session != {}:
        for user_stat in watchtime_session.values():
            now = get_timestamp()
            if user_stat["status"] == "join":
                user_stat["watchtime_session"] = int((now - max(user_stat["join_on"], channel_live_on)).total_seconds())
            else:
                user_stat["watchtime_session"] = int((user_stat["part_on"] - max(user_stat["join_on"], channel_live_on)).total_seconds())
    if (not channel_live) and (watchtime_session != {}):
        print(f"[_LOG] [{get_timestamp()}] Write Watchtime to DB")
        for username, user_stat in watchtime_session.items():
            try:
                if user_stat["watchtime_session"] != 0:
                    if check_exist(username):
                        userdata = retrieve(username)
                        userdata["watchtime"] += int(user_stat["watchtime_session"])
                        update(userdata)
                    else:
                        userdata = {
                            "username": username,
                            "coin": 0,
                            "watchtime": int(user_stat["watchtime"]),
                            "submonth": 0
                        }
                        insert(userdata)
            except KeyError:
                pass
        print(f"[_LOG] [{get_timestamp()}] Write Watchtime Success")
        watchtime_session = {}


@routines.routine(minutes=watchtime_to_point)
async def add_point_by_watchtime():
    global watchtime_session
    update_user_watchtime()
    for username, user_stat in watchtime_session.items():
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
            add_coin(username, point_to_add)


async def get_user_watchtime(username: str, live: bool, channels: str, send_message):
    if live:
        update_user_watchtime()
    try:
        session = watchtime_session[username]["watchtime_session"]
    except KeyError:
        session = 0
    if check_exist(username):
        past = retrieve(username)["watchtime"]
    else:
        past = 0
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
        await send_message(f"@{username} เพิ่งมาดู @{channels} สิน้าาาาา sniffsAH")
    print(f"[TIME] [{get_timestamp()}] Watchtime checked by {username}: {watchtime_dhms[0]} day {watchtime_dhms[1]} hours {watchtime_dhms[2]} mins {watchtime_dhms[3]} secs")
