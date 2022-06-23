import os
from random import random


flip_rate = int(os.environ.get("fliprate", "50"))
flip_threshold = int(os.environ.get("flipthreshold", "0"))


def coinflip(side: str, bet: int):
    flip = ['h', 't']
    mod = 100
    if bet > flip_threshold:
        mod = flip_rate
    rand = int(random() * mod)
    if rand > flip_rate:
        result = side[0]
    else:
        flip.remove(side[0])
        result = flip[0]
    if side[0] == result[0]:
        return True, result[0]
    else:
        return False, result[0]
