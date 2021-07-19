import requests


webfeed_url = "http://api-server:8000/api/v1/webfeed"
webfeed_status = True
default_timeout = 10000
long_timeout = 30000

default_tag_name = "tag is-info has-text-weight-bold ml-2 mr-2"
default_tag_viewer = "tag is-primary has-text-weight-bold ml-2 mr-2"
default_snap_name = "tag is-danger has-text-weight-bold ml-2 mr-2"
default_info = "tag is-warning has-text-weight-bold ml-2 mr-2"

gift_icon = "<span class='icon'><i class='fas fa-gift'></i></span>"
lotto_icon = "<span class='icon'><i class='fas fa-cart-plus'></i></span>"
raffle_icon = "<span class='icon'><i class='fas fa-ticket-alt'></i></span>"
coin_icon = "<span class='icon'><i class='fas fa-coins'></i></span>"
sniffsnos_icon = "<span class='icon'><i class='fas fa-hand-point-up'></i></span>"
snappeduser_icon = "<span class='icon'><i class='fas fa-user-alt-slash'></i></span>"
music_icon = "<span class='icon'><i class='fas fa-music'></i></span>"
crosshair_icon = "<span class='icon'><i class='fas fa-crosshairs'></i></span>"
dodge_icon = "<span class='icon'><i class='fas fa-running'></i></span>"
vip_icon = "<span class='icon'><i class='fas fa-user-secret'></i></span>"
suicide_icon = "<span class='icon'><i class='fas fa-hand-point-left'></i></span>"
feed_icon = "<span class='icon'><i class='fas fa-rss'></i></span>"


def activate_webfeed_feed(status):
    global webfeed_status
    if status:
        if not webfeed_status:
            webfeed_status = status
            feedtext = f"<span class='{default_info}'>{feed_icon}</span>"
            feedtext += "<span class='text-white'>Webfeed System started</span>"
            send_feed(feedtext, long_timeout)
    elif not status:
        if webfeed_status:
            webfeed_status = status
            feedtext = f"<span class='{default_info}'>{feed_icon}</span>"
            feedtext += "<span class='text-white'>Webfeed System stopped</span>"
            send_feed(feedtext, long_timeout)


def subscription_payout_feed(username, coin, viewer):
    feedtext_1 = f"<span class='{default_tag_name}'>{username}</span>"
    feedtext_1 += f"<span class='text-white'>ได้รับ {coin_icon} {coin} Sniffscoin จากการ Subscribe</span>"
    send_feed(feedtext_1)
    feedtext_2 = f"<span class='text-white'>สมาชิก</span><span class='{default_tag_viewer}'>{viewer}</span>"
    feedtext_2 += f"<span class='text-white'>คน ได้รับ 1 Sniffscoin {coin_icon} จากการ Subscribe ของ</span>"
    feedtext_2 += f"<span class='{default_tag_name}'>{username}</span>"
    send_feed(feedtext_2)


def gift_subscription_payout_feed(username, recipent, coin, viewer):
    feedtext_1 = f"<span class='{default_tag_name}'>{username}</span>"
    feedtext_1 += f"<span class='text-white'>ได้รับ {coin_icon} {coin} Sniffscoin จากการ {gift_icon} Gift ให้</span><span class='{default_tag_name}'>{recipent}</span>"
    send_feed(feedtext_1)
    feedtext_2 = f"<span class='{default_tag_name}'>{recipent}</span>"
    feedtext_2 += f"<span class='text-white'>ได้รับ {coin_icon} {coin} Sniffscoin</span>"
    send_feed(feedtext_2)
    feedtext_3 = f"<span class='text-white'>สมาชิก</span><span class='{default_tag_viewer}'>{viewer}</span>"
    feedtext_3 += f"<span class='text-white'>คน ได้รับ 1 Sniffscoin {coin_icon}</span>"
    send_feed(feedtext_3)


