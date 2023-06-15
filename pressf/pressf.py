import discord
import logging

from redbot.core import commands, Config, app_commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list

from typing import Literal, Optional

from .noobutils import EmojiConverter, get_button_colour
from .views import Confirmation, PressFView

class PressF(commands.Cog):
    """
    F.

    Press F to pay respect on something using buttons.
    """
    def __init__(self, bot: Red) -> None:
        self.bot = bot

        self.config = Config.get_conf(self, identifier=5434354373844151563453, force_registration=True)
        default_guild = {
            "emoji": "🇫",
            "buttoncolour": "blurple"
        }
        self.config.register_guild(**default_guild)
        self.log = logging.getLogger("red.NoobCogs.PressF")
        self.active_cache = []

    __version__ = "1.1.1"
    __author__ = ["NoobInDaHause"]
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
    @commands.bot_has_permissions(embed_links=True, use_external_emojis=True)
    @app_commands.guild_only()
    @app_commands.describe(thing="The thing that you want to pay respects to.")
    async def pressf(self, context: commands.Context, *, thing: str):
        """
        Pay respects on something.
        """
        if context.channel.id in self.active_cache:
            return await context.send(
                content="You are already paying respects on something in this channel, wait for it to finish."
            )
        self.active_cache.append(context.channel.id)
        e = await self.config.guild(context.guild).emoji()
        c = await self.config.guild(context.guild).buttoncolour()
        view = PressFView(self)
        view.press_f_button.emoji = e
        view.press_f_button.style = get_button_colour(c)
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
        colour: Optional[Literal["red", "green", "blurple", "grey"]]
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

    @pressfset.command(name="resetcog")
    @commands.is_owner()
    async def pressfset_resetcog(self, context: commands.Context):
        """
        Reset the cogs configuration.
        """
        conf_msg = "Are you sure you want to reset the cogs config?"
        conf_act = "Successfully reset the cogs config."
        view = Confirmation()
        await view.start(context=context, confirm_action=conf_act, confirmation_msg=conf_msg)
    
        await view.wait()

        if view.value == "yes":
            await self.config.clear_all()

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
            await self.config.guild(context.guild).clear()
