from redbot.core.bot import Red
from redbot.core.utils import get_end_user_data_statement

__red_end_user_data_statement__ = get_end_user_data_statement(__file__)

from .globalban import GlobalBan

async def setup(bot: Red):
    cog = GlobalBan(bot)
    await cog.cog_load()
    await bot.add_cog(cog)