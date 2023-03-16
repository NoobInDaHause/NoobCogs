import asyncio
import discord
import logging

from redbot.core import commands, Config
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list, box
from redbot.core.utils.predicates import MessagePredicate

from disputils import BotEmbedPaginator


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
        
    __version__ = "1.0.1"
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
    
    async def _send_to_gchan(self, ctx: commands.Context, embed):
        """
        Sends to the set giveaway donation request channel.
        """
        settings = await self.config.guild(ctx.guild).all()
        
        channel = ctx.guild.get_channel(settings["gchannel_id"])
        gman_pingrole = ctx.guild.get_role(settings["gman_id"])
        
        if not gman_pingrole:
            try:
                return await channel.send(embed=embed)
            except discord.HTTPException:
                return await ctx.send("It appears that I do not see the giveaway donation request channel. It's most likely deleted or I do not have permission to view it.")
        else:
            am = discord.AllowedMentions(roles=True, users=False, everyone=False)
            return await channel.send(content=gman_pingrole.mention, embed=embed, allowed_mentions=am)
    
    async def _send_to_echan(self, ctx: commands.Context, embed):
        """
        Sends to the set event donation request channel.
        """
        settings = await self.config.guild(ctx.guild).all()
        
        channel = ctx.guild.get_channel(settings["echannel_id"])
        eman_pingrole = ctx.guild.get_role(settings["eman_id"])
        
        if not eman_pingrole:
            try:
                return await channel.send(embed=embed)
            except discord.HTTPException:
                return await ctx.send("It appears that I do not see the event donation request channel. It's most likely deleted or I do not have permission to view it.")
        else:
            am = discord.AllowedMentions(roles=True, users=False, everyone=False)
            return await channel.send(content=eman_pingrole.mention, embed=embed, allowed_mentions=am)
        
    async def _send_to_hchan(self, ctx: commands.Context, embed):
        """
        Sends to the set heist donation request channel.
        """
        settings = await self.config.guild(ctx.guild).all()
        
        channel = ctx.guild.get_channel(settings["hchannel_id"])
        hman_pingrole = ctx.guild.get_role(settings["hman_id"])
        
        if not hman_pingrole:
            try:
                return await channel.send(embed=embed)
            except discord.HTTPException:
                return await ctx.send("It appears that I do not see the heist donation request channel. It's most likely deleted or I do not have permission to view it.")
        else:
            am = discord.AllowedMentions(roles=True, users=False, everyone=False)
            return await channel.send(content=hman_pingrole.mention, embed=embed, allowed_mentions=am)
    
    @commands.command(name="sdonohelp")
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def sdonohelp(self, ctx):
        """
        Know how to run the donation commands.
        
        Available commands:
        `[p]giveawaydonate`
        `[p]eventdonate`
        `[p]heistdonate`
        """
        emotes = ["⏪", "◀️", "▶️", "⏩", "❌"]
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
            `{ctx.prefix}eventdonate "Owo bot" "Split Or Steal" none "A sloppy burger" can i have chezburger plz`
            `{ctx.prefix}edonate owobot splitorsteal none sloppyburger mmmmmm chezburger`
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
        ).set_footer(text=f"Command executed by: {ctx.author} | Page", icon_url=ctx.author.avatar_url)
        
        em2 = discord.Embed(
            title=f"How to use `{ctx.prefix}eventdonate` command",
            description=edonodesc,
            colour=await ctx.embed_colour()
        ).set_footer(text=f"Command executed by: {ctx.author} | Page", icon_url=ctx.author.avatar_url)
        
        em3 = discord.Embed(
            title=f"How to use `{ctx.prefix}heistdonate` command",
            description=hdonodesc,
            colour=await ctx.embed_colour()
        ).set_footer(text=f"Command executed by: {ctx.author} | Page", icon_url=ctx.author.avatar_url)
        
        bemeds = [em1, em2, em3]
        paginator = BotEmbedPaginator(ctx, bemeds, control_emojis=emotes)
        await paginator.run(timeout=60)
    
    @commands.group(name="serverdonationsset", aliases=["sdonateset", "sdonoset"])
    @commands.guild_only()
    @commands.admin_or_permissions(administrator=True)
    @commands.bot_has_permissions(embed_links=True)
    async def serverdonationsset(self, ctx):
        """
        Settings for ServerDonations cog.
        
        See sub commands for more info.
        """
        
    @serverdonationsset.group(name="pingrole", invoke_without_command=True)
    async def serverdonationsset_pingrole(self, ctx):
        """
        Commands to set or remove roles that gets pinged for donations.
        
        See sub commands for more info.
        """
        await ctx.send_help()
        
    @serverdonationsset_pingrole.group(name="gman", invoke_without_command=True)
    async def serverdonationsset_pingrole_gman(self, ctx):
        """
        Set or remove the giveaway manager ping role.
        """
        await ctx.send_help()
        
    @serverdonationsset_pingrole_gman.command(name="set")
    async def serverdonationsset_pingrole_gman_set(
        self,
        ctx: commands.Context,
        *,
        role: discord.Role = None
    ):
        """
        Set the giveaway manager ping role.
        
        This role gets pinged whenever there is a server giveaway donation request.
        """
        settings = await self.config.guild(ctx.guild).gman_id()
        gmanrole = [settings]
        
        if not role:
            return await ctx.send_help()
        
        if role.id in gmanrole:
            return await ctx.send("It appears that role is already the set giveaway manager role.")
        
        if settings:
            return await ctx.send("It appears you already have a giveaway manager role set.")
        
        await self.config.guild(ctx.guild).gman_id.set(role.id)
        await ctx.send(f"Successfully set `@{role.name}` as the giveaway manager role.")
        
    @serverdonationsset_pingrole_gman.command(name="remove")
    async def serverdonationsset_pingrole_gman_remove(self, ctx):
        """
        Remove the set giveaway manager ping role.
        """
        settings = await self.config.guild(ctx.guild).gman_id()
        
        if not settings:
            return await ctx.send("It appears you do not have a giveaway manager role set.")
        
        await ctx.send("Are you sure you want to remove the set giveaway manager role? (`yes`/`no`)")
        
        pred = MessagePredicate.yes_or_no(ctx)
        try:
            await ctx.bot.wait_for("message", check=pred, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to respond. Cancelling.")
        
        if pred.result:
            await self.config.guild(ctx.guild).gman_id.clear()
            await ctx.send("Successfullt removed the giveaway manager role.")
        else:
            await ctx.send("Alright not doing that then.")
            
    @serverdonationsset_pingrole.group(name="eman", invoke_without_command=True)
    async def serverdonationsset_pingrole_eman(self, ctx):
        """
        Set or remove the event manager ping role.
        """
        await ctx.send_help()
        
    @serverdonationsset_pingrole_eman.command(name="set")
    async def serverdonationsset_pingrole_eman_set(
        self,
        ctx: commands.Context,
        *,
        role: discord.Role = None
    ):
        """
        Set the event manager ping role.
        
        This role gets pinged whenever there is a server event donation request.
        """
        settings = await self.config.guild(ctx.guild).eman_id()
        emanrole = [settings]
        
        if not role:
            return await ctx.send_help()
        
        if role.id in emanrole:
            return await ctx.send("It appeats that role is already the set event manager role.")
        
        if settings:
            return await ctx.send("It appears you already have a set event manager role.")
        
        await self.config.guild(ctx.guild).eman_id.set(role.id)
        await ctx.send(f"Successfully set `@{role.name}` as the event manager role.")
        
    @serverdonationsset_pingrole_eman.command(name="remove")
    async def serverdonationsset_pingrole_eman_remove(self, ctx):
        """
        Remove the set event manager ping role.
        """
        settings = await self.config.guild(ctx.guild).eman_id()
        
        if not settings:
            return await ctx.send("It appears you do not have a set event manager role.")
        
        await ctx.send("Are you sure you want to remove the set event manager role? (`yes`/`no`)")
        
        pred = MessagePredicate.yes_or_no(ctx)
        try:
            await ctx.bot.wait_for("message", check=pred, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to respond. Cancelling.")
        
        if pred.result:
            await self.config.guild(ctx.guild).eman_id.clear()
            await ctx.send("Successfullt removed the event manager role.")
        else:
            await ctx.send("Alright not doing that then.")
            
    @serverdonationsset_pingrole.group(name="hman", invoke_without_command=True)
    async def serverdonationsset_pingrole_hman(self, ctx):
        """
        Set or remove the heist manager ping role.
        
        This role gets pinged whenever there is a server heist donation request.
        """
        await ctx.send_help()
        
    @serverdonationsset_pingrole_hman.command(name="set")
    async def serverdonationsset_pingrole_hman_set(
        self,
        ctx: commands.Context,
        *,
        role: discord.Role = None
    ):
        """
        Set the heist manager ping role.
        """
        settings = await self.config.guild(ctx.guild).hman_id()
        hmanrole = [settings]
        
        if not role:
            return await ctx.send_help()
        
        if role.id in hmanrole:
            return await ctx.send("It appeats that role is already the set heist manager role.")
        
        if settings:
            return await ctx.send("It appears you already have a set heist manager role.")
        
        await self.config.guild(ctx.guild).hman_id.set(role.id)
        await ctx.send(f"Successfully set `@{role.name}` as the heist manager role.")
        
    @serverdonationsset_pingrole_hman.command(name="remove")
    async def serverdonationsset_pingrole_hman_remove(self, ctx):
        """
        Remove the set heist manager ping role.
        """
        settings = await self.config.guild(ctx.guild).hman_id()
        
        if not settings:
            return await ctx.send("It appeats you do not have a set heist manager role.")
        
        await ctx.send("Are you sure you want to remove the set heist manager role? (`yes`/`no`)")
        
        pred = MessagePredicate.yes_or_no(ctx)
        try:
            await ctx.bot.wait_for("message", check=pred, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to respond. Cancelling.")
        
        if pred.result:
            await self.config.guild(ctx.guild).hman_id.clear()
            await ctx.send("Successfullt removed the heist manager role.")
        else:
            await ctx.send("Alright not doing that then.")
            
    @serverdonationsset.group(name="channel", aliases=["chan"], invoke_without_command=True)
    async def serverdonationsset_channel(self, ctx):
        """
        Commands to restrict serverdonations command on a channel.
        
        See sub commands for more info.
        """
        await ctx.send_help()
        
    @serverdonationsset_channel.group(name="gchannel", aliases=["gchan"], invoke_without_command=True)
    async def serverdonationsset_channel_gchannel(self, ctx):
        """
        Set or remove the giveaway donation channel.
        
        The gchannel is required for the `[p]giveawaydonate` command.
        """
        await ctx.send_help()
        
    @serverdonationsset_channel_gchannel.command(name="set")
    async def serverdonationsset_channel_gchannel_set(
        self,
        ctx: commands.Context,
        *,
        channel: discord.TextChannel = None
    ):
        """
        Set the channel for giveaway donation requests.
        """
        settings = await self.config.guild(ctx.guild).gchannel_id()
        gtextchan = [settings]
        
        if not channel:
            return await ctx.send_help()
        
        if channel.id in gtextchan:
            return await ctx.send("It appears that channel is already the set giveaway channel.")
        
        if settings:
            return await ctx.send("You already have a set giveaway channel.")
        
        await self.config.guild(ctx.guild).gchannel_id.set(channel.id)
        await ctx.send(f"Successfully set {channel.mention} as the giveaway donation requests channel.")
        
    @serverdonationsset_channel_gchannel.command(name="remove")
    async def serverdonationsset_channel_gchannel_remove(self, ctx):
        """
        Remove the set giveaway donation request channel.
        """
        settings = await self.config.guild(ctx.guild).gchannel_id()
        
        if not settings:
            return await ctx.send("It appears you do not have a set giveaway donation request channel.")
        
        await ctx.send("Are you sure you want to remove the giveaway donation requests channel? (`yes`/`no`)")
        
        pred = MessagePredicate.yes_or_no(ctx)
        try:
            await ctx.bot.wait_for("message", check=pred, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to respond. Cancelling.")
        
        await self.config.guild(ctx.guild).gchannel_id.clear()
        await ctx.send("Successfully removed the giveaway donation request channel.")
        
    @serverdonationsset_channel.group(name="echannel", aliases=["echan"], invoke_without_command=True)
    async def serverdonationsset_channel_echannel(self, ctx):
        """
        Set or remove the channel for event donation requests.
        
        The echannel is required for the `[p]eventdonate` command.
        """
        await ctx.send_help()
        
    @serverdonationsset_channel_echannel.command(name="set")
    async def serverdonationsset_channel_echannel_set(
        self,
        ctx: commands.Context,
        *,
        channel: discord.TextChannel = None
    ):
        """
        Set the channel for event donation requests.
        """
        settings = await self.config.guild(ctx.guild).echannel_id()
        etextchan = [settings]
        
        if not channel:
            return await ctx.send_help()
        
        if channel.id in etextchan:
            return await ctx.send("It appears that channel is already the set event donation request channel.")
        
        if settings:
            return await ctx.send("It appears you already have set event donation request channel.")
        
        await self.config.guild(ctx.guild).echannel_id.set(channel.id)
        await ctx.send(f"Successfullt set {channel.mention} as the event donation request channel.")
        
    @serverdonationsset_channel_echannel.command(name="remove")
    async def serverdonationsset_channel_echannel_remove(self, ctx):
        """
        Remove the set event donation request channel,
        """
        settings = await self.config.guild(ctx.guild).echannel_id()
        
        if not settings:
            return await ctx.send("It appears you do not have a set event donation request channel.")
        
        await ctx.send("Are you sure you want to remove the set event donation request channel? (`yes`/`no`)")
        
        pred = MessagePredicate.yes_or_no(ctx)
        try:
            await ctx.bot.wait_for("message", check=pred, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to respond. Cancelling.")
        
        if pred.result:
            await self.config.guild(ctx.guild).echannel_id.clear()
            await ctx.send("Successfullt removed the event donation request channel.")
        else:
            await ctx.send("Alright not doing that then.")
            
    @serverdonationsset_channel.group(name="hchannel", aliases=["hchan"], invoke_without_command=True)
    async def serverdonationsset_channel_hchannel(self, ctx):
        """
        Set or remove the heist donation request channel.
        
        The hchannel is required for the `[p]heistdonate` command.
        """
        await ctx.send_help()
        
    @serverdonationsset_channel_hchannel.command(name="set")
    async def serverdonationsset_channel_hchannel_set(
        self,
        ctx: commands.Context,
        *,
        channel: discord.TextChannel = None
    ):
        """
        Set the channel for heist donation requests.
        """
        settings = await self.config.guild(ctx.guild).hchannel_id()
        htextchan = [settings]
        
        if not channel:
            return await ctx.send_help()
        
        if channel.id in htextchan:
            return await ctx.send("It appears that channel is already the set heist donation request channel.")
        
        if settings:
            return await ctx.send("It appears you already have a set heist donation request channel.")
        
        await self.config.guild(ctx.guild).hchannel_id.set(channel.id)
        await ctx.send(f"Successfully set {channel.mention} as the heist donation request channel.")
        
    @serverdonationsset_channel_hchannel.command(name="remove")
    async def serverdonationsset_channel_hchannel_remove(self, ctx):
        """
        Remove the set heist donation request channel.
        """
        settings = await self.config.guild(ctx.guild).hchannel_id()
        
        if not settings:
            return await ctx.send("It appears you do not have a set heist donation request channel.")
        
        await ctx.send("Are you sure you want to remove the heist donation request channel? (`yes`/`no`)")
        
        pred = MessagePredicate.yes_or_no(ctx)
        try:
            await ctx.bot.wait_for("message", check=pred, tiemout=30)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to respond. Cancelling.")
        
        if pred.result:
            await self.config.guild(ctx.guild).hchannel_id.clear()
            await ctx.send("Successfully removed the heist donation request channel.")
        else:
            await ctx.send("Alright not doing that then.")
            
    @serverdonationsset.command(name="showsetting", aliases=["showset", "ss", "showsettings"])
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @commands.admin_or_permissions(administrator=True)
    async def serverdonationsset_showsetting(self, ctx):
        """
        See the guild settings set for ServerDonations.
        """
        settings = await self.config.guild(ctx.guild).all()
        
        gman = ctx.guild.get_role(settings["gman_id"])
        gman = "No giveaway manager role set." if not gman else gman.mention
        
        eman = ctx.guild.get_role(settings["eman_id"])
        eman = "No event manager role set." if not eman else eman.mention
        
        hman = ctx.guild.get_role(settings["hman_id"])
        hman = "No heist manager role set." if not hman else hman.mention
        
        gchan = ctx.guild.get_channel(settings["gchannel_id"])
        gchan = "No giveaway donation request channel set." if not gchan else gchan.mention
        
        echan = ctx.guild.get_channel(settings["echannel_id"])
        echan = "No event donation request channel set." if not echan else echan.mention
        
        hchan = ctx.guild.get_channel(settings["hchannel_id"])
        hchan = "No heist donation request channel set." if not hchan else hchan.mention
        
        emb = discord.Embed(
            colour=await ctx.embed_colour(),
        )
        emb.set_author(name=f"ServerDonations settings for [{ctx.guild}]", icon_url=ctx.guild.icon_url)
        emb.add_field(name="Giveaway manager role:", value=gman, inline=False)
        emb.add_field(name="Event manager role:", value=eman, inline=False)
        emb.add_field(name="Heist manager role:", value=hman, inline=False)
        emb.add_field(name="Giveaway donation request channel:", value=gchan, inline=False)
        emb.add_field(name="Event donation request channel:", value=echan, inline=False)
        emb.add_field(name="Heist donation request channel:", value=hchan, inline=False)
        
        await ctx.send(embed=emb)
        
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
        See `[p]sdonohelp` to know how to donate.
        """
        settings = await self.config.guild(ctx.guild).gchannel_id()
        gchan = [settings]
        
        if not settings:
            return await ctx.send("No giveaway donation request channel set.")
        
        if ctx.channel.id not in gchan:
            return await ctx.send(f"This command is restricted to be only used in <#{settings}>")
        
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
        
        await ctx.tick()
        await self._send_to_gchan(ctx, embed=embed)
        
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
        See `[p]sdonohelp` to know how to donate.
        """
        settings = await self.config.guild(ctx.guild).echannel_id()
        echan = [settings]
        
        if not settings:
            return await ctx.send("No event donation request channel set.")
        
        if ctx.channel.id not in echan:
            return await ctx.send(f"This command is restricted to be only used in <#{settings}>")
            
        emb = discord.Embed(
            colour = await ctx.embed_colour(),
            title="Someone would like to donate for an event!",
            timestamp=ctx.message.created_at
        )
        emb.set_thumbnail(url=ctx.author.avatar_url)
        emb.set_footer(text=ctx.guild, icon_url=ctx.guild.icon_url)
        emb.add_field(name="Donor:", value=ctx.author.mention, inline=False)
        emb.add_field(name="Type:", value=type, inline=True)
        emb.add_field(name="Event:", value=event, inline=True)
        emb.add_field(name="Requirements", value=requirements, inline=False)
        emb.add_field(name="Prize:", value=prize, inline=True)
        emb.add_field(name="Message:", value=message, inline=True)
        
        await ctx.tick()
        await self._send_to_echan(ctx, embed=emb)
        
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
        See `[p]sdonohelp` to know how to donate.
        """
        settings = await self.config.guild(ctx.guild).hchannel_id()
        hchan = [settings]
        
        if not settings:
            return await ctx.send("No heist donation request channel set.")
        
        if ctx.channel.id not in hchan:
            return await ctx.send(f"This command is restricted to be only used in <#{settings}>")
            
        emb = discord.Embed(
            colour = await ctx.embed_colour(),
            title="Someone would like to donate for a heist!",
            timestamp=ctx.message.created_at
        )
        emb.set_thumbnail(url=ctx.author.avatar_url)
        emb.set_footer(text=ctx.guild, icon_url=ctx.guild.icon_url)
        emb.add_field(name="Donor:", value=ctx.author.mention, inline=False)
        emb.add_field(name="Type:", value=type, inline=True)
        emb.add_field(name="Amount:", value=amount, inline=True)
        emb.add_field(name="Requirements:", value=requirements, inline=False)
        emb.add_field(name="Message:", value=message, inline=False)
        
        await ctx.tick()
        await self._send_to_hchan(ctx, embed=emb)