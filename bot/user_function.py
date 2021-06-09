import asyncio
from datetime import datetime


class UserFunction:
    def __init__(self):
        self.watchtime_session = {}
        self.watchtime_to_point = 10  # 1 min to 1 point
        self.user_point = {}

    def user_join(self, username, timestamp):
        try:
            if self.watchtime_session[username]["status"] != "join":
                self.watchtime_session[username]["status"] = "join"
                self.watchtime_session[username]["join_on"] = timestamp
        except KeyError:
            self.watchtime_session[username] = {}
            self.watchtime_session[username]["status"] = "join"
            self.watchtime_session[username]["join_on"] = timestamp
    
    def user_part(self, username, timestamp):
        try:
            if self.watchtime_session[username]["status"] != "part":
                self.watchtime_session[username]["status"] = "part"
                self.watchtime_session[username]["part_on"] = timestamp
        except KeyError:
            self.watchtime_session[username] = {}
            self.watchtime_session[username]["status"] = "part"
            self.watchtime_session[username]["part_on"] = timestamp
        # TODO: write watchtime to DB when user part
    
    async def get_channel_live_on(self, channel_live, channel_live_on):
        if channel_live:
            self.channel_live, self.channel_live_on = channel_live, channel_live_on
        else:
            self.channel_live = False
            self.channel_live_on = ""

    async def update_user_watchtime(self):
        while self.channel_live:
            for user_stat in self.watchtime_session.values():
                now = datetime.utcnow()
                if user_stat["status"] == "join":
                    user_stat["watchtime_session"] = (now - max(user_stat["join_on"], self.channel_live_on)).total_seconds()
                else:
                    user_stat["watchtime_session"] = (user_stat["part_on"] - max(user_stat["join_on"], self.channel_live_on)).total_seconds()
            await asyncio.sleep(1)
        if self.watchtime_session != {}:
            # TODO: write watchtime to DB when live end
            print("write watchtime to DB")
            print(self.watchtime_session)
            self.watchtime_session = {}
    
    async def add_point_by_watchtime(self):
        if self.channel_live:
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
                print(f"User: {username} ได้รับ {point_to_add} sniffscoin จากการดูไลฟ์ครบ {str(int((point_to_add * watchtime_to_point) / 60))} นาที")
            await asyncio.sleep(watchtime_to_point * 60)
        print(self.user_point)
        asyncio.create_task(self.add_point_by_watchtime())
    
    def get_user_watchtime(self, username):
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
