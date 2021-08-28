import re

from src.timefn.timestamp import get_timestamp


class automod:
    def __init__(self):
        # self.CURSES = ("fuck", "poo", "boo", "you are suck")
        self.warning_users = {}

    async def auto_mod(self, user: str, role: bool, message: str, raw_data: str, send_message, timeout, ban):
        msg_id = re.search(r"(?<=id=)(.*?)(?=;)", raw_data)[0]
        # await self.auto_cursesword(user, role, message, msg_id, send_message, timeout, ban)
        await self.auto_removelink(user, role, message, msg_id, send_message, timeout, ban)
        await self.auto_removetwitchlink(user, message, msg_id, send_message, timeout, ban)

    # async def auto_cursesword(self, user, role, message, msg_id, send_message, timeout, ban):
    #     if any([curse in message.lower() for curse in self.CURSES]):
    #         warning_curses_timers = (1, 5, 60)
    #         await self.warn(user, send_message, timeout, ban, warning_curses_timers, msg_id, reason="curses")
    #     pass

    async def auto_removelink(self, user: str, role: bool, message: str, msg_id: str, send_message, timeout, ban):
        # if any([curse in message.lower() for curse in self.CURSES]):
        #     warning_curses_timers = (1, 5, 60)
        #     await self.warn(user, send_message, timeout, ban, warning_curses_timers, reason="curses")
        if not role:  # not mod or subscriber
            test_url1 = re.match("https?://", message)
            test_url2 = re.match(r"[A-z]+\.(com|org|in|co|tv|us)", message)  # need to fine tune regex
            test_result = bool(test_url1 or test_url2)
            if test_result:
                warning_link_timers = (0, 0, 1, 5, 10, 30, 60)
                await self.warn(user, send_message, timeout, ban, warning_link_timers, msg_id, reason="paste_link_by_non_sub")

    async def auto_removetwitchlink(self, user: str, message: str, msg_id: str, send_message, timeout, ban):
        check_url = bool(re.match("https?://(www.)?twitch.tv/", message))
        check_clipurl = not bool(re.match("https?://(www.)?twitch.tv/.*/clip/.*", message))
        if check_url and check_clipurl:
            warning_link_timers = (0, 0, 10, 30, 60)
            await self.warn(user, send_message, timeout, ban, warning_link_timers, msg_id, reason="paste_twitch_link")

    async def warn(self, user: str, send_message, timeout, ban, timers: tuple[int], msg_id=None, reason=None):
        warning = 0
        try:
            warning = self.warning_users[user][reason]
            self.warning_users[user][reason] += 1
        except KeyError:
            self.warning_users[user] = {}
            self.warning_users[user][reason] = 1
        if warning < len(timers):
            timeout_mins = timers[warning]
            if timeout_mins == 0:
                await send_message(f"/delete {msg_id}")
                print(f"[AMOD] [{get_timestamp()}] DeleteMessage: {user} Duration: {timeout_mins} Reason: {reason}")
                await send_message(f"@{user} เตือนก่อนน้า sniffsAngry sniffsAngry sniffsAngry")
            else:
                await timeout(user, timeout_mins * 60, f"ไม่ได้น้า เตือนครั้งที่ {self.warning_users[user][reason]}")
                print(f"[AMOD] [{get_timestamp()}] Timeout: {user} Duration: {timeout_mins} Reason: {reason}")
                await send_message(f"@{user} ไม่เชื่อฟังสนิฟ sniffsAngry sniffsAngry sniffsAngry ไปนั่งพักก่อนซัก {timeout_mins} นาทีนะ")
        else:
            self.warning_users[user][reason] = 0  # reset counter
            await ban(user, f"ละเมิดกฎครบ {self.warning_users[user][reason]} ครั้ง บินไปซะ")
            await send_message(f"@{user} เตือนแล้วไม่ฟัง ขออนุญาตบินนะคะ sniffsAngry sniffsAngry sniffsAngry")
