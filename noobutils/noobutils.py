import datetime
import discord
import logging

from redbot.core import commands, app_commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list

from typing import Literal

from .views import Calculator, CookieClicker, PressF

class NoobUtils(commands.Cog):
    """
    Some maybe useful or useless commands.
    
    Cog made by a noob at python with interesting useful or useless commands.
    [Click here](https://github.com/NoobInDaHause/NoobCogs/blob/red-3.5/noobutils/README.md) to see all of the available commands for NoobUtils.
    """
    def __init__(self, bot: Red):
        self.bot = bot
        self.log = logging.getLogger("red.NoobCogs.NoobUtils")
        self.ongoing_pressf_chans = []
        
    __version__ = "1.2.6"
    __author__ = ["Noobindahause#2808"]
    
    def format_help_for_context(self, context: commands.Context) -> str:
        """
        Thanks Sinbad and sravan!
        """
        p = "s" if len(self.__author__) != 1 else ""
        return f"""{super().format_help_for_context(context)}
        
        Cog Version: {self.__version__}
        Cog Author{p}: {humanize_list(self.__author__)}
        """
    
    async def red_delete_data_for_user(
        self, *, requester: Literal["discord_deleted_user", "owner", "user", "user_strict"], user_id: int
    ) -> None:
        # This cog does not store any end user data whatsoever.
        return await super().red_delete_data_for_user(requester=requester, user_id=user_id)
    
    @commands.hybrid_command(name="calculator")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def calculator(self, context: commands.Context):
        """
        Calculate with buttons.
        """
        view = Calculator()
        await view.start(context=context)
    
    @commands.hybrid_command(name="cookieclicker")
    async def cookieclicker(self, context: commands.Context):
        """
        Cookie clicker.
        """
        view = CookieClicker()
        await view.start(context=context)
    
    @commands.hybrid_command(name="membercount", aliases=["mcount"])
    @commands.guild_only()
    @app_commands.guild_only()
    async def membercount(self, context: commands.Context):
        """
        See the current member count on this guild.
        
        Contains separate member count of users and bots.
        """
        await context.typing()
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
    
    @commands.hybrid_command(name="pressf")
    @commands.guild_only()
    @app_commands.guild_only()
    @app_commands.describe(
        member="The member that you want to pay respects to."
    )
    async def pressf(self, context: commands.Context, *, member: discord.Member):
        """
        Press F to pay respect on someone.
        
        Press F with buttons.
        """
        if context.channel.id in self.ongoing_pressf_chans:
            return await context.send(context="We are still paying respects to someone here.")
        
        view = PressF()
        self.ongoing_pressf_chans.append(context.channel.id)
        await view.start(context=context, member=member)
        
        await view.wait()
        
        if view.value == "done":
            index = self.ongoing_pressf_chans.index(context.channel.id)
            self.ongoing_pressf_chans.pop(index)
    
    @commands.command(name="testlog")
    @commands.is_owner()
    async def testlog(self, context: commands.Context, *, anything: str):
        """
        Test out the logging module. (Bot owner only)
        
        Say anything in the `anything` parameter to log it in the console.
        """
        self.log.info(anything)
        await context.tick()