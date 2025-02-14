import noobutils as nu

from redbot.core import bot, utils

from .serverdonations import ServerDonations

__red_end_user_data_statement__ = utils.get_end_user_data_statement_or_raise(__file__)


async def setup(bot: bot.Red):
    nu.version_check("1.12.3")

    cog = ServerDonations(bot)
    await bot.add_cog(cog)
