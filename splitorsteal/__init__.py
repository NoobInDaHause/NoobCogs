import noobutils as nu

from redbot.core import bot, utils

from .splitorsteal import SplitOrSteal

__red_end_user_data_statement__ = utils.get_end_user_data_statement(__file__)


async def setup(bot: bot.Red):
    nu.version_check("1.12.3")

    cog = SplitOrSteal(bot)
    await bot.add_cog(cog)
