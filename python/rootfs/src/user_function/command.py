import asyncio
import random
import re
import os

from twitchio.ext import routines

from .lotto import check_winner
from .games import coinflip
from .raffle import raffle_save, raffle_winner
from src.coin.coin import add_coin
from src.timefn.timestamp import get_timestamp
from src.misc import alldata
from src.misc.webfeed import buy_lotto_feed, buy_raffle_feed, call_to_hell_feed, coinflip_feed, draw_lotto_feed, draw_raffle_feed, shooter_dodge_feed, shooter_success_feed, shooter_suicide_feed, shooter_unsuccess_feed, shooter_vip_feed


# mod function
async def call_to_hell(timeout):
    print(f"[HELL] [{get_timestamp()}] Wanna go to hell?")
    callhell_timeout = 180
    casualtie = 0
    usernames = alldata.get_users_list()
    exclude_list = alldata.vip_list + alldata.dev_list
    usernames = [username for username in usernames if username not in exclude_list]
    number_user = int(len(usernames) / 2)
    random.shuffle(usernames)
    poor_users = usernames[:number_user]
    if os.environ.get("env", "") == "dev":
        callhell_timeout = 60
        poor_users += ["sirju001"]
    for username in poor_users:
        casualtie += 1
        call_to_hell_feed(username, casualtie, len(poor_users))
        print(f"[HELL] [{get_timestamp()}] Timeout: {username} Duration: {callhell_timeout} Reason: โดนสนิฟดีดนิ้ว")
        await timeout(username, callhell_timeout, "โดนสนิฟดีดนิ้ว")
        await asyncio.sleep(1)
    data = {
        "casualtie": casualtie,
        "poor_users": poor_users
    }
    return data


async def shooter(employer: str, target: str, send_message, timeout, override: bool):
    dodge_rate = 10
    payrate = 5
    shooter_timeout = random.randint(15, 60)
    target = re.sub(r'^@', '', target)
    if target == "me":
        await timeout(employer, shooter_timeout, f"อยากไปเยือนยมโลกหรอ สนิฟจัดให้ {shooter_timeout} วินาที")
        await send_message(f"@{employer} แวะไปเยือนยมโลก {shooter_timeout} วินาที sniffsAH")
        shooter_suicide_feed(employer, shooter_timeout)
        print(f"[SHOT] [{get_timestamp()}] Shooter: {employer} suicide by sniffsbot for {shooter_timeout} sec")
        return
    exclude_target = alldata.vip_list + alldata.dev_list
    cooldown = 1200
    if alldata.shooter_cooldown == 0:
        available = True
    else:
        now = get_timestamp()
        diff = (now - alldata.shooter_cooldown).total_seconds()
        if diff > cooldown:
            available = True
        else:
            available = False
    if override:
        available = True
        dodge_rate = 0
    if available:
        userdata = next((userdata for userdata in alldata.allusers_stats if userdata["User_Name"] == employer), None)

        # have userdata case
        if userdata:

            # enough money case
            if userdata["Coin"] >= payrate:
                add_coin(employer, -payrate)
                targetdata = next((userdata for userdata in alldata.allusers_stats if userdata["User_Name"] == target), None)
                if targetdata:
                    submonth = targetdata["Sub_Month"]
                    dodge_rate += min(submonth * 1.5, 10)
                if target in exclude_target:
                    shooter_state = "vip"
                else:
                    if random.random() > (dodge_rate / 100):
                        shooter_state = "success"
                    else:
                        shooter_state = "dodge"

            # not enough money case
            else:
                if target in exclude_target:
                    shooter_state = "vip_nomoney"
                else:
                    shooter_state = "nomoney"

        # no userdata case
        else:
            if target in exclude_target:
                shooter_state = "vip_nomoney"
            else:
                shooter_state = "nomoney"

        # execute base on state
        match shooter_state:
            case "success":
                if not override:
                    alldata.shooter_cooldown = get_timestamp()
                await timeout(target, shooter_timeout, f"{employer} จ้างมือปืนสนิฟยิงปิ้วๆ {shooter_timeout} วินาที")
                await send_message(f"@{employer} จ้างมือปืนสนิฟยิง @{target} {shooter_timeout} วินาที sniffsAH")
                shooter_success_feed(employer, target, shooter_timeout, userdata["Coin"])
                print(f"[SHOT] [{get_timestamp()}] Shooter: {employer} request sniffsbot to shoot {target} for {shooter_timeout} sec")
            case "dodge":
                await send_message(f"@{target} หลบมือปืนสนิฟได้ sniffsHeart @{employer} เสียใจด้วยนะ (Dodge = {int(dodge_rate)}%)")
                shooter_dodge_feed(target, dodge_rate)
            case "vip":
                await timeout(employer, shooter_timeout, f"บังอาจเหิมเกริมหรอ นั่งพักไปก่อน {shooter_timeout} วินาที")
                await send_message(f"@{employer} บังอาจนักนะ PunOko บินไปเองซะ {shooter_timeout} วินาที")
                shooter_vip_feed(employer, shooter_timeout)
                print(f"[SHOT] [{get_timestamp()}] Shooter: {employer} hit by sniffsbot for {shooter_timeout} sec")
            case "vip_nomoney":
                await timeout(employer, int(shooter_timeout * 2), f"ไม่มีเงินจ้างแล้วยังเหิมเกริมอีก รับโทษ 2 เท่า ({shooter_timeout} วินาที)")
                await send_message(f"@{employer} ไม่มีเงินจ้างมือปืน ยังจะเหิมเกริม PunOko บินไปซะ {int(shooter_timeout * 2)} วินาที")
                shooter_unsuccess_feed(employer, int(shooter_timeout * 2))
                print(f"[SHOT] [{get_timestamp()}] Shooter: {employer} hit by sniffsbot for {int(shooter_timeout * 2)} sec")
            case "nomoney":
                await timeout(employer, shooter_timeout, f"ไม่มีเงินจ้างมือปืนงั้นรึ โดนยิงเองซะ {shooter_timeout} วินาที")
                await send_message(f"@{employer} ไม่มีเงินจ้างมือปืน PunOko โดนมือปืนยิงตาย {shooter_timeout} วินาที")
                shooter_unsuccess_feed(employer, shooter_timeout)
                print(f"[SHOT] [{get_timestamp()}] Shooter: {employer} hit by sniffsbot for {shooter_timeout} sec")
            case _:
                return


