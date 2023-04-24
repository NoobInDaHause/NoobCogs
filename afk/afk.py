import datetime
import discord
import logging

from redbot.core.bot import Red
from redbot.core import commands, Config
from redbot.core.utils.chat_formatting import humanize_list, pagify

from typing import Literal, Optional

from .views import Paginator, Confirmation

class Afk(commands.Cog):
    """
    Notify users whenever you go AFK with pings logging.
    
    Be afk and notify users who ping you with a reason of your choice. This cog is inspired by sravan and Andy's afk cog.
    """
    
    def __init__(self, bot: Red) -> None:
        self.bot = bot
        
        self.config = Config.get_conf(self, identifier=54646544526864548, force_registration=True)
        default_guild = {
            "nick": True,
            "delete_after": 10
        }
        default_member = {
            "afk": False,
            "sticky": False,
            "toggle_logs": True,
            "reason": None,
            "pinglogs": []
        }
        self.config.register_guild(**default_guild)
        self.config.register_member(**default_member)
        self.log = logging.getLogger("red.WintersCogs.Afk")
        
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
    ):
        """
        This cog stores data provided by users for the express purpose of notifying users whenever they go AFK and only for that reason.
        It does not store user data which was not provided through a command.
        Users may remove their own content without making a data removal request.
        This cog does not support data requests, but will respect deletion requests.
        
        Also thanks sravan and aikaterna for the end user data statement!
        """
        await self.config.user_from_id(user_id).clear()
    
    async def start_afk(self, context: commands.Context, author: discord.Member, reason: str):
        """
        Start AFK status.
        """
        afk_reason = f"{author.mention} is currently AFK since <t:{round(datetime.datetime.now(datetime.timezone.utc).timestamp())}:R>.\n\n**Reason:**\n{reason}"
        await self.config.member(author).afk.set(True)
        await self.config.member(author).reason.set(afk_reason)

        if await self.config.guild(context.guild).nick():
            try:
                await author.edit(nick=f"[AFK] {author.display_name}", reason="User is AFK.")
            except discord.HTTPException:
                if author.id == context.guild.owner.id:
                    await context.channel.send("Could not change your nick cause you are the guild owner.", delete_after=10)
                else:
                    await context.channel.send("Could not change your nick due to role hierarchy or I'm missing the manage nicknames permission.", delete_after=10)
    
    async def end_afk(self, context: commands.Context, author: discord.Member):
        """
        End AFK status.
        """
        await self.config.member(author).afk.set(False)
        await self.config.member(author).reason.clear()

        if await self.config.guild(context.guild).nick():
            try:
                await author.edit(nick=f"{author.display_name}".replace("[AFK]", ""), reason="User is no longer AFK.")
            except discord.HTTPException:
                if author.id == context.guild.owner.id:
                    await context.send(content="Could not change your nick cause you are the guild owner.", delete_after=10, ephemeral=True)
                else:
                    await context.send(content="Could not change your nick due to role hierarchy or I'm missing the manage nicknames permission.", delete_after=10, ephemeral=True)

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
                embed.set_footer(text=f"Page ({ind}/{len(pages)})", icon_url=author.avatar.url)
                final_page[ind - 1] = embed

            pages = Paginator(bot=self.bot, author=author, pages=list(final_page.values()), timeout=60)
            await pages.start(context)
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
        ).set_thumbnail(url=author.avatar.url)
        
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
            context = await self.bot.get_context(payload)
            await self.end_afk(context, payload.author)
        
        if not payload.mentions:
            return

        for afk_user in payload.mentions:
            if afk_user.id == payload.author.id:
                continue

            if not await self.config.member(afk_user).afk():
                continue

            ping_log = f"` - ` {payload.author.mention} [pinged you in]({payload.jump_url}) {payload.channel.mention} <t:{round(datetime.datetime.now(datetime.timezone.utc).timestamp())}:R>.\n**Message:** {payload.content}"
            
            await self.log_and_notify(afk_user, payload, ping_log)
    
    @commands.hybrid_command(name="afk", aliases=["away"])
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.bot_has_permissions(embed_links=True)
    @discord.app_commands.guild_only()
    @discord.app_commands.describe(
        reason="The optional reason for the AFK."
    )
    async def afk(
        self,
        context: commands.Context,
        *,
        reason: Optional[str] = "No reason given."
    ):
        """
        Be afk and notify users whenever they ping you.
        
        The reason is optional.
        """
        if await self.config.member(context.author).afk():
            return await context.send("It appears you are already AFK.")

        await context.send("You are now AFK. Any member that pings you will now get notified.")
        await self.start_afk(context, context.author, reason)
    
    @commands.hybrid_group(name="afkset", aliases=["awayset"])
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def afkset(self, context: commands.Context):
        """
        Settings for the AFK cog.
        """
    
    @afkset.command(name="forceafk", aliases=["forceaway"])
    @commands.admin_or_permissions(manage_guild=True, administrator=True)
    @discord.app_commands.guild_only()
    @discord.app_commands.describe(
        member="The member that you want to forcefully set or remove an AFK status to.",
        reason="The optional reason for the AFK."
    )
    async def afkset_forceafk(
        self,
        context: commands.Context,
        member: discord.Member,
        *,
        reason: Optional[str] = "No reason given."
    ):
        """
        Forcefully add or remove an AFK status on a user.
        """
        if not context.author.guild_permissions.manage_guild:
            return await context.reply(content="You do not have permission to use this command.", ephemeral=True)
        
        if member.id == context.guild.owner.id:
            return await context.send("I'm afraid you can not do that to the guild owner.")
        elif member.id == context.author.id:
            return await context.send(f"Why would you force AFK yourself? Please use `{context.prefix}afk`.")
        elif member.bot:
            return await context.send("I'm afraid you can not do that to bots.")
        elif context.author.id == context.guild.owner.id:
            pass
        elif member.top_role >= context.author.top_role:
            return await context.send("I'm afraid you can not do that due to role hierarchy.")

        if await self.config.member(member).afk():
            await context.send(f"Forcefully removed **{member}**'s AFK status.")
            return await self.end_afk(context, member)

        await context.send(f"Forcefully added **{member}**'s AFK status.")
        await self.start_afk(context, member, reason)
    
    @afkset.command(name="sticky")
    @discord.app_commands.guild_only()
    @discord.app_commands.describe(
        state="True or False."
    )
    async def afkset_sticky(
        self,
        context: commands.Context,
        state: bool
    ):
        """
        Toggle whether to sticky your afk
        """
        await self.config.member(context.author).sticky.set(state)
        status = "will now" if state else "will not"
        await context.send(f"I {status} sticky your AFK.")
        
    @afkset.command(name="deleteafter", aliases=["da"])
    @commands.admin_or_permissions(manage_guild=True, administrator=True)
    @discord.app_commands.describe(
        seconds="The amount of seconds before the notify embed gets deleted."
    )
    async def afkset_deleteafter(
        self,
        context: commands.Context,
        seconds: Optional[int]
    ):
        """
        Change the delete after on every AFK response on users.
        
        Put `0` to disable.
        Default is 10 seconds.
        """
        if not context.author.guild_permissions.manage_guild:
            return await context.reply(content="You do not have permission to use this command.", ephemeral=True)

        if not seconds:
            await self.config.guild(context.guild).delete_after.set(0)
            return await context.send("The delete after has been disabled.")
        
        if seconds >= 121:
            return await context.send("The maximum seconds of delete after is 120 seconds.")
        
        await self.config.guild(context.guild).delete_after.set(seconds)
        await context.send(f"Successfully set the delete after to {seconds} seconds.")
        
    @afkset.command(name="togglelogs")
    @discord.app_commands.guild_only()
    @discord.app_commands.describe(
        state="True or False."
    )
    async def afkset_togglelogs(
        self,
        context: commands.Context,
        state: bool
    ):
        """
        Toggle whether to log all pings you recieved or not.
        """
        await self.config.member(context.author).toggle_logs.set(state)
        status = "will now" if state else "will not"
        await context.send(f"I {status} log all the pings you recieved.")
    
    @afkset.command(name="reset")
    @discord.app_commands.guild_only()
    async def afkset_reset(self, context: commands.Context):
        """
        Reset your AFK settings to default.
        """
        confirm_action = "Successfully resetted your AFK settings."
        view = Confirmation(bot=self.bot, author=context.author, timeout=30, confirm_action=confirm_action)
        view.message = await context.send("Are you sure you want to reset your AFK settings?", view=view)
        
        await view.wait()
        
        if view.value == "yes":
            await self.config.member(context.author).clear()
    
    @afkset.command(name="nick")
    @commands.admin_or_permissions(manage_guild=True, administrator=True)
    @discord.app_commands.guild_only()
    @discord.app_commands.describe(
        state="True or False."
    )
    async def afkset_nick(
        self,
        context: commands.Context,
        state: bool
    ):
        """
        Toggle whether to change the users nick with `[AFK] {user_display_name}` or not.
        
        This defaults to `True`.
        """
        if not context.author.guild_permissions.manage_guild:
            return await context.reply(content="You do not have permission to use this command.", ephemeral=True)

        await self.config.guild(context.guild).nick.set(state)
        status = "will now" if state else "will not"
        await context.send(f"I {status} edit the users nick whenever they go AFK.")
    
    @afkset.command(name="resetcog")
    @commands.is_owner()
    async def afkset_resetcog(self, context: commands.Context):
        """
        Reset the AFK cogs configuration. (Bot owners only.)
        """
        if not context.bot.is_owner(context.author):
            return await context.reply(content="You do not have permission to use this command.", ephemeral=True)
        
        confirm_action = "Successfully resetted the AFK cogs configuration."
        view = Confirmation(bot=self.bot, author=context.author, timeout=30, confirm_action=confirm_action)
        view.message = await context.send("Are you sure you want to reset the AFK cogs whole configuration?", view=view)
        
        await view.wait()
        
        if view.value == "yes":
            await self.config.clear_all()
    
    @afkset.command(name="showsettings", aliases=["showsetting", "ss", "showset"])
    @discord.app_commands.guild_only()
    async def afkset_showsettings(self, context: commands.Context):
        """
        See your AFK settings.
        """
        member_settings = await self.config.member(context.author).all()
        guild_settings = await self.config.guild(context.guild).all()
        da = f"{guild_settings['delete_after']} seconds." if guild_settings['delete_after'] != 0 else "Disabled."
        gset = f"\n> Guild settings\n**Nick change:** {guild_settings['nick']}\n**Delete after:** {da}" if await context.bot.is_owner(context.author) or context.author.guild_permissions.manage_guild else ""
        
        embed = discord.Embed(
            title=f"{context.author.name}'s AFK settings.",
            description=f"**Is afk:** {member_settings['afk']}\n**Is sticky:** {member_settings['sticky']}\n**Ping logging:** {member_settings['toggle_logs']}\n{gset}",
            colour=context.author.colour,
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        await context.send(embed=embed)
