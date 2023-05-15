import datetime
import discord
import logging

from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list, humanize_number

from typing import Literal, Optional

from .utils import is_have_avatar, FuzzyRole

class Reach(commands.Cog):
    """
    Reach roles on a channel.
    
    See how many members in a role who can view a channel.
    """
    def __init__(self, bot: Red):
        self.bot = bot
        self.log = logging.getLogger("red.NoobCogs.Reach")

    __version__ = "1.0.0"
    __author__ = ["Noobindahause#2808"]
    __documentation__ = "https://github.com/NoobInDaHause/NoobCogs/blob/red-3.5/reach/README.md"

    def format_help_for_context(self, context: commands.Context) -> str:
        """
        Thanks Sinbad and sravan!
        """
        p = "s" if len(self.__author__) != 0 or 1 else ""
        return f"""{super().format_help_for_context(context)}
        
        Cog Version: **{self.__version__}**
        Cog Author{p}: {humanize_list([f"**{auth}**" for auth in self.__author__])}
        Cog Documentation: [[Click here]]({self.__documentation__})"""

    async def red_delete_data_for_user(
        self,
        *,
        requester: Literal['discord_deleted_user', 'owner', 'user', 'user_strict'],
        user_id: int
    ):
        # This cog does not store any end user data whatsoever.
        return await super().red_delete_data_for_user(requester=requester, user_id=user_id)

    async def new_here_reach(self, context: commands.Context, channel: discord.TextChannel):
        reached = 0
        here_members = 0
        for member in context.guild.members:
            if member.bot:
                continue
            if member.status == discord.Status.offline:
                continue
            here_members += 1
            if not channel.permissions_for(member).view_channel:
                continue
            reached += 1

        if not reached:
            return "**0%**", reached, here_members

        div = reached / here_members * 100
        wh = f"**{round(div, 2)}%**"
        return wh, reached, here_members

    @commands.command(name="reach", usage="[channel] <roles...>")
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.bot_has_permissions(embed_links=True, manage_roles=True)
    async def reach(
        self,
        context: commands.Context,
        channel: Optional[discord.TextChannel],
        *roles: Optional[FuzzyRole]
    ):  # sourcery skip: low-code-quality
        """
        Reach channel and see how many members who can view the channel.
        
        Separate roles with a space if multiple. (ID's accepted)
        Role searching may or may not be 100% accurate.
        You can pass `everyone` or `here` to check `@everyone` or `@here` reach.
        """
        if not channel:
            channel = context.channel

        await context.typing()
        reols = []
        for x in roles:
            if x in reols:
                continue
            reols.append(x)

        if len(reols) >= 16:
            return await context.send("Easy there you can only reach up to 15 roles at a time.")
        total_reach = []
        total_members = []

        final = []
        for i in reols:
            try:
                reached = 0
                for mem in i.members:
                    if mem.bot:
                        continue
                    if not channel.permissions_for(mem).view_channel:
                        continue
                    reached += 1
                    if mem in total_reach:
                        continue
                    total_reach.append(mem)

                iid = f"(`{i.id}`)" if i.id != context.guild.default_role.id else ""
                if not reached:
                    b = (
                        f"` #{len(final) + 1} ` {i.mention}{iid}: 0 out of "
                        f"{humanize_number(len([m for m in i.members if not m.bot]))} members - **0%**\n"
                    )
                    for m in i.members:
                        if m.bot:
                            continue
                        if m in total_members:
                            continue
                        total_members.append(m)
                    final.append(b)
                    continue

                div = reached / len([m for m in i.members if not m.bot]) * 100
                f = (
                    f"` #{len(final) + 1} ` {i.mention}{iid}: {humanize_number(reached)} out of "
                    f"{humanize_number(len([m for m in i.members if not m.bot]))} members "
                    f"- **{round(div, 2)}%**\n"
                )
                for m in i.member:
                    if m.bot:
                        continue
                    if m in total_members:
                        continue
                    total_members.append(m)
                final.append(f)
            
            except Exception:
                if i.lower() == "everyone":
                    reached = 0
                    for member in context.guild.members:
                        if member.bot:
                            continue
                        if not channel.permissions_for(member).view_channel:
                            continue
                        reached += 1
                        if member in total_reach:
                            continue
                        total_reach.append(member)
        
                    if not reached:
                        oy = f"` #{len(final) + 1} ` @everyone: 0 out of {humanize_number(len([mem for mem in context.guild.members if not mem.bot]))} members - **0%**\n"
                        for mem in context.guild.members:
                            if mem.bot:
                                continue
                            if mem in total_members:
                                continue
                            total_members.append(mem)
                        final.append(oy)
                        continue

                    div = reached / len([mem for mem in context.guild.members if not mem.bot]) * 100
                    oy = f"` #{len(final) + 1} ` @everyone: {humanize_number(reached)} out of {humanize_number(len([mem for mem in context.guild.members if not mem.bot]))} members - **{round(div, 2)}%**\n"
                    for mem in context.guild.members:
                        if mem.bot:
                            continue
                        if mem in total_members:
                            continue
                        total_members.append(mem)
                    final.append(oy)
                
                elif i.lower() == "here":
                    reached = 0
                    here_members = 0
                    for member in context.guild.members:
                        if member.bot:
                            continue
                        if member.status == discord.Status.offline:
                            continue
                        here_members += 1
                        if not channel.permissions_for(member).view_channel:
                            continue
                        reached += 1
                        if member in total_reach:
                            continue
                        total_reach.append(member)

                    if not reached:
                        yo = f"` #{len(final) + 1} ` @here: 0 out of {humanize_number(here_members)} members - **0%**\n"
                        for mem in context.guild.members:
                            if mem.bot:
                                continue
                            if mem.status == discord.Status.offline:
                                continue
                            if mem in total_members:
                                continue
                            total_members.append(mem)
                        final.append(yo)
                        continue

                    div = reached / here_members * 100
                    yo = f"` #{len(final) + 1} ` @here: {humanize_number(reached)} out of {humanize_number(here_members)} members - **{round(div, 2)}%**\n"
                    for mem in context.guild.members:
                        if mem.bot:
                            continue
                        if mem.status == discord.Status.offline:
                            continue
                        if mem in total_members:
                            continue
                        total_members.append(mem)
                    final.append(yo)
                
                else:
                    continue

        final_roles = "".join(final)

        divov = len(total_reach) / len(total_members) * 100
        ov = (
            f"> ` - ` Overall Reach: **{humanize_number(len(total_reach))}**\n"
            f"> ` - ` Overall Members: **{humanize_number(len(total_members))}**\n"
            f"> ` - ` Overall Percentage: **{round(divov, 2)}%**"
        )
        embed = (
            discord.Embed(
                title="Role Reach",
                description=f"Channel: {channel.mention} (`{channel.id}`)\n\n{final_roles}\n",
                colour=await context.embed_colour(),
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            .set_footer(text=context.guild.name, icon_url=is_have_avatar(context.guild))
            .add_field(name="__**Overall Results:**__",value=ov,inline=False)
        )

        await context.send(embed=embed)
