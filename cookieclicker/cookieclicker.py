import discord
import logging
import noobutils as nu

from redbot.core.bot import app_commands, commands, Config, Red
from redbot.core.utils import chat_formatting as cf

from typing import Literal, Optional

from .views import CookieClickerView


class CookieClicker(commands.Cog):
    """
    Play a cookie clicker.

    Anti stress 100%.
    """

    def __init__(self, bot: Red) -> None:
        self.bot = bot

        self.config = Config.get_conf(
            self, identifier=348468464655768, force_registration=True
        )
        default_guild = {"emoji": "🍪", "buttoncolour": "blurple"}
        self.config.register_guild(**default_guild)
        self.log = logging.getLogger("red.NoobCogs.PressF")

    __version__ = "1.0.4"
    __author__ = ["NoobInDaHause"]
    __docs__ = (
        "https://github.com/NoobInDaHause/NoobCogs/blob/red-3.5/cookieclicker/README.md"
    )

    def format_help_for_context(self, context: commands.Context) -> str:
        """
        Thanks Sinbad and sravan!
        """
        plural = "s" if len(self.__author__) > 1 else ""
        return f"""{super().format_help_for_context(context)}

        Cog Version: **{self.__version__}**
        Cog Author{plural}: {cf.humanize_list([f'**{auth}**' for auth in self.__author__])}
        Cog Documentation: [[Click here]]({self.__docs__})"""

    async def red_delete_data_for_user(
        self,
        *,
        requester: Literal["discord_deleted_user", "owner", "user", "user_strict"],
        user_id: int,
    ):
        """
        No EUD to delete.
        """
        return await super().red_delete_data_for_user(
            requester=requester, user_id=user_id
        )

    @commands.hybrid_command(name="cookieclicker")
    @commands.bot_has_permissions(embed_links=True)
    @commands.guild_only()
    @app_commands.guild_only()
    async def cookieclicker(self, context: commands.Context):
        """
        Cookie clicker.

        Anti stress guaranteed.
        """
        e = await self.config.guild(context.guild).emoji()
        c = await self.config.guild(context.guild).buttoncolour()
        view = CookieClickerView()
        view.cookieclicker.emoji = e
        view.cookieclicker.style = nu.get_button_colour(c)
        await view.start(context)

    @commands.group(name="cookieclickerset", aliases=["ccset"])
    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    @commands.bot_has_permissions(use_external_emojis=True)
    async def cookieclickerset(self, context: commands.Context):
        """
        Configure the cogs settings.
        """
        pass

    @cookieclickerset.command(name="emoji")
    async def cookieclickerset_emoji(
        self, context: commands.Context, emoji: Optional[nu.NoobEmojiConverter]
    ):
        """
        Change the cookie emoji.

        Leave `emoji` blank to see current set emoji.
        """
        if not emoji:
            e = await self.config.guild(context.guild).emoji()
            return await context.send(
                content=f"The current CookieClicker emoji is {e}."
            )
        await self.config.guild(context.guild).emoji.set(str(emoji))
        await context.send(
            content=f"The new CookieClicker emoji has been set to {emoji}."
        )

    @cookieclickerset.command(name="buttoncolour", aliases=["buttoncolor"])
    async def cookieclickerset_buttoncolour(
        self,
        context: commands.Context,
        colour: Optional[Literal["red", "green", "blurple", "grey"]],
    ):
        """
        Change the CookieClicker button colour.

        Leave `colour` blank to see current set colour.
        """
        if not colour:
            c = await self.config.guild(context.guild).buttoncolour()
            return await context.send(
                content=f"The current CookieClicker button colour is {c}"
            )
        await self.config.guild(context.guild).buttoncolour.set(colour)
        await context.send(
            content=f"The new CookieClicker button colour has been set to {colour}."
        )

    @cookieclickerset.command(name="reset")
    async def cookieclickerset_reset(self, context: commands.Context):
        """
        Reset the CookieClicker current guild settings to default.
        """
        confirmation_msg = "Are you sure you want to reset the current guild settings?"
        confirm_action = "Successfully reset the guilds settings."
        view = nu.NoobConfirmation()
        await view.start(context, confirm_action, content=confirmation_msg)

        await view.wait()

        if view.value is True:
            await self.config.clear_all()
