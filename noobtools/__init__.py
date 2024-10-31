import noobutils as nu
import redbot.core.utils as utils

from .noobtools import NoobTools

__red_end_user_data_statement__ = utils.get_end_user_data_statement(__file__)

async def setup(bot: nu.Red):
    nu.version_check("1.11.9")

    cog = NoobTools(bot)
    await bot.add_cog(cog)
