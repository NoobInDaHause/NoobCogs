import discord
import logging

from redbot.core import commands, Config
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list, box
try:
    from slashtags import menu
    from redbot.core.utils.menus import DEFAULT_CONTROLS
except ModuleNotFoundError:
    from redbot.core.utils.menus import menu, DEFAULT_CONTROLS
from redbot.core.utils.predicates import MessagePredicate


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
        self.log = logging.getLogger("red.WintersCogs.ServerDonations")
        
    __version__ = "1.2.14"
    __author__ = ["Noobindahause#2808"]
    
    def format_help_for_context(self, ctx: commands.Context) -> str:
        """
        Thanks Sinbad and sravan!
        """
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\n\nCog Version: {self.__version__}\nCog Author: {humanize_list([f'{author}' for author in self.__author__])}"
    
    async def red_delete_data_for_user(self, *, requester, user_id):
        # This cog does not store any end user data whatsoever.
        return
    
    async def send_to_set_channel(self, ctx: commands.Context, embed, chantype: str):
        """
        Sends to the set giveaway donation request channel.
        """
        settings = await self.config.guild(ctx.guild).all()
        
        if chantype == "giveaway":
            channel = ctx.guild.get_channel(settings["gchannel_id"])
            pingrole = ctx.guild.get_role(settings["gman_id"])
            channeltype = "giveaway"
            lett = ""
        elif chantype == "event":
            channel = ctx.guild.get_channel(settings["echannel_id"])
            pingrole = ctx.guild.get_role(settings["eman_id"])
            channeltype = "event"
            lett = "n"
        else:
            channel = ctx.guild.get_channel(settings["hchannel_id"])
            pingrole = ctx.guild.get_role(settings["hman_id"])
            channeltype = "heist"
            lett = ""
        
        if not pingrole:
            try:
                await channel.send(embed=embed)
                await ctx.tick()
                return await ctx.send(f"You have sent a{lett} {channeltype} donation request. Please wait for a manager to respond.")
            except Exception:
                return await ctx.send(f"It appears that I do not see the {channeltype} donation request channel. It's most likely deleted or I do not have permission to view it.")
        else:
            am = discord.AllowedMentions(roles=True, users=False, everyone=False)
            try:
                await channel.send(content=pingrole.mention, embed=embed, allowed_mentions=am)
                await ctx.tick()
                return await ctx.send(f"You have sent a{lett} {channeltype} donation request. Please wait for a manager to respond.")
            except Exception:
                return await ctx.send(f"It appears that I do not see the {channeltype} donation request channel. It's most likely deleted or I do not have permission to view it.")
    
    @commands.command(name="sdonatehelp")
    @commands.bot_has_permissions(embed_links=True)
    async def sdonatehelp(self, ctx):
        """
        Know how to run the donation commands.
        
        Available commands:
        `[p]giveawaydonate`
        `[p]eventdonate`
        `[p]heistdonate`
        """
        gdono = f"Syntax: {ctx.prefix}giveawaydonate <type> <duration> <winners> <requirements> <prize> <message>\nAlias: {ctx.prefix}gdonate"
        edono = f"Syntax: {ctx.prefix}eventdonate <type> <event> <requirements> <prize> <message>\nAlias: {ctx.prefix}edonate"
        hdono = f"Syntax: {ctx.prefix}heistdonate <type> <requirements> <amount> <message>\nAlias: {ctx.prefix}hdonate"
        
        gdonodesc = f"""
        {box(gdono, "yaml")}
        *Arguments:*
        **Type**
        ` - ` The type should be the type of the currency or item that you would like to donate.
        ` - ` Requires double quotes `""` if it has some spaces.
        **Duration**
        ` - ` The duration is how long would the giveaway last.
        ` - ` Requires double quotes `""` if it has some spaces.
        **Winners**
        ` - ` The amount of winners for the giveaway.
        ` - ` Requires double quotes `""` if it has some spaces.
        **Requirements**
        ` - ` The requirements for the giveaway. (this can be anything like roles, messages, do this do that or anything you can imagine)
        ` - ` Type `none` if you do not want any requirements.
        ` - ` Requires double quotes `""` if it has some spaces.
        **Prize**
        ` - ` The prize of the giveaway.
        ` - ` Requires double quotes `""` if it has some spaces.
        **Message**
        ` - ` Send an optional message to the giveaway.
        ` - ` Type `none` if you do not want to send a message.
        ` - ` Does not require double quotes `""` if it has some spaces.
        
        Examples:
            `{ctx.prefix}giveawaydonate "Dank Memer" "1 day and 12 hours" 1w none "69 coins" hallo guys welcome to my minecraft channel.`
            `{ctx.prefix}gdonate dank 1d12h 1w none 420coins free 420 coins!!`
        """
        
        edonodesc = f"""
        {box(edono, "yaml")}
        *Arguments:*
        **Type**
        ` - ` The type should be the type of the currency or item that you would like to donate.
        ` - ` Requires double quotes `""` if it has some spaces.
        **Event**
        ` - ` The type of event that you want to sponsor. (this can be any event or games that users can play)
        ` - ` Requires double quotes `""` if it has some spaces.
        **Requirements**
        ` - ` The requirements for the giveaway. (this can be anything like roles, messages, do this do that or anything you can imagine)
        ` - ` Type `none` if you do not want any requirements.
        ` - ` Requires double quotes `""` if it has some spaces.
        **Prize**
        ` - ` The prize of the event.
        ` - ` Requires double quotes `""` if it has some spaces.
        **Message**
        ` - ` Send an optional message to the event.
        ` - ` Type `none` if you do not want to send a message.
        ` - ` Does not require double quotes `""` if it has some spaces.
        
        Examples:
            `{ctx.prefix}eventdonate "Owo bot" "Split Or Steal" none "1m owo coins" can i have chezburger plz`
            `{ctx.prefix}edonate owobot splitorsteal none 1mowocoins mmmmmm chezburger`
        """
        
        hdonodesc = f"""
        {box(hdono, "yaml")}
        *Arguments:*
        **Type**
        ` - ` The type should be the type of the currency or item that you would like to donate.
        ` - ` Requires double quotes `""` if it has some spaces.
        **Requirements**
        ` - ` The requirements for the giveaway. (this can be anything like roles, messages, do this do that or anything you can imagine)
        ` - ` Type `none` if you do not want any requirements.
        ` - ` Requires double quotes `""` if it has some spaces.
        **Amount**
        ` - ` The amount that you want to donate.
        ` - ` Requires double quotes `""` if it has some spaces.
        **Message**
        ` - ` Send an optional message to the event.
        ` - ` Type `none` if you do not want to send a message.
        ` - ` Does not require double quotes `""` if it has some spaces.
        
        Examples:
            `{ctx.prefix}heistdonate "Bro Bot" none "69420 coins" heist this shit up`
            `{ctx.prefix}hdonate brobot none 69420coins bored so heres a heist for yall`
        """
        
        em1 = discord.Embed(
            title=f"How to use `{ctx.prefix}giveawaydonate` command",
            description=gdonodesc,
            colour=await ctx.embed_colour()
        ).set_footer(text=f"Command executed by: {ctx.author} | Page 1/3", icon_url=ctx.author.avatar_url)
        
        em2 = discord.Embed(
            title=f"How to use `{ctx.prefix}eventdonate` command",
            description=edonodesc,
            colour=await ctx.embed_colour()
        ).set_footer(text=f"Command executed by: {ctx.author} | Page 2/3", icon_url=ctx.author.avatar_url)
        
        em3 = discord.Embed(
            title=f"How to use `{ctx.prefix}heistdonate` command",
            description=hdonodesc,
            colour=await ctx.embed_colour()
        ).set_footer(text=f"Command executed by: {ctx.author} | Page 3/3", icon_url=ctx.author.avatar_url)
        
        bemeds = [em1, em2, em3]
        await menu(ctx, bemeds, controls=DEFAULT_CONTROLS, timeout=60)
    
    @commands.group(name="serverdonationsset", aliases=["sdonateset"])
    @commands.guild_only()
    @commands.admin_or_permissions(administrator=True, manage_guild=True)
    @commands.bot_has_permissions(embed_links=True)
    async def serverdonationsset(self, ctx):
        """
        Settings for ServerDonations cog.
        
        See sub commands for more info.
        """
        
    @serverdonationsset.command(name="reset")
    async def serverdonationsset_reset(self, ctx):
        """
        Reset the serverdonations guild settings to default.
        """
        await ctx.send("Are you sure you want to reset the guild's settings to default? (`yes`/`no`)")

        pred = MessagePredicate.yes_or_no(ctx)
        try:
            await ctx.bot.wait_for("message", check=pred, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to respond. Cancelling.")
        
        if pred.result:
            await self.config.guild(ctx.guild).clear()
            await ctx.send("Successfully resetted the guild's settings to default.")
        else:
            await ctx.send("Alright not doing that then.")
    
    @serverdonationsset.group(name="pingrole")
    async def serverdonationsset_pingrole(self, ctx):
        """
        Commands to set or remove roles that gets pinged for donation requests.
        
        See sub commands for more info.
        """
        
    @serverdonationsset_pingrole.command(name="giveawaymanager", aliases=["gman"])
    async def serverdonationsset_pingrole_gman(
        self,
        ctx: commands.Context,
        role: discord.Role = None
    ):
        """
        Set or remove the giveaway manager ping role.
        
        This role gets pinged whenever there is a server giveaway donation request.
        Pass without role to remove the current set one.
        """
        settings = await self.config.guild(ctx.guild).gman_id()
        
        if not role:
            if not settings:
                return await ctx.send("It appears there is no set giveaway manager role. Set one by passing a role.")
            else:
                await self.config.guild(ctx.guild).gman_id.clear()
                return await ctx.send("The giveaway manager ping role has been removed.")
        
        if role.id == settings:
            return await ctx.send("It appears that role is already the set giveaway manager role.")
        
        await self.config.guild(ctx.guild).gman_id.set(role.id)
        await ctx.send(f"Successfully set `@{role.name}` as the giveaway manager ping role.")
            
    @serverdonationsset_pingrole.command(name="eventmanager", aliases=["eman"])
    async def serverdonationsset_pingrole_eman(
        self,
        ctx: commands.Context,
        role: discord.Role = None
    ):
        """
        Set or remove the event manager ping role.
        
        This role gets pinged whenever there is a server event donation request.
        Pass without role to remove the current set one.
        """
        settings = await self.config.guild(ctx.guild).eman_id()
        
        if not role:
            if not settings:
                return await ctx.send("It appears there is no set event manager role. Set one by passing a role.")
            else:
                await self.config.guild(ctx.guild).eman_id.clear()
                return await ctx.send("The event manager ping role has been removed.")
        
        if role.id == settings:
            return await ctx.send("It appears that role is already the set event manager ping role.")
        
        await self.config.guild(ctx.guild).eman_id.set(role.id)
        await ctx.send(f"Successfully set `@{role.name}` as the event manager role.")
            
    @serverdonationsset_pingrole.command(name="heistmanager", aliases=["hman"])
    async def serverdonationsset_pingrole_hman(
        self,
        ctx: commands.Context,
        role: discord.Role = None
    ):
        """
        Set or remove the heist manager ping role.
        
        This role gets pinged whenever there is a server heist donation request.
        Pass without role to remove the current set one.
        """
        settings = await self.config.guild(ctx.guild).hman_id()
        
        if not role:
            if not settings:
                return await ctx.send("It appears there is no set heist manager role. Set one by passing a role.")
            else:
                await self.config.guild(ctx.guild).hman_id.clear()
                return await ctx.send("The heist manager ping role has been removed.")
        
        if role.id == settings:
            return await ctx.send("It appears that role is already the set heist manager role.")
        
        await self.config.guild(ctx.guild).hman_id.set(role.id)
        await ctx.send(f"Successfully set `@{role.name}` as the heist manager ping role.")
            
    @serverdonationsset.group(name="channel", aliases=["chan"])
    async def serverdonationsset_channel(self, ctx):
        """
        Commands to set the requests on a specific channel.
        
        See sub commands for more info.
        """
        
    @serverdonationsset_channel.command(name="gchannel", aliases=["gchan"])
    async def serverdonationsset_channel_gchannel(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel = None
    ):
        """
        Set or remove the giveaway donation request channel.
        
        The gchannel is required for the `[p]giveawaydonate` command.
        Pass without channel to remove the current set one.
        """
        settings = await self.config.guild(ctx.guild).gchannel_id()
        
        if not channel:
            if not settings:
                return await ctx.send("It appears there is no set giveaway donation request channel. Ask an admin to set one.")
            else:
                await self.config.guild(ctx.guild).gchannel_id.clear()
                return await ctx.send("The giveaway donation request channel has been removed.")
            
        if channel.id == settings:
            return await ctx.send("It appears that channel is already the set giveaway donation request channel.")
        
        await self.config.guild(ctx.guild).gchannel_id.set(channel.id)
        await ctx.send(f"Successfully set {channel.mention} as the giveaway donation request channel.")
        
    @serverdonationsset_channel.command(name="echannel", aliases=["echan"])
    async def serverdonationsset_channel_echannel(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel = None
    ):
        """
        Set or remove the event donation requests channel.
        
        The echannel is required for the `[p]eventdonate` command.
        Pass without channel to remove the current set one.
        """
        settings = await self.config.guild(ctx.guild).echannel_id()
        
        if not channel:
            if not settings:
                return await ctx.send("It appears there is no set event donation request channel. Ask an admin to set one.")
            else:
                await self.config.guild(ctx.guild).echannel_id.clear()
                return await ctx.send("The event donation request channel has been removed.")
            
        if channel.id == settings:
            return await ctx.send("It appears that channel is already the set event donation request channel.")
        
        await self.config.guild(ctx.guild).echannel_id.set(channel.id)
        await ctx.send(f"Successfully set {channel.mention} as the event donation request channel.")
            
    @serverdonationsset_channel.command(name="hchannel", aliases=["hchan"])
    async def serverdonationsset_channel_hchannel(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel = None
    ):
        """
        Set or remove the heist donation request channel.
        
        The hchannel is required for the `[p]heistdonate` command.
        Pass without channel to remove the current set one.
        """
        settings = await self.config.guild(ctx.guild).hchannel_id()
        
        if not channel:
            if not settings:
                return await ctx.send("It appears there is no set heist donation request channel. Ask an admin to set one.")
            else:
                await self.config.guild(ctx.guild).hchannel_id.clear()
                return await ctx.send("The heist donation request channel has been removed.")
            
        if channel.id == settings:
            return await ctx.send("It appears that channel is already the set heist donation request channel.")
        
        await self.config.guild(ctx.guild).hchannel_id.set(channel.id)
        await ctx.send(f"Successfully set {channel.mention} as the heist donation request channel.")
            
    @serverdonationsset.command(name="showsetting", aliases=["showset", "ss", "showsettings"])
    async def serverdonationsset_showsetting(self, ctx):
        """
        See the guild settings set for ServerDonations.
        """
        settings = await self.config.guild(ctx.guild).all()
        
        gman = ctx.guild.get_role(settings["gman_id"])
        gman = gman.mention if gman else "No role set."
        
        eman = ctx.guild.get_role(settings["eman_id"])
        eman = eman.mention if eman else "No role set."
        
        hman = ctx.guild.get_role(settings["hman_id"])
        hman = hman.mention if hman else "No role set."
        
        gchan = ctx.guild.get_channel(settings["gchannel_id"])
        gchan = gchan.mention if gchan else "No channel set."
        
        echan = ctx.guild.get_channel(settings["echannel_id"])
        echan = echan.mention if echan else "No channel set."
        
        hchan = ctx.guild.get_channel(settings["hchannel_id"])
        hchan = hchan.mention if hchan else "No channel set."
        
        emb = discord.Embed(
            colour=await ctx.embed_colour(),
        )
        embed.set_author(name=f"ServerDonations settings for [{ctx.guild}]", icon_url=ctx.guild.icon_url)
        embed.add_field(name="Giveaway manager role:", value=gman, inline=True)
        embed.add_field(name="Event manager role:", value=eman, inline=True)
        embed.add_field(name="Heist manager role:", value=hman, inline=True)
        embed.add_field(name="Giveaway donate channel:", value=gchan, inline=True)
        embed.add_field(name="Event donate channel:", value=echan, inline=True)
        embed.add_field(name="Heist donate channel:", value=hchan, inline=True)
        
        await ctx.send(embed=embed)
        
    @commands.command(name="giveawaydonate", aliases=["gdonate"])
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def giveawaydonate(
        self,
        ctx: commands.Context,
        type,
        duration,
        winners,
        requirements,
        prize,
        *,
        message
    ):
        """
        Donate to server giveaways.
        
        Arguments must be split by `spaces`. If an argument contains a space, put it in quotes "".
        See `[p]sdonatehelp` to know how to donate.
        """
        settings = await self.config.guild(ctx.guild).gchannel_id()
        chantype = "giveaway"
        
        if not settings:
            return await ctx.send("No giveaway donation request channel set.")
        
        embed = discord.Embed(
            colour = await ctx.embed_colour(),
            title="Someone would like to donate for a giveaway!",
            timestamp=ctx.message.created_at
        )
        embed.set_thumbnail(url=ctx.author.avatar_url)
        embed.set_footer(text=ctx.guild, icon_url=ctx.guild.icon_url)
        embed.add_field(name="Donor:", value=ctx.author.mention, inline=False)
        embed.add_field(name="Type:", value=type, inline=True)
        embed.add_field(name="Duration:", value=duration, inline=True)
        embed.add_field(name="Winners:", value=winners, inline=False)
        embed.add_field(name="Requirements:", value=requirements, inline=True)
        embed.add_field(name="Prize:", value=prize, inline=True)
        embed.add_field(name="Message:", value=message, inline=False)
        embed.add_field(name="Jump to Command:", value=f"[[Click here]]({ctx.message.jump_url})", inline=False)
        
        await self.send_to_set_channel(ctx, embed=embed, chantype=chantype)
        
    @commands.command(name="eventdonate", aliases=["edonate"])
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def eventdonate(
        self,
        ctx: commands.Context,
        type,
        event,
        requirements,
        prize,
        *,
        message
    ):
        """
        Donate to server events.
        
        Arguments must be split by `spaces`. If an argument contains a space, put it in quotes "".
        See `[p]sdonatehelp` to know how to donate.
        """
        settings = await self.config.guild(ctx.guild).echannel_id()
        chantype = "event"
        
        if not settings:
            return await ctx.send("No event donation request channel set.")
            
        embed = discord.Embed(
            colour = await ctx.embed_colour(),
            title="Someone would like to donate for an event!",
            timestamp=ctx.message.created_at
        )
        embed.set_thumbnail(url=ctx.author.avatar_url)
        embed.set_footer(text=ctx.guild, icon_url=ctx.guild.icon_url)
        embed.add_field(name="Donor:", value=ctx.author.mention, inline=False)
        embed.add_field(name="Type:", value=type, inline=True)
        embed.add_field(name="Event:", value=event, inline=True)
        embed.add_field(name="Requirements:", value=requirements, inline=False)
        embed.add_field(name="Prize:", value=prize, inline=True)
        embed.add_field(name="Message:", value=message, inline=True)
        embed.add_field(name="Jump to Command:", value=f"[[Click here]]({ctx.message.jump_url})", inline=False)
        
        await self.send_to_set_channel(ctx, embed=embed, chantype=chantype)
        
    @commands.command(name="heistdonate", aliases=["hdonate"])
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def heistdonate(
        self,
        ctx: commands.Context,
        type,
        requirements,
        amount,
        *,
        message
    ):
        """
        Donate to server heists.
        
        Arguments must be split by `spaces`. If an argument contains a space, put it in quotes "".
        This command is especially designed for Bro bot and/or Dank Memer Bot or any other bot that has the similar feature.
        See `[p]sdonatehelp` to know how to donate.
        """
        settings = await self.config.guild(ctx.guild).hchannel_id()
        chantype = "heist"
        
        if not settings:
            return await ctx.send("No heist donation request channel set.")
            
        embed = discord.Embed(
            colour = await ctx.embed_colour(),
            title="Someone would like to donate for a heist!",
            timestamp=ctx.message.created_at
        )
        embed.set_thumbnail(url=ctx.author.avatar_url)
        embed.set_footer(text=ctx.guild, icon_url=ctx.guild.icon_url)
        embed.add_field(name="Donor:", value=ctx.author.mention, inline=False)
        embed.add_field(name="Type:", value=type, inline=True)
        embed.add_field(name="Amount:", value=amount, inline=True)
        embed.add_field(name="Requirements:", value=requirements, inline=False)
        embed.add_field(name="Message:", value=message, inline=False)
        embed.add_field(name="Jump to Command:", value=f"[[Click here]]({ctx.message.jump_url})", inline=False)
        
        await self.send_to_set_channel(ctx, embed=embed, chantype=chantype)
