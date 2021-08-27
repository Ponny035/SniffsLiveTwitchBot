from random import choice


def coinflip(side: str):
    result = choice(("head", "tail"))
    if side[0] == result[0]:
        return True, result[0]
    else:
        return False, result[0]
