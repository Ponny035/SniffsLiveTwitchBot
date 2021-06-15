import asyncio
from datetime import datetime
import json
import random
import re
import requests

from .db_function import DBManager
import lotto


class UserFunction:
    def __init__(self, environment):
        self.db_manager = DBManager(environment)
        self.lotto = lotto()
        self.environment = environment

        self.watchtime_session = {}
        # self.user_point = {}
        self.command_cooldown = {}
        # self.song_list = {}
        self.sorted_song_list = []
        self.player_lotto_list = []
        self.song_playing = None
        self.channel_live = False

        self.list_url = 'http://api-server:8000/api/v1/songlist'
        self.vote_url = 'http://api-server:8000/api/v1/vote'
        self.select_url = 'http://api-server:8000/api/v1/select'
        self.delete_url = 'http://api-server:8000/api/v1/del'
        self.clear_url = 'http://api-server:8000/api/v1/clear'

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
            self.update_user_watchtime(True)

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

    def update_user_watchtime(self, force=False):
        if self.channel_live and self.watchtime_session != {}:
            for user_stat in self.watchtime_session.values():
                now = self.get_timestamp()
                if user_stat["status"] == "join":
                    user_stat["watchtime_session"] = int((now - max(user_stat["join_on"], self.channel_live_on)).total_seconds())
                else:
                    user_stat["watchtime_session"] = int((user_stat["part_on"] - max(user_stat["join_on"], self.channel_live_on)).total_seconds())
        if force and self.watchtime_session != {}:
            for user_stat in self.watchtime_session.values():
                now = self.get_timestamp()
                if user_stat["status"] == "join":
                    user_stat["watchtime_session"] = int((now - max(user_stat["join_on"], self.channel_live_on)).total_seconds())
                else:
                    user_stat["watchtime_session"] = int((user_stat["part_on"] - max(user_stat["join_on"], self.channel_live_on)).total_seconds())
        if (not self.channel_live) and (self.watchtime_session != {}):
            self.print_to_console("write watchtime to DB")
            for username, user_stat in self.watchtime_session.items():
                try:
                    if user_stat["watchtime_session"] != 0:
                        if self.db_manager.check_exist(username):
                            userdata = self.db_manager.retrieve(username)
                            userdata["watchtime"] += int(user_stat["watchtime_session"])
                            self.db_manager.update(userdata)
                        else:
                            userdata = {
                                "username": username,
                                "coin": 0,
                                "watchtime": int(user_stat["watchtime"]),
                                "submonth": 0
                            }
                            self.db_manager.insert(userdata)
                            self.print_to_console(f"[_LOG] {self.watchtime_session}")
                            self.watchtime_session = {}
                except KeyError:
                    pass

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
                if point_to_add > 0:
                    self.add_coin(username, point_to_add)
            await asyncio.sleep(self.watchtime_to_point * 60)
        # self.print_to_console("write point to DB")
        # self.print_to_console(f"[_LOG] {self.user_point}")

    def get_user_watchtime(self, username, live):
        if live:
            self.update_user_watchtime()
        try:
            watchtime_session = self.watchtime_session[username]["watchtime_session"]
        except KeyError:
            watchtime_session = 0
        if self.db_manager.check_exist(username):
            watchtime_past = self.db_manager.retrieve(username)["watchtime"]
        else:
            watchtime_past = 0
        watchtime = watchtime_past + watchtime_session
        watchtime_hms = self.sec_to_hms(watchtime)
        print(f"[TIME] [{self.get_timestamp()}] Watchtime checked by {username}: {watchtime_hms[0]} hours {watchtime_hms[1]} mins {watchtime_hms[2]} secs")
        return watchtime_hms

    # coin related system
    def add_coin(self, username, coin, nolog=False):
        # try:
        #     self.user_point[username] += coin
        # except KeyError:
        #     self.user_point[username] = coin
        if self.db_manager.check_exist(username):
            userdata = self.db_manager.retrieve(username)
            userdata['coin'] += coin
            self.db_manager.update(userdata)
        else:
            userdata = {
                "username": username,
                "coin": coin,
                "watchtime": 0,
                "submonth": 0
            }
            self.db_manager.insert(userdata)
        if not nolog:
            print(f"[COIN] [{self.get_timestamp()}] User: {username} receive(deduct) {coin} sniffscoin")

    def get_coin(self, username):
        # try:
        #     coin = self.user_point[username]
        # except KeyError:
        #     coin = 0
        if self.db_manager.check_exist(username):
            coin = self.db_manager.retrieve(username)['coin']
        else:
            coin = 0
        print(f"[COIN] [{self.get_timestamp()}] Coin checked by {username}: {coin} sniffscoin")
        return coin

    def payday(self, usernames, coin, nolog=False):
        for username in usernames:
            self.add_coin(username.lower(), coin, nolog)
        print(f"[COIN] [{self.get_timestamp()}] All {len(usernames)} users receive {coin} sniffscoin")

    def subscription_payout(self, username, sub_month_count, usernames):
        self.add_coin(username, self.sub_to_point, True)
        self.payday(usernames, 1, True)
        try:
            if self.db_manager.check_exist(username):
                userdata = self.db_manager.retrieve(username)
                userdata["submonth"] = int(sub_month_count)
                self.db_manager.update(userdata)
            else:
                userdata = {
                    "username": username,
                    "coin": 0,
                    "watchtime": 0,
                    "submonth": int(sub_month_count)
                }
                self.db_manager.insert(userdata)
        except:
            print(f"[_ERR] [{self.get_timestamp()}] Cannot update db for user {username} with {sub_month_count} submonth")
        response1 = f"ยินดีต้อนรับ @{username} มาเป็นต้าวๆของสนิฟ"
        response2 = f"@{username} ได้รับ {self.sub_to_point} sniffscoin และผู้ชมทั้งหมด {len(usernames)} คนได้รับ 1 sniffscoin"
        print(f"[COIN] [{self.get_timestamp()}] {username} receive {self.sub_to_point} sniffscoin by sub")
        return [response1, response2]

    def gift_subscription_payout(self, username, recipent, usernames):
        self.add_coin(username, self.sub_to_point, True)
        self.add_coin(recipent, self.sub_to_point, True)
        self.payday(usernames, 1, True)
        response1 = f"@{username} ได้รับ {self.sub_to_point} sniffscoin จากการ Gift ให้ {recipent}"
        response2 = f"@{recipent} ได้รับ {self.sub_to_point} sniffscoin และผู้ชมทั้งหมด {len(usernames)} คนได้รับ 1 sniffscoin"
        print(f"[COIN] [{self.get_timestamp()}] {username} receive {self.sub_to_point} sniffscoin by giftsub to {recipent}")
        return [response1, response2]

    def giftmystery_subscription_payout(self, username, gift_count, usernames):
        self.add_coin(username, self.sub_to_point * gift_count, True)
        self.payday(usernames, 1, True)
        response1 = f"@{username} ได้รับ {self.sub_to_point * gift_count} sniffscoin จากการ Gift ให้สมาชิก {gift_count} คน"
        print(f"[COIN] [{self.get_timestamp()}] {username} receive {self.sub_to_point * gift_count} sniffscoin by giftmysterysub")
        return [response1]

    def anongift_subscription_payout(self, recipent, usernames):
        self.add_coin(recipent, self.sub_to_point, True)
        self.payday(usernames, 1, True)
        response1 = f"ขอบคุณ Gift จากผู้ไม่ประสงค์ออกนามค่าา"
        response2 = f"@{recipent} ได้รับ {self.sub_to_point} sniffscoin และผู้ชมทั้งหมด {len(usernames)} คนได้รับ 1 sniffscoin"
        print(f"[COIN] [{self.get_timestamp()}] {recipent} receive {self.sub_to_point} sniffscoin by anongiftsub")
        return [response1, response2]

    async def add_point_by_bit(self, username, bits, send_message):
        point_to_add = int(bits / self.bit_to_point)
        if point_to_add > 0:
            self.add_coin(username, point_to_add)
            send_message(f"@{username} ได้รับ {point_to_add} sniffscoin จากการ Bit จำนวน {bits} bit")
        else:
            send_message(f"ขอบคุณ @{username} สำหรับ {bits} บิทค้าาา")

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

    async def shooter(self, employer, target, send_message, timeout):
        payrate = 5
        shooter_timeout = random.randint(15, 60)
        exclude_target = ["sniffslive", "sirju001", "moobot", "sniffs_bot", "sniffsbot"]
        if self.environment == "dev":
            exclude_target += ["bosssoq"]
        cooldown = 1200
        command = "shooter"
        try:
            timestamp = self.command_cooldown[command]
            now = self.get_timestamp()
            diff = (now - timestamp).total_seconds()
            if diff > cooldown:
                available = True
            else:
                available = False
        except KeyError:
            available = True
        if available:
            self.command_cooldown[command] = self.get_timestamp()
            if self.db_manager.check_exist(employer):
                userdata = self.db_manager.retrieve(employer)
                if userdata["coin"] >= payrate:
                    self.add_coin(employer, -payrate)
                    if target in exclude_target:
                        await timeout(employer, shooter_timeout, f"บังอาจเหิมเกริมหรอ นั่งพักไปก่อน {shooter_timeout} วินาที")
                        await send_message(f"@{employer} บังอาจนักนะ บินไปเองซะ {shooter_timeout} วินาที")
                        print(f"[SHOT] [{self.get_timestamp()}] Shooter: {employer} hit by sniffsbot for {shooter_timeout} sec")
                    else:
                        await timeout(target, shooter_timeout, f"{employer} จ้างมือปืนสนิฟยิงปิ้วๆ {shooter_timeout} วินาที")
                        await send_message(f"@{employer} จ้างมือปืนสนิฟยิง @{target} {shooter_timeout} วินาที")
                        print(f"[SHOT] [{self.get_timestamp()}] Shooter: {employer} request sniffsbot to shoot {target} for {shooter_timeout} sec")
            else:
                if target in exclude_target:
                    await timeout(employer, int(shooter_timeout * 2), f"ไม่มีเงินจ้างแล้วยังเหิมเกริมอีก รับโทษ 2 เท่า ({shooter_timeout} วินาที)")
                    await send_message(f"@{employer} ไม่มีเงินจ้างมือปืน ยังจะเหิมเกริม บินไปซะ {int(shooter_timeout * 2)} วินาที")
                    print(f"[SHOT] [{self.get_timestamp()}] Shooter: {employer} hit by sniffsbot for {int(shooter_timeout * 2)} sec")
                else:
                    await timeout(employer, shooter_timeout, f"ไม่มีเงินจ้างมือปืนงั้นรึ โดนยิงเองซะ {shooter_timeout} วินาที")
                    await send_message(f"@{employer} ไม่มีเงินจ้างมือปืน โดนมือปืนยิงตาย {shooter_timeout} วินาที")
                    print(f"[SHOT] [{self.get_timestamp()}] Shooter: {employer} hit by sniffsbot for {shooter_timeout} sec")

    # song request system
    async def user_song_request(self, content, timestamp, username, send_message):
        cost = 1
        song_name = re.search("(?<=\\!sr ).+", content)[0]
        if song_name is not None:
            if self.db_manager.check_exist(username):
                userdata = self.db_manager.retrieve(username)
                if userdata["coin"] >= cost:
                    self.add_coin(username, -cost)
                    song_name = song_name.strip()
                    song_key = song_name.lower()
                    song_request = {
                        "songKey": song_key,
                        "songName": song_name,
                        "vote": 1,
                        "ts": datetime.timestamp(timestamp) * 1000
                    }
                    response = requests.post(self.vote_url, json=song_request)
                    if response.status_code == 200:
                        response_json = json.loads(response.content)
                        self.sorted_song_list = response_json["songlist"]
                        try:
                            self.song_playing = response_json["nowplaying"]
                        except KeyError:
                            self.song_playing = None
                        await send_message(f"@{username} ใช้ {cost} sniffscoin โหวตเพลง {response_json['songname']} คะแนนรวม {response_json['songvote']} คะแนน")
                    elif response.status_code == 404:
                        print(f"[SONG] [{self.get_timestamp()}] {song_name} Error connecting to API")
            # try:
            #     self.song_list[song_name]["vote"] -= 1
            # except KeyError:
            #     self.song_list[song_name] = {}
            #     self.song_list[song_name]["vote"] = -1
            #     self.song_list[song_name]["timestamp"] = timestamp
            # await send_message(f"@{username} โหวตเพลง {song_name} คะแนนรวม {-self.song_list[song_name]['vote']} คะแนน")

    async def now_playing(self, username, send_message):
        self.sorted_song_list, self.song_playing = self.get_song_list_api()
        if self.song_playing is not None:
            await send_message(f"@{username} สนิฟกำลังร้องเพลง {self.song_playing['songName']} น้า")

    # async def sorted_song(self):
    #     try:
    #         self.sorted_song_list = sorted(self.song_list.keys(), key=lambda song_name: (self.song_list[song_name]["vote"], self.song_list[song_name]["timestamp"]))
    #     except:
    #         self.sorted_song_list = []

    def get_song_list_api(self):
        response = requests.get(self.list_url)
        if response.status_code == 200:
            response_json = json.loads(response.content)
            try:
                sorted_song_list = response_json["songlist"]
            except KeyError:
                sorted_song_list = None
            try:
                song_playing = response_json["nowplaying"]
            except KeyError:
                song_playing = None
        else:
            sorted_song_list = None
            song_playing = None
        return sorted_song_list, song_playing

    async def get_song_list(self, send_message):
        self.sorted_song_list, self.song_playing = self.get_song_list_api()
        if self.sorted_song_list != []:
            max_song_list = min(len(self.sorted_song_list), 5)
            for i in range(0, max_song_list):
                await send_message(f"[{i + 1}] {self.sorted_song_list[i]['songName']} {self.sorted_song_list[i]['vote']} คะแนน")
                print(f"[SONG] [{self.get_timestamp()}] {i + 1} {self.sorted_song_list[i]['songName']} {self.sorted_song_list[i]['vote']} point")
        else:
            await send_message("ยังไม่มีเพลงในคิวจ้า")
        # await self.sorted_song()
        # if self.sorted_song_list != []:
        #     await send_message("List เพลงจากต้าวๆ")
        #     max_song_list = min(len(self.song_list), 5)
        #     for i in range(0, max_song_list):
        #         await send_message(f"[{i + 1}] {self.sorted_song_list[i]} {-self.song_list[self.sorted_song_list[i]]['vote']} คะแนน")
        #         print(f"[SONG] [{self.get_timestamp()}] {i + 1} {self.sorted_song_list[i]} {-self.song_list[self.sorted_song_list[i]]['vote']} point")
        # else:
        #     await send_message("ยังไม่มีเพลงในคิวจ้า")

    async def select_song(self, song_id, send_message):
        song_id = int(song_id)
        try:
            # if we have front end, we need to fetch new list
            # self.sorted_song_list, self.song_playing = self.get_song_list_api()
            song_select = self.sorted_song_list[song_id - 1]["songKey"]
            response = requests.post(self.select_url, json={"songKey": song_select})
            if response.status_code == 200:
                response_json = json.loads(response.content)
                self.sorted_song_list = response_json["songlist"]
                self.song_playing = response_json["nowplaying"]
                await send_message(f"สนิฟเลือกเพลง {self.song_playing['songName']}")
                print(f"[SONG] [{self.get_timestamp()}] Sniffs choose {self.song_playing['songName']} Delete this song from list")
            elif response.status_code == 404:
                response_json = json.loads(response.content)
                self.sorted_song_list = response_json["songlist"]
                try:
                    self.song_playing = response_json["nowplaying"]
                except KeyError:
                    self.song_playing = None
                await send_message("ไม่มีเพลงนี้น้า")
                print(f"[SONG] [{self.get_timestamp()}] No song in list // error from api")
        except IndexError:
            await send_message("ไม่มีเพลงนี้น้า")
            print(f"[SONG] [{self.get_timestamp()}] No song in list // out of range")
        # try:
        #     self.song_playing = self.sorted_song_list[song_id - 1]
        #     try:
        #         del self.song_list[self.song_playing]
        #     except KeyError:
        #         print(f"[SONG] [{self.get_timestamp()}] Failed to delete song {self.song_playing} from list")
        #     self.sorted_song_list = []
        #     await send_message(f"สนิฟเลือกเพลง {self.song_playing}")
        #     print(f"[SONG] [{self.get_timestamp()}] Sniffs choose {self.song_playing} Delete this song from list")
        # except IndexError:
        #     await send_message("ไม่มีเพลงนี้น้า")
        #     print(f"[SONG] [{self.get_timestamp()}] No song in list")

    async def delete_songlist(self, send_message):
        response = requests.post(self.clear_url, json={"confirm": True})
        if response.status_code == 200:
            self.sorted_song_list = []
            try:
                response_json = json.loads(response.content)
                self.song_playing = response_json["nowplaying"]
            except KeyError:
                self.song_playing = None
            await send_message(f"ล้าง List เพลงให้แล้วต้าวสนิฟ")
        elif response.status_code == 404:
            print(f"[SONG] [{self.get_timestamp()}] Error deleting from api")
        # self.song_playing = ""
        # self.song_list = {}
        # self.sorted_song_list = []

    async def delete_song(self, song_id, send_message):
        song_id = int(song_id)
        try:
            # if we have front end, we need to fetch new list
            # self.sorted_song_list, self.song_playing = self.get_song_list_api()
            song_select = self.sorted_song_list[song_id - 1]["songKey"]
            response = requests.post(self.delete_url, json={"songKey": song_select})
            if response.status_code == 200:
                response_json = json.loads(response.content)
                self.sorted_song_list = response_json["songlist"]
                try:
                    self.song_playing = response_json["nowplaying"]
                except KeyError:
                    self.song_playing = None
                await send_message(f"สนิฟลบเพลง {song_select}")
                await self.get_song_list(send_message)
                print(f"[SONG] [{self.get_timestamp()}] Sniffs delete {song_select} from list")
            elif response.status_code == 404:
                response_json = json.loads(response.content)
                try:
                    self.sorted_song_list = response_json["songlist"]
                    self.song_playing = response_json["nowplaying"]
                except KeyError:
                    self.sorted_song_list = []
                    self.song_playing = None
                await send_message("ไม่มีเพลงนี้น้า")
                print(f"[SONG] [{self.get_timestamp()}] No song in list // error from api")
        except IndexError:
            await send_message("ไม่มีเพลงนี้น้า")
            print(f"[SONG] [{self.get_timestamp()}] No song in list // out of range")
        # if self.sorted_song_list != []:
        #     try:
        #         del_song = self.sorted_song_list[song_id - 1]
        #         del self.song_list[del_song]
        #         await send_message(f"ลบเพลง {del_song} เรียบร้อยแล้วจ้า")
        #         await self.get_song_list(send_message)
        #     except:
        #         print(f"[SONG] [{self.get_timestamp()}] Failed to delete song {song_id} from list")

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

    # lotto system
    async def buy_lotto(self, username, lotto, send_message):
        lotto_cost = 5
        if re.match(r"[0-9]{4}", lotto) is not None:
            if self.db_manager.check_exist(username):
                userstat = self.db_manager.retrieve(username)
                if userstat["coin"] >= lotto_cost:
                    lotto_int = int(lotto)
                    if self.player_lotto_list != []:
                        for player_lotto in self.player_lotto_list:
                            if lotto_int in player_lotto:
                                await send_message(f"@{username} ไม่สามารถซื้อเลขซ้ำได้")
                                print(f"[LOTO] [{self.get_timestamp()}] {username} Duplicate Lotto: {lotto}")
                                return
                    self.add_coin(username, -lotto_cost)
                    self.player_lotto_list += [[username, lotto_int]]
                    await send_message(f"@{username} ซื้อ SniffsLotto หมายเลข {lotto} สำเร็จ")
                    print(f"[LOTO] [{self.get_timestamp()}] {username} buy {lotto} successfully")
                else:
                    await send_message(f"@{username} ไม่มีเงินแล้วยังจะซื้ออีก")
                    print(f"[LOTO] [{self.get_timestamp()}] {username} coin insufficient")

    async def draw_lotto(self, send_message):
        print(f"[LOTO] All player list : {self.player_lotto_list}")
        lotto_winners = self.lotto.check_winner(self.player_lotto_list)
        # lotto_winners = [["bosssoq", 1110], ["ponny", 110], ["franess", 10]]
        count_winners = len(lotto_winners)
        payout = 0
        for winner in lotto_winners:
            self.add_coin(winner[0], int(winner[1]))
            payout += int(winner[1])
        await send_message(f"ประกาศผลรางวัล SniffsLotto แล้ว มีผู้ชนะทั้งหมด {count_winners} คน ได้รับรางวัลรวม {payout} sniffscoin")
        print(f"[LOTO] [{self.get_timestamp()}] LOTTO winners: {count_winners} users | payout: {payout} coin")
