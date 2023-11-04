import discord
import logging
import noobutils as nu

from redbot.core.bot import commands, Config, Red
from redbot.core.utils import chat_formatting as cf, mod

from datetime import datetime, timedelta, timezone
from discord.ext import tasks
from typing import Literal

from .converters import AmountConverter

# member = {
#     str(member_id): {
#         "tier": int,
#         "donations": int,
#         "due_timestamp": int,
#         "grinder_since": int
#     }
# }


class GrinderLogger(commands.Cog):
    """
    Grinder Managing System.

    Manage grinders from your server.
    """

    def __init__(self, bot: Red, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.config = Config.get_conf(self, identifier=546466564, force_registration=True)
        default_guild = {
            "managers": [],
            "grinders": {},
            "channels": {
                "logging": None,
                "reminding": None,
                "notifying": None
            },
            "tiers": {
                "1": {},
                "2": {},
                "3": {},
                "4": {},
                "5": {}
            }
        }
        self.config.register_guild(**default_guild)

        self.log = logging.getLogger("red.NoobCogs.GrinderLogger")

    __version__ = "1.0.0"
    __author__ = ["NoobInDaHause"]
    __docs__ = "https://github.com/NoobInDaHause/NoobCogs/blob/red-3.5/grinderlogger/README.md"

    def format_help_for_context(self, context: commands.Context) -> str:
        """
        Thanks Sinbad and sravan!
        """
        plural = "s" if len(self.__author__) > 1 else ""
        return f"""{super().format_help_for_context(context)}

        Cog Version: **{self.__version__}**
        Cog Author{plural}: {cf.humanize_list([f'**{auth}**' for auth in self.__author__])}
        Cog Documentation: [[Click here]]({self.__docs__})"""

    async def red_delete_data_for_user(
        self,
        *,
        requester: Literal["discord_deleted_user", "owner", "user", "user_strict"],
        user_id: int,
    ):
        """
        This cog stores user ID for grinder logs.

        Users can remove their data at anytime.
        """
        for g in (await self.config.all_guilds()).keys():
            if guild := self.bot.get_guild(g):
                async with self.config.guild(guild).grinders() as grinders:
                    try:
                        del grinders[str(user_id)]
                    except KeyError:
                        continue

    async def cog_load(self):
        self.log.info("GrinderLogger due reminder task started.")
        self.due_reminder.start()

    async def cog_unload(self):
        self.log.info("GrinderLogger due reminder task cancelled.")
        await self.due_reminder.cancel()

    @tasks.loop(seconds=5)
    async def due_reminder(self):
        for g in (await self.config.all_guilds()).keys():
            if guild := self.bot.get_guild(g):
                async with self.config.guild(guild).grinders() as grinders:
                    for k, v in grinders.items():
                        pass

    @due_reminder.before_loop
    async def due_reminder_before_loop(self):
        await self.bot.wait_until_red_ready()

    @staticmethod
    def is_a_grinder_manager():
        async def check_if_is_a_grinder_manager_or_higher(context: commands.Context):
            cog: "GrinderLogger" = context.bot.get_cog("GrinderLogger")

            if not context.guild:
                return False

            managers = await cog.config.guild(context.guild).managers()

            if await mod.is_mod_or_superior(context.bot, context.author):
                return True
            if any(role_id in context.author._roles for role_id in managers):
                return True
            return False
        return commands.check(check_if_is_a_grinder_manager_or_higher)

    @commands.group(name="grinderlogger", aliases=["grlog"])
    @commands.bot_has_permissions(embed_links=True)
    @commands.guild_only()
    async def grinderlogger(self, context: commands.Context):
        """
        GrinderLogger base commands.
        """
        pass

    @grinderlogger.command(name="promote")
    @is_a_grinder_manager()
    async def grinderlogger_promote(
        self,
        context: commands.Context,
        member: discord.Member,
        tier: Literal["1", "2", "3", "4", "5"]
    ):
        """
        Promote a member.
        """

    @commands.group(name="grinderloggerset", aliases=["grlogset"])
    @commands.admin_or_permissions(manage_guild=True)
    @commands.bot_has_permissions(embed_links=True)
    @commands.guild_only()
    async def grinderloggerset(self, context: commands.Context):
        """
        GrinderLogger settings commands.
        """
        pass

    @grinderlogger.command(name="add")
    async def grinderlogger_add(
        self,
        context: commands.Context,
        member: discord.Member,
        tier: Literal["1", "2", "3", "4", "5"]
    ):
        """
        Add a member.
        """

    @grinderloggerset.command(name="definetier", aliases=["dt"])
    async def grinderloggerset_definetier(
        self,
        context: commands.Context,
        tier: Literal["1", "2", "3", "4", "5"],
        role: discord.Role,
        amount: AmountConverter
    ):
        """
        Define a tier with a role and amount.
        """
        async with self.config.guild(context.guild).tiers() as tiers:
            tiers[tier] = {str(amount): role.id}
        await context.send(
            content=f"Set Tier {tier} with the role {role.mention} and {cf.humanize_number(amount)}/day."
        )

    @grinderloggerset.command(name="removetier", aliases=["rt"])
    async def grinderloggerset_removetier(
        self,
        context: commands.Context,
        tier: Literal["1", "2", "3", "4", "5"]
    ):
        """
        Remove a tier.
        """
        async with self.config.guild(context.guild).tiers() as tiers:
            tiers[tier] = {}
        await context.send(content="That tier has been cleared.")

    @grinderloggerset.command(name="manager")
    async def grinderloggerset_manager(
        self,
        context: commands.Context,
        add_or_remove_or_list: Literal["add", "remove", "list"],
        *roles: nu.NoobFuzzyRole
    ):
        """
        Add, remove, or check the list of grinder managers.
        """
        if add_or_remove_or_list == "list":
            ...

        if not roles:
            return await context.send_help()

        success = []
        failed = []
        async with self.config.guild(context.guild).managers() as managers:
            for role in roles:
                if (
                    add_or_remove_or_list == "add" and role.id in managers
                ) or (
                    add_or_remove_or_list == "remove" and role.id not in managers
                ):
                    failed.append(role)
                    continue
                if add_or_remove_or_list == "add":
                    managers.append(role.id)
                else:
                    managers.remove(role.id)
                success.append(role)

        _type = "was added to" if add_or_remove_or_list == "add" else "was removed from"
        _type2 = "add to" if add_or_remove_or_list == "add" else "remove from"
        if success:
            await context.send(
                content=f"Roles {cf.humanize_list([role.mention for role in success])} {_type} the list "
                "of grinder managers."
            )
        if failed:
            await context.send(
                content=f"Roles {cf.humanize_list([role.mention for role in failed])} failed to {_type2} "
                "the list of grinder managers."
            )

    @grinderloggerset.group(name="channel", aliases=["chan"])
    async def grinderloggerset_channel(self, context: commands.Context):
        """
        Channel related commands idk.
        """
        pass

    @grinderloggerset_channel.command(name="logchannel", aliases=["logchan"])
    async def grinderloggerset_channel_logchannel(
        self, context: commands.Context, channel: discord.TextChannel = None
    ):
        """
        Set the grinder logging channel.
        """
        if not channel:
            await self.config.guild(context.guild).channel.logging.set(None)
            return await context.send(content="The grinder logging channel has been cleared.")
        await self.config.guild(context.guild).channel.logging.set(channel.id)
        await context.send(content=f"Set {channel.mention} as the grinder logging channel.")

    @grinderloggerset_channel.command(name="reminderchannel", aliases=["rmchan"])
    async def grinderloggerset_channel_reminderchannel(
        self,
        context: commands.Context,
        channel: discord.TextChannel = None
    ):
        """
        Set the due grinders reminder channel.
        """
        if not channel:
            await self.config.guild(context.guild).channel.reminding.set(None)
            return await context.send(content="The due grinders reminder channel has been cleared.")
        await self.config.guild(context.guild).channel.reminding.set(channel.id)
        await context.send(content=f"Set {channel.mention} as the due grinders reminder channel.")

    @grinderloggerset_channel.command(name="notificationchannel", aliases=["notifchan"])
    async def grinderloggerset_channel_notificationchannel(
        self,
        context: commands.Context,
        channel: discord.TextChannel = None
    ):
        """
        Set the due grinders notifying channel.
        """
        if not channel:
            await self.config.guild(context.guild).channel.notifying.set(None)
            return await context.send(content="The due grinders notification channel has been cleared.")
        await self.config.guild(context.guild).channel.notifying.set(channel.id)
        await context.send(content=f"Set {channel.mention} as the due grinders notification channel.")

    @grinderloggerset.command(name="showsettings", aliases=["ss"])
    async def grinderloggerset_showsettings(self, context: commands.Context):
        """
        Show GrinderLogger settings.
        """
        managers = await self.config.guild(context.guild).managers()
        channels = await self.config.guild(context.guild).channels()
        tiers = await self.config.guild(context.guild).tiers()
        logchan = f'<#{channels["logging"]}>' if channels["logging"] else "None"
        notifychan = f'<#{channels["notifying"]}>' if channels["notifying"] else "None"
        rmchan = f'<#{channels["reminding"]}>' if channels["reminding"] else "None"
        t1 = [
            f"`Tier 1` - Role: {f'<@&{v}>' if v else 'None'}, Amount: {cf.humanize_number(int(k)) if k else 'None'}"
            for k, v in tiers["1"].items()
        ]
        t2 = [
            f"`Tier 2` - Role: {f'<@&{v}>' if v else 'None'}, Amount: {cf.humanize_number(int(k)) if k else 'None'}"
            for k, v in tiers["2"].items()
        ]
        t3 = [
            f"`Tier 3` - Role: {f'<@&{v}>' if v else 'None'}, Amount: {cf.humanize_number(int(k)) if k else 'None'}"
            for k, v in tiers["3"].items()
        ]
        t4 = [
            f"`Tier 4` - Role: {f'<@&{v}>' if v else 'None'}, Amount: {cf.humanize_number(int(k)) if k else 'None'}"
            for k, v in tiers["4"].items()
        ]
        t5 = [
            f"`Tier 5` - Role: {f'<@&{v}>' if v else 'None'}, Amount: {cf.humanize_number(int(k)) if k else 'None'}"
            for k, v in tiers["5"].items()
        ]
        c = t1 + t2 + t3 + t4 + t5

        embed = discord.Embed(
            title=f"GrinderLogger settings for [{context.guild.name}]",
            colour=await context.embed_colour(),
            timestamp=datetime.now(timezone.utc)
        )
        embed.add_field(
            name="Managers:",
            value=cf.humanize_list([f"<@&{i}>" for i in managers]),
            inline=False
        )
        embed.add_field(
            name="Channels:",
            value=f"` - ` Log Channel: {logchan}\n"
            f"` - ` Due Notifications Channel: {notifychan}\n"
            f"` - ` Due Reminder Channel: {rmchan}\n",
            inline=False
        )
        embed.add_field(
            name="Tiers:",
            value="\n".join(c),
            inline=False
        )
        await context.send(embed=embed)