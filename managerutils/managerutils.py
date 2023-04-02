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
from .embed_defaults import *
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
                "content": None,
                "colour_value": None,
                "str_colour": None,
                "footer_text": None,
                "footer_icon": None,
                "thumbnail": None,
                "image": None,
                "description": None,
                "show_footer": True
            },
            "event_embed": {
                "title": None,
                "content": None,
                "description": None,
                "colour_value": None,
                "str_colour": None,
                "footer_text": None,
                "footer_icon": None,
                "image": None,
                "thumbnail": None,
                "show_footer": True,
                "sponsor_field": {
                    "name": None,
                    "value": None,
                    "inline": False
                },
                "name_field": {
                    "name": None,
                    "value": None,
                    "inline": True
                },
                "prize_field": {
                    "name": None,
                    "value": None,
                    "inline": True
                },
                "message_field": {
                    "name": None,
                    "value": None,
                    "inline": False
                },
            },
            "heist_embed": {
                "title": None,
                "content": None,
                "description": None,
                "colour_value": None,
                "str_colour": None,
                "footer_text": None,
                "footer_icon": None,
                "image": None,
                "thumbnail": None,
                "checklist_toggle": True,
                "show_footer": True,
                "hsponsor_field": {
                    "name": None,
                    "value": None,
                    "inline": True
                },
                "hamount_field": {
                    "name": None,
                    "value": None,
                    "inline": True
                },
                "hrequirements_field": {
                    "name": None,
                    "value": None,
                    "inline": False
                },
                "hmessage_field": {
                    "name": None,
                    "value": None,
                    "inline": False
                }
            }
        }
        self.config.register_guild(**default_guild_settings)
        self.log = logging.getLogger("red.WintersCogs.ManagerUtils")
        
    __version__ = "2.2.0"
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
        
    @managerutilsset.group(name="embed")
    async def managerutilsset_embed(self, ctx):
        """
        Customize the giveaway, event or heist embed to your liking.
        """
    
    @managerutilsset_embed.group(name="giveaways", aliases=["giveaway", "gaw"])
    async def managerutilsset_embed_giveaways(self, ctx):
        """
        Customize the giveaway embed to your liking.
        """
        
    @managerutilsset_embed_giveaways.command(name="content")
    async def managerutilsset_embed_giveaways_content(self, ctx: commands.Context, *, content = None):
        """
        Customize the message content above the giveaways embed.
        
        Available variables:
        ` - ` {role} - the pingrole
        ` - ` {sponsor} - the sponsor
        ` - ` {prize} - the prize
        ` - ` {host} - the host
        ` - ` {message} - the sponsors message
        ` - ` {guild} - the guild name
        """
        if not content:
            await self.config.guild(ctx.guild).giveaway_embed.content.clear()
            return await ctx.send("Successfully resetted the giveaway embed message content.")
        
        await self.config.guild(ctx.guild).giveaway_embed.content.set(content)
        await ctx.send(f"Successfully set the giveaway embed message content to:\n{box(content, 'py')}")
    
    @managerutilsset_embed_giveaways.command(name="colour", aliases=["color"])
    async def managerutilsset_embed_giveaways_colour(self, ctx: commands.Context, colour: discord.Colour = None):
        """
        Customize the giveaway embed colour.
        
        Pass without colour to reset the color to the bots default embed color.
        """
        if not colour:
            await self.config.guild(ctx.guild).giveaway_embed.colour_value.clear()
            await self.config.guild(ctx.guild).giveaway_embed.str_colour.clear()
            return await ctx.send("Successfully resetted the giveaway embed colour.")
        
        await self.config.guild(ctx.guild).giveaway_embed.colour_value.set(colour.value)
        await self.config.guild(ctx.guild).giveaway_embed.str_colour.set(str(colour))
        await ctx.send(f"Successfully set the giveaway embed colour to:\n{box(colour, 'py')}")
    
    @managerutilsset_embed_giveaways.command(name="title")
    async def managerutilsset_embed_giveaways_title(self, ctx: commands.Context, *, title = None):
        """
        Customize the giveaway embed title.
        
        Pass without title to reset to the default title.
        
        Available variables:
        ` - ` {guild} - the guild name.
        
        This defaults to `Server Giveaway Time!`.
        """
        if not title:
            await self.config.guild(ctx.guild).giveaway_embed.title.clear()
            return await ctx.send("Successfully resetted the giveaways embed title.")
        
        await self.config.guild(ctx.guild).giveaway_embed.title.set(title)
        await ctx.send(f"Successfully set the giveaway embed title to:\n{box(title, 'py')}")
    
    @managerutilsset_embed_giveaways.command(name="thumbnail")
    async def managerutilsset_embed_giveaways_thumbnail(self, ctx: commands.Context, link = None):
        """
        Customize the giveaway embed thumbnail.
        
        Pass without link to remove it.
        
        The thumbnail defaults to `None` but if you want to add a thumbnail use this command.
        
        Available variables:
        ` - ` {host.avatar_url} - the avatar of the host
        ` - ` {guild.icon_url} - the guilds image
        
        If you use these variables please make sure to not add anything else besides the variables. 
        """
        if not link:
            await self.config.guild(ctx.guild).giveaway_embed.thumbnail.clear()
            return await ctx.send("The giveaway embed thumbnail has been removed.")
        
        await self.config.guild(ctx.guild).giveaway_embed.thumbnail.set(link)
        await ctx.send(f"Successfully set the giveaway embed tumbnail to:\n{box(link, 'py')}")
        
    @managerutilsset_embed_giveaways.command(name="image")
    async def managerutilsset_embed_giveaways_image(self, ctx: commands.Context, link = None):
        """
        Add or remove an image to the giveaways embed.
        
        Pass without link to remove it.
        
        The image defaults to `None` but if you want to add an image use this command.
        """
        if not link:
            if not await self.config.guild(ctx.guild).giveaway_embed.image():
                return await ctx.send("It appears you do not have a giveaway embed image set.")
            await self.config.guild(ctx.guild).giveaway_embed.image.clear()
            return await ctx.send("The giveaway embed image has been removed.")
        
        await self.config.guild(ctx.guild).giveaway_embed.image.set(link)
        await ctx.send(f"Successfully set the giveaway embed image to:\n{box(link, 'py')}")
    
    @managerutilsset_embed_giveaways.command(name="description", aliases=["desc"])
    async def managerutilsset_embed_giveaways_description(self, ctx: commands.Context, *, description = None):
        """
        Customize the giveaways embed description.
        
        Pass without description to reset it to default.
        
        This defaults to:
        `**Prize:** {prize}
        **Sponsor:** {sponsor}
        **Message:** {message}`
        
        Available variables:
        ` - ` {sponsor} - the sponsor
        ` - ` {prize} - the prize
        ` - ` {host} - the host
        ` - ` {message} - the sponsors message
        ` - ` {guild} - the guild name
        """
        if not description:
            await self.config.guild(ctx.guild).giveaway_embed.description.clear()
            return await ctx.send("Successfully resetted the giveaways embed description.")
        
        await self.config.guild(ctx.guild).giveaway_embed.description.set(description)
        await ctx.send(f"Successfully set the giveaways embed description to:\n{box(description, 'py')}")
    
    @managerutilsset_embed_giveaways.group(name="footer")
    async def managerutilsset_embed_giveaways_footer(self, ctx):
        """
        Customize the giveaways embed footer text or icon.
        """
    
    @managerutilsset_embed_giveaways_footer.command(name="text")
    async def managerutilsset_embed_giveaways_footer_text(self, ctx: commands.Context, *, text = None):
        """
        Customize the giveaways embed footer text.
        
        Pass without text to reset it to default.
        
        This defaults to `Hosted by: {host}`.
        
        Available variables:
        ` - ` {host} - the host name
        ` - ` {host.id} - the host ID
        ` - ` {guild} - the guild name
        """
        if not text:
            await self.config.guild(ctx.guild).giveaway_embed.footer_text.clear()
            return await ctx.send("Successfully resetted the giveaways embed footer text.")
        
        await self.config.guild(ctx.guild).giveaway_embed.footer_text.set(text)
        await ctx.send(f"Successfully set the giveaways embed footer text to:\n{box(text, 'py')}")
    
    @managerutilsset_embed_giveaways_footer.command(name="icon")
    async def managerutilsset_embed_giveaways_footer_icon(self, ctx: commands.Context, icon = None):
        """
        Customize or remove the giveaways embed footer icon.
        
        Pass without link to remove it.
        
        This defaults to hosts avatar.
        
        Available variables:
        ` - ` {host.avatar_url} - the avatar of the host
        ` - ` {guild.icon_url} - the guild image
        
        If you use one of these variables don't add anything else besides the variable that you chose.
        """
        if not icon:
            await self.config.guild(ctx.guild).giveaway_embed.footer_icon.set("removed")
            return await ctx.send("The giveaway embed footer icon has been removed.")
        
        await self.config.guild(ctx.guild).giveaway_embed.footer_icon.set(icon)
        await ctx.send(f"Successfully set the giveaway embed footer icon to:\n{box(icon, 'py')}")
    
    @managerutilsset_embed_giveaways_footer.command(name="toggle")
    async def managerutilsset_embed_giveaways_footer_remove(self, ctx):
        """
        Toggle whether to remove or add back the giveaways embed footer text and icon.
        """
        current = await self.config.guild(ctx.guild).giveaway_embed.show_footer()
        await self.config.guild(ctx.guild).giveaway_embed.show_footer.set(not current)
        status = "removed" if current else "added back"
        await ctx.send(f"The giveaways embed footer text and icon has been {status}.")
    
    @managerutilsset_embed.group(name="events", aliases=["event"])
    async def managerutilsset_embed_events(self, ctx):
        """
        Customize the event embed to your liking.
        """
    
    @managerutilsset_embed_events.command(name="content")
    async def managerutilsset_embed_events_content(self, ctx: commands.Context, *, content = None):
        """
        Customize the message content above the events embed.
        
        Available variables:
        ` - ` {role} - the pingrole
        ` - ` {sponsor} - the sponsor
        ` - ` {name} - the event name
        ` - ` {prize} - the prize
        ` - ` {host} - the host
        ` - ` {message} - the sponsors message
        ` - ` {guild} - the guild name
        """
        if not content:
            await self.config.guild(ctx.guild).event_embed.content.clear()
            return await ctx.send("Successfully resetted the event embed message content.")
        
        await self.config.guild(ctx.guild).event_embed.content.set(content)
        await ctx.send(f"Successfully set the event embed message content to:\n{box(content, 'py')}")
    
    @managerutilsset_embed_events.command(name="title")
    async def managerutilsset_embed_events_title(self, ctx: commands.Context, *, title = None):
        """
        Customize the event embed title.
        
        Pass without title to reset to the default title.
        
        Available variables:
        ` - ` {guild} - the guild name.
        
        This defaults to `Server Event Time!`.
        """
        if not title:
            await self.config.guild(ctx.guild).event_embed.title.clear()
            return await ctx.send("Successfully resetted the events embed title.")
        
        await self.config.guild(ctx.guild).event_embed.title.set(title)
        await ctx.send(f"Successfully set the event embed title to:\n{box(title, 'py')}")
    
    @managerutilsset_embed_events.command(name="colour", aliases=["color"])
    async def managerutilsset_embed_events_colour(self, ctx: commands.Context, colour: discord.Colour = None):
        """
        Customize the event embed colour.
        
        Pass without colour to reset the color to the bots default embed color.
        """
        if not colour:
            await self.config.guild(ctx.guild).event_embed.colour_value.clear()
            await self.config.guild(ctx.guild).event_embed.str_colour.clear()
            return await ctx.send("Successfully resetted the event embed colour.")
        
        await self.config.guild(ctx.guild).event_embed.colour_value.set(colour.value)
        await self.config.guild(ctx.guild).event_embed.str_colour.set(str(colour))
        await ctx.send(f"Successfully set the event embed colour to:\n{box(colour, 'py')}")
    
    @managerutilsset_embed_events.command(name="thumbnail")
    async def managerutilsset_embed_events_thumbnail(self, ctx: commands.Context, link = None):
        """
        Customize the event embed thumbnail.
        
        Pass without link to remove it.
        
        The thumbnail defaults to `{guild.icon_url}` but if you want to remove the thumbnail use this command.
        
        Available variables:
        ` - ` {host.avatar_url} - the avatar of the host
        ` - ` {guild.icon_url} - the guilds image
        
        If you use these variables please make sure to not add anything else besides the variables. 
        """
        if not link:
            await self.config.guild(ctx.guild).event_embed.thumbnail.set("removed")
            return await ctx.send("The event embed thumbnail has been removed.")
        
        await self.config.guild(ctx.guild).event_embed.thumbnail.set(link)
        await ctx.send(f"Successfully set the event embed tumbnail to:\n{box(link, 'py')}")
    
    @managerutilsset_embed_events.command(name="image")
    async def managerutilsset_embed_events_image(self, ctx: commands.Context, link = None):
        """
        Add or remove an image to the events embed.
        
        Pass without link to remove it.
        
        The image defaults to `None` but if you want to add an image use this command.
        """
        if not link:
            if not await self.config.guild(ctx.guild).event_embed.image():
                return await ctx.send("It appears you do not have an event embed image set.")
            await self.config.guild(ctx.guild).event_embed.image.clear()
            return await ctx.send("The event embed image has been removed.")
        
        await self.config.guild(ctx.guild).event_embed.image.set(link)
        await ctx.send(f"Successfully set the event embed image to:\n{box(link, 'py')}")
    
    @managerutilsset_embed_events.command(name="description", aliases=["desc"])
    async def managerutilsset_embed_events_description(self, ctx: commands.Context, *, description = None):
        """
        Customize the event embed description.
        
        Pass without description to remove it.
        
        This defaults to `None`.
        
        Available variables:
        ` - ` {sponsor} - the sponsor
        ` - ` {name} - the event name
        ` - ` {prize} - the prize
        ` - ` {host} - the host
        ` - ` {message} - the sponsors message
        ` - ` {guild} - the guild name
        """
        if not description:
            if not await self.config.guild(ctx.guild).event_embed.description():
                return await ctx.send("It appears you do not have an embed description set.")
            await self.config.guild(ctx.guild).event_embed.description.clear()
            return await ctx.send("Successfully removed the events embed description.")
        
        await self.config.guild(ctx.guild).event_embed.description.set(description)
        await ctx.send(f"Successfully set the events embed description to:\n{box(description, 'py')}")
    
    @managerutilsset_embed_events.group(name="footer")
    async def managerutilsset_embed_events_footer(self, ctx):
        """
        Customize the events embed footer text or icon.
        """
    
    @managerutilsset_embed_events_footer.command(name="text")
    async def managerutilsset_embed_events_footer_text(self, ctx: commands.Context, *, text = None):
        """
        Customize the events embed footer text.
        
        Pass without text to reset it to default.
        
        This defaults to `Hosted by: {host}`.
        
        Available variables:
        ` - ` {host} - the host name
        ` - ` {host.id} - the host ID
        ` - ` {guild} - the guild name
        """
        if not text:
            await self.config.guild(ctx.guild).event_embed.footer_text.clear()
            return await ctx.send("Successfully resetted the events embed footer text.")
        
        await self.config.guild(ctx.guild).event_embed.footer_text.set(text)
        await ctx.send(f"Successfully set the events embed footer text to:\n{box(text, 'py')}")
    
    @managerutilsset_embed_events_footer.command(name="icon")
    async def managerutilsset_embed_events_footer_icon(self, ctx: commands.Context, icon = None):
        """
        Customize or remove the events embed footer icon.
        
        Pass without link to remove it.
        
        This defaults to `{host.avatar_url}`.
        
        Available variables:
        ` - ` {host.avatar_url} - the avatar of the host
        ` - ` {guild.icon_url} - the guild image
        
        If you use one of these variables don't add anything else besides the variable that you chose.
        """
        if not icon:
            await self.config.guild(ctx.guild).event_embed.footer_icon.set("removed")
            return await ctx.send("The event embed footer icon has been removed.")
        
        await self.config.guild(ctx.guild).event_embed.footer_icon.set(icon)
        await ctx.send(f"Successfully set the event embed footer icon to:\n{box(icon, 'py')}")
    
    @managerutilsset_embed_events_footer.command(name="toggle")
    async def managerutilsset_embed_events_footer_remove(self, ctx):
        """
        Toggle whether to remove or add back the events embed footer text and icon.
        """
        current = await self.config.guild(ctx.guild).event_embed.show_footer()
        await self.config.guild(ctx.guild).event_embed.show_footer.set(not current)
        status = "removed" if current else "added back"
        await ctx.send(f"The events embed footer text and icon has been {status}.")
    
    @managerutilsset_embed_events.group(name="fields", aliases=["field"])
    async def managerutilsset_embed_events_fields(self, ctx):
        """
        Customize the event embed fields to your liking.
        """
    
    @managerutilsset_embed_events_fields.command(name="sponsor", usage="<name> | <value> | <inline>")
    async def managerutilsset_embed_events_fields_sponsor(self, ctx: commands.Context, *, sfield = None):
        """
        Customize the event embed sponsor field.
        
        Pass without arguments to reset the sponsor field.
        For the <inline> argument you must only answer with `1` for True or `0` for False and nothing else.
        Split arguments with `|`.
        
        Available variables:
        ` - ` {sponsor} - the sponsor from `[p]eventping` (can only be used in value argument.)
        """
        if not sfield:
            await self.config.guild(ctx.guild).event_embed.sponsor_field.name.clear()
            await self.config.guild(ctx.guild).event_embed.sponsor_field.value.clear()
            await self.config.guild(ctx.guild).event_embed.sponsor_field.inline.clear()
            return await ctx.send("Successfully resetted the event sponsor field.")
        
        sfield = sfield.split("|")
        maxargs = len(sfield)

        if maxargs > 3:
            return await ctx.send("Argument error, perhaps you added an extra `|`.")
        if maxargs < 3:
            return await ctx.send("Argument error, perhaps you are missing a `|`.")
        
        sponsor_name = sfield[0]
        sponsor_name.replace(" ", "")
        sponsor_value = sfield[1]
        sponsor_value.replace(" ", "")
        sponsor_inline = sfield[2]
        sponsor_inline.replace(" ", "")
        if "1" in sponsor_inline:
            sponsor_inline = True
        elif "0" in sponsor_inline:
            sponsor_inline = False
        else:
            return await ctx.send("Your answer for the `<inline>` argument should only be `1` for True or `0` for False.")
        
        await self.config.guild(ctx.guild).event_embed.sponsor_field.name.set(sponsor_name)
        await self.config.guild(ctx.guild).event_embed.sponsor_field.value.set(sponsor_value)
        await self.config.guild(ctx.guild).event_embed.sponsor_field.inline.set(sponsor_inline)
        await ctx.send(f"Successfully set the event sponsor field to:\n```py\nName: {sponsor_name}\nValue: {sponsor_value}\nInline: {sponsor_inline}```")
    
    @managerutilsset_embed_events_fields.command(name="name", usage="<name> | <value> | <inline>")
    async def managerutilsset_embed_events_fields_name(self, ctx: commands.Context, *, nfield = None):
        """
        Customize the event embed name field.
        
        Pass without arguments to reset the name field.
        For the <inline> argument you must only answer with `1` for True or `0` for False and nothing else.
        Split arguments with `|`.
        
        Available variables:
        ` - ` {name} - the event name from `[p]eventping` (can only be used in value argument.)
        """
        if not nfield:
            await self.config.guild(ctx.guild).event_embed.name_field.name.clear()
            await self.config.guild(ctx.guild).event_embed.name_field.value.clear()
            await self.config.guild(ctx.guild).event_embed.name_field.inline.clear()
            return await ctx.send("Successfully resetted the event name field.")
        
        nfield = nfield.split("|")
        maxargs = len(nfield)

        if maxargs > 3:
            return await ctx.send("Argument error, perhaps you added an extra `|`.")
        if maxargs < 3:
            return await ctx.send("Argument error, perhaps you are missing a `|`.")
        
        name_name = nfield[0]
        name_name.replace(" ", "")
        name_value = nfield[1]
        name_value.replace(" ", "")
        name_inline = nfield[2]
        name_inline.replace(" ", "")
        if "1" in name_inline:
            name_inline = True
        elif "0" in name_inline:
            name_inline = False
        else:
            return await ctx.send("Your answer for the `<inline>` argument should only be `1` for True or `0` for False.")
        
        await self.config.guild(ctx.guild).event_embed.name_field.name.set(name_name)
        await self.config.guild(ctx.guild).event_embed.name_field.value.set(name_value)
        await self.config.guild(ctx.guild).event_embed.name_field.inline.set(name_inline)
        await ctx.send(f"Successfully set the event name field to:\n```py\nName: {name_name}\nValue: {name_value}\nInline: {name_inline}```")
    
    @managerutilsset_embed_events_fields.command(name="prize", usage="<name> | <value> | <inline>")
    async def managerutilsset_embed_events_fields_prize(self, ctx: commands.Context, *, pfield = None):
        """
        Customize the event embed prize field.
        
        Pass without arguments to reset the name field.
        For the <inline> argument you must only answer with `1` for True or `0` for False and nothing else.
        Split arguments with `|`.
        
        Available variables:
        ` - ` {prize} - the event prize from `[p]eventping` (can only be used in value argument.)
        """
        if not pfield:
            await self.config.guild(ctx.guild).event_embed.prize_field.name.clear()
            await self.config.guild(ctx.guild).event_embed.prize_field.value.clear()
            await self.config.guild(ctx.guild).event_embed.prize_field.inline.clear()
            return await ctx.send("Successfully resetted the event prize field.")
        
        pfield = pfield.split("|")
        maxargs = len(pfield)

        if maxargs > 3:
            return await ctx.send("Argument error, perhaps you added an extra `|`.")
        if maxargs < 3:
            return await ctx.send("Argument error, perhaps you are missing a `|`.")
        
        prize_name = pfield[0]
        prize_name.replace(" ", "")
        prize_value = pfield[1]
        prize_value.replace(" ", "")
        prize_inline = pfield[2]
        prize_inline.replace(" ", "")
        if "1" in prize_inline:
            prize_inline = True
        elif "0" in prize_inline:
            prize_inline = False
        else:
            return await ctx.send("Your answer for the `<inline>` argument should only be `1` for True or `0` for False.")
        
        await self.config.guild(ctx.guild).event_embed.prize_field.name.set(prize_name)
        await self.config.guild(ctx.guild).event_embed.prize_field.value.set(prize_value)
        await self.config.guild(ctx.guild).event_embed.prize_field.inline.set(prize_inline)
        await ctx.send(f"Successfully set the event prize field to:\n```py\nName: {prize_name}\nValue: {prize_value}\nInline: {prize_inline}```")
    
    @managerutilsset_embed_events_fields.command(name="message", aliases=["msg"], usage="<name> | <value> | <inline>")
    async def managerutilsset_embed_events_fields_message(self, ctx: commands.Context, *, mfield = None):
        """
        Customize the event embed message field.
        
        Pass without arguments to reset the name field.
        For the <inline> argument you must only answer with `1` for True or `0` for False and nothing else.
        Split arguments with `|`.
        
        Available variables:
        ` - ` {message} - the event sponsor message from `[p]eventping` (can only be used in value argument.)
        """
        if not mfield:
            await self.config.guild(ctx.guild).event_embed.message_field.name.clear()
            await self.config.guild(ctx.guild).event_embed.message_field.value.clear()
            await self.config.guild(ctx.guild).event_embed.message_field.inline.clear()
            return await ctx.send("Successfully resetted the event prize field.")
        
        mfield = mfield.split("|")
        maxargs = len(mfield)

        if maxargs > 3:
            return await ctx.send("Argument error, perhaps you added an extra `|`.")
        if maxargs < 3:
            return await ctx.send("Argument error, perhaps you are missing a `|`.")
        
        message_name = mfield[0]
        message_name.replace(" ", "")
        message_value = mfield[1]
        message_value.replace(" ", "")
        message_inline = mfield[2]
        message_inline.replace(" ", "")
        if "1" in message_inline:
            message_inline = True
        elif "0" in message_inline:
            message_inline = False
        else:
            return await ctx.send("Your answer for the `<inline>` argument should only be `1` for True or `0` for False.")
        
        await self.config.guild(ctx.guild).event_embed.message_field.name.set(message_name)
        await self.config.guild(ctx.guild).event_embed.message_field.value.set(message_value)
        await self.config.guild(ctx.guild).event_embed.message_field.inline.set(message_inline)
        await ctx.send(f"Successfully set the event message field to:\n```py\nName: {message_name}\nValue: {message_value}\nInline: {message_inline}```")
    
    @managerutilsset_embed.group(name="hiests", aliases=["heist"])
    async def managerutilsset_embed_heists(self, ctx):
        """
        Customize the heist embed to your liking.
        """
    
    @managerutilsset_embed_heists.command(name="content")
    async def managerutilsset_embed_heists_content(self, ctx: commands.Context, *, content = None):
        """
        Customize the message content above the heists embed.
        
        Available variables:
        ` - ` {role} - the pingrole
        ` - ` {sponsor} - the sponsor
        ` - ` {name} - the event name
        ` - ` {prize} - the prize
        ` - ` {host} - the host
        ` - ` {message} - the sponsors message
        ` - ` {guild} - the guild name
        """
        if not content:
            await self.config.guild(ctx.guild).heist_embed.content.clear()
            return await ctx.send("Successfully resetted the heist embed message content.")
        
        await self.config.guild(ctx.guild).heist_embed.content.set(content)
        await ctx.send(f"Successfully set the heist embed message content to:\n{box(content, 'py')}")
    
    @managerutilsset_embed_heists.command(name="colour", aliases=["color"])
    async def managerutilsset_embed_heists_colour(self, ctx: commands.Context, colour: discord.Colour = None):
        """
        Customize the heist embed colour.
        
        Pass without colour to reset the color to the bots default embed color.
        """
        if not colour:
            await self.config.guild(ctx.guild).heist_embed.colour_value.clear()
            await self.config.guild(ctx.guild).heist_embed.str_colour.clear()
            return await ctx.send("Successfully resetted the heist embed colour.")
        
        await self.config.guild(ctx.guild).heist_embed.colour_value.set(colour.value)
        await self.config.guild(ctx.guild).heist_embed.str_colour.set(str(colour))
        await ctx.send(f"Successfully set the heist embed colour to:\n{box(colour, 'py')}")
    
    @managerutilsset_embed_heists.command(name="title")
    async def managerutilsset_embed_heists_title(self, ctx: commands.Context, *, title = None):
        """
        Customize the heist embed title.
        
        Pass without title to reset to the default title.
        
        Available variables:
        ` - ` {guild} - the guild name.
        
        This defaults to `Server Event Time!`.
        """
        if not title:
            await self.config.guild(ctx.guild).heist_embed.title.clear()
            return await ctx.send("Successfully resetted the heists embed title.")
        
        await self.config.guild(ctx.guild).heist_embed.title.set(title)
        await ctx.send(f"Successfully set the heist embed title to:\n{box(title, 'py')}")
    
    @managerutilsset_embed_heists.command(name="thumbnail")
    async def managerutilsset_embed_heists_thumbnail(self, ctx: commands.Context, link = None):
        """
        Customize the heist embed thumbnail.
        
        Pass without link to remove it.
        
        The thumbnail defaults to `{guild.icon_url}` but if you want to add a thumbnail use this command.
        
        Available variables:
        ` - ` {host.avatar_url} - the avatar of the host
        ` - ` {guild.icon_url} - the guilds image
        
        If you use these variables please make sure to not add anything else besides the variables. 
        """
        if not link:
            await self.config.guild(ctx.guild).heist_embed.thumbnail.set("removed")
            return await ctx.send("The heist embed thumbnail has been removed.")
        
        await self.config.guild(ctx.guild).heist_embed.thumbnail.set(link)
        await ctx.send(f"Successfully set the heist embed tumbnail to:\n{box(link, 'py')}")
    
    @managerutilsset_embed_heists.command(name="image")
    async def managerutilsset_embed_heists_image(self, ctx: commands.Context, link = None):
        """
        Add or remove an image to the heists embed.
        
        Pass without link to remove it.
        
        The image defaults to `None` but if you want to add an image use this command.
        """
        if not link:
            if not await self.config.guild(ctx.guild).heist_embed.image():
                return await ctx.send("It appears you do not have a heist embed image set.")
            await self.config.guild(ctx.guild).heist_embed.image.clear()
            return await ctx.send("The heist embed image has been removed.")
        
        await self.config.guild(ctx.guild).heist_embed.image.set(link)
        await ctx.send(f"Successfully set the heist embed image to:\n{box(link, 'py')}")
    
    @managerutilsset_embed_heists.command(name="description", aliases=["desc"])
    async def managerutilsset_embed_heists_description(self, ctx: commands.Context, *, description = None):
        """
        Customize the heist embed description.
        
        Pass without description to remove it.
        
        This defaults to `None`.
        
        Available variables:
        ` - ` {sponsor} - the sponsor
        ` - ` {name} - the event name
        ` - ` {prize} - the prize
        ` - ` {host} - the host
        ` - ` {message} - the sponsors message
        ` - ` {guild} - the guild name
        """
        if not description:
            if not await self.config.guild(ctx.guild).heist_embed.description():
                return await ctx.send("It appears you do not have a heist description set.")
            await self.config.guild(ctx.guild).heist_embed.description.clear()
            return await ctx.send("Successfully removed the heists embed description.")
        
        await self.config.guild(ctx.guild).heist_embed.description.set(description)
        await ctx.send(f"Successfully set the heists embed description to:\n{box(description, 'py')}")
    
    @managerutilsset_embed_heists.group(name="footer")
    async def managerutilsset_embed_heists_footer(self, ctx):
        """
        Customize the heists embed footer text or icon.
        """
    
    @managerutilsset_embed_heists_footer.command(name="text")
    async def managerutilsset_embed_heists_footer_text(self, ctx: commands.Context, *, text = None):
        """
        Customize the heists embed footer text.
        
        Pass without text to reset it to default.
        
        This defaults to `Hosted by: {host}`.
        
        Available variables:
        ` - ` {host} - the host name
        ` - ` {host.id} - the host ID
        ` - ` {guild} - the guild name
        """
        if not text:
            await self.config.guild(ctx.guild).heist_embed.footer_text.clear()
            return await ctx.send("Successfully resetted the heists embed footer text.")
        
        await self.config.guild(ctx.guild).heist_embed.footer_text.set(text)
        await ctx.send(f"Successfully set the heists embed footer text to:\n{box(text, 'py')}")
    
    @managerutilsset_embed_heists_footer.command(name="icon")
    async def managerutilsset_embed_heists_footer_icon(self, ctx: commands.Context, icon = None):
        """
        Customize or remove the heists embed footer icon.
        
        Pass without link to remove it.
        
        This defaults to `{host.avatar_url}`.
        
        Available variables:
        ` - ` {host.avatar_url} - the avatar of the host
        ` - ` {guild.icon_url} - the guild image
        
        If you use one of these variables don't add anything else besides the variable that you chose.
        """
        if not icon:
            await self.config.guild(ctx.guild).heist_embed.footer_icon.set("removed")
            return await ctx.send("The heist embed footer icon has been removed.")
        
        await self.config.guild(ctx.guild).heist_embed.footer_icon.set(icon)
        await ctx.send(f"Successfully set the heist embed footer icon to:\n{box(icon, 'py')}")
    
    @managerutilsset_embed_heists_footer.command(name="toggle")
    async def managerutilsset_embed_heists_footer_remove(self, ctx):
        """
        Toggle whether to remove or add back the heists embed footer text and icon.
        """
        current = await self.config.guild(ctx.guild).heist_embed.show_footer()
        await self.config.guild(ctx.guild).heist_embed.show_footer.set(not current)
        status = "removed" if current else "added back"
        await ctx.send(f"The heists embed footer text and icon has been {status}.")
    
    @managerutilsset_embed_heists.group(name="fields", aliases=["field"])
    async def managerutilsset_embed_heists_fields(self, ctx):
        """
        Customize the heist embed fields to your liking.
        """
    
    @managerutilsset_embed_heists_fields.command(name="sponsor", usage="<name> | <value> | <inline>")
    async def managerutilsset_embed_heists_fields_sponsor(self, ctx: commands.Context, *, hsfield = None):
        """
        Customize the heist embed sponsor field.
        
        Pass without arguments to reset the sponsor field.
        For the <inline> argument you must only answer with `1` for True or `0` for False and nothing else.
        Split arguments with `|`.
        
        Available variables:
        ` - ` {sponsor} - the sponsor from `[p]heistping` (can only be used in value argument.)
        """
        if not hsfield:
            await self.config.guild(ctx.guild).heist_embed.hsponsor_field.name.clear()
            await self.config.guild(ctx.guild).heist_embed.hsponsor_field.value.clear()
            await self.config.guild(ctx.guild).heist_embed.hsponsor_field.inline.clear()
            return await ctx.send("Successfully resetted the heist sponsor field.")
        
        hsfield = hsfield.split("|")
        maxargs = len(hsfield)

        if maxargs > 3:
            return await ctx.send("Argument error, perhaps you added an extra `|`.")
        if maxargs < 3:
            return await ctx.send("Argument error, perhaps you are missing a `|`.")
        
        sponsor_name = hsfield[0]
        sponsor_name.replace(" ", "")
        sponsor_value = hsfield[1]
        sponsor_value.replace(" ", "")
        sponsor_inline = hsfield[2]
        sponsor_inline.replace(" ", "")
        if "1" in sponsor_inline:
            sponsor_inline = True
        elif "0" in sponsor_inline:
            sponsor_inline = False
        else:
            return await ctx.send("Your answer for the `<inline>` argument should only be `1` for True or `0` for False.")
        
        await self.config.guild(ctx.guild).heist_embed.hsponsor_field.name.set(sponsor_name)
        await self.config.guild(ctx.guild).heist_embed.hsponsor_field.value.set(sponsor_value)
        await self.config.guild(ctx.guild).heist_embed.hsponsor_field.inline.set(sponsor_inline)
        await ctx.send(f"Successfully set the heist sponsor field to:\n```py\nName: {sponsor_name}\nValue: {sponsor_value}\nInline: {sponsor_inline}```")
    
    @managerutilsset_embed_heists_fields.command(name="amount", usage="<name> | <value> | <inline>")
    async def managerutilsset_embed_heists_fields_amount(self, ctx: commands.Context, *, asfield = None):
        """
        Customize the heist embed amount field.
        
        Pass without arguments to reset the amount field.
        For the <inline> argument you must only answer with `1` for True or `0` for False and nothing else.
        Split arguments with `|`.
        
        Available variables:
        ` - ` {amount} - the amount from `[p]heistping` (can only be used in value argument.)
        """
        if not asfield:
            await self.config.guild(ctx.guild).heist_embed.hsponsor_field.name.clear()
            await self.config.guild(ctx.guild).heist_embed.hsponsor_field.value.clear()
            await self.config.guild(ctx.guild).heist_embed.hsponsor_field.inline.clear()
            return await ctx.send("Successfully resetted the heist amount field.")
        
        asfield = asfield.split("|")
        maxargs = len(asfield)

        if maxargs > 3:
            return await ctx.send("Argument error, perhaps you added an extra `|`.")
        if maxargs < 3:
            return await ctx.send("Argument error, perhaps you are missing a `|`.")
        
        amount_name = asfield[0]
        amount_name.replace(" ", "")
        amount_value = asfield[1]
        amount_value.replace(" ", "")
        amount_inline = asfield[2]
        amount_inline.replace(" ", "")
        if "1" in amount_inline:
            amount_inline = True
        elif "0" in amount_inline:
            amount_inline = False
        else:
            return await ctx.send("Your answer for the `<inline>` argument should only be `1` for True or `0` for False.")
        
        await self.config.guild(ctx.guild).heist_embed.hamount_field.name.set(amount_name)
        await self.config.guild(ctx.guild).heist_embed.hamount_field.value.set(amount_value)
        await self.config.guild(ctx.guild).heist_embed.hamount_field.inline.set(amount_inline)
        await ctx.send(f"Successfully set the heist amount field to:\n```py\nName: {amount_name}\nValue: {amount_value}\nInline: {amount_inline}```")
    
    @managerutilsset_embed_heists_fields.command(name="requirements", aliases=["req"], usage="<name> | <value> | <inline>")
    async def managerutilsset_embed_heists_fields_requirements(self, ctx: commands.Context, *, rsfield = None):
        """
        Customize the heist embed requirements field.
        
        Pass without arguments to reset the requirements field.
        For the <inline> argument you must only answer with `1` for True or `0` for False and nothing else.
        Split arguments with `|`.
        
        Available variables:
        ` - ` {requirements} - the requirements from `[p]heistping` (can only be used in value argument.)
        """
        if not rsfield:
            await self.config.guild(ctx.guild).heist_embed.hrequirements_field.name.clear()
            await self.config.guild(ctx.guild).heist_embed.hrequirements_field.value.clear()
            await self.config.guild(ctx.guild).heist_embed.hrequirements_field.inline.clear()
            return await ctx.send("Successfully resetted the heist requirements field.")
        
        rsfield = rsfield.split("|")
        maxargs = len(rsfield)

        if maxargs > 3:
            return await ctx.send("Argument error, perhaps you added an extra `|`.")
        if maxargs < 3:
            return await ctx.send("Argument error, perhaps you are missing a `|`.")
        
        requirements_name = rsfield[0]
        requirements_name.replace(" ", "")
        requirements_value = rsfield[1]
        requirements_value.replace(" ", "")
        requirements_inline = rsfield[2]
        requirements_inline.replace(" ", "")
        if "1" in requirements_inline:
            requirements_inline = True
        elif "0" in requirements_inline:
            requirements_inline = False
        else:
            return await ctx.send("Your answer for the `<inline>` argument should only be `1` for True or `0` for False.")
        
        await self.config.guild(ctx.guild).heist_embed.hrequirements_field.name.set(requirements_name)
        await self.config.guild(ctx.guild).heist_embed.hrequirements_field.value.set(requirements_value)
        await self.config.guild(ctx.guild).heist_embed.hrequirements_field.inline.set(requirements_inline)
        await ctx.send(f"Successfully set the heist requirements field to:\n```py\nName: {requirements_name}\nValue: {requirements_value}\nInline: {requirements_inline}```")
    
    @managerutilsset_embed_heists_fields.command(name="message", aliases=["msg"], usage="<name> | <value> | <inline>")
    async def managerutilsset_embed_heists_fields_message(self, ctx: commands.Context, *, hmfield = None):
        """
        Customize the heist embed message field.
        
        Pass without arguments to reset the message field.
        For the <inline> argument you must only answer with `1` for True or `0` for False and nothing else.
        Split arguments with `|`.
        
        Available variables:
        ` - ` {message} - the heist sponsor message from `[p]heistping` (can only be used in value argument.)
        """
        if not hmfield:
            await self.config.guild(ctx.guild).heist_embed.hmessage_field.name.clear()
            await self.config.guild(ctx.guild).heist_embed.hmessage_field.value.clear()
            await self.config.guild(ctx.guild).heist_embed.hmessage_field.inline.clear()
            return await ctx.send("Successfully resetted the heist message field.")
        
        hmfield = hmfield.split("|")
        maxargs = len(hmfield)

        if maxargs > 3:
            return await ctx.send("Argument error, perhaps you added an extra `|`.")
        if maxargs < 3:
            return await ctx.send("Argument error, perhaps you are missing a `|`.")
        
        message_name = hmfield[0]
        message_name.replace(" ", "")
        message_value = hmfield[1]
        message_value.replace(" ", "")
        message_inline = hmfield[2]
        message_inline.replace(" ", "")
        if "1" in message_inline:
            message_inline = True
        elif "0" in message_inline:
            message_inline = False
        else:
            return await ctx.send("Your answer for the `<inline>` argument should only be `1` for True or `0` for False.")
        
        await self.config.guild(ctx.guild).heist_embed.hmessage_field.name.set(message_name)
        await self.config.guild(ctx.guild).heist_embed.hmessage_field.value.set(message_value)
        await self.config.guild(ctx.guild).heist_embed.hmessage_field.inline.set(message_inline)
        await ctx.send(f"Successfully set the heist message field to:\n```py\nName: {message_name}\nValue: {message_value}\nInline: {message_inline}```")
    
    @managerutilsset_embed_heists_fields.command(name="cltoggle")
    async def managerutilsset_embed_heists_fields_cltoggle(self, ctx):
        """
        Toggle whether to show the Checklist field or not.
        """
        current = await self.config.guild(ctx.guild).heist_embed.checklist_toggle()
        await self.config.guild(ctx.guild).heist_embed.checklist_toggle.set(not current)
        status = "will not" if current else "will"
        return await ctx.send(f"I {status} show the checklist field.")
    
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
        # sourcery skip: low-code-quality
        """
        See the current settings for this guild.
        """
        settings = await self.config.guild(ctx.guild).all()
        gaw = await self.config.guild(ctx.guild).giveaway_embed.all()
        event = await self.config.guild(ctx.guild).event_embed.all()
        snfield = await self.config.guild(ctx.guild).event_embed.sponsor_field.all()
        nnfield = await self.config.guild(ctx.guild).event_embed.name_field.all()
        pnfield = await self.config.guild(ctx.guild).event_embed.prize_field.all()
        mnfield = await self.config.guild(ctx.guild).event_embed.message_field.all()
        heist = await self.config.guild(ctx.guild).heist_embed.all()
        hsnfield = await self.config.guild(ctx.guild).heist_embed.hsponsor_field.all()
        hanfield = await self.config.guild(ctx.guild).heist_embed.hamount_field.all()
        hrnfield = await self.config.guild(ctx.guild).heist_embed.hrequirements_field.all()
        hmnfield = await self.config.guild(ctx.guild).heist_embed.hmessage_field.all()
        
        role_set = f"""
        > **Manager Roles:**
        ` - ` Giveaway Manager Roles: {humanize_list([f'<@&{role}>' for role in settings["giveaway_manager_ids"]]) if settings["giveaway_manager_ids"] else "`No giveaway managers set.`"}
        ` - ` Event Manager Roles: {humanize_list([f'<@&{role}>' for role in settings["event_manager_ids"]]) if settings["event_manager_ids"] else "`No event managers set.`"}
        ` - ` Heist Manager Roles: {humanize_list([f'<@&{role}>' for role in settings["heist_manager_ids"]]) if settings["heist_manager_ids"] else "`No heist managers set.`"}
        
        > **Ping Roles:**
        ` - ` Giveaway Ping Role: {f"<@&{settings['giveaway_ping_role_id']}>" if settings["giveaway_ping_role_id"] else "`No giveaway ping role set.`"}
        ` - ` Event Ping Role: {f"<@&{settings['event_ping_role_id']}>" if settings["event_ping_role_id"] else "`No event ping role set.`"}
        ` - ` Heist Ping Role: {f"<@&{settings['heist_ping_role_id']}>" if settings["heist_ping_role_id"] else "`No heist ping role set.`"}
        """
        
        channel_set = f"""
        > **Announcement Channels:**
        ` - ` Giveaway Announcement Channels: {humanize_list([f'<#{channel}>' for channel in settings["giveaway_announcement_channel_ids"]]) if settings["giveaway_announcement_channel_ids"] else "`No giveaway announcement channels set.`"}
        ` - ` Event Announcement Channels: {humanize_list([f'<#{channel}>' for channel in settings["event_announcement_channel_ids"]]) if settings["event_announcement_channel_ids"] else "`No event announcement channels set.`"}
        ` - ` Heist Announcement Channel: {humanize_list([f'<#{channel}>' for channel in settings["heist_announcement_channel_ids"]]) if settings["heist_announcement_channel_ids"] else "`No heist announcement channels set.`"}
        
        > **Log Channels:**
        ` - ` Giveaway Log Channel: {f"<#{settings['giveaway_log_channel_id']}>" if settings["giveaway_log_channel_id"] else "`No giveaway log channel set.`"}
        ` - ` Event Log Channel: {f"<#{settings['event_log_channel_id']}>" if settings["event_log_channel_id"] else "`No event log channel set.`"}
        ` - ` Heist Log Channel: {f"<#{settings['heist_log_channel_id']}>" if settings["heist_log_channel_id"] else "`No heist log channel set.`"}
        """
        
        gaw_embed = f"""
        **Title:**
        {box(gaw["title"] or gembed_title, 'py')}
        **Description:**
        {box(gaw["description"] or gembed_description, 'py')}
        **Thumbnail:**
        {box(gaw["thumbnail"] or gembed_thumbnail if gembed_thumbnail else "removed", 'py')}
        **Image:**
        {box(gaw["image"] or gembed_image if gembed_image else "None", 'py')}
        **Colour:**
        {box(gaw["str_colour"] or await ctx.embed_colour(), 'py')}
        **Footer Text:**
        {box(gaw["footer_text"] or gembed_footer_text, 'py')}
        **Footer Icon:**
        {box(gaw["footer_icon"] or gembed_footer_icon if gembed_footer_icon else "None", 'py')}
        **Show Footer:**
        {box(gaw["show_footer"], 'py')}
        """
        
        event_embed = f"""
        **Title:**
        {box(event["title"] or eembed_title, 'py')}
        **Description:**
        {box(event["description"] or eembed_description if eembed_description else "None", 'py')}
        **Thumbnail:**
        {box(event["thumbnail"] or eembed_thumbnail if eembed_thumbnail else "removed", 'py')}
        **Image:**
        {box(event["image"] or eembed_image if eembed_image else "None", 'py')}
        **Colour:**
        {box(event["str_colour"] or await ctx.embed_colour(), 'py')}
        **Footer Text:**
        {box(event["footer_text"] or eembed_footer_text, 'py')}
        **Footer Icon:**
        {box(event["footer_icon"] or eembed_footer_icon if eembed_footer_icon else "None", 'py')}
        **Show Footer:**
        {box(event["show_footer"], 'py')}
        **Sponsor Field:**
        ```py\nName: {snfield["name"] or eembed_sponsor_field_name}\nValue: {snfield["value"] or eembed_sponsor_field_value}\nInline: {snfield["inline"]}\n```
        **Name Field:**
        ```py\nName: {nnfield["name"] or eembed_name_field_name}\nValue: {nnfield["value"] or eembed_name_field_value}\nInline: {nnfield["inline"]}\n```
        **Prize Field:**
        ```py\nName: {pnfield["name"] or eembed_prize_field_name}\nValue: {pnfield["value"] or eembed_prize_field_value}\nInline: {pnfield["inline"]}\n```
        **Message Field:**
        ```py\nName: {mnfield["name"] or eembed_message_field_name}\nValue: {mnfield["value"] or eembed_message_field_value}\nInline: {mnfield["inline"]}\n```
        """
        
        heist_embed = f"""
        **Title:**
        {box(heist["title"] or hembed_title, 'py')}
        **Description:**
        {box(heist["description"] or hembed_description if hembed_description else "None", 'py')}
        **Thumbnail:**
        {box(heist["thumbnail"] or hembed_thumbnail if hembed_thumbnail else "removed", 'py')}
        **Image:**
        {box(heist["image"] or hembed_image if hembed_image else "None", 'py')}
        **Colour:**
        {box(heist["str_colour"] or await ctx.embed_colour(), 'py')}
        **Footer Text:**
        {box(heist["footer_text"] or hembed_footer_text, 'py')}
        **Footer Icon:**
        {box(heist["footer_icon"] or hembed_footer_icon if hembed_footer_icon else "None", 'py')}
        **Show Footer:**
        {box(heist["show_footer"], 'py')}
        **Show Checklist:**
        {box(heist["checklist_toggle"], 'py')}
        **Sponsor Field:**
        ```py\nName: {hsnfield["name"] or hembed_sponsor_field_name}\nValue: {hsnfield["value"] or hembed_sponsor_field_value}\nInline: {hsnfield["inline"]}\n```
        **Amount Field:**
        ```py\nName: {hanfield["name"] or hembed_amount_field_name}\nValue: {hanfield["value"] or hembed_amount_field_value}\nInline: {hanfield["inline"]}\n```
        **Requirements Field:**
        ```py\nName: {hrnfield["name"] or hembed_requirements_field_name}\nValue: {hrnfield["value"] or hembed_requirements_field_value}\nInline: {hrnfield["inline"]}\n```
        **Message Field:**
        ```py\nName: {hmnfield["name"] or hembed_message_field_name}\nValue: {hmnfield["value"] or hembed_message_field_value}\nInline: {hmnfield["inline"]}\n```
        """
        
        em1 = discord.Embed(
            title="Role settings",
            description=role_set,
            colour=await ctx.embed_colour(),
        )
        em1.set_author(name=f"ManagerUtils settings for [{ctx.guild}]", icon_url=ctx.guild.icon_url)
        em1.set_footer(text=f"Command executed by: {ctx.author} | Page (1/5)", icon_url=ctx.author.avatar_url)
        
        em2 = discord.Embed(
            title="Channel settings",
            description=channel_set,
            colour=await ctx.embed_colour(),
        )
        em2.set_author(name=f"ManagerUtils settings for [{ctx.guild}]", icon_url=ctx.guild.icon_url)
        em2.set_footer(text=f"Command executed by: {ctx.author} | Page (3/5)", icon_url=ctx.author.avatar_url)
        
        em3 = discord.Embed(
            title="Giveaway embed settings",
            description=gaw_embed,
            colour=await ctx.embed_colour(),
        )
        em3.set_author(name=f"ManagerUtils settings for [{ctx.guild}]", icon_url=ctx.guild.icon_url)
        em3.set_footer(text=f"Command executed by: {ctx.author} | Page (3/5)", icon_url=ctx.author.avatar_url)
        
        em4 = discord.Embed(
            title="Event embed settings",
            description=event_embed,
            colour=await ctx.embed_colour(),
        )
        em4.set_author(name=f"ManagerUtils settings for [{ctx.guild}]", icon_url=ctx.guild.icon_url)
        em4.set_footer(text=f"Command executed by: {ctx.author} | Page (4/5)", icon_url=ctx.author.avatar_url)
        
        em5 = discord.Embed(
            title="Heist embed settings",
            description=heist_embed,
            colour=await ctx.embed_colour(),
        )
        em5.set_author(name=f"ManagerUtils settings for [{ctx.guild}]", icon_url=ctx.guild.icon_url)
        em5.set_footer(text=f"Command executed by: {ctx.author} | Page (5/5)", icon_url=ctx.author.avatar_url)
        
        embeds = [em1, em2, em3, em4, em5]
        await menu(ctx, embeds, controls=DEFAULT_CONTROLS, timeout=60)
    
    @managerutilsset.command(name="resetcog")
    @commands.is_owner()
    async def managerutilsset_resetcog(self, ctx):
        """
        Reset the managerutils cogs configuration.

        Bot owners only.
        """
        await ctx.send("This will reset the managerutils cogs whole configuration, do you want to continue? (`yes`/`no`)")

        pred = MessagePredicate.yes_or_no(ctx)
        try:
            await ctx.bot.wait_for("message", check=pred, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to respond, cancelling.")

        if pred.result:
            await self.config.clear_all()
            return await ctx.send("Successfully cleared the managerutils cogs configuration.")
        else:
            await ctx.send("Alright not doing that then.")
    
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
        eping = f"Syntax: {ctx.prefix}eventping <sponsor> | <event_name> | <prize> | [message]\nAlias: {ctx.prefix}eping"
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

        sponsor = giveaways[0]
        sponsor.replace(" ", "")
        prize = giveaways[1]
        prize.replace(" ", "")
        message = giveaways[2]
        message.replace(" ", "")

        glogchan = ctx.guild.get_channel(settings["giveaway_log_channel_id"])
        role = (
            f"<@&{settings['giveaway_ping_role_id']}>"
            or f"No giveaway ping role set. Use `{ctx.prefix}muset pingrole giveaways` to set one."
        )
        set_footer_icon = await self.config.guild(ctx.guild).giveaway_embed.footer_icon()
        set_footer_text = await self.config.guild(ctx.guild).giveaway_embed.footer_text()
        set_title = await self.config.guild(ctx.guild).giveaway_embed.title()
        set_description = await self.config.guild(ctx.guild).giveaway_embed.description()
        set_image = await self.config.guild(ctx.guild).giveaway_embed.image()
        set_thumbnail = await self.config.guild(ctx.guild).giveaway_embed.thumbnail()
        set_colour = await self.config.guild(ctx.guild).giveaway_embed.colour_value()
        show_footer = await self.config.guild(ctx.guild).giveaway_embed.show_footer()
        set_content = await self.config.guild(ctx.guild).giveaway_embed.content()

        gembed = discord.Embed(
            title=f"{set_title or gembed_title}".replace("{sponsor}", f"{sponsor}").replace("{host}", f"{ctx.author.mention}").replace("{message}", f"{message}").replace("{prize}", f"{prize}"),
            description=f"{set_description or gembed_description}".replace("{sponsor}", f"{sponsor}").replace("{host}", f"{ctx.author.mention}").replace("{message}", f"{message}").replace("{prize}", f"{prize}"),
            colour=set_colour or await ctx.embed_colour(),
            timestamp=datetime.datetime.now(datetime.timezone.utc),
        )
        gembed.set_image(
            url=set_image or gembed_image
        )
        gembed.set_thumbnail(
            url=f"{set_thumbnail or gembed_thumbnail}".replace("{host.avatar_url}", f"{ctx.author.avatar_url}").replace("{guild.icon_url}", f"{ctx.guild.icon_url}").replace("removed", "")
        )

        if show_footer:
            gembed.set_footer(
                text=f"{set_footer_text or gembed_footer_text}".replace("{host}", f"{ctx.author}").replace("{host.id}", f"{ctx.author.id}").replace("{guild}", f"{ctx.guild.name}"),
                icon_url=f"{set_footer_icon or gembed_footer_icon}".replace("{host.avatar_url}", f"{ctx.author.avatar_url}").replace("{guild.icon_url}", f"{ctx.guild.icon_url}").replace("removed", "")
            )

        if await self.config.guild(ctx.guild).auto_delete_commands():
            with contextlib.suppress(Exception):
                await ctx.message.delete()

        try:
            am = discord.AllowedMentions(roles=True, users=True, everyone=False)
            glog = await ctx.send(
                embed=gembed,
                content=f"{set_content or gembed_content}".replace("{sponsor}", f"{sponsor}").replace("{host}", f"{ctx.author.mention}").replace("{message}", f"{message}").replace("{prize}", f"{prize}").replace("{role}", f"{role}"),
                allowed_mentions=am
            )
        except Exception:
            return await ctx.author.send("It appears that I not have permission to send a message from that channel.")
        
        if glogchan:
            try:
                embed = discord.Embed(
                    title="Giveaway Logging",
                    description=f"**Host:** {ctx.author.mention}\n**Channel:** {ctx.channel.mention}\n**Sponsor:** {sponsor}\n**Prize:** {prize}\n**Message:** {message}",
                    colour=ctx.author.colour,
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                )
                embed.set_footer(text=f"Host: {ctx.author} (ID: {ctx.author.id})", icon_url=ctx.author.avatar_url)
                embed.set_thumbnail(url=ctx.guild.icon_url)

                button = url_button.URLButton(
                    "Jump To Message",
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
    ):    # sourcery skip: low-code-quality
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

        sponsor = events[0]
        sponsor.replace(" ", "")
        name = events[1]
        name.replace(" ", "")
        prize = events[2]
        prize.replace(" ", "")
        message = events[3]
        message.replace(" ", "")

        elogchan = ctx.guild.get_channel(settings["event_log_channel_id"])
        role = (
            f"<@&{settings['event_ping_role_id']}>"
            or f"No event ping role set. Use `{ctx.prefix}muset pingrole events` to set one."
        )
        set_footer_icon = await self.config.guild(ctx.guild).event_embed.footer_icon()
        set_footer_text = await self.config.guild(ctx.guild).event_embed.footer_text()
        set_title = await self.config.guild(ctx.guild).event_embed.title()
        set_description = await self.config.guild(ctx.guild).event_embed.description()
        set_image = await self.config.guild(ctx.guild).event_embed.image()
        set_thumbnail = await self.config.guild(ctx.guild).event_embed.thumbnail()
        set_colour = await self.config.guild(ctx.guild).event_embed.colour_value()
        show_footer = await self.config.guild(ctx.guild).event_embed.show_footer()
        sponsor_field = await self.config.guild(ctx.guild).event_embed.sponsor_field.all()
        name_field = await self.config.guild(ctx.guild).event_embed.name_field.all()
        prize_field = await self.config.guild(ctx.guild).event_embed.prize_field.all()
        message_field = await self.config.guild(ctx.guild).event_embed.message_field.all()
        set_content = await self.config.guild(ctx.guild).event_embed.content()
        
        eembed = discord.Embed(
            title=f"{set_title or eembed_title}".replace("{guild}", f"{ctx.guild.name}"),
            description=f"{set_description or eembed_description}".replace("{sponsor}", f"{sponsor}").replace("{host}", f"{ctx.author.mention}").replace("{message}", f"{message}").replace("{prize}", f"{prize}").replace("{name}", f"{name}").replace("{guild}", f"{ctx.guild.name}"),
            colour=set_colour or await ctx.embed_colour(),
            timestamp=datetime.datetime.now(datetime.timezone.utc),
        )
        eembed.set_image(
            url=set_image or eembed_image
        )
        eembed.set_thumbnail(
            url=f"{set_thumbnail or eembed_thumbnail}".replace("{host.avatar_url}", f"{ctx.author.avatar_url}").replace("{guild.icon_url}", f"{ctx.guild.icon_url}").replace("removed", ""),
        )
        eembed.add_field(
            name=sponsor_field["name"] or eembed_sponsor_field_name,
            value=f"{sponsor_field['value'] or eembed_sponsor_field_value}".replace("{sponsor}", f"{sponsor}"),
            inline=sponsor_field["inline"]
        )
        eembed.add_field(
            name=name_field["name"] or eembed_name_field_name,
            value=f"{name_field['value'] or eembed_name_field_value}".replace("{name}", f"{name}"),
            inline=name_field["inline"]
        )
        eembed.add_field(
            name=prize_field["name"] or eembed_prize_field_name,
            value=f"{prize_field['value'] or eembed_prize_field_value}".replace("{prize}", f"{prize}"),
            inline=prize_field["inline"]
        )
        eembed.add_field(
            name=message_field["name"] or eembed_message_field_name,
            value=f"{message_field['value'] or eembed_message_field_value}".replace("{message}", f"{message}"),
            inline=message_field["inline"]
        )
        if show_footer:
            eembed.set_footer(
                text=f"{set_footer_text or eembed_footer_text}".replace("{host}", f"{ctx.author}").replace("{host.id}", f"{ctx.author.id}").replace("{guild}", f"{ctx.guild.name}"),
                icon_url=f"{set_footer_icon or eembed_footer_icon}".replace("{host.avatar_url}", f"{ctx.author.avatar_url}").replace("{guild.icon_url}", f"{ctx.guild.icon_url}").replace("removed", "")
            )

        if await self.config.guild(ctx.guild).auto_delete_commands():
            with contextlib.suppress(Exception):
                await ctx.message.delete()

        try:
            am = discord.AllowedMentions(roles=True, users=True, everyone=False)
            elog = await ctx.send(
                embed=eembed,
                content=f"{set_content or eembed_content}".replace("{sponsor}", f"{sponsor}").replace("{host}", f"{ctx.author.mention}").replace("{message}", f"{message}").replace("{prize}", f"{prize}").replace("{name}", f"{name}").replace("{guild}", f"{ctx.guild.name}").replace("{role}", f"{role}"),
                allowed_mentions=am
            )
        except Exception:
            return await ctx.author.send("It appears that I do not have permission to send a message from that channel.")
        
        if elogchan:
            try:
                embed = discord.Embed(
                    title="Event Logging",
                    description=f"**Host:** {ctx.author.mention}\n**Channel:** {ctx.channel.mention}\n**Sponsor:** {sponsor}\n**Event Name:** {name}\n**Prize:** {prize}\n**Message:** {message}",
                    colour=ctx.author.colour,
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                )
                embed.set_footer(text=f"Host: {ctx.author} (ID: {ctx.author.id})", icon_url=ctx.author.avatar_url)
                embed.set_thumbnail(url=ctx.guild.icon_url)

                button = url_button.URLButton(
                    "Jump To Message",
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
               
        sponsor = heists[0]
        sponsor.replace(" ", "")
        amount = heists[1]
        amount.replace(" ", "")
        requirements = heists[2]
        requirements.replace(" ", "")
        message = heists[3]
        message.replace(" ", "")
        
        hlogchan = ctx.guild.get_channel(settings["heist_log_channel_id"])
        role = (
            f"<@&{settings['heist_ping_role_id']}>"
            or f"No heist ping role set. Use `{ctx.prefix}muset pingrole heists` to set one."
        )
        set_footer_icon = await self.config.guild(ctx.guild).heist_embed.footer_icon()
        set_footer_text = await self.config.guild(ctx.guild).heist_embed.footer_text()
        set_title = await self.config.guild(ctx.guild).heist_embed.title()
        set_description = await self.config.guild(ctx.guild).heist_embed.description()
        set_image = await self.config.guild(ctx.guild).heist_embed.image()
        set_thumbnail = await self.config.guild(ctx.guild).heist_embed.thumbnail()
        set_colour = await self.config.guild(ctx.guild).heist_embed.colour_value()
        show_footer = await self.config.guild(ctx.guild).heist_embed.show_footer()
        hsponsor_field = await self.config.guild(ctx.guild).heist_embed.hsponsor_field.all()
        hamount_field = await self.config.guild(ctx.guild).heist_embed.hamount_field.all()
        hrequirements_field = await self.config.guild(ctx.guild).heist_embed.hrequirements_field.all()
        hmessage_field = await self.config.guild(ctx.guild).heist_embed.hmessage_field.all()
        set_content = await self.config.guild(ctx.guild).heist_embed.content()
        
        hembed = discord.Embed(
            title=f"{set_title or hembed_title}".replace("{guild}", f"{ctx.guild.name}"),
            description=f"{set_description or hembed_description}".replace("{sponsor}", f"{sponsor}").replace("{host}", f"{ctx.author.mention}").replace("{message}", f"{message}").replace("{requirements}", f"{requirements}").replace("{amount}", f"{amount}").replace("{guild}", f"{ctx.guild.name}"),
            colour=set_colour or await ctx.embed_colour(),
            timestamp=datetime.datetime.now(datetime.timezone.utc),
        )
        hembed.set_image(
            url=set_image or hembed_image
        )
        hembed.set_thumbnail(
            url=f"{set_thumbnail or hembed_thumbnail}".replace("{host.avatar_url}", f"{ctx.author.avatar_url}").replace("{guild.icon_url}", f"{ctx.guild.icon_url}").replace("removed", "")
        )
        hembed.add_field(
            name=hsponsor_field["name"] or hembed_sponsor_field_name,
            value=f"{hsponsor_field['value'] or hembed_sponsor_field_value}".replace("{sponsor}", f"{sponsor}"),
            inline=hsponsor_field["inline"]
        )
        hembed.add_field(
            name=hamount_field["name"] or hembed_amount_field_name,
            value=f"{hamount_field['value'] or hembed_amount_field_value}".replace("{amount}", f"{amount}"),
            inline=hamount_field["inline"]
        )
        
        if await self.config.guild(ctx.guild).heist_embed.checklist_toggle():
            hembed.add_field(
                name="Checklist:",
                value="` - ` Have a life saver on your inventory.\n` - ` Withdraw at least **1** coin.\n` - ` Press the big green `JOIN HEIST` button.\n` - ` Lastly don't get caught.",
                inline=False
            )
        
        hembed.add_field(
            name=hrequirements_field["name"] or hembed_requirements_field_name,
            value=f"{hrequirements_field['value'] or hembed_requirements_field_value}".replace("{requirements}", f"{requirements}"),
            inline=False
        )
        hembed.add_field(
            name=hmessage_field["name"] or hembed_message_field_name,
            value=f"{hmessage_field['value'] or hembed_message_field_value}".replace("{message}", f"{message}"),
            inline=False
        )
        
        if show_footer:
            hembed.set_footer(
                text=f"{set_footer_text or hembed_footer_text}".replace("{host}", f"{ctx.author}").replace("{host.id}", f"{ctx.author.id}").replace("{guild}", f"{ctx.guild.name}"),
                icon_url=f"{set_footer_icon or hembed_footer_icon}".replace("{host.avatar_url}", f"{ctx.author.avatar_url}").replace("{guild.icon_url}", f"{ctx.guild.icon_url}").replace("removed", "")
            )
        
        if await self.config.guild(ctx.guild).auto_delete_commands():
            with contextlib.suppress(Exception):
                await ctx.message.delete()
        
        try:
            am = discord.AllowedMentions(roles=True, users=True, everyone=False)
            hlog = await ctx.send(
                embed=hembed,
                content=f"{set_content or hembed_content}".replace("{sponsor}", f"{sponsor}").replace("{host}", f"{ctx.author.mention}").replace("{message}", f"{message}").replace("{requirements}", f"{requirements}").replace("{amount}", f"{amount}").replace("{guild}", f"{ctx.guild.name}").replace("{role}", f"{role}"),
                allowed_mentions=am
            )
        except Exception:
            return await ctx.author.send("It appears that I do not have permission to send a message from that channel.")
        
        if hlogchan:
            try:
                embed = discord.Embed(
                    title="Heist Logging",
                    description=f"**Host:** {ctx.author.mention}\n**Channel:** {ctx.channel.mention}\n**Sponsor:** {sponsor}\n**Amount:** {amount}\n**Requirements:** {requirements}\n**Message:** {message}",
                    colour=ctx.author.colour,
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                )
                embed.set_footer(text=f"Host: {ctx.author} (ID: {ctx.author.id})", icon_url=ctx.author.avatar_url)
                embed.set_thumbnail(url=ctx.guild.icon_url)
                
                button = url_button.URLButton(
                    "Jump To Message",
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
        