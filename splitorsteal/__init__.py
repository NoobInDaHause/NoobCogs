import noobutils as nu

from .splitorsteal import SplitOrSteal

__red_end_user_data_statement__ = nu.get_eud(__file__)


async def setup(bot: nu.Red):
    nu.version_check("1.13.2")

    await bot.add_cog(SplitOrSteal(bot=bot))
