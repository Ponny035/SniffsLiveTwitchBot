import asyncio
import random
import re
import os

# from src.db_function import DBManager
from .lotto import check_winner
from src.coin.coin import add_coin
from src.db_function import DBManager
from src.timefn.timestamp import get_timestamp


# init variable
player_lotto_list = []
shooter_cooldown = 0
db = DBManager()


# mod function
async def call_to_hell(usernames, exclude_list, timeout):
    print(f"[HELL] [{get_timestamp()}] Wanna go to hell?")
    callhell_timeout = 180
    casualtie = 0
    usernames = [username for username in usernames if username not in exclude_list]
    number_user = int(len(usernames) / 2)
    random.shuffle(usernames)
    poor_users = usernames[:number_user]
    if os.environ.get("env", "") == "dev":
        callhell_timeout = 60
        poor_users += ["sirju001"]
    for username in poor_users:
        casualtie += 1
        print(f"[HELL] [{get_timestamp()}] Timeout: {username} Duration: {callhell_timeout} Reason: โดนสนิฟดีดนิ้ว")
        await timeout(username, callhell_timeout, "โดนสนิฟดีดนิ้ว")
        await asyncio.sleep(1)
    data = {
        "casualtie": casualtie,
        "poor_users": poor_users
    }
    return data


async def shooter(employer, target, dev_list, send_message, timeout):
    global shooter_cooldown
    dodge_rate = 10
    payrate = 5
    shooter_timeout = random.randint(15, 60)
    exclude_target = [os.environ.get("CHANNELS", ""), os.environ.get("BOTNICK", ""), "sirju001", "moobot", "sniffsbot"] + dev_list
    cooldown = 1200
    if shooter_cooldown == 0:
        available = True
    else:
        now = get_timestamp()
        diff = (now - shooter_cooldown).total_seconds()
        if diff > cooldown:
            available = True
        else:
            available = False
    if available:
        shooter_cooldown = get_timestamp()
        if db.check_exist(employer):
            userdata = db.retrieve(employer)
            if userdata["coin"] >= payrate:
                add_coin(employer, -payrate)
                if db.check_exist(target):
                    submonth = db.retrieve(target)["submonth"]
                    dodge_rate += min(submonth, 6)
                if target in exclude_target:
                    await timeout(employer, shooter_timeout, f"บังอาจเหิมเกริมหรอ นั่งพักไปก่อน {shooter_timeout} วินาที")
                    await send_message(f"@{employer} บังอาจนักนะ บินไปเองซะ {shooter_timeout} วินาที")
                    print(f"[SHOT] [{get_timestamp()}] Shooter: {employer} hit by sniffsbot for {shooter_timeout} sec")
                else:
                    if random.random() > (dodge_rate / 100):
                        await timeout(target, shooter_timeout, f"{employer} จ้างมือปืนสนิฟยิงปิ้วๆ {shooter_timeout} วินาที")
                        await send_message(f"@{employer} จ้างมือปืนสนิฟยิง @{target} {shooter_timeout} วินาที")
                        print(f"[SHOT] [{get_timestamp()}] Shooter: {employer} request sniffsbot to shoot {target} for {shooter_timeout} sec")
                    else:
                        await send_message(f"@{target} หลบมือปืนสนิฟได้ @{employer} เสียใจด้วยนะ (Dodge = {int(dodge_rate)}%)")
            else:
                if target in exclude_target:
                    await timeout(employer, int(shooter_timeout * 2), f"ไม่มีเงินจ้างแล้วยังเหิมเกริมอีก รับโทษ 2 เท่า ({shooter_timeout} วินาที)")
                    await send_message(f"@{employer} ไม่มีเงินจ้างมือปืน ยังจะเหิมเกริม บินไปซะ {int(shooter_timeout * 2)} วินาที")
                    print(f"[SHOT] [{get_timestamp()}] Shooter: {employer} hit by sniffsbot for {int(shooter_timeout * 2)} sec")
                else:
                    await timeout(employer, shooter_timeout, f"ไม่มีเงินจ้างมือปืนงั้นรึ โดนยิงเองซะ {shooter_timeout} วินาที")
                    await send_message(f"@{employer} ไม่มีเงินจ้างมือปืน โดนมือปืนยิงตาย {shooter_timeout} วินาที")
                    print(f"[SHOT] [{get_timestamp()}] Shooter: {employer} hit by sniffsbot for {shooter_timeout} sec")
        else:
            if target in exclude_target:
                await timeout(employer, int(shooter_timeout * 2), f"ไม่มีเงินจ้างแล้วยังเหิมเกริมอีก รับโทษ 2 เท่า ({shooter_timeout} วินาที)")
                await send_message(f"@{employer} ไม่มีเงินจ้างมือปืน ยังจะเหิมเกริม บินไปซะ {int(shooter_timeout * 2)} วินาที")
                print(f"[SHOT] [{get_timestamp()}] Shooter: {employer} hit by sniffsbot for {int(shooter_timeout * 2)} sec")
            else:
                await timeout(employer, shooter_timeout, f"ไม่มีเงินจ้างมือปืนงั้นรึ โดนยิงเองซะ {shooter_timeout} วินาที")
                await send_message(f"@{employer} ไม่มีเงินจ้างมือปืน โดนมือปืนยิงตาย {shooter_timeout} วินาที")
                print(f"[SHOT] [{get_timestamp()}] Shooter: {employer} hit by sniffsbot for {shooter_timeout} sec")


# lotto system
async def buy_lotto(username, lotto, send_message):
    global player_lotto_list
    lotto_cost = 5
    if (re.match(r"[0-9]{4}", lotto) is not None) and (len(lotto) == 4):
        if db.check_exist(username):
            userstat = db.retrieve(username)
            if userstat["coin"] >= lotto_cost:
                lotto_int = int(lotto)
                if player_lotto_list != []:
                    for player_lotto in player_lotto_list:
                        if lotto_int in player_lotto:
                            await send_message(f"@{username} ไม่สามารถซื้อเลขซ้ำได้")
                            print(f"[LOTO] [{get_timestamp()}] {username} Duplicate Lotto: {lotto}")
                            return
                add_coin(username, -lotto_cost)
                player_lotto_list += [[username, lotto_int]]
                await send_message(f"@{username} ซื้อ SniffsLotto หมายเลข {lotto} สำเร็จ")
                print(f"[LOTO] [{get_timestamp()}] {username} buy {lotto} successfully")
            else:
                await send_message(f"@{username} ไม่มีเงินแล้วยังจะซื้ออีก")
                print(f"[LOTO] [{get_timestamp()}] {username} coin insufficient")


async def draw_lotto(send_message):
    global player_lotto_list
    if player_lotto_list != []:
        print(f"[LOTO] All player list : {player_lotto_list}")
        win_number, lotto_winners = check_winner(player_lotto_list)
        win_number_string = f"{win_number:04d}"
        count_winners = len(lotto_winners)
        payout = 0
        for winner in lotto_winners:
            add_coin(winner[0], int(winner[1]))
            payout += int(winner[1])
        await send_message(f"ประกาศผลรางวัล SniffsLotto เลขที่ออก {win_number_string} มีผู้ชนะทั้งหมด {count_winners} คน ได้รับรางวัลรวม {payout} sniffscoin")
        print(f"[LOTO] [{get_timestamp()}] LOTTO draw: {win_number_string} | winners: {count_winners} users | payout: {payout} coin")
        player_lotto_list = []
