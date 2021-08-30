from src.db_function import upsert, retrieve
from src.timefn.timestamp import get_timestamp


def add_coin(username: str, coin: int, nolog=False):
    userdata = retrieve(username)
    if userdata:
        userdata["Coin"] += coin
    else:
        userdata["User_Name"] = username
        userdata["Coin"] = coin
    upsert(userdata)
    if not nolog:
        print(f"[COIN] [{get_timestamp()}] User: {username} receive(deduct) {coin} sniffscoin")


async def get_coin(username: str, send_message):
    userdata = retrieve(username)
    if userdata:
        coin = userdata["Coin"]
    else:
        coin = 0
    await send_message(f"@{username} มี {coin} sniffscoin sniffsAH")
    print(f"[COIN] [{get_timestamp()}] Coin checked by {username}: {coin} sniffscoin")


def payday(usernames, coin, nolog=False):
    for username in usernames:
        add_coin(username.lower(), coin, nolog)
    print(f"[COIN] [{get_timestamp()}] All {len(usernames)} users receive {coin} sniffscoin")
