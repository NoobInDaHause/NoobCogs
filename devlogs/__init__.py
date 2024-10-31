import noobutils as nu
import redbot.core.utils as utils

from .devlogs import DevLogs

__red_end_user_data_statement__ = utils.get_end_user_data_statement_or_raise(__file__)


async def setup(bot: nu.Red) -> None:
    nu.version_check("1.11.9")

    if "Dev" not in bot.cogs:
        raise nu.CogLoadError(
            "This cog requires the bot to be started with the `--dev` flag."
        )

    cog = DevLogs(bot)
    await bot.add_cog(cog)
