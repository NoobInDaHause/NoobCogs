import asyncio
import datetime
import discord
import logging

from redbot.core import commands, app_commands, Config
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list

from discord.ext import tasks
from typing import Literal

from .views import Confirmation

class RainbowRole(commands.Cog):
    """
    Have a role that changes colour every 10 minutes.
    
    May or may not be API intense but the cog is cool.
    Due to API rate limits you can only have 1 rainbowrole pre guild.
    The role color changes every 10 minutes or so depending on how many guilds the bot is in.
    [Click here](https://github.com/NoobInDaHause/WintersCogs/blob/red-3.5/rainbowrole/README.md) to see all of the available commands for RainbowRole.
    """
    def __init__(self, bot: Red):
        self.bot = bot
        
        self.config = Config.get_conf(self, identifier=128943761874)
        default_guild = {
            "role": 0,
            "status": False
        }
        self.config.register_guild(**default_guild)
        self.log = logging.getLogger("red.WintersCogs.RainbowRole")
        self.change_rainbowrole_color.start()
        
    __version__ = "1.0.0"
    __author__ = ["Noobindahause#2808"]
    
    def format_help_for_context(self, context: commands.Context) -> str:
        """
        Thanks Sinbad and sravan!
        """
        plural = "s" if len(self.__author__) != 1 else ""
        return f"{super().format_help_for_context(context)}\n\nCog Version: {self.__version__}\nCog Author{plural}: {humanize_list(self.__author__)}"
    
    async def red_delete_data_for_user(
        self, *, requester: Literal["discord_deleted_user", "owner", "user", "user_strict"], user_id: int
    ) -> None:
        # This cog does not store any end user data whatsoever.
        return
        
    def access_denied(self):
        return "https://cdn.discordapp.com/attachments/1080904820958974033/1101002761597898863/1.mp4"
    
    def cog_load(self):
        self.log.info("Cog loaded: Rainbowrole task started!")
    
    def cog_unload(self):
        self.log.info("Cog unloaded: Rainbowrole task cancelled.")
        self.bot.loop.create_task(self.change_rainbowrole_color.cancel())
    
    @tasks.loop(minutes=10)
    async def change_rainbowrole_color(self):
        for guild in self.bot.guilds:
            await asyncio.sleep(5)
            settings = await self.config.guild(guild).all()
            if not settings["status"]:
                continue
            if not settings["role"]:
                continue
            try:
                rainbowrole = guild.get_role(settings["role"])
                await rainbowrole.edit(colour=discord.Colour.random(), reason="Rainbow Role.")
            except Exception:
                continue

    @change_rainbowrole_color.before_loop
    async def change_rainbowrole_color_before_loop(self):
        await self.bot.wait_until_red_ready()
    
    @commands.hybrid_group(name="rainbowroleset", invoke_without_command=True, aliases=["rrset"])
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.guild_only()
    @app_commands.guild_only()
    async def rainbowroleset(self, context: commands.Context):
        """
        Settings for the RainbowRole cog.
        """
        await context.send_help()
    
    @rainbowroleset.command(name="reset")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @app_commands.guild_only()
    async def rainbowroleset_reset(self, context: commands.Context):
        """
        Reset the RainbowRoles guild settings.
        """
        confirm_action = "Successfully resetted the guilds rainbowrole settings."
        view = Confirmation(bot=self.bot, author=context.author, timeout=30, confirm_action=confirm_action)
        view.message = await context.send("Are you sure you want to reset the guilds rainbowrole settings?", view=view)
        
        await view.wait()
        
        if view.value == "yes":
            await self.config.guild(context.guild).clear()
    
    @rainbowroleset.command(name="resetcog")
    @commands.is_owner()
    async def rainbowroleset_resetcog(self, context: commands.Context):
        """
        Reset the RainbowRole cogs whole config. (Bot owners only)
        """
        confirm_action = "Successfully resetted the rainbowrole cogs config."
        view = Confirmation(bot=self.bot, author=context.author, timeout=30, confirm_action=confirm_action)
        view.message = await context.send("Are you sure you want to reset the rainbowrole cogs whole config?", view=view)
        
        await view.wait()
        
        if view.value == "yes":
            await self.config.clear_all()
    
    @rainbowroleset.command(name="role")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(
        role="Set the rainbowrole."
    )
    async def rainbowroleset_role(self, context: commands.Context, role: discord.Role):
        """
        Set the guilds rainbow role.
        """
        await self.config.guild(context.guild).role.set(role.id)
        await context.send(f"**{role.name}** has been set as the guilds rainbowrole. Start the cog with `{context.prefix}rrset status` if you haven't already.")
        
    @rainbowroleset.command(name="status")
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(manage_roles=True)
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(
        state="True or False."
    )
    async def rainbowroleset_status(self, context: commands.Context, state: bool):
        """
        Toggle whether to enable or disable the RainbowRole cog.
        """
        await self.config.guild(context.guild).status.set(state)
        status = "enabled" if state else "disabled"
        await context.send(f"The rainbowrole cog has been {status}.")
        
    @rainbowroleset.command(name="showsettings", aliases=["ss"])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    @app_commands.guild_only()
    async def rainbowroleset_showsettings(self, context: commands.Context):
        """
        See the current guild settings for the RainbowRole cog.
        """
        settings = await self.config.guild(context.guild).all()
        embed = discord.Embed(
            title=f"Current RainbowRole guild settings for {context.guild}",
            colour=await context.embed_colour(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.add_field(name="Role:", value=f"<@&{settings['role']}>" if settings['role'] else "None", inline=False)
        embed.add_field(name="Status:", value=settings['status'], inline=False)
        if not context.guild.me.guild_permissions.manage_roles:
            embed.add_field(
                name="⚠️ Warning", value="I do not have `manage_roles` permission! RainbowRole will not work.", inline=False
            )
        await context.send(embed=embed)
        
    # ---------------------------------------------------------------------------
    
    @rainbowroleset_reset.error
    async def rainbowroleset_reset_error(self, context: commands.Context, error):
        if context.prefix == "/":
            await context.reply(content=self.access_denied(), ephemeral=True, mention_author=False)
            
    @rainbowroleset_resetcog.error
    async def rainbowroleset_resetcog_error(self, context: commands.Context, error):
        if context.prefix == "/":
            await context.reply(content=self.access_denied(), ephemeral=True, mention_author=False)
            
    @rainbowroleset_role.error
    async def rainbowroleset_role_error(self, context: commands.Context, error):
        if context.prefix == "/":
            await context.reply(content=self.access_denied(), ephemeral=True, mention_author=False)
            
    @rainbowroleset_status.error
    async def rainbowroleset_status_error(self, context: commands.Context, error):
        if context.prefix == "/":
            await context.reply(content=self.access_denied(), ephemeral=True, mention_author=False)
