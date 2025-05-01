import noobutils as nu

from .devlogs import DevLogs

__red_end_user_data_statement__ = nu.get_eud(__file__)


async def setup(bot: nu.Red) -> None:
    nu.version_check("1.13.0")

    if "Dev" not in bot.cogs:
        raise nu.CogLoadError(
            "This cog requires the bot to be started with the `--dev` flag."
        )

    cog = DevLogs(bot=bot)
    await bot.add_cog(cog)
