import asyncio
import datetime
import discord
import logging

from typing import Literal, Optional

try:
    from slashtags import menu
    from redbot.core.utils.menus import DEFAULT_CONTROLS
except ModuleNotFoundError:
    from redbot.core.utils.menus import DEFAULT_CONTROLS, menu
from redbot.core.bot import Red
from redbot.core import commands, Config 
from redbot.core.utils.chat_formatting import humanize_list, pagify
from redbot.core.utils.predicates import MessagePredicate

class Afk(commands.Cog):
    """
    Notify users whenever you go AFK with pings logging.
    
    Be afk and notify users who ping you with a reason of your choice. This cog is inspired by sravan and Andy's afk cog.
    """
    
    def __init__(self, bot: Red) -> None:
        self.bot = bot
        
        self.config = Config.get_conf(self, identifier=54646544526864548, force_registration=True)
        default_guild = {
            "nick": True
        }
        default_member = {
            "afk": False,
            "sticky": False,
            "toggle_logs": True,
            "reason": None,
            "pinglogs": []
        }
        default_global = {
            "delete_after": 10
        }
        self.config.register_global(**default_global)
        self.config.register_guild(**default_guild)
        self.config.register_member(**default_member)
        self.log = logging.getLogger("red.WintersCogs.Afk")
        
    __version__ = "1.4.15"
    __author__ = ["Noobindahause#2808"]
    
    def format_help_for_context(self, ctx: commands.Context) -> str:
        """
        Thanks Sinbad and sravan!
        """
        p = "s" if len(self.__author__) != 1 else ""
        return f"{super().format_help_for_context(ctx)}\n\nCog Version: {self.__version__}\nCog Author{p}: {humanize_list(self.__author__)}"
    
    async def red_delete_data_for_user(
        self, *, requester: Literal["discord", "owner", "user", "user_strict"], user_id: int
    ):
        """
        This cog stores data provided by users for the express purpose of notifying users whenever they go AFK and only for that reason.
        It does not store user data which was not provided through a command.
        Users may remove their own content without making a data removal request.
        This cog does not support data requests, but will respect deletion requests.
        
        Also thanks sravan and aikaterna for the end user data statement!
        """
        for guild in self.bot.guilds:
            await self.config.member_from_id(guild.id, user_id).clear()
    
    async def start_afk(self, ctx: commands.Context, author: discord.Member, reason: str):
        """
        Start AFK status.
        """
        afk_reason = f"{author.mention} is currently AFK since <t:{round(datetime.datetime.now(datetime.timezone.utc).timestamp())}:R>.\n\n**Reason:**\n{reason}"
        await self.config.member(author).afk.set(True)
        await self.config.member(author).reason.set(afk_reason)

        if await self.config.guild(ctx.guild).nick():
            try:
                await author.edit(nick=f"[AFK] {author.display_name}", reason="User is AFK.")
            except discord.HTTPException:
                if author.id == ctx.guild.owner.id:
                    await ctx.send("Could not change your nick cause you are the guild owner.", delete_after=10)
                else:
                    await ctx.send("Could not change your nick due to role hierarchy or I'm missing the manage nicknames permission.", delete_after=10)
    
    async def end_afk(self, ctx: commands.Context, author: discord.Member):
        """
        End AFK status.
        """
        await self.config.member(author).afk.set(False)
        await self.config.member(author).reason.clear()

        if await self.config.guild(ctx.guild).nick():
            try:
                await author.edit(nick=f"{author.display_name}".replace("[AFK]", ""), reason="User is no longer AFK.")
            except discord.HTTPException:
                if author.id == ctx.guild.owner.id:
                    await ctx.send("Could not change your nick cause you are the guild owner.", delete_after=10)
                else:
                    await ctx.send("Could not change your nick due to role hierarchy or I'm missing the manage nicknames permission.", delete_after=10)

        if not await self.config.member(author).toggle_logs():
            return await self.config.member(author).pinglogs.clear()

        pings = await self.config.member(author).pinglogs()

        if pings:
            pinglist = """\n""".join(pings)
            pages = list(pagify(pinglist, delims=["` - `"], page_length=2000))
            final_page = {}

            for ind, page in enumerate(pages, 1):
                embed = discord.Embed(
                    title=f"You have recieved some pings while you were AFK, {author.name}.",
                    description=page,
                    color=discord.Colour.random()
                )
                embed.set_footer(text=f"Page ({ind}/{len(pages)})", icon_url=author.avatar_url)
                final_page[ind - 1] = embed

            await menu(ctx, list(final_page.values()), controls=DEFAULT_CONTROLS, timeout=120)
            await self.config.member(author).pinglogs.clear()
    
    async def log_and_notify(self, author: discord.Member, payload: discord.Message, ping_log):
        """
        Log pings and at the same time notify members when they mentioned an AFK memebr.
        """
        async with self.config.member(author).pinglogs() as pl:
            pl.append(ping_log)

        embed = discord.Embed(
            description=await self.config.member(author).reason(),
            colour=author.colour
        )
        embed.set_thumbnail(url=author.avatar_url)
        
        da = await self.config.guild(payload.guild).delete_after()
        
        return await payload.channel.send(embed=embed, reference=payload, mention_author=False,  delete_after=da) if da != 0 else await payload.channel.send(embed=embed, reference=payload, mention_author=False)

    @commands.Cog.listener("on_message_without_command")
    async def on_message_without_command(self, payload):
        if not payload.guild:
            return
        
        if payload.author.bot:
            return

        if await self.config.member(payload.author).sticky():
            pass
        elif await self.config.member(payload.author).afk():
            await payload.channel.send(f"Welcome back {payload.author.name}! I have removed your AFK status.")
            ctx = await self.bot.get_context(payload)
            await self.end_afk(ctx, payload.author)
        
        if not payload.mentions:
            return

        for afk_user in payload.mentions:
            if afk_user.id == payload.author.id:
                continue

            if not await self.config.member(afk_user).afk():
                continue

            ping_log = f"` - ` {payload.author.mention} [pinged you in]({payload.jump_url}) {payload.channel.mention} <t:{round(datetime.datetime.now(datetime.timezone.utc).timestamp())}:R>.\n**Message:** {payload.content}"
            
            await self.log_and_notify(afk_user, payload, ping_log)
    
    @commands.command(name="afk", aliases=["away"])
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.bot_has_permissions(embed_links=True)
    async def afk(self, ctx: commands.Context, *, reason: Optional[str]):
        """
        Be afk and notify users whenever they ping you.
        
        The reason is optional.
        """
        if await self.config.member(ctx.author).afk():
            return await ctx.send("It appears you are already AFK.")

        if not reason:
            reason = "No reason given."

        await ctx.send("You are now AFK. Any member that pings you will now get notified.")
        await self.start_afk(ctx, ctx.author, reason)
    
    @commands.group(name="afkset", aliases=["awayset"])
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def afkset(self, ctx):
        """
        Settings for the AFK cog.
        """
    
    @afkset.command(name="forceafk", aliases=["forceaway"])
    @commands.admin_or_permissions(manage_guild=True, administrator=True)
    async def forceafk(self, ctx: commands.Context, member: discord.Member, *, reason: Optional[str]):
        """
        Forcefully add or remove an AFK status on a user.
        """
        if ctx.bot.is_owner(ctx.author):
            pass
        elif member.id == ctx.guild.owner.id:
            return await ctx.send("I'm afraid you can not do that to the guild owner.")
        elif member.id == ctx.author.id:
            return await ctx.send(f"Why would you force AFK yourself? Please use `{ctx.prefix}afk`.")
        elif member.bot:
            return await ctx.send("I'm afraid you can not do that to bots.")
        elif ctx.author.id == ctx.guild.owner.id:
            pass
        elif member.top_role >= ctx.author.top_role:
            return await ctx.send("I'm afraid you can not do that due to role hierarchy.")
        
        if not reason:
            reason = "No reason given."

        if await self.config.member(member).afk():
            await ctx.send(f"Forcefully removed **{member}**'s AFK status.")
            return await self.end_afk(ctx, member)

        await ctx.send(f"Forcefully added **{member}**'s AFK status.")
        await self.start_afk(ctx, member, reason)
    
    @afkset.command(name="sticky")
    async def afkset_sticky(self, ctx):
        """
        Toggle whether to sticky your afk
        """
        current = await self.config.member(ctx.author).sticky()
        await self.config.member(ctx.author).sticky.set(not current)
        status = "will not" if current else "will now"
        await ctx.send(f"I {status} sticky your AFK.")
        
    @afkset.command(name="deleteafter", aliases=["da"])
    @commands.is_owner()
    async def afkset_deleteafter(self, ctx: commands.Context, seconds: Optional[int]):
        """
        Change the delete after on every AFK response on users.
        
        Put `0` to disable.
        Default is 10 seconds.
        """
        if not seconds:
            await self.config.delete_after.set(0)
            return await ctx.send("The delete after has been disabled.")
        
        if seconds >= 121:
            return await ctx.send("The maximum seconds of delete after is 120 seconds.")
        
        await self.config.delete_after.set(seconds)
        await ctx.send(f"Successfully set the delete after to {seconds} seconds.")
        
    @afkset.command(name="togglelogs")
    async def afkset_togglelogs(self, ctx):
        """
        Toggle whether to log all pings you recieved or not.
        """
        current = await self.config.member(ctx.author).toggle_logs()
        await self.config.member(ctx.author).toggle_logs.set(not current)
        status = "will not" if current else "will"
        await ctx.send(f"I {status} log all the pings you recieved.")
    
    @afkset.command(name="reset")
    async def afkset_reset(self, ctx):
        """
        Reset your AFK settings to default.
        """
        await ctx.send("This will reset your AFK settings, do you want to continue? (`yes`/`no`)")
        
        pred = MessagePredicate.yes_or_no(ctx)
        try:
            await ctx.bot.wait_for("message", check=pred, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to respond, cancelling.")
        
        if pred.result:
            await self.config.member(ctx.author).clear()
            await ctx.send("Successfully resetted your AFK settings.")
        else:
            await ctx.send("Alright not doing that then.")
    
    @afkset.command(name="nick")
    @commands.admin_or_permissions(manage_guild=True, administrator=True)
    async def afkset_nick(self, ctx):
        """
        Toggle whether to change the users nick with `[AFK] {user_display_name}` or not.
        
        This defaults to `True`.
        """
        current = await self.config.guild(ctx.guild).nick()
        await self.config.guild(ctx.guild).nick.set(not current)
        status = "will not" if current else "will"
        await ctx.send(f"I {status} edit the users nick whenever they go AFK.")
    
    @afkset.command(name="resetcog")
    @commands.is_owner()
    async def afkset_resetcog(self, ctx):
        """
        Reset the AFK cogs configuration.

        Bot owners only.
        """
        await ctx.send("This will reset the AFK cogs whole configuration, do you want to continue? (`yes`/`no`)")

        pred = MessagePredicate.yes_or_no(ctx)
        try:
            await ctx.bot.wait_for("message", check=pred, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to respond, cancelling.")

        if pred.result:
            await self.config.clear_all()
            return await ctx.send("Successfully cleared the AFK cogs configuration.")
        else:
            await ctx.send("Alright not doing that then.")
    
    @afkset.command(name="showsetting", aliases=["showsettings", "ss", "showset"])
    async def afkset_showsettings(self, ctx):
        """
        See your AFK settings.
        """
        member_settings = await self.config.member(ctx.author).all()
        guild_settings = await self.config.guild(ctx.guild).all()
        global_settings = await self.config.all()
        da = f"{global_settings['delete_after']} seconds." if global_settings['delete_after'] != 0 else "Disabled."
        gset = f"\n> Guild settings\n**Nick change:** {guild_settings['nick']}" if await ctx.bot.is_owner(ctx.author) or ctx.author.guild_permissions.manage_guild else ""
        globe = f"\n> Global settings\n**Delete after:** {da}" if await ctx.bot.is_owner(ctx.author) else ""
        
        embed = discord.Embed(
            title=f"{ctx.author.name}'s AFK settings.",
            description=f"**Is afk:** {member_settings['afk']}\n**Is sticky:** {member_settings['sticky']}\n**Ping logging:** {member_settings['toggle_logs']}\n{gset}\n{globe}",
            colour=ctx.author.colour,
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        await ctx.send(embed=embed)