import noobutils as nu
import redbot.core.utils as utils

from .randomcolourrole import RandomColourRole

__red_end_user_data_statement__ = utils.get_end_user_data_statement(__file__)


async def setup(bot: nu.Red):
    nu.version_check("1.11.9")

    cog = RandomColourRole(bot)
    await bot.add_cog(cog)
