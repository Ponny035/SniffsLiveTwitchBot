# from typing import Dict, Optional, Union
# from dataclasses import dataclass
# from contextlib import contextmanager
from collections import defaultdict #second choice of try
# from . import db 
# import warnings
from datetime import datetime
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
#     #login -> action excute
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
#             #combine the two
#             self.actions[login] = Ban(reason=_combine_resons(existing_action.reason, action.reason))
#         else:
#             #ban lower tier action
#             self.actions[login] = action
#         return

#         if isinstance(action, Timeout):
#             if isinstance(existing_action, Ban):
#                 #Existing action is higher-tier
#                 return
            
#             if isinstance(existing_action,Timeout):
#                 #combine two
#                 self.actions[login] = Timeout(
#                     duration=max(action.duration, existing_action.duration),
#                     reason=_combine_resons(existing_action.reason, action.reason),
#                     once=existing_action.once and action.once,
#                 )
#             else:
#                 #timeout lower tier action
#                 self.actions[login] = action
#             return

#             if isinstance(action, Unban):
#                 if isinstance(existing_action, Ban) or isinstance(existing_action, Timeout):
#                     #exist action is higher tier
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
        self.CURSES = ("fuck", "poo", "boo", "you are suck")
        self.warning_timers = (1, 5, 60)
        self.warning_users = {}

    def get_timestamp(self):
        return datetime.utcnow().replace(microsecond=0)

    async def clear(self, user, message, send_message, mod_action):
        if any([curse in message.lower() for curse in self.CURSES]):
            await self.warn(user, send_message, mod_action, reason="curses")

    async def warn(self, user, send_message, mod_action, reason=None):
        # Warnings = db("SELECT warning FROM user WHERE user id?",
        # user["id"])
        warning = 0
        try:
            warning = self.warning_users[user]
            self.warning_users[user] += 1
        except KeyError:
            self.warning_users[user] = 1
        if warning < len(self.warning_timers):
            timeout_mins = self.warning_timers[warning]
            await mod_action.timeout(user, timeout_mins * 60, f"คำพูดไม่น่ารัก เตือนครั้งที่ {self.warning_users[user]}")
            print(f"[AMOD] [{self.get_timestamp()}] Timeout: {user} Duration: {timeout_mins} Reason: {reason}")
            await send_message(f"@{user} คำพูดไม่น่ารัก ไปนั่งพักก่อนซัก {timeout_mins} นาทีนะ")

            # db.execute("UPDATE users SET warnings = Warnings +1 WHERE UserID = ?",
            # user["ID"])

        else:
            await mod_action.ban(user, f"คำพูดไม่น่ารัก ครบ {self.warning_users[user]} ครั้ง บินไปซะ")
            await send_message(f"@{user} เตือนแล้วไม่ฟัง ขออนุญาตบินนะคะ")
