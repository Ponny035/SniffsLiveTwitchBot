import asyncio
from datetime import datetime


class UserFunction:
    def __init__(self):
        self.watchtime_session = {}
        self.user_point = {}
        self.command_cooldown = {}
        self.channel_live = False
        self.watchtime_to_point = 1  # 1 min to 1 point
        self.cooldown = 20

    def get_timestamp(self):
        return datetime.utcnow().replace(microsecond=0)

    async def activate_point_system(self, live, starttime=None):
        self.channel_live = live
        if starttime is not None:
            self.channel_live_on = starttime
            await self.add_point_by_watchtime()
        else:
            self.channel_live_on = None

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
            print("write watchtime to DB")
            print(f"[_LOG] {self.watchtime_session}")
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
        print("write point to DB")
        print(f"[_LOG] {self.user_point}")

    def get_user_watchtime(self, username):
        self.update_user_watchtime()
        try:
            watchtime = self.watchtime_session[username]["watchtime_session"]
            # TODO: fetch watchtime from DB
        except KeyError:
            watchtime = 0
        return watchtime

    def add_coin(self, username, coin):
        try:
            self.user_point[username] += coin
        except KeyError:
            self.user_point[username] = coin

    def get_coin(self, username):
        try:
            coin = self.user_point[username]
        except KeyError:
            coin = 0
        return coin

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
                return False
        except KeyError:
            return True
