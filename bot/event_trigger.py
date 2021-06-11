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
                    await asyncio.sleep(10)
                    success_callback[1] = 0
            elif not self.channel_live:
                channel_status = await self.twitch_api.get_stream(self.CHANNELS)
                if channel_status is not None and success_callback[1] == 0:
                    self.channel_live = (channel_status["type"] == "live")
                    self.channel_live_on = datetime.strptime(channel_status["started_at"], "%Y-%m-%dT%H:%M:%SZ")
                    success_callback = [1, 1]
                    await chan_online(self.channel_live_on)
                    await asyncio.sleep(10)
                    success_callback[0] = 0

    async def check_bits(self, ctx, event_bit):
        bits = 0
        try:
            bits = re.search(r"(?<=bits=)([0-9]+)", ctx.raw_data)[0]
            print(f"[BITS] [{ctx.timestamp.replace(microsecond=0)}] {ctx.author.name.lower()}: {bits} bits")
        except:
            pass
        await event_bit(ctx, bits)

    async def parsing_sub_data(self, sub, resub, subgift, submysterygift, anonsubgift, anonsubmysterygift, raid):
        pass