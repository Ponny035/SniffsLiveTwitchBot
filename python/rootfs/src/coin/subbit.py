from .coin import add_coin, payday
from src.timefn.timestamp import get_timestamp
from src.db_function import check_exist, insert, retrieve, update


# const variables
sub_to_point = 10
bit_to_point = 50


async def subscription_payout(username, sub_month_count, usernames, send_message):
    add_coin(username, sub_to_point, True)
    payday(usernames, 1, True)
    try:
        if check_exist(username):
            userdata = retrieve(username)
            userdata["submonth"] = int(sub_month_count)
            update(userdata)
        else:
            userdata = {
                "username": username,
                "coin": 0,
                "watchtime": 0,
                "submonth": int(sub_month_count)
            }
            insert(userdata)
    except Exception as msg:
        print(f"[_ERR] [{get_timestamp()}] Cannot update db for user {username} with {sub_month_count} submonth {msg}")
    await send_message(f"ยินดีต้อนรับ @{username} มาเป็นต้าวๆของสนิฟ sniffsHeart sniffsHeart sniffsHeart")
    await send_message(f"@{username} ได้รับ {sub_to_point} sniffscoin และผู้ชมทั้งหมด {len(usernames)} คนได้รับ 1 sniffscoin")
    print(f"[COIN] [{get_timestamp()}] {username} receive {sub_to_point} sniffscoin by sub")


async def gift_subscription_payout(username, recipent, usernames, send_message):
    add_coin(username, sub_to_point, True)
    add_coin(recipent, sub_to_point, True)
    payday(usernames, 1, True)
    await send_message(f"@{username} ได้รับ {sub_to_point} sniffscoin จากการ Gift ให้ {recipent} sniffsHeart sniffsHeart sniffsHeart")
    await send_message(f"@{recipent} ได้รับ {sub_to_point} sniffscoin และผู้ชมทั้งหมด {len(usernames)} คนได้รับ 1 sniffscoin")
    print(f"[COIN] [{get_timestamp()}] {username} receive {sub_to_point} sniffscoin by giftsub to {recipent}")


async def giftmystery_subscription_payout(username, gift_count, usernames, send_message):
    add_coin(username, sub_to_point * gift_count, True)
    payday(usernames, 1, True)
    await send_message(f"@{username} ได้รับ {sub_to_point * gift_count} sniffscoin จากการ Gift ให้สมาชิก {gift_count} คน sniffsHeart sniffsHeart sniffsHeart")
    print(f"[COIN] [{get_timestamp()}] {username} receive {sub_to_point * gift_count} sniffscoin by giftmysterysub")


async def anongift_subscription_payout(recipent, usernames, send_message):
    add_coin(recipent, sub_to_point, True)
    payday(usernames, 1, True)
    await send_message("ขอบคุณ Gift จากผู้ไม่ประสงค์ออกนามค่าา sniffsHeart sniffsHeart sniffsHeart")
    await send_message(f"@{recipent} ได้รับ {sub_to_point} sniffscoin และผู้ชมทั้งหมด {len(usernames)} คนได้รับ 1 sniffscoin")
    print(f"[COIN] [{get_timestamp()}] {recipent} receive {sub_to_point} sniffscoin by anongiftsub")


async def add_point_by_bit(username, bits, submonth, send_message):
    if submonth > 0:
        mod_rate = min(submonth, 6) / 100
    else:
        mod_rate = 0
    point_to_add = int((bits / bit_to_point) * (1 + mod_rate))
    if point_to_add > 0:
        add_coin(username, point_to_add)
        await send_message(f"@{username} ได้รับ {point_to_add} sniffscoin จากการ Bit จำนวน {bits} bit sniffsHeart sniffsHeart sniffsHeart")
    else:
        await send_message(f"ขอบคุณ @{username} สำหรับ {bits} บิทค้าาา sniffsHeart sniffsHeart sniffsHeart")
