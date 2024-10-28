import noobutils as nu

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

    if version_check_func := getattr(nu, "version_check", None):
        version_check_func("1.11.9")
    else:
        raise errors.CogLoadError(
            "Please update the noobutils to the latest version.\n"
            "`[p]pipinstall --force-reinstall --no-cache-dir "
            "git+https://github.com/NoobInDaHause/noobutils.git`\nAnd then restart your bot."
        )

    cog = DevLogs(bot)
    await bot.add_cog(cog)
