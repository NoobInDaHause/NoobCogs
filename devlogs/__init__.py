from redbot.core import bot, errors, utils

from .devlogs import DevLogs

__red_end_user_data_statement__ = utils.get_end_user_data_statement(__file__)

try:
    CogLoadError = errors.CogLoadError
except ImportError:
    CogLoadError = RuntimeError


async def setup(bot: bot.Red) -> None:
    if "Dev" not in bot.cogs:
        raise CogLoadError(
            "This cog requires the bot to be started with the `--dev` flag."
        )
    cog = DevLogs(bot)
    await bot.add_cog(cog)
