from redbot.core import commands

from emoji import EMOJI_DATA

# https://github.com/i-am-zaidali/cray-cogs/blob/cdeef241b7b40f20313645a2a3cbe91ca12423f2/tickchanger/util.py#L5
class EmojiConverter(commands.EmojiConverter):
    async def convert(self, context, emoji: str):
        emoji = emoji.strip()
        try:
            EMOJI_DATA[emoji]
        except KeyError:
            return await super().convert(context, emoji)
        else:
            return emoji
