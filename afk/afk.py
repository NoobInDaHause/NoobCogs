import datetime
import discord
import logging

from redbot.core import app_commands, commands, Config
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list, pagify
from redbot.core.utils.menus import menu

from typing import Literal, Optional

from .views import Confirmation

class Afk(commands.Cog):
    """
    Notify users whenever you go AFK with pings logging.
    
    Be afk and notify users who ping you with a reason of your choice. This cog is inspired by sravan and Andy's afk cog.
    [Click here](https://github.com/NoobInDaHause/WintersCogs/blob/red-3.5/afk/README.md) to see all the commands available for Afk.
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
        self.log = logging.getLogger("red.NoobCogs.Afk")
        
    __version__ = "1.0.3"
    __author__ = ["Noobindahause#2808"]
    
    def format_help_for_context(self, context: commands.Context) -> str:
        """
        Thanks Sinbad and sravan!
        """
        p = "s" if len(self.__author__) != 1 else ""
        return f"""{super().format_help_for_context(context)}
        
        Cog Version: {self.__version__}
        Cog Author{p}: {humanize_list(self.__author__)}
        """
    
    async def red_delete_data_for_user(
        self, *, requester: Literal["discord_deleted_user", "owner", "user", "user_strict"], user_id: int
    ):
        """
        This cog stores data provided by users for the express purpose of notifying users whenever they go AFK and only for that reason.
        It does not store user data which was not provided through a command.
        Users may remove their own content without making a data removal request.
        This cog does not support data requests, but will respect deletion requests.
        
        Also thanks sravan and aikaterna for the end user data statement!
        """
        for guild in self.bot.guilds:
            await self.config.member_from_ids(guild_id=guild.id, member_id=user_id).clear()
    
    async def start_afk(self, payload: discord.Message, user: discord.Member, reason: str):
        """
        Start AFK status.
        """
        await self.config.member(user).afk.set(True)
        await self.config.member(user).reason.set(reason)

        if await self.config.guild(payload.guild).nick():
            try:
                await user.edit(nick=f"[AFK] {user.display_name}", reason="User is AFK.")
            except discord.errors.Forbidden:
                if user.id == payload.guild.owner.id:
                    await payload.channel.send("Could not change your nick cause you are the guild owner.", delete_after=10)
                else:
                    await payload.channel.send("Could not change your nick due to role hierarchy or I'm missing the manage nicknames permission.", delete_after=10)
    
    async def end_afk(self, payload: discord.Message, user: discord.Member):
        """
        End AFK status.
        """
        await payload.channel.send(f"Welcome back {user.name}! I have removed your AFK status.")
        await self.config.member(user).afk.set(False)
        await self.config.member(user).reason.clear()

        if await self.config.guild(payload.guild).nick():
            try:
                await user.edit(nick=f"{user.display_name}".replace("[AFK]", ""), reason="User is no longer AFK.")
            except discord.errors.Forbidden:
                if user.id == payload.guild.owner.id:
                    await payload.channel.send(content="Could not change your nick cause you are the guild owner.", delete_after=10)
                else:
                    await payload.channel.send(content="Could not change your nick due to role hierarchy or I'm missing the manage nicknames permission.", delete_after=10)

        if not await self.config.member(user).toggle_logs():
            return await self.config.member(user).pinglogs.clear()

        pings = await self.config.member(user).pinglogs()
        pinglist = """\n""".join(pings)
        pages = list(pagify(pinglist, delims=["` - `"], page_length=2000))
        final_page = {}

        for ind, page in enumerate(pages, 1):
            embed = discord.Embed(
                title=f"You have recieved some pings while you were AFK, {user.name}.",
                description=page,
                color=user.colour
            )
            embed.set_footer(text=f"Page ({ind}/{len(pages)})", icon_url=user.avatar.url)
            final_page[ind - 1] = embed

        context = await self.bot.get_context(payload)
        await menu(context, list(final_page.values()), timeout=60)
        await self.config.member(user).pinglogs.clear()
    
    async def log_and_notify(self, payload: discord.Message, afk_user: discord.Member):
        """
        Log pings and at the same time notify members when they mentioned an AFK memebr.
        """
        async with self.config.member(afk_user).pinglogs() as pl:
            ping_log = f"` - ` {payload.author.mention} [pinged you in]({payload.jump_url}) {payload.channel.mention} <t:{round(datetime.datetime.now(datetime.timezone.utc).timestamp())}:R>.\n**Message:** {payload.content}"
            pl.append(ping_log)

        embed = discord.Embed(
            description=f"{afk_user.mention} is currently AFK since <t:{round(datetime.datetime.now(datetime.timezone.utc).timestamp())}:R>.\n\n**Reason:**\n{await self.config.member(afk_user).reason()}",
            colour=afk_user.colour
        ).set_thumbnail(url=afk_user.avatar.url)

        da = await self.config.guild(payload.guild).delete_after()

        return (
            await payload.channel.send(
                embed=embed,
                reference=payload,
                mention_author=False,
                delete_after=da,
            )
            if da != 0
            else await payload.channel.send(
                embed=embed, reference=payload, mention_author=False
            )
        )
    
    @commands.Cog.listener("on_message_without_command")
    async def on_message_without_command(self, payload: discord.Message):
        if not payload.guild:
            return
        
        if payload.author.bot:
            return

        if await self.config.member(payload.author).sticky():
            pass
        elif await self.config.member(payload.author).afk():
            await self.end_afk(payload=payload, user=payload.author)
        
        if not payload.mentions:
            return

        for afk_user in payload.mentions:
            if afk_user.id == payload.author.id:
                continue

            if not await self.config.member(afk_user).afk():
                continue
            
            await self.log_and_notify(payload=payload, afk_user=afk_user)
    
    @commands.hybrid_command(name="afk", aliases=["away"])
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.bot_has_permissions(embed_links=True, manage_nicknames=True)
    @app_commands.guild_only()
    @app_commands.describe(
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
            return await context.reply(content="It appears you are already AFK.", ephemeral=True, mention_author=False)

        await context.send("You are now AFK. Any member that pings you will now get notified.")
        await self.start_afk(payload=context.message, user=context.author, reason=reason)
    
    @commands.group(name="afkset", invoke_without_command=True, aliases=["awayset"])
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def afkset(self, context: commands.Context):
        """
        Settings for the AFK cog.
        """
        await context.send_help()
    
    @afkset.command(name="deleteafter", aliases=["da"])
    @commands.has_permissions(manage_guild=True)
    async def afkset_deleteafter(
        self,
        context: commands.Context,
        seconds: Optional[int]
    ):
        """
        Change the delete after on every AFK notify.
        
        Leave `seconds` blank to disable.
        Default is 10 seconds.
        """
        if not seconds:
            await self.config.guild(context.guild).delete_after.set(0)
            return await context.send("The delete after has been disabled.")
        
        if seconds >= 121:
            return await context.send("The maximum seconds of delete after is 120 seconds.")
        
        await self.config.guild(context.guild).delete_after.set(seconds)
        await context.send(f"Successfully set the delete after to {seconds} seconds.")
    
    @afkset.command(name="forceafk", aliases=["forceaway"])
    @commands.has_permissions(manage_guild=True)
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
        if await context.bot.is_owner(context.author):
            if await self.config.member(member).afk():
                await context.reply(content=f"Forcefully removed **{member}**'s AFK status.", ephemeral=True, mention_author=False)
                return await self.end_afk(payload=context.message, user=member)

            await self.start_afk(payload=context.message, user=member, reason=reason)
            return await context.reply(content=f"Forcefully added **{member}**'s AFK status.", ephemeral=True, mention_author=False)
        
        if member.bot:
            return await context.reply(content="I'm afraid you can not do that to bots.", ephemeral=True, mention_author=False)
        if member.id == context.guild.owner.id:
            return await context.reply(content="I'm afraid you can not do that to the guild owner.", ephemeral=True, mention_author=False)
        if member.id == context.author.id:
            return await context.reply(content=f"Why would you force AFK yourself? Please use `{context.prefix}afk`.", ephemeral=True, mention_author=False)
        if member.top_role >= context.author.top_role:
            return await context.reply(content="I'm afraid you can not do that due to role hierarchy.", ephemeral=True, mention_author=False)

        if await self.config.member(member).afk():
            await self.end_afk(payload=context.message, user=member)
            return await context.send(f"Forcefully removed **{member}**'s AFK status.")

        await self.start_afk(payload=context.message, user=context.author, reason=reason)
        await context.send(f"Forcefully added **{member}**'s AFK status.")
    
    @afkset.command(name="nick")
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    async def afkset_nick(
        self,
        context: commands.Context,
        state: bool
    ):
        """
        Toggle whether to change the users nick with `[AFK] {user_display_name}` or not.
        
        This defaults to `True`.
        """
        await self.config.guild(context.guild).nick.set(state)
        status = "will now" if state else "will not"
        await context.send(f"I {status} edit the users nick whenever they go AFK.")
    
    @afkset.command(name="reset")
    async def afkset_reset(self, context: commands.Context):
        """
        Reset your AFK settings to default.
        """
        confirmation_msg = "Are you sure you want to reset your AFK settings?"
        confirm_action = "Successfully resetted your AFK settings."
        view = Confirmation(timeout=30)
        await view.start(context=context, confirmation_msg=confirmation_msg, confirm_action=confirm_action)
        
        await view.wait()
        
        if view.value == "yes":
            await self.config.member(context.author).clear()
    
    @afkset.command(name="resetcog")
    @commands.is_owner()
    async def afkset_resetcog(self, context: commands.Context):
        """
        Reset the AFK cogs configuration. (Bot owners only.)
        """
        confirmation_msg = "Are you sure you want to reset the AFK cogs whole configuration?"
        confirm_action = "Successfully resetted the AFK cogs configuration."
        view = Confirmation(timeout=30)
        await view.start(context=context, confirmation_msg=confirmation_msg, confirm_action=confirm_action)
        
        await view.wait()
        
        if view.value == "yes":
            await self.config.clear_all()
            await self.config.clear_all_members()
    
    @afkset.command(name="showsettings", aliases=["ss"])
    async def afkset_showsettings(self, context: commands.Context):
        """
        See your AFK settings.
        
        Guild settings show up when you have manage_guild permission.
        """
        member_settings = await self.config.member(context.author).all()
        guild_settings = await self.config.guild(context.guild).all()
        da = f"{guild_settings['delete_after']} seconds." if guild_settings['delete_after'] != 0 else "Disabled."
        gset = f"`Nick change:` {guild_settings['nick']}\n`Delete after:` {da}"
        
        embed = discord.Embed(
            title=f"{context.author.name}'s AFK settings.",
            description=f"`Is afk:` {member_settings['afk']}\n`Is sticky:` {member_settings['sticky']}\n`Ping logging:` {member_settings['toggle_logs']}",
            colour=context.author.colour,
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        
        if await context.bot.is_owner(context.author) or context.author.guild_permissions.manage_guild:
            embed.add_field(name="Guild settings:", value=gset, inline=False)
        
        await context.send(embed=embed)
    
    @afkset.command(name="sticky")
    async def afkset_sticky(
        self,
        context: commands.Context,
        state: bool
    ):
        """
        Toggle whether to sticky your afk or not.
        
        This defaults to `False`.
        """
        await self.config.member(context.author).sticky.set(state)
        status = "will now" if state else "will not"
        await context.send(f"I {status} sticky your AFK.")
        
    @afkset.command(name="togglelogs", aliases=["tl"])
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