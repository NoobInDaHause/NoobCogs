import asyncio
import contextlib
import datetime
import discord
import logging
import TagScriptEngine as tse
import traceback

from redbot.core import commands, Config
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list, box

from typing import Literal, Optional

from .views import Confirmation

class CustomError(commands.Cog):
    """
    Customize your bots error message.

    Red already has a core command that changes the error message but I made my own with customization.
    This cog uses TagScriptEngine so be sure you have knowledge in that.
    Credits to sitryk, cray and phen for some of the code.
    """
    def __init__(self, bot: Red):
        self.bot = bot

        self.config = Config.get_conf(self, identifier=9874825374237, force_registration=True)
        default_global = {
            "error_msg": "`Error in command '{command}'. Check your console or logs for details.`"
        }
        self.config.register_global(**default_global)
        self.log = logging.getLogger("red.NoobCogs.CustomError")
        self.old_error = self.bot.on_command_error
        
        bot.on_command_error = self.on_command_error

    __version__ = "1.1.5"
    __author__ = ["NoobInDaHause"]
    __docs__ = "https://github.com/NoobInDaHause/NoobCogs/blob/red-3.5/customerror/README.md"

    def format_help_for_context(self, context: commands.Context) -> str:
        """
        Thanks Sinbad and sravan!
        """
        p = "s" if len(self.__author__) != 1 else ""
        return f"""{super().format_help_for_context(context)}

        Cog Version: **{self.__version__}**
        Cog Author{p}: {humanize_list([f"**{auth}**" for auth in self.__author__])}
        Cog Documentation: [[Click here]]({self.__docs__})"""

    async def red_delete_data_for_user(
        self, *, requester: Literal['discord_deleted_user', 'owner', 'user', 'user_strict'], user_id: int
    ):
        """
        This cog does not store any end user data whatsoever.
        """
        return await super().red_delete_data_for_user(requester=requester, user_id=user_id)

    # https://github.com/Sitryk/sitcogsv3/blob/e1d8d0f3524dfec17872379c12c0edcb9360948d/errorhandler/cog.py#L30
    # modified to work with tagscriptengine and my code
    async def on_command_error(self, ctx: commands.Context, error, unhandled_by_cog = False):
        context = ctx
        tagengine = tse.AsyncInterpreter(
            blocks=[
                tse.EmbedBlock(), tse.LooseVariableGetterBlock(), tse.StrictVariableGetterBlock(),
                tse.IfBlock(), tse.RandomBlock(), tse.CommandBlock(), tse.RedirectBlock(), tse.FiftyFiftyBlock(),
                tse.AllBlock(), tse.AnyBlock(), tse.BlacklistBlock(), tse.ReplaceBlock()
            ]
        )
        if isinstance(error, commands.CommandInvokeError):
            self.log.exception(
                msg=f"Exception in command '{context.command.qualified_name}'", exc_info=error.original
            )
            exception_log = f"Exception in command '{context.command.qualified_name}'\n"
            exception_log += "".join(
                traceback.format_exception(type(error), error, error.__traceback__)
            )
            context.bot._last_exception = exception_log

            cog = context.bot.get_cog("CustomError")
            msg = await cog.config.error_msg()
            processed = await tagengine.process(
                message=msg,
                seed_variables={
                    "author": tse.MemberAdapter(context.author),
                    "guild": tse.GuildAdapter(context.author.guild),
                    "channel": tse.ChannelAdapter(context.message.channel),
                    "prefix": tse.StringAdapter(context.prefix),
                    "error": tse.StringAdapter(error),
                    "command": tse.StringAdapter(context.command.qualified_name),
                    "message_content": tse.StringAdapter(context.message.content),
                    "message_id": tse.StringAdapter(context.message.id),
                    "message_jump_url": tse.StringAdapter(context.message.jump_url)
                }
            )
            with contextlib.suppress(discord.errors.Forbidden, discord.errors.HTTPException):
                await context.send(
                    content=processed.body,
                    embed=processed.actions.get("embed"),
                    allowed_mentions=discord.AllowedMentions(users=True, roles=False, everyone=False)
                )
            return

        await self.old_error(context, error, unhandled_by_cog)

    async def cog_unload(self):
        self.bot.on_command_error = self.old_error

    @commands.group(name="customerror")
    @commands.is_owner()
    async def customerror(self, context: commands.Context):
        """
        Base commands for customizing the bots error message.

        Bot owners only.
        """
        pass

    @customerror.command(name="message")
    async def customerror_message(self, context: commands.Context, *, message: Optional[str]):
        """
        Customize [botname]'s error message.

        Bot owners only.
        Be sure that you have TagScriptEgnine knowledge.
        Available variables:
        {author} - The command invoker.
        {author(id)} - The command invokers ID.
        {author(mention)} - Mention the command invoker.
        {guild} - The guild.
        {guild(id)} - The guilds ID.
        {channel} - The channel.
        {channel(id)} - The channel ID.
        {channel(mention)} - Mention the channel.
        {prefix} - The prefix used.
        {error} - The raised command error.
        {command} - The command name.
        {message_content} - The message content.
        {message_id} - The message ID.
        {message_jump_url} - The message jump url.
        """
        if not message:
            await self.config.error_msg.clear()
            return await context.send(content="The error message has been reset.")

        await self.config.error_msg.set(message)
        await context.send(content=f"The error message has been set to: {box(message, 'py')}")

    @customerror.command(name="plzerror")
    async def customerror_plzerror(self, context: commands.Context):
        """
        Test the bots error message.

        Bot owners only.
        """
        msg = await context.maybe_send_embed(message="Testing out error message please wait...")
        await asyncio.sleep(1.0)
        await msg.delete()
        await asyncio.sleep(0.5)
        raise NotImplementedError("This is a test error.")

    @customerror.command(name="reset")
    async def customerror_reset(self, context: commands.Context):
        """
        Reset the cogs settings.

        Bot owners only.
        """
        act = "Successfully reset the cogs settings."
        msg = "Are you sure you want to reset the cogs settings?"
        view = Confirmation()
        await view.start(context, confirm_action=act, confirmation_msg=msg)

        await view.wait()

        if view.value == "yes":
            await self.config.clear_all()

    @customerror.command(name="showsettings", aliases=["ss"])
    async def customerror_showsettings(self, context: commands.Context):
        """
        See your current settings for the CustomError cog.

        Bot owners only.
        """
        settings = await self.config.error_msg()
        embed = discord.Embed(
            title="Current error message",
            description=box(settings, "py"),
            colour=await context.embed_colour(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        await context.send(embed=embed)