def giftmystery_subscription_payout_feed(username, coin, gift_count):
    feedtext = f"<span class='{default_tag_name}'>{username}</span>"
    feedtext += f"<span class='text-white'>ได้รับ {coin_icon} {coin} Sniffscoin จากการ {gift_icon} Gift Sub x {gift_count}</span>"
    send_feed(feedtext)


def anongift_subscription_payout_feed(recipent, coin, viewer):
    feedtext_1 = f"<span class='{default_tag_name}'>{recipent}</span>"
    feedtext_1 += f"<span class='text-white'>ได้รับ {coin_icon} {coin} Sniffscoin</span>"
    send_feed(feedtext_1)
    feedtext_2 = f"<span class='text-white'>สมาชิก</span><span class='{default_tag_viewer}'>{viewer}</span>"
    feedtext_2 += f"<span class='text-white'>คน ได้รับ 1 Sniffscoin {coin_icon}</span>"
    send_feed(feedtext_2)


def raid_feed(username, viewer):
    feedtext = "<span class='text-white'>ขอบคุณ</span>"
    feedtext += f"<span class='{default_tag_name}'>{username}</span>"
    feedtext += "<span class='text-white'>สำหรับการ Raid ผู้ชมจำนวน</span>"
    feedtext += f"<span class='{default_tag_viewer}'>{viewer}</span><span class='text-white'>คน</span>"


def bit_to_coin_feed(username, coin, bits):
    feedtext = f"<span class='{default_tag_name}'>{username}</span>"
    feedtext += f"<span class='text-white'>ได้รับ {coin_icon} {coin} Sniffscoin จากการให้ {bits} bit"
    send_feed(feedtext)


def payday_feed(coin, viewer):
    feedtext = f"<span class='text-white'>สมาชิก</span><span class='{default_tag_viewer}'>{viewer}</span>"
    feedtext += f"<span class='text-white'>คน ได้รับ {coin} Sniffscoin {coin_icon}</span>"
    send_feed(feedtext)


def givecoin_feed(username, coin):
    feedtext = f"<span class='{default_tag_name}'>{username}</span>"
    feedtext += f"<span class='text-white'>ได้รับ {coin_icon} {coin} Sniffscoin</span>"
    send_feed(feedtext)


def call_to_hell_feed(username, idx, total):
    feedtext = f"<span class='{default_tag_name}'>SNIFFSNOS</span>"
    feedtext += f"<span class='text-white'>{sniffsnos_icon}</span>"
    feedtext += f"<span class='{default_snap_name}'>{username}</span>"
    feedtext += f"<span class='text-white'>({snappeduser_icon}{idx}/{total})</span>"
    send_feed(feedtext)


def song_request_on_feed():
    feedtext = f"<span class='{default_info}'>{music_icon}</span>"
    feedtext += "<span class='text-white'>เปิดระบบขอเพลง (!sr)</span>"
    send_feed(feedtext, long_timeout)


def song_request_off_feed():
    feedtext = f"<span class='{default_info}'>{music_icon}</span>"
    feedtext += "<span class='text-white'>ปิดระบบขอเพลง</span>"
    send_feed(feedtext, long_timeout)


def user_song_request_feed(username, song_name, coinleft):
    feedtext = f"<span class='{default_tag_name}'>{username}</span>"
    feedtext += f"<span class='text-white'>โหวตเพลง {song_name} {music_icon} ({coinleft})</span>"
    send_feed(feedtext)


def shooter_suicide_feed(username, timeout):
    feedtext = f"<span class='{default_snap_name}'>{username}</span>"
    feedtext += f"<span class='text-white'>{suicide_icon} แวะไปเยือนยมโลก {timeout}s</span>"
    send_feed(feedtext)


def shooter_success_feed(username, target, timeout, coinleft):
    feedtext = f"<span class='{default_tag_name}'>{username}</span>"
    feedtext += f"<span class='text-white'>จ้างมือปินสนิฟ {crosshair_icon} ยิง</span>"
    feedtext += f"<span class='{default_snap_name}'>{target}</span>"
    feedtext += f"<span class='text-white'>{timeout}s ({coinleft})</span>"
    send_feed(feedtext)


