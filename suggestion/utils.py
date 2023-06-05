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
        
def is_have_avatar(thing: Union[discord.Member, discord.Guild] = None) -> str:
    if not thing:
        return ""
    if isinstance(thing, discord.Member):
        try:
            return thing.avatar.url
        except AttributeError:
            return thing.display_avatar.url
    if isinstance(thing, discord.Guild):
        try:
            return thing.icon.url
        except AttributeError:
            return ""

def access_denied() -> str:
    return "https://cdn.discordapp.com/attachments/1000751975308197918/1110013262835228814/1.mp4"