import noobutils as nu
import redbot.core.utils as utils

from .pressf import PressF

__red_end_user_data_statement__ = utils.get_end_user_data_statement(__file__)


async def setup(bot: nu.Red):
    nu.version_check("1.12.3")

    cog = PressF(bot)
    await bot.add_cog(cog)
