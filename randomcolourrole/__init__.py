from redbot.core import bot, utils

from .randomcolourrole import RandomColourRole

__red_end_user_data_statement__ = utils.get_end_user_data_statement(__file__)


async def setup(bot: bot.Red):
    cog = RandomColourRole(bot)
    await bot.add_cog(cog)
