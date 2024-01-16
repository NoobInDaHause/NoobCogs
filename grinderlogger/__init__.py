from redbot.core import bot, utils

__red_end_user_data_statement__ = utils.get_end_user_data_statement_or_raise(__file__)

from .grinderlogger import GrinderLogger


async def setup(bot: bot.Red):
    cog = GrinderLogger(bot)
    await bot.add_cog(cog)
