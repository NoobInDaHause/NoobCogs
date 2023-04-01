import asyncio
import contextlib
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

RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]

class Afk(commands.Cog):
    """
    Notify users whenever you go AFK with pings logging.
    
    Be afk and notify users who ping you with a reason of your choice. This cog is inspired by sravan and Andy's afk cog.
    """
    
    def __init__(self, bot: Red) -> None:
        self.bot = bot
        
        self.config = Config.get_conf(self, identifier=54646544526864548, force_registration=True)
        default_member = {
            "afk": False,
            "sticky": False,
            "toggle_logs": True,
            "reason": None,
            "delete_after": 10,
            "pinglogs": []
        }
        self.config.register_member(**default_member)
        self.log = logging.getLogger("red.WintersCogs.Afk")
        
    __version__ = "1.0.0"
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
        """
        This cog stores data provided by users for the express purpose of notifying users whenever they go AFK and only for that reason. It does not store user data which was not provided through a command. Users may remove their own content without making a data removal request. This cog does not support data requests, but will respect deletion requests.
        
        Also thanks sravan!
        """
        super().red_delete_data_for_user(requester=requester, user_id=user_id)
        await self.config.user_from_id(user_id).clear()
    
    async def initialize(self, bot: Red):
        await bot.wait_until_red_ready()
        
    @commands.Cog.listener("on_message_without_command")
    async def on_message_without_command(self, message):
        # sourcery skip: low-code-quality
        if message.author.bot or not message.guild:
            return

        if await self.config.member(message.author).sticky():
            pass
        elif await self.config.member(message.author).afk():
            await message.channel.send(f"Welcome back {message.author.name}! I have removed your AFK status.")
            await self.config.member(message.author).afk.set(False)
            await self.config.member(message.author).reason.clear()
            with contextlib.suppress(discord.HTTPException):
                await message.author.edit(nick=f"{message.author.display_name}".replace("[AFK]", ""))
            
            if not await self.config.member(message.author).toggle_logs():
                return await self.config.member(message.author).pinglogs.clear()
            
            pings = await self.config.member(message.author).pinglogs()
            
            if pings:
                pinglist = """\n""".join(pings)
                pages = list(pagify(pinglist, delims=["` - `"], page_length=2000))
                final_page = {}
            
                for ind, page in enumerate(pages, 1):
                    embed = discord.Embed(
                        title=f"You have recieved some pings while you were AFK, {message.author.name}.",
                        description=page,
                        color=discord.Colour.random()
                    )
                    embed.set_footer(text=f"Page ({ind}/{len(pages)})", icon_url=message.author.avatar_url)
                    final_page[ind - 1] = embed
                
                ctx = await self.bot.get_context(message)
                await menu(ctx, list(final_page.values()), controls=DEFAULT_CONTROLS, timeout=120)
                await self.config.member(message.author).pinglogs.clear()
        
        if not message.mentions:
            return

        for afk_user in message.mentions:
            if afk_user == message.author:
                continue

            if not await self.config.member(afk_user).afk():
                continue
            
            async with self.config.member(afk_user).pinglogs() as pl:
                ping = f"` - ` {message.author.mention} [has pinged you in]({message.jump_url}) {message.channel.mention} <t:{round(datetime.datetime.now(datetime.timezone.utc).timestamp())}:R>.\n**Message Content:** {message.content}"
                pl.append(ping)
            
            embed = discord.Embed(
                description=await self.config.member(afk_user).reason(),
                colour=afk_user.colour
            )
            embed.set_thumbnail(url=afk_user.avatar_url)
            
            da = await self.config.member(afk_user).delete_after()
            
            if da == 0:
                await message.channel.send(
                    embed=embed, reference=message, mention_author=False
                )
            else:
                await message.channel.send(
                    embed=embed, reference=message, mention_author=False, delete_after=da
                )
    
    @commands.command(name="afk", aliases=["away"])
    @commands.guild_only()
    @commands.bot_has_permissions(manage_nicknames=True, embed_links=True)
    async def afk(self, ctx: commands.Context, *, reason: Optional[str] =  "No reason given."):
        """
        Be afk and notify users whenever they ping you.
        
        The reason is optional.
        """
        reason = f"{ctx.author.mention} is currently AFK since <t:{round(datetime.datetime.now(datetime.timezone.utc).timestamp())}:R>.\n\n**Reason:**\n{reason}"

        is_afk = await self.config.member(ctx.author).afk()

        if is_afk:
            return await ctx.send("It appears you are already AFK.")

        await self.config.member(ctx.author).afk.set(True)
        await self.config.member(ctx.author).reason.set(reason)

        with contextlib.suppress(discord.HTTPException):
            await ctx.author.edit(nick=f"[AFK] {ctx.author.display_name}")
            
        await ctx.send("You are now AFK. Any member that pings you will now get notified.")
        
        
    @commands.group(name="afkset", aliases=["awayset"])
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def afkset(self, ctx):
        """
        Settings for the AFK cog.
        """
    @afkset.command(name="forceafk", aliases=["forceaway"])
    @commands.bot_has_permissions(manage_nicknames=True)
    @commands.admin_or_permissions(manage_guild=True, administrator=True)
    async def forceafk(self, ctx: commands.Context, member: discord.Member, *, reason: Optional[str] = "No reason given."):
        """
        Forcefully add or remove an AFK status on a user.
        """
        if ctx.author.id == ctx.guild.owner.id:
            pass
        elif member.id == ctx.guild.owner.id:
            return await ctx.send("I'm afraid you can not do that to the guild owner.")
        elif member.bot:
            return await ctx.send("I'm afraid you can not do that to bots.")
        elif member.top_role >= ctx.author.top_role:
            return await ctx.send("I'm afraid you can not do that due to role hierarchy.")
        
        reason = f"{member.mention} is currently AFK since <t:{round(datetime.datetime.now(datetime.timezone.utc).timestamp())}:R>.\n\n**Reason:**\n{reason}"

        is_afk = await self.config.member(member).afk()
        pings = await self.config.member(member).pinglogs()
        tl = await self.config.member(member).toggle_logs()

        if is_afk:
            await self.config.member(member).afk.set(False)
            await self.config.member(member).reason.clear()
            with contextlib.suppress(discord.HTTPException):
                await member.edit(nick=f"{member.display_name}".replace("[AFK]", ""))
            await ctx.send(f"Forcefully removed **{member}**'s AFK status.")

            if not tl:
                return await self.config.member(member).pinglogs.clear()
            
            if pings:
                pinglist = """\n""".join(pings)
                pages = list(pagify(pinglist, delims=["` - `"], page_length=2000))
                final_page = {}

                for ind, page in enumerate(pages, 1):
                    embed = discord.Embed(
                        title=f"You have recieved some pings while you were AFK, {member.name}.",
                        description=page,
                        color=discord.Colour.random()
                    )
                    embed.set_footer(text=f"Page ({ind}/{len(pages)})", icon_url=member.avatar_url)
                    final_page[ind - 1] = embed

                await menu(ctx, list(final_page.values()), controls=DEFAULT_CONTROLS, timeout=120)
                await self.config.member(member).pinglogs.clear()
                
            return

        await self.config.member(member).afk.set(True)
        await self.config.member(member).reason.set(reason)
        with contextlib.suppress(discord.HTTPException):
            await member.edit(nick=f"[AFK] {member.display_name}")
        await ctx.send(f"Forcefully added **{member}**'s AFK status.")
    
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
    async def afkset_deleteafter(self, ctx: commands.Context, seconds: int):
        """
        Change the delete after on every AFK response on users.
        
        Put `0` to disable.
        Default is 10 seconds.
        """
        if seconds == 0:
            await self.config.member(ctx.author).delete_after.set(seconds)
            return await ctx.send("The delete after has been disabled.")
        
        if seconds > 120:
            return await ctx.send("The maximum seconds of delete after is 120 seconds.")
        
        await self.config.member(ctx.author).delete_after.set(seconds)
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
    
    @afkset.command(name="showsetting", aliases=["showsettings", "ss", "showset"])
    async def afkset_showsettings(self, ctx):
        """
        See your AFK settings.
        """
        da = await self.config.member(ctx.author).delete_after()
        is_afk = await self.config.member(ctx.author).afk()
        is_sticky = await self.config.member(ctx.author).sticky()
        tl = await self.config.member(ctx.author).toggle_logs()
        
        embed = discord.Embed(
            title=f"{ctx.author.name}'s AFK settings.",
            description=f"**Is afk:**\n{is_afk}\n**Is sticky:**\n{is_sticky}\n**Delete After:**\n{'None' if da == 0 else da}\n**Ping logging:**\n{tl}",
            colour=ctx.author.colour,
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        await ctx.send(embed=embed)