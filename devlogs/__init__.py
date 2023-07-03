from redbot.core import bot, errors, utils

from .devlogs import DevLogs

__red_end_user_data_statement__ = utils.get_end_user_data_statement(__file__)

async def setup(bot: bot.Red) -> None:
    if "Dev" not in bot.cogs:
        raise errors.CogLoadError(
            "This cog requires the bot to be started with the `--dev` flag."
        )
    cog = DevLogs(bot)
    await bot.add_cog(cog)
