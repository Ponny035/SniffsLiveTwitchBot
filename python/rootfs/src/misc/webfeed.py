import base64
import json
import requests

from twitchio.models import Stream

from src.misc import alldata
from src.timefn.timestamp import get_timestamp


webfeed_url = "https://rest.ably.io/channels/webfeed/messages"
default_timeout = 10000
long_timeout = 30000


def activate_webfeed_feed():
    if alldata.feed_enable:
        send_feed("webfeed", {"status": True}, long_timeout)
    elif not alldata.feed_enable:
        send_feed("webfeed", {"status": False}, long_timeout)


def subscription_payout_feed(username: str, coin: int, plan: int, viewer: int):
    send_feed("subPayout", {"username": username, "coin": coin, "plan": plan, "viewer": viewer})


def gift_subscription_payout_feed(username: str, recipent: str, coin: int, plan: int, viewer: int):
    send_feed("giftSubPayout", {"username": username, "recipent": recipent, "coin": coin, "plan": plan, "viewer": viewer})


def giftmystery_subscription_payout_feed(username, coin, gift_count, plan):
    send_feed("giftMystSubPayout", {"username": username, "coin": coin, "giftCount": gift_count, "plan": plan})


def anongift_subscription_payout_feed(recipent, coin, plan, viewer):
    send_feed("anonGiftSubPayout", {"recipent": recipent, "coin": coin, "plan": plan, "viewer": viewer})


def raid_feed(username, viewer):
    send_feed("raidfeed", {"username": username, "viewer": viewer})


def bit_to_coin_feed(username, coin, bits):
    send_feed("bitfeed", {"username": username, "coin": coin, "bits": bits})


def payday_feed(coin, viewer):
    send_feed("paydayfeed", {"coin": coin, "viewer": viewer})


def givecoin_feed(username, coin):
    send_feed("givecoinfeed", {"username": username, "coin": coin})


def deductcoin_feed(username, coin):
    send_feed("deductcoinfeed", {"username": username, "coin": coin})


def call_to_hell_feed(username, idx, total):
    send_feed("sniffsnos", {"username": username, "idx": idx, "total": total})


def song_request_on_feed():
    send_feed("songReqStat", {"status": True}, long_timeout)


def song_request_off_feed():
    send_feed("songReqStat", {"status": False}, long_timeout)


def user_song_request_feed(username, song_name, coinleft):
    send_feed("userSongReq", {"username": username, "songName": song_name, "coinleft": coinleft})


def shooter_suicide_feed(username, timeout):
    send_feed("shooterSuicideFeed", {"username": username, "timeout": timeout})


def shooter_success_feed(username, target, timeout, coinleft):
    send_feed("shooterSuccessFeed", {"username": username, "target": target, "timeout": timeout, "coinleft": coinleft})


def shooter_dodge_feed(target, dodge_rate):
    send_feed("shooterDodgeFeed", {"target": target, "dodgeRate": dodge_rate})


def shooter_unsuccess_feed(username, timeout):
    send_feed("shooterUnsuccessFeed", {"username": username, "timeout": timeout})


def shooter_vip_feed(username, timeout):
    send_feed("shooterVIPFeed", {"username": username, "timeout": timeout})


def lotto_start_feed():
    send_feed("lottoStat", {"status": True}, long_timeout)


def lotto_stop_feed():
    send_feed("lottoStat", {"status": True}, long_timeout)


def buy_lotto_feed(username, lotto, coinleft):
    send_feed("buyLottoFeed", {"username": username, "lotto": lotto, "coinleft": coinleft})
    send_discord('lottobuy', {
        "username": username,
        "lotto": lotto,
        "coinleft": coinleft
    })


def draw_lotto_feed(win_number_string, payout, lotto_winners):
    send_feed("drawLottoFeed", {"winNumber": win_number_string, "payout": payout, "usernames": lotto_winners}, long_timeout)
    send_discord("lottodraw", {
        "usernames": lotto_winners,
        "win_number": win_number_string,
        "payout": payout
    })


def raffle_start_feed():
    send_feed("raffleStat", {"status": True}, long_timeout)


def raffle_stop_feed():
    send_feed("raffleStat", {"status": False}, long_timeout)


def buy_raffle_feed(username, count):
    send_feed("buyRaffleFeed", {"username": username, "count": count})
    send_discord("rafflebuy", {
        "username": username,
        "count": count
    })


def draw_raffle_feed(username):
    send_feed("drawRaffleFeed", {"username": username})
    send_discord("raffledraw", {
        "username": username
    })


def coinflip_feed(username, win_side, coin_left, win, prize=None):
    send_feed("coinflipFeed", {"username": username, "winside": win_side, "coinleft": coin_left, "win": win, "prize": prize})
    send_discord('coinflip', {
        'username': username,
        'win_side': win_side,
        'coin_left': coin_left,
        'win': win,
        'prize': prize
    })


def live_notification_feed(channel: Stream):
    payload = json.dumps({
        "user_name": channel.user.name,
        "title": channel.title,
        "game_name": channel.game_name,
        "viewers": channel.viewer_count,
        "thumbnail_url": channel.thumbnail_url
    })
    res = requests.post(webfeed_url,
                        headers={'Authorization': "Basic " + base64.b64encode(alldata.ABLYKEY.encode()).decode()},
                        json={'name': 'livemessage', 'data': payload})
    if res.status_code == 201:
        print(f"[INFO] [{get_timestamp()}] Send Webfeed success")
    else:
        print(f"[WARN] [{get_timestamp()}] unable to Send Webfeed with {res.json()}")


def send_feed(msgtype, feedtext, timeout=default_timeout):
    payload = json.dumps({"type": msgtype, "message": feedtext, "timeout": timeout})
    res = requests.post(webfeed_url,
                        headers={'Authorization': "Basic " + base64.b64encode(alldata.ABLYKEY.encode()).decode()},
                        json={'name': 'feedmessage', 'data': payload})
    if res.status_code == 201:
        print(f"[INFO] [{get_timestamp()}] Send Webfeed success")
    else:
        print(f"[WARN] [{get_timestamp()}] unable to Send Webfeed with {res.json()}")


def send_discord(type: str, message: dict):
    payload = json.dumps(message)
    res = requests.post(webfeed_url,
                        headers={'Authorization': "Basic " + base64.b64encode(alldata.ABLYKEY.encode()).decode()},
                        json={'name': type, 'data': payload})
    if res.status_code == 201:
        print(f"[INFO] [{get_timestamp()}] Send Webfeed success")
    else:
        print(f"[WARN] [{get_timestamp()}] unable to Send Webfeed with {res.json()}")
