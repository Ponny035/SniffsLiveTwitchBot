from random import choice, randint
from time import time


from .. import db_function


def coinflip(bot, user, side=None, *args):
    if side is None:
        bot.send_message("ต้องเดาข้างที่จะตกก่อนนะ!")

    elif (side := side.lower()) not in (opt := ("h", "t", "head", "tails", "หัว", "ก้อย")):
        bot.send_message("ใส่ด้านของเหรียญตามนี้เท่านั้นนะ!:"+", ".join(opt))

    else:
        result = choice(("heads","tails"))

        if side[0] == result[0]:
            bot.send_message(f"เหรียญออกที่ {result}ค่า! ได้รับx sniff coin")
            
        else:
            bot.send_message(f"ไม่น้าาาเหรียญออกที่ {result}")