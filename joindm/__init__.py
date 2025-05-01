import noobutils as nu

from .joindm import JoinDM

__red_end_user_data_statement__ = nu.get_eud(__file__)


async def setup(bot: nu.Red):
    nu.version_check("1.13.0")

    await bot.add_cog(JoinDM(bot=bot))
