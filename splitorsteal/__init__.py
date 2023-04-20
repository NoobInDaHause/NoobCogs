from redbot.core.bot import Red
from redbot.core.utils import get_end_user_data_statement

__red_end_user_data_statement__ = get_end_user_data_statement(__file__)

from .splitorsteal import SplitOrSteal

def setup(bot: Red):
    n = SplitOrSteal(bot)
    bot.add_cog(n)