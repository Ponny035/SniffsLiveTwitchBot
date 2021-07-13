import random

rafflelist = []

# beginraffle = "พิม !raffle เพื่อเข้ามาลุ้นของรางวัลกาชาจากสนิฟเลย!"

def rafflesave():
    rafflelist.append()

def get_winner(lotto_list):
    rafflelist = [player[1] for player in rafflesave]
    unique_raffle = list(set(rafflelist))
    if len(unique_raffle) > 1:
        for i in range(5):
            winning_list = random.choice(unique_raffle)
    else:
        winning_list = unique_raffle[0]
        while winning_list == unique_raffle[0]:
            winning_list = random.randint(10000)
    return int(winning_list)
