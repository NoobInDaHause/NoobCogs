import contextlib
import datetime
import noobutils as nu
import TagScriptEngine as tse
import typing as t


DEFAULT_GUILD = {"message": None, "toggled": False}


class JoinDM(nu.Cog):
    """
    DM newly joined users from your guild with your set message.

    This cog uses TagScriptEngine and requires you to know basic tagscript knowledge to use this cog.
    """

    def __init__(self, bot: nu.Red, *args, **kwargs):
        super().__init__(
            bot=bot,
            cog_name=self.__class__.__name__,
            version="1.1.3",
            authors=["NoobInDaHause"],
            use_config=True,
            identifier=947_123_432_421,
            force_registration=True,
            *args,
            **kwargs,
        )
        self.config.register_guild(**DEFAULT_GUILD)
        self.tagengine = tse.AsyncInterpreter(
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
                tse.AssignmentBlock(),
                tse.PythonBlock(),
            ]
        )

    async def red_delete_data_for_user(
        self,
        *,
        requester: t.Literal["discord_deleted_user", "owner", "user", "user_strict"],
        user_id: int,
    ):
        """
        This cog does not store any end user data whatsoever.
        """
        return await super().red_delete_data_for_user(
            requester=requester, user_id=user_id
        )

    async def dm_user(self, member: nu.discord.Member, message: str):
        proccessed = await self.tagengine.process(
            message=message,
            seed_variables={
                "member": tse.MemberAdapter(member),
                "guild": tse.GuildAdapter(member.guild),
            },
        )
        with contextlib.suppress(
            nu.discord.errors.Forbidden, nu.discord.errors.HTTPException
        ):
            await member.send(
                content=proccessed.body,
                embed=proccessed.actions.get("embed"),
                view=nu.discord.ui.View().add_item(
                    nu.discord.ui.Button(
                        label=f"Sent from: {member.guild.name} ({member.guild.id}).",
                        disabled=True,
                        style=nu.get_button_colour("grey"),
                    )
                ),
            )

    @nu.listener("on_member_join")
    async def dm_on_join(self, member: nu.discord.Member):
        data = await self.config.guild(member.guild).all()
        if (
            not member.bot
            and member.guild is not None
            and data["message"] is not None
            and data["toggled"] is True
        ):
            await self.dm_user(member, data["message"])

    @nu.group(name="joindmset", aliases=["jdmset"])
    @nu.commands.admin_or_permissions(manage_guild=True)
    @nu.commands.bot_has_permissions(embed_links=True)
    async def joindmset(self, context: nu.commands.Context):
        """
        Configure your joindm settings.
        """
        pass

    @joindmset.command(name="reset")
    async def joindmset_reset(self, context: nu.commands.Context):
        """
        Reset your current joindm guild settings.
        """
        c_act = "Successfully reset your joindm guild settings."
        c_conf = "Are you sure you want to reset your joindm guild settings?"

        view = nu.NoobConfirmation(obj=context, confirm_action=c_act)
        await view.start(content=c_conf)

        await view.wait()

        if view.value is True:
            await self.config.guild(context.guild).clear()

    @joindmset.command(name="resetcog")
    @nu.commands.is_owner()
    async def joindmset_resetcog(self, context: nu.commands.Context):
        """
        Reset the cogs whole configuration.
        """
        c_act = "Successfully reset the cogs config."
        c_conf = "Are you sure you want to reset the cogs config?"

        view = nu.NoobConfirmation(obj=context, confirm_action=c_act)
        await view.start(content=c_conf)

        await view.wait()

        if view.value is True:
            await self.config.clear_all()

    @joindmset.command(name="message", aliases=["msg"])
    async def joindmset_message(
        self, context: nu.commands.Context, *, message: str = None
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
            content=f"Successfully set your joindm message to: {nu.cf.box(message, 'py')}"
        )

    @joindmset.command(name="toggle")
    async def joindmset_toggle(self, context: nu.commands.Context):
        """
        Toggle the joindm on or off.
        """
        current = await self.config.guild(context.guild).toggled()
        await self.config.guild(context.guild).toggled.set(not current)
        status = "will not" if current else "will now"
        await context.send(content=f"I {status} DM newly joined users.")

    @joindmset.command(name="showsettings", aliases=["ss"])
    async def joindmset_showsettings(self, context: nu.commands.Context):
        """
        Show the currently joindm guild settings.
        """
        data = await self.config.guild(context.guild).all()
        embed = nu.discord.Embed(
            title=f"{context.guild}'s current guild settings",
            colour=await context.embed_colour(),
            timestamp=datetime.datetime.now(datetime.timezone.utc),
        )
        embed.set_thumbnail(url=nu.is_have_avatar(context.guild))
        embed.add_field(name="Toggled:", value=data["toggled"], inline=False)
        embed.add_field(
            name="Message:", value=nu.cf.box(data["message"], "py"), inline=False
        )
        await context.send(embed=embed)
