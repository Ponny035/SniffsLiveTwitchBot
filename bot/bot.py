import asyncio
from datetime import datetime
import random

import nest_asyncio
from twitchio.ext import commands


class TwitchBot(commands.Bot,):
    def __init__(self, environment, dryrun, userfunction, automod, event_trigger):

        self.environment = environment
        self.dryrun = dryrun
        self.automod = automod  # need to fixed
        self.channel_live = False
        self.channel_live_on = ""
        self.user_function = userfunction()
        self.market_open = False
        nest_asyncio.apply()

        try:
            if(environment == "dev"):
                print("Init bot on DEVELOPMENT environment")
                with open("./data/dev_env", "r", encoding="utf-8") as f:
                    IRC_TOKEN, API_TOKEN, self.NICK, self.CHANNELS = (l.strip() for l in f.readlines())
                super().__init__(
                    irc_token=IRC_TOKEN,
                    api_token=API_TOKEN,
                    client_id="uej04g8lskt59abzr5o50lt67k9kmi",
                    prefix="!",
                    nick=self.NICK,
                    initial_channels=[self.CHANNELS],
                )

            elif(environment == "prod"):
                print("Init bot on PRODUCTION environment")
                with open("./data/env", "r", encoding="utf-8") as f:
                    IRC_TOKEN, API_TOKEN, self.NICK, self.CHANNELS = (l.strip() for l in f.readlines())

                super().__init__(
                    irc_token=IRC_TOKEN,
                    api_token=API_TOKEN,
                    client_id="uej04g8lskt59abzr5o50lt67k9kmi",
                    prefix="!",
                    nick=self.NICK,
                    initial_channels=[self.CHANNELS],
                )

            self.event_trigger = event_trigger(self.CHANNELS)

            print("Done")

        except (FileNotFoundError):
            msg = "Sorry you DON'T HAVE PERMISSION to run on production."
            raise TypeError(msg)

        except Exception as e:
            msg = "start bot fail with error \"" + str(e) + "\" try check your ... first "
            raise TypeError(msg)

    def get_timestamp(self):
        return datetime.utcnow().replace(microsecond=0)

    async def send_message(self, msg):
        if self.dryrun != "msgoff":
            await self.channel.send(msg)
        else:
            print(f"[INFO] Dry run mode is on \"{msg}\" not sent")

    async def event_ready(self):
        print("Bot joining channel.")
        self.channel = self.get_channel(self.CHANNELS)
        asyncio.create_task(self.event_trigger.get_channel_status(self.event_offline, self.event_live))
        await self.send_message(self.NICK + " is joined the channels.")
        print("Joined")

    async def event_raw_usernotice(self, channel, tags):
        await self.event_trigger.parsing_sub_data(
            channel,
            tags,
            self.event_sub,
            self.event_resub,
            self.event_subgift,
            self.event_submystergift,
            self.event_anonsubgift,
            self.event_anonmysterysubgift,
            self.event_raid
        )

    # custom event to trigger when channel is live and return channel start time
    async def event_live(self, starttime):
        self.channel_live = True
        self.channel_live_on = starttime
        print(f"[INFO] [{starttime}] {self.CHANNELS} is live")
        await self.greeting_sniffs()
        await self.activate_point_system()

    # custome event to trigger when channel is offline
    async def event_offline(self):
        self.channel_live = False
        print(f"[INFO] [{self.get_timestamp()}] {self.CHANNELS} is offline")
        await self.greeting_sniffs()
        await self.activate_point_system()

    async def event_message(self, ctx):
        if ctx.author.name.lower() != self.NICK:
            print(f"[MESSAGE] [{ctx.timestamp.replace(microsecond=0)}] {ctx.author.name.lower()}: {ctx.content}")

            await self.event_trigger.check_bits(ctx, self.event_bits)
            await self.handle_commands(ctx)

    async def event_bits(self, ctx, bits):
        await self.send_message(f"ขอบคุณ @{ctx.author.name.lower()} สำหรับ {bits} บิทค้าาา")

    async def event_sub(self, channel, data):
        print(f"sub: {data}")
        pass

    async def event_resub(self, channel, data):
        print(f"resub: {data}")
        pass

    async def event_subgift(self, channel, data):
        print(f"subgift: {data}")
        pass
    
    async def event_submystergift(self, channel, data):
        print(f"submysterygift: {data}")
        pass

    async def event_anonsubgift(self, channel, data):
        print(f"anonsubgift: {data}")
        pass

    async def event_anonsubmysterygift(self, channel, data):
        print(f"anonsubmysterygift: {data}")
        pass

    async def event_raid(self, channel, data):
        print(f"raid: {data}")
        pass

    async def event_join(self, user):
        if self.channel_live:
            if user.name.lower() == "armzi":
                await self.send_message(f"พ่อ @{user.name} มาแล้วววววว ไกปู")
        if user.name.lower() not in [self.NICK, self.NICK+"\r"]:
            self.user_function.user_join_part("join", user.name.lower(), self.get_timestamp())

    async def event_part(self, user):
        if self.channel_live:
            if user.name.lower() == "armzi":
                await self.send_message(f"พ่อ @{user.name} ไปแล้วววววว บะบายค้าาา")
        if user.name.lower() not in [self.NICK, self.NICK+"\r"]:
            self.user_function.user_join_part("part", user.name.lower(), self.get_timestamp())

    # TODO (1.1): write watchtime to db after live end

    async def get_users_list(self):
        users = await self.get_chatters(self.CHANNELS)
        return users.all

    async def greeting_sniffs(self):
        if self.channel_live:
            await self.send_message(f"@{self.CHANNELS} มาแล้ววววว")
        elif not self.channel_live:
            await self.send_message(f"@{self.CHANNELS} ไปแล้ววววว")

    async def activate_point_system(self):
        if self.channel_live:
            usernames = await self.get_users_list()
            for username in usernames:
                self.user_function.user_join_part("join", username.lower(), self.channel_live_on)
        asyncio.create_task(self.user_function.activate_point_system(self.channel_live, self.channel_live_on))

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
            print(f"[PAYDAY] [{self.get_timestamp()}] All {len(users)} users receive {coin} sniffscoin")
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
            print(f"[GIVE] [{self.get_timestamp()}] User: {username} receive {coin} sniffscoin")
            await self.send_message(f"@{username} ได้รับ {coin} sniffscoin")

    @commands.command(name="coin")
    async def check_coin(self, ctx):
        if self.market_open or ctx.author.is_subscriber == 1 or ctx.author.is_mod or ctx.author.name.lower() == self.CHANNELS:
            coin = self.user_function.get_coin(ctx.author.name.lower())
            print(f"[COIN] [{self.get_timestamp()}] Coin checked by {ctx.author.name.lower()}: {coin} sniffscoin")
            await self.send_message(f"@{ctx.author.name.lower()} มี {coin} sniffscoin")

    @commands.command(name="watchtime")
    async def check_user_watchtime(self, ctx):
        watchtime = self.user_function.get_user_watchtime(ctx.author.name.lower())
        watchtime_hour = 0
        watchtime_min = 0
        watchtime_sec = int(watchtime % 60)
        if watchtime >= 60: watchtime_min = int(watchtime / 60)
        if watchtime_min >= 60: watchtime_hour = int(watchtime_min / 60); watchtime_min = int(watchtime_min % 60)
        print(f"[WATCHTIME] [{self.get_timestamp()}] Watchtime checked by {ctx.author.name.lower()}: {watchtime_hour} hours {watchtime_min} mins {watchtime_sec} secs")
        if watchtime_hour > 0:
            await self.send_message(f"@{ctx.author.name.lower()} ดูไลฟ์มาแล้ว {watchtime_hour} ชั่วโมง {watchtime_min} นาที {watchtime_sec} วินาที")
        elif watchtime_min > 0:
            await self.send_message(f"@{ctx.author.name.lower()} ดูไลฟ์มาแล้ว {watchtime_min} นาที {watchtime_sec} วินาที")
        else:
            await self.send_message(f"@{ctx.author.name.lower()} ดูไลฟ์มาแล้ว {watchtime_sec} วินาที")

    @commands.command(name="uptime")  # getting live stream time
    async def uptime_command(self, ctx):
        if not self.channel_live:
            return await self.send_message("ยังไม่ถึงเวลาไลฟน้าาาา")
        uptime = (self.get_timestamp() - self.channel_live_on).total_seconds()
        uptime_hour = 0
        uptime_min = 0
        uptime_sec = int(uptime % 60)
        if uptime >= 60: uptime_min = int(uptime / 60)
        if uptime_min >= 60: uptime_hour = int(uptime_min / 60); uptime_min = int(uptime_min % 60)
        print(f"[UPTIME] [{self.get_timestamp()}] Uptime checked by {ctx.author.name.lower()}: {uptime_hour} hours {uptime_min} mins {uptime_sec} secs")
        if uptime_hour > 0:
            await self.send_message(f"สนิฟไลฟ์มาแล้ว {uptime_hour} ชั่วโมง {uptime_min} นาที {uptime_sec} วินาที น้าาา")
        elif uptime_min > 0:
            await self.send_message(f"สนิฟไลฟ์มาแล้ว {uptime_min} นาที {uptime_sec} วินาที น้าาา")
        else:
            await self.send_message(f"สนิฟไลฟ์มาแล้ว {uptime_sec} วินาที น้าาา")

    @commands.command(name="discord")
    async def discord_command(self, ctx):
        await self.send_message("https://discord.gg/Q3AMaHQEGU")  # this is a temporary link waiting for permanent link

    @commands.command(name="facebook")
    async def facebook_command(self, ctx):
        await self.send_message("https://www.facebook.com/sniffslive/")  # waiting for permanent link

    @commands.command(name="callhell")
    async def callhell(self, ctx):
        callhell_timeout = 180
        casualtie = 0
        print(f"[CALLHELL] [{self.get_timestamp()}] Wanna go to hell?")
        await self.send_message("รถทัวร์สู่ยมโลก มารับแล้ว")
        userslist = await self.get_users_list()
        exclude_list = [self.NICK, self.CHANNELS, "sirju001"]
        userslist = [username for username in userslist if username not in exclude_list]
        if ctx.author.name.lower() == self.CHANNELS or (self.environment == "dev" and ctx.author.name.lower() == "bosssoq"):
            number_user = int(len(userslist) / 2)
            random.shuffle(userslist)
            poor_users = userslist[:number_user]
            if self.environment == "dev": poor_users += ["sirju001"]  # just for fun
            for username in poor_users:
                casualtie += 1
                print(f"[CALLHELL] [{self.get_timestamp()}] Timeout: {username}")
                await self.channel.timeout(username, callhell_timeout, "โดนสนิฟดีดนิ้ว")
                await asyncio.sleep(0.5)
            users_string = ", ".join(poor_users)
            await self.send_message(f"บ๊ายบายคุณ {users_string}")
            await self.send_message(f"ใช้งาน Sniffnos มี {casualtie} คนในแชทหายตัวไป....")
