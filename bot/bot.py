import asyncio
from datetime import datetime
import random
import re

from twitchio.client import Client
from twitchio.ext import commands


class TwitchBot(commands.Bot,):
    def __init__(self,environment,dryrun,userfunction,automod):

        self.environment = environment
        self.dryrun = dryrun
        self.automod = automod  # need to fixed
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

    async def send_message(self, msg):
        if self.dryrun != "msgoff":
            await self.channel.send(msg)
        else: print(f"[INFO] Dry run mode is on \"{msg}\" not sent")

    async def event_ready(self):
        print("Bot joining channel.")
        self.channel = self.get_channel(self.CHANNELS)
        await self.get_channel_status()
        await self.send_message(self.NICK + " is joined the channels.")
        print("Joined")
        await self.greeting_sniffs()

    async def event_message(self, ctx):
        if ctx.author.name.lower() != self.NICK:
            print(f"[{ctx.timestamp}] {ctx.author.name.lower()}: {ctx.content}")

            # catch bit event TODO (2.2): every xxx bit add xxx point
            try:
                self.bit = re.search(r"(?<=bits=)([0-9]+)", ctx.raw_data)[0]
                print(f"[{ctx.timestamp}] {ctx.author.name.lower()}: {self.bit} bits")
                await self.send_message(f"ขอบคุณ @{ctx.author.name.lower()} สำหรับ {self.bit} บิทคร้าบ")
            except:
                self.bit = 0

            await self.handle_commands(ctx)

    async def event_join(self, user):  # get user join notice TODO (1.1.1): write to dict
        await self.get_channel_status()
        if self.channel_live:
            if user.name.lower() == "armzi": await self.send_message(f"พ่อ @{user.name} มาแล้วววววว ไกปู")
        if user.name.lower() not in [self.NICK, self.NICK+"\r"]: self.user_function.user_join(user.name.lower(), datetime.utcnow())

    async def event_part(self, user):  # get user part notice TODO (1.1.2): write to dict
        await self.get_channel_status()
        if self.channel_live:
            if user.name.lower() == "armzi": await self.send_message(f"พ่อ @{user.name} ไปแล้ว บะบายคร้าบบบบ")
        if user.name.lower() not in [self.NICK, self.NICK+"\r"]: self.user_function.user_part(user.name.lower(), datetime.utcnow())

    # TODO (1.1): write watchtime to db after live end
    # TODO (1.1): asynnio every xx minutes to increase xx points (diff watchtime_session and watchtime_redeem => mod xx minute => add point => write watchtime_redeem = xx minute)

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
            usernames = await self.get_users_list()
            for username in usernames: self.user_function.user_join(username,self.channel_live_on)
            await self.user_function.get_channel_live_on(self.channel_live, self.channel_live_on)
            asyncio.create_task(self.user_function.update_user_watchtime())
            asyncio.create_task(self.user_function.add_point_by_watchtime())
            print(f"[{datetime.utcnow()}] {self.CHANNELS} is live.")
            while self.channel_live:
                await self.get_channel_status()
                if not self.channel_live:
                    await self.send_message(f"@{self.CHANNELS} ไปแล้ววววว")
                    await self.greeting_sniffs()
                await asyncio.sleep(5)
        else:
            await self.user_function.get_channel_live_on(self.channel_live, self.channel_live_on)
            print(f"[{datetime.utcnow()}] {self.CHANNELS} is offline.")
            while not self.channel_live:
                await self.get_channel_status()
                if self.channel_live:
                    await self.send_message(f"@{self.CHANNELS} มาแล้ววววว")
                    await self.greeting_sniffs()
                await asyncio.sleep(5)

    @commands.command(name="payday")
    async def give_coin_allusers(self, ctx):
        if ctx.author.name.lower() == self.CHANNELS or (self.environment == "dev" and ctx.author.name.lower() == "bosssoq"):
            commands_split = ctx.content.split()
            try:
                coin = int(commands_split[1])
                if coin < 0: coin = 0
            except:
                coin = 1
            users = await self.get_users_list()
            # TODO: add sniffscoin to DB
            for username in users:
                self.user_function.add_coin(username.lower(), coin)
            print(f"[{datetime.utcnow()}] All {len(users)} users receive {coin} sniffscoin")
            await self.send_message(f"ผู้ชมทั้งหมด {len(users)} คน ได้รับ {coin} sniffscoin")

    @commands.command(name="give")
    async def give_coin_user(self, ctx):
        if ctx.author.name.lower() == self.CHANNELS or (self.environment == "dev" and ctx.author.name.lower() == "bosssoq"):
            commands_split = ctx.content.split()
            try:
                username = commands_split[1]
            except:
                username = ""
            try:
                coin = int(commands_split[2])
                if coin < 0: coin = 0
            except:
                coin = 1
            if username != "":
                self.user_function.add_coin(username, coin)
            print(f"[{datetime.utcnow()}] User: {username} receive {coin} sniffscoin")
            await self.send_message(f"@{username} ได้รับ {coin} sniffscoin")

    @commands.command(name="coin")
    async def check_coin(self, ctx):
        if self.market_open or ctx.author.is_subscriber == 1 or ctx.author.is_mod or ctx.author.name.lower() == self.CHANNELS:
            coin = self.user_function.get_coin(ctx.author.name.lower())
            print(f"[{datetime.utcnow()}] Coin checked by {ctx.author.name.lower()}: {coin} sniffscoin")
            await self.send_message(f"@{ctx.author.name.lower()} มี {coin} sniffscoin")
    
    @commands.command(name="watchtime")
    async def check_user_watchtime(self, ctx):
        watchtime = self.user_function.get_user_watchtime(ctx.author.name.lower())
        watchtime_hour = 0
        watchtime_min = 0
        watchtime_sec = int(watchtime % 60)
        if watchtime >= 60: watchtime_min = int(watchtime / 60)
        if watchtime_min >= 60: watchtime_hour = int(watchtime_min / 60); watchtime_min = int(watchtime_min % 60)
        print(f"[{datetime.utcnow()}] Watchtime checked by {ctx.author.name.lower()}: {watchtime_hour} hours {watchtime_min} mins {watchtime_sec} secs")
        if watchtime_hour > 0:
            await self.send_message(f"@{ctx.author.name.lower()} ดูไลฟ์มาแล้ว {watchtime_hour} ชั่วโมง {watchtime_min} นาที {watchtime_sec} วินาที")
        elif watchtime_min > 0:
            await self.send_message(f"@{ctx.author.name.lower()} ดูไลฟ์มาแล้ว {watchtime_min} นาที {watchtime_sec} วินาที")
        else:
            await self.send_message(f"@{ctx.author.name.lower()} ดูไลฟ์มาแล้ว {watchtime_sec} วินาที")
    
    @commands.command(name="uptime")#getting live stream time
    async def uptime_command(self, ctx):
        if not self.channel_live: return await self.send_message("ยังไม่ถึงเวลาไลฟน้าาาา")
        uptime = (datetime.utcnow() - self.channel_live_on).total_seconds()
        uptime_hour = 0
        uptime_min = 0
        uptime_sec = int(uptime % 60)
        if uptime >= 60: uptime_min = int(uptime / 60)
        if uptime_min >= 60: uptime_hour = int(uptime_min / 60); uptime_min = int(uptime_min % 60)
        print(f"[{datetime.utcnow()}] Uptime checked by {ctx.author.name.lower()}: {uptime_hour} hours {uptime_min} mins {uptime_sec} secs")
        if uptime_hour > 0:
            await self.send_message(f"สนิฟไลฟ์มาแล้ว {uptime_hour} ชั่วโมง {uptime_min} นาที {uptime_sec} วินาที น้าาา")
        elif uptime_min > 0:
            await self.send_message(f"สนิฟไลฟ์มาแล้ว {uptime_min} นาที {uptime_sec} วินาที น้าาา")
        else:
            await self.send_message(f"สนิฟไลฟ์มาแล้ว {uptime_sec} วินาที น้าาา")

    @commands.command(name="discord")
    async def discord_command(self, ctx):
        await self.send_message("https://discord.gg/Q3AMaHQEGU")#this is a temporary link waiting for permanent link

    @commands.command(name="facebook")
    async def facebook_command(self, ctx):
        await self.send_message("https://www.facebook.com/sniffslive/")#waiting for permanent link
    
    @commands.command(name="thanos")
    async def thanos(self, ctx):
        thanos_timeout = 180
        casualtie = 0
        print("Thanos: Do you call me?")
        userslist = await self.get_users_list()
        userslist = [username for username in userslist if username not in [self.NICK, self.CHANNELS]]
        print(userslist)
        if ctx.author.name.lower() == self.CHANNELS or (self.environment == "dev" and ctx.author.name.lower() == "bosssoq"):
            number_user = int(len(userslist) / 2)
            random.shuffle(userslist)
            poor_users = userslist[:number_user]
            for username in poor_users:
                if (bool(random.getrandbits(1))):
                    casualtie += 1
                    print(f"[THANOS] [{datetime.utcnow()}] Timeout: {username}")
                    await self.channel.timeout(username, thanos_timeout, "โดนทานอสดีดนิ้ว")
                    await asyncio.sleep(0.5)
            
        await self.channel.send(f"ใช้งาน Thanos Mode มี {casualtie} คนในแชทหายตัวไป....")
