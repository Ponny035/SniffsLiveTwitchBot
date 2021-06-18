from src.db_function import DBManager
from src.timefn.timestamp import get_timestamp


db = DBManager()


def add_coin(username, coin, nolog=False):
    if db.check_exist(username):
        userdata = db.retrieve(username)
        userdata["coin"] += coin
        db.update(userdata)
    else:
        userdata = {
            "username": username,
            "coin": coin,
            "watchtime": 0,
            "submonth": 0
        }
        db.insert(userdata)
    if not nolog:
        print(f"[COIN] [{get_timestamp()}] User: {username} receive(deduct) {coin} sniffscoin")


async def get_coin(username, send_message):
    if db.check_exist(username):
        coin = db.retrieve(username)["coin"]
    else:
        coin = 0
    await send_message(f"@{username} มี {coin} sniffscoin")
    print(f"[COIN] [{get_timestamp()}] Coin checked by {username}: {coin} sniffscoin")


def payday(usernames, coin, nolog=False):
    for username in usernames:
        add_coin(username.lower(), coin, nolog)
    print(f"[COIN] [{get_timestamp()}] All {len(usernames)} users receive {coin} sniffscoin")
