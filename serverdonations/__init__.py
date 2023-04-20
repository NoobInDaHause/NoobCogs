from redbot.core.bot import Red
from redbot.core.utils import get_end_user_data_statement

__red_end_user_data_statement__ = get_end_user_data_statement(__file__)

from .serverdonations import ServerDonations

def setup(bot: Red):
    n = ServerDonations(bot)
    bot.add_cog(n)