import discord

from redbot.core.commands import EmojiConverter as ec
from emoji import EMOJI_DATA
from typing import Union

# https://github.com/i-am-zaidali/cray-cogs/blob/cdeef241b7b40f20313645a2a3cbe91ca12423f2/tickchanger/util.py#L5
class EmojiConverter(ec):
    async def convert(self, ctx, emoji: str):
        emoji = emoji.strip()
        try:
            EMOJI_DATA[emoji]
        except KeyError:
            return await super().convert(ctx, emoji)
        else:
            return emoji
