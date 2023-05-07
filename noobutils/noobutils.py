import datetime
import discord
import logging

from redbot.core import commands, app_commands, Config
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list

from typing import Literal

from .views import Calculator, CookieClicker, PressFView, PressFButton
from .utils import EmojiConverter

class NoobUtils(commands.Cog):
    """
    Some maybe useful or useless commands.
    
    Cog made by a noob at python with interesting useful or useless commands.
    [Click here](https://github.com/NoobInDaHause/NoobCogs/blob/red-3.5/noobutils/README.md) to see all of the available commands for NoobUtils.
    """
    def __init__(self, bot: Red):
        self.bot = bot
        
        self.config = Config.get_conf(self, identifier=85623587, force_registration=True)
        default_guild = {
            "pressf_emoji": "🇫"
        }
        self.config.register_guild(**default_guild)
        self.log = logging.getLogger("red.NoobCogs.NoobUtils")
        
    __version__ = "1.3.0"
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
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def cookieclicker(self, context: commands.Context):
        """
        Cookie clicker.
        """
        view = CookieClicker()
        await view.start(context=context)
    
    @commands.hybrid_command(name="membercount", aliases=["mcount"])
    @commands.cooldown(1, 10, commands.BucketType.user)
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
    
    @commands.group(name="noobset")
    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    async def noobset(self, context: commands.Context):
        """
        Change some settings for the NoobUtils cog commands.
        """
    
    @noobset.comamnd(name="pressfemoji")
    async def pressfemoji(self, context: commands.Context, emoji: EmojiConverter):
        """
        Change the emoji of the press f command.
        """
        await self.config.guild(context.guild).pressf_emoji.set(str(emoji))
        await context.send(f"{emoji} is the new Press F emoji.")
    
    @commands.hybrid_command(name="pressf")
    @commands.cooldown(1, 60, commands.BucketType.user)
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
        emoji = await self.config.guild(context.guild).pressf_emoji()
        button = PressFButton(style=discord.ButtonStyle.success, label="0", emoji=emoji)
        view = PressFView()
        view.add_item(button)
        await view.start(context=context, member=member)
    
    @commands.command(name="testlog")
    @commands.is_owner()
    async def testlog(self, context: commands.Context, *, anything: str):
        """
        Test out the logging module. (Bot owner only)
        
        Say anything in the `anything` parameter to log it in the console.
        """
        self.log.info(anything)
        await context.tick()