import datetime
import discord
import logging

from redbot.core import commands, app_commands, Config
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list

from amari import AmariClient, InvalidToken, NotFound, RatelimitException, AmariServerError
from typing import Literal, Optional

from .views import Calculator, CookieClicker, PressFView
from .utils import EmojiConverter, is_have_avatar

class NoobUtils(commands.Cog):
    """
    Some maybe useful or useless commands.

    Cog made by a noob at python with interesting useful or useless commands.
    """
    def __init__(self, bot: Red):
        self.bot = bot

        self.config = Config.get_conf(self, identifier=85623587, force_registration=True)
        default_guild = {
            "emojis": {
                "pressf": "🇫",
                "cookie": "🍪"
            }
        }
        self.config.register_guild(**default_guild)
        self.log = logging.getLogger("red.NoobCogs.NoobUtils")

    __version__ = "1.4.0"
    __author__ = ["Noobindahause#2808"]
    __docs__ = "https://github.com/NoobInDaHause/NoobCogs/blob/red-3.5/noobutils/README.md"

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
        self,
        *,
        requester: Literal["discord_deleted_user", "owner", "user", "user_strict"],
        user_id: int
    ) -> None:
        # This cog does not store any end user data whatsoever.
        return await super().red_delete_data_for_user(requester=requester, user_id=user_id)

    @commands.hybrid_command(name="amarilevel", aliases=["alvl", "alevel"])
    @commands.bot_has_permissions(embed_links=True)
    @app_commands.describe(
        member="The member that you want to level check."
    )
    async def amarilevel(self, context: commands.Context, member: Optional[discord.Member]):
        """
        Check your or someone else's amari level.

        Requires amari api token, apply for one [here](https://forms.gle/TEZ3YbbMPMEWYuuMA).
        If you already have an amari api token set it with:
        `[p]set api amari auth,<your_api_key>`
        """
        api_dict: dict = await self.bot.get_shared_api_tokens("amari")

        if not api_dict:
            return await context.send(content="No api token found. Ask the bot owner to set one.")

        token = api_dict.get("auth")
        member = member or context.author

        if member.bot:
            return await context.send(content="Bots do not have amari levels.")

        await context.typing()
        amari = AmariClient(token)
        try:
            lb = await amari.fetch_full_leaderboard(context.guild.id)
            memb = await amari.fetch_user(context.guild.id, member.id)
            rank = lb.get_user(member.id)

            embed = (
                discord.Embed(
                    description=f"{member.mention}'s amari.",
                    colour=member.colour,
                    timestamp=datetime.datetime.now(datetime.timezone.utc)
                )
                .set_thumbnail(url=is_have_avatar(member))
                .add_field(name="Amari Rank:", value=rank.position + 1, inline=False)
                .add_field(name="Amari Level:", value=memb.level, inline=False)
                .add_field(name="Amari EXP:", value=memb.exp, inline=False)
                .add_field(name="Amari Weekly EXP:", value=memb.weeklyexp, inline=False)
            )
            await context.send(embed=embed)
        except NotFound:
            await context.send(content="No amari data was found for this member.")
        except InvalidToken:
            await context.send(
                content="It appears the set api token is invalid. Let the bot owner know about this."
            )
        except RatelimitException:
            await context.send(content="The amari api is being rate limited, try again in a few minutes.")
        except AmariServerError:
            await context.send(
                content="There was an internal error in the Amari servers. Please try again later."
            )

        await amari.close()

    @commands.hybrid_command(name="calculator")
    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.bot_has_permissions(embed_links=True)
    async def calculator(self, context: commands.Context):
        """
        Calculate with buttons.
        """
        view = Calculator()
        await view.start(context=context)
    
    @commands.hybrid_command(name="cookieclicker")
    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.bot_has_permissions(embed_links=True)
    async def cookieclicker(self, context: commands.Context):
        """
        Cookie clicker.

        Anti stress guaranteed.
        """
        emoji = await self.config.guild(context.guild).emojis.cookie()
        view = CookieClicker(emoji=emoji)
        await view.start(context=context)
    
    @commands.hybrid_command(name="membercount", aliases=["mcount"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.bot_has_permissions(embed_links=True)
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
            .set_author(
                name=f"Current member count for [{context.guild.name}]",
                icon_url=is_have_avatar(context.guild)
            )
        )
        await context.send(embed=embed)

    @commands.group(name="noobset")
    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    async def noobset(self, context: commands.Context):
        """
        Change some settings for the NoobUtils cog commands.
        """
        pass

    @noobset.command(name="emoji")
    async def noobset_emoji(
        self,
        context: commands.Context,
        type: Literal["pressf", "cookie"],
        emoji: Optional[EmojiConverter]
    ):
        """
        Change the emoji of the press f command.
        
        Pass without emoji to reset it.
        """
        if type == "pressf"
            if not emoji:
                await self.config.guild(context.guild).emojis.pressf.clear()
                return await context.send("The Press F emoji has been reset to default.")
            await self.config.guild(context.guild).emojis.pressf.set(str(emoji))
            await context.send(f"{emoji} is the new Press F emoji.")
        elif type == "cookie":
            if not emoji:
                await self.config.guild(context.guild).emojis.cookie.clear()
                return await context.send("The cookie emoji has been reset to default.")
            await self.config.guild(context.guild).emojis.cookie.set(str(emoji))
            await context.send(f"{emoji} is the new Cookie emoji.")

    @commands.hybrid_command(name="pressf")
    @commands.cooldown(1, 60, commands.BucketType.user)
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @app_commands.guild_only()
    @app_commands.describe(
        thing="A thing that you want to pay respects to."
    )
    async def pressf(self, context: commands.Context, *, thing: str):
        """
        Press F to pay respect on something.
        
        Press F with buttons.
        """
        emoji = await self.config.guild(context.guild).emojis.pressf()
        view = PressFView(emoji=emoji)
        await view.start(context=context, thing=thing)
    
    @commands.command(name="testlog")
    @commands.is_owner()
    async def testlog(self, context: commands.Context, *, anything: str):
        """
        Test out the logging module. (Bot owner only)
        
        Say anything in the `anything` parameter to log it in the console.
        """
        self.log.info(anything)
        await context.tick()
