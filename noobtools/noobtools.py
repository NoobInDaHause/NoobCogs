import amari
import discord
import logging
import noobutils as nu
import random

from redbot.core.bot import app_commands, commands, Config, Red
from redbot.core.utils import chat_formatting as cf, mod

from typing import List, Literal, Optional

from .converters import CustomFuzzyRole
from .views import ChangeAuditReasonView


class NoobTools(commands.Cog):
    """
    NoobInDahause's personal tools.
    """

    def __init__(self, bot: Red, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.config = Config.get_conf(
            self, identifier=1234567890, force_registration=True
        )
        default_global = {
            "audit_reason": {"with_reason": None, "without_reason": None},
            "tick_emoji": None,
        }
        self.config.register_global(**default_global)

        self.log = logging.getLogger("red.NoobCogs.NoobTools")
        self.old_get_audit_reason = mod.get_audit_reason

    __version__ = "1.0.0"
    __author__ = ["NoobInDaHause"]
    __docs__ = (
        "https://github.com/NoobInDaHause/NoobCogs/blob/red-3.5/noobtools/README.md"
    )

    def format_help_for_context(self, context: commands.Context) -> str:
        """
        Thanks Sinbad and sravan!
        """
        plural = "s" if len(self.__author__) > 1 else ""
        return (
            f"{super().format_help_for_context(context)}\n\n"
            f"Cog Version: **{self.__version__}**\n"
            f"Cog Author{plural}: {cf.humanize_list([f'**{auth}**' for auth in self.__author__])}\n"
            f"Cog Documentation: [[Click here]]({self.__docs__})"
        )

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

    async def cog_load(self) -> None:
        if t := await self.config.tick_emoji():
            commands.context.TICK = t

        a = await self.config.audit_reason()
        if a["with_reason"] and a["without_reason"]:

            def get_audit_reason(
                author: discord.Member, reason: str = None, *, shorten: bool = False
            ):
                audit_reason = (
                    a["with_reason"].format(
                        author_name=author.name, author_id=author.id, reason=reason
                    )
                    if reason
                    else a["without_reason"].format(
                        author_name=author.name, author_id=author.id
                    )
                )
                if shorten and len(audit_reason) > 512:
                    audit_reason = f"{audit_reason[:509]}..."
                return audit_reason

            mod.get_audit_reason = get_audit_reason

    async def cog_unload(self) -> None:
        mod.get_audit_reason = self.old_get_audit_reason
        commands.context.TICK = "✅"

    @commands.hybrid_command(name="amarilevel", aliases=["alvl", "alevel", "amari"])
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.bot_has_permissions(embed_links=True)
    @app_commands.guild_only()
    @app_commands.describe(member="The member that you want to level check.")
    async def amarilevel(
        self, context: commands.Context, member: discord.Member = None
    ):
        """
        Check your or someone else's amari level.

        Requires amari api token.
        If you are the bot owner apply for one in their support server [here](https://discord.gg/kqefESMzQj).
        If you already have an amari api token set it with:
        `[p]set api amari auth,<your_api_key>`
        """
        api_dict: dict = await self.bot.get_shared_api_tokens("amari")

        if not api_dict:
            return await context.send(
                content="No amari api token found. Ask the bot owner to set one."
            )

        token = api_dict.get("auth")
        member = member or context.author

        if member.bot:
            return await context.send(content="Bots do not have amari levels.")

        async with context.typing():
            try:
                _amari = amari.AmariClient(token)
                lb = await _amari.fetch_full_leaderboard(context.guild.id)
                memb = await _amari.fetch_user(context.guild.id, member.id)
                rank = lb.get_user(member.id)
                embed = discord.Embed(
                    title="Amari Rank",
                    description=(
                        f"- **Rank**: {cf.humanize_number(rank.position + 1)}\n"
                        f"- **Level**: {cf.humanize_number(memb.level)}\n"
                        f"- **EXP**: {cf.humanize_number(memb.exp)}\n"
                        f"- **Weekly EXP**: {cf.humanize_number(memb.weeklyexp)}"
                    ),
                    colour=member.colour,
                    timestamp=discord.utils.utcnow(),
                )
                embed.set_thumbnail(url=nu.is_have_avatar(member))
                embed.set_footer(text=member, icon_url=nu.is_have_avatar(context.guild))
                await context.send(embed=embed)
            except amari.InvalidToken:
                await context.send(
                    content="The amari api token is invalid please report this to the bot owner."
                )
            except amari.NotFound:
                await context.send(content="This guild has no amari data..")
            except amari.HTTPException:
                await context.send(
                    content="Amari API took too long to respond. Perhaps it is down check back later."
                )
            except Exception as e:
                self.log.exception(str(e), exc_info=e)
                await context.send(
                    content="An error has occurred.\nPlease report this to the bot owner.\n"
                    f"Here is the traceback: {cf.box(e, 'py')}"
                )
            await _amari.close()

    @commands.command(name="reach")
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.bot_has_permissions(embed_links=True, manage_roles=True)
    async def reach(
        self,
        context: commands.Context,
        channel: Optional[discord.TextChannel],
        *roles: CustomFuzzyRole,
    ):
        """
        Reach channel and see how many members who can view the channel.

        Separate roles with a space if multiple. (ID's accepted)
        Role searching may or may not be 100% accurate.
        You can pass `everyone` or `here` to check `@everyone` or `@here` reach.
        """
        if not roles:
            return await context.send_help()

        channel = channel or context.channel
        roles = list(set(roles))

        if len(roles) > 15:
            return await context.send(
                "Easy there you can only reach up to 15 roles at a time."
            )

        final_members: List[discord.Member] = []
        final_str: List[str] = []
        all_members = []

        async with context.typing():
            for role in roles:
                if isinstance(role, str):
                    if role.lower() == "everyone":
                        everyone = [
                            member
                            for member in context.guild.members
                            if not member.bot
                            and channel.permissions_for(member).view_channel
                        ]
                        final_members.extend(everyone)
                        am = [m for m in context.guild.members if not m.bot]
                        mems = len(am)
                        ev = len(everyone)
                        all_members.extend(am)
                        try:
                            div = round((ev / mems * 100), 2)
                        except ZeroDivisionError:
                            div = 0
                        final_str.append(
                            f"` #{len(final_str) + 1} ` @everyone: {cf.humanize_number(ev)} out of "
                            f"{cf.humanize_number(mems)} members - **{div}%**"
                        )
                    elif role.lower() == "here":
                        here = [
                            member
                            for member in context.guild.members
                            if not member.bot
                            and channel.permissions_for(member).view_channel
                            and member.status != discord.Status.offline
                        ]
                        final_members.extend(here)
                        am = [
                            m
                            for m in context.guild.members
                            if not m.bot and m.status != discord.Status.offline
                        ]
                        mems = len(am)
                        her = len(here)
                        all_members.extend(am)
                        try:
                            div = round((her / mems * 100), 2)
                        except ZeroDivisionError:
                            div = 0
                        final_str.append(
                            f"` #{len(final_str) + 1} ` @here: {cf.humanize_number(her)} out of "
                            f"{cf.humanize_number(mems)} members - **{div}%**"
                        )
                else:
                    reached = [
                        member
                        for member in role.members
                        if not member.bot
                        and channel.permissions_for(member).view_channel
                    ]
                    final_members.extend(reached)
                    am = [i for i in role.members if not i.bot]
                    mems = len(am)
                    rol = len(reached)
                    all_members.extend(am)
                    try:
                        div = round((rol / mems * 100), 2)
                    except ZeroDivisionError:
                        div = 0
                    final_str.append(
                        f"` #{len(final_str) + 1} ` {role.mention}: {cf.humanize_number(rol)} out of "
                        f"{cf.humanize_number(mems)} members - **{div}%**"
                    )

            overall_reach = len(list(set(final_members)))
            overall_members = len(list(set(all_members)))
            try:
                divov = overall_reach / overall_members * 100
            except ZeroDivisionError:
                divov = 0
            okay = "\n".join(final_str)
            embed = (
                discord.Embed(
                    title="Role Reach",
                    description=f"Channel: {channel.mention} (`{channel.id}`)\n\n{okay}\n",
                    colour=await context.embed_colour(),
                    timestamp=discord.utils.utcnow(),
                )
                .set_footer(
                    text=context.guild.name, icon_url=nu.is_have_avatar(context.guild)
                )
                .add_field(
                    name="__**Overall Results:**__",
                    value=(
                        f"> ` - ` Overall Reach: **{cf.humanize_number(overall_reach)}**\n"
                        f"> ` - ` Overall Members: **{cf.humanize_number(overall_members)}**\n"
                        f"> ` - ` Overall Percentage: **{round(divov, 2)}%**"
                    ),
                    inline=False,
                )
            )

            await context.send(embed=embed)

    @commands.hybrid_command(name="membercount", aliases=["mcount"])
    @commands.bot_has_permissions(embed_links=True)
    async def membercount(self, context: commands.Context):
        """
        See the total members in this guild.
        """
        all_members = [mem for mem in context.guild.members if not mem.bot]
        all_bots = [mbot for mbot in context.guild.members if mbot.bot]
        embed = discord.Embed(
            title=f"Membercount for [{context.guild.name}]",
            timestamp=discord.utils.utcnow(),
            colour=await context.embed_colour(),
        )
        embed.set_thumbnail(url=nu.is_have_avatar(context.guild))
        embed.add_field(
            name="Members:", value=cf.humanize_number(len(all_members)), inline=True
        )
        embed.add_field(
            name="Bots:", value=cf.humanize_number(len(all_bots)), inline=True
        )
        embed.add_field(
            name="All:",
            value=cf.humanize_number(context.guild.member_count),
            inline=True,
        )
        await context.send(embed=embed)

    @commands.command(name="randomcolour", aliases=["randomcolor"])
    @commands.bot_has_permissions(embed_links=True)
    async def randomcolour(self, context: commands.Context):
        """
        Generate a random colour.
        """
        colour = discord.Colour(random.randint(0, 0xFFFFFF))
        url = f"https://singlecolorimage.com/get/{str(colour)[1:]}/400x100"
        embed = discord.Embed(
            title="Here is your random colour.",
            description=f"`Hex:` {str(colour)}\n`Value:` {colour.value}\n`RGB:` {colour.to_rgb()}",
            colour=colour,
            timestamp=discord.utils.utcnow(),
        )
        embed.set_image(url=url)
        await context.send(embed=embed)

    @commands.command(name="changetickemoji")
    @commands.is_owner()
    async def changetickemoji(
        self, context: commands.Context, emoji: nu.NoobEmojiConverter = None
    ):
        """
        Change [botname]'s tick emoji.

        Leave emoji parameter as blank to check current tick emoji.
        """
        if not emoji:
            tick = commands.context.TICK
            await context.tick()
            return await context.send(
                content=f"My current tick emoji is set to: {tick}"
            )
        commands.context.TICK = str(emoji)
        if str(emoji) != "✅":
            await self.config.tick_emoji.set(str(emoji))
        else:
            await self.config.tick_emoji.clear()
        await context.tick()
        await context.send(content=f"Successfully set {str(emoji)} as my tick emoji.")

    @commands.command(name="changeauditreason")
    @commands.is_owner()
    async def changeauditreason(
        self, context: commands.Context, check: Optional[Literal["check", "reset"]]
    ):
        """
        This command changes [botname]'s audit reason.

        For every cog that uses audit reasons.

        Add `check` to see current settings or `reset` to reset settings.

        Available variables:
        {author_name}: The audit authors name.
        {author_id}: The audit authors ID.
        {reason}: The audit reason.

        Note:
        You need all three variables present in the audit that is with reason.
        """
        if check == "check":
            a = await self.config.audit_reason()
            return await context.send(
                content="Your current get_audit_reason settings is:\n\n**With reason:**\n"
                f"```{a['with_reason']}```\n**Without reason:**\n```{a['without_reason']}```"
            )
        if check == "reset":
            await self.config.audit_reason.with_reason.clear()
            await self.config.audit_reason.without_reason.clear()
            mod.get_audit_reason = self.old_get_audit_reason
            return await context.send(content="Audit reason settings has been cleared.")
        view = ChangeAuditReasonView(self)
        await view.start(context)
