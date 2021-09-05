import os
import re
import traceback

import requests
from twitchio.channel import Channel
from twitchio.message import Message
from twitchio.user import User
from twitchio.ext import commands, routines

from .coin.coin import add_coin, get_coin, payday
from .coin.subbit import subscription_payout, gift_subscription_payout, giftmystery_subscription_payout, anongift_subscription_payout, add_point_by_bit
from .misc.automod import auto_mod
from .misc.cooldown import set_cooldown, check_cooldown
from .misc.event_trigger import EventTrigger
from .misc.updatesub import update_submonth
from .misc.webfeed import activate_webfeed_feed, deductcoin_feed, givecoin_feed, lotto_start_feed, lotto_stop_feed, payday_feed, raffle_start_feed, raffle_stop_feed, raid_feed, song_request_off_feed, song_request_on_feed
from .user_function.command import buy_coinflip, call_to_hell, shooter, buy_lotto, draw_lotto, transfer_coin, send_lotto_msg, check_message, buy_raffle, draw_raffle
from .user_function.raffle import raffle_start, raffle_stop
from .user_function.songrequest import user_song_request, now_playing, get_song_list, select_song, delete_songlist, remove_nowplaying, delete_song, song_feed
from .timefn.timefn import activate_point_system, add_point_by_watchtime, user_join_part, get_user_watchtime
from .timefn.timestamp import get_timestamp, sec_to_hms


