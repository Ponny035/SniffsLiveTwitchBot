import asyncio
import os

import nest_asyncio
from twitchio.ext import commands

from .coin.coin import add_coin, get_coin, payday
from .coin.subbit import subscription_payout, gift_subscription_payout, giftmystery_subscription_payout, anongift_subscription_payout, add_point_by_bit
from .misc.automod import automod
from .misc.cooldown import set_cooldown, check_cooldown
from .misc.event_trigger import EventTrigger
from .misc.updatesub import update_submonth
from .user_function.command import call_to_hell, shooter, buy_lotto, draw_lotto, update_lotto, send_lotto_msg, check_message, buy_raffle, draw_raffle
from .user_function.raffle import raffle_start, raffle_stop
from .user_function.songrequest import user_song_request, now_playing, get_song_list, select_song, delete_songlist, remove_nowplaying, delete_song, song_feed
from .timefn.timefn import activate_point_system, user_join_part, get_user_watchtime
from .timefn.timestamp import get_timestamp, sec_to_hms


class TwitchBot(commands.Bot,):
    def __init__(self):

        # get os environ
        self.environment = os.environ.get("env", "")
        self.dryrun = os.environ.get("msg", "msgon")
        self.NICK = os.environ.get("BOTNICK", "")
        self.CHANNELS = os.environ.get("CHANNELS", "")

        # init external function
        self.automod = automod()  # need to fixed

        nest_asyncio.apply()

        # define default variable
        self.market_open = True
        self.lotto_open = False
        self.raffle_open = False
        self.song_feed_on = True
        self.channel_live = False
        self.channel_live_on = None
        self.request_status = False
        self.first_run = True
        self.discord_link = "https://discord.gg/Q3AMaHQEGU"  # temp link
        self.facebook_link = "https://www.facebook.com/sniffslive/"
        self.youtube_link = "https://www.youtube.com/SniffsLive"
        self.instagram_link = "https://www.instagram.com/musicsn/"
        self.vip_list = [self.NICK, self.CHANNELS, "sirju001", "mafiamojo", "armzi", "moobot", "sniffsbot"]

        try:
            if(self.environment == "dev"):
                print(f"[INFO] [{get_timestamp()}] Init bot on DEVELOPMENT environment")
                self.dev_list = ["ponny35", "bosssoq", "franess"]

            elif(self.environment == "prod"):
                print(f"[INFO] [{get_timestamp()}] Init bot on PRODUCTION environment")
                self.dev_list = []

            super().__init__(
                irc_token=os.environ.get("IRC_TOKEN", ""),
                api_token=os.environ.get("API_TOKEN", ""),
                client_id="uej04g8lskt59abzr5o50lt67k9kmi",
                prefix="!",
                nick=self.NICK,
                initial_channels=[self.CHANNELS],
            )
            self.event_trigger = EventTrigger(self.CHANNELS)

            print(f"[INFO] [{get_timestamp()}] Done")

        except (FileNotFoundError):
            msg = "Sorry you DON'T HAVE PERMISSION to run on production."
            raise TypeError(msg)

        except Exception as e:
            msg = "start bot fail with error \"" + str(e) + "\" try check your ... first "
            raise TypeError(msg)

    async def send_message(self, msg):
        if self.dryrun != "msgoff":
            await self.channel.send(msg)
        else:
            print(f"[INFO] [{get_timestamp()}] Dry run mode is on \"{msg}\" not sent")

    def print_to_console(self, msg):
        if self.environment == "dev":
            print(msg)

    async def event_ready(self):
        print(f"[INFO] [{get_timestamp()}] Bot joining channel.")
        self.channel = self.get_channel(self.CHANNELS)
        if self.first_run:
            self.first_run = False
            asyncio.create_task(self.event_trigger.get_channel_status(self.event_offline, self.event_live))
            asyncio.create_task(send_lotto_msg(self.send_message))
        await self.send_message(self.NICK + " is joined the channels.")
        print(f"[INFO] [{get_timestamp()}] Joined")

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
        usernames = await self.get_users_list()
        asyncio.create_task(activate_point_system(self.channel_live, self.channel_live_on, usernames))

    # custome event to trigger when channel is offline
    async def event_offline(self):
        self.channel_live = False
        self.channel_live_on = None
        print(f"[INFO] [{get_timestamp()}] {self.CHANNELS} is offline")
        await self.greeting_sniffs()
        asyncio.create_task(activate_point_system(self.channel_live))

    async def event_message(self, ctx):
        if ctx.author.name.lower() != self.NICK:
            print(f"[_MSG] [{ctx.timestamp.replace(microsecond=0)}] {ctx.author.name.lower()}: {ctx.content}")

            await check_message(ctx.author.name.lower(), ctx.content, self.vip_list, self.dev_list, self.send_message, self.channel.timeout)
            await update_submonth(ctx.author.name.lower(), ctx.raw_data)
            await self.event_trigger.handle_channelpoints(ctx.raw_data, self.event_channelpoint)
            await self.event_trigger.check_bits(ctx.raw_data, self.event_bits)
            await self.automod.auto_mod(ctx.author.name.lower(), (ctx.author.is_mod or ctx.author.is_subscriber == 1), ctx.content, ctx.raw_data, self.send_message, self.channel)
            await self.handle_commands(ctx)

    async def event_bits(self, data):
        await add_point_by_bit(data["username"], data["bits"], data["submonth"], self.send_message)

    async def event_channelpoint(self, data):
        add_coin(data["username"], data["coin"])

    async def event_sub(self, channel, data):
        usernames = await self.get_users_list()
        await subscription_payout(data["username"], data["sub_month_count"], usernames, self.send_message)
        self.print_to_console(f"sub: {data}")

    async def event_resub(self, channel, data):
        usernames = await self.get_users_list()
        await subscription_payout(data["username"], data["sub_month_count"], usernames, self.send_message)
        self.print_to_console(f"resub: {data}")

    async def event_subgift(self, channel, data):
        usernames = await self.get_users_list()
        await gift_subscription_payout(data["username"], data["recipent"], usernames, self.send_message)
        self.print_to_console(f"subgift: {data}")

    async def event_submystergift(self, channel, data):
        usernames = await self.get_users_list()
        await giftmystery_subscription_payout(data["username"], data["gift_sub_count"], usernames, self.send_message)
        self.print_to_console(f"submysterygift: {data}")

    async def event_anonsubgift(self, channel, data):
        usernames = await self.get_users_list()
        await anongift_subscription_payout(data["recipent"], data["gift_sub_count"], usernames, self.send_message)
        self.print_to_console(f"anonsubgift: {data}")

    async def event_anonsubmysterygift(self, channel, data):
        await self.send_message(f"ขอบคุณ Gift จากผู้ไม่ประสงค์ออกนามจำนวน {data['gift_sub_count']} Gift sniffsHeart sniffsHeart sniffsHeart")
        self.print_to_console(f"anonsubmysterygift: {data}")

    async def event_raid(self, channel, data):
        await self.send_message(f"ขอบคุณ @{data['username']} สำหรับการ Raid ผู้ชมจำนวน {data['viewers']} ค่าา sniffsHeart sniffsHeart sniffsHeart")
        self.print_to_console(f"raid: {data}")

    async def event_join(self, user):
        if user.name.lower() == "sirju001":
            await self.send_message("ดาบผู้ขี้เกียจ มาแล้ววววววว รอแทงได้เลย sniffsAH")
        if self.channel_live:
            if user.name.lower() == "armzi":
                await self.send_message(f"พ่อ @{user.name} มาแล้วววววว ไกปู sniffsShock")
            if user.name.lower() not in [self.NICK, self.NICK + "\r"]:
                user_join_part("join", user.name.lower(), get_timestamp())

    async def event_part(self, user):
        if user.name.lower() == "sirju001":
            await self.send_message(f"@{user.name.lower()} แอบหนีไปดูแมวอีกแล้ววววว sniffsAH")
        if self.channel_live:
            if user.name.lower() == "armzi":
                await self.send_message(f"พ่อ @{user.name} ไปแล้วววววว บะบายค้าาา sniffsBaby")
            if user.name.lower() not in [self.NICK, self.NICK + "\r"]:
                user_join_part("part", user.name.lower(), get_timestamp())

    async def get_users_list(self):
        users = await self.get_chatters(self.CHANNELS)
        return users.all

    async def greeting_sniffs(self):
        if self.channel_live:
            await self.send_message(f"sniffsHi sniffsHi sniffsHi @{self.CHANNELS} มาแล้ววววว")
        elif not self.channel_live:
            await self.send_message(f"sniffsZzz sniffsZzz sniffsZzz @{self.CHANNELS} ไปแล้ววววว")

    @commands.command(name="market")
    async def activate_market(self, ctx):
        if (ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list):
            commands_split = ctx.content.split()
            try:
                status = commands_split[1]
            except IndexError:
                status = None
            if status == "open":
                if not self.market_open:
                    self.market_open = True
                    print(f"[COIN] [{get_timestamp()}] Market is now open")
                    await self.send_message("เปิดตลาดแล้วจ้าาาา~ sniffsBaby sniffsBaby")
            elif status == "close":
                if self.market_open:
                    self.market_open = False
                    print(f"[COIN] [{get_timestamp()}] Market is now close")
                    await self.send_message("ปิดตลาดแล้วจ้าาาา~ sniffsBaby sniffsBaby")

    @commands.command(name="payday")
    async def give_coin_allusers(self, ctx):
        if (ctx.author.name.lower() == self.CHANNELS) or (ctx.author.name.lower() in self.dev_list):
            commands_split = ctx.content.split()
            try:
                coin = int(commands_split[1])
                if coin < 0:
                    coin = 0
            except IndexError:
                coin = 1
            usernames = await self.get_users_list()
            payday(usernames, coin)
            await self.send_message(f"ผู้ชมทั้งหมด {len(usernames)} คน ได้รับ {coin} sniffscoin sniffsAH")

    @commands.command(name="give")
    async def give_coin_user(self, ctx):
        if (ctx.author.name.lower() == self.CHANNELS) or (ctx.author.name.lower() in self.dev_list):
            commands_split = ctx.content.split()
            try:
                username = commands_split[1]
            except IndexError:
                username = None
            try:
                coin = int(commands_split[2])
                if coin < 0:
                    coin = 0
            except IndexError:
                coin = 1
            if (username is not None):
                add_coin(username, coin)
                await self.send_message(f"@{username} ได้รับ {coin} sniffscoin sniffsAH")

    @commands.command(name="coin")
    async def check_coin(self, ctx):
        if (ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod or ctx.author.is_subscriber == 1 or self.market_open):
            if (check_cooldown(ctx.author.name.lower(), "coin")) or (ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list):
                if not ((ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list)):
                    set_cooldown(ctx.author.name.lower(), "coin")
                await get_coin(ctx.author.name.lower(), self.send_message)

    @commands.command(name="watchtime")
    async def check_user_watchtime(self, ctx):
        if (check_cooldown(ctx.author.name.lower(), "watchtime")) or (ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list):
            if not ((ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list)):
                set_cooldown(ctx.author.name.lower(), "watchtime")
            await get_user_watchtime(ctx.author.name.lower(), self.channel_live, self.CHANNELS, self.send_message)

    @commands.command(name="uptime")  # getting live stream time
    async def uptime_command(self, ctx):
        if (check_cooldown(ctx.author.name.lower(), "uptime")) or (ctx.author.is_mod or ctx.author.name.lower() == self.CHANNELS) or (ctx.author.name.lower() in self.dev_list):
            if not ((ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list)):
                set_cooldown(ctx.author.name.lower(), "uptime")
            if not self.channel_live:
                return await self.send_message("ยังไม่ถึงเวลาไลฟ์น้าาาา sniffsHeart sniffsHeart sniffsHeart")
            uptime = sec_to_hms((get_timestamp() - self.channel_live_on).total_seconds())
            print(f"[TIME] [{get_timestamp()}] Uptime checked by {ctx.author.name.lower()}: {uptime[0]} days {uptime[1]} hours {uptime[2]} mins {uptime[3]} secs")
            if any(time > 0 for time in uptime):
                response_string = f"@{ctx.author.name.lower()} สนิฟไลฟ์มาแล้ว"
                if uptime[0] > 0:
                    response_string += f" {uptime[0]} วัน"
                if uptime[1] > 0:
                    response_string += f" {uptime[1]} ชั่วโมง"
                if uptime[2] > 0:
                    response_string += f" {uptime[2]} นาที"
                if uptime[3] > 0:
                    response_string += f" {uptime[3]} วินาที"
                response_string += " น้าาา sniffsHeart sniffsHeart sniffsHeart"
                await self.send_message(response_string)

    @commands.command(name="discord")
    async def discord_command(self, ctx):
        if (check_cooldown(ctx.author.name.lower(), "discord")) or (ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list):
            if not ((ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list)):
                set_cooldown(ctx.author.name.lower(), "discord")
            await self.send_message(f"@{ctx.author.name.lower()} มาคุยกันได้ใน Discord {self.discord_link} sniffsBaby")

    @commands.command(name="facebook", aliases=("fb", "Facebook"))
    async def facebook_command(self, ctx):
        if (check_cooldown(ctx.author.name.lower(), "facebook")) or (ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list):
            if not ((ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list)):
                set_cooldown(ctx.author.name.lower(), "facebook")
            await self.send_message(f"@{ctx.author.name.lower()} มาตามเพจสนิฟที่นี่ {self.facebook_link} sniffsBaby")

    @commands.command(name="youtube", aliases=("yt", "Youtube"))
    async def youtube_command(self, ctx):
        if (check_cooldown(ctx.author.name.lower(), "youtube")) or (ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list):
            if not ((ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list)):
                set_cooldown(ctx.author.name.lower(), "youtube")
            await self.send_message(f"@{ctx.author.name.lower()} Channel ร้างของสนิฟเอง {self.youtube_link} sniffsBaby")

    @commands.command(name="instagram", aliases=("ig", "Instagram"))
    async def instagram_command(self, ctx):
        if (check_cooldown(ctx.author.name.lower(), "instagram")) or (ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list):
            if not ((ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list)):
                set_cooldown(ctx.author.name.lower(), "instagram")
            await self.send_message(f"@{ctx.author.name.lower()} IG ของสนิฟ {self.instagram_link} sniffsBaby")

    @commands.command(name="commands", aliases=["command", "cmd"])
    async def commmands_command(self, ctx):
        if (check_cooldown(ctx.author.name.lower(), "commands")) or (ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list):
            if not ((ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list)):
                set_cooldown(ctx.author.name.lower(), "commands")
            await self.send_message("!sr ขอเพลง | !coin เช็คเหรียญ | !lotto ซื้อหวย | !kill จ้างมือปืนสนิฟ")
            await self.send_message("!uptime | !watchtime | !discord | !fb | !yt | !ig")

    @commands.command(name="callhell")
    async def callhell(self, ctx):
        if (ctx.author.name.lower() == self.CHANNELS) or (ctx.author.name.lower() in self.dev_list):
            await self.send_message("รถทัวร์สู่ยมโลก มารับแล้ว")
            usernames = await self.get_users_list()
            exclude_list = self.vip_list + self.dev_list
            data = await call_to_hell(usernames, exclude_list, self.channel.timeout)
            users_string = ", ".join(data["poor_users"])
            await self.send_message(f"บ๊ายบายคุณ {users_string}")
            await self.send_message(f"ใช้งาน Sniffnos มี {data['casualtie']} คนในแชทหายตัวไป.... sniffsCry sniffsCry sniffsCry")

    @commands.command(name="sr")
    async def user_song_request(self, ctx):
        if self.request_status:
            if (check_cooldown(ctx.author.name.lower(), "song_request", 120)) or (ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list):
                success = await user_song_request(ctx.content, get_timestamp(), ctx.author.name.lower(), self.send_message)
                if not ((ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list)):
                    if success:
                        set_cooldown(ctx.author.name.lower(), "song_request")

    # !song req {on|off} | !song sel {song-id} | !song clear | !song del {song-id} | !song delnp | !song feed {on|off}
    @commands.command(name="song")
    async def song_request(self, ctx):
        if (ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list):
            commands_split = ctx.content.split()
            try:
                command1 = commands_split[1]
            except IndexError:
                command1 = None
            try:
                command2 = commands_split[2]
            except IndexError:
                command2 = None
            if command1 == "req":
                if self.request_status and command2 == "off":
                    self.request_status = False
                    await self.send_message("ปิดระบบขอเพลงแล้วน้าต้าวๆ sniffsAH")
                elif not self.request_status and command2 == "on":
                    self.request_status = True
                    await self.send_message("เปิดระบบขอเพลงแล้วน้าต้าวๆ sniffsMic ส่งเพลงโดยพิมพ์ !sr ตามด้วยชื่อเพลงน้า (cost 1 sniffscoin)")
            elif command1 == "feed" and command2 is not None:
                if self.song_feed_on and command2 == "off":
                    self.song_feed_on = False
                    await song_feed(False, self.send_message)
                elif (not self.song_feed_on) and command2 == "on":
                    self.song_feed_on = True
                    await song_feed(True, self.send_message)
            elif command1 == "list":
                if not self.song_feed_on:
                    await get_song_list(self.send_message)
            elif command1 == "clear":
                await delete_songlist(self.send_message)
            elif command1 == "del" and command2 is not None:
                await delete_song(command2, self.send_message)
            elif command1 == "sel" and command2 is not None:
                await select_song(command2, self.send_message)
            elif command1 == "delnp":
                await remove_nowplaying(self.send_message)

    @commands.command(name="np")
    async def get_song(self, ctx):
        if self.request_status:
            if (check_cooldown(ctx.author.name.lower(), "song")) or (ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list):
                if not ((ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list)):
                    set_cooldown(ctx.author.name.lower(), "song")
                await now_playing(ctx.author.name.lower(), self.send_message)

    @commands.command(name="kill")
    async def kill_user(self, ctx):
        if self.channel_live:
            commands_split = ctx.content.split()
            try:
                target = commands_split[1].lower()
            except IndexError:
                target = None
            if target is not None:
                await shooter(ctx.author.name.lower(), target, self.vip_list, self.dev_list, self.send_message, self.channel.timeout)

    @commands.command(name="lotto")
    async def sniffs_lotto(self, ctx):
        commands_split = ctx.content.split()
        try:
            lotto = commands_split[1]
        except IndexError:
            lotto = None
        if lotto is not None:
            if lotto == "start":
                if (ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list):
                    if not self.lotto_open:
                        self.lotto_open = True
                        await update_lotto(self.lotto_open)
                        print(f"[LOTO] [{get_timestamp()}] LOTTO System started")
                        await self.send_message("sniffsHi เร่เข้ามาเร่เข้ามา SniffsLotto ใบละ 5 coins !lotto ตามด้วยเลข 2 หลัก ประกาศรางวัลตอนปิดไลฟ์จ้า sniffsAH")
            elif lotto == "stop":
                if (ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list):
                    if self.lotto_open:
                        self.lotto_open = False
                        await update_lotto(self.lotto_open)
                        print(f"[LOTO] [{get_timestamp()}] LOTTO System stopped")
                        await self.send_message("ปิดการซื้อ SniffsLotto แล้วจ้า รอประกาศผลรางวัลเลย sniffsAH")
            elif lotto == "draw":
                if (ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list):
                    if self.lotto_open:
                        self.lotto_open = False
                        await update_lotto(self.lotto_open)
                        print(f"[LOTO] [{get_timestamp()}] LOTTO System stopped")
                        await self.send_message("ปิดการซื้อ SniffsLotto แล้วจ้า รอประกาศผลรางวัลเลย sniffsAH")                
                    await draw_lotto(self.send_message)
            else:
                if self.lotto_open:
                    await buy_lotto(ctx.author.name.lower(), lotto, self.send_message)

    @commands.command(name="raffle")
    async def sniffs_raffle(self, ctx):
        commands_split = ctx.content.split()
        try:
            raffle = commands_split[1]
        except IndexError:
            raffle = None
        if raffle == "start":
            if (ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list):
                if not self.raffle_open:
                    self.raffle_open = True
                    success = raffle_start(self.raffle_open)
                    if success:
                        print(f"[RAFL] [{get_timestamp()}] Raffle system started")
                        await self.send_message("พิมพ์ !raffle เพื่อเข้ามาลุ้นของรางวัลกาชาจากสนิฟเลย! sniffsHeart")
        elif raffle == "stop":
            if (ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list):
                if self.raffle_open:
                    self.raffle_open = False
                    success = raffle_stop(self.raffle_open)
                    if success:
                        print(f"[RAFL] [{get_timestamp()}] Raffle system stopped")
                        await self.send_message("ปิดการซื้อตั๋วแล้ว รอสนิฟจับของรางวัลน้าาา sniffsHeart")
        elif raffle == "draw":
            if (ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list):
                if self.raffle_open:
                    self.raffle_open = False
                    success = raffle_stop(self.raffle_open)
                    if success:
                        print(f"[RAFL] [{get_timestamp()}] Raffle system stopped")
                        await self.send_message("ปิดการซื้อตั๋วแล้ว รอสนิฟจับของรางวัลน้าาา sniffsHeart")
                await draw_raffle(self.send_message)
        else:
            if self.raffle_open:
                if raffle is not None:
                    try:
                        count = int(raffle)
                        if count < 0:
                            return
                    except Exception:
                        return
                elif raffle is None:
                    count = 1
                await buy_raffle(ctx.author.name.lower(), count, self.send_message, self.channel.timeout)
