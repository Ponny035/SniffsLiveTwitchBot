# from typing import Dict, Optional, Union
# from dataclasses import dataclass
# from contextlib import contextmanager
# from collections import defaultdict  # second choice of try
# from . import db
# import warnings
from datetime import datetime
import re
# import logging

# log = logging.getLogger(__name__)


# @dataclass
# class Untimeout:
#     pass


# @dataclass
# class Unban:
#     pass


# @dataclass
# class Timeout:
#     duration: int
#     reason: Optional[str]
#     once: bool

# @dataclass
# class Ban:
#     reason: Optional[str]

# ModerationAction = Union[Untimeout, Unban, Timeout, Ban]

# def _combine_resons(a: Optional[str], b:Optional[str]) -> Optional[str]:
#     if a is None and b is None:
#         return None

#     if a is None:
#         return b

#     if b is None:
#         return a

#     return f"{a} + {b}"


# class ModerationActions:
#     # login -> action excute
#     actions: Dict[str, ModerationAction]

#     def __init__(self) -> None:
#         super().__init__()
#         self.actions = {}

#     def add(self, login: str, action: ModerationAction) -> None:
#         if login not in self.actions:
#             self.actions[login] = action
#             return

#         existing_action = self.actions[login]

#         if isinstance(action, Ban):
#             # combine the two
#             self.actions[login] = Ban(reason=_combine_resons(existing_action.reason, action.reason))
#         else:
#             # ban lower tier action
#             self.actions[login] = action
#         return

#         if isinstance(action, Timeout):
#             if isinstance(existing_action, Ban):
#                 # Existing action is higher-tier
#                 return

#             if isinstance(existing_action,Timeout):
#                 # combine two
#                 self.actions[login] = Timeout(
#                     duration=max(action.duration, existing_action.duration),
#                     reason=_combine_resons(existing_action.reason, action.reason),
#                     once=existing_action.once and action.once,
#                 )
#             else:
#                 # timeout lower tier action
#                 self.actions[login] = action
#             return

#             if isinstance(action, Unban):
#                 if isinstance(existing_action, Ban) or isinstance(existing_action, Timeout):
#                     # exist action is higher tier
#                     return

#                 if isinstance(existing_action, Unban):
#                     pass
#                 return

#     def execute(self, bot) -> None:
#         for login, action in self.actions.items():
#             if isinstance(action, Ban):
#                 bot.ban_login(login, action.reason)
#             if isinstance(action, Timeout):
#                 bot.timeout_login(login, action.duration, action.reason, action.once)
#             if isinstance(action, Unban):
#                 bot.unban_login(login)
#             if isinstance(action, Untimeout):
#                 bot.untimeout_login(login)


# @contextmanager
# def new_message_processing_scope(bot):
#     bot.thread_locals.moderation_actions = ModerationActions()

#     try:
#         yield
#     finally:
#         mod_actions = bot.thread_locals.moderation_actions
#         bot.thread_locals.moderation_actions = None
#         try:
#             mod_actions.execute(bot)
#         except:
#             log.exception("Faild to execute moderation action after messsage process scope end")


class automod:
    def __init__(self):
        # self.CURSES = ("fuck", "poo", "boo", "you are suck")
        self.warning_users = {}

    def get_timestamp(self):
        return datetime.utcnow().replace(microsecond=0)

    async def auto_mod(self, user, role, message, raw_data, send_message, mod_action):
        msg_id = re.search(r"(?<=id=)(.*?)(?=;)", raw_data)[0]
        await self.auto_cursesword(user, role, message, msg_id, send_message, mod_action)
        await self.auto_removelink(user, role, message, msg_id, send_message, mod_action)
        await self.auto_removetwitchlink(user, message, msg_id, send_message, mod_action)

    async def auto_cursesword(self, user, role, message, msg_id, send_message, mod_action):
        # if any([curse in message.lower() for curse in self.CURSES]):
        #     warning_curses_timers = (1, 5, 60)
        #     await self.warn(user, send_message, mod_action, warning_curses_timers, msg_id, reason="curses")
        pass

    async def auto_removelink(self, user, role, message, msg_id, send_message, mod_action):
        # if any([curse in message.lower() for curse in self.CURSES]):
        #     warning_curses_timers = (1, 5, 60)
        #     await self.warn(user, send_message, mod_action, warning_curses_timers, reason="curses")
        if not role:  # not mod or subscriber
            test_url1 = re.match("https?://", message)
            test_url2 = re.match(r"[A-z]+\.(com|org|in|co|tv|us)", message)  # need to fine tune regex
            test_result = bool(test_url1 or test_url2)
            if test_result:
                warning_link_timers = (0, 0, 1, 5, 10, 30, 60)
                await self.warn(user, send_message, mod_action, warning_link_timers, msg_id, reason="paste_link_by_non_sub")

    async def auto_removetwitchlink(self, user, message, msg_id, send_message, mod_action):
        check_url = bool(re.match("https?://(www.)?twitch.tv/", message))
        check_clipurl = not bool(re.match("https?://(www.)?twitch.tv/.*/clip/.*", message))
        if check_url and check_clipurl:
            warning_link_timers = (0, 0, 10, 30, 60)
            await self.warn(user, send_message, mod_action, warning_link_timers, msg_id, reason="paste_twitch_link")      

    async def warn(self, user, send_message, mod_action, timers, msg_id=None, reason=None):
        # Warnings = db("SELECT warning FROM user WHERE user id?",
        # user["id"])
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
                print(f"[AMOD] [{self.get_timestamp()}] DeleteMessage: {user} Duration: {timeout_mins} Reason: {reason}")
                await send_message(f"@{user} เตือนก่อนน้า sniffsAngry sniffsAngry sniffsAngry")
            else:
                await mod_action.timeout(user, timeout_mins * 60, f"ไม่ได้น้า เตือนครั้งที่ {self.warning_users[user][reason]}")
                print(f"[AMOD] [{self.get_timestamp()}] Timeout: {user} Duration: {timeout_mins} Reason: {reason}")
                await send_message(f"@{user} ไม่เชื่อฟังสนิฟ sniffsAngry sniffsAngry sniffsAngry ไปนั่งพักก่อนซัก {timeout_mins} นาทีนะ")

            # db.execute("UPDATE users SET warnings = Warnings +1 WHERE UserID = ?",
            # user["ID"])

        else:
            self.warning_users[user][reason] = 0  # reset counter
            await mod_action.ban(user, f"ละเมิดกฎครบ {self.warning_users[user][reason]} ครั้ง บินไปซะ")
            await send_message(f"@{user} เตือนแล้วไม่ฟัง ขออนุญาตบินนะคะ sniffsAngry sniffsAngry sniffsAngry")
