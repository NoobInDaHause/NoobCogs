import datetime
import discord
import logging

from redbot.core import commands, app_commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list, pagify
from redbot.core.utils.menus import menu

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
        
        if not reached:
            return "**0%**", reached, len([mem for mem in context.guild.members if not mem.bot])
        
        div = reached / len([mem for mem in context.guild.members if not mem.bot]) * 100
        yo = f"**{round(div, 2)}%**"
        return yo, reached, len([mem for mem in context.guild.members if not mem.bot])
    
    async def new_here_reach(self, context: commands.Context, channel: discord.TextChannel):
        reached = 0
        here_members = 0
        for member in context.guild.members:
            if member.bot:
                continue
            if member.status == discord.Status.offline:
                continue
            if not channel.permissions_for(member).view_channel:
                continue
            reached += 1

        for m in context.guild.members:
            if m.bot:
                continue
            if m.status == discord.Status.offline:
                continue
            here_members += 1

        if not reached:
            return "**0%**", reached, here_members
        
        div = reached / here_members * 100
        wh = f"**{round(div, 2)}%**"
        return wh, reached, here_members
    
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
        channel: Optional[discord.TextChannel] = None,
        *,
        roles: Optional[str] = None
    ):    # sourcery skip: low-code-quality
        """
        Reach channel and see how many members who can view the channel.
        
        Separate roles with a space if multiple. (ID's accepted)
        You can pass `everyone` or `here`.
        """
        if not channel:
            channel = context.channel

        if not roles:
            return await context.send_help()

        await context.typing()
        reols = roles.split(" ")
        input_roles = []
        for z in reols:
            if z == "@everyone":
                z.replace("@", "")
            if z == "@here":
                z.replace("@", "")
            if z in input_roles:
                continue
            input_roles.append(z)

        total_reach = 0
        total_members = 0

        conf_roles = []
        final = []
        for i in input_roles:
            try:
                f = i.replace("<", "").replace("@", "").replace("&", "").replace(">", "")
                j = context.guild.get_role(int(f))
                conf_roles.append(j)
            except Exception:
                if i.lower() == "everyone":
                    k = await self.new_everyone_reach(context=context, channel=channel)
                    oy = f"` - ` @everyone : {k[1]} out of {k[2]} members - {k[0]}"
                    total_reach += k[1]
                    total_members += k[2]
                    final.append(oy)
                elif i.lower() == "here":
                    k = await self.new_here_reach(context=context, channel=channel)
                    yo = f"` - ` @here : {k[1]} out of {k[2]} members - {k[0]}"
                    total_reach += k[1]
                    total_members += k[2]
                    final.append(yo)
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
            if not reached:
                b = (
                    f"` - ` {role.mention}: {reached} out of "
                    f"{len([m for m in role.members if not m.bot])} members - **0%**"
                )
                total_reach += reached
                total_members += len([m for m in role.members if not m.bot])
                final.append(b)
                continue

            div = reached / len([m for m in role.members if not m.bot]) * 100
            f = (
                f"` - ` {role.mention}: {reached} out of "
                f"{len([m for m in role.members if not m.bot])} members "
                f"- **{round(div, 2)}%**"
            )
            total_reach += reached
            total_members += len([m for m in role.members if not m.bot])
            final.append(f)

        if not final:
            return await context.send("No roles were reached.")

        breh = final[0]
        final.pop(f"{breh}")
        if final[1]:
            bruh = final[1]
            final.pop(f"{bruh}")
        final_roles = "\n".join(final)
        pages = list(pagify(final_roles, delims=["` - `"], page_length=1000))
        real_final = {}

        divov = total_reach / total_members * 100
        ov = (
            f"**Overall Results:**\n"
            f"`Overall Reach:` **{total_reach}**\n"
            f"`Overall Members:` **{total_members}**\n"
            f"`Overall Percentage:` **{round(divov, 2)}%**"
        )
        for ind, page in enumerate(pages, 1):
            embed = discord.Embed(
                title="Role Reach",
                description=f"Channel: {channel.mention}\n\n"
                f"{breh}\n{bruh}\n{page}\n\n{ov}",
                colour=await context.embed_colour(),
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            embed.set_footer(
                text=f"{context.guild.name} | Page ({ind}/{len(pages)})",
                icon_url=is_have_avatar(context.guild)
            )
            real_final[ind - 1] = embed

        await menu(context, list(real_final.values()), timeout=60)