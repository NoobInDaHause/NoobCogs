import asyncio
import contextlib
import noobutils as nu
import random

from typing import Literal


DEFAULT_GUILD = {"role": None, "status": False}


class RandomColourRole(nu.Cog):
    """
    Have a role that changes colour every 5 minutes.

    May or may not be API intense but the cog is cool.
    Due to API rate limits you can only have 1 randomcolourrole per guild.
    The role colour changes every 5 minutes or so depending on how many guilds the bot is in.
    """

    def __init__(self, bot: nu.Red, *args, **kwargs):
        super().__init__(
            bot=bot,
            cog_name=self.__class__.__name__,
            version="1.2.2",
            authors=["NoobInDaHause"],
            use_config=True,
            identifier=128943761874,
            force_registration=True,
            *args,
            **kwargs,
        )
        self.config.register_guild(**DEFAULT_GUILD)

    async def red_delete_data_for_user(
        self,
        *,
        requester: Literal["discord_deleted_user", "owner", "user", "user_strict"],
        user_id: int,
    ) -> None:
        """
        This cog does not store any end user data whatsoever.
        """
        return await super().red_delete_data_for_user(
            requester=requester, user_id=user_id
        )

    async def cog_load(self):
        self.log.info("Random Colour Role task started.")
        self.change_random_colour_role.start()

    async def cog_unload(self):
        self.log.info("Random Color Role task cancelled.")
        await self.change_random_colour_role.cancel()

    @nu.discord.ext.tasks.loop(minutes=5)
    async def change_random_colour_role(self):
        for k, v in ((await self.config.all_guilds()).copy()).items():
            await asyncio.sleep(2.5)
            if guild := self.bot.get_guild(k):
                if v["status"] and v["role"]:
                    with contextlib.suppress(Exception):
                        await guild.get_role(v["role"]).edit(
                            colour=random.randint(0, 0xFFFFFF),
                            reason="Random Colour Role.",
                        )

    @change_random_colour_role.before_loop
    async def change_random_colour_role_before_loop(self):
        await self.bot.wait_until_red_ready()

    @nu.commands.group(
        name="randomcolourroleset", aliases=["rcrset", "randomcolorroleset"]
    )
    @nu.commands.guild_only()
    @nu.commands.has_permissions(manage_guild=True)
    async def randomcolourroleset(self, context: nu.commands.Context):
        """
        Settings for the RandomColourRole cog.
        """
        pass

    @randomcolourroleset.command(name="reset")
    async def randomcolourroleset_reset(self, context: nu.commands.Context):
        """
        Reset the RandomColourRoles guild settings.
        """
        act = "Successfully resetted the guilds randomcolourrole settings."
        conf = "Are you sure you want to reset the guilds randomcolourrole settings?"

        view = nu.NoobConfirmation(obj=context, confirm_action=act)
        await view.start(content=conf)

        await view.wait()

        if view.value is True:
            await self.config.guild(context.guild).clear()

    @randomcolourroleset.command(name="resetcog")
    @nu.commands.is_owner()
    async def randomcolourroleset_resetcog(self, context: nu.commands.Context):
        """
        Reset the RandomColourRole cogs whole config. (Bot owners only)
        """
        act = "Successfully resetted the randomcolourrole cogs config."
        conf = "Are you sure you want to reset the randomcolourrole cogs whole config?"

        view = nu.NoobConfirmation(obj=context, confirm_action=act)
        await view.start(content=conf)

        await view.wait()

        if view.value is True:
            await self.config.clear_all()
            await self.config.clear_all_guilds()

    @randomcolourroleset.command(name="role")
    @nu.commands.bot_has_permissions(manage_roles=True)
    async def randomcolourroleset_role(
        self, context: nu.commands.Context, role: nu.discord.Role = None
    ):
        """
        Set the guilds random colour role.
        """
        if not role:
            await self.config.guild(context.guild).role.set(None)
            return await context.send(content="The role has been cleared.")

        if role >= context.guild.me.top_role:
            return await context.send(
                content="It appears that role is higher than my top role please lower it below my top role."
            )

        await self.config.guild(context.guild).role.set(role.id)
        await context.send(
            content=f"**{role.name}** has been set as the guilds randomcolourrole. "
            f"Start the cog with `{context.prefix}rcrset status` if you haven't already."
        )

    @randomcolourroleset.command(name="status")
    @nu.commands.bot_has_permissions(manage_roles=True)
    async def randomcolourroleset_status(self, context: nu.commands.Context, state: bool):
        """
        Toggle whether to enable or disable the RandomColourRole.
        """
        await self.config.guild(context.guild).status.set(state)
        status = "enabled" if state else "disabled"
        await context.send(content=f"The randomcolourrole has been {status}.")

    @randomcolourroleset.command(name="showsettings", aliases=["ss"])
    async def randomcolourroleset_showsettings(self, context: nu.commands.Context):
        """
        See the current guild settings for the RandomColourRole.
        """
        settings = await self.config.guild(context.guild).all()
        role = context.guild.get_role(settings["role"])
        embed = nu.discord.Embed(
            title=f"Current RandomColourRole guild settings for {context.guild}",
            colour=await context.embed_colour(),
            timestamp=nu.discord.utils.utcnow(),
        )
        embed.add_field(
            name="Role:", value=role.mention if role else "None", inline=False
        )
        embed.add_field(name="Status:", value=settings["status"], inline=False)

        warns = ""
        if not context.guild.me.guild_permissions.manage_roles:
            warns += "I do not have `manage_roles` permission! RandomColourRole will not work.\n"
        if role and role >= context.guild.me.top_role:
            warns += "The set role is higher than my top role! please lower it down below my top role."

        if warns:
            embed.add_field(name="⚠️ Warning", value=warns, inline=False)
        await context.send(embed=embed)
