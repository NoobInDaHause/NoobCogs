from discord.ext.commands.converter import EmojiConverter as ec
from emoji import EMOJI_DATA

# https://github.com/i-am-zaidali/cray-cogs/blob/cdeef241b7b40f20313645a2a3cbe91ca12423f2/tickchanger/util.py#L5
class EmojiConverter(ec):
    """
    Credits to cray for this code.
    """
    async def convert(self, ctx, argument):
        argument = argument.strip()
        try:
            EMOJI_DATA[argument]
        except KeyError:
            return await super().convert(ctx, argument)

        else:
            return argument