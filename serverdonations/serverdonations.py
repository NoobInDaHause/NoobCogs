import asyncio
import datetime
import discord
import logging

from redbot.core import commands, Config
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list, box
from redbot.core.utils.menus import menu

from typing import Literal, Optional

from .cog_data import SdonateDesc, SdonateDefaults, SDEmbedData
from .utils import is_have_avatar
from .views import Confirmation, GiveawayFields, EventFields, HeistFields

class Coordinate(dict):
    def __missing__(self, key):
        return key

class ServerDonations(commands.Cog):
    """
    Donate bot currencies or other things to servers.
    
    Base commands to donate to server giveaways, events, heists etc.
    """
    def __init__(self, bot: Red) -> None:
        self.bot = bot
        
        self.config = Config.get_conf(self, identifier=7364456583646323, force_registration=True)
        #default_guild_settings = {
        #    "gman_id": None,
        #    "eman_id": None,
        #    "hman_id": None,
        #    "gchannel_id": None,
        #    "echannel_id": None,
        #    "hchannel_id": None
        #}
        self.config.register_guild(**SdonateDefaults.default_guild)
        self.log = logging.getLogger("red.NoobCogs.ServerDonations")
    
    __version__ = "2.0.9"
    __author__ = ["Noobindahause#2808"]
    __docs__ = "https://github.com/NoobInDaHause/NoobCogs/blob/red-3.5/serverdonations/README.md"

    def format_help_for_context(self, context: commands.Context) -> str:
        """
        Thanks Sinbad and sravan!
        """
        plural = "s" if len(self.__author__) != 1 else ""
        return f"""{super().format_help_for_context(context)}
        
        Cog Version: **{self.__version__}**
        Cog Author{plural}: {humanize_list([f'**{auth}**' for auth in self.__author__])}
        Cog Documentation: [[Click here]]({self.__docs__})
        """

    async def red_delete_data_for_user(
        self, *, requester: Literal["discord_deleted_user", "owner", "user", "user_strict"], user_id: int
    ) -> None:
        # This cog does not store any end user data whatsoever.
        return await super().red_delete_data_for_user(requester=requester, user_id=user_id)

    def make_colour_embed(self, description: str, colour: discord.Colour) -> discord.Embed:
        return discord.Embed(
            description=description,
            timestamp=datetime.datetime.now(datetime.timezone.utc),
        ).set_image(
            url=f"https://singlecolorimage.com/get/{str(colour)[1:]}/400x100.png"
        )

    async def set_g_embed_footer(
        self,
        context: commands.Context,
        types: str,
        type2: str,
        url_or_text: Optional[str] = None
    ):
        if type2 == "icon":
            other = ["{guild_icon}", "{donor_avatar}"]
            acc = (".png", ".jpg", ".jpeg", ".gif")
            if not url_or_text:
                await self.config.guild(context.guild).embeds.giveaway.g_footer.g_ficon.set("")
                return await context.send(content=f"The {types} footer icon has been removed.")
            if url_or_text.lower() == "reset":
                await self.config.guild(context.guild).embeds.giveaway.g_footer.g_ficon.clear()
                return await context.send(content=f"The {types} footer icon has been reset.")
            if (not url_or_text.endswith(acc)) and (url_or_text not in other):
                return await context.send(content="Invalid variable or url.")
            await self.config.guild(context.guild).embeds.giveaway.g_footer.g_ficon.set(url_or_text)
            return await context.send(
                content=f"The {types} footer icon has been set to: {box(url_or_text, 'py')}"
            )
        if type2 == "text":
            if not url_or_text:
                await self.config.guild(context.guild).embeds.giveaway.g_footer.g_ftext.set("")
                return await context.send(content=f"The {types} footer text has been removed.")
            if url_or_text.lower() == "reset":
                await self.config.guild(context.guild).embeds.giveaway.g_footer.g_ftext.clear()
                return await context.send(content=f"The {types} footer text has been reset.")
            await self.config.guild(context.guild).embeds.giveaway.g_footer.g_ftext.set(url_or_text)
            return await context.send(
                content=f"The {types} footer text has been set to: {box(url_or_text, 'py')}"
            )

    async def set_e_embed_footer(
        self,
        context: commands.Context,
        types: str,
        type2: str,
        url_or_text: Optional[str] = None
    ):
        if type2 == "icon":
            other = ["{guild_icon}", "{donor_avatar}"]
            acc = (".png", ".jpg", ".jpeg", ".gif")
            if not url_or_text:
                await self.config.guild(context.guild).embeds.event.e_footer.e_ficon.set("")
                return await context.send(content=f"The {types} footer icon has been removed.")
            if url_or_text.lower() == "reset":
                await self.config.guild(context.guild).embeds.event.e_footer.e_ficon.clear()
                return await context.send(content=f"The {types} footer icon has been reset.")
            if (not url_or_text.endswith(acc)) and (url_or_text not in other):
                return await context.send(content="Invalid variable or url.")
            await self.config.guild(context.guild).embeds.event.e_footer.e_ficon.set(url_or_text)
            return await context.send(
                content=f"The {types} footer icon has been set to: {box(url_or_text, 'py')}"
            )
        if type2 == "text":
            if not url_or_text:
                await self.config.guild(context.guild).embeds.event.e_footer.e_ftext.set("")
                return await context.send(content=f"The {types} footer text has been removed.")
            if url_or_text.lower() == "reset":
                await self.config.guild(context.guild).embeds.event.e_footer.e_ftext.clear()
                return await context.send(content=f"The {types} footer text has been reset.")
            await self.config.guild(context.guild).embeds.event.e_footer.e_ftext.set(url_or_text)
            return await context.send(
                content=f"The {types} footer text has been set to: {box(url_or_text, 'py')}"
            )

    async def set_h_embed_footer(
        self,
        context: commands.Context,
        types: str,
        type2: str,
        url_or_text: Optional[str] = None
    ):
        if type2 == "icon":
            other = ["{guild_icon}", "{donor_avatar}"]
            acc = (".png", ".jpg", ".jpeg", ".gif")
            if not url_or_text:
                await self.config.guild(context.guild).embeds.heist.h_footer.h_ficon.set("")
                return await context.send(content=f"The {types} footer icon has been removed.")
            if url_or_text.lower() == "reset":
                await self.config.guild(context.guild).embeds.heist.h_footer.h_ficon.clear()
                return await context.send(content=f"The {types} footer icon has been reset.")
            if (not url_or_text.endswith(acc)) and (url_or_text not in other):
                return await context.send(content="Invalid variable or url.")
            await self.config.guild(context.guild).embeds.heist.h_footer.h_ficon.set(url_or_text)
            return await context.send(
                content=f"The {types} footer icon has been set to: {box(url_or_text, 'py')}"
            )
        if type2 == "text":
            if not url_or_text:
                await self.config.guild(context.guild).embeds.heist.h_footer.h_ftext.set("")
                return await context.send(content=f"The {types} footer text has been removed.")
            if url_or_text.lower() == "reset":
                await self.config.guild(context.guild).embeds.heist.h_footer.h_ftext.clear()
                return await context.send(content=f"The {types} footer text has been reset.")
            await self.config.guild(context.guild).embeds.heist.h_footer.h_ftext.set(url_or_text)
            return await context.send(
                content=f"The {types} footer text has been set to: {box(url_or_text, 'py')}"
            )

    # https://github.com/phenom4n4n/phen-cogs/blob/d60b66c0738937e71ee4865d62235e1b2c3cd819/forcemention/forcemention.py#L64
    # modified a lil bit to work with my code
    async def forcemention(
        self,
        channel: discord.TextChannel,
        role: discord.Role,
        embed: discord.Embed,
        *args,
        **kwargs
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
            await channel.send(
                embed=embed,
                allowed_mentions=mentionPerms,
                *args,
                **kwargs
            )
            await asyncio.sleep(1.5)
            await role.edit(mentionable=False)
        else:
            await channel.send(
                embed=embed,
                allowed_mentions=mentionPerms,
                *args,
                **kwargs
            )
    
    async def send_to_g_chan(self, context: commands.Context, embed: discord.Embed):
        """
        Sends to the set giveaway donation request channel.

        <type> | <duration> | <winners> | [requirements] | <prize> | [message]
        """
        settings = await self.config.guild(context.guild).all()

        view = discord.ui.View()
        button = discord.ui.Button(label="Jump To Command", url=context.message.jump_url)
        view.add_item(button)

        channel = context.guild.get_channel(settings["channels"]["gchan"])
        
        if not settings["roles"]["gman"]:
            try:
                await channel.send(
                    content=f'{settings["embeds"]["giveaway"]["g_content"]}'.format_map(
                        Coordinate(
                            role="`No giveaway manager role set.`",
                            donor=context.author,
                            guild=context.guild
                        )
                    ),
                    embed=embed,
                    view=view
                )
                return await context.tick()
            except (discord.errors.Forbidden, discord.errors.HTTPException) as e:
                return await context.send(
                    content="An error has occurred while sending the giveaway donation request.\n"
                    f"Here is the traceback: {box(e, 'py')}"
                )
        
        role = context.guild.get_role(settings["roles"]["gman"])
        try:
            await self.forcemention(
                channel=channel,
                role=role,
                embed=embed,
                content=f'{settings["embeds"]["giveaway"]["g_content"]}'.format_map(
                        Coordinate(
                            role=role.mention,
                            donor=context.author,
                            guild=context.guild
                        )
                    ),
                view=view
            )
            await context.tick()
        except (discord.errors.Forbidden, discord.errors.HTTPException) as e:
            await context.send(
                content="An error has occurred while sending the giveaway donation request.\n"
                    f"Here is the traceback: {box(e, 'py')}"
            )

    async def send_to_e_chan(self, context: commands.Context, embed: discord.Embed):
        """
        Sends to the set event donation request channel.

        <type> | <name> | [requirements] | <prize> | [message]
        """
        settings = await self.config.guild(context.guild).all()

        view = discord.ui.View()
        button = discord.ui.Button(label="Jump To Command", url=context.message.jump_url)
        view.add_item(button)

        channel = context.guild.get_channel(settings["channels"]["echan"])
        
        if not settings["roles"]["eman"]:
            try:
                await channel.send(
                    content=f'{settings["embeds"]["event"]["e_content"]}'.format_map(
                        Coordinate(
                            role="`No event manager role set.`",
                            donor=context.author,
                            guild=context.guild
                        )
                    ),
                    embed=embed,
                    view=view
                )
                return await context.tick()
            except (discord.errors.Forbidden, discord.errors.HTTPException) as e:
                return await context.send(
                    content="An error has occurred while sending the event donation request.\n"
                    f"Here is the traceback: {box(e, 'py')}"
                )
        
        role = context.guild.get_role(settings["roles"]["eman"])
        try:
            await self.forcemention(
                channel=channel,
                role=role,
                embed=embed,
                content=f'{settings["embeds"]["event"]["e_content"]}'.format_map(
                        Coordinate(
                            role=role.mention,
                            donor=context.author,
                            guild=context.guild
                        )
                    ),
                view=view
            )
            await context.tick()
        except (discord.errors.Forbidden, discord.errors.HTTPException) as e:
            await context.send(
                content="An error has occurred while sending the event donation request.\n"
                    f"Here is the traceback: {box(e, 'py')}"
            )

    async def send_to_h_chan(self, context: commands.Context, embed: discord.Embed):
        """
        Sends to the set event donation request channel.

        <type> | <amount> | [requirements] | [message]
        """
        settings = await self.config.guild(context.guild).all()

        view = discord.ui.View()
        button = discord.ui.Button(label="Jump To Command", url=context.message.jump_url)
        view.add_item(button)

        channel = context.guild.get_channel(settings["channels"]["hchan"])
        
        if not settings["roles"]["hman"]:
            try:
                await channel.send(
                    content=f'{settings["embeds"]["heist"]["h_content"]}'.format_map(
                        Coordinate(
                            role="`No heist manager role set.`",
                            donor=context.author,
                            guild=context.guild
                        )
                    ),
                    embed=embed,
                    view=view
                )
                return await context.tick()
            except (discord.errors.Forbidden, discord.errors.HTTPException) as e:
                return await context.send(
                    content="An error has occurred while sending the heist donation request.\n"
                    f"Here is the traceback: {box(e, 'py')}"
                )
        
        role = context.guild.get_role(settings["roles"]["hman"])
        try:
            await self.forcemention(
                channel=channel,
                role=role,
                embed=embed,
                content=f'{settings["embeds"]["heist"]["h_content"]}'.format_map(
                        Coordinate(
                            role=role.mention,
                            donor=context.author,
                            guild=context.guild
                        )
                    ),
                view=view
            )
            await context.tick()
        except (discord.errors.Forbidden, discord.errors.HTTPException) as e:
            await context.send(
                content="An error has occurred while sending the heist donation request.\n"
                    f"Here is the traceback: {box(e, 'py')}"
            )

    async def set_g_thumb(self, context: commands.Context, types: str, url_or_avatar: str = None):
        other = ["{guild_icon}", "{donor_avatar}"]
        acc = (".png", ".jpg", ".jpeg", ".gif")
        if not url_or_avatar:
            await self.config.guild(context.guild).embeds.giveaway.g_thumb.set("")
            return await context.send(content=f"The {types} embed thumbnail has been removed.")
        if url_or_avatar.lower() == "reset":
            await self.config.guild(context.guild).embeds.giveaway.g_thumb.clear()
            return await context.send(content=f"The {types} embed thumbnail has been reset.")
        if (not url_or_avatar.endswith(acc)) and (url_or_avatar not in other):
            return await context.send(content="Invalid variable or url.")
        await self.config.guild(context.guild).embeds.giveaway.g_thumb.set(url_or_avatar)
        return await context.send(
            content=f"The {types} embed thumbnail has been set to: {box(url_or_avatar, 'py')}"
        )

    async def set_e_thumb(self, context: commands.Context, types: str, url_or_avatar: str = None):
        other = ["{guild_icon}", "{donor_avatar}"]
        acc = (".png", ".jpg", ".jpeg", ".gif")
        if not url_or_avatar:
            await self.config.guild(context.guild).embeds.event.e_thumb.set("")
            return await context.send(content=f"The {types} embed thumbnail has been removed.")
        if url_or_avatar.lower() == "reset":
            await self.config.guild(context.guild).embeds.event.e_thumb.clear()
            return await context.send(content=f"The {types} embed thumbnail has been reset.")
        if (not url_or_avatar.endswith(acc)) and (url_or_avatar not in other):
            return await context.send(content="Invalid variable or url.")
        await self.config.guild(context.guild).embeds.event.e_thumb.set(url_or_avatar)
        return await context.send(
            content=f"The {types} embed thumbnail has been set to: {box(url_or_avatar, 'py')}"
        )

    async def set_h_thumb(self, context: commands.Context, types: str, url_or_avatar: str = None):
        other = ["{guild_icon}", "{donor_avatar}"]
        acc = (".png", ".jpg", ".jpeg", ".gif")
        if not url_or_avatar:
            await self.config.guild(context.guild).embeds.heist.h_thumb.set("")
            return await context.send(content=f"The {types} embed thumbnail has been removed.")
        if url_or_avatar.lower() == "reset":
            await self.config.guild(context.guild).embeds.heist.h_thumb.clear()
            return await context.send(content=f"The {types} embed thumbnail has been reset.")
        if (not url_or_avatar.endswith(acc)) and (url_or_avatar not in other):
            return await context.send(content="Invalid variables or url.")
        await self.config.guild(context.guild).embeds.heist.h_thumb.set(url_or_avatar)
        return await context.send(
            content=f"The {types} embed thumbnail has been set to: {box(url_or_avatar, 'py')}"
        )

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
        ).set_footer(
            text=f"Command executed by: {context.author} | Page 1/3",
            icon_url=is_have_avatar(context.author)
        )
        
        em2 = discord.Embed(
            title=f"How to use `{context.prefix}eventdonate` command",
            description=SdonateDesc.edonodesc.replace("[p]", f"{context.prefix}"),
            colour=await context.embed_colour()
        ).set_footer(
            text=f"Command executed by: {context.author} | Page 2/3",
            icon_url=is_have_avatar(context.author)
        )
        
        em3 = discord.Embed(
            title=f"How to use `{context.prefix}heistdonate` command",
            description=SdonateDesc.hdonodesc.replace("[p]", f"{context.prefix}"),
            colour=await context.embed_colour()
        ).set_footer(
            text=f"Command executed by: {context.author} | Page 3/3",
            icon_url=is_have_avatar(context.author)
        )
        
        bemeds = [em1, em2, em3]
        await menu(context, bemeds, timeout=60)

    @commands.group(name="serverdonationsset", aliases=["sdonateset", "sdonoset"])
    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    @commands.bot_has_permissions(embed_links=True)
    async def serverdonationsset(self, context: commands.Context):
        """
        Configure the ServerDonations configuration settings.
        """
        pass

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

    @serverdonationsset.command(name="role")
    @commands.bot_has_permissions(manage_roles=True)
    async def serverdonationsset_role(
        self,
        context: commands.Context,
        types: Literal["giveaway", "event", "heist"],
        role: Optional[discord.Role]
    ):
        """
        Set the giveaway, event or heist manager role.

        Leave `role` blank to remove the current set role for the given type.
        """
        if role and role >= context.guild.me.top_role:
            return await context.send(
                content="It appears that role is higher than me in hierarchy."
            )

        if types == "giveaway":
            if not role:
                await self.config.guild(context.guild).roles.gman.clear()
                return await context.send(content=f"The {types} manager role has been removed.")
            await self.config.guild(context.guild).roles.gman.set(role.id)
            await context.send(content=f"**{role.name}** has been set as the {types} manager role.")
        elif types == "event":
            if not role:
                await self.config.guild(context.guild).roles.ecman.clear()
                return await context.send(content=f"The {types} manager has been removed.")
            await self.config.guild(context.guild).roles.eman.set(role.id)
            await context.send(content=f"**{role.name}** has been set as the {types} manager role.")
        elif types == "heist":
            if not role:
                await self.config.guild(context.guild).roles.hcman.clear()
                return await context.send(content=f"The {types} manager has been removed.")
            await self.config.guild(context.guild).roles.hman.set(role.id)
            await context.send(content=f"**{role.name}** has been set as the {types} manager role.")

    @serverdonationsset.command(name="channel", aliases=["chan"])
    async def serverdonationsset_channel(
        self,
        context: commands.Context,
        types: Literal["giveaway", "event", "heist"],
        channel: Optional[discord.TextChannel]
    ):
        """
        Set the giveaway, event or heist donation request channel.

        Leave `channel` blank to remove the current set channel for the given type.
        """
        if channel and not channel.permissions_for(context.guild.me).send_messages:
            return await context.send(
                content="It appears that I do not have permission to send messages in that channel."
            )

        if types == "giveaway":
            if not channel:
                await self.config.guild(context.guild).channels.gchan.clear()
                return await context.send(content=f"The {types} channel has been removed.")
            await self.config.guild(context.guild).channels.gchan.set(channel.id)
            await context.send(
                content=f"{channel.mention} has been set as the {types} donation requests channel."
            )
        elif types == "event":
            if not channel:
                await self.config.guild(context.guild).channels.echan.clear()
                return await context.send(contnt=f"The {types} channel has been removed.")
            await self.config.guild(context.guild).channels.echan.set(channel.id)
            await context.send(
                content=f"{channel.mention} has been set as the {types} donation requests channel."
            )
        elif types == "heist":
            if not channel:
                await self.config.guild(context.guild).channels.hchan.clear()
                return await context.send(content=f"The {types} channel has been removed.")
            await self.config.guild(context.guild).channels.hchan.set(channel.id)
            await context.send(
                content=f"{channel.mention} has been set as the {types} donation requests channel."
            )

    @serverdonationsset.group(name="embed")
    async def serverdonationsset_embed(self, context: commands.Context):
        """
        Customize the giveaway, event or heist donation request embed.
        """
        pass
    
    @serverdonationsset_embed.command(name="content")
    async def serverdonationsset_embed_content(
        self,
        context: commands.Context,
        types: Literal["giveaway", "event", "heist"],
        *,
        content: Optional[str]
    ):
        """
        Customize the content for giveaway, event or heist donation embed.

        Leave `content` blank to reset it to default for the given type.

        Available variables:
        ` - ` {role} - The ping role.
        ` - ` {guild.name} - The guilds name.
        ` - ` {guild.id} - The guilds ID.
        ` - ` {donor} - The donors username.
        ` - ` {donor.id} - The donors ID.
        ` - ` {donor.mention} - Mentions the donor.
        """
        if types == "giveaway":
            if not content:
                await self.config.guild(context.guild).embeds.giveaway.g_content.clear()
                return await context.send(content=f"The {types} embed content has been reset.")
            await self.config.guild(context.guild).embeds.giveaway.g_content.set(content)
            await context.send(content=f"The {types} embed content has been set to: {box(content, 'py')}")
        elif types == "event":
            if not content:
                await self.config.guild(context.guild).embeds.event.e_content.clear()
                return await context.send(content=f"The {types} embed content has been reset.")
            await self.config.guild(context.guild).embeds.event.e_content.set(content)
            await context.send(content=f"The {types} embed content has been set to: {box(content, 'py')}")
        elif types == "heist":
            if not content:
                await self.config.guild(context.guild).embeds.heist.h_content.clear()
                return await context.send(content=f"The {types} embed content has been reset.")
            await self.config.guild(context.guild).embeds.heist.h_content.set(content)
            await context.send(content=f"The {types} embed content has been set to: {box(content, 'py')}")

    @serverdonationsset_embed.command(name="title")
    async def serverdonationsset_embed_title(
        self,
        context: commands.Context,
        types: Literal["giveaway", "event", "heist"],
        *,
        title: Optional[str]
    ):
        """
        Customize the title for giveaway, event or heist donation embed.
        
        Leave `title` blank to reset it to default for the given type

        Available variables:
        ` - ` {guild.name} - The guilds name.
        ` - ` {guild.id} - The guilds ID.
        ` - ` {donor} - The donors username.
        ` - ` {donor.id} - The donors ID.
        """
        if types == "giveaway":
            if not title:
                await self.config.guild(context.guild).embeds.giveaway.g_title.clear()
                return await context.send(content=f"The {types} embed title has been reset.")
            await self.config.guild(context.guild).embeds.giveaway.g_title.set(title)
            await context.send(content=f"The {types} embed title has been set to: {box(title, 'py')}")
        elif types == "event":
            if not title:
                await self.config.guild(context.guild).embeds.event.e_title.clear()
                return await context.send(content=f"The {types} embed title has been reset.")
            await self.config.guild(context.guild).embeds.event.e_title.set(title)
            await context.send(content=f"The {types} embed title has been set to: {box(title, 'py')}")
        elif types == "heist":
            if not title:
                await self.config.guild(context.guild).embeds.heist.h_title.clear()
                return await context.send(content=f"The {types} embed title has been reset.")
            await self.config.guild(context.guild).embeds.heist.h_title.set(title)
            await context.send(content=f"The {types} embed title has been set to: {box(title, 'py')}")

    @serverdonationsset_embed.command(name="description")
    async def serverdonationsset_embed_description(
        self,
        context: commands.Context,
        types: Literal["giveaway", "event", "heist"],
        *,
        description: Optional[str]
    ):
        """
        Customize the description for giveaway, event or heist donation embed.
        
        Leave `description` blank to reset it to default.

        Available variables:
        ` - ` {guild.name} - The guilds name.
        ` - ` {guild.id} - The guilds ID.
        ` - ` {donor} - The donors username.
        ` - ` {donor.id} - The donors ID.
        ` - ` {donor.mention} - Mentions the donor.
        """
        if types == "giveaway":
            if not description:
                await self.config.guild(context.guild).embeds.giveaway.g_desc.clear()
                return await context.send(content=f"The {types} embed description has been reset.")
            await self.config.guild(context.guild).embeds.giveaway.g_desc.set(description)
            await context.send(
                content=f"The {types} embed description has been set to: {box(description, 'py')}"
            )
        elif types == "event":
            if not description:
                await self.config.guild(context.guild).embeds.event.e_desc.clear()
                return await context.send(content=f"The {types} embed description has been reset.")
            await self.config.guild(context.guild).embeds.event.e_desc.set(description)
            await context.send(
                content=f"The {types} embed description has been set to: {box(description, 'py')}"
            )
        elif types == "heist":
            if not description:
                await self.config.guild(context.guild).embeds.heist.h_desc.clear()
                return await context.send(content=f"The {type} embed description has been reset.")
            await self.config.guild(context.guild).embeds.heist.h_desc.set(description)
            await context.send(
                content=f"The {types} embed description has been set to: {box(description, 'py')}"
            )

    @serverdonationsset_embed.command(name="colour", aliases=["color"])
    async def serverdonationsset_embed_colour(
        self,
        context: commands.Context,
        types: Literal["giveaway", "event", "heist"],
        colour: Optional[discord.Colour]
    ):
        """
        Customize the colour for giveaway, event or heist donation embed.
        
        Leave `colour` blank to reset it to default.

        All the colours defaults to bots embed colour.
        """
        botcolour = await context.embed_colour()

        if types == "event":
            if not colour:
                await self.config.guild(context.guild).embeds.event.e_colour.clear()
                embed = self.make_colour_embed(
                    description=f"The {types} donation embed colour has been reset.",
                    colour=botcolour
                )
                return await context.send(embed=embed)
            await self.config.guild(context.guild).embeds.event.e_colour.set(colour.value)
            embed = self.make_colour_embed(
                description=f"The {types} donation embed colour has been set to: {box(colour, 'py')}",
                colour=colour
            )
            await context.send(embed=embed)
        elif types == "giveaway":
            if not colour:
                await self.config.guild(context.guild).embeds.giveaway.g_colour.clear()
                embed = self.make_colour_embed(
                    description=f"The {types} donation embed colour has been reset.",
                    colour=botcolour
                )
                return await context.send(embed=embed)
            await self.config.guild(context.guild).embeds.giveaway.g_colour.set(colour.value)
            embed = self.make_colour_embed(
                description=f"The {types} donation embed colour has been set to: {box(colour, 'py')}",
                colour=colour
            )
            await context.send(embed=embed)
        elif types == "heist":
            if not colour:
                await self.config.guild(context.guild).embeds.heist.h_colour.clear()
                embed = self.make_colour_embed(
                    description=f"The {types} donation embed colour has been reset.",
                    colour=botcolour
                )
                return await context.send(embed=embed)
            await self.config.guild(context.guild).embeds.heist.h_colour.set(colour.value)
            embed = self.make_colour_embed(
                description=f"The {types} donation embed colour has been set to: {box(colour, 'py')}",
                colour=colour
            )
            await context.send(embed=embed)

    @serverdonationsset_embed.command(name="thumbnail")
    async def serverdonationsset_embed_thumbnail(
        self,
        context: commands.Context,
        types: Literal["giveaway", "event", "heist"],
        url_or_avatar: Optional[str]
    ):
        """
        Customize the thumbnail for giveaway, event or heist donation embed.

        Leave `url_or_avatar` blank to remove the thumbnail

        Put 'reset' in `url_or_avatar` to reset it to default.

        Available variables:
        ` - ` {guild_icon} - The guilds icon.
        ` - ` {donor_avatar} - The donors avatar.
        ` - ` Any valid url or link.

        Note:
        If you use any one of the variables please put it exactly the same as the above and only that.
        """
        if types == "giveaway":
            await self.set_g_thumb(context=context, types=types, url_or_avatar=url_or_avatar)
        elif types == "event":
            await self.set_e_thumb(context=context, types=types, url_or_avatar=url_or_avatar)
        elif types == "heist":
            await self.set_h_thumb(context=context, types=types, url_or_avatar=url_or_avatar)

    @serverdonationsset_embed.command(name="image")
    async def serverdonationsset_embed_image(
        self,
        context: commands.Context,
        types: Literal["giveaway", "event", "heist"],
        url: Optional[str]
    ):
        """
        Customize the image for the giveaway, event or heist donation embed.

        Leave `url` blank to remove the image.

        Put 'reset' in `url` to reset it to default.
        """
        acc = (".png", ".jpg", ".jpeg", ".gif")
        if types == "giveaway":
            if not url:
                await self.config.guild(context.guild).embeds.giveaway.g_image.set("")
                return await context.send(content=f"The {types} embed image has been removed.")
            if url.lower() == "reset":
                await self.config.guild(context.guild).embeds.giveaway.g_image.clear()
                return await context.send(content=f"The {types} embed image has been reset.")
            if not url.endswith(acc):
                return await context.send(content="Invalid url.")
            await self.config.guild(context.guild).embeds.giveaway.g_image.set(url)
            await context.send(content=f"The {types} embed image has been set to: {box(url, 'py')}")
        elif types == "event":
            if not url:
                await self.config.guild(context.guild).embeds.event.e_image.set("")
                return await context.send(content=f"The {types} embed image has been removed.")
            if url.lower() == "reset":
                await self.config.guild(context.guild).embeds.event.e_image.clear()
                return await context.send(content=f"The {types} embed image has been reset.")
            if not url.endswith(acc):
                return await context.send(content="Invalid url.")
            await self.config.guild(context.guild).embeds.event.e_image.set(url)
            await context.send(content=f"The {types} embed image has been set to: {box(url, 'py')}")
        elif types == "heist":
            if not url:
                await self.config.guild(context.guild).embeds.heist.h_image.set("")
                return await context.send(content=f"The {types} embed image has been removed.")
            if url.lower() == "reset":
                await self.config.guild(context.guild).embeds.heist.h_image.clear()
                return await context.send(content=f"The {types} embed image has been reset.")
            if not url.endswith(acc):
                return await context.send(content="Invalid url.")
            await self.config.guild(context.guild).embeds.heist.h_image.set(url)
            await context.send(content=f"The {types} embed image has been set to: {box(url, 'py')}")

    @serverdonationsset_embed.command(name="footer")
    async def serverdonationsset_embed_footer(
        self,
        context: commands.Context,
        types: Literal["giveaway", "event", "heist"],
        type2: Literal["icon", "text"],
        *,
        url_or_text: Optional[str] = None
    ):
        """
        Customize the footer for the giveaway, event or heist embed.

        Leave `url_or_text` blank to remove the icon or text.

        Put 'reset' in `url_or_text` to reset the icon if icon or text if text.

        Available variables for the icon:
        ` - ` {guild_icon} - The guilds icon.
        ` - ` {donor_avatar} - The donors avatar.
        ` - ` Any valid urls.

        Note:
        If you use any one of the variables please put it exactly the same as the above and only that.
        """
        if types == "event":
            await self.set_e_embed_footer(context=context, types=types, type2=type2, url_or_text=url_or_text)
        elif types == "giveaway":
            await self.set_g_embed_footer(context=context, types=types, type2=type2, url_or_text=url_or_text)
        elif types == "heist":
            await self.set_h_embed_footer(context=context, types=types, type2=type2, url_or_text=url_or_text)

    @serverdonationsset_embed.command(name="field", aliases=["fields"])
    async def serverdonationsset_embed_field(
        self,
        context: commands.Context,
        types: Literal["giveaway", "event", "heist"]
    ):
        """
        Customize the fields for the giveaway, event or heist donation embed.
        """
        if types == "event":
            view = EventFields()
            desc = """
            Only the embed field value has variables.

            No matter what you put inside the field value you must use the `{<name>}` variable.
            The `<name>` inside the variable should be the same name as what setting you are customizing.
            Example you picked `requirements` you should put the variable as {requirements}.
            This variable is required to show what the donor is actually inputting on that specific field.

            Sponsor variable has some unique extensions:
            {sponsor} - The sponsors username.
            {sponsor.id} - The sponsors ID.
            {sponsor.mention} - Mentions the sponsor.
            """
            embed = discord.Embed(
                title="ServerDonations Event Field Menu",
                description=desc,
                colour=await context.embed_colour()
            )
            return await view.start(context=context, embed=embed)
        if types == "giveaway":
            view = GiveawayFields()
            desc = """
            Only the embed field value has variables.

            No matter what you put inside the field value you must use the `{<name>}` variable.
            The `<name>` inside the variable should be the same name as what setting you are customizing.
            Example you picked `requirements` you should put the variable as {requirements}.
            This variable is required to show what the donor is actually inputting on that specific field.

            Sponsor variable has some unique extensions:
            {sponsor} - The sponsors username.
            {sponsor.id} - The sponsors ID.
            {sponsor.mention} - Mentions the sponsor.
            """
            embed = discord.Embed(
                title="ServerDonations Giveaway Field Menu",
                description=desc,
                colour=await context.embed_colour()
            )
            return await view.start(context=context, embed=embed)
        if types == "heist":
            view = HeistFields()
            desc = """
            Only the embed field value has variables.

            No matter what you put inside the field value you must use the `{<name>}` variable.
            The `<name>` inside the variable should be the same name as what setting you are customizing.
            Example you picked `requirements` you should put the variable as {requirements}.
            This variable is required to show what the donor is actually inputting on that specific field.

            Sponsor variable has some unique extensions:
            {sponsor} - The sponsors username.
            {sponsor.id} - The sponsors ID.
            {sponsor.mention} - Mentions the sponsor.
            """
            embed = discord.Embed(
                title="ServerDonations Heist Field Menu",
                description=desc,
                colour=await context.embed_colour()
            )
            return await view.start(context=context, embed=embed)

    @serverdonationsset.command(name="resetcog")
    @commands.is_owner()
    async def serverdonationsset_resetcog(self, context):
        """
        Reset the ServerDonations cogs configuration.

        Bot owners only.
        """
        conf_msg = "This will reset the serverdonations cogs whole configuration, do you want to continue?"
        conf_act = "Successfully cleared the serverdonations cogs configuration."
        view = Confirmation(30)
        await view.start(context, conf_msg, conf_act)
        
        await view.wait()
        
        if view.value == "yes":
            await self.config.clear_all()

    @serverdonationsset.command(name="showsettings", aliases=["ss"])
    async def serverdonationsset_showsetting(self, context: commands.Context):
        """
        See the guild settings set for ServerDonations.
        """
        settings = await self.config.guild(context.guild).all()
        channel = settings["channels"]
        role = settings["roles"]
        gaw = settings["embeds"]["giveaway"]
        event = settings["embeds"]["event"]
        heist = settings["embeds"]["heist"]
        defcolor = await context.embed_colour()

        chanembed = (
            discord.Embed(
                title="ServerDonations channel settings",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                colour=await context.embed_colour()
            )
            .add_field(
                name="Giveaway donation channel:",
                value=f'<#{channel["gchan"]}> ({channel["gchan"]})'
                if channel["gchan"]
                else "No giveaway donation request channel set.",
                inline=False
            )
            .add_field(
                name="Event donation channel:",
                value=f'<#{channel["echan"]}> ({channel["echan"]})'
                if channel["echan"]
                else "No event donation request channel set.",
                inline=False
            )
            .add_field(
                name="Heist donation channel:",
                value=f'<#{channel["hchan"]}> ({channel["hchan"]})'
                if channel["hchan"]
                else "No heist donation request channel set.",
                inline=False
            )
            .set_footer(text="Page (1/5)", icon_url=is_have_avatar(context.author))
        )
        roleembed = (
            discord.Embed(
                title="ServerDonations role settings",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                colour=await context.embed_colour()
            )
            .add_field(
                name="Giveaway manager role:",
                value=f'<@&{role["gman"]}> ({role["gman"]})'
                if role["gman"]
                else "No giveaway manager role set.",
                inline=False
            )
            .add_field(
                name="Event manager role:",
                value=f'<@&{role["eman"]}> ({role["eman"]})'
                if role["eman"]
                else "No event manager role set.",
                inline=False
            )
            .add_field(
                name="Heist manager role:",
                value=f'<@&{role["hman"]}> ({role["hman"]})'
                if role["hman"]
                else "No heist manager role set.",
                inline=False
            )
            .set_footer(text="Page (2/5)", icon_url=is_have_avatar(context.author))
        )
        gcol = discord.Colour(gaw["g_colour"]) if gaw["g_colour"] else defcolor
        gawembed = (
            discord.Embed(
                title="ServerDonations giveaway donation embed settings",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                colour=await context.embed_colour(),
                description=SDEmbedData.gaw.format_map(
                    Coordinate(
                        s1=gaw["g_content"], s2=gaw["g_title"], s3=gaw["g_desc"], s4=gcol,
                        s5=gaw["g_thumb"], s6=gaw["g_image"], s7=gaw["g_footer"]["g_ftext"],
                        s8=gaw["g_footer"]["g_ficon"], s9=gaw["g_fields"]["g_type"]["g_tname"],
                        s10=gaw["g_fields"]["g_type"]["g_tvalue"], s11=gaw["g_fields"]["g_type"]["g_tinline"],
                        s12=gaw["g_fields"]["g_spon"]["g_sname"], s13=gaw["g_fields"]["g_spon"]["g_svalue"],
                        s14=gaw["g_fields"]["g_spon"]["g_sinline"], s15=gaw["g_fields"]["g_dura"]["g_dname"],
                        s16=gaw["g_fields"]["g_dura"]["g_dvalue"], s17=gaw["g_fields"]["g_dura"]["g_dinline"],
                        s18=gaw["g_fields"]["g_winn"]["g_wname"], s19=gaw["g_fields"]["g_winn"]["g_wvalue"],
                        s20=gaw["g_fields"]["g_winn"]["g_winline"], s21=gaw["g_fields"]["g_requ"]["g_rname"],
                        s22=gaw["g_fields"]["g_requ"]["g_rvalue"], s23=gaw["g_fields"]["g_requ"]["g_rinline"],
                        s24=gaw["g_fields"]["g_priz"]["g_pname"], s25=gaw["g_fields"]["g_priz"]["g_pvalue"],
                        s26=gaw["g_fields"]["g_priz"]["g_pinline"], s27=gaw["g_fields"]["g_mess"]["g_mname"],
                        s28=gaw["g_fields"]["g_mess"]["g_mvalue"], s29=gaw["g_fields"]["g_mess"]["g_minline"]
                    )
                )
            )
            .set_footer(text="Page (3/5)", icon_url=is_have_avatar(context.author))
        )
        ecol = discord.Colour(event["e_colour"]) if event["e_colour"] else defcolor
        eventembed = (
            discord.Embed(
                title="ServerDonations event donation embed settings",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                colour=await context.embed_colour(),
                description=SDEmbedData.event.format_map(
                    Coordinate(
                        s1=event["e_content"], s2=event["e_title"], s3=event["e_desc"], s4=ecol,
                        s5=event["e_thumb"], s6=event["e_image"], s7=event["e_footer"]["e_ftext"],
                        s8=event["e_footer"]["e_ficon"], s9=event["e_fields"]["e_spon"]["e_sname"],
                        s10=event["e_fields"]["e_spon"]["e_svalue"],
                        s11=event["e_fields"]["e_spon"]["e_sinline"],
                        s12=event["e_fields"]["e_name"]["e_nname"],
                        s13=event["e_fields"]["e_name"]["e_nvalue"],
                        s14=event["e_fields"]["e_name"]["e_ninline"],
                        s15=event["e_fields"]["e_requ"]["e_rname"],
                        s16=event["e_fields"]["e_requ"]["e_rvalue"],
                        s17=event["e_fields"]["e_requ"]["e_rinline"],
                        s18=event["e_fields"]["e_priz"]["e_pname"],
                        s19=event["e_fields"]["e_priz"]["e_pvalue"],
                        s20=event["e_fields"]["e_priz"]["e_pinline"],
                        s21=event["e_fields"]["e_mess"]["e_mname"],
                        s22=event["e_fields"]["e_mess"]["e_mvalue"],
                        s23=event["e_fields"]["e_mess"]["e_minline"],
                        s24=event["e_fields"]["e_type"]["e_tname"],
                        s25=event["e_fields"]["e_type"]["e_tvalue"],
                        s26=event["e_fields"]["e_type"]["e_tinline"]
                    )
                )
            )
            .set_footer(text="Page (4/5)", icon_url=is_have_avatar(context.author))
        )
        hcol = discord.Colour(heist["h_colour"]) if heist["h_colour"] else defcolor
        heistembed = (
            discord.Embed(
                title="ServerDonations heist donation embed settings",
                timestamp=datetime.datetime.now(datetime.timezone.utc),
                colour=await context.embed_colour(),
                description=SDEmbedData.heist.format_map(
                    Coordinate(
                        s1=heist["h_content"], s2=heist["h_title"], s3=heist["h_desc"], s4=hcol,
                        s5=heist["h_thumb"], s6=heist["h_image"], s7=heist["h_footer"]["h_ftext"],
                        s8=heist["h_footer"]["h_ficon"], s9=heist["h_fields"]["h_type"]["h_tname"],
                        s10=heist["h_fields"]["h_type"]["h_tvalue"],
                        s11=heist["h_fields"]["h_type"]["h_tinline"],
                        s12=heist["h_fields"]["h_spon"]["h_sname"],
                        s13=heist["h_fields"]["h_spon"]["h_svalue"],
                        s14=heist["h_fields"]["h_spon"]["h_sinline"],
                        s15=heist["h_fields"]["h_amou"]["h_aname"],
                        s16=heist["h_fields"]["h_amou"]["h_avalue"],
                        s17=heist["h_fields"]["h_amou"]["h_ainline"],
                        s18=heist["h_fields"]["h_requ"]["h_rname"],
                        s19=heist["h_fields"]["h_requ"]["h_rvalue"],
                        s20=heist["h_fields"]["h_requ"]["h_rinline"],
                        s21=heist["h_fields"]["h_mess"]["h_mname"],
                        s22=heist["h_fields"]["h_mess"]["h_mvalue"],
                        s23=heist["h_fields"]["h_mess"]["h_minline"]
                    )
                )
            )
            .set_footer(text="Page (5/5)", icon_url=is_have_avatar(context.author))
        )
        list_embeds = [chanembed, roleembed, gawembed, eventembed, heistembed]
        await menu(context, list_embeds, timeout=60)

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
        settings = await self.config.guild(context.guild).all()

        if not settings["channels"]["gchan"]:
            return await context.send("No giveaway donation request channel set.")

        gdonos = gmsg.split("|")

        if len(gdonos) < 6:
            return await context.send(
                "All arguments are required but if you dont want anything on one "
                "of the arguments just put `none`."
            )

        if len(gdonos) > 6:
            return await context.send(
                content="It appears you added an extra `|` redo the command again."
            )

        gawset = settings["embeds"]["giveaway"]
        gfields = settings["embeds"]["giveaway"]["g_fields"]

        embed = (
            discord.Embed(
                colour=discord.Colour(gawset["g_colour"])
                if gawset["g_colour"]
                else await context.embed_colour(),
                title=f'{gawset["g_title"]}'.format_map(
                    Coordinate(donor=context.author, guild=context.guild)
                ),
                description=f'{gawset["g_desc"]}'.format_map(
                    Coordinate(
                        donor=context.author, guild=context.guild
                    )
                )
                if gawset["g_desc"]
                else "",
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            .set_image(
                url=f'{gawset["g_image"]}'
                if gawset["g_image"]
                else ""
            )
            .set_thumbnail(
                url=f'{gawset["g_thumb"]}'.format_map(
                    Coordinate(
                        donor_avatar=is_have_avatar(context.author),
                        guild_icon=is_have_avatar(context.guild)
                    )
                )
            )
            .set_footer(
                text=f'{gawset["g_footer"]["g_ftext"]}'.format_map(
                    Coordinate(donor=context.author, guild=context.guild)
                ),
                icon_url=f'{gawset["g_footer"]["g_ficon"]}'.format_map(
                    Coordinate(
                        donor_avatar=is_have_avatar(context.author),
                        guild_icon=is_have_avatar(context.guild)
                    )
                )
            )
            .add_field(
                name=gfields["g_spon"]["g_sname"],
                value=f'{gfields["g_spon"]["g_svalue"]}'.format_map(
                    Coordinate(sponsor=context.author)
                ),
                inline=gfields["g_spon"]["g_sinline"]
            )
            .add_field(
                name=gfields["g_type"]["g_tname"],
                value=f'{gfields["g_type"]["g_tvalue"]}'.format_map(
                    Coordinate(type=gdonos[0].strip())
                ),
                inline=gfields["g_type"]["g_tinline"]
            )
            .add_field(
                name=gfields["g_dura"]["g_dname"],
                value=f'{gfields["g_dura"]["g_dvalue"]}'.format_map(
                    Coordinate(duration=gdonos[1].strip())
                ),
                inline=gfields["g_dura"]["g_dinline"]
            )
            .add_field(
                name=gfields["g_winn"]["g_wname"],
                value=f'{gfields["g_winn"]["g_wvalue"]}'.format_map(
                    Coordinate(winners=gdonos[2].strip())
                ),
                inline=gfields["g_winn"]["g_winline"]
            )
            .add_field(
                name=gfields["g_requ"]["g_rname"],
                value=f'{gfields["g_requ"]["g_rvalue"]}'.format_map(
                    Coordinate(requirements=gdonos[3].strip())
                ),
                inline=gfields["g_requ"]["g_rinline"]
            )
            .add_field(
                name=gfields["g_priz"]["g_pname"],
                value=f'{gfields["g_priz"]["g_pvalue"]}'.format_map(
                    Coordinate(prize=gdonos[4].strip())
                ),
                inline=gfields["g_priz"]["g_pinline"]
            )
            .add_field(
                name=gfields["g_mess"]["g_mname"],
                value=f'{gfields["g_mess"]["g_mvalue"]}'.format_map(
                    Coordinate(message=gdonos[5].strip())
                ),
                inline=gfields["g_mess"]["g_minline"]
            )
        )
        await self.send_to_g_chan(context=context, embed=embed)

    @commands.command(
        name="eventdonate",
        aliases=["edonate", "edono"],
        usage="<type> | <name> | [requirements] | <prize> | [message]"
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
        settings = await self.config.guild(context.guild).all()

        if not settings["channels"]["echan"]:
            return await context.send("No event donation request channel set.")
            
        edonos = emsg.split("|")

        if len(edonos) < 5:
            return await context.send(
                "All arguments are required but if you dont want anything on one "
                "of the arguments just put `none`."
            )

        if len(edonos) > 5:
            return await context.send(
                content="It appears you added an extra `|` redo the command again."
            )

        eventset = settings["embeds"]["event"]
        efields = settings["embeds"]["event"]["e_fields"]

        embed = (
            discord.Embed(
                colour=discord.Colour(eventset["e_colour"])
                if eventset["e_colour"]
                else await context.embed_colour(),
                title=f'{eventset["e_title"]}'.format_map(
                    Coordinate(donor=context.author, guild=context.guild)
                ),
                description=f'{eventset["e_desc"]}'.format_map(
                    Coordinate(
                        donor=context.author, guild=context.guild
                    )
                )
                if eventset["e_desc"]
                else "",
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            .set_image(
                url=f'{eventset["e_image"]}'
                if eventset["e_image"]
                else ""
            )
            .set_thumbnail(
                url=f'{eventset["e_thumb"]}'.format_map(
                    Coordinate(
                        donor_avatar=is_have_avatar(context.author),
                        guild_icon=is_have_avatar(context.guild)
                    )
                )
            )
            .set_footer(
                text=f'{eventset["e_footer"]["e_ftext"]}'.format_map(
                    Coordinate(donor=context.author, guild=context.guild)
                ),
                icon_url=f'{eventset["e_footer"]["e_ficon"]}'.format_map(
                    Coordinate(
                        donor_avatar=is_have_avatar(context.author),
                        guild_icon=is_have_avatar(context.guild)
                    )
                )
            )
            .add_field(
                name=efields["e_spon"]["e_sname"],
                value=f'{efields["e_spon"]["e_svalue"]}'.format_map(
                    Coordinate(sponsor=context.author)
                ),
                inline=efields["e_spon"]["e_sinline"]
            )
            .add_field(
                name=efields["e_type"]["e_tname"],
                value=f'{efields["e_type"]["e_tvalue"]}'.format_map(
                    Coordinate(type=edonos[0].strip())
                ),
                inline=efields["e_type"]["e_tinline"]
            )
            .add_field(
                name=efields["e_name"]["e_nname"],
                value=f'{efields["e_name"]["e_nvalue"]}'.format_map(
                    Coordinate(name=edonos[1].strip())
                ),
                inline=efields["e_name"]["e_ninline"]
            )
            .add_field(
                name=efields["e_requ"]["e_rname"],
                value=f'{efields["e_requ"]["e_rvalue"]}'.format_map(
                    Coordinate(requirements=edonos[2].strip())
                ),
                inline=efields["e_requ"]["e_rinline"]
            )
            .add_field(
                name=efields["e_priz"]["e_pname"],
                value=f'{efields["e_priz"]["e_pvalue"]}'.format_map(
                    Coordinate(prize=edonos[3].strip())
                ),
                inline=efields["e_priz"]["e_pinline"]
            )
            .add_field(
                name=efields["e_mess"]["e_mname"],
                value=f'{efields["e_mess"]["e_mvalue"]}'.format_map(
                    Coordinate(message=edonos[4].strip())
                ),
                inline=efields["e_mess"]["e_minline"]
            )
        )
        await self.send_to_e_chan(context=context, embed=embed)

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
        settings = await self.config.guild(context.guild).all()

        if not settings["channels"]["hchan"]:
            return await context.send("No heist donation request channel set.")
            
        hdonos = hmsg.split("|")

        if len(hdonos) < 4:
            return await context.send(
                "All arguments are required but if you dont want anything on one "
                "of the arguments just put `none`."
            )

        if len(hdonos) > 4:
            return await context.send(
                content="It appears you added an extra `|` redo the command again."
            )

        heistset = settings["embeds"]["heist"]
        hfields = settings["embeds"]["heist"]["h_fields"]

        embed = (
            discord.Embed(
                colour=discord.Colour(heistset["h_colour"])
                if heistset["h_colour"]
                else await context.embed_colour(),
                title=f'{heistset["h_title"]}'.format_map(
                    Coordinate(donor=context.author, guild=context.guild)
                ),
                description=f'{heistset["h_desc"]}'.format_map(
                    Coordinate(
                        donor=context.author, guild=context.guild
                    )
                )
                if heistset["h_desc"]
                else "",
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            .set_image(
                url=f'{heistset["h_image"]}'
                if heistset["h_image"]
                else ""
            )
            .set_thumbnail(
                url=f'{heistset["h_thumb"]}'.format_map(
                    Coordinate(
                        donor_avatar=is_have_avatar(context.author),
                        guild_icon=is_have_avatar(context.guild)
                    )
                )
            )
            .set_footer(
                text=f'{heistset["h_footer"]["h_ftext"]}'.format_map(
                    Coordinate(donor=context.author, guild=context.guild)
                ),
                icon_url=f'{heistset["h_footer"]["h_ficon"]}'.format_map(
                    Coordinate(
                        donor_avatar=is_have_avatar(context.author),
                        guild_icon=is_have_avatar(context.guild)
                    )
                )
            )
            .add_field(
                name=hfields["h_spon"]["h_sname"],
                value=f'{hfields["h_spon"]["h_svalue"]}'.format_map(
                    Coordinate(sponsor=context.author)
                ),
                inline=hfields["h_spon"]["h_sinline"]
            )
            .add_field(
                name=hfields["h_type"]["h_tname"],
                value=f'{hfields["h_type"]["h_tvalue"]}'.format_map(
                    Coordinate(type=hdonos[0].strip())
                ),
                inline=hfields["h_type"]["h_tinline"]
            )
            .add_field(
                name=hfields["h_amou"]["h_aname"],
                value=f'{hfields["h_amou"]["h_avalue"]}'.format_map(
                    Coordinate(amount=hdonos[1].strip())
                ),
                inline=hfields["h_amou"]["h_ainline"]
            )
            .add_field(
                name=hfields["h_requ"]["h_rname"],
                value=f'{hfields["h_requ"]["h_rvalue"]}'.format_map(
                    Coordinate(requirements=hdonos[2].strip())
                ),
                inline=hfields["h_requ"]["h_rinline"]
            )
            .add_field(
                name=hfields["h_mess"]["h_mname"],
                value=f'{hfields["h_mess"]["h_mvalue"]}'.format_map(
                    Coordinate(message=hdonos[3].strip())
                ),
                inline=hfields["h_mess"]["h_minline"]
            )
        )
        await self.send_to_h_chan(context=context, embed=embed)
