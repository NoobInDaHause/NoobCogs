import noobutils as nu

from .afk import Afk

__red_end_user_data_statement__ = nu.get_eud(__file__)


async def setup(bot: nu.Red):
    nu.version_check("1.13.0")

    cog = Afk(bot=bot)
    await bot.add_cog(cog)
