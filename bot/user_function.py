import asyncio
from datetime import datetime
from twitchio.client import Client


class UserFunction:
    def __init__(self, channels):
        self.CHANNELS = channels
        self.channel_live = False
        self.watchtime_session = {}
        self.watchtime_to_point = 1  # 1 min to 1 point
        self.user_point = {}
        self.twitch_api = Client(
            client_id="wt9nmvcq4oszo9k4qpswvl7htigg08",
            client_secret="5c2ihtk3viinbrpnvlooys8c56w56f"
        )
        # asyncio.ensure_future(self.get_channel_status(self.callFunc))
        # asyncio.get_event_loop().run_forever()

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

    async def get_channel_status(self, callback1, callback2):
        success_callback = [0, 0]
        while True:
            if self.channel_live:
                channel_status = await self.twitch_api.get_stream(self.CHANNELS)
                if channel_status is None and success_callback[0] == 0:
                    self.channel_live = False
                    success_callback = [1, 1]
                    await callback1()
                    await asyncio.sleep(10)
                    success_callback[1] = 0
            elif not self.channel_live:
                channel_status = await self.twitch_api.get_stream(self.CHANNELS)
                if channel_status is not None and success_callback[1] == 0:
                    self.channel_live = (channel_status["type"] == "live")
                    self.channel_live_on = datetime.strptime(channel_status["started_at"], "%Y-%m-%dT%H:%M:%SZ")
                    success_callback = [1, 1]
                    await callback2(self.channel_live_on)
                    await asyncio.sleep(10)
                    success_callback[0] = 0

    async def update_user_watchtime(self, starttime):
        if self.channel_live:
            for user_stat in self.watchtime_session.values():
                now = datetime.utcnow()
                if user_stat["status"] == "join":
                    user_stat["watchtime_session"] = (now - max(user_stat["join_on"], starttime)).total_seconds()
                else:
                    user_stat["watchtime_session"] = (user_stat["part_on"] - max(user_stat["join_on"], starttime)).total_seconds()
            await asyncio.sleep(1)
            asyncio.create_task(self.update_user_watchtime(starttime))
        elif self.watchtime_session != {}:
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
            print(self.user_point)
            await asyncio.sleep(self.watchtime_to_point * 60)
            asyncio.create_task(self.add_point_by_watchtime())
        else:
            print(self.user_point)

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
        # self.bot_cmd.send_message("test")
        return coin
