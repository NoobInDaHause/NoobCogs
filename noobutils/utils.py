import discord

from redbot.core import commands

from emoji import EMOJI_DATA
from typing import Union

# https://github.com/i-am-zaidali/cray-cogs/blob/cdeef241b7b40f20313645a2a3cbe91ca12423f2/tickchanger/util.py#L5
class EmojiConverter(commands.EmojiConverter):
    async def convert(self, ctx, emoji):
        emoji = emoji.strip()
        try:
            EMOJI_DATA[emoji]
        except KeyError:
            return await super().convert(ctx, emoji)

        else:
            return emoji
        
def is_have_avatar(thing: Union[discord.Member, discord.Guild] = None):
    if not thing:
        return ""
    if isinstance(thing, discord.Member):
        try:
            return thing.avatar.url
        except AttributeError:
            return ""
    if isinstance(thing, discord.Guild):
        try:
            return thing.icon.url
        except AttributeError:
            return ""