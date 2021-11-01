import random


raffle_list: list = []


def raffle_start():
    # clear raffle list every time start raffle
    global raffle_list
    raffle_list = []


def raffle_save(username, count):
    global raffle_list
    raffle_list += [username] * count
    return True


def raffle_winner():
    global raffle_list
    if len(raffle_list) > 0:
        rand = random.randint(0, len(raffle_list) - 1)
        winner = raffle_list[rand]
        del raffle_list[rand]
        return winner
    return None
