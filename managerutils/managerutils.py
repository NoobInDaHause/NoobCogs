import asyncio
import contextlib
import datetime
import discord
import logging

try:
    from slashtags import menu
    from redbot.core.utils.menus import DEFAULT_CONTROLS
except ModuleNotFoundError:
    from redbot.core.utils.menus import DEFAULT_CONTROLS, menu
from redbot.core import Config, commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list, box
from redbot.core.utils.predicates import MessagePredicate

from . import url_button
from .utils import *

from typing import Literal

RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]

class ManagerUtils(commands.Cog):
    """
    Some utility commands that are useful for managers from servers.
    
    Utility cog for server giveaway, event or heist managers.
    Formerly called serverevents.
    """
    
    def __init__(self, bot: Red) -> None:
        self.bot = bot
        
        self.config = Config.get_conf(self, identifier=3454365754648, force_registration=True)
        default_guild_settings = {
            "auto_delete_commands": False,
            "giveaway_manager_ids": [],
            "event_manager_ids": [],
            "heist_manager_ids": [],
            "giveaway_ping_role_id": None,
            "event_ping_role_id": None,
            "heist_ping_role_id": None,
            "giveaway_log_channel_id": None,
            "event_log_channel_id": None,
            "heist_log_channel_id": None,
            "giveaway_announcement_channel_ids": [],
            "event_announcement_channel_ids": [],
            "heist_announcement_channel_ids": [],
            "giveaway_embed": {
                "title": None,
                "colour": None,
                "footer": None,
                "footer_icon": None,
                "description": None,
            },
            "event_embed": {
                "title": None,
                "colour": None,
                "footer": None,
                "footer_icon": None,
                "thumbnail": None,
                "field_1": None,
                "field_2": None,
                "field_3": None,
                "field_4": None,
                "field_5": None,
                "field_value_1": None,
                "field_value_2": None,
                "field_value_3": None,
                "field_value_4": None,
                "field_value_5": None,
                "field_inline_1": False,
                "field_inline_2": True,
                "field_inline_3": True,
                "field_inline_4": False,
                "field_inline_5": False,
            },
            "heist_embed": {
                "title": None,
                "colour": None,
                "footer": None,
                "footer_icon": None,
                "thumbnail": None,
                "field_1": None,
                "field_2": None,
                "field_3": None,
                "field_4": None,
                "field_5": None,
                "field_value_1": None,
                "field_value_2": None,
                "field_value_3": None,
                "field_value_4": None,
                "field_value_5": None,
                "field_inline_1": True,
                "field_inline_2": True,
                "field_inline_3": False,
                "field_inline_4": False,
                "field_inline_5": False,
            }
        }
        self.config.register_guild(**default_guild_settings)
        self.log = logging.getLogger("red.WintersCogs.ManagerUtils")
        
    __version__ = "1.3.8"
    __author__ = ["Noobindahause#2808"]
    
    def format_help_for_context(self, ctx: commands.Context) -> str:
        """
        Thanks Sinbad and sravan!
        """
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\n\nCog Version: {self.__version__}\nCog Author: {humanize_list([f'{auth}' for auth in self.__author__])}"
    
    async def red_delete_data_for_user(
        self, *, requester: RequestType, user_id: int
    ) -> None:
        # This cog does not store any end user data whatsoever. Also thanks sravan!
        super().red_delete_data_for_user(requester=requester, user_id=user_id)
    
    @commands.group(name="managerutilsset", aliases=["muset"])
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @commands.admin_or_permissions(manage_guild=True, administrator=True)
    async def managerutilsset(self, ctx):
        """
        Guild settings for server events.
        
        See sub commands.
        """
        
    @managerutilsset.group(name="manager", aliases=["managers"])
    async def managerutilsset_manager(self, ctx):
        """
        Set or remove the giveaway, event or heist manager roles.
        
        These roles will have access to the manager only commands.
        """
        
    @managerutilsset_manager.group(name="giveaways", aliases=["giveaway", "gaw"])
    async def managerutilsset_manager_giveaways(self, ctx):
        """
        Add or remove a role in the list of giveaway manager role.
        """
    
    @managerutilsset_manager_giveaways.command(name="add")
    async def managerutilsset_manager_giveaways_add(self, ctx: commands.Context, role: discord.Role):
        """
        Add a role to the list of giveaway managers.
        """
        if role.id in await self.config.guild(ctx.guild).giveaway_manager_ids():
            return await ctx.send("That role is already in the list of giveaway managers.")
        
        async with self.config.guild(ctx.guild).giveaway_manager_ids() as gmans:
            gmans.append(role.id)
        await ctx.send(f"Successfully added `@{role.name}` in the list of giveaway manager roles.")
    
    @managerutilsset_manager_giveaways.command(name="remove")
    async def managerutilsset_manager_giveaways_remove(self, ctx: commands.Context, role: discord.Role):
        """
        Remove a role from the list of giveaway managers.
        """
        if not await self.config.guild(ctx.guild).giveaway_manager_ids():
            return await ctx.send("It appears there are no roles from the list of giveaway managers.")
        
        if role.id not in await self.config.guild(ctx.guild).giveaway_manager_ids():
            return await ctx.send("It appears that role is not in the list of giveaway managers.")
        
        async with self.config.guild(ctx.guild).giveaway_manager_ids() as gmans:
            index = gmans.index(role.id)
            gmans.pop(index)
        await ctx.send(f"Successfully removed `@{role.name}` from the list of giveaway manager roles.")
    
    @managerutilsset_manager_giveaways.command(name="clear")
    async def managerutilsset_manager_giveaways_clear(self, ctx):
        """
        Clear the list of giveaway manager roles.
        
        If you are too lazy to remove each role one by one from the list of giveaway managers, then say no more cause this command is for you.
        There is an alternative command `[p]muset reset` but that command resets the whole guild's settings.
        """
        await ctx.send("Are you sure you want to clear the list of giveaway managers? (`yes`/`no`)")

        pred = MessagePredicate.yes_or_no(ctx)
        try:
            await ctx.bot.wait_for("message", check=pred, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to respond. Cancelling.")

        if not pred.result:
            return await ctx.send("Alright not doing that then.")
        
        await self.config.guild(ctx.guild).giveaway_manager_ids.clear()
        await ctx.send("Successfully cleared the list of giveaway manager roles.")
    
    @managerutilsset_manager.group(name="events", aliases=["event"])
    async def managerutilsset_manager_events(self, ctx):
        """
        Add or remove a role from the list of event manager roles.
        """
        
    @managerutilsset_manager_events.command(name="add")
    async def managerutilsset_manager_events_add(self, ctx: commands.Context, role: discord.Role):
        """
        Add a role to the list of event managers.
        """
        if role.id in await self.config.guild(ctx.guild).event_manager_ids():
            return await ctx.send("That role is already in the list of event managers.")
        
        async with self.config.guild(ctx.guild).event_manager_ids() as emans:
            emans.append(role.id)
        await ctx.send(f"Successfully added `@{role.name}` in the list of event manager roles.")
    
    @managerutilsset_manager_events.command(name="remove")
    async def managerutilsset_manager_events_remove(self, ctx: commands.Context, role: discord.Role):
        """
        Remove a role from the list of event managers.
        """
        if not await self.config.guild(ctx.guild).event_manager_ids():
            return await ctx.send("It appears there are no roles from the list of event managers.")
        
        if role.id not in await self.config.guild(ctx.guild).event_manager_ids():
            return await ctx.send("It appears that role is not in the list of event managers.")
        
        async with self.config.guild(ctx.guild).event_manager_ids() as emans:
            index = emans.index(role.id)
            emans.pop(index)
        await ctx.send(f"Successfully removed `@{role.name}` from the list of giveaway manager roles.")
    
    @managerutilsset_manager_events.command(name="clear")
    async def managerutilsset_manager_events_clear(self, ctx):
        """
        Clear the list of event manager roles.
        
        If you are too lazy to remove each role one by one from the list of event managers, then say no more cause this command is for you.
        There is an alternative command `[p]muset reset` but that command resets the whole guild's settings.
        """
        await ctx.send("Are you sure you want to clear the list of event managers? (`yes`/`no`)")

        pred = MessagePredicate.yes_or_no(ctx)
        try:
            await ctx.bot.wait_for("message", check=pred, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to respond. Cancelling.")

        if not pred.result:
            return await ctx.send("Alright not doing that then.")
        
        await self.config.guild(ctx.guild).event_manager_ids.clear()
        await ctx.send("Successfully cleared the list of event manager roles.")
    
    @managerutilsset_manager.group(name="heists", aliases=["heist"])
    async def managerutilsset_manager_heists(self, ctx):
        """
        Add or remove a role from the list of heist manager role.
        """
        
    @managerutilsset_manager_heists.command(name="add")
    async def managerutilsset_manager_heists_add(self, ctx: commands.Context, role: discord.Role):
        """
        Add a role to the list of heist managers.
        """
        if role.id in await self.config.guild(ctx.guild).heist_manager_ids():
            return await ctx.send("That role is already in the list of heist managers.")
        
        async with self.config.guild(ctx.guild).heist_manager_ids() as hmans:
            hmans.append(role.id)
        await ctx.send(f"Successfully added `@{role.name}` in the list of heist manager roles.")
    
    @managerutilsset_manager_heists.command(name="remove")
    async def managerutilsset_manager_heists_remove(self, ctx: commands.Context, role: discord.Role):
        """
        Remove a role from the list of heist managers.
        """
        if not await self.config.guild(ctx.guild).heist_manager_ids():
            return await ctx.send("It appears there are no roles from the list of heist managers.")
        
        if role.id not in await self.config.guild(ctx.guild).heist_manager_ids():
            return await ctx.send("It appears that role is not in the list of heist managers.")
        
        async with self.config.guild(ctx.guild).heist_manager_ids() as hmans:
            index = hmans.index(role.id)
            hmans.pop(index)
        await ctx.send(f"Successfully removed `@{role.name}` from the list of heist manager roles.")
    
    @managerutilsset_manager_heists.command(name="clear")
    async def managerutilsset_manager_heists_clear(self, ctx):
        """
        Clear the list of heist manager roles.
        
        If you are too lazy to remove each role one by one from the list of heist managers, then say no more cause this command is for you.
        There is an alternative command `[p]muset reset` but that command resets the whole guild's settings.
        """
        await ctx.send("Are you sure you want to clear the list of heist managers? (`yes`/`no`)")

        pred = MessagePredicate.yes_or_no(ctx)
        try:
            await ctx.bot.wait_for("message", check=pred, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to respond. Cancelling.")

        if not pred.result:
            return await ctx.send("Alright not doing that then.")
        
        await self.config.guild(ctx.guild).heist_manager_ids.clear()
        await ctx.send("Successfully cleared the list of heist manager roles.")
    
    @managerutilsset.group(name="pingrole", aliases=["prole"])
    async def managerutilsset_pingrole(self, ctx):
        """
        Set or remove the giveaway, event or heist ping roles.
        
        These are the roles that gets pinged for giveaways, events or heists.
        """
    
    @managerutilsset_pingrole.command(name="giveaways", aliases=["giveaway", "gaw"])
    async def managerutilsset_pingrole_giveaways(self, ctx: commands.Context, role: discord.Role = None):
        """
        Set or remove the giveaway ping role.
        
        Pass without role to remove the current set one.
        """
        if not role:
            if not await self.config.guild(ctx.guild).giveaway_ping_role_id():
                return await ctx.send("It appears you do not have a giveaway ping role set.")
            await self.config.guild(ctx.guild).giveaway_ping_role_id.clear()
            return await ctx.send("The set giveaway ping role has been removed.")
        
        if role.id == await self.config.guild(ctx.guild).giveaway_ping_role_id():
            return await ctx.send("That role is already the set giveaway ping role.")
        
        await self.config.guild(ctx.guild).giveaway_ping_role_id.set(role.id)
        return await ctx.send(f"Successfully set `@{role.name}` as the giveaway ping role.")
    
    @managerutilsset_pingrole.command(name="events", aliases=["event"])
    async def managerutilsset_pingrole_events(self, ctx: commands.Context, role: discord.Role = None):
        """
        Set or remove the event ping role.
        
        Pass without role to remove the current set one.
        """
        if not role:
            if not await self.config.guild(ctx.guild).event_ping_role_id():
                return await ctx.send("It appears you do not have an event ping role set.")
            await self.config.guild(ctx.guild).event_ping_role_id.clear()
            return await ctx.send("The set event ping role has been removed.")
        
        if role.id == await self.config.guild(ctx.guild).event_ping_role_id():
            return await ctx.send("That role is already the set event ping role.")
        
        await self.config.guild(ctx.guild).event_ping_role_id.set(role.id)
        return await ctx.send(f"Successfully set `@{role.name}` as the event ping role.")
    
    @managerutilsset_pingrole.command(name="heists", aliases=["heist"])
    async def managerutilsset_pingrole_heists(self, ctx: commands.Context, role: discord.Role = None):
        """
        Set or remove the heist ping role.
        
        Pass without role to remove the current set one.
        """
        if not role:
            if not await self.config.guild(ctx.guild).heist_ping_role_id():
                return await ctx.send("It appears you do not have a heist ping role set.")
            await self.config.guild(ctx.guild).heist_ping_role_id.clear()
            return await ctx.send("The set heist ping role has been removed.")
        
        if role.id == await self.config.guild(ctx.guild).heist_ping_role_id():
            return await ctx.send("That role is already the set heist ping role.")
        
        await self.config.guild(ctx.guild).heist_ping_role_id.set(role.id)
        return await ctx.send(f"Successfully set `@{role.name}` as the heist ping role.")
    
    @managerutilsset.group(name="logchannel", aliases=["logchan"])
    async def managerutilsset_logchannel(self, ctx):
        """
        Set or remove the giveaway, event or heist log channel.
        
        These are the log channels where the giveaway, event or heist ping command is used.
        """
        
    @managerutilsset_logchannel.command(name="giveaways", aliases=["giveaway", "gaw"])
    async def managerutilsset_logchannel_giveaways(self, ctx: commands.Context, channel: discord.TextChannel = None):
        """
        Set or remove the giveaway log channel.
        
        Pass without channel to remove the current set one.
        """
        if not channel:
            if not await self.config.guild(ctx.guild).giveaway_log_channel_id():
                return await ctx.send("It appears you do not have a set giveaway log channel.")
            await self.config.guild(ctx.guild).giveaway_log_channel_id.clear()
            return await ctx.send("The giveaway log channel has been removed.")
        
        if channel.id == await self.config.guild(ctx.guild).giveaway_log_channel_id():
            return await ctx.send("That channel is already the set giveaway log channel.")
        
        await self.config.guild(ctx.guild).giveaway_log_channel_id.set(channel.id)
        return await ctx.send(f"Successfully set {channel.mention} as the giveaway log channel.")
    
    @managerutilsset_logchannel.command(name="events", aliases=["event"])
    async def managerutilsset_logchannel_events(self, ctx: commands.Context, channel: discord.TextChannel = None):
        """
        Set or remove the event log channel.
        
        Pass without channel to remove the current set one.
        """
        if not channel:
            if not await self.config.guild(ctx.guild).event_log_channel_id():
                return await ctx.send("It appears you do not have a set event log channel.")
            await self.config.guild(ctx.guild).event_log_channel_id.clear()
            return await ctx.send("The event log channel has been removed.")
        
        if channel.id == await self.config.guild(ctx.guild).event_log_channel_id():
            return await ctx.send("That channel is already the set event log channel.")
        
        await self.config.guild(ctx.guild).event_log_channel_id.set(channel.id)
        return await ctx.send(f"Successfully set {channel.mention} as the event log channel.")
    
    @managerutilsset_logchannel.command(name="heists", aliases=["heist"])
    async def managerutilsset_logchannel_heists(self, ctx: commands.Context, channel: discord.TextChannel = None):
        """
        Set or remove the heist log channel.
        
        Pass without channel to remove the current set one.
        """
        if not channel:
            if not await self.config.guild(ctx.guild).heist_log_channel_id():
                return await ctx.send("It appears you do not have a set heist log channel.")
            await self.config.guild(ctx.guild).heist_log_channel_id.clear()
            return await ctx.send("The heist log channel has been removed.")
        
        if channel.id == await self.config.guild(ctx.guild).heist_log_channel_id():
            return await ctx.send("That channel is already the set heist log channel.")
        
        await self.config.guild(ctx.guild).heist_log_channel_id.set(channel.id)
        return await ctx.send(f"Successfully set {channel.mention} as the heist log channel.")
    
    @managerutilsset.group(name="announcechannel", aliases=["announcechan", "achan"])
    async def managerutilsset_announcechannel(self, ctx):
        """
        Add or remove the giveaway, event, or heist announcement channel.
        
        These are the channels for giveaway, event or heist announcement channel.
        """
    
    @managerutilsset_announcechannel.group(name="giveaways", aliases=["giveaway", "gaw"])
    async def managerutilsset_announcechannel_giveaways(self, ctx):
        """
        Add or remove a giveaway announcements channel.
        
        These channels are required to run the `[p]gping` command.
        """
        
    @managerutilsset_announcechannel_giveaways.command(name="add")
    async def managerutilsset_announcechannel_giveaways_add(self, ctx: commands.Context, channel: discord.TextChannel):
        """
        Add a channel to the list of giveaway announcements channel.
        
        Use `[p]muset announcechan giveaways remove` to remove a channel from the list of giveaway announcement channel.
        """
        if channel.id in await self.config.guild(ctx.guild).giveaway_announcement_channel_ids():
            return await ctx.send("That channel is already in the list of giveaway announcement channel.")
        
        async with self.config.guild(ctx.guild).giveaway_announcement_channel_ids() as gc:
            gc.append(channel.id)
        return await ctx.send(f"Successfully added {channel.mention} in the list of giveaway announcement channel.")
    
    @managerutilsset_announcechannel_giveaways.command(name="remove")
    async def managerutilsset_announcechannel_giveaways_remove(self, ctx: commands.Context, channel: discord.TextChannel):
        """
        Remove a channel from the list of giveaway announcements channel.
        
        Use `[p]muset announcechan giveaways add` to add a channel in the list of giveaway announcement channel.
        """
        if channel.id not in await self.config.guild(ctx.guild).giveaway_announcement_channel_ids():
            return await ctx.send("That channel is not in the list of giveaway announcement channel.")
        
        async with self.config.guild(ctx.guild).giveaway_announcement_channel_ids() as gc:
            index = gc.index(channel.id)
            gc.pop(index)
        return await ctx.send(f"Successfully removed {channel.mention} from the list of giveaway announcement channel.")
    
    @managerutilsset_announcechannel_giveaways.command(name="clear")
    async def managerutilsset_announcechannel_giveaways_clear(self, ctx):
        """
        Clear the list of giveaway announcement channel.
        
        If you are too lazy to remove each channel one by one from the list of giveaway announcement channel, then say no more cause this command is for you.
        There is an alternative command `[p]muset reset` but that command resets the whole guild's settings.
        """
        await ctx.send("Are you sure you want to clear the list of giveaway announcement channel? (`yes`/`no`)")

        pred = MessagePredicate.yes_or_no(ctx)
        try:
            await ctx.bot.wait_for("message", check=pred, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to respond. Cancelling.")

        if not pred.result:
            return await ctx.send("Alright not doing that then.")
        
        await self.config.guild(ctx.guild).giveaway_announcement_channel_ids.clear()
        return await ctx.send("Successfully cleared the list of giveaway announcement channel.")
    
    @managerutilsset_announcechannel.group(name="events", aliases=["event"])
    async def managerutilsset_announcechannel_events(self, ctx):
        """
        Add or remove a event announcements channel.
        
        These channels are required to run the `[p]eping` command.
        """
        
    @managerutilsset_announcechannel_events.command(name="add")
    async def managerutilsset_announcechannel_events_add(self, ctx: commands.Context, channel: discord.TextChannel):
        """
        Add a channel to the list of event announcements channel.
        
        Use `[p]muset announcechan events remove` to remove a channel from the list of event announcement channel.
        """
        if channel.id in await self.config.guild(ctx.guild).event_announcement_channel_ids():
            return await ctx.send("That channel is already in the list of event announcement channel.")
        
        async with self.config.guild(ctx.guild).event_announcement_channel_ids() as ec:
            ec.append(channel.id)
        return await ctx.send(f"Successfully added {channel.mention} in the list of event announcement channel.")
    
    @managerutilsset_announcechannel_events.command(name="remove")
    async def managerutilsset_announcechannel_events_remove(self, ctx: commands.Context, channel: discord.TextChannel):
        """
        Remove a channel from the list of event announcements channel.
        
        Use `[p]muset announcechan events add` to add a channel in the list of event announcement channel.
        """
        if channel.id not in await self.config.guild(ctx.guild).event_announcement_channel_ids():
            return await ctx.send("That channel is not in the list of event announcement channel.")
        
        async with self.config.guild(ctx.guild).event_announcement_channel_ids() as ec:
            index = ec.index(channel.id)
            ec.pop(index)
        return await ctx.send(f"Successfully removed {channel.mention} from the list of event announcement channel.")
    
    @managerutilsset_announcechannel_events.command(name="clear")
    async def managerutilsset_announcechannel_events_clear(self, ctx):
        """
        Clear the list of event announcement channel.
        
        If you are too lazy to remove each channel one by one from the list of event announcement channel, then say no more cause this command is for you.
        There is an alternative command `[p]muset reset` but that command resets the whole guild's settings.
        """
        await ctx.send("Are you sure you want to clear the list of event announcement channel? (`yes`/`no`)")

        pred = MessagePredicate.yes_or_no(ctx)
        try:
            await ctx.bot.wait_for("message", check=pred, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to respond. Cancelling.")

        if not pred.result:
            return await ctx.send("Alright not doing that then.")
        
        await self.config.guild(ctx.guild).event_announcement_channel_ids.clear()
        return await ctx.send("Successfully cleared the list of event announcement channel.")
    
    @managerutilsset_announcechannel.group(name="heists", aliases=["heist"])
    async def managerutilsset_announcechannel_heists(self, ctx):
        """
        Add or remove a heist announcements channel.
        
        These channels are required to run the `[p]hping` command.
        """
        
    @managerutilsset_announcechannel_heists.command(name="add")
    async def managerutilsset_announcechannel_heists_add(self, ctx: commands.Context, channel: discord.TextChannel):
        """
        Add a channel to the list of heist announcements channel.
        
        Use `[p]muset announcechan heists remove` to remove a channel from the list of heist announcement channel.
        """
        if channel.id in await self.config.guild(ctx.guild).heist_announcement_channel_ids():
            return await ctx.send("That channel is already in the list of heist announcement channel.")
        
        async with self.config.guild(ctx.guild).heist_announcement_channel_ids() as hc:
            hc.append(channel.id)
        return await ctx.send(f"Successfully added {channel.mention} in the list of heist announcement channel.")
    
    @managerutilsset_announcechannel_heists.command(name="remove")
    async def managerutilsset_announcechannel_heists_remove(self, ctx: commands.Context, channel: discord.TextChannel):
        """
        Remove a channel from the list of heist announcements channel.
        
        Use `[p]muset announcechan heists add` to add a channel in the list of heist announcement channel.
        """
        if channel.id not in await self.config.guild(ctx.guild).heist_announcement_channel_ids():
            return await ctx.send("That channel is not in the list of heist announcement channel.")
        
        async with self.config.guild(ctx.guild).heist_announcement_channel_ids() as hc:
            index = hc.index(channel.id)
            hc.pop(index)
        return await ctx.send(f"Successfully removed {channel.mention} from the list of heist announcement channel.")
    
    @managerutilsset_announcechannel_heists.command(name="clear")
    async def managerutilsset_announcechannel_heists_clear(self, ctx):
        """
        Clear the list of heist announcement channel.
        
        If you are too lazy to remove each channel one by one from the list of heist announcement channel, then say no more cause this command is for you.
        There is an alternative command `[p]muset reset` but that command resets the whole guild's settings.
        """
        await ctx.send("Are you sure you want to clear the list of heist announcement channel? (`yes`/`no`)")

        pred = MessagePredicate.yes_or_no(ctx)
        try:
            await ctx.bot.wait_for("message", check=pred, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to respond. Cancelling.")

        if not pred.result:
            return await ctx.send("Alright not doing that then.")
        
        await self.config.guild(ctx.guild).heist_announcement_channel_ids.clear()
        return await ctx.send("Successfully cleared the list of heist announcement channel.")
    
    @managerutilsset.command(name="autodelete", aliases=["autodel"])
    async def managerutilsset_autodelete(self, ctx):
        """
        Toggle whether to automatically delete the manager commands.
        
        Useful if you want it to be clean and show only the ping and embed.
        """
        current = await self.config.guild(ctx.guild).auto_delete_commands()
        await self.config.guild(ctx.guild).auto_delete_commands.set(not current)
        status = "will not" if current else "will"
        return await ctx.send(f" I {status} automatically delete invoked manager commands.")
    
    @managerutilsset.command(name="showsetting", aliases=["showsettings", "ss", "showset"])
    async def managerutilsset_showsettings(self, ctx):
        """
        See the current settings for this guild.
        """
        settings = await self.config.guild(ctx.guild).all()

        gmanrole = humanize_list([f'<@&{role}>' for role in settings["giveaway_manager_ids"]]) if settings["giveaway_manager_ids"] else "No giveaway managers set."

        emanrole = humanize_list([f'<@&{role}>' for role in settings["event_manager_ids"]]) if settings["event_manager_ids"] else "No event managers set."

        hmanrole = humanize_list([f'<@&{role}>' for role in settings["heist_manager_ids"]]) if settings["heist_manager_ids"] else "No heist managers set."

        groleid = settings["giveaway_ping_role_id"]
        gpingrole = f"<@&{groleid}>" if groleid else "No giveaway ping role set."

        eroleid = settings["event_ping_role_id"]
        epingrole = f"<@&{eroleid}>" if eroleid else "No event ping role set."

        hroleid = settings["heist_ping_role_id"]
        hpingrole = f"<@&{hroleid}>" if hroleid else "No heist ping role set."

        glogid = settings["giveaway_log_channel_id"]
        glogchan = f"<#{glogid}>" if glogid else "No giveaway log channel set."

        elogid = settings["event_log_channel_id"]
        elogchan = f"<#{elogid}>" if elogid else "No event log channel set."

        hlogid = settings["heist_log_channel_id"]
        hlogchan = f"<#{hlogid}>" if hlogid else "No heist log channel set."

        gannchan = humanize_list([f'<#{channel}>' for channel in settings["giveaway_announcement_channel_ids"]]) if settings["giveaway_announcement_channel_ids"] else "No giveaway announcement channels set."

        eannchan = humanize_list([f'<#{channel}>' for channel in settings["event_announcement_channel_ids"]]) if settings["event_announcement_channel_ids"] else "No event announcement channels set."

        hannchan = humanize_list([f'<#{channel}>' for channel in settings["heist_announcement_channel_ids"]]) if settings["heist_announcement_channel_ids"] else "No heist announcement channels set."

        em1 = discord.Embed(
            title="Manager role settings",
            colour=await ctx.embed_colour(),
        )
        em1.set_author(name=f"Settings for [{ctx.guild}]", icon_url=ctx.guild.icon_url)
        em1.set_footer(text=f"Command executed by: {ctx.author} | Page (1/4)", icon_url=ctx.author.avatar_url)
        em1.add_field(name="Giveaway Manager Role:", value=gmanrole, inline=False)
        em1.add_field(name="Event Manager Role:", value=emanrole, inline=False)
        em1.add_field(name="Heist Manager Role:", value=hmanrole, inline=False)
        
        em2 = discord.Embed(
            title="Ping role settings",
            colour=await ctx.embed_colour(),
        )
        em2.set_author(name=f"Settings for [{ctx.guild}]", icon_url=ctx.guild.icon_url)
        em2.set_footer(text=f"Command executed by: {ctx.author} | Page (2/4)", icon_url=ctx.author.avatar_url)
        em2.add_field(name="Giveaway Ping Role:", value=gpingrole, inline=False)
        em2.add_field(name="Event Ping Role:", value=epingrole, inline=False)
        em2.add_field(name="Heist Ping Role:", value=hpingrole, inline=False)
        
        em3 = discord.Embed(
            title="Log channel settings",
            colour=await ctx.embed_colour(),
        )
        em3.set_author(name=f"Settings for [{ctx.guild}]", icon_url=ctx.guild.icon_url)
        em3.set_footer(text=f"Command executed by: {ctx.author} | Page (3/4)", icon_url=ctx.author.avatar_url)
        em3.add_field(name="Giveaway Log Channel:", value=glogchan, inline=False)
        em3.add_field(name="Event Log Channel:", value=elogchan, inline=False)
        em3.add_field(name="Heist Log Channel:", value=hlogchan, inline=False)
        
        em4 = discord.Embed(
            title="Announcement channel settings",
            colour=await ctx.embed_colour(),
        )
        em4.set_author(name=f"Settings for [{ctx.guild}]", icon_url=ctx.guild.icon_url)
        em4.set_footer(text=f"Command executed by: {ctx.author} | Page (4/4)", icon_url=ctx.author.avatar_url)
        em4.add_field(name="Giveaway Announcement Channels:", value=gannchan, inline=False)
        em4.add_field(name="Event Announcement Channels:", value=eannchan, inline=False)
        em4.add_field(name="Heist Announcement Channel:", value=hannchan, inline=False)
        
        embeds = [em1, em2, em3, em4]
        return await menu(ctx, embeds, controls=DEFAULT_CONTROLS, timeout=60)
    
    @managerutilsset.command(name="reset")
    async def managerutils_reset(self, ctx):
        """
        Reset the guild settings to default.
        """
        await ctx.send("Are you sure you want to reset the managerutils guild settings? (`yes`/`no`)")

        pred = MessagePredicate.yes_or_no(ctx)
        try:
            await ctx.bot.wait_for("message", check=pred, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to respond. Cancelling.")

        if not pred.result:
            return await ctx.send("Alright not doing that then.")
        
        await self.config.guild(ctx.guild).clear()
        return await ctx.send("Successfully resetted the guild's settings.")
            
    @commands.command(name="managerutilshelp", aliases=["muhelp"])
    @commands.bot_has_permissions(embed_links=True)
    async def managerutilshelp(self, ctx):
        """
        Know how to use the manager utils commands.
        
        Available commands:
        `[p]giveawayping
        [p]eventping
        [p]heistping`
        """
        gping = f"Syntax: {ctx.prefix}giveawayping <sponsor> | <prize> | [message]\nAlias: {ctx.prefix}gping"
        eping = f"Syntax: {ctx.prefix}eventping <sponsor> | <event_name> | <prize> | [requirements] | [message]\nAlias: {ctx.prefix}eping"
        hping = f"Syntax: {ctx.prefix}heistping <sponsor> | <amount> | [requirements] | [message]\nAlias: {ctx.prefix}hping"
        
        d1 = f"""
        {box(gping, "yaml")}
        *Arguments:*
        **Sponsor**
        ` - ` The sponsor mention required for the sponsor field.
        **Prize**
        ` - ` The prize of the giveaway.
        **Message**
        ` - ` The optional message from the sponsor.
        ` - ` Pass `none` if None.
        
        Examples:
            `{ctx.prefix}giveawayping @Noobindahause | 69 million coins | I am rich af. :moneybag:`
            `{ctx.prefix}gping @Noobindahause | 10 karuta tickets | not really playing this bot much so here you go.`
        """
        
        d2 = f"""
        {box(eping, "yaml")}
        *Arguments*
        **Sponsor**
        ` - ` The sponsor mention required for the sponsor field.
        **Event_Name**
        ` - ` The name or type of the event.
        **Requirements**
        ` - ` The optional requirements for the event. (this can be anything like roles, messages, do this do that or anything you can imagine)
        ` - ` Pass `none` if None.
        **Prize**
        ` - ` The prize of the event.
        **Message**
        ` - ` The optional message from the sponsor.
        ` - ` Pass `none` if None.
        
        Examples:
            `{ctx.prefix}eventping @Noobindahause | gtn | 10 million bro coins | Broooooooo :sunglasses:`
            `{ctx.prefix}eping @Noobindahause | skirbble | basic nitro | I am rich af V2 :money_mouth:.`
        """
        
        d3 = f"""
        {box(hping, "yaml")}
        *Arguments*
        **Sponsor**
        ` - ` The sponsor mention required for the sponsor field.
        **Amount**
        ` - ` The amount of coins to heist.
        **Requirements**
        ` - ` The optional requirements for the event. (this can be anything like roles, messages, do this do that or anything you can imagine)
        ` - ` Pass `none` if None.
        **Message**
        ` - ` The optional message from the sponsor.
        ` - ` Pass `none` if None.
        
        Examples:
            `{ctx.prefix}heistping @Noobindahause | 10 million bro coins | amari level 5 | Time for bro heist`
            `{ctx.prefix}hping @Noobindahause | 1 billion dank coins | @somerolemention | I am rich af V3 :credit_card:.`
        """
        
        em1 = discord.Embed(
            title=f"How to use `{ctx.prefix}giveawayping` command",
            description=d1,
            colour=await ctx.embed_colour(),
        ).set_footer(text=f"Command executed by: {ctx.author} | Page 1/3", icon_url=ctx.author.avatar_url)
        
        em2 = discord.Embed(
            title=f"How to use `{ctx.prefix}eventping` command",
            description=d2,
            colour=await ctx.embed_colour()
        ).set_footer(text=f"Command executed by: {ctx.author} | Page 2/3", icon_url=ctx.author.avatar_url)
        
        em3 = discord.Embed(
            title=f"How to use `{ctx.prefix}heistping` command",
            description=d3,
            colour=await ctx.embed_colour()
        ).set_footer(text=f"Command executed by: {ctx.author} | Page 3/3", icon_url=ctx.author.avatar_url)
        
        embeds = [em1, em2, em3]
        return await menu(ctx, embeds, controls=DEFAULT_CONTROLS, timeout=60)
    
    @commands.command(name="giveawayping", aliases=["gping"], usage="<sponsor> | <prize> | [message]")
    @commands.guild_only()
    @is_gman()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.bot_has_permissions(mention_everyone=True, embed_links=True)
    async def giveawayping(
        self,
        ctx: commands.Context,
        *,
        giveaways
    ):
        # sourcery skip: low-code-quality
        """
        Ping for server giveaways.
        
        See `[p]muhelp` to know how to run the commands.
        Split arguments with `|`.
        Requires set Giveaway Manager role to use this command.
        """
        settings = await self.config.guild(ctx.guild).all()
        authorizedchans = await self.config.guild(ctx.guild).giveaway_announcement_channel_ids()
        
        if not authorizedchans:
            return await ctx.send("It appears there are no authorized giveaway announcement channels. Ask an admin to add one.")
        
        if ctx.channel.id not in authorizedchans:
            return await ctx.send(f"You can not run this command in an unauthorized channel.\nAuthorized channels: {humanize_list([f'<#{channel}>' for channel in authorizedchans])}")
        
        giveaways = giveaways.split("|")
        maxargs = len(giveaways)
        
        if maxargs > 3:
            return await ctx.send(f"Argument error, perhaps you added an extra `|`, see `{ctx.prefix}muhelp` to know how to use managerutils commands.")
        if maxargs < 3:
            return await ctx.send(f"Argument error, see `{ctx.prefix}muhelp` to know how to use managerutils commands.")
        
        if await self.config.guild(ctx.guild).auto_delete_commands():
            with contextlib.suppress(Exception):
                await ctx.message.delete()
        
        if not await self.config.guild(ctx.guild).auto_delete_commands():
            with contextlib.suppress(Exception):
                await ctx.tick()
        
        glogchan = ctx.guild.get_channel(settings["giveaway_log_channel_id"])
        gpingrole = ctx.guild.get_role(settings["giveaway_ping_role_id"])
        
        gembed = discord.Embed(
            title="Server Giveaway Time!",
            description=f"**Sponsor:** {giveaways[0]}\n**Prize:** {giveaways[1]}\n**Message:** {giveaways[1]}",
            colour=await ctx.embed_colour(),
            timestamp=datetime.datetime.now(datetime.timezone.utc),
        )
        gembed.set_footer(text=f"Hosted by: {ctx.author}", icon_url=ctx.author.avatar_url)
        
        if not gpingrole:
            try:
                glog = await ctx.send(content=f"No giveaway ping role set. Use `{ctx.prefix}muset pingrole grole` to set one.", embed=gembed)
            except Exception:
                return await ctx.author.send("It appears that I not have permission to send a message from that channel.")
        
        if gpingrole:
            try:
                am = discord.AllowedMentions(roles=True, users=False, everyone=False)
                glog = await ctx.send(embed=gembed, content=gpingrole.mention, allowed_mentions=am)
            except Exception:
                return await ctx.author.send("It appears that I do not have permission to send a message from that channel.")
            
        if glogchan:
            try:
                embed = discord.Embed(
                    title="Giveaway Logging",
                    description=f"**Host:** {ctx.author.mention}\n**Channel:** {ctx.channel.mention}\n**Sponsor:** {giveaways[0]}\n**Prize:** {giveaways[1]}\n**Message:** {giveaways[2]}",
                    colour=ctx.author.colour,
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                )
                embed.set_footer(text=f"Host ID: {ctx.author.id}", icon_url=ctx.author.avatar_url)
                embed.set_thumbnail(url=ctx.guild.icon_url)
                
                button = url_button.URLButton(
                    "Jump To Giveaway Ping",
                    glog.jump_url,
                )
                await url_button.send_message(
                    self.bot,
                    settings["giveaway_log_channel_id"],
                    embed=embed,
                    url_button=button,
                )
            except Exception:
                return await ctx.send("It appears that I do not see the giveaway log channel. It's most likely deleted or I do not have permission to view it.")
            
    @commands.command(name="eventping", aliases=["eping"], usage="<sponsor> | <event_name> | <prize> | [message]")
    @commands.guild_only()
    @is_eman()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.bot_has_permissions(mention_everyone=True, embed_links=True)
    async def eventping(
        self,
        ctx: commands.Context,
        *,
        events
    ):  # sourcery skip: low-code-quality
        """
        Ping for server events.
        
        See `[p]muhelp` to know how to run the commands.
        Split arguments with `|`.
        Requires set Event Manager role to use this command.
        """
        settings = await self.config.guild(ctx.guild).all()
        authorizedchans = await self.config.guild(ctx.guild).event_announcement_channel_ids()
        
        if not authorizedchans:
            return await ctx.send("It appears there are no authorized event announcement channels. Ask an admin to add one.")
        
        if ctx.channel.id not in authorizedchans:
            return await ctx.send(f"You can not run this command in an unauthorized channel.\nAuthorized channels: {humanize_list([f'<#{channel}>' for channel in authorizedchans])}")
        
        events = events.split("|")
        maxargs = len(events)
        
        if maxargs > 4:
            return await ctx.send(f"Argument error, perhaps you added an extra `|`, see `{ctx.prefix}muhelp` to know how to use managerutils commands.")
        if maxargs < 4:
            return await ctx.send(f"Argument error, see `{ctx.prefix}muhelp` to know how to use managerutils commands.")
        
        if await self.config.guild(ctx.guild).auto_delete_commands():
            with contextlib.suppress(Exception):
                await ctx.message.delete()
        
        if not await self.config.guild(ctx.guild).auto_delete_commands():
            with contextlib.suppress(Exception):
                await ctx.tick()
                
        elogchan = ctx.guild.get_channel(settings["event_log_channel_id"])
        epingrole = ctx.guild.get_role(settings["event_ping_role_id"])
        
        eembed = discord.Embed(
            title="Server Event Time!",
            colour=await ctx.embed_colour(),
            timestamp=datetime.datetime.now(datetime.timezone.utc),
        )
        eembed.set_footer(text=f"Hosted by: {ctx.author} (ID: {ctx.author.id})", icon_url=ctx.author.avatar_url)
        eembed.set_thumbnail(url=ctx.guild.icon_url)
        eembed.add_field(name="Event Sponsor:", value=events[0], inline=False)
        eembed.add_field(name="Event Name:", value=events[1], inline=True)
        eembed.add_field(name="Event Prize:", value=events[2], inline=True)
        eembed.add_field(name="Message:", value=events[3], inline=False)
        
        if not epingrole:
            try:
                elog = await ctx.send(content=f"No event ping role set. Use `{ctx.prefix}muset pingrole erole` to set one.", embed=eembed)
            except Exception:
                return await ctx.author.send("It appears that I do not have permission to send a message from that channel.")
        
        if epingrole:
            try:
                am = discord.AllowedMentions(roles=True, users=False, everyone=False)
                elog = await ctx.send(embed=eembed, content=epingrole.mention, allowed_mentions=am)
            except Exception:
                return await ctx.author.send("It appears that I do not have permission to send a message from that channel.")
            
        if elogchan:
            try:
                embed = discord.Embed(
                    title="Event Logging",
                    description=f"**Host:** {ctx.author.mention}\n**Channel:** {ctx.channel.mention}\n**Sponsor:** {events[0]}\n**Event Name:** {events[1]}\n**Prize:** {events[2]}\n**Message:** {events[3]}",
                    colour=ctx.author.colour,
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                )
                embed.set_footer(text=f"Host ID: {ctx.author.id}", icon_url=ctx.author.avatar_url)
                embed.set_thumbnail(url=ctx.guild.icon_url)
                
                button = url_button.URLButton(
                    "Jump To Event Ping",
                    elog.jump_url,
                )
                await url_button.send_message(
                    self.bot,
                    settings["event_log_channel_id"],
                    embed=embed,
                    url_button=button,
                )
            except Exception:
                return await ctx.send("It appears that I do not see the event log channel. It's most likely deleted or I do not have permission to view it.")
            
    @commands.command(name="heistping", aliases=["hping"], usage="<sponsor> | <amount> | [requirements] | [message]")
    @commands.guild_only()
    @is_hman()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.bot_has_permissions(mention_everyone=True, embed_links=True)
    async def heistping(
        self,
        ctx: commands.Context,
        *,
        heists
    ):  # sourcery skip: low-code-quality
        """
        Ping for server heists.
        
        See `[p]muhelp` to know how to run the commands.
        Split arguments with `|`.
        Requires set Heist Manager role to use this command.
        """
        settings = await self.config.guild(ctx.guild).all()
        authorizedchans = await self.config.guild(ctx.guild).heist_announcement_channel_ids()
        
        if not authorizedchans:
            return await ctx.send("It appears there are no authorized heist announcement channels. Ask an admin to add one.")
        
        if ctx.channel.id not in authorizedchans:
            return await ctx.send(f"You can not run this command in an unauthorized channel.\nAuthorized channels: {humanize_list([f'<#{channel}>' for channel in authorizedchans])}")
        
        heists = heists.split("|")
        maxargs = len(heists)
        
        if maxargs > 4:
            return await ctx.send(f"Argument error, perhaps you added an extra `|`, see `{ctx.prefix}muhelp` to know how to use managerutils commands.")
        if maxargs < 4:
            return await ctx.send(f"Argument error, see `{ctx.prefix}muhelp` to know how to use managerutils commands.")
        
        if await self.config.guild(ctx.guild).auto_delete_commands():
            with contextlib.suppress(Exception):
                await ctx.message.delete()
        
        if not await self.config.guild(ctx.guild).auto_delete_commands():
            with contextlib.suppress(Exception):
                await ctx.tick()
                
        hlogchan = ctx.guild.get_channel(settings["heist_log_channel_id"])
        hpingrole = ctx.guild.get_role(settings["heist_ping_role_id"])
        
        hembed = discord.Embed(
            title="Server Heist Time!",
            colour=await ctx.embed_colour(),
            timestamp=datetime.datetime.now(datetime.timezone.utc),
        )
        hembed.set_footer(text=f"Hosted by: {ctx.author} (ID: {ctx.author.id})", icon_url=ctx.author.avatar_url)
        hembed.set_thumbnail(url=ctx.guild.icon_url)
        hembed.add_field(name="Heist Sponsor:", value=heists[0], inline=True)
        hembed.add_field(name="Amount:", value=heists[1], inline=True)
        hembed.add_field(name="Requirements:", value=heists[2], inline=False)
        hembed.add_field(name="Checklist:", value="` - ` Have a life saver on your inventory.\n` - ` Withdraw at least **1** coin.\n` - ` Press the big green `JOIN HEIST` button.", inline=False)
        hembed.add_field(name="Message:", value=heists[3], inline=False)
        
        if not hpingrole:
            try:
                hlog = await ctx.send(content=f"No heist ping role set. Use `{ctx.prefix}muset pingrole hrole` to set one.", embed=hembed)
            except Exception:
                return await ctx.author.send("It appears that I do not have permission to send a message from that channel.")
        
        if hpingrole:
            try:
                am = discord.AllowedMentions(roles=True, users=False, everyone=False)
                hlog = await ctx.send(embed=hembed, content=hpingrole.mention, allowed_mentions=am)
            except Exception:
                return await ctx.author.send("It appears that I do not have permission to send a message from that channel.")
        
        if hlogchan:
            try:
                embed = discord.Embed(
                    title="Heist Logging",
                    description=f"**Host:** {ctx.author.mention}\n**Channel:** {ctx.channel.mention}\n**Sponsor:** {heists[0]}\n**Amount:** {heists[1]}\n**Requirements:** {heists[2]}\n**Message:** {heists[3]}",
                    colour=ctx.author.colour,
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                )
                embed.set_footer(text=f"Host ID: {ctx.author.id}", icon_url=ctx.author.avatar_url)
                embed.set_thumbnail(url=ctx.guild.icon_url)
                
                button = url_button.URLButton(
                    "Jump To Heist Ping",
                    hlog.jump_url,
                )
                await url_button.send_message(
                    self.bot,
                    settings["heist_log_channel_id"],
                    embed=embed,
                    url_button=button,
                )
            except Exception:
                return await ctx.send("It appears that I do not see the heist log channel. It's most likely deleted or I do not have permission to view it.")
        