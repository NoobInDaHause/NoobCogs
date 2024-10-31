import noobutils as nu
import redbot.core.utils as utils

from .joindm import JoinDM

__red_end_user_data_statement__ = utils.get_end_user_data_statement(__file__)


async def setup(bot: nu.Red):
    nu.version_check("1.11.9")

    cog = JoinDM(bot)
    await bot.add_cog(cog)
