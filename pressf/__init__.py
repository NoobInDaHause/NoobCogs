from redbot.core.bot import Red
from redbot.core.utils import get_end_user_data_statement

__red_end_user_data_statement__ = get_end_user_data_statement(__file__)

from .pressf import PressF

async def setup(bot: Red):
    cog = PressF(bot)
    await bot.add_cog(cog)
