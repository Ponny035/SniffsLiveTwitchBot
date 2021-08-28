from src.db_function import check_exist, insert, retrieve, update
from src.timefn.timestamp import get_timestamp


def add_coin(username: str, coin: int, nolog=False):
    if check_exist(username):
        userdata = retrieve(username)
        userdata["coin"] += coin
        update(userdata)
    else:
        userdata = {
            "username": username,
            "coin": coin,
            "watchtime": 0,
            "submonth": 0
        }
        insert(userdata)
    if not nolog:
        print(f"[COIN] [{get_timestamp()}] User: {username} receive(deduct) {coin} sniffscoin")


async def get_coin(username: str, send_message):
    if check_exist(username):
        coin = retrieve(username)["coin"]
    else:
        coin = 0
    await send_message(f"@{username} มี {coin} sniffscoin sniffsAH")
    print(f"[COIN] [{get_timestamp()}] Coin checked by {username}: {coin} sniffscoin")


def payday(usernames, coin, nolog=False):
    for username in usernames:
        add_coin(username.lower(), coin, nolog)
    print(f"[COIN] [{get_timestamp()}] All {len(usernames)} users receive {coin} sniffscoin")
