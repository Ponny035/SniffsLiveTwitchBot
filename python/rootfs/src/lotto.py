import random

def get_winning_number(digit=4):
    winning_number = random.random()
    for i in range(digit):
        winning_number = winning_number * 10
    
    return int(winning_number)

def check_winner(lotto_list):
    win_number = get_winning_number()
    last_two_digits = win_number%100
    last_three_digits = win_number%1000
    winning_list = []
    for lotto in lotto_list:
        player_lotto = lotto[1]
        player_last_two_digits = player_lotto%100
        player_last_three_digits = player_lotto%1000
        if win_number == player_lotto:
            winning_list.append([lotto[0],160])
            continue

        elif last_three_digits == player_last_three_digits:
            winning_list.append([lotto[0],40])
            continue
        
        elif last_two_digits == player_last_two_digits:
            winning_list.append([lotto[0],10])
    return win_number, winning_list