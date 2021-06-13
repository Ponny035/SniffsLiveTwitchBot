import asyncio
from datetime import datetime
import random
import re

from .db_function import DBManager


class UserFunction:
    def __init__(self, environment):
        self.db_manager = DBManager(environment)
        self.environment = environment
        self.watchtime_session = {}
        self.user_point = {}
        self.command_cooldown = {}
        self.song_list = {}
        self.sorted_song_list = []
        self.song_playing = None
        self.channel_live = False
        self.coin_join_before_live = 5
        self.sub_to_point = 10  # 1 sub for 10 point
        self.bit_to_point = 50  # 50 bits for 1 point
        self.watchtime_to_point = 10  # 10 min to 1 point
        self.cooldown = 20

    def get_timestamp(self):
        return datetime.utcnow().replace(microsecond=0)

    def sec_to_hms(self, time):
        hour = min = sec = 0
        try:
            hour = int(time / 3600)
            min = int((time / 60) - (60 * hour))
            sec = int(time % 60)
        except:
            pass
        return [hour, min, sec]

    def print_to_console(self, msg):
        if self.environment == "dev":
            print(msg)

    async def activate_point_system(self, live, starttime=None, usernames=None):
        self.channel_live = live
        if (live) and (starttime is not None):
            self.channel_live_on = starttime
            if usernames is not None:
                for username in usernames:
                    self.user_join_part("join", username.lower(), self.channel_live_on)
                    self.add_coin(username.lower(), self.coin_join_before_live)
            await self.add_point_by_watchtime()
        else:
            self.channel_live_on = None

    # watchtime related system
    def user_join_part(self, status, username, timestamp):
        try:
            if self.watchtime_session[username]["status"] != status:
                self.watchtime_session[username]["status"] = status
                if status == "join":
                    self.watchtime_session[username]["join_on"] = timestamp
                elif status == "part":
                    self.watchtime_session[username]["part_on"] = timestamp
                    self.update_user_watchtime()
        except KeyError:
            self.watchtime_session[username] = {}
            self.watchtime_session[username]["status"] = status
            if status == "join":
                self.watchtime_session[username]["join_on"] = timestamp
            elif status == "part":
                self.watchtime_session[username]["part_on"] = timestamp
                self.update_user_watchtime()
        # TODO: write watchtime to DB when user part

    def update_user_watchtime(self):
        if self.channel_live:
            for user_stat in self.watchtime_session.values():
                now = self.get_timestamp()
                if user_stat["status"] == "join":
                    user_stat["watchtime_session"] = (now - max(user_stat["join_on"], self.channel_live_on)).total_seconds()
                else:
                    user_stat["watchtime_session"] = (user_stat["part_on"] - max(user_stat["join_on"], self.channel_live_on)).total_seconds()
        elif self.watchtime_session != {}:
            # TODO: write watchtime to DB when live end
            self.print_to_console("write watchtime to DB")
            self.print_to_console(f"[_LOG] {self.watchtime_session}")
            self.watchtime_session = {}

    async def add_point_by_watchtime(self):
        while self.channel_live:
            self.update_user_watchtime()
            for username, user_stat in self.watchtime_session.items():
                watchtime_to_point = self.watchtime_to_point * 60
                try:
                    watchtime_session = user_stat["watchtime_session"]
                except KeyError:
                    watchtime_session = 0
                try:
                    watchtime_redeem = user_stat["watchtime_redeem"]
                except KeyError:
                    watchtime_redeem = 0
                point_to_add = int((watchtime_session - watchtime_redeem) / watchtime_to_point)
                watchtime_redeem += point_to_add * watchtime_to_point
                user_stat["watchtime_redeem"] = watchtime_redeem
                self.add_coin(username, point_to_add)
                # print(f"User: {username} ได้รับ {point_to_add} sniffscoin จากการดูไลฟ์ครบ {str(int((point_to_add * watchtime_to_point) / 60))} นาที")
            await asyncio.sleep(self.watchtime_to_point * 60)
        self.print_to_console("write point to DB")
        self.print_to_console(f"[_LOG] {self.user_point}")

    def get_user_watchtime(self, username):
        self.update_user_watchtime()
        try:
            watchtime = self.watchtime_session[username]["watchtime_session"]
            # TODO: fetch watchtime from DB
        except KeyError:
            watchtime = 0
        watchtime_hms = self.sec_to_hms(watchtime)
        print(f"[TIME] [{self.get_timestamp()}] Watchtime checked by {username}: {watchtime_hms[0]} hours {watchtime_hms[1]} mins {watchtime_hms[2]} secs")
        return watchtime_hms

    # coin related system
    def add_coin(self, username, coin, nolog=False):
        try:
            self.user_point[username] += coin
        except KeyError:
            self.user_point[username] = coin
        if not nolog:
            print(f"[COIN] [{self.get_timestamp()}] User: {username} receive(deduct) {coin} sniffscoin")

    def get_coin(self, username):
        try:
            coin = self.user_point[username]
        except KeyError:
            coin = 0
        print(f"[COIN] [{self.get_timestamp()}] Coin checked by {username}: {coin} sniffscoin")
        return coin

    def payday(self, usernames, coin, nolog=False):
        for username in usernames:
            self.add_coin(username.lower(), coin, nolog)
        print(f"[COIN] [{self.get_timestamp()}] All {len(usernames)} users receive {coin} sniffscoin")

    def subscription_payout(self, username, usernames):
        self.add_coin(username, self.sub_to_point)
        self.payday(usernames, 1, True)
        response1 = f"ยินดีต้อนรับ @{username} มาเป็นต้าวๆของสนิฟ"
        response2 = f"@{username} ได้รับ {self.sub_to_point} sniffscoin และผู้ชมทั้งหมด {len(usernames)} คนได้รับ 1 sniffscoin"
        print(f"[COIN] [{self.get_timestamp()}] {username} receive {self.sub_to_point} sniffscoin by sub")
        return [response1, response2]

    def gift_subscription_payout(self, username, recipent, usernames):
        self.add_coin(username, self.sub_to_point)
        self.add_coin(recipent, self.sub_to_point)
        self.payday(usernames, 1, True)
        response1 = f"@{username} ได้รับ {self.sub_to_point} sniffscoin จากการ Gift ให้ {recipent}"
        response2 = f"@{recipent} ได้รับ {self.sub_to_point} sniffscoin และผู้ชมทั้งหมด {len(usernames)} คนได้รับ 1 sniffscoin"
        print(f"[COIN] [{self.get_timestamp()}] {username} receive {self.sub_to_point} sniffscoin by giftsub to {recipent}")
        return [response1, response2]

    def giftmystery_subscription_payout(self, username, gift_count, usernames):
        self.add_coin(username, self.sub_to_point * gift_count)
        self.payday(usernames, 1, True)
        response1 = f"@{username} ได้รับ {self.sub_to_point * gift_count} sniffscoin จากการ Gift ให้สมาชิก {gift_count} คน"
        print(f"[COIN] [{self.get_timestamp()}] {username} receive {self.sub_to_point * gift_count} sniffscoin by giftmysterysub")
        return [response1]

    def anongift_subscription_payout(self, recipent, usernames):
        self.add_coin(recipent, self.sub_to_point)
        self.payday(usernames, 1, True)
        response1 = f"ขอบคุณ Gift จากผู้ไม่ประสงค์ออกนามค่าา"
        response2 = f"@{recipent} ได้รับ {self.sub_to_point} sniffscoin และผู้ชมทั้งหมด {len(usernames)} คนได้รับ 1 sniffscoin"
        print(f"[COIN] [{self.get_timestamp()}] {recipent} receive {self.sub_to_point} sniffscoin by anongiftsub")
        return [response1, response2]

    async def add_point_by_bit(self, username, bits):
        response = ""
        point_to_add = int(bits / self.bit_to_point)
        if point_to_add > 0:
            self.add_coin(username, point_to_add)
            response = f"@{username} ได้รับ {point_to_add} sniffscoin จากการ Bit จำนวน {bits} bit"
            return response

    # mod function
    async def call_to_hell(self, usernames, exclude_list, timeout):
        print(f"[HELL] [{self.get_timestamp()}] Wanna go to hell?")
        callhell_timeout = 180
        casualtie = 0
        usernames = [username for username in usernames if username not in exclude_list]
        number_user = int(len(usernames) / 2)
        random.shuffle(usernames)
        poor_users = usernames[:number_user]
        if self.environment == "dev":
            callhell_timeout = 60  # for testing purpose only
            try:
                poor_users.remove("bosssoq")
            except ValueError:
                pass
            poor_users += ["sirju001"]
        for username in poor_users:
            casualtie += 1
            print(f"[HELL] [{self.get_timestamp()}] Timeout: {username} Duration: {callhell_timeout} Reason: โดนสนิฟดีดนิ้ว")
            await timeout(username, callhell_timeout, "โดนสนิฟดีดนิ้ว")
            await asyncio.sleep(1)
        data = {
            "casualtie": casualtie,
            "poor_users": poor_users
        }
        return data

    # song request system
    async def user_song_request(self, content, timestamp, username, send_message):
        song_name = re.search("(?<=\\!sr ).+", content)[0]
        if song_name is not None:
            song_name = song_name.strip().lower()
            try:
                self.song_list[song_name]["vote"] -= 1
            except KeyError:
                self.song_list[song_name] = {}
                self.song_list[song_name]["vote"] = -1
                self.song_list[song_name]["timestamp"] = timestamp
            await send_message(f"@{username} โหวตเพลง {song_name}")

    async def now_playing(self, username, send_message):
        if self.song_playing is not None:
            await send_message(f"@{username} สนิฟกำลังร้องเพลง {self.song_playing} น้า")

    async def sorted_song(self):
        try:
            self.sorted_song_list = sorted(self.song_list.keys(), key=lambda song_name: (self.song_list[song_name]["vote"], self.song_list[song_name]["timestamp"]))
        except:
            self.sorted_song_list = []

    async def get_song_list(self, send_message):
        await self.sorted_song()
        if self.sorted_song_list != []:
            await send_message("List เพลงจากต้าวๆ")
            max_song_list = min(len(self.song_list), 5)
            for i in range(0, max_song_list):
                await send_message(f"[{i + 1}] {self.sorted_song_list[i]} {-self.song_list[self.sorted_song_list[i]]['vote']} คะแนน")
                print(f"[SONG] [{self.get_timestamp()}] {i + 1} {self.sorted_song_list[i]} {-self.song_list[self.sorted_song_list[i]]['vote']} point")
        else:
            await send_message("ยังไม่มีเพลงในคิวจ้า")

    async def select_song(self, song_id, send_message):
        song_id = int(song_id)
        try:
            self.song_playing = self.sorted_song_list[song_id - 1]
            try:
                del self.song_list[self.song_playing]
            except KeyError:
                print(f"[SONG] [{self.get_timestamp()}] Failed to delete song {self.song_playing} from list")
            self.sorted_song_list = []
            await send_message(f"สนิฟเลือกเพลง {self.song_playing}")
            print(f"[SONG] [{self.get_timestamp()}] Sniffs choose {self.song_playing} Delete this song from list")
        except IndexError:
            await send_message("ไม่มีเพลงนี้น้า")
            print(f"[SONG] [{self.get_timestamp()}] No song in list")

    async def delete_songlist(self):
        self.song_playing = ""
        self.song_list = {}
        self.sorted_song_list = []

    async def delete_song(self, song_id, send_message):
        song_id = int(song_id)
        if self.sorted_song_list != []:
            try:
                del_song = self.sorted_song_list[song_id - 1]
                del self.song_list[del_song]
                await send_message(f"ลบเพลง {del_song} เรียบร้อยแล้วจ้า")
                await self.get_song_list(send_message)
            except:
                print(f"[SONG] [{self.get_timestamp()}] Failed to delete song {song_id} from list")

    # cooldown related system
    def set_cooldown(self, username, command):
        now = self.get_timestamp()
        try:
            self.command_cooldown[username][command] = now
        except KeyError:
            self.command_cooldown[username] = {}
            self.command_cooldown[username][command] = now

    def check_cooldown(self, username, command, cooldown=None):
        if cooldown is None:
            cooldown = self.cooldown
        try:
            timestamp = self.command_cooldown[username][command]
            now = self.get_timestamp()
            diff = (now - timestamp).total_seconds()
            if diff > self.cooldown:
                return True
            else:
                print(f"[INFO] [{self.get_timestamp()}] COOLDOWN: {username} COMMAND: {command} DURATION: {self.cooldown - diff}s")
                return False
        except KeyError:
            return True
