import asyncio
import contextlib
import datetime
import discord

from typing import Literal, Optional

from redbot.core.bot import Red
from redbot.core import modlog, commands, Config
from redbot.core.utils.chat_formatting import humanize_list, pagify

from .buttons import Confirmation, Paginator, GbanViewReset

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
        
    __version__ = "1.0.0"
    __author__ = ["Noobindahause#2808"]
    
    def format_help_for_context(self, context: commands.Context) -> str:
        """
        Thanks Sinbad and sravan!
        """
        plural = "s" if len(self.__author__) != 1 else ""
        return f"{super().format_help_for_context(context)}\n\nCog Version: {self.__version__}\nCog Author{plural}: {humanize_list(self.__author__)}"
    
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

    @commands.hybrid_group(name="globalban", aliases=["gban"])
    @commands.is_owner()
    @commands.bot_has_permissions(embed_links=True)
    async def globalban(self, context: commands.Context):
        """
        Base commands for the GlobalBan Cog. (Bot owners only)
        """
    
    @globalban.command(name="ban")
    @discord.app_commands.describe(
        user_id="The ID of the User that you want to globally ban.",
        reason="The Optional reason for this global ban."
    )
    async def globalban_ban(
        self,
        context: commands.Context,
        user_id,
        *,
        reason: Optional[str] = "No reason provided."
    ):
        """
        Globally ban a user. (Bot owners only)
        """
        if not await context.bot.is_owner(context.author):
            return await context.reply("You do not have permission to run this command.", ephemeral=True)
        
        try:
            user_id = int(user_id)
        except ValueError:
            return await context.send("Please input a valid user ID.")
        
        try:
            member = await context.bot.fetch_user(user_id)
        except discord.errors.NotFound:
            return await context.send("It appears that ID is not a valid user ID.")

        if user_id in await self.config.banlist():
            return await context.send(f"**{member}** is already globally banned.")
        if user_id == context.author.id:
            return await context.send("I can not let you globally ban yourself.")
        if await context.bot.is_owner(member):
            return await context.send("You can not globally ban other bot owners.")
        if user_id == context.bot.user.id:
            return await context.send("You can not globally ban me! >:C")
        
        confirm_action = "Alright this might take a while."
        view = Confirmation(bot=self.bot, author=context.author, timeout=30, confirm_action=confirm_action)
        view.message = await context.send(f"Are you sure you want to globally ban **{member}**?", view=view)
        
        await view.wait()
        
        if view.value == "no":
            return
        
        logs = await self.config.banlogs()
        
        async with self.config.banlogs() as gbl:
            log = f"> **GlobalBan Logs Case `#{len(logs) + 1}`**\n`Type:` GlobalBan\n`User:` {member} ({user_id})\n`Authorized by:` {context.author} ({context.author.id})\n`Reason:` {reason}\n`Timestamp:` <t:{round(datetime.datetime.now(datetime.timezone.utc).timestamp())}:F>"
            gbl.append(log)
        
        async with self.config.banlist() as bl:
            bl.append(user_id)
        
        errors = []
        guilds = []
        for guild in context.bot.guilds:
            await asyncio.sleep(10)
            try:
                await guild.fetch_ban(member)
                errors.append(f"**{guild} (ID: {guild.id})**")
            except discord.errors.NotFound:
                try:
                    await guild.ban(member, reason=f"Global Ban authorized by {context.author} (ID: {context.author.id}). | Reason: {reason}")
                    guilds.append(guild)
                    if await self.config.create_modlog():
                        await modlog.create_case(
                        bot=context.bot,
                        guild=guild,
                        created_at=datetime.datetime.now(datetime.timezone.utc),
                        action_type="globalban",
                        user=member,
                        moderator=context.bot.user,
                        reason=f"Authorized by {context.author} (ID: {context.author.id}). | Reason: {reason}",
                        until=None,
                        channel=None,
                        )
                except discord.HTTPException:
                    errors.append(f"**{guild} (ID: {guild.id})**")
                
        await context.send(f"Globally banned **{member}** in **{len(guilds)}** guilds.")
        
        if errors:
            em = ", ".join(errors)
            pages = list(pagify(em, delims=[", "], page_length=2000))
            final_page = {}
            
            for ind, page in enumerate(pages, 1):
                desc = f"Most likely that I don't have ban permission or the user is already banned.\nErrored guild(s):\n{page}"
                embed = discord.Embed(
                    title=f"An error occured when banning {member}.",
                    description=desc,
                    colour=await context.embed_colour(),
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                )
                embed.set_footer(text=f"Page ({ind}/{len(pages)})")
                final_page[ind - 1] = embed
        
            pages = Paginator(bot=self.bot, author=context.author, pages=list(final_page.values()), timeout=60)
            await pages.start(context)
            
    @globalban.command(name="unban")
    @discord.app_commands.describe(
        user_id="The ID of the User that you want to globally unban.",
        reason="The Optional reason for this global unban."
    )
    async def globalban_unban(
        self,
        context: commands.Context,
        user_id,
        *,
        reason: Optional[str] = "No reason provided."
    ):
        """
        Globally unban a user.
        """
        if not await context.bot.is_owner(context.author):
            return await context.reply("You do not have permission to run this command.", ephemeral=True)

        try:
            user_id = int(user_id)
        except ValueError:
            return await context.send("Please input a valid user ID.")
        
        try:
            member = await context.bot.fetch_user(user_id)
        except discord.errors.NotFound:
            return await context.send("It appears that is not a valid user ID.")

        if user_id not in await self.config.banlist():
            return await context.send(f"**{member}** is not globally banned.")
            
        confirm_action = "Alright this might take a while."
        view = Confirmation(bot=self.bot, author=context.author, timeout=30, confirm_action=confirm_action)
        view.message = await context.send(f"Are you sure you want to globally unban **{member}**?", view=view)
        
        await view.wait()
        
        if view.value == "no":
            return
        
        logs = await self.config.banlogs()
        
        async with self.config.banlogs() as gbl:
            log = f"> **GlobalBan Logs Case `#{len(logs) + 1}`**\n`Type:` GlobalUnBan\n`User:` {member} ({user_id})\n`Authorized by:` {context.author} ({context.author.id})\n`Reason:` {reason}\n`Timestamp:` <t:{round(datetime.datetime.now(datetime.timezone.utc).timestamp())}:F>"
            gbl.append(log)
        
        async with self.config.banlist() as bl:
            index = bl.index(user_id)
            bl.pop(index)
        
        errors = []
        guilds = []
        for guild in context.bot.guilds:
            await asyncio.sleep(10)
            try:
                await guild.unban(member, reason=f"Global UnBan authorized by {context.author} (ID: {context.author.id}). | Reason: {reason}")
                guilds.append(guild)
                if await self.config.create_modlog():
                    await modlog.create_case(
                    bot=context.bot,
                    guild=guild,
                    created_at=datetime.datetime.now(datetime.timezone.utc),
                    action_type="globalunban",
                    user=member,
                    moderator=context.bot.user,
                    reason=f"Authorized by {context.author} (ID: {context.author.id}). | Reason: {reason}",
                    until=None,
                    channel=None,
                    )
            except discord.HTTPException:
                errors.append(f"**{guild} (ID: {guild.id})**")
                
        await context.send(f"Globally unbanned **{member}** in **{len(guilds)}** guilds.")
        
        if errors:
            em = ", ".join(errors)
            pages = list(pagify(em, delims=[", "], page_length=2000))
            final_page = {}
            
            for ind, page in enumerate(pages, 1):
                desc = f"Most likely that I don't have ban permission or the user is not banned.\nErrored guild(s):\n{page}"
                embed = discord.Embed(
                    title=f"An error occured when unbanning {member}.",
                    description=desc,
                    colour=await context.embed_colour(),
                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                )
                embed.set_footer(text=f"Page ({ind}/{len(pages)})")
                final_page[ind - 1] = embed
        
            pages = Paginator(bot=self.bot, author=context.author, pages=list(final_page.values()), timeout=60)
            await pages.start(context)
            
    @globalban.command(name="logs")
    async def globalban_logs(self, context: commands.Context):
        """
        Show the global ban or unban logs.
        """
        if not await context.bot.is_owner(context.author):
            return await context.reply("You do not have permission to run this command.", ephemeral=True)

        logs = await self.config.banlogs()
        
        if not logs:
            return await context.send("It appears there are no cases logged.")
        
        banlogs = """\n\n""".join(logs)
        pages = list(pagify(banlogs, delims=["> "], page_length=2000))
        final_page = {}
        
        for ind, page in enumerate(pages, 1):
            embed = discord.Embed(
                title="Globalban Case Logs",
                description=page,
                colour=await context.embed_colour(),
                timestamp=datetime.datetime.now(datetime.timezone.utc),
            )
            embed.set_footer(text=f"Page ({ind}/{len(pages)})")
            final_page[ind - 1] = embed
        
        pages = Paginator(bot=self.bot, author=context.author, pages=list(final_page.values()), timeout=60)
        await pages.start(context)
    
    @globalban.command(name="list")
    async def globalban_list(self, context: commands.Context):
        """
        Show the ban list.
        """
        if not await context.bot.is_owner(context.author):
            return await context.reply("You do not have permission to run this command.", ephemeral=True)

        bans = await self.config.banlist()
        
        if not bans:
            return await context.send("No users were globally banned.")
        
        users = []
        for mem in bans:
            try:
                member = await context.bot.fetch_user(mem)
                l = f"` #{len(users) + 1} ` {member} (ID: {member.id})"
                users.append(l)
            except discord.errors.NotFound:
                continue
        
        banlist = "\n".join(users)
        pages = list(pagify(banlist, delims=["` #"], page_length=2000))
        final_page = {}
        
        for ind, page in enumerate(pages, 1):
            embed = discord.Embed(
                title="Globalban Ban List",
                description=page,
                colour=await context.embed_colour(),
                timestamp=datetime.datetime.now(datetime.timezone.utc),
            )
            embed.set_footer(text=f"Page ({ind}/{len(pages)})")
            final_page[ind - 1] = embed
        
        pages = Paginator(bot=self.bot, author=context.author, pages=list(final_page.values()), timeout=60)
        await pages.start(context)
        
    @globalban.command(name="reset")
    async def globalban_reset(self, context: commands.Context):
        """
        Reset any of the globalban config.
        """
        if not await context.bot.is_owner(context.author):
            return await context.reply("You do not have permission to run this command.", ephemeral=True)
        
        view = GbanViewReset(bot=self.bot, author=context.author, config=self.config, timeout=30)
        view.message = await context.send(content="Choose what config to reset.", view=view)
        
        await view.wait()
    
    @globalban.command(name="createmodlog")
    @discord.app_commands.describe(
        state="True or False."
    )
    async def globalban_createmodlog(self, context: commands.Context, state: bool):
        """
        Toggle whether to make a modlog case when you globally ban or unban a user.
        """
        if not await context.bot.is_owner(context.author):
            return await context.reply("You do not have permission to run this command.", ephemeral=True)
        
        await self.config.create_modlog.set(state)
        status = "will now" if state else "will not"
        await context.send(f"I {status} make a modlog case whenever you globally ban or unban a user.")