class TwitchBot(commands.Bot,):
    def __init__(self):

        # get os environ
        self.environment: str = os.environ.get("env", "")
        self.dryrun: str = os.environ.get("msg", "msgon")
        self.NICK: str = os.environ.get("BOTNICK", "")
        self.CHANNELS: str = os.environ.get("CHANNELS", "")
        self.TOKEN: str = os.environ.get("IRC_TOKEN", "")
        self.APIID: str = os.environ.get("API_ID", "")
        self.APISEC: str = os.environ.get("API_TOKEN", "")

        # define default variable
        self.feed_enable: bool = True
        self.market_open: bool = True
        self.lotto_open: bool = False
        self.raffle_open: bool = False
        self.song_feed_on: bool = True
        self.channel = None
        self.channel_live: bool = False
        self.channel_live_on = 0
        self.request_status: bool = False
        self.first_run: bool = True
        self.discord_link: str = "https://discord.gg/Q3AMaHQEGU"  # temp link
        self.facebook_link: str = "https://www.facebook.com/sniffslive/"
        self.youtube_link: str = "https://www.youtube.com/SniffsLive"
        self.instagram_link: str = "https://www.instagram.com/musicsn/"
        self.vip_list: list[str] = [self.NICK, self.CHANNELS, "sirju001", "mafiamojo", "armzi", "moobot", "sniffsbot"]

        try:
            if(self.environment == "dev"):
                print(f"[INFO] [{get_timestamp()}] Init bot on DEVELOPMENT environment")
                self.dev_list: list[str] = ["ponny35", "bosssoq", "franess", "foxzapop"]

            elif(self.environment == "prod"):
                print(f"[INFO] [{get_timestamp()}] Init bot on PRODUCTION environment")
                self.dev_list: list[str] = []

            super().__init__(
                token=self.TOKEN,
                client_secret=self.APISEC,
                client_id=self.APIID,
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

    async def send_message(self, msg: str):
        while self.channel is None:
            await self.join_channels([self.CHANNELS])
            self.channel = self.get_channel(self.CHANNELS)
        if self.dryrun != "msgoff":
            await self.channel.send(msg)
        else:
            print(f"[INFO] [{get_timestamp()}] Dry run mode is on \"{msg}\" not sent")

    async def send_message_timeout(self, username: str, period: int, reason=""):
        if self.dryrun != "msgoff":
            await self.channel.send(f"/timeout {username} {period} {reason}")
        else:
            print(f"[INFO] [{get_timestamp()}] Dry run mode is on timeout not sent")

    async def send_message_ban(self, username: str, reason=""):
        if self.dryrun != "msgoff":
            await self.channel.send(f"/ban {username} {reason}")
        else:
            print(f"[INFO] [{get_timestamp()}] Dry run mode is on ban not sent")

    async def send_message_feed(self, msg: str):
        if not self.feed_enable:
            await self.channel.send(msg)

    def print_to_console(self, msg: str):
        if self.environment == "dev":
            print(msg)

    async def event_ready(self):
        print(f"[INFO] [{get_timestamp()}] Bot joining channel.")
        self.channel = self.get_channel(self.CHANNELS)
        while len(self.connected_channels) == 0:
            await self.join_channels([self.CHANNELS])
            self.channel = self.get_channel(self.CHANNELS)
        print(F"{self.channel} Connected")
        if self.first_run:
            self.first_run = False
            self.event_trigger.get_channel_status.start(self.event_offline, self.event_live, stop_on_error=False)
            self.check_channel.start(stop_on_error=False)
        else:
            print(f"[INFO] [{get_timestamp()}] BOT Reconnected")
        await self.send_message(self.NICK + " is joined the channels.")
        print(f"[INFO] [{get_timestamp()}] Joined")

    @routines.routine(seconds=20)
    async def check_channel(self):
        if len(self.connected_channels) == 0:
            print(f"[_ERR] [{get_timestamp()}] No Connected Channels!")
            await self.join_channels([self.CHANNELS])
            self.channel = self.get_channel(self.CHANNELS)
            print(f"[INFO] [{get_timestamp()}] Rejoined Channels!")

    async def event_raw_usernotice(self, channel: Channel, tags: list):
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
        usernames = self.get_users_list()
        await activate_point_system(self.channel_live, self.channel_live_on, usernames)
        add_point_by_watchtime.start(stop_on_error=False)

    # custom event to trigger when channel is offline
    async def event_offline(self):
        self.channel_live = False
        self.channel_live_on = 0
        print(f"[INFO] [{get_timestamp()}] {self.CHANNELS} is offline")
        await self.greeting_sniffs()
        add_point_by_watchtime.cancel()
        await activate_point_system(self.channel_live)

    async def event_message(self, message: Message):
        if (message.author is not None) and (message.author.name.lower() != self.NICK):
            print(f"[_MSG] [{message.timestamp.replace(microsecond=0)}] {message.author.name.lower()} Is Mod {message.author.is_mod} Is Sub {bool(message.author.is_subscriber)}: {message.content}")

            await check_message(message.author.name.lower(), message.content, self.vip_list, self.dev_list, self.send_message, self.send_message_timeout)
            await update_submonth(message.author.name.lower(), message.raw_data)
            await self.event_trigger.handle_channelpoints(message.raw_data, self.event_channelpoint)
            await self.event_trigger.check_bits(message.raw_data, self.event_bits)
            await auto_mod(message.author.name.lower(), (message.author.is_mod or bool(message.author.is_subscriber)), message.content, message.raw_data, self.send_message, self.send_message_timeout, self.send_message_ban)
            await self.handle_commands(message)

    async def event_bits(self, data: dict):
        await add_point_by_bit(data["username"], data["bits"], data["submonth"], self.send_message_feed)

    async def event_channelpoint(self, data: dict):
        add_coin(data["username"], data["coin"])

    async def event_sub(self, channel: Channel, data: dict):
        usernames = self.get_users_list()
        await subscription_payout(data["username"], data["sub_month_count"], data["methods"], usernames, self.send_message, self.send_message_feed)
        self.print_to_console(f"sub: {data}")

    async def event_resub(self, channel: Channel, data: dict):
        usernames = self.get_users_list()
        await subscription_payout(data["username"], data["sub_month_count"], data["methods"], usernames, self.send_message, self.send_message_feed)
        self.print_to_console(f"resub: {data}")

    async def event_subgift(self, channel: Channel, data: dict):
        usernames = self.get_users_list()
        await gift_subscription_payout(data["username"], data["recipent"], data["methods"], usernames, self.send_message_feed)
        self.print_to_console(f"subgift: {data}")

    async def event_submystergift(self, channel: Channel, data: dict):
        usernames = self.get_users_list()
        await giftmystery_subscription_payout(data["username"], data["gift_sub_count"], data["methods"], usernames, self.send_message_feed)
        self.print_to_console(f"submysterygift: {data}")

    async def event_anonsubgift(self, channel: Channel, data: dict):
        usernames = self.get_users_list()
        await anongift_subscription_payout(data["recipent"], data["methods"], usernames, self.send_message, self.send_message_feed)
        self.print_to_console(f"anonsubgift: {data}")

    async def event_anonsubmysterygift(self, channel: Channel, data: dict):
        await self.send_message(f"ขอบคุณ Gift จากผู้ไม่ประสงค์ออกนามจำนวน {data['gift_sub_count']} Gift sniffsHeart sniffsHeart sniffsHeart")
        self.print_to_console(f"anonsubmysterygift: {data}")

    async def event_raid(self, channel: Channel, data: dict):
        await self.send_message_feed(f"ขอบคุณ @{data['username']} สำหรับการ Raid ผู้ชมจำนวน {data['viewers']} คน ค่าา sniffsHeart sniffsHeart sniffsHeart")
        raid_feed(data['username'], data['viewers'])
        self.print_to_console(f"raid: {data}")

    async def event_join(self, channel: Channel, user: User):
        if self.channel_live:
            if user.name.lower() == "armzi":
                await self.send_message(f"พ่อ @{user.name} มาแล้วววววว ไกปู sniffsShock")
            if user.name.lower() not in [self.NICK, self.NICK + "\r"]:
                user_join_part("join", user.name.lower(), get_timestamp())

    async def event_part(self, channel: Channel, user: User):
        if self.channel_live:
            if user.name.lower() == "armzi":
                await self.send_message(f"พ่อ @{user.name} ไปแล้วววววว บะบายค้าาา sniffsBaby")
            if user.name.lower() not in [self.NICK, self.NICK + "\r"]:
                user_join_part("part", user.name.lower(), get_timestamp())

    def get_users_list(self):
        url_endpoint = f"https://tmi.twitch.tv/group/user/{self.CHANNELS}/chatters"
        resp = requests.get(url_endpoint)
        if resp.status_code == 200:
            data = resp.json()
            users = [name for key in data['chatters'] for name in data['chatters'][key]]
            return users
        else:
            return []

    async def greeting_sniffs(self):
        if self.channel_live:
            await self.send_message(f"sniffsHi sniffsHi sniffsHi @{self.CHANNELS} มาแล้ววววว")
        elif not self.channel_live:
            await self.send_message(f"sniffsZzz sniffsZzz sniffsZzz @{self.CHANNELS} ไปแล้ววววว")

    @commands.command(name="market")
    async def activate_market(self, ctx: commands.Context):
        if (ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list):
            commands_split = ctx.message.content.split()
            try:
                status = commands_split[1]
                match status:
                    case "open":
                        if not self.market_open:
                            self.market_open = True
                            print(f"[COIN] [{get_timestamp()}] Market is now open")
                            await self.send_message("เปิดตลาดแล้วจ้าาาา~ sniffsBaby sniffsBaby")
                    case "close":
                        if self.market_open:
                            self.market_open = False
                            print(f"[COIN] [{get_timestamp()}] Market is now close")
                            await self.send_message("ปิดตลาดแล้วจ้าาาา~ sniffsBaby sniffsBaby")
            except IndexError:
                return

    @commands.command(name="webfeed")
    async def activate_webfeed(self, ctx: commands.Context):
        if (ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list):
            commands_split = ctx.message.content.split()
            try:
                status = commands_split[1]
                match status:
                    case "on":
                        if not self.feed_enable:
                            self.feed_enable = True
                            print(f"[FEED] [{get_timestamp()}] Webfeed System started")
                            await self.send_message("Webfeed System started sniffsAH")
                            activate_webfeed_feed(self.feed_enable)
                    case "off":
                        if self.feed_enable:
                            self.feed_enable = False
                            print(f"[FEED] [{get_timestamp()}] Webfeed System stopped")
                            await self.send_message("Webfeed System stopped sniffsAH")
                            activate_webfeed_feed(self.feed_enable)
            except IndexError:
                return

    @commands.command(name="payday")
    async def give_coin_allusers(self, ctx: commands.Context):
        if (ctx.author.name.lower() == self.CHANNELS) or (ctx.author.name.lower() in self.dev_list):
            commands_split = ctx.message.content.split()
            try:
                coin = int(commands_split[1])
                if coin < 0:
                    return
            except IndexError:
                coin = 1
            usernames = self.get_users_list()
            payday(usernames, coin)
            await self.send_message_feed(f"ผู้ชมทั้งหมด {len(usernames)} คน ได้รับ {coin} sniffscoin sniffsAH")
            payday_feed(coin, len(usernames))

    @commands.command(name="give")
    async def give_coin_user(self, ctx: commands.Context):
        if (ctx.author.name.lower() == self.CHANNELS) or (ctx.author.name.lower() in self.dev_list):
            commands_split = ctx.message.content.split()
            try:
                username = commands_split[1]
                username = re.sub(r'^@', '', username)
                username = username.lower()
            except IndexError:
                return
            try:
                coin = int(commands_split[2])
                if coin < 0:
                    return
            except IndexError:
                coin = 1
            add_coin(username, coin)
            await self.send_message_feed(f"@{username} ได้รับ {coin} sniffscoin sniffsAH")
            givecoin_feed(username, coin)

    @commands.command(name="deduct")
    async def deduct_coin_user(self, ctx: commands.Context):
        if (ctx.author.name.lower() == self.CHANNELS) or (ctx.author.name.lower() in self.dev_list):
            commands_split = ctx.message.content.split()
            try:
                username = commands_split[1]
                username = re.sub(r'^@', '', username)
                username = username.lower()
            except IndexError:
                return
            try:
                coin = int(commands_split[2])
                if coin < 0:
                    return
            except IndexError:
                coin = 1
            add_coin(username, -coin)
            await self.send_message_feed(f"@{username} ถูกหัก {coin} sniffscoin sniffsAH")
            deductcoin_feed(username, coin)

    @commands.command(name="coin")
    async def check_coin(self, ctx: commands.Context):
        if ctx.cooldown:
            if (ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod or bool(ctx.author.is_subscriber) or self.market_open):
                await get_coin(ctx.author.name.lower(), self.send_message)

    @commands.command(name="watchtime")
    async def check_user_watchtime(self, ctx: commands.Context):
        if ctx.cooldown:
            await get_user_watchtime(ctx.author.name.lower(), self.channel_live, self.CHANNELS, self.send_message)

    @commands.command(name="uptime")  # getting live stream time
    async def uptime_command(self, ctx: commands.Context):
        if ctx.cooldown:
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

    @commands.command(name="discord", aliases=("dis"))
    async def discord_command(self, ctx: commands.Context):
        if ctx.cooldown:
            await self.send_message(f"@{ctx.author.name.lower()} มาคุยกันได้ใน Discord {self.discord_link} sniffsBaby")

    @commands.command(name="facebook", aliases=("fb", "Facebook"))
    async def facebook_command(self, ctx: commands.Context):
        if ctx.cooldown:
            await self.send_message(f"@{ctx.author.name.lower()} มาตามเพจสนิฟที่นี่ {self.facebook_link} sniffsBaby")

    @commands.command(name="youtube", aliases=("yt", "Youtube"))
    async def youtube_command(self, ctx: commands.Context):
        if ctx.cooldown:
            await self.send_message(f"@{ctx.author.name.lower()} Channel ร้างของสนิฟเอง {self.youtube_link} sniffsBaby")

    @commands.command(name="instagram", aliases=("ig", "Instagram"))
    async def instagram_command(self, ctx: commands.Context):
        if ctx.cooldown:
            await self.send_message(f"@{ctx.author.name.lower()} IG ของสนิฟ {self.instagram_link} sniffsBaby")

    @commands.command(name="commands", aliases=["command", "cmd"])
    async def commmands_command(self, ctx: commands.Context):
        if ctx.cooldown:
            await self.send_message("!sr ขอเพลง | !coin เช็คเหรียญ | !lotto ซื้อหวย | !kill จ้างมือปืนสนิฟ")
            await self.send_message("!uptime | !watchtime | !discord | !fb | !yt | !ig")

    @commands.command(name="callhell")
    async def callhell(self, ctx: commands.Context):
        if (ctx.author.name.lower() == self.CHANNELS) or (ctx.author.name.lower() in self.dev_list):
            await self.send_message("รถทัวร์สู่ยมโลก มารับแล้ว")
            usernames = self.get_users_list()
            exclude_list = self.vip_list + self.dev_list
            data = await call_to_hell(usernames, exclude_list, self.send_message_timeout)
            await self.send_message(f"ใช้งาน Sniffnos มี {data['casualtie']} คนในแชทหายตัวไป.... sniffsCry sniffsCry sniffsCry")

    @commands.command(name="sr")
    async def user_song_request(self, ctx: commands.Context):
        if ctx.cooldown:
            if self.request_status:
                success = await user_song_request(ctx.message.content, get_timestamp(), ctx.author.name.lower(), self.send_message_feed)
                if success:
                    set_cooldown(ctx.author.name.lower(), "sr")

    # !song req {on|off} | !song sel {song-id} | !song clear | !song del {song-id} | !song delnp | !song feed {on|off}
    @commands.command(name="song")
    async def song_request(self, ctx: commands.Context):
        if (ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list):
            commands_split = ctx.message.content.split()
            try:
                main_command: str = commands_split[1]
            except IndexError:
                return
            try:
                argument: str = commands_split[2]
            except IndexError:
                argument = None
            match main_command:
                case "req":
                    if self.request_status and argument == "off":
                        self.request_status = False
                        await self.send_message("ปิดระบบขอเพลงแล้วน้าต้าวๆ sniffsAH")
                        song_request_off_feed()
                    elif not self.request_status and argument == "on":
                        self.request_status = True
                        await self.send_message("เปิดระบบขอเพลงแล้วน้าต้าวๆ sniffsMic ส่งเพลงโดยพิมพ์ !sr ตามด้วยชื่อเพลงน้า (cost 1 sniffscoin)")
                        song_request_on_feed()
                case "feed":
                    if self.song_feed_on and argument == "off":
                        self.song_feed_on = False
                        await song_feed(False, self.send_message)
                    elif not self.song_feed_on and argument == "on":
                        self.song_feed_on = True
                        await song_feed(True, self.send_message)
                case "list":
                    if not self.song_feed_on:
                        await get_song_list(self.send_message)
                case "clear":
                    await delete_songlist(self.send_message)
                case "del":
                    if argument is not None:
                        await delete_song(argument, self.send_message)
                case "sel":
                    if argument is not None:
                        await select_song(argument, self.send_message)
                case "delnp":
                    await remove_nowplaying(self.send_message)

    @commands.command(name="np")
    async def get_song(self, ctx: commands.Context):
        if ctx.cooldown:
            if self.request_status:
                await now_playing(ctx.author.name.lower(), self.send_message)

    @commands.command(name="kill")
    async def kill_user(self, ctx: commands.Context):
        if self.channel_live:
            commands_split = ctx.message.content.split()
            try:
                target = commands_split[1].lower()
                await shooter(ctx.author.name.lower(), target, self.vip_list, self.dev_list, self.send_message_feed, self.send_message_timeout)
            except IndexError:
                return

    @commands.command(name="lotto")
    async def sniffs_lotto(self, ctx: commands.Context):
        commands_split = ctx.message.content.split()
        try:
            lotto = commands_split[1]
            match lotto:
                case "start":
                    if (ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list):
                        if not self.lotto_open:
                            self.lotto_open = True
                            print(f"[LOTO] [{get_timestamp()}] LOTTO System started")
                            send_lotto_msg.start(self.send_message, stop_on_error=True)
                            lotto_start_feed()
                case "stop":
                    if (ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list):
                        if self.lotto_open:
                            self.lotto_open = False
                            print(f"[LOTO] [{get_timestamp()}] LOTTO System stopped")
                            send_lotto_msg.cancel()
                            await self.send_message("ปิดการซื้อ SniffsLotto แล้วจ้า รอประกาศผลรางวัลเลย sniffsAH")
                            lotto_stop_feed()
                case "draw":
                    if (ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list):
                        if self.lotto_open:
                            self.lotto_open = False
                            send_lotto_msg.cancel()
                            print(f"[LOTO] [{get_timestamp()}] LOTTO System stopped")
                            await self.send_message("ปิดการซื้อ SniffsLotto แล้วจ้า รอประกาศผลรางวัลเลย sniffsAH")
                            lotto_stop_feed()
                        await draw_lotto(self.send_message)
                case _:
                    if self.lotto_open:
                        await buy_lotto(ctx.author.name.lower(), lotto, self.send_message_feed)
        except IndexError:
            return

    @commands.command(name="raffle")
    async def sniffs_raffle(self, ctx: commands.Context):
        commands_split = ctx.message.content.split()
        try:
            raffle = commands_split[1]
        except IndexError:
            raffle = None
        match raffle:
            case "start":
                if (ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list):
                    if not self.raffle_open:
                        self.raffle_open = True
                        success = raffle_start(self.raffle_open)
                        if success:
                            print(f"[RAFL] [{get_timestamp()}] Raffle system started")
                            await self.send_message("พิมพ์ !raffle เพื่อเข้ามาลุ้นของรางวัลกาชาจากสนิฟเลย! sniffsHeart")
                            raffle_start_feed()
            case "stop":
                if (ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list):
                    if self.raffle_open:
                        self.raffle_open = False
                        success = raffle_stop(self.raffle_open)
                        if success:
                            print(f"[RAFL] [{get_timestamp()}] Raffle system stopped")
                            await self.send_message("ปิดการซื้อตั๋วแล้ว รอสนิฟจับของรางวัลน้าาา sniffsHeart")
                            raffle_stop_feed()
            case "draw":
                if (ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list):
                    if self.raffle_open:
                        self.raffle_open = False
                        success = raffle_stop(self.raffle_open)
                        if success:
                            print(f"[RAFL] [{get_timestamp()}] Raffle system stopped")
                            await self.send_message("ปิดการซื้อตั๋วแล้ว รอสนิฟจับของรางวัลน้าาา sniffsHeart")
                            raffle_stop_feed()
                    await draw_raffle(self.send_message)
            case _:
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
                    await buy_raffle(ctx.author.name.lower(), count, self.send_message_feed, self.send_message_timeout)

    @commands.command(name="flip")
    async def coin_flip(self, ctx: commands.Context):
        if ctx.cooldown:
            if (ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod or bool(ctx.author.is_subscriber) or self.market_open):
                commands_split = ctx.message.content.split()
                try:
                    side = commands_split[1]
                    if (side := side.lower()) not in (opt := ("h", "t", "head", "tail", "หัว", "ก้อย")):
                        await self.send_message("ใส่ด้านของเหรียญตามนี้เท่านั้นนะ! " + ", ".join(opt))
                        return
                except IndexError:
                    return
                try:
                    bet = int(commands_split[2])
                    if bet < 1:
                        return
                except IndexError:
                    bet = 1
                except ValueError:
                    bet = 1
                await buy_coinflip(ctx.author.name.lower(), side, bet, self.send_message_feed)

    @commands.command(name="transfer")
    async def transfer(self, ctx: commands.Context):
        commands_split = ctx.message.content.split()
        try:
            recipent = commands_split[1]
        except IndexError:
            return
        try:
            amount = int(commands_split[2])
            if amount < 0:
                return
        except Exception:
            return
        viewers = self.get_users_list()
        await transfer_coin(ctx.author.name.lower(), recipent, amount, viewers, self.send_message)

    async def global_before_invoke(self, ctx: commands.Context):
        postpone_cooldown = ["market", "webfeed", "payday", "give", "callhell", "sr", "song", "kill", "lotto", "raffle", "flip", "transfer"]
        ctx.cooldown = check_cooldown(ctx.author.name.lower(), ctx.command.name) or (ctx.author.name.lower() == self.CHANNELS or ctx.author.is_mod) or (ctx.author.name.lower() in self.dev_list)
        if (ctx.cooldown) and (ctx.command.name not in postpone_cooldown):
            set_cooldown(ctx.author.name.lower(), ctx.command.name)

    async def event_command_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.CommandNotFound):
            pass
        else:
            print(''.join(traceback.format_exception(type(error), error, error.__traceback__)))
