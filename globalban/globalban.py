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

class GlobalBan(commands.Cog):
    """
    Globally ban a user from all the guilds the bot is in.
    """
    
    def __init__(self, bot: Red) -> None:
        self.bot = bot

        self.config = Config.get_conf(self, identifier=74654871231365754648, force_registration=True)
        default_global = {
            "banlist": [],
            "banlogs": [],
            "create_modlog": False
        }
        self.config.register_global(**default_global)
        
    __version__ = "1.4.3"
    __author__ = ["Noobindahause#2808"]
    
    def format_help_for_context(self, ctx: commands.Context) -> str:
        """
        Thanks Sinbad and sravan!
        """
        p = "s" if len(self.__author__) != 1 else ""
        return f"{super().format_help_for_context(ctx)}\n\nCog Version: {self.__version__}\nCog Author{p}: {humanize_list(self.__author__)}"
    
    async def red_delete_data_for_user(
        self, *, requester: Literal["discord", "owner", "user", "user_strict"], user_id: int
    ) -> None:
        # This cog does not store any end user data whatsoever. But it stores user ID's for the ban list! Also thanks sravan!
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
        try:
            member = await ctx.bot.fetch_user(user_id)
        except discord.errors.NotFound:
            return await ctx.send("It appears that ID is not a valid user ID.")

        if str(user_id) in await self.config.banlist():
            return await ctx.send(f"**{member}** is already globally banned.")
        if user_id == ctx.author.id:
            return await ctx.send("I can not let you globally ban yourself.")
        if user_id == ctx.bot.user.id:
            return await ctx.send("You can not globally ban me! >:C")
        if not reason:
            reason = "No reason provided."
        
        await ctx.send(f"Are you sure you want to globally ban **{member}**? (`yes`/`no`)")

        pred = MessagePredicate.yes_or_no(ctx)
        try:
            await ctx.bot.wait_for("message", check=pred, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to respond, cancelling.")

        if not pred.result:
            return await ctx.send("Alright not doing that then.")
        
        await ctx.send("Alright this might take a while.")
        
        logs = await self.config.banlogs()
        
        async with self.config.banlogs() as gbl:
            log = f"> **GlobalBan Logs Case `#{len(logs) + 1}`**\n`Type:` GlobalBan\n`User:` {member} ({user_id})\n`Authorized by:` {ctx.author} ({ctx.author.id})\n`Reason:` {reason}\n`Timestamp:` <t:{round(datetime.datetime.now(datetime.timezone.utc).timestamp())}:F>"
            gbl.append(log)
        
        async with self.config.banlist() as bl:
            bl.append(str(user_id))
        
        errors = []
        guilds = []
        for guild in ctx.bot.guilds:
            try:
                guilds.append(guild)
                await guild.ban(member, reason=f"Global Ban authorized by {ctx.author} (ID: {ctx.author.id}). | Reason: {reason}")
                if await self.config.create_modlog():
                    await modlog.create_case(
                    bot=ctx.bot,
                    guild=guild,
                    created_at=datetime.datetime.now(datetime.timezone.utc),
                    action_type="globalban",
                    user=member,
                    moderator=ctx.bot.user,
                    reason=f"Authorized by {ctx.author} (ID: {ctx.author.id}). | Reason: {reason}",
                    until=None,
                    channel=None,
                    )
                await asyncio.sleep(10)
            except discord.HTTPException:
                errors.append(f"**{guild}**")
                
        await ctx.send(f"Globally banned **{member}** in **{len(guilds)}** guilds.")
        
        if errors:
            humanize_globalban = humanize_list(errors)
            embeds = []
            for page in pagify(humanize_globalban, delims=["\n"], page_length=1000):
                desc = f"An error occured when banning {member}.\nMost likely that I don't have ban permission or the user is already banned in these guild(s):\n{page}"
                embed = discord.Embed(
                    description=desc,
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
        try:
            member = await ctx.bot.fetch_user(user_id)
        except discord.errors.NotFound:
            return await ctx.send("It appears that is not a valid user ID.")

        if str(user_id) not in await self.config.banlist():
            return await ctx.send(f"**{member}** is not globally banned.")
        
        if not reason:
            reason = "No reason provided."
            
        await ctx.send(f"Are you sure you want to globally unban **{member}**? (`yes`/`no`)")

        pred = MessagePredicate.yes_or_no(ctx)
        try:
            await ctx.bot.wait_for("message", check=pred, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to respond, cancelling.")

        if not pred.result:
            return await ctx.send("Alright not doing that then.")
        
        await ctx.send("Alright this might take a while.")
        
        logs = await self.config.banlogs()
        
        async with self.config.banlogs() as gbl:
            log = f"> **GlobalBan Logs Case `#{len(logs) + 1}`**\n`Type:` GlobalUnBan\n`User:`{member} ({user_id})\n`Authorized by:` {ctx.author} ({ctx.author.id})\n`Reason:` {reason}\n`Timestamp:` <t:{round(datetime.datetime.now(datetime.timezone.utc).timestamp())}:F>"
            gbl.append(log)
        
        async with self.config.banlist() as bl:
            index = bl.index(str(user_id))
            bl.pop(index)
        
        errors = []
        guilds = []
        for guild in ctx.bot.guilds:
            try:
                guilds.append(guild)
                await guild.unban(member, reason=f"Global UnBan authorized by {ctx.author} (ID: {ctx.author.id}). | Reason: {reason}")
                if await self.config.create_modlog():
                    await modlog.create_case(
                    bot=ctx.bot,
                    guild=guild,
                    created_at=datetime.datetime.now(datetime.timezone.utc),
                    action_type="globalunban",
                    user=member,
                    moderator=ctx.bot.user,
                    reason=f"Authorized by {ctx.author} (ID: {ctx.author.id}). | Reason: {reason}",
                    until=None,
                    channel=None,
                    )
                await asyncio.sleep(10)
            except discord.HTTPException:
                errors.append(f"**{guild}**")
                
        await ctx.send(f"Globally unbanned **{member}** in **{len(guilds)}** guilds.")
        
        if errors:
            humanize_globalunban = humanize_list(errors)
            embeds = []
            for page in pagify(humanize_globalunban, delims=[""], page_length=1000):
                desc = f"An error occured when unbanning {member}.\nMost likely that I don't have ban permission or the user is not banned in these guild(s):\n{page}"
                embed = discord.Embed(
                    description=desc,
                    colour=await ctx.embed_colour(),
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                )
                embeds.append(embed)
        
            await menu(ctx, embeds, controls=DEFAULT_CONTROLS, timeout=60)
            
    @globalban.command(name="banlogs")
    async def globalban_banlogs(self, ctx):
        """
        Show the global ban or unban logs.
        """
        logs = await self.config.banlogs()
        
        if not logs:
            return await ctx.send("It appears there are no cases logged.")
        
        banlogs = """\n\n""".join(logs)
        pages = list(pagify(banlogs, delims=[" "], page_length=2000))
        final_page = {}
        
        for ind, page in enumerate(pages, 1):
            embed = discord.Embed(
                title="Globalban Case Logs",
                description=page,
                colour=await ctx.embed_colour(),
                timestamp=datetime.datetime.now(datetime.timezone.utc),
            )
            embed.set_footer(text=f"Page ({ind}/{len(pages)})")
            final_page[ind - 1] = embed
        
        await menu(ctx, list(final_page.values()), controls=DEFAULT_CONTROLS, timeout=60)
    
    @globalban.command(name="banlist")
    async def globalban_banlist(self, ctx):
        """
        Show the ban list.
        """
        bans = await self.config.banlist()
        
        if not bans:
            return await ctx.send("No users were globally banned.")
        
        banlist = ", ".join(bans)
        pages = list(pagify(banlist, delims=[" "], page_length=2000))
        final_page = {}
        
        for ind, page in enumerate(pages, 1):
            embed = discord.Embed(
                title="Globalban Ban List",
                description=page,
                colour=await ctx.embed_colour(),
                timestamp=datetime.datetime.now(datetime.timezone.utc),
            )
            embed.set_footer(text=f"Page ({ind}/{len(pages)})")
            final_page[ind - 1] = embed
        
        await menu(ctx, list(final_page.values()), controls=DEFAULT_CONTROLS, timeout=60)
        
    @globalban.group(name="reset")
    async def globalban_reset(self, ctx):
        """
        Reset any of the globalban config.
        """
    
    @globalban_reset.command(name="banlist")
    async def globalban_reset_banlist(self, ctx):
        """
        Reset or clear the ban list.

        Note: This will not unban any of the users that were globally banned.
        """
        await ctx.send("Are you sure you want to reset the globalban banlist? (`yes`/`no`)")
        
        pred = MessagePredicate.yes_or_no(ctx)
        try:
            await ctx.bot.wait_for("message", check=pred, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to respond. Cancelling.")
        
        if pred.result:
            await self.config.banlist.clear()
            await ctx.send("Successfully resetted the globalban banlist.")
        else:
            await ctx.send("Alright not doing that then.")
    
    @globalban_reset.command(name="banlogs")
    async def globalban_reset_banlogs(self, ctx):
        """
        Reset or clear the ban logs.

        Note: This will not unban any of the users that were globally banned.
        """
        await ctx.send("Are you sure you want to reset the globalban banlogs? (`yes`/`no`)")
        
        pred = MessagePredicate.yes_or_no(ctx)
        try:
            await ctx.bot.wait_for("message", check=pred, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to respond. Cancelling.")
        
        if pred.result:
            await self.config.banlogs.clear()
            await ctx.send("Successfully resetted the globalban banlogs.")
        else:
            await ctx.send("Alright not doing that then.")
    
    @globalban_reset.command(name="cog")
    async def globalban_reset_cog(self, ctx):
        """
        Reset the globalban cogs whole configuration.

        Note: This will not unban any of the users that were globally banned.
        """
        await ctx.send("This will reset the globalban cogs whole configuration, do you want to continue? (`yes`/`no`)")

        pred = MessagePredicate.yes_or_no(ctx)
        try:
            await ctx.bot.wait_for("message", check=pred, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to respond, cancelling.")

        if pred.result:
            await self.config.clear_all()
            return await ctx.send("Successfully cleared the globalban cogs configuration.")
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