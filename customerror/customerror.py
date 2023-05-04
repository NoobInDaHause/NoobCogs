import datetime
import discord
import logging
import traceback

from redbot.core import commands, app_commands, Config
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list, box

from typing import Literal, Optional

class CustomError(commands.Cog):
    """
    Customize your bots error message.
    
    Red already has a core command that changes the error message but the customization is limited so I made my own.
    This cog requires the Dev cog enabled, start your bot with `--dev` flag to enable the cog.
    Credits to sitryk for some of the code.
    """
    def __init__(self, bot: Red):
        self.bot = bot
        
        self.config = Config.get_conf(self, identifier=9874825374237, force_registration=True)
        default_msg = """await ctx.send(f"`Error in command '{ctx.command.qualified_name}'. Check your console or logs for details.`")"""
        default_global = {
            "error_msg": default_msg
        }
        self.config.register_global(**default_global)
        self.log = logging.getLogger("red.NoobCogs.CustomError")
        self.old_error = self.bot.on_command_error
        
        bot.on_command_error = self.on_command_error
        
    __version__ = "1.0.2"
    __author__ = ["Noobindahause#2808"]
    
    def format_help_for_context(self, context: commands.Context) -> str:
        """
        Thanks Sinbad and sravan!
        """
        plural = "s" if len(self.__author__) != 1 else ""
        return f"{super().format_help_for_context(context)}\n\nCog Version: {self.__version__}\nCog Author{plural}: {humanize_list(self.__author__)}"
    
    async def red_delete_data_for_user(self, *, requester: Literal['discord_deleted_user', 'owner', 'user', 'user_strict'], user_id: int):
        """
        This cog does not store any end user data whatsoever.
        """
        return await super().red_delete_data_for_user(requester=requester, user_id=user_id)
    
    # https://github.com/Sitryk/sitcogsv3/blob/e1d8d0f3524dfec17872379c12c0edcb9360948d/errorhandler/cog.py#L30
    async def on_command_error(self, ctx: commands.Context, error, unhandled_by_cog = False):
        if isinstance(error, commands.CommandInvokeError):
            self.log.exception("Exception in command '{ctx.command.qualified_name}'", exc_info=error.original)
            exception_log = f"Exception in command '{ctx.command.qualified_name}'\n"
            exception_log += "".join(
                traceback.format_exception(type(error), error, error.__traceback__)
            )
            ctx.bot._last_exception = exception_log
            
            ce = ctx.bot.get_cog("CustomError")
            cmd = ctx.bot.get_command("eval")
            error_msg = await ce.config.error_msg()
            return await ctx.invoke(cmd, body=error_msg)
        
        await self.old_error(ctx, error, unhandled_by_cog)
    
    async def cog_unload(self):
        self.bot.on_command_error = self.old_error
    
    @commands.hybrid_group(name="customerror")
    @commands.is_owner()
    async def customerror(self, context: commands.Context):
        """
        Base commands for customizing the bots error message. (Bot owners only)
        """
        
    @customerror.command(name="message")
    @commands.is_owner()
    @app_commands.describe(
        message="The custom error message."
    )
    async def customerror_message(self, context: commands.Context, *, message: Optional[str]):
        """
        Customize [botname]'s error message. (Bot owners only)
        
        Requires knowledge of python and discord.py.
        And the dev cog loaded.

        See `[p]help eval` to check all the available variables.
        """
        cmd = self.bot.get_command('eval')
        if not cmd:
            return await context.reply(content="The dev cog isn't loaded, load it when you start the bot with the `--dev` flag.")
        
        if not message:
            await self.config.error_msg.clear()
            return await context.reply(content="The error message has been reset.", ephemeral=True, mention_author=False)
        
        await self.config.error_msg.set(message)
        await context.reply(content=f"The error message has been set to: {box(message, 'py')}", ephemeral=True, mention_author=False)
        
    @customerror.command(name="plzerror")
    @commands.is_owner()
    async def customerror_plzerror(self, context: commands.Context):
        """
        Test the bots error message. (Bot owners only)
        """
        cmd = self.bot.get_command('eval')
        if not cmd:
            return await context.reply(content="The dev cog isn't loaded, load it when you start the bot with the `--dev` flag.")
        
        raise NotImplementedError("plzerror")
    
    @customerror.command(name="showsettings", aliases=["ss"])
    @commands.is_owner()
    async def customerror_showsettings(self, context: commands.Context):
        """
        See your current settings for the CustomError cog. (Bot owners only)
        """
        cmd = self.bot.get_command('eval')
        if not cmd:
            return await context.reply(content="The dev cog isn't loaded, load it when you start the bot with the `--dev` flag.")
        
        settings = await self.config.error_msg()
        embed = discord.Embed(
            title="Current error message",
            description=box(settings, "py"),
            colour=await context.embed_colour(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        await context.send(embed=embed)