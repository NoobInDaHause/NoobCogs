from redbot.core.bot import Red
from redbot.core.utils import get_end_user_data_statement

__red_end_user_data_statement__ = get_end_user_data_statement(__file__)

from .suggestion import Suggestion

async def setup(bot: Red):
    cog = Suggestion(bot)
    await bot.add_cog(cog)
    await cog.initialize()
