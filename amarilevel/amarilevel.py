import datetime
import discord
import logging

from redbot.core import commands, app_commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list, box

from amari import AmariClient
from typing import Literal, Optional

from .noobutils import is_have_avatar

class AmariLevel(commands.Cog):
    """
    Check your amari level but through red.

    You will need an amari api token for this to work.
    You can apply for one [here](https://forms.gle/TEZ3YbbMPMEWYuuMA).
    Then set it with `[p]set api amari auth,<your_api_key>`.
    """
    def __init__(self, bot: Red) -> None:
        self.bot = bot

        self.log = logging.getLogger("red.NoobCogs.AmariLevel")

    __version__ = "1.0.1"
    __author__ = ["NoobInDaHause"]
    __docs__ = "https://github.com/NoobInDaHause/NoobCogs/blob/red-3.5/amarilevel/README.md"

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
    ):
        """
        This cog does not store any end user data whatsoever.
        """
        return await super().red_delete_data_for_user(requester=requester, user_id=user_id)

    @commands.hybrid_command(name="amarilevel", aliases=["alvl", "alevel"])
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.bot_has_permissions(embed_links=True)
    @app_commands.guild_only()
    @app_commands.describe(member="The member that you want to level check.")
    async def amarilevel(self, context: commands.Context, member: Optional[discord.Member]):
        """
        Check your or someone else's amari level.

        Requires amari api token, apply for one [here](https://forms.gle/TEZ3YbbMPMEWYuuMA).
        If you already have an amari api token set it with:
        `[p]set api amari auth,<your_api_key>`
        """
        api_dict: dict = await self.bot.get_shared_api_tokens("amari")

        if not api_dict:
            return await context.send(content="No amari api token found. Ask the bot owner to set one.")

        token = api_dict.get("auth")
        member = member or context.author

        if member.bot:
            return await context.send(content="Bots do not have amari levels.")

        await context.typing()
        try:
            amari = AmariClient(token)
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
        except Exception as e:
            self.log.exception(e, exc_info=e)
            await context.send(
                content="An error has occurred.\nPlease report this to the bot owner.\n"
                f"Here is the traceback: {box(e, 'py')}"
            )

        await amari.close()
