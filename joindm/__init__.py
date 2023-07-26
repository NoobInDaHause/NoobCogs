from redbot.core import bot, utils

from .joindm import JoinDM

__red_end_user_data_statement__ = utils.get_end_user_data_statement(__file__)

async def setup(bot: bot.Red):
    cog = JoinDM(bot)
    await bot.add_cog(cog)
