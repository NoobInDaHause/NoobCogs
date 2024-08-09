import contextlib
import datetime
import discord
import noobutils as nu
import TagScriptEngine as tse
import traceback

from redbot.core.bot import commands, Red
from redbot.core.utils import chat_formatting as cf

from typing import Literal


DEFAULT_GLOBAL = {
    "error_msg": "`Error in command '{command}'. Check your console or logs for details.`"
}


class CustomError(nu.Cog):
    """
    Customize your bots error message.

    Red already has a core command that changes the error message but I made my own with customization.
    This cog uses TagScriptEngine so be sure you have knowledge in that.
    Credits to sitryk and phen for some of the code.
    """

    def __init__(self, bot: Red, *args, **kwargs):
        super().__init__(
            bot=bot,
            cog_name=self.__class__.__name__,
            version="1.2.3",
            authors=["NoobInDaHause"],
            use_config=True,
            identifier=9874825374237,
            force_registration=True,
            *args,
            **kwargs,
        )
        self.config.register_global(**DEFAULT_GLOBAL)
        self.old_error = self.bot.on_command_error
        bot.on_command_error = self.on_command_error

    async def red_delete_data_for_user(
        self,
        *,
        requester: Literal["discord_deleted_user", "owner", "user", "user_strict"],
        user_id: int,
    ):
        """
        This cog does not store any end user data whatsoever.
        """
        return await super().red_delete_data_for_user(
            requester=requester, user_id=user_id
        )

    # https://github.com/Sitryk/sitcogsv3/blob/e1d8d0f3524dfec17872379c12c0edcb9360948d/errorhandler/cog.py#L30
    # modified to work with tagscriptengine and my code
    async def on_command_error(
        self,
        ctx: commands.Context,
        error: commands.CommandError,
        unhandled_by_cog: bool = False,
    ):
        context = ctx
        tagengine = tse.AsyncInterpreter(
            blocks=[
                tse.EmbedBlock(),
                tse.LooseVariableGetterBlock(),
                tse.StrictVariableGetterBlock(),
                tse.IfBlock(),
                tse.RandomBlock(),
                tse.CommandBlock(),
                tse.FiftyFiftyBlock(),
                tse.AllBlock(),
                tse.AnyBlock(),
                tse.ReplaceBlock(),
                tse.AssignmentBlock(),
                tse.PythonBlock(),
            ]
        )
        if not isinstance(error, commands.CommandInvokeError):
            await self.old_error(context, error, unhandled_by_cog)
        else:
            to_convert = {
                "author": tse.MemberAdapter(context.author),
                "channel": tse.ChannelAdapter(context.message.channel),
                "prefix": tse.StringAdapter(context.prefix),
                "error": tse.StringAdapter(error),
                "command": tse.StringAdapter(context.command.qualified_name),
                "message_content": tse.StringAdapter(context.message.content),
                "message_id": tse.StringAdapter(context.message.id),
                "message_jump_url": tse.StringAdapter(context.message.jump_url),
            }
            if g := (getattr(context.author, "guild", None) or context.guild:
                to_convert["guild"] = tse.GuildAdapter(g)
            msg = await self.config.error_msg()
            processed = await tagengine.process(message=msg, seed_variables=to_convert)
            self.log.exception(
                msg=f"Exception in command '{context.command.qualified_name}'",
                exc_info=error.original,
            )
            exception_log = f"Exception in command '{context.command.qualified_name}'\n"
            exception_log += "".join(
                traceback.format_exception(type(error), error, error.__traceback__)
            )
            context.bot._last_exception = exception_log

            with contextlib.suppress(
                discord.errors.Forbidden, discord.errors.HTTPException
            ):
                await context.send(
                    content=processed.body,
                    embed=processed.actions.get("embed"),
                    allowed_mentions=discord.AllowedMentions(
                        users=True, roles=False, everyone=False
                    ),
                )

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
    async def customerror_message(
        self, context: commands.Context, *, message: str = None
    ):
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

        There is also:
        IfBlock, RandomBlock, CommandBlock, FiftyFiftyBlock, AllBlock, AnyBlock, ReplaceBlock
        """
        if not message:
            await self.config.error_msg.clear()
            return await context.send(content="The error message has been reset.")

        await self.config.error_msg.set(message)
        await context.send(
            content=f"The error message has been set to: {cf.box(message, 'py')}"
        )

    @customerror.command(name="plzerror")
    async def customerror_plzerror(self, context: commands.Context):
        """
        Test the bots error message.

        Bot owners only.
        """
        msg = await context.maybe_send_embed(
            message="Testing out error message please wait..."
        )
        await msg.delete(delay=1.5)
        raise NotImplementedError("This is a test error.")

    @customerror.command(name="reset")
    async def customerror_reset(self, context: commands.Context):
        """
        Reset the cogs settings.

        Bot owners only.
        """
        act = "Successfully reset the cogs settings."
        msg = "Are you sure you want to reset the cogs settings?"
        view = nu.NoobConfirmation()
        await view.start(context, act, content=msg)

        await view.wait()

        if view.value is True:
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
            description=cf.box(settings, "py"),
            colour=await context.embed_colour(),
            timestamp=datetime.datetime.now(datetime.timezone.utc),
        )
        await context.send(embed=embed)
