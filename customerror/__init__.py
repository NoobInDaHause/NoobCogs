import noobutils as nu

from redbot.core import bot, errors, utils

from .customerror import CustomError

__red_end_user_data_statement__ = utils.get_end_user_data_statement_or_raise(__file__)


async def setup(bot: bot.Red):
    if version_check_func := getattr(nu, "version_check", None):
        version_check_func("1.11.9")
    else:
        raise errors.CogLoadError(
            "Please update the noobutils to the latest version.\n"
            "`[p]pipinstall --force-reinstall --no-cache-dir "
            "git+https://github.com/NoobInDaHause/noobutils.git`\nAnd then restart your bot."
        )

    cog = CustomError(bot)
    await bot.add_cog(cog)
