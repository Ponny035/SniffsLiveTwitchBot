from .coin import add_coin, payday
from src.timefn.timestamp import get_timestamp
from src.db_function import upsert, retrieve
from src.misc.webfeed import anongift_subscription_payout_feed, bit_to_coin_feed, gift_subscription_payout_feed, giftmystery_subscription_payout_feed, subscription_payout_feed


# const variables
sub_to_point = [5, 10, 25]
bit_to_point = 50


async def subscription_payout(username: str, sub_month_count: str, plan: list[int], usernames: list[str], send_message, send_message_feed):
    plan_select = int(plan[1] / 1000)
    add_coin(username, sub_to_point[plan_select - 1], True)
    payday(usernames, 1, True)
    try:
        userdata = retrieve(username)
        if not userdata:
            userdata = {}
            userdata["User_Name"] = username.lower()
        userdata["Sub_Month"] = int(sub_month_count)
        upsert(userdata)
    except Exception as msg:
        print(f"[_ERR] [{get_timestamp()}] Cannot update db for user {username} with {sub_month_count} submonth {msg}")
    await send_message(f"ยินดีต้อนรับ @{username} มาเป็นต้าวๆของสนิฟ sniffsHeart sniffsHeart sniffsHeart")
    await send_message_feed(f"@{username} ได้รับ {sub_to_point[plan_select - 1]} sniffscoin จากการซับระดับ {plan_select} และผู้ชมทั้งหมด {len(usernames)} คนได้รับ 1 sniffscoin")
    subscription_payout_feed(username, sub_to_point[plan_select - 1], plan_select, len(usernames))
    print(f"[COIN] [{get_timestamp()}] {username} receive {sub_to_point[plan_select - 1]} sniffscoin by sub tier {plan_select}")


async def gift_subscription_payout(username: str, recipent: str, plan: list[int], usernames: list[str], send_message):
    plan_select = int(plan[1] / 1000)
    add_coin(username, sub_to_point[plan_select - 1], True)
    add_coin(recipent, sub_to_point[plan_select - 1], True)
    payday(usernames, 1, True)
    await send_message(f"@{username} ได้รับ {sub_to_point[plan_select - 1]} sniffscoin จากการ Gift ให้ {recipent} ระดับ {plan_select} sniffsHeart sniffsHeart sniffsHeart")
    await send_message(f"@{recipent} ได้รับ {sub_to_point[plan_select - 1]} sniffscoin จากการได้รับ Gift ระดับ {plan_select} และผู้ชมทั้งหมด {len(usernames)} คนได้รับ 1 sniffscoin")
    gift_subscription_payout_feed(username, recipent, sub_to_point[plan_select - 1], plan_select, len(usernames))
    print(f"[COIN] [{get_timestamp()}] {username} receive {sub_to_point[plan_select - 1]} sniffscoin by giftsub to {recipent} tier {plan_select}")


async def giftmystery_subscription_payout(username: str, gift_count: int, plan: list[int], usernames: list[str], send_message):
    plan_select = int(plan[1] / 1000)
    # add_coin(username, sub_to_point * gift_count, True)
    # payday(usernames, 1, True)
    # It seems like giftsub call subgift again, so we don't need to add coin here
    await send_message(f"@{username} ได้รับ {sub_to_point[plan_select - 1] * gift_count} sniffscoin จากการ Gift ระดับ {plan_select} ให้สมาชิก {gift_count} คน sniffsHeart sniffsHeart sniffsHeart")
    giftmystery_subscription_payout_feed(username, sub_to_point[plan_select - 1] * gift_count, gift_count, plan_select)
    print(f"[COIN] [{get_timestamp()}] {username} receive {sub_to_point[plan_select - 1] * gift_count} sniffscoin by giftmysterysub tier {plan_select}")


async def anongift_subscription_payout(recipent: str, plan: list[int], usernames: list[str], send_message, send_message_feed):
    plan_select = int(plan[1] / 1000)
    add_coin(recipent, sub_to_point[plan_select - 1], True)
    payday(usernames, 1, True)
    await send_message(f"ขอบคุณ Gift ระดับ {plan_select} จากผู้ไม่ประสงค์ออกนามค่าา sniffsHeart sniffsHeart sniffsHeart")
    await send_message_feed(f"@{recipent} ได้รับ {sub_to_point[plan_select - 1]} sniffscoin จากการได้รับ Gift ระดับ {plan_select} และผู้ชมทั้งหมด {len(usernames)} คนได้รับ 1 sniffscoin")
    anongift_subscription_payout_feed(recipent, sub_to_point[plan_select - 1], plan_select, len(usernames))
    print(f"[COIN] [{get_timestamp()}] {recipent} receive {sub_to_point[plan_select - 1]} sniffscoin by anongiftsub tier {plan_select}")


async def add_point_by_bit(username: str, bits: int, submonth: int, send_message):
    if submonth > 0:
        mod_rate = min(submonth, 6) / 100
    else:
        mod_rate = 0
    point_to_add = int((bits / bit_to_point) * (1 + mod_rate))
    if point_to_add > 0:
        add_coin(username, point_to_add)
        await send_message(f"@{username} ได้รับ {point_to_add} sniffscoin จากการ Bit จำนวน {bits} bit sniffsHeart sniffsHeart sniffsHeart")
        bit_to_coin_feed(username, point_to_add, bits)
    else:
        await send_message(f"ขอบคุณ @{username} สำหรับ {bits} บิทค้าาา sniffsHeart sniffsHeart sniffsHeart")
