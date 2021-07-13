import random


raffle_list = []
raffle_status = False


def raffle_start(status):
    # clear raffle list every time start raffle
    global raffle_list, raffle_status
    if not raffle_status:
        raffle_status = status
        raffle_list = []
        return True
    return False


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


def raffle_stop(status):
    global raffle_status
    if raffle_status:
        raffle_status = status
        return True
    return False
