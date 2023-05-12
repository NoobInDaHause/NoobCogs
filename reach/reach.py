import datetime
import discord
import logging

from redbot.core import commands, app_commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list

from typing import Literal, Optional

from .utils import is_have_avatar

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

    async def new_everyone_reach(self, context: commands.Context, channel: discord.TextChannel):
        reached = 0
        for member in context.guild.members:
            if member.bot:
                continue
            if not channel.permissions_for(member).view_channel:
                continue
            reached += 1
        div = reached / len([mem for mem in context.guild.members if not mem.bot]) * 100
        return (
            f"@everyone: {reached} out of {len([mem for mem in context.guild.members if not mem.bot])} -"
            f" **{round(div, 2)}%**"
        )
    
    async def new_here_reach(self, context: commands.Context, channel: discord.TextChannel):
        reached = 0
        for member in context.guild.members:
            if member.bot:
                continue
            if member.status == discord.Status.offline:
                continue
            if not channel.permissions_for(member).view_channel:
                continue
            reached += 1
        
        here_members = 0
        for m in context.guild.members:
            if m.bot:
                continue
            if member.status == discord.Status.offline:
                continue
            here_members += 1
        
        div = reached / here_members * 100
        return f"@here: {reached} out of {here_members} - **{round(div, 2)}%**"
    
    @commands.hybrid_command(name="reach")
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @app_commands.guild_only()
    @app_commands.describe(
        channel="The channel that you want to reach.",
        roles="The roles that you want to channel reach. (sparate with spaces if multiple)"
    )
    async def reach(
        self,
        context: commands.Context,
        channel: Optional[discord.TextChannel],
        *,
        roles
    ):  # sourcery skip: low-code-quality
        """
        Reach channel and see how many members who can view the channel.
        
        Separate roles with a space if multiple. (ID's accepted)
        You can pass `everyone` or `here`.
        """
        if not channel:
            channel = context.channel
        
        input_roles = roles.split(" ")
        
        ev_or_here = []
        conf_roles = []
        for i in input_roles:
            try:
                j = await context.guild.get_role(int(i))
                conf_roles.append(j)
            except Exception:
                ev_or_here.append(str(j))
        final = []
        for r in ev_or_here:
            if r.lower() == "everyone":
                k = await self.new_everyone_reach(context=context, channel=channel)
                final.append(k)
            elif r.lower() == "here":
                k = await self.new_here_reach(context=context, channel=channel)
                final.append(k)
            else:
                continue
        
        for role in conf_roles:
            reached = 0
            for member in role.members:
                if member.bot:
                    continue
                if not channel.permissions_for(member).view_channel:
                    continue
                reached += 1
            div = reached / len([m for m in role.members if not m.bot]) * 100
            f = (
                f"` - ` {role.mention} ({role.id}): {reached} out of "
                f"{len([m for m in role.members if not m.bot])} members "
                f"- **{round(div, 2)}%**"
            )
            final.append(f)

        final_roles = "\n".join(final)
        embed = discord.Embed(
            title="Role Reach",
            description=f"Channel: {channel.mention} `{channel.id}`\n\n{final_roles}",
            colour=await context.embed_colour(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.set_footer(text=context.guild.name, icon_url=is_have_avatar(context.guild))
        await context.send(embed=embed)
        