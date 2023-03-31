import asyncio
import contextlib
import datetime
import discord

from typing import Literal

try:
    from slashtags import menu
    from redbot.core.utils.menus import DEFAULT_CONTROLS
except ModuleNotFoundError:
    from redbot.core.utils.menus import DEFAULT_CONTROLS, menu
from redbot.core.bot import Red
from redbot.core import modlog, commands, Config
from redbot.core.utils.chat_formatting import humanize_list, pagify
from redbot.core.utils.predicates import MessagePredicate

RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]

class GlobalBan(commands.Cog):
    """
    Globally ban a user from all the guilds the bot is in.
    """
    
    def __init__(self, bot: Red) -> None:
        self.bot = bot
        self.config = Config.get_conf(self, identifier=74654871231365754648, force_registration=True)
        default_global = {"banlist": [], "create_modlog": False}
        self.config.register_global(**default_global)
        
    __version__ = "1.1.3"
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
    
    async def initialize(self, bot: Red):
        await bot.wait_until_red_ready()
        await self.register_casetypes()

    @staticmethod
    async def register_casetypes():
        globalban_types = [
            {
                "name": "globalban",
                "default_setting": True,
                "image": ":earth_americas::hammer:",
                "case_str": "GlobalBan",
            },
            {
                "name": "globalunban",
                "default_setting": True,
                "image": ":earth_americas::dove:",
                "case_str": "GlobalUnBan",
            }
        ]
        with contextlib.suppress(RuntimeError):
            await modlog.register_casetypes(globalban_types)
            
    @commands.group(name="globalban", aliases=["gban"])
    @commands.is_owner()
    @commands.bot_has_permissions(embed_links=True)
    async def globalban(self, ctx):
        """
        Globally ban or unban a user from the guilds the bot is in.
        """
    
    @globalban.command(name="ban")
    async def globalban_ban(self, ctx: commands.Context, user_id: int, *, reason = None):
        """
        Globally ban a user.
        """
        if user_id in await self.config.banlist():
            return await ctx.send("That user is already globally banned.")
        
        if not reason:
            reason = "No reason provided."
        
        errors = []
        guilds = []
        member = await ctx.bot.fetch_user(user_id)
        for guild in ctx.bot.guilds:
            try:
                guilds.append(guild)
                await guild.ban(member, reason=f"Global Ban authorized by {ctx.author} (ID: {ctx.author.id}).\nReason: {reason}")
                if await self.config.create_modlog():
                    await modlog.create_case(
                    bot=ctx.bot,
                    guild=guild,
                    created_at=datetime.datetime.now(datetime.timezone.utc),
                    action_type="globalban",
                    user=member,
                    moderator=ctx.bot.user,
                    reason=f"Authorized by {ctx.author} (ID: {ctx.author.id}).\nReason: {reason}",
                    until=None,
                    channel=None,
                    )
                async with self.config.banlist() as bl:
                    bl.append(user_id)
            except discord.HTTPException:
                errors.append(f"**{guild}**")
                
        await ctx.send(f"Globally banned **{member}** in **{len(guilds)}** guilds.")
        
        if errors:
            humanize_globalban = humanize_list(errors)
            embeds = []
            for page in pagify(humanize_globalban, delims=["\n"], page_length=1000):
                embed = discord.Embed(
                    title=f"An error occured while banning {member} in these guild(s)",
                    description=page,
                    colour=await ctx.embed_colour(),
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                )
                embeds.append(embed)
        
            await menu(ctx, embeds, controls=DEFAULT_CONTROLS, timeout=60)
            
    @globalban.command(name="unban")
    async def globalban_unban(self, ctx: commands.Context, user_id: int, *, reason = None):
        """
        Globally unban a user.
        """
        if user_id not in await self.config.banlist():
            return await ctx.send("That user is not globally banned.")
        
        if not reason:
            reason = "No reason provided."
            
        errors = []
        guilds = []
        member = await ctx.bot.fetch_user(user_id)
        for guild in ctx.bot.guilds:
            try:
                guilds.append(guild)
                await guild.unban(member, reason=f"Global UnBan authorized by {ctx.author} (ID: {ctx.author.id}).\nReason: {reason}")
                if await self.config.create_modlog():
                    await modlog.create_case(
                    bot=ctx.bot,
                    guild=guild,
                    created_at=datetime.datetime.now(datetime.timezone.utc),
                    action_type="globalunban",
                    user=member,
                    moderator=ctx.bot.user,
                    reason=f"Authorized by {ctx.author} (ID: {ctx.author.id}).\nReason: {reason}",
                    until=None,
                    channel=None,
                    )
                async with self.config.banlist() as bl:
                    index = bl.index(user_id)
                    bl.pop(index)
            except discord.HTTPException:
                errors.append(f"**{guild}**")
                
        await ctx.send(f"Globally unbanned **{member}** in **{len(guilds)}** guilds.")
        
        if errors:
            humanize_globalunban = humanize_list(errors)
            embeds = []
            for page in pagify(humanize_globalunban, delims=["\n"], page_length=1000):
                embed = discord.Embed(
                    title=f"An error occured while unbanning {member} in these guild(s)",
                    description=page,
                    colour=await ctx.embed_colour(),
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                )
                embeds.append(embed)
        
            await menu(ctx, embeds, controls=DEFAULT_CONTROLS, timeout=60)
            
    @globalban.command(name="list")
    async def globalban_list(self, ctx):
        """
        Show the ban list.
        """
        banlist = await self.config.banlist()
        
        if not banlist:
            return await ctx.send("No users were globally banned.")
        
        humanize_banlist = humanize_list(banlist)
        embeds = []
        for page in pagify(humanize_banlist, delims=["\n"], page_length=1000):
            embed = discord.Embed(
                title="Globalban List",
                description=page,
                colour=await ctx.embed_colour(),
                timestamp=datetime.datetime.now(datetime.timezone.utc),
            )
            embeds.append(embed)
        
        await menu(ctx, embeds, controls=DEFAULT_CONTROLS, timeout=60)
        
    @globalban.command(name="reset")
    async def globalban_reset(self, ctx):
        """
        Reset the globalban cog.
        """
        await ctx.send("Are you sure you want to reset the globalban cog? (`yes`/`no`)")
        
        pred = MessagePredicate.yes_or_no(ctx)
        try:
            await ctx.bot.wait_for("message", check=pred, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to respond. Cancelling.")
        
        if pred.result:
            await self.config.banlist.clear()
            await ctx.send("Successfully resetted the globalban cog.")
        else:
            await ctx.send("Alright not doing that then.")
    
    @globalban.command(name="createmodlog")
    async def globalban_createmodlog(self, ctx):
        """
        Toggle whether to make a modlog case when you globally ban or unban a user.
        """
        current = await self.config.create_modlog()
        await self.config.create_modlog.set(not current)
        status = "will not" if current else "will"
        await ctx.send(f"I {status} make a modlog case whenever you globally ban or unban a user.")