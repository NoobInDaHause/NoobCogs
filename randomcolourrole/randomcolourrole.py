import asyncio
import datetime
import discord
import logging
import random

from redbot.core import bot, commands, Config
from redbot.core.utils.chat_formatting import humanize_list

from discord.ext import tasks
from typing import Literal, Optional

from .views import Confirmation

class RandomColourRole(commands.Cog):
    """
    Have a role that changes colour every 5 minutes.

    May or may not be API intense but the cog is cool.
    Due to API rate limits you can only have 1 randomcolourrole pre guild.
    The role colour changes every 20 minutes or so depending on how many guilds the bot is in.
    """
    def __init__(self, bot: bot.Red, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot

        self.config = Config.get_conf(self, identifier=128943761874, force_registration=True)
        default_guild = {
            "role": None,
            "status": False
        }
        self.config.register_guild(**default_guild)
        self.log = logging.getLogger("red.NoobCogs.RandomColourRole")

    __version__ = "1.1.1"
    __author__ = ["NoobInDaHause"]
    __docs__ = "https://github.com/NoobInDaHause/NoobCogs/blob/red-3.5/randomcolourrole/README.md"

    def format_help_for_context(self, context: commands.Context) -> str:
        """
        Thanks Sinbad and sravan!
        """
        plural = "s" if len(self.__author__) != 1 else ""
        return f"""{super().format_help_for_context(context)}

        Cog Version: **{self.__version__}**
        Cog Author{plural}: {humanize_list([f'**{auth}**' for auth in self.__author__])}
        Cog Documentation: [[Click here]]({self.__docs__})"""

    async def red_delete_data_for_user(
        self, *, requester: Literal["discord_deleted_user", "owner", "user", "user_strict"], user_id: int
    ) -> None:
        """
        This cog does not store any end user data whatsoever.
        """
        return await super().red_delete_data_for_user(requester=requester, user_id=user_id)

    async def cog_load(self):
        self.log.info("Random Colour Role task started.")
        self.change_random_colour_role.start()

    async def cog_unload(self):
        self.log.info("Random Color Role task cancelled.")
        await self.change_random_colour_role.cancel()

    @tasks.loop(minutes=5)
    async def change_random_colour_role(self):
        for guild in self.bot.guilds:
            await asyncio.sleep(2.5)
            settings = await self.config.guild(guild).all()
            if settings["status"] is True and settings["role"] is not None:
                try:
                    role = guild.get_role(settings["role"])
                    await role.edit(colour=random.randint(0, 0xFFFFFF), reason="Random Colour Role.")
                except Exception:
                    continue

    @change_random_colour_role.before_loop
    async def change_random_colour_role_before_loop(self):
        await self.bot.wait_until_red_ready()

    @commands.group(name="randomcolourroleset", aliases=["rcrset", "randomcolorroleset"])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def randomcolourroleset(self, context: commands.Context):
        """
        Settings for the RandomColourRole cog.
        """
        pass

    @randomcolourroleset.command(name="reset")
    async def randomcolourroleset_reset(self, context: commands.Context):
        """
        Reset the RandomColourRoles guild settings.
        """
        act = "Successfully resetted the guilds randomcolourrole settings."
        conf = "Are you sure you want to reset the guilds randomcolourrole settings?"
        view = Confirmation(timeout=30)
        await view.start(context=context, confirmation_msg=conf, confirm_action=act)

        await view.wait()

        if view.value == "yes":
            await self.config.guild(context.guild).clear()

    @randomcolourroleset.command(name="resetcog")
    @commands.is_owner()
    async def randomcolourroleset_resetcog(self, context: commands.Context):
        """
        Reset the RandomColourRole cogs whole config. (Bot owners only)
        """
        act = "Successfully resetted the randomcolourrole cogs config."
        conf = "Are you sure you want to reset the randomcolourrole cogs whole config?"
        view = Confirmation(timeout=30)
        await view.start(context=context, confirmation_msg=conf, confirm_action=act)

        await view.wait()

        if view.value == "yes":
            await self.config.clear_all()

    @randomcolourroleset.command(name="role")
    @commands.bot_has_permissions(manage_roles=True)
    async def randomcolourroleset_role(self, context: commands.Context, role: Optional[discord.Role]):
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
    @commands.bot_has_permissions(manage_roles=True)
    async def randomcolourroleset_status(self, context: commands.Context, state: bool):
        """
        Toggle whether to enable or disable the RandomColourRole.
        """
        await self.config.guild(context.guild).status.set(state)
        status = "enabled" if state else "disabled"
        await context.send(content=f"The randomcolourrole has been {status}.")

    @randomcolourroleset.command(name="showsettings", aliases=["ss"])
    async def randomcolourroleset_showsettings(self, context: commands.Context):
        """
        See the current guild settings for the RandomColourRole.
        """
        settings = await self.config.guild(context.guild).all()
        role = context.guild.get_role(settings['role'])
        embed = discord.Embed(
            title=f"Current RandomColourRole guild settings for {context.guild}",
            colour=await context.embed_colour(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.add_field(name="Role:", value=role.mention if role else "None", inline=False)
        embed.add_field(name="Status:", value=settings['status'], inline=False)

        warns = ""
        if not context.guild.me.guild_permissions.manage_roles:
            warns += "I do not have `manage_roles` permission! RandomColourRole will not work.\n"
        if role and role >= context.guild.me.top_role:
            warns += "The set role is higher than my top role! please lower it down below my top role."

        if warns:
            embed.add_field(
                name="⚠️ Warning", value=warns, inline=False
            )
        await context.send(embed=embed)
