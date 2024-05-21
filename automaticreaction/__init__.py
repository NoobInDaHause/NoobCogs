from redbot.core import bot, utils

from .automaticreaction import AutomaticReaction

__red_end_user_data_statement__ = utils.get_end_user_data_statement_or_raise(__file__)


async def setup(bot: bot.Red):
    cog = AutomaticReaction(bot)
    await bot.add_cog(cog)