# lotto system
async def buy_lotto(username: str, lotto: str, count: int, send_message):
    lotto_cost = 5
    if (re.match(r"[0-9]{2}", lotto) is not None) and (len(lotto) == 2):
        userdata = next((userdata for userdata in alldata.allusers_stats if userdata["User_Name"] == username), None)
        if userdata:
            total_lotto = min(int(userdata["Coin"] / lotto_cost), count)
            if total_lotto > 0:
                lotto_int = int(lotto)
                add_coin(username, -lotto_cost * total_lotto)
                alldata.player_lotto_list += [[username, lotto_int]] * total_lotto
                await send_message(f"@{username} ซื้อ SniffsLotto หมายเลข {lotto} จำนวน {total_lotto} ใบ สำเร็จ sniffsHeart sniffsHeart sniffsHeart")
                buy_lotto_feed(username, lotto, total_lotto, userdata["Coin"])
                print(f"[LOTO] [{get_timestamp()}] {username} buy {lotto} * {total_lotto} successfully")
                return True
            else:
                await send_message(f"@{username} ไม่มีเงินแล้วยังจะซื้ออีก PunOko PunOko PunOko")
                print(f"[LOTO] [{get_timestamp()}] {username} coin insufficient")
                return False


async def draw_lotto(send_message):
    if alldata.player_lotto_list != []:
        print(f"[LOTO] [{get_timestamp()}] All player list : {alldata.player_lotto_list}")
        win_number, lotto_winners = check_winner()
        win_number_string = f"{win_number:02d}"
        count_winners = len(lotto_winners)
        payout = sum(lotto_winners.values())
        for username, prize in lotto_winners.items():
            add_coin(username, int(prize))
        await send_message(f"ประกาศผลรางวัล SniffsLotto เลขที่ออก {win_number_string} sniffsAH มีผู้ชนะทั้งหมด {count_winners} คน ได้รับรางวัลรวม {payout} sniffscoin sniffsHeart")
        if count_winners > 0 and count_winners <= 5:
            await send_message(f"ผู้โชคดีได้แก่ {'@'+', @'.join(lotto_winners.keys())} คร่า sniffsHeart sniffsHeart sniffsHeart")
        draw_lotto_feed(win_number_string, payout, lotto_winners)
        print(f"[LOTO] [{get_timestamp()}] LOTTO draw: {win_number_string} | winners: {count_winners} users | payout: {payout} coin")
        alldata.player_lotto_list = []


@routines.routine(minutes=20)
async def send_lotto_msg(send_message):
    try:
        await send_message("sniffsHi เร่เข้ามาเร่เข้ามา SniffsLotto ใบละ 5 coins !lotto ตามด้วยเลข 2 หลัก ประกาศรางวัลตอนปิดไลฟ์จ้า sniffsAH")
    except RuntimeError:
        raise RuntimeError


