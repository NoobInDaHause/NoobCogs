import discord
import logging

from redbot.core import commands, Config, app_commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list

from typing import Literal, Optional

from .utils import EmojiConverter
from .views import Confirmation, PressFView

class PressF(commands.Cog):
    def __init__(self, bot: Red) -> None:
        self.bot = bot

        self.config = Config.get_conf(self, identifier=5434354373844151563453, force_registration=True)
        default_guild = {
            "emoji": "🇫",
            "buttoncolour": "blurple"
        }
        self.config.register_guild(**default_guild)
        self.log = logging.getLogger("red.NoobCogs.PressF")

    __version__ = "1.0.0"
    __author__ = ["Noobindahause#2808"]
    __docs__ = "https://github.com/NoobInDaHause/NoobCogs/blob/red-3.5/pressf/README.md"

    def format_help_for_context(self, context: commands.Context) -> str:
        """
        Thanks Sinbad and sravan!
        """
        plural = "s" if len(self.__author__) != 0 or 1 else ""
        return f"""{super().format_help_for_context(context)}

        Cog Version: **{self.__version__}**
        Cog Author{plural}: {humanize_list([f'**{auth}**' for auth in self.__author__])}
        Cog Documentation: [[Click here]]({self.__docs__})"""

    async def red_delete_data_for_user(
        self, *, requester: Literal['discord_deleted_user', 'owner', 'user', 'user_strict'], user_id: int
    ):
        """
        No EUD to delete.
        """
        return await super().red_delete_data_for_user(requester=requester, user_id=user_id)

    @commands.hybrid_command(name="pressf")
    @commands.guild_only()
    @commands.cooldown(1, 60, commands.BucketType.channel)
    @commands.bot_has_permissions(embed_links=True, use_external_emojis=True)
    @app_commands.guild_only()
    @app_commands.describe(
        thing="The thing that you want to pay respects to."
    )
    async def pressf(self, context: commands.Context, *, thing: Optional[str]):
        """
        Pay respects on something.
        """
        if not thing:
            context.command.reset_cooldown(context)
            return await context.send_help()
        e = await self.config.guild(context.guild).emoji()
        c = await self.config.guild(context.guild).buttoncolour()
        view = PressFView()
        view.press_f_button.emoji = e
        view.press_f_button.style = (
            discord.ButtonStyle.red
            if c == "red"
            else discord.ButtonStyle.green
            if c == "green"
            else discord.ButtonStyle.blurple
            if c == "blurple"
            else discord.ButtonStyle.grey
        )
        await view.start(context, thing)

    @commands.group(name="pressfset")
    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    @commands.bot_has_permissions(use_external_emojis=True)
    async def pressfset(self, context: commands.Context):
        """
        Configure the cogs settings.
        """
        pass

    @pressfset.command(name="emoji")
    async def pressfset_emoji(self, context: commands.Context, emoji: Optional[EmojiConverter]):
        """
        Change the F emoji.

        Leave `emoji` blank to see current set emoji.
        """
        if not emoji:
            e = await self.config.guild(context.guild).emoji()
            return await context.send(content=f"The current Press F emoji is {e}.")
        await self.config.guild(context.guild).emoji.set(str(emoji))
        await context.send(content=f"The new Press F emoji has been set to {emoji}.")

    @pressfset.command(name="buttoncolour", aliases=["buttoncolor"])
    async def pressfset_buttoncolour(
        self,
        context: commands.Context,
        colour: Literal["red", "green", "blurple", "grey"]
    ):
        """
        Change the Press F button colour.

        Leave `colour` blank to see current set colour.
        """
        if not colour:
            c = await self.config.guild(context.guild).buttoncolour()
            return await context.send(content=f"The current Press F button colour is {c}")
        await self.config.guild(context.guild).buttoncolour.set(colour)
        await context.send(content=f"The new Press F button colour has been set to {colour}.")

    @pressfset.command(name="reset")
    async def pressfset_reset(self, context: commands.Context):
        """
        Reset the Press F current guild settings to default.
        """
        confirmation_msg = "Are you sure you want to reset the current guild settings?"
        confirm_action = "Successfully reset the guilds settings."
        view = Confirmation()
        await view.start(context=context, confirm_action=confirm_action, confirmation_msg=confirmation_msg)

        await view.wait()

        if view.value == "yes":
            await self.config.clear_all()
