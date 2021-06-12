# from typing import Dict, Optional, Union
# from dataclasses import dataclass
# from contextlib import contextmanager
from collections import defaultdict #second choice of try
# from . import db 
import warnings
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




Curses = ("fuck, poo, boo, you are suck")
Warning_timers = (1,5,60)


def clear(bot, user, message):
    if any([curses in message for curses in Curses]):
        warn(bot, user, reason="cursss")
        return False

    return True


def warn(bot, user, *, reason=None):
    # Warnings = db("SELECT warning FROM user WHERE user id?",
    # user["id"])

    if warn < len(Warning_timers):
        mins = Warning_timers[warnings]
        bot.send_message(f"/timeout {user['name']} {mins}m")
        bot.seng_message(f"{user['name']}, you ahve been mute for this reason: {reason}. Un mute in {mins} mins.")

        # db.execute("UPDATE users SET warnings = Warnings +1 WHERE UserID = ?",
        # user["ID"])

    else:
        bot.send_message(f"/ban{user['name']} Repeted infractions.")
        bot.send_message(f"{user['name']}, you have beeen ban from chat.")