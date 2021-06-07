import asyncio
from datetime import datetime
import re

from twitchio.client import Client
from twitchio.ext import commands


class TwitchBot(commands.Bot,):
    def __init__(self,environment):

        self.environment = environment
        self.market_open = False
        self.CHANNEL_LIVE = False

        try:
            if(environment == "dev"):
                print("Init bot on DEVELOPMENT environment")
                with open ("./data/dev_env", "r", encoding="utf-8") as f:
                    IRC_TOKEN, API_TOKEN, self.NICK, self.CHANNELS = (l.strip() for l in f.readlines())
                super().__init__(
                    irc_token = IRC_TOKEN,
                    api_token = API_TOKEN,
                    client_id = "uej04g8lskt59abzr5o50lt67k9kmi",
                    prefix = "!", 
                    nick = self.NICK,
                    initial_channels = [self.CHANNELS],
                )
                self.twitch_api = Client(
                    client_id = "wt9nmvcq4oszo9k4qpswvl7htigg08",
                    client_secret = "5c2ihtk3viinbrpnvlooys8c56w56f"
                )

            elif(environment == "prod"):
                print("Init bot on PRODUCTION environment")
                with open ("./data/env", "r", encoding="utf-8") as f:
                    IRC_TOKEN, API_TOKEN, self.NICK, self.CHANNELS = (l.strip() for l in f.readlines())

                super().__init__(
                    irc_token = IRC_TOKEN,
                    api_token = API_TOKEN,
                    client_id = "uej04g8lskt59abzr5o50lt67k9kmi",
                    prefix = "!", 
                    nick = self.NICK,
                    initial_channels = [self.CHANNELS],
                )
                self.twitch_api = Client(
                    client_id = "wt9nmvcq4oszo9k4qpswvl7htigg08",
                    client_secret = "5c2ihtk3viinbrpnvlooys8c56w56f"
                )
            print("Done")
        except (FileNotFoundError):
            msg = "Sorry you DON'T HAVE PERMISSION to run on production."
            raise TypeError(msg)

        except Exception as e:
            msg = "start bot fail with error \"" + str(e) + "\" try check your ... first "
            raise TypeError(msg)
            
    async def event_ready(self):
        print("Bot joining channel.")
        self.channel = self.get_channel(self.CHANNELS)
        await self.get_channel_status()
        # await self.channel.send(self.NICK + " is joined the channels.")
        print("Joined")

    async def event_message(self, ctx):
        if ctx.author.name.lower() != self.NICK:
            print(f"[{ctx.timestamp}] {ctx.author.name.lower()}: {ctx.content}")

            # catch bit event TODO (2.2): every xxx bit add xxx point
            try:
                self.bit = re.search(r"(?<=bits=)([0-9]+)", ctx.raw_data)[0]
                print(f"[{ctx.timestamp}] {ctx.author.name.lower()}: {self.bit} bits")
                await self.channel.send(f"ขอบคุณ @{ctx.author.name.lower()} สำหรับ {self.bit} บิทคร้าบ")
            except:
                self.bit = 0

            await self.handle_commands(ctx)

    async def event_join(self, user):  # get user join notice TODO (1.1.1): write to dict
        if user.name.lower() == "armzi":
            await self.channel.send(f"พ่อ @{user.name} มาแล้วววววว ไกปู")
        print(f'[{datetime.utcnow()}] User Join: {user.name}')

    async def event_part(self, user):  # get user part notice TODO (1.1.2): write to dict
        if user.name.lower() == "armzi":
            await self.channel.send(f"พ่อ @{user.name} ไปแล้ว บะบายคร้าบบบบ")
        print(f'[{datetime.utcnow()}] User Part: {user.name}')

    # TODO (1.1): asyncio every second to update watchtime in dict key [username, watchtime_session, watchtime_redeem]
    # TODO (1.1): asyncio every minute to write watchtime to db {from watchtime_session add to watchtime in db}
    # TODO (1.1): asynnio every xx minutes to increase xx points (diff watchtime_session and watchtime_redeem => mod xx minute => add point => write watchtime_redeem = xx minute)

    async def event_usernotice_subscription(self, metadata):  # get sub metadata TODO (2.1): implement function
        print("New Sub")
        print(metadata)

    async def get_users_list(self):
        users = await self.get_chatters(self.CHANNELS)
        return users.all
    
    async def get_channel_status(self):
        while not self.CHANNEL_LIVE:
            channel_status = await self.twitch_api.get_stream(self.CHANNELS)
            try:
                self.CHANNEL_LIVE = (channel_status["type"] == "live")
            except KeyError:
                self.CHANNEL_LIVE = False
        print("LIVE")
        # await self.channel.send(f"@{self.CHANNELS} มาแล้ววววว")

    @commands.command(name="payday")
    async def give_coin_allusers(self, ctx):
        if ctx.author.name.lower() == self.CHANNELS or (self.environment == "dev" and ctx.author.name.lower() == "bosssoq"):
            commands_split = ctx.content.split()
            try:
                coin = int(commands_split[1])
            except:
                coin = 1
            users = await self.get_users_list()
            # TODO: add sniffscoin to DB
            print(f"[{datetime.utcnow()}] All {len(users)} users receive {coin} sniffscoin")
            await ctx.send(f"ผู้ชมทั้งหมด {len(users)} คน ได้รับ {coin} sniffscoin")

    @commands.command(name="coin")
    async def check_coin(self, ctx):
        if self.market_open or ctx.author.is_subscriber == 1 or ctx.author.is_mod or ctx.author.name.lower() == self.CHANNELS:
            user_stat = {  # dummy response
                "username": ctx.author.name.lower(),
                "coin": 1,
            }
            if user_stat: coin = user_stat["coin"]
            else: coin = 0
            print(f"[{datetime.utcnow()}] Coin checked by {ctx.author.name.lower()}: {coin} sniffscoin")
            await self.channel.send(f"@{ctx.author.name.lower()} มี {coin} sniffscoin")
