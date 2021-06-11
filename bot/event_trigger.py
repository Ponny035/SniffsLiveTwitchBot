import asyncio
from datetime import datetime
import re

from twitchio.client import Client


class EventTrigger:
    def __init__(self, channels):
        self.CHANNELS = channels
        self.channel_live = False

        self.twitch_api = Client(
            client_id="wt9nmvcq4oszo9k4qpswvl7htigg08",
            client_secret="5c2ihtk3viinbrpnvlooys8c56w56f"
        )

    async def get_channel_status(self, chan_offline, chan_online):
        success_callback = [0, 0]
        while True:
            if self.channel_live:
                channel_status = await self.twitch_api.get_stream(self.CHANNELS)
                if channel_status is None and success_callback[0] == 0:
                    self.channel_live = False
                    success_callback = [1, 1]
                    await chan_offline()
                    await asyncio.sleep(31)
                    success_callback[1] = 0
            elif not self.channel_live:
                channel_status = await self.twitch_api.get_stream(self.CHANNELS)
                if channel_status is not None and success_callback[1] == 0:
                    self.channel_live = (channel_status["type"] == "live")
                    self.channel_live_on = datetime.strptime(channel_status["started_at"], "%Y-%m-%dT%H:%M:%SZ")
                    success_callback = [1, 1]
                    await chan_online(self.channel_live_on)
                    await asyncio.sleep(31)
                    success_callback[0] = 0

    async def check_bits(self, ctx, event_bit):
        bits = 0
        try:
            bits = re.search(r"(?<=bits=)([0-9]+)", ctx.raw_data)[0]
            print(f"[BITS] [{ctx.timestamp.replace(microsecond=0)}] {ctx.author.name.lower()}: {bits} bits")
            await event_bit(ctx, bits)
        except:
            pass

    async def parsing_sub_data(self, channel, tags, sub, resub, subgift, submysterygift, anonsubgift, anonsubmysterygift, raid):
        try:
            username = tags["login"]
        except KeyError:
            try:
                username = tags["display-name"].lower()
            except KeyError:
                pass
        try:
            plan = tags["msg-param-sub-plan"]
        except KeyError:
            plan = ""
        try:
            plan_name = tags["msg-param-sub-plan-name"].replace("\\s", " ")
        except KeyError:
            plan_name = None
        try:
            prime = (plan == "Prime")
        except:
            prime = False
        methods = [prime, plan, plan_name]
        try:
            streak_months = tags["msg-param-streak-months"]
        except KeyError:
            streak_months = 0
        try:
            recipent = tags["msg-param-recipient-user-name"]
        except KeyError:
            try:
                recipent = tags["msg-param-recipent-display-name"].lower()
            except KeyError:
                pass
        try:
            gift_sub_count = tags["msg-param-mass-gift-count"]
        except KeyError:
            gift_sub_count = 0
        try:
            sub_month_count = tags["msg-param-cumulative-months"]
        except KeyError:
            pass
        try:
            msg_id = tags["msg-id"]
        except KeyError:
            return

        if msg_id == "sub":
            data = {
                "username": username,
                "methods": methods,
                "sub_month_count": sub_month_count
            }
            await sub(channel, data)

        elif msg_id == "resub":
            data = {
                "username": username,
                "methods": methods,
                "sub_month_count": sub_month_count,
                "streak_months": streak_months
            }
            await resub(channel, data)

        elif msg_id == "subgift":
            data = {
                "username": username,
                "methods": methods,
                "streak_months": streak_months,
                "recipent": recipent
            }
            await subgift(channel, data)

        elif msg_id == "submysterygift":
            data = {
                "username": username,
                "methods": methods,
                "gift_sub_count": gift_sub_count
            }
            await submysterygift(channel, data)

        elif msg_id == "anonsubgift":
            data = {
                "methods": methods,
                "streak_months": streak_months,
                "recipent": recipent
            }
            await anonsubgift(channel, data)

        elif msg_id == "anonsubmysterygift":
            data = {
                "methods": methods,
                "gift_sub_count": gift_sub_count
            }
            await anonsubmysterygift(channel, data)

        elif msg_id == "raid":
            try:
                username = tags["msg-param-login"]
            except KeyError:
                username = tags["msg-param-displayName"].lower()
            data = {
                "username": username,
                "viewers": tags["msg-param-viewerCount"]
            }
            await raid(channel, data)
