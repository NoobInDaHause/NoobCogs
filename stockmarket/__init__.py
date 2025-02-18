import noobutils as nu

from redbot.core import bank, utils

from .stockmarket import StockMarket

__red_end_user_data_statement__ = utils.get_end_user_data_statement_or_raise(__file__)


async def setup(bot: nu.Red):
    nu.version_check("1.12.3")

    if "Economy" not in bot.cogs:
        raise nu.CogLoadError("This cog requires Red's core Economy cog to be loaded.")
    if not await bank.is_global():
        raise nu.CogLoadError(
            "This cog requires the Economy cog to be set on Global.\n"
            "To change your economy to global use `[p]bankset toggleglobal`."
        )

    cog = StockMarket(bot)
    await bot.add_cog(cog)
