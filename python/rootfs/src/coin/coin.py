from src.db_function import upsert, bulk_upsert
from src.timefn.timestamp import get_timestamp
from src.misc import alldata


def add_coin(username: str, coin: int, nolog=False):
    userdata = next((userdata for userdata in alldata.allusers_stats if userdata["User_Name"] == username), None)
    if userdata:
        userdata["Coin"] += coin
    else:
        userdata = {}
        userdata["User_Name"] = username.lower()
        userdata["Coin"] = coin
        userdata["Watch_Time"] = 0
        userdata["Sub_Month"] = 0
        alldata.allusers_stats.append(userdata)
    upsert(userdata)
    if not nolog:
        print(f"[COIN] [{get_timestamp()}] User: {username} receive(deduct) {coin} sniffscoin")


async def get_coin(username: str, send_message):
    userdata = next((userdata for userdata in alldata.allusers_stats if userdata["User_Name"] == username), None)
    if userdata:
        coin = userdata["Coin"]
    else:
        coin = 0
    await send_message(f"@{username} มี {coin} sniffscoin sniffsAH")
    print(f"[COIN] [{get_timestamp()}] Coin checked by {username}: {coin} sniffscoin")


def payday(coin, nolog=False):
    usernames = alldata.get_users_list()
    bulk_userdatas = []
    for username in usernames:
        userdata = next((userdata for userdata in alldata.allusers_stats if userdata["User_Name"] == username), None)
        if userdata:
            userdata["Coin"] += coin
        else:
            userdata["User_Name"] = username.lower()
            userdata["Coin"] = coin
            userdata["Watch_Time"] = 0
            userdata["Sub_Month"] = 0
            alldata.allusers_stats.append(userdata)
        bulk_userdatas.append(userdata)
        if not nolog:
            print(f"[COIN] [{get_timestamp()}] User: {username} receive(deduct) {coin} sniffscoin")
    bulk_upsert(bulk_userdatas)
    print(f"[COIN] [{get_timestamp()}] All {len(usernames)} users receive {coin} sniffscoin")
