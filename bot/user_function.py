import asyncio
from datetime import datetime


class UserFunction:
    def __init__(self):
        self.watchtime_session = {}

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
    
    def get_channel_live_on(self, channel_live, channel_live_on):
        if channel_live: self.channel_live, self.channel_live_on = channel_live, channel_live_on

    async def update_user_watchtime(self):
        while self.channel_live:
            for user_stat in self.watchtime_session.values():
                now = datetime.utcnow()
                if user_stat["status"] == "join":
                    user_stat["watchtime_session"] = (now - max(user_stat["join_on"], self.channel_live_on)).total_seconds()
                else:
                    user_stat["watchtime_session"] = (user_stat["part_on"] - max(user_stat["join_on"], self.channel_live_on)).total_seconds()
            await asyncio.sleep(1)
        while True:
            await asyncio.sleep(60)
    
    def get_user_watchtime(self, username):
        try:
            watchtime = self.watchtime_session[username]["watchtime_session"]
        except KeyError:
            watchtime = 0
        return watchtime
