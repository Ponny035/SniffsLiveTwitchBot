import random

from src.misc import alldata


def get_winning_number():
    lotto_number = [player[1] for player in alldata.player_lotto_list]
    unique_lotto_list = list(set(lotto_number))
    if len(unique_lotto_list) > 1:
        for i in range(5):
            winning_number = random.choice(unique_lotto_list)
    else:
        winning_number = unique_lotto_list[0]
        while winning_number == unique_lotto_list[0]:
            winning_number = random.randint(0, 99)
    return int(winning_number)


def check_winner():
    win_number = get_winning_number()
    total_income = len(alldata.player_lotto_list) * 5
    tax = 0.2
    if len(alldata.player_lotto_list) > 5:
        min_prize = 10
    else:
        min_prize = 5
    win_prize = (total_income * (1 - tax) + (random.random() * 5))
    winning_dict = {}
    for lotto in alldata.player_lotto_list:
        player_lotto = lotto[1]
        if win_number == player_lotto:
            try:
                winning_dict[lotto[0]] += 1
            except KeyError:
                winning_dict[lotto[0]] = 1
    len_winner = sum(winning_dict.values())
    try:
        final_prize = max(int(win_prize / len_winner), min_prize)
    except ZeroDivisionError:
        final_prize = 0
    winning_dict.update({key: final_prize * winning_dict[key] for key in winning_dict.keys()})
    return win_number, winning_dict