@send_lotto_msg.error
async def send_lotto_msg_error(error: Exception):
    print(f"[_ERR] [{get_timestamp()}] ROUTINES: Lotto Message Error with {error}")


async def check_message(username: str, message: str, send_message, timeout):
    restricted_message = ["บอทกาก", "บอทกๅก"]
    exclude_list = alldata.vip_list + alldata.dev_list
    if username not in exclude_list:
        for res_msg in restricted_message:
            result = re.search(res_msg, message)
            if result:
                await timeout(username, 30, f"@{username} ไหน ใครกาก")
                await send_message(f"@{username} บังอาจนักนะ PunOko PunOko")
                print(f"[_MOD] [{get_timestamp()}] Kill: {username} for 30 secs")


async def buy_raffle(username: str, count: int, send_message, timeout):
    raffle_cost = 1
    userdata = next((userdata for userdata in alldata.allusers_stats if userdata["User_Name"] == username), None)
    if userdata:
        total_raffle = min(int(userdata["Coin"] / raffle_cost), count)
        if total_raffle > 0:
            success = raffle_save(username, total_raffle)
            if success:
                add_coin(username, -int(total_raffle * raffle_cost))
                await send_message(f"@{username} ซื้อตั๋วสำเร็จ {total_raffle} ใบ sniffsHeart")
                buy_raffle_feed(username, total_raffle)
                print(f"[RAFL] [{get_timestamp()}] {username} buy {total_raffle} tickets")
                return True
    else:
        await timeout(username, 60, "ไม่มีเงินจ่ายค่าตั๋ว")
        print(f"[RAFL] [{get_timestamp()}] {username} Timeout 60 sec Reason: no money")
        return False


async def draw_raffle(send_message):
    winner = raffle_winner()
    if winner is not None:
        print(f"[RAFL] [{get_timestamp()}] Winner: {winner}")
        await send_message(f"ผู้โชคดีได้แก่ {winner} ค่าาาาา sniffsHeart")
        draw_raffle_feed(winner)
    else:
        print(f"[RAFL] [{get_timestamp()}] Empty raffle list")
        await send_message("ตั๋วหมดโหลแล้วสนิฟ sniffsAH")


# coinflip system
async def buy_coinflip(username: str, side: str, bet: int, send_message):
    prize = bet * 2
    userdata = next((userdata for userdata in alldata.allusers_stats if userdata["User_Name"] == username), None)
    if userdata:
        if userdata["Coin"] >= bet:
            add_coin(username, -bet)
            result, win_side = coinflip(side, bet)
            if win_side == "h":
                win_side = "หัว"
            else:
                win_side = "ก้อย"
            if result:
                await send_message(f"เหรียญออกที่{win_side}ค่า! sniffsHeart ได้รับ {prize} sniff coin")
                add_coin(username, prize)
                coinflip_feed(username, win_side, userdata["Coin"], result, prize)
                print(f"[FLIP] [{get_timestamp()}] {username} won {prize}")
            else:
                await send_message(f"ไม่น้าาาเหรียญออกที่{win_side} sniffsCry")
                coinflip_feed(username, win_side, userdata["Coin"], result)
                print(f"[FLIP] [{get_timestamp()}] {username} lose {bet}")
        else:
            await send_message(f"@{username} ไม่มีเงินแล้วยังจะซื้ออีก PunOko PunOko PunOko")
            print(f"[FLIP] [{get_timestamp()}] {username} coin insufficient")


async def transfer_coin(user: str, recipent: str, amount: int, send_message):
    recipent = re.sub(r'^@', '', recipent)
    recipent = recipent.lower()
    viewers = alldata.get_users_list()
    viewers = [viewer.lower() for viewer in viewers]
    userdata = next((userdata for userdata in alldata.allusers_stats if userdata["User_Name"] == user), None)
    recipentdata = next((userdata for userdata in alldata.allusers_stats if userdata["User_Name"] == recipent), None)
    if not userdata:
        return
    if not(recipentdata or (recipent in viewers)):
        return
    if userdata["Coin"] >= amount:
        add_coin(user, -amount)
        add_coin(recipent, amount)
        print(f"[COIN] [{get_timestamp()}] {user} transfer {amount} sniffscoin to {recipent}")
        await send_message(f"@{user} โอนเหรียญให้ {recipent} จำนวน {amount} Sniffscoin สำเร็จค่าาา~~")
