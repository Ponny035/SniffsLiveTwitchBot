import asyncio
from datetime import datetime

import nest_asyncio
from twitchio.ext import commands


class TwitchBot(commands.Bot,):
    def __init__(self, environment, dryrun, userfunction, automod, event_trigger):

        self.environment = environment
        self.dryrun = dryrun

        # init external function
        self.automod = automod()  # need to fixed
        self.user_function = userfunction(self.environment)

        nest_asyncio.apply()

        # define default variable
        self.market_open = False
        self.channel_live = False
        self.channel_live_on = None
        self.request_status = False
        self.discord_link = "https://discord.gg/Q3AMaHQEGU"  # temp link
        self.facebook_link = "https://www.facebook.com/sniffslive/"
        self.youtube_link = "https://www.youtube.com/SniffsLive"

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

    def print_to_console(self, msg):
        if self.environment == "dev":
            print(msg)

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
            self.event_anonsubmysterygift,
            self.event_raid
        )

    # custom event to trigger when channel is live and return channel start time
    async def event_live(self, starttime):
        self.channel_live = True
        self.channel_live_on = starttime
        print(f"[INFO] [{starttime}] {self.CHANNELS} is live")
        await self.greeting_sniffs()
        await self.activate_point_system("start")

    # custome event to trigger when channel is offline
    async def event_offline(self):
        self.channel_live = False
        self.channel_live_on = None
        print(f"[INFO] [{self.get_timestamp()}] {self.CHANNELS} is offline")
        await self.greeting_sniffs()
        await self.activate_point_system("stop")
        await self.user_function.delete_songlist()

    async def event_message(self, ctx):
        if ctx.author.name.lower() != self.NICK:
            print(f"[_MSG] [{ctx.timestamp.replace(microsecond=0)}] {ctx.author.name.lower()}: {ctx.content}")

            await self.event_trigger.check_bits(ctx.raw_data, self.event_bits)
            await self.automod.auto_mod(ctx.author.name.lower(), (ctx.author.is_mod or ctx.author.is_subscriber == 1), ctx.content, ctx.raw_data, self.send_message, self.channel)
            await self.handle_commands(ctx)

    async def event_bits(self, data):
        await self.user_function.add_point_by_bit(data["username"], data["bits"], self.send_message)

    async def event_sub(self, channel, data):
        usernames = await self.get_users_list()
        response = self.user_function.subscription_payout(data["username"], data["sub_month_count"], usernames)
        for msg in response:
            await self.send_message(msg)
        self.print_to_console(f"sub: {data}")

    async def event_resub(self, channel, data):
        usernames = await self.get_users_list()
        response = self.user_function.subscription_payout(data["username"], data["sub_month_count"], usernames)
        for msg in response:
            await self.send_message(msg)
        self.print_to_console(f"resub: {data}")
        pass

    async def event_subgift(self, channel, data):
        usernames = await self.get_users_list()
        response = self.user_function.gift_subscription_payout(data["username"], data["recipent"], usernames)
        for msg in response:
            await self.send_message(msg)
        self.print_to_console(f"subgift: {data}")
        pass
    
    async def event_submystergift(self, channel, data):
        usernames = await self.get_users_list()
        response = self.user_function.giftmystery_subscription_payout(data["username"], data["gift_sub_count"], usernames)
        for msg in response:
            await self.send_message(msg)
        self.print_to_console(f"submysterygift: {data}")
        pass

    async def event_anonsubgift(self, channel, data):
        usernames = await self.get_users_list()
        response = self.user_function.anongift_subscription_payout(data["recipent"], data["gift_sub_count"], usernames)
        for msg in response:
            await self.send_message(msg)
        self.print_to_console(f"anonsubgift: {data}")
        pass

    async def event_anonsubmysterygift(self, channel, data):
        await self.send_message(f"ขอบคุณ Gift จากผู้ไม่ประสงค์ออกนามจำนวน {data['gift_sub_count']} Gift")
        self.print_to_console(f"anonsubmysterygift: {data}")
        pass

    async def event_raid(self, channel, data):
        await self.send_message(f"ขอบคุณ @{data['username']} สำหรับการ Raid ผู้ชมจำนวน {data['viewers']} ค่าา")
        self.print_to_console(f"raid: {data}")
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

    async def activate_point_system(self, cmd):
        if cmd == "start":
            usernames = await self.get_users_list()
        elif cmd == "stop":
            usernames = None
        asyncio.create_task(self.user_function.activate_point_system(self.channel_live, self.channel_live_on, usernames))

    @commands.command(name="market")
    async def activate_market(self, ctx):
        if (ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (self.environment == "dev" and ctx.author.name.lower() == "bosssoq"):
            commands_split = ctx.content.split()
            try:
                status = commands_split[1]
            except:
                status = None
            if status == "open":
                self.market_open = True
                print(f"[COIN] [{self.get_timestamp()}] Market is now open")
                await self.send_message("เปิดตลาดแล้วจ้าาาา~")
            elif status == "close":
                self.market_open = False
                print(f"[COIN] [{self.get_timestamp()}] Market is now close")
                await self.send_message("ปิดตลาดแล้วจ้าาาา~")

    @commands.command(name="payday")
    async def give_coin_allusers(self, ctx):
        if (ctx.author.name.lower() == self.CHANNELS) or (self.environment == "dev" and ctx.author.name.lower() == "bosssoq"):
            commands_split = ctx.content.split()
            try:
                coin = int(commands_split[1])
                if coin < 0: coin = 0
            except:
                coin = 1
            usernames = await self.get_users_list()
            self.user_function.payday(usernames, coin)
            await self.send_message(f"ผู้ชมทั้งหมด {len(usernames)} คน ได้รับ {coin} sniffscoin")

    @commands.command(name="give")
    async def give_coin_user(self, ctx):
        if (ctx.author.name.lower() == self.CHANNELS) or (self.environment == "dev" and ctx.author.name.lower() == "bosssoq"):
            commands_split = ctx.content.split()
            try:
                username = commands_split[1]
            except:
                username = None
            try:
                coin = int(commands_split[2])
                if coin < 0: coin = 0
            except:
                coin = 1
            usernames = await self.get_users_list()
            # print(usernames)
            if (username is not None) and (username in usernames):
                self.user_function.add_coin(username, coin)
                await self.send_message(f"@{username} ได้รับ {coin} sniffscoin")

    @commands.command(name="coin")
    async def check_coin(self, ctx):
        if (self.market_open or ctx.author.is_subscriber == 1 or ctx.author.is_mod or ctx.author.name.lower() == self.CHANNELS):
            if (ctx.author.is_mod or ctx.author.name.lower() == self.CHANNELS) or (self.user_function.check_cooldown(ctx.author.name.lower(), "coin")) or (self.environment == "dev" and ctx.author.name.lower() == "bosssoq"):
                self.user_function.set_cooldown(ctx.author.name.lower(), "coin")
                coin = self.user_function.get_coin(ctx.author.name.lower())
                await self.send_message(f"@{ctx.author.name.lower()} มี {coin} sniffscoin")

    @commands.command(name="watchtime")
    async def check_user_watchtime(self, ctx):
        if (ctx.author.is_mod or ctx.author.name.lower() == self.CHANNELS) or (self.user_function.check_cooldown(ctx.author.name.lower(), "watchtime")) or (self.environment == "dev" and ctx.author.name.lower() == "bosssoq"):
            self.user_function.set_cooldown(ctx.author.name.lower(), "watchtime")
            watchtime = self.user_function.get_user_watchtime(ctx.author.name.lower(), self.channel_live)
            if any(time > 0 for time in watchtime):
                response_string = f"@{ctx.author.name.lower()} ดูไลฟ์มาแล้ว"
                if watchtime[0] > 0:
                    response_string += f" {watchtime[0]} ชั่วโมง"
                if watchtime[1] > 0:
                    response_string += f" {watchtime[1]} นาที"
                if watchtime[2] > 0:
                    response_string += f" {watchtime[2]} วินาที"
                await self.send_message(response_string)
            else:
                await self.send_message(f"@{ctx.author.name.lower()} เพิ่งมาดู @{self.CHANNELS} สิน้าาาาา")

    @commands.command(name="uptime")  # getting live stream time
    async def uptime_command(self, ctx):
        if (ctx.author.is_mod or ctx.author.name.lower() == self.CHANNELS) or (self.user_function.check_cooldown(ctx.author.name.lower(), "uptime")) or (self.environment == "dev" and ctx.author.name.lower() == "bosssoq"):
            self.user_function.set_cooldown(ctx.author.name.lower(), "uptime")
            if not self.channel_live:
                return await self.send_message("ยังไม่ถึงเวลาไลฟ์น้าาาา")
            uptime = self.user_function.sec_to_hms((self.get_timestamp() - self.channel_live_on).total_seconds())
            print(f"[TIME] [{self.get_timestamp()}] Uptime checked by {ctx.author.name.lower()}: {uptime[0]} hours {uptime[1]} mins {uptime[2]} secs")
            if any(time > 0 for time in uptime):
                response_string = f"@{ctx.author.name.lower()} สนิฟไลฟ์มาแล้ว"
                if uptime[0] > 0:
                    response_string += f" {uptime[0]} ชั่วโมง"
                if uptime[1] > 0:
                    response_string += f" {uptime[1]} นาที"
                if uptime[2] > 0:
                    response_string += f" {uptime[2]} วินาที"
                response_string += " น้าาา"
                await self.send_message(response_string)

    @commands.command(name="discord")
    async def discord_command(self, ctx):
        if (ctx.author.is_mod or ctx.author.name.lower() == self.CHANNELS) or (self.user_function.check_cooldown(ctx.author.name.lower(), "discord")) or (self.environment == "dev" and ctx.author.name.lower() == "bosssoq"):
            self.user_function.set_cooldown(ctx.author.name.lower(), "discord")
            await self.send_message(f"@{ctx.author.name.lower()} {self.discord_link}")

    @commands.command(name="facebook")
    async def facebook_command(self, ctx):
        if (ctx.author.is_mod or ctx.author.name.lower() == self.CHANNELS) or (self.user_function.check_cooldown(ctx.author.name.lower(), "facebook")) or (self.environment == "dev" and ctx.author.name.lower() == "bosssoq"):
            self.user_function.set_cooldown(ctx.author.name.lower(), "facebook")
            await self.send_message(f"@{ctx.author.name.lower()} {self.facebook_link}")

    @commands.command(name="callhell")
    async def callhell(self, ctx):
        if ctx.author.name.lower() == self.CHANNELS or (self.environment == "dev" and ctx.author.name.lower() == "bosssoq"):
            await self.send_message("รถทัวร์สู่ยมโลก มารับแล้ว")
            usernames = await self.get_users_list()
            exclude_list = [self.NICK, self.CHANNELS, "sirju001"]
            data = await self.user_function.call_to_hell(usernames, exclude_list, self.channel.timeout)
            users_string = ", ".join(data["poor_users"])
            await self.send_message(f"บ๊ายบายคุณ {users_string}")
            await self.send_message(f"ใช้งาน Sniffnos มี {data['casualtie']} คนในแชทหายตัวไป....")

    # @commands.command(name="commands", aliases=["command", "cmd"])
    # async def commmands_command(self,ctx):
    #     if (ctx.author.is_mod or ctx.author.name.lower() == self.CHANNELS) or (self.user_function.check_cooldown(ctx.author.name.lower(), "commands")) or (self.environment == "dev" and ctx.author.name.lower() == "bosssoq"):
    #         self.user_function.set_cooldown(ctx.author.name.lower(), "commands")
    #         await self.send_message(f"นี่คือคำสั่งทั้งหมดน้า พิมพ์ !commands เพื่อดูคำสั่งทั้งหมด | พิมพ์ !coin เพื่อเช็คจำนวน sniffcoin ที่มีอยู่ | พิมพ์ !watchtime เพื่อเช็คเวลาที่ดูมาแล้ว | พิมพ์ !uptime เพื่อดูเวลาว่าสนิฟไลฟ์มากี่ชั่วโมงแล้ว | พิมพ์ !discord เพื่อเข้าสู่พื้นที่ของต้าวๆ | พิมพ์ !facebook เพื่อติดตามสนิฟผ่านทางเพจ! | พิมพ์ !youtube เพื่อติดตามสนิฟผ่านยูทูป")
    
    @commands.command(name="youtube")
    async def facebook_command(self, ctx):
        if (ctx.author.is_mod or ctx.author.name.lower() == self.CHANNELS) or (self.user_function.check_cooldown(ctx.author.name.lower(), "youtube")) or (self.environment == "dev" and ctx.author.name.lower() == "bosssoq"):
            self.user_function.set_cooldown(ctx.author.name.lower(), "youtube")
            await self.send_message(f"@{ctx.author.name.lower()} {self.youtube_link}")

    @commands.command(name="sr")
    async def user_song_request(self, ctx):
        if self.request_status:
            if (ctx.author.is_mod or ctx.author.name.lower() == self.CHANNELS) or (self.user_function.check_cooldown(ctx.author.name.lower(), "song_request", 300)) or (self.environment == "dev" and ctx.author.name.lower() == "bosssoq"):
                self.user_function.set_cooldown(ctx.author.name.lower(), "song_request")
                await self.user_function.user_song_request(ctx.content, self.get_timestamp(), ctx.author.name.lower(), self.send_message)

    # !song request on | !song request off | !song list | !song select {song-id} | !song list clear
    @commands.command(name="song")
    async def song_request(self, ctx):
        if (ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (self.environment == "dev" and ctx.author.name.lower() == "bosssoq"):
            commands_split = ctx.content.split()
            try:
                command1 = commands_split[1]
            except:
                command1 = None
            try:
                command2 = commands_split[2]
            except:
                command2 = None
            if command1 == "request":
                if self.request_status and command2 == "off":
                    self.request_status = False
                    await self.send_message("ปิดระบบขอเพลงแล้วน้าต้าวๆ")
                elif not self.request_status and command2 == "on":
                    self.request_status = True
                    await self.send_message("เปิดระบบขอเพลงแล้วน้าต้าวๆ ส่งเพลงโดยพิมพ์ !request ตามด้วยชื่อเพลงน้า")
            elif command1 == "list":
                if command2 is None:
                    await self.user_function.get_song_list(self.send_message)
                elif command2 == "clear":
                    await self.user_function.delete_songlist(self.send_message)
            elif command1 == "delete" and command2 is not None:
                await self.user_function.delete_song(command2, self.send_message)
            elif command1 == "select" and command2 is not None:
                await self.user_function.select_song(command2, self.send_message)

    @commands.command(name="np")
    async def get_song(self, ctx):
        if self.request_status:
            if (ctx.author.is_mod or ctx.author.name.lower() == self.CHANNELS) or (self.user_function.check_cooldown(ctx.author.name.lower(), "song")) or (self.environment == "dev" and ctx.author.name.lower() == "bosssoq"):
                self.user_function.set_cooldown(ctx.author.name.lower(), "song")
                await self.user_function.now_playing(ctx.author.name.lower(), self.send_message)
