from redbot.core import bot, utils

from .suggestions import Suggestions

__red_end_user_data_statement__ = utils.get_end_user_data_statement(__file__)


async def setup(bot: bot.Red):
    cog = Suggestions(bot)
    await bot.add_cog(cog)
