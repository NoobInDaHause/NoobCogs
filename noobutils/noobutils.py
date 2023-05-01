import datetime
import discord
import logging

from redbot.core import commands, app_commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list, box

from typing import Literal

from .views import Calculator, CookieClicker

class NoobUtils(commands.Cog):
    """
    Some maybe useful or useless commands.
    
    Cog made by a noob at python with interesting useful or useless commands.
    [Click here](https://github.com/NoobInDaHause/NoobCogs/blob/red-3.5/noobutils/README.md) to see all of the available commands for NoobUtils.
    """
    def __init__(self, bot: Red):
        self.bot = bot
        self.log = logging.getLogger("red.WintersCogs.NoobUtils")
        
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
    
    @commands.hybrid_command(name="calculator")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def calculator(self, context: commands.Context):
        """
        Calculate with buttons.
        """
        view = Calculator(bot=self.bot, author=context.author)
        view.message = await context.send(content=box("0", "py"), view=view)
    
    @commands.hybrid_command(name="cookieclicker")
    async def cookieclicker(self, context: commands.Context):
        """
        Cookie clicker.
        """
        view = CookieClicker(bot=self.bot, author=context.author)
        view.message = await context.send(view=view)
    
    @commands.hybrid_command(name="membercount", aliases=["mcount"])
    @commands.guild_only()
    @app_commands.guild_only()
    async def membercount(self, context: commands.Context):
        """
        See the current member count on this guild.
        
        Contains separate member count of users and bots.
        """
        if context.prefix != "/":
            await context.tick()
        
        members = len([mem for mem in context.guild.members if not mem.bot])
        bots = len([mem for mem in context.guild.members if mem.bot])
        all_members = len(context.guild.members)
        embed = (
            discord.Embed(
                colour=await context.embed_colour(),
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            .add_field(name="Members:", value=members, inline=True)
            .add_field(name="Bots:", value=bots, inline=True)
            .add_field(name="All Members:", value=all_members, inline=True)
            .set_author(name=f"Current member count for [{context.guild.name}]", icon_url=context.guild.icon.url)
        )
        await context.send(embed=embed)
        
    @commands.hybrid_command(name="testaccessdenied")
    async def testaccessdenied(self, context: commands.Context):
        """
        Useless command just to test Noobindahause's Access Denied.

        This command only works in slash commands.
        """
        if context.prefix != "/":
            return await context.send(content="This command can only be used as a slash command.")
        
        await context.reply(content=self.access_denied(), ephemeral=True)
    
    @commands.hybrid_command(name="testlog")
    @commands.is_owner()
    @app_commands.describe(
        anything="Just write anything :p."
    )
    async def testlog(self, context: commands.Context, *, anything: str):
        """
        Test out the logging module. (Bot owner only)
        
        Say anything in the `anything` parameter to log it in the console.
        """
        if context.prefix != "/":
            await context.tick()
        
        self.log.info(anything)
        
    # ---------------------------------------------------------------------
      
    @testlog.error
    async def testlog_error(self, context: commands.Context, error):
        if context.prefix == "/":
            return await context.reply(content=self.access_denied(), ephemeral=True)

        if isinstance(error, commands.MissingRequiredArgument):
            return await context.send_help()