def shooter_dodge_feed(target, dodge_rate):
    feedtext = f"<span class='{default_snap_name}'>{target}</span>"
    feedtext += f"<span class='text-white'>หลบมือปืนสนิฟได้ {dodge_icon} ({int(dodge_rate)}%)"
    send_feed(feedtext)


def shooter_unsuccess_feed(username, timeout):
    feedtext = f"<span class='{default_snap_name}'>{username}</span>"
    feedtext += f"<span class='text-white'>ไม่มีเงินจ้างมือปืน ถูกยิงเอง {crosshair_icon} {timeout}s</span>"
    send_feed(feedtext)


def shooter_vip_feed(username, timeout):
    feedtext = f"<span class='{default_snap_name}'>{username}</span>"
    feedtext += f"<span class='text-white'>บังอาจยิง {vip_icon} VIP โดนยิงเอง {crosshair_icon} {timeout}s</span>"
    send_feed(feedtext)


def lotto_start_feed():
    feedtext = f"<span class='{default_info}'>{lotto_icon}</span>"
    feedtext += "<span class='text-white'>เปิดระบบ SniffsLotto (!lotto)</span>"
    send_feed(feedtext, long_timeout)


def lotto_stop_feed():
    feedtext = f"<span class='{default_info}'>{lotto_icon}</span>"
    feedtext += "<span class='text-white'>ปิดระบบ SniffsLotto รอประกาศรางวัล</span>"
    send_feed(feedtext, long_timeout)


def buy_lotto_feed(username, lotto):
    feedtext = f"<span class='{default_tag_name}'>{username}</span>"
    feedtext += f"<span class='text-white'>ซื้อ {lotto_icon} SniffsLotto หมายเลข {lotto} สำเร็จ</span>"
    send_feed(feedtext)


def draw_lotto_feed(win_number_string, payout, lotto_winners):
    feedtext_1 = f"<span class='{default_info}'>SniffsLotto</span>"
    feedtext_1 += f"<span class='text-white'>เลขที่ออก</span><span class='{default_tag_viewer}'>{win_number_string}</span>"
    feedtext_1 += f"<span class='text-white'>เงินรางวัลรวม {coin_icon} {payout} Sniffscoin</span>"
    send_feed(feedtext_1, long_timeout)
    for username, prize in lotto_winners.items():
        feedtext_2 = f"<span class='{default_tag_name}'>{username}</span>"
        feedtext_2 += f"<span class='text-white'>ได้รับ {coin_icon} {prize} Sniffscoin</span>"
        send_feed(feedtext_2, long_timeout)


def raffle_start_feed():
    feedtext = f"<span class='{default_info}'>{raffle_icon}</span>"
    feedtext += "<span class='text-white'>เปิดให้ซื้อตั๋วชิงโชค (!raffle)</span>"
    send_feed(feedtext, long_timeout)


def raffle_stop_feed():
    feedtext = f"<span class='{default_info}'>{raffle_icon}</span>"
    feedtext += "<span class='text-white'>ปิดการซื้อตั๋วชิงโชค รอจับรางวัล</span>"
    send_feed(feedtext, long_timeout)


def draw_raffle_feed(username):
    feedtext = f"<span class='{default_tag_name}'>{username}</span>"
    feedtext += f"<span class='text-white'>ได้รับรางวัล {raffle_icon}</span>"
    send_feed(feedtext, long_timeout)


def buy_raffle_feed(username, count):
    feedtext = f"<span class='{default_tag_name}'>{username}</span>"
    feedtext += f"<span class='text-white'>ซื้อตั๋วชิงโชค {raffle_icon} {count} ใบ"
    send_feed(feedtext)


def send_feed(feedtext, timeout=default_timeout):
    requests.post(webfeed_url, json={'message': feedtext, 'timeout': timeout})
