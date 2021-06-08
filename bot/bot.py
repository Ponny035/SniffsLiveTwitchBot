import asyncio
from datetime import datetime
import re

from twitchio.client import Client
from twitchio.ext import commands


class TwitchBot(commands.Bot,):
    def __init__(self,environment,userfunction):

        self.environment = environment
        self.channel_live = False
        self.channel_live_on = ""
        self.market_open = False
        self.user_function = userfunction

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
        await self.greeting_sniffs()

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
        await self.get_channel_status()
        if self.channel_live:
            if user.name.lower() == "armzi": await self.channel.send(f"พ่อ @{user.name} มาแล้วววววว ไกปู")
        if user.name.lower() not in [self.NICK, self.NICK+"\r"]: self.user_function.user_join(user.name.lower(), datetime.utcnow())

    async def event_part(self, user):  # get user part notice TODO (1.1.2): write to dict
        await self.get_channel_status()
        if self.channel_live:
            if user.name.lower() == "armzi": await self.channel.send(f"พ่อ @{user.name} ไปแล้ว บะบายคร้าบบบบ")
        if user.name.lower() not in [self.NICK, self.NICK+"\r"]: self.user_function.user_part(user.name.lower(), datetime.utcnow())

    # TODO (1.1): write watchtime to db after live end
    # TODO (1.1): asynnio every xx minutes to increase xx points (diff watchtime_session and watchtime_redeem => mod xx minute => add point => write watchtime_redeem = xx minute)

    async def event_usernotice_subscription(self, metadata):  # get sub metadata TODO (2.1): implement function
        print("New Sub")
        print(metadata)

    async def get_users_list(self):
        users = await self.get_chatters(self.CHANNELS)
        return users.all
    
    async def get_channel_status(self):
        channel_status = await self.twitch_api.get_stream(self.CHANNELS)
        if channel_status is not None:
            self.channel_live = (channel_status["type"] == "live")
            self.channel_live_on = datetime.strptime(channel_status["started_at"], "%Y-%m-%dT%H:%M:%SZ")
        else: self.channel_live = False

    async def greeting_sniffs(self):
        if self.channel_live:
            self.user_function.get_channel_live_on(self.channel_live, self.channel_live_on)
            await self.user_function.update_user_watchtime()
            print(f"[{datetime.utcnow()}] {self.CHANNELS} is live.")
            while self.channel_live:
                await self.get_channel_status()
                if not self.channel_live:
                    await self.channel.send(f"@{self.CHANNELS} ไปแล้ววววว")
                    await self.greeting_sniffs()
                await asyncio.sleep(5)
        else:
            self.user_function.get_channel_live_on(self.channel_live, self.channel_live_on)
            print(f"[{datetime.utcnow()}] {self.CHANNELS} is offline.")
            while not self.channel_live:
                await self.get_channel_status()
                if self.channel_live:
                    await self.channel.send(f"@{self.CHANNELS} มาแล้ววววว")
                    await self.greeting_sniffs()
                await asyncio.sleep(5)

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
            await ctx.send(f"@{ctx.author.name.lower()} มี {coin} sniffscoin")
    
    @commands.command(name="watchtime")
    async def check_user_watchtime(self, ctx):
        watchtime = self.user_function.get_user_watchtime(ctx.author.name.lower())
        watchtime_min = str(int(watchtime / 60))
        watchtime_sec = str(int(watchtime % 60))
        print(f"[{datetime.utcnow()}] Watchtime checked by {ctx.author.name.lower()}: {watchtime_min} mins {watchtime_sec} secs")
        await ctx.send(f"@{ctx.author.name.lower()} ดูไลฟ์มาแล้ว {watchtime_min} นาที {watchtime_sec} วินาที")
    
    @commands.command(name="uptime")#getting live stream time
    async def uptime_command(self, ctx):
        if not self.channel_live: return await ctx.send("ยังไม่ถึงเวลาไลฟน้าาาา")
        uptime = (datetime.utcnow() - self.channel_live_on).total_seconds()
        uptime_hour = 0
        uptime_min = 0
        uptime_sec = int(uptime % 60)
        if uptime >= 60: uptime_min = int(uptime / 60)
        if uptime_min >= 60: uptime_hour = int(uptime_min / 60); uptime_min = int(uptime_min % 60)
        print(f"[{datetime.utcnow()}] Uptime checked by {ctx.author.name.lower()}: {uptime_hour} hours {uptime_min} mins {uptime_sec} secs")
        if uptime_hour > 0:
            await ctx.send(f"สนิฟไลฟ์มาแล้ว {uptime_hour} ชั่วโมง {uptime_min} นาที {uptime_sec} วินาที น้าาา")
        elif uptime_min > 0:
            await ctx.send(f"สนิฟไลฟ์มาแล้ว {uptime_min} นาที {uptime_sec} วินาที น้าาา")
        else:
            await ctx.send(f"สนิฟไลฟ์มาแล้ว {uptime_sec} วินาที น้าาา")

    @commands.command(name="discord")
    async def discord_command(self, ctx):
        await ctx.send("https://discord.gg/Q3AMaHQEGU")#this is a temporary link waiting for permanent link

    @commands.command(name="facebook")
    async def facebook_command(self, ctx):
        await ctx.send("https://www.facebook.com/sniffslive/")#waiting for permanent link
