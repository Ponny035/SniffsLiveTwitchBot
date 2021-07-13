import random


def get_winning_number(lotto_list):
    lotto_number = [player[1] for player in lotto_list]
    unique_lotto_list = list(set(lotto_number))
    if len(unique_lotto_list) > 1:
        for i in range(5):
            winning_number = random.choice(unique_lotto_list)
    else:
        winning_number = unique_lotto_list[0]
        while winning_number == unique_lotto_list[0]:
            winning_number = random.randint(0, 99)
    return int(winning_number)


def check_winner(lotto_list):
    win_number = get_winning_number(lotto_list)
    total_income = len(lotto_list) * 5
    tax = 0.2
    if len(lotto_list) > 5:
        min_prize = 10
    else:
        min_prize = 5
    win_prize = (total_income * (1 - tax) + (random.random() * 5))
    winning_dict = {}
    for lotto in lotto_list:
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
    winning_dict.update({n: final_prize * winning_dict[n] for n in winning_dict.keys()})
    return win_number, winning_dict
