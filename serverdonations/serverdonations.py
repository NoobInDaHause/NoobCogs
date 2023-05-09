import asyncio
import discord
import logging

from redbot.core import commands, Config
from redbot.core.bot import Red
from redbot.core.utils.menus import menu
from redbot.core.utils.chat_formatting import humanize_list

from typing import Literal, Optional

from .constants import SdonateDesc
from .utils import is_have_avatar
from .views import Confirmation

class ServerDonations(commands.Cog):
    """
    Donate bot currencies or other things to servers.
    
    Base commands to donate to server giveaways, events, heists etc.
    """
    
    def __init__(self, bot: Red) -> None:
        self.bot = bot
        
        self.config = Config.get_conf(self, identifier=7364456583646323, force_registration=True)
        default_guild_settings = {
            "gman_id": None,
            "eman_id": None,
            "hman_id": None,
            "gchannel_id": None,
            "echannel_id": None,
            "hchannel_id": None
        }
        self.config.register_guild(**default_guild_settings)
        self.log = logging.getLogger("red.NoobCogs.ServerDonations")
        
    __version__ = "1.2.1"
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
    
    async def send_to_g_chan(self, context: commands.Context, chan_id: int, g_values: list):
        """
        Sends to the set giveaway donation request channel.
        """
        # <type> | <duration> | <winners> | [requirements] | <prize> | [message]
        view = discord.ui.View()
        button = discord.ui.Button(label="Jump To Command", url=context.message.jump_url)
        view.add_item(button)
        
        embed = (
            discord.Embed(
                colour = await context.embed_colour(),
                title="Someone would like to donate for a giveaway!",
                timestamp=context.message.created_at
            )
            .set_thumbnail(url=is_have_avatar(context.author))
            .set_footer(text=context.guild, icon_url=is_have_avatar(context.guild))
            .add_field(name="Donor:", value=context.author.mention, inline=False)
            .add_field(name="Type:", value=g_values[0], inline=True)
            .add_field(name="Duration:", value=g_values[1], inline=True)
            .add_field(name="Winners:", value=g_values[2], inline=False)
            .add_field(name="Requirements:", value=g_values[3], inline=True)
            .add_field(name="Prize:", value=g_values[4], inline=True)
            .add_field(name="Message:", value=g_values[5], inline=False)
        )
        
        g_role = await self.config.guild(context.guild).gman_id()
        channel = context.guild.get_channel(chan_id)
        
        if not g_role:
            try:
                await channel.send(embed=embed, view=view)
            except (discord.errors.Forbidden, discord.errors.HTTPException):
                return await context.send("It appears that I do not see the set giveaway donation channel request, most likely deleted or I do not have permission to view it.")
        
        grole = context.guild.get_role(g_role)
        try:
            await self.forcemention(channel=channel, role=grole, embed=embed, view=view)
        except (discord.errors.Forbidden, discord.errors.HTTPException):
            return await context.send("An error occured while sending the donation request embed. Most likely that the channel is deleted or I do not have permission to view or send message in it.")
    
    async def send_to_e_chan(self, context: commands.Context, chan_id: int, e_values: list):
        """
        Sends to the set event donation request channel.
        """
        # <type> | <event> | [requirements] | <prize> | [message]
        view = discord.ui.View()
        button = discord.ui.Button(label="Jump To Command", url=context.message.jump_url)
        view.add_item(button)
        
        embed = (
            discord.Embed(
                colour = await context.embed_colour(),
                title="Someone would like to donate for an event!",
                timestamp=context.message.created_at
            )
            .set_thumbnail(url=is_have_avatar(context.author))
            .set_footer(text=context.guild, icon_url=is_have_avatar(context.guild))
            .add_field(name="Donor:", value=context.author.mention, inline=False)
            .add_field(name="Type:", value=e_values[0], inline=True)
            .add_field(name="Event:", value=e_values[1], inline=True)
            .add_field(name="Requirements:", value=e_values[2], inline=False)
            .add_field(name="Prize:", value=e_values[3], inline=True)
            .add_field(name="Message:", value=e_values[4], inline=True)
        )
        e_role = await self.config.guild(context.guild).eman_id()
        channel = context.guild.get_channel(chan_id)
        
        if not e_role:
            try:
                await channel.send(embed=embed, view=view)
            except (discord.errors.Forbidden, discord.errors.HTTPException):
                return await context.send("It appears that I do not see the set event donation channel request, most likely deleted or I do not have permission to view it.")
        
        erole = context.guild.get_role(e_role)
        try:
            await self.forcemention(channel=channel, role=erole, embed=embed, view=view)
        except (discord.errors.Forbidden, discord.errors.HTTPException):
            return await context.send("An error occured while sending the donation request embed. Most likely that the channel is deleted or I do not have permission to view or send message in it.")
        
    async def send_to_h_chan(self, context: commands.Context, chan_id: int, h_values: list):
        """
        Sends to the set heist donation request channel.
        """
        # <type> | <amount> | [requirements] | [message]
        view = discord.ui.View()
        button = discord.ui.Button(label="Jump To Command", url=context.message.jump_url)
        view.add_item(button)
        
        embed = (
            discord.Embed(
                colour = await context.embed_colour(),
                title="Someone would like to donate for a heist!",
                timestamp=context.message.created_at
            )
            .set_thumbnail(url=is_have_avatar(context.author))
            .set_footer(text=context.guild, icon_url=is_have_avatar(context.guild))
            .add_field(name="Donor:", value=context.author.mention, inline=False)
            .add_field(name="Type:", value=h_values[0], inline=True)
            .add_field(name="Amount:", value=h_values[1], inline=True)
            .add_field(name="Requirements:", value=h_values[2], inline=False)
            .add_field(name="Message:", value=h_values[3], inline=False)
        )
        h_role = await self.config.guild(context.guild).hman_id()
        channel = context.guild.get_channel(chan_id)
        
        if not h_role:
            try:
                await channel.send(embed=embed, view=view)
            except (discord.errors.Forbidden, discord.errors.HTTPException):
                return await context.send("It appears that I do not see the set heist donation channel request, most likely deleted or I do not have permission to view it.")
        
        hrole = context.guild.get_role(h_role)
        try:
            await self.forcemention(channel=channel, role=hrole, embed=embed, view=view)
        except (discord.errors.Forbidden, discord.errors.HTTPException):
            return await context.send("An error occured while sending the donation request embed. Most likely that the channel is deleted or I do not have permission to view or send message in it.")
        
    # https://github.com/phenom4n4n/phen-cogs/blob/d60b66c0738937e71ee4865d62235e1b2c3cd819/forcemention/forcemention.py#L64
    # modified a lil bit to work with my code
    async def forcemention(
        self, channel: discord.TextChannel, role: discord.Role, embed: discord.Embed, view: discord.ui.View, **kwargs
    ):
        mentionPerms = discord.AllowedMentions(roles=True)
        me = channel.guild.me
        if (
            not role.mentionable
            and not channel.permissions_for(me).mention_everyone
            and channel.permissions_for(me).manage_roles
            and me.top_role > role
        ):
            await role.edit(mentionable=True)
            await channel.send(content=role.mention, embed=embed, view=view, allowed_mentions=mentionPerms, **kwargs)
            await asyncio.sleep(1.5)
            await role.edit(mentionable=False)
        else:
            await channel.send(content=role.mention, embed=embed, view=view, allowed_mentions=mentionPerms, **kwargs)
    
    @commands.command(name="sdonatehelp")
    @commands.bot_has_permissions(embed_links=True)
    async def sdonatehelp(self, context: commands.Context):
        """
        Know how to run the donation commands.
        
        Available commands:
        `[p]giveawaydonate`
        `[p]eventdonate`
        `[p]heistdonate`
        """
        em1 = discord.Embed(
            title=f"How to use `{context.prefix}giveawaydonate` command",
            description=SdonateDesc.gdonodesc.replace("[p]", f"{context.prefix}"),
            colour=await context.embed_colour()
        ).set_footer(text=f"Command executed by: {context.author} | Page 1/3", icon_url=is_have_avatar(context.author))
        
        em2 = discord.Embed(
            title=f"How to use `{context.prefix}eventdonate` command",
            description=SdonateDesc.edonodesc.replace("[p]", f"{context.prefix}"),
            colour=await context.embed_colour()
        ).set_footer(text=f"Command executed by: {context.author} | Page 2/3", icon_url=is_have_avatar(context.author))
        
        em3 = discord.Embed(
            title=f"How to use `{context.prefix}heistdonate` command",
            description=SdonateDesc.hdonodesc.replace("[p]", f"{context.prefix}"),
            colour=await context.embed_colour()
        ).set_footer(text=f"Command executed by: {context.author} | Page 3/3", icon_url=is_have_avatar(context.author))
        
        bemeds = [em1, em2, em3]
        await menu(context, bemeds, timeout=60)
    
    @commands.group(name="serverdonationsset", aliases=["sdonateset"])
    @commands.guild_only()
    @commands.admin_or_permissions(administrator=True, manage_guild=True)
    @commands.bot_has_permissions(embed_links=True)
    async def serverdonationsset(self, context):
        """
        Settings for ServerDonations cog.
        
        See sub commands for more info.
        """
        
    @serverdonationsset.command(name="reset")
    async def serverdonationsset_reset(self, context: commands.Context):
        """
        Reset the serverdonations guild settings to default.
        """
        conf_msg = "Are you sure you want to reset the guild's settings to default?"
        conf_act = "Successfully resetted the guild's settings to default."
        view = Confirmation(timeout=30)
        await view.start(context, conf_msg, conf_act)
        
        await view.wait()
        
        if view.value == "yes":
            await self.config.guild(context.guild).clear()
    
    @serverdonationsset.group(name="manager")
    @commands.bot_has_permissions(manage_roles=True)
    async def serverdonationsset_manager(self, context):
        """
        Commands to set or remove manager roles that gets pinged for donation requests.
        
        See sub commands for more info.
        """
        
    @serverdonationsset_manager.command(name="giveaway", aliases=["gaw"])
    async def serverdonationsset_manager_giveaway(
        self,
        context: commands.Context,
        role: Optional[discord.Role]
    ):
        """
        Set or remove the giveaway manager ping role.
        
        This role gets pinged whenever there is a server giveaway donation request.
        Pass without role to remove the current set one.
        """
        g_role = await self.config.guild(context.guild).gman_id()

        if not role:
            if not g_role:
                return await context.send("It appears there is no set giveaway manager role. Set one by passing a role.")
            await self.config.guild(context.guild).gman_id.clear()
            return await context.send("The giveaway manager ping role has been removed.")

        if role >= context.guild.me.top_role:
            return await context.send("It appears that role is highre than me in hierarchy, please move it down below my top role.")
        
        if role.id == g_role:
            return await context.send("It appears that role is already the set giveaway manager role.")

        await self.config.guild(context.guild).gman_id.set(role.id)
        await context.send(f"Successfully set `@{role.name}` as the giveaway manager ping role.")
            
    @serverdonationsset_manager.command(name="event")
    async def serverdonationsset_manager_event(
        self,
        context: commands.Context,
        role: Optional[discord.Role]
    ):
        """
        Set or remove the event manager ping role.
        
        This role gets pinged whenever there is a server event donation request.
        Pass without role to remove the current set one.
        """
        e_role = await self.config.guild(context.guild).eman_id()

        if not role:
            if not e_role:
                return await context.send("It appears there is no set event manager role. Set one by passing a role.")
            await self.config.guild(context.guild).eman_id.clear()
            return await context.send("The event manager ping role has been removed.")

        if role >= context.guild.me.top_role:
            return await context.send("It appears that role is highre than me in hierarchy, please move it down below my top role.")
        
        if role.id == e_role:
            return await context.send("It appears that role is already the set event manager ping role.")

        await self.config.guild(context.guild).eman_id.set(role.id)
        await context.send(f"Successfully set `@{role.name}` as the event manager role.")
            
    @serverdonationsset_manager.command(name="heist")
    async def serverdonationsset_manager_heist(
        self,
        context: commands.Context,
        role: Optional[discord.Role]
    ):
        """
        Set or remove the heist manager ping role.
        
        This role gets pinged whenever there is a server heist donation request.
        Pass without role to remove the current set one.
        """
        h_role = await self.config.guild(context.guild).hman_id()

        if not role:
            if not h_role:
                return await context.send("It appears there is no set heist manager role. Set one by passing a role.")
            await self.config.guild(context.guild).hman_id.clear()
            return await context.send("The heist manager ping role has been removed.")

        if role >= context.guild.me.top_role:
            return await context.send("It appears that role is highre than me in hierarchy, please move it down below my top role.")
        
        if role.id == h_role:
            return await context.send("It appears that role is already the set heist manager role.")

        await self.config.guild(context.guild).hman_id.set(role.id)
        await context.send(f"Successfully set `@{role.name}` as the heist manager ping role.")
            
    @serverdonationsset.group(name="channel", aliases=["chan"])
    async def serverdonationsset_channel(self, context):
        """
        Commands to set the requests on a specific channel.
        
        See sub commands for more info.
        """
        
    @serverdonationsset_channel.command(name="giveaway", aliases=["gaw"])
    async def serverdonationsset_channel_giveaway(
        self,
        context: commands.Context,
        channel: Optional[discord.TextChannel]
    ):
        """
        Set or remove the giveaway donation request channel.
        
        The gchannel is required for the `[p]giveawaydonate` command.
        Pass without channel to remove the current set one.
        """
        g_chan = await self.config.guild(context.guild).gchannel_id()

        if not channel:
            if not g_chan:
                return await context.send("It appears there is no set giveaway donation request channel. Ask an admin to set one.")
            await self.config.guild(context.guild).gchannel_id.clear()
            return await context.send("The giveaway donation request channel has been removed.")

        if channel.id == g_chan:
            return await context.send("It appears that channel is already the set giveaway donation request channel.")

        try:
            await channel.send("If you are seeing this message then that means you have set up the channel correctly.")
        except (discord.errors.Forbidden, discord.errors.HTTPException):
            return await context.send("I do not have permission to view or send messages in that channel.")
        
        await self.config.guild(context.guild).gchannel_id.set(channel.id)
        await context.send(f"Successfully set {channel.mention} as the giveaway donation request channel.")
        
    @serverdonationsset_channel.command(name="event")
    async def serverdonationsset_channel_event(
        self,
        context: commands.Context,
        channel: Optional[discord.TextChannel]
    ):
        """
        Set or remove the event donation requests channel.
        
        The echannel is required for the `[p]eventdonate` command.
        Pass without channel to remove the current set one.
        """
        e_chan = await self.config.guild(context.guild).echannel_id()

        if not channel:
            if not e_chan:
                return await context.send("It appears there is no set event donation request channel. Ask an admin to set one.")
            await self.config.guild(context.guild).echannel_id.clear()
            return await context.send("The event donation request channel has been removed.")

        if channel.id == e_chan:
            return await context.send("It appears that channel is already the set event donation request channel.")

        try:
            await channel.send("If you are seeing this message then that means you have set up the channel correctly.")
        except (discord.errors.Forbidden, discord.errors.HTTPException):
            return await context.send("I do not have permission to view or send messages in that channel.")
        
        await self.config.guild(context.guild).echannel_id.set(channel.id)
        await context.send(f"Successfully set {channel.mention} as the event donation request channel.")
            
    @serverdonationsset_channel.command(name="heist")
    async def serverdonationsset_channel_heist(
        self,
        context: commands.Context,
        channel: Optional[discord.TextChannel]
    ):
        """
        Set or remove the heist donation request channel.
        
        The hchannel is required for the `[p]heistdonate` command.
        Pass without channel to remove the current set one.
        """
        h_chan = await self.config.guild(context.guild).hchannel_id()

        if not channel:
            if not h_chan:
                return await context.send("It appears there is no set heist donation request channel. Ask an admin to set one.")
            await self.config.guild(context.guild).hchannel_id.clear()
            return await context.send("The heist donation request channel has been removed.")

        if channel.id == h_chan:
            return await context.send("It appears that channel is already the set heist donation request channel.")

        try:
            await channel.send("If you are seeing this message then that means you have set up the channel correctly.")
        except (discord.errors.Forbidden, discord.errors.HTTPException):
            return await context.send("I do not have permission to view or send messages in that channel.")
        
        await self.config.guild(context.guild).hchannel_id.set(channel.id)
        await context.send(f"Successfully set {channel.mention} as the heist donation request channel.")
            
    @serverdonationsset.command(name="resetcog")
    @commands.is_owner()
    async def serverdonationsset_resetcog(self, context):
        """
        Reset the AFK cogs configuration.

        Bot owners only.
        """
        conf_msg = "This will reset the serverdonations cogs whole configuration, do you want to continue?"
        conf_act = "Successfully cleared the serverdonations cogs configuration."
        view = Confirmation(30)
        await view.start(context, conf_msg, conf_act)
        
        await view.wait()
        
        if view.value == "yes":
            await self.config.clear_all()
    
    @serverdonationsset.command(name="showsetting", aliases=["showset", "ss", "showsettings"])
    async def serverdonationsset_showsetting(self, context: commands.Context):
        """
        See the guild settings set for ServerDonations.
        """
        settings = await self.config.guild(context.guild).all()
        embed = (
            discord.Embed(
                colour=await context.embed_colour(),
                timestamp=context.message.created_at
            )
            .set_author(name=f"ServerDonations settings for [{context.guild}]", icon_url=is_have_avatar(context.guild))
            .add_field(
                name="Giveaway manager role:",
                value=f"<@&{settings['gman_id']}>" if settings['gman_id'] else "No role set.", 
                inline=True
            )
            .add_field(
                name="Event manager role:",
                value=f"<@&{settings['eman_id']}>" if settings['eman_id'] else "No role set.",
                inline=True
            )
            .add_field(
                name="Heist manager role:",
                value=f"<@&{settings['hman_id']}>" if settings['hman_id'] else "No role set.",
                inline=True
            )
            .add_field(
                name="Giveaway donate channel:",
                value=f"<#{settings['gchannel_id']}>" if settings['gchannel_id'] else "No channel set.",
                inline=True
            )
            .add_field(
                name="Event donate channel:",
                value=f"<#{settings['echannel_id']}>" if settings['echannel_id'] else " No channel set.",
                inline=True
            )
            .add_field(
                name="Heist donate channel:",
                value=f"<#{settings['hchannel_id']}>" if settings['hchannel_id'] else "No channel set.",
                inline=True
            )
        )
        await context.send(embed=embed)
        
    @commands.command(
        name="giveawaydonate",
        aliases=["gdonate", "gdono"],
        usage="<type> | <duration> | <winners> | [requirements] | <prize> | [message]"
    )
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def giveawaydonate(
        self,
        context: commands.Context,
        *,
        gmsg: str
    ):
        """
        Donate to server giveaways.
        
        Split arguments with `|`.
        See `[p]sdonatehelp` to know how to donate.
        """
        chan = await self.config.guild(context.guild).gchannel_id()
        
        if not chan:
            return await context.send("No giveaway donation request channel set.")
        
        gdonos = gmsg.split("|")
        await context.tick()
        await self.send_to_g_chan(context=context, chan_id=chan, g_values=gdonos)
        
    @commands.command(
        name="eventdonate",
        aliases=["edonate", "edono"],
        usage="<type> | <event> | [requirements] | <prize> | [message]"
    )
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def eventdonate(
        self,
        context: commands.Context,
        *,
        emsg: str
    ):
        """
        Donate to server events.
        
        Split arguments with `|`.
        See `[p]sdonatehelp` to know how to donate.
        """
        chan = await self.config.guild(context.guild).echannel_id()
        
        if not chan:
            return await context.send("No event donation request channel set.")
            
        edonos = emsg.split("|")
        await context.tick()
        await self.send_to_e_chan(context=context, chan_id=chan, e_values=edonos)
        
    @commands.command(
        name="heistdonate",
        aliases=["hdonate", "hdono"],
        usage="<type> | <amount> | [requirements] | [message]"
    )
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def heistdonate(
        self,
        context: commands.Context,
        *,
        hmsg: str
    ):
        """
        Donate to server heists.
        
        Split arguments with `|`.
        This command is especially designed for Bro bot and/or Dank Memer Bot or any other bot that has the similar feature.
        See `[p]sdonatehelp` to know how to donate.
        """
        chan = await self.config.guild(context.guild).hchannel_id()
        
        if not chan:
            return await context.send("No heist donation request channel set.")
            
        hdonos = hmsg.split("|")
        await context.tick()
        await self.send_to_h_chan(context=context, chan_id=chan, h_values=hdonos)
