import contextlib
import datetime
import discord
import logging
import noobutils as nu
import TagScriptEngine as tse

from redbot.core.bot import commands, Config, Red
from redbot.core.utils import chat_formatting as cf

from typing import Literal


class JoinDM(commands.Cog):
    """
    DM newly joined users from your guild with your set message.

    This cog uses TagScriptEngine and requires you basic tagscript knowledge to use this cog.
    """

    def __init__(self, bot: Red, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot

        default_guild = {"message": None, "toggled": False}
        self.config = Config.get_conf(
            self, identifier=947_123_432_421, force_registration=True
        )
        self.config.register_guild(**default_guild)
        self.log = logging.getLogger("red.NoobCogs.JoinDM")

    __version__ = "1.0.4"
    __author__ = ["NoobInDaHause"]
    __docs__ = "https://github.com/NoobInDaHause/NoobCogs/blob/red-3.5/joindm/README.md"

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
        This cog does not store any end user data whatsoever.
        """
        return await super().red_delete_data_for_user(
            requester=requester, user_id=user_id
        )

    async def dm_user(self, member: discord.Member, message: str):
        tagengine = tse.AsyncInterpreter(
            blocks=[
                tse.EmbedBlock(),
                tse.LooseVariableGetterBlock(),
                tse.StrictVariableGetterBlock(),
                tse.IfBlock(),
                tse.RandomBlock(),
                tse.FiftyFiftyBlock(),
                tse.AllBlock(),
                tse.AnyBlock(),
                tse.ReplaceBlock(),
            ]
        )
        proccessed = await tagengine.process(
            message=message,
            seed_variables={
                "member": tse.MemberAdapter(member),
                "guild": tse.GuildAdapter(member.guild),
            },
        )
        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                label=f"Sent from: {member.guild.name} ({member.guild.id}).",
                disabled=True,
                style=nu.get_button_colour("grey"),
            )
        )
        with contextlib.suppress(
            discord.errors.Forbidden, discord.errors.HTTPException
        ):
            await member.send(
                content=proccessed.body,
                embed=proccessed.actions.get("embed"),
                view=view,
            )

    @commands.Cog.listener("on_member_join")
    async def on_member_join(self, member: discord.Member):
        data = await self.config.guild(member.guild).all()
        if (
            not member.bot
            and member.guild is not None
            and data["message"] is not None
            and data["toggled"] is True
        ):
            await self.dm_user(member, data["message"])

    @commands.group(name="joindmset", aliases=["jdmset"])
    @commands.admin_or_permissions(manage_guild=True)
    @commands.bot_has_permissions(embed_links=True)
    async def joindmset(self, context: commands.Context):
        """
        Configure your joindm settings.
        """
        pass

    @joindmset.command(name="reset")
    async def joindmset_reset(self, context: commands.Context):
        """
        Reset your current joindm guild settings.
        """
        c_act = "Successfully reset your joindm guild settings."
        c_conf = "Are you sure you want to reset your joindm guild settings?"
        view = nu.NoobConfirmation()
        await view.start(context, c_act, content=c_conf)

        await view.wait()

        if view.value is True:
            await self.config.guild(context.guild).clear()

    @joindmset.command(name="resetcog")
    @commands.is_owner()
    async def joindmset_resetcog(self, context: commands.Context):
        """
        Reset the cogs whole configuration.
        """
        c_act = "Successfully reset the cogs config."
        c_conf = "Are you sure you want to reset the cogs config?"
        view = nu.NoobConfirmation()
        await view.start(context, c_act, content=c_conf)

        await view.wait()

        if view.value is True:
            await self.config.clear_all()

    @joindmset.command(name="message", aliases=["msg"])
    async def joindmset_message(
        self, context: commands.Context, *, message: str = None
    ):
        """
        Set the join dm message.

        Leave `message` blank to clear message.

        Available variables:
        {member} - Member block.
        {guild} - Guild block.

        Example:
        ` - ` Hello {member(mention)} ({member(id)})! Welcome to {guild} ({guild(id)})!
        """
        if not message:
            await self.config.guild(context.guild).message.clear()
            return await context.send(content="The joindm message has been cleared.")

        await self.config.guild(context.guild).message.set(message)
        await context.send(
            content=f"Successfully set your joindm message to: {cf.box(message, 'py')}"
        )

    @joindmset.command(name="toggle")
    async def joindmset_toggle(self, context: commands.Context):
        """
        Toggle the joindm on or off.
        """
        if not await self.config.guild(context.guild).message():
            return await context.send(
                content="Setup a joindm message first before turning the joindm on."
            )

        current = await self.config.guild(context.guild).toggled()
        await self.config.guild(context.guild).toggled.set(not current)
        status = "will not" if current else "will now"
        await context.send(content=f"I {status} DM newly joined users.")

    @joindmset.command(name="showsettings", aliases=["ss"])
    async def joindmset_showsettings(self, context: commands.Context):
        """
        Show the currently joindm guild settings.
        """
        data = await self.config.guild(context.guild).all()
        embed = discord.Embed(
            title=f"{context.guild}'s current guild settings",
            colour=await context.embed_colour(),
            timestamp=datetime.datetime.now(datetime.timezone.utc),
        )
        embed.set_thumbnail(url=nu.is_have_avatar(context.guild))
        embed.add_field(name="Toggled:", value=data["toggled"], inline=False)
        embed.add_field(
            name="Message:", value=cf.box(data["message"], "py"), inline=False
        )
        await context.send(embed=embed)
