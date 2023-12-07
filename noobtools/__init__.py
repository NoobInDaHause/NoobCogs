from redbot.core import bot, utils

__red_end_user_data_statement__ = utils.get_end_user_data_statement(__file__)

from .noobtools import NoobTools

async def setup(bot: bot.Red):
    cog = NoobTools(bot)
    await bot.add_cog(cog)
