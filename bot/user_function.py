import asyncio
from datetime import datetime
import random


class UserFunction:
    def __init__(self, environment):
        self.environment = environment
        self.watchtime_session = {}
        self.user_point = {}
        self.command_cooldown = {}
        self.channel_live = False
        self.sub_to_point = 10  # 1 sub for 10 point
        self.bit_to_point = 50  # 50 bits for 1 point
        self.watchtime_to_point = 10  # 10 min to 1 point
        self.cooldown = 20

    def get_timestamp(self):
        return datetime.utcnow().replace(microsecond=0)

    def sec_to_hms(self, time):
        hour, min, sec = 0, 0, 0
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
    def add_coin(self, username, coin):
        try:
            self.user_point[username] += coin
        except KeyError:
            self.user_point[username] = coin
        print(f"[COIN] [{self.get_timestamp()}] User: {username} receive(deduct) {coin} sniffscoin")

    def get_coin(self, username):
        try:
            coin = self.user_point[username]
        except KeyError:
            coin = 0
        print(f"[COIN] [{self.get_timestamp()}] Coin checked by {username}: {coin} sniffscoin")
        return coin

    def payday(self, usernames, coin):
        for username in usernames:
            self.add_coin(username.lower(), coin)
        print(f"[COIN] [{self.get_timestamp()}] All {len(usernames)} users receive {coin} sniffscoin")

    def subscription_payout(self, username, usernames):
        self.add_coin(username, self.sub_to_point)
        self.payday(usernames, 1)
        response1 = f"ยินดีต้อนรับ @{username} มาเป็นต้าวๆของสนิฟ"
        response2 = f"@{username} ได้รับ {self.sub_to_point} sniffscoin และผู้ชมทั้งหมด {len(usernames)} คนได้รับ 1 sniffscoin"
        print(f"[COIN] [{self.get_timestamp()}] {username} receive {self.sub_to_point} sniffscoin by sub")
        return [response1, response2]

    def gift_subscription_payout(self, username, recipent, usernames):
        self.add_coin(username, self.sub_to_point)
        self.add_coin(recipent, self.sub_to_point)
        self.payday(usernames, 1)
        response1 = f"@{username} ได้รับ {self.sub_to_point} sniffscoin จากการ Gift ให้ {recipent}"
        response2 = f"@{recipent} ได้รับ {self.sub_to_point} sniffscoin และผู้ชมทั้งหมด {len(usernames)} คนได้รับ 1 sniffscoin"
        print(f"[COIN] [{self.get_timestamp()}] {username} receive {self.sub_to_point} sniffscoin by giftsub to {recipent}")
        return [response1, response2]

    def giftmystery_subscription_payout(self, username, gift_count, usernames):
        self.add_coin(username, self.sub_to_point * gift_count)
        self.payday(usernames, 1)
        response1 = f"@{username} ได้รับ {self.sub_to_point * gift_count} sniffscoin จากการ Gift ให้สมาชิก {gift_count} คน"
        print(f"[COIN] [{self.get_timestamp()}] {username} receive {self.sub_to_point * gift_count} sniffscoin by giftmysterysub")
        return [response1]

    def anongift_subscription_payout(self, recipent, usernames):
        self.add_coin(recipent, self.sub_to_point)
        self.payday(usernames, 1)
        response1 = f"ขอบคุณ Gift จากผู้ไม่ประสงค์ออกนามค่าา"
        response2 = f"@{recipent} ได้รับ {self.sub_to_point} sniffscoin และผู้ชมทั้งหมด {len(usernames)} คนได้รับ 1 sniffscoin"
        print(f"[COIN] [{self.get_timestamp()}] {recipent} receive {self.sub_to_point} sniffscoin by anongiftsub")
        return [response1, response2]

    async def add_point_by_bit(self, username, bits):
        response = ""
        point_to_add = int(bits / self.bit_to_point)
        print(point_to_add)
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
            print(f"[HELL] [{self.get_timestamp()}] Timeout: {username}")
            await timeout(username, callhell_timeout, "โดนสนิฟดีดนิ้ว")
            await asyncio.sleep(0.5)
        data = {
            "casualtie": casualtie,
            "poor_users": poor_users
        }
        return data

    # cooldown related system
    def set_cooldown(self, username, command):
        now = self.get_timestamp()
        try:
            self.command_cooldown[username][command] = now
        except KeyError:
            self.command_cooldown[username] = {}
            self.command_cooldown[username][command] = now

    def check_cooldown(self, username, command):
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
