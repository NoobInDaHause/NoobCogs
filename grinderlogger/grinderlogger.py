import contextlib
import datetime as dt
import discord
import logging
import noobutils as nu
import time

from redbot.core.bot import commands, Config, Red
from redbot.core.utils import chat_formatting as cf, mod

from discord.ext import tasks
from typing import Any, Dict, List, Literal, TYPE_CHECKING, Union

from .converters import AmountConverter

if TYPE_CHECKING:
    from donationlogger.donationlogger import DonationLogger


class GrinderLogger(commands.Cog):
    """
    GrinderLogger system.

    Manage grinders from your server.
    """

    def __init__(self, bot: Red, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot

        self.config = Config.get_conf(
            self, identifier=1234567890, force_registration=True
        )
        default_guild = {
            "managers": [],
            "grinders": {},
            "channels": {
                "logging": None,
                "notifying": None,
                "history": None,
            },
            "tiers": {"1": {}, "2": {}, "3": {}, "4": {}, "5": {}},
            "dm_status": True,
            "bank": None,
        }
        default_member = {
            "donations": 0,
            "times_as_grinder": 0,
            "last_time_as_grinder": None,
        }
        self.config.register_guild(**default_guild)
        self.config.register_member(**default_member)
        self.config.init_custom(group_identifier="Grinders", identifier_count=1)
        self.log = logging.getLogger("red.NoobCogs.GrinderLogger")
        self.init_done = False
        self.data: Dict[str, Dict[str, Dict[str, Any]]] = {}

    __version__ = "1.0.0"
    __author__ = ["NoobInDaHause"]
    __docs__ = (
        "https://github.com/NoobInDaHause/NoobCogs/blob/red-3.5/grinderlogger/README.md"
    )

    def format_help_for_context(self, context: commands.Context) -> str:
        plural = "s" if len(self.__author__) > 1 else ""
        return (
            f"{super().format_help_for_context(context)}\n\n"
            f"Cog Version: **{self.__version__}**\n"
            f"Cog Author{plural}: {cf.humanize_list([f'**{auth}**' for auth in self.__author__])}\n"
            f"Cog Documentation: [[Click here]]({self.__docs__})\n"
            f"Utils Version: **{nu.__version__}**"
        )

    async def red_delete_data_for_user(
        self,
        *,
        requester: Literal["discord_deleted_user", "owner", "user", "user_strict"],
        user_id: int,
    ):
        """
        This cog stores user ID for grinder logs. Users can remove their data at anytime.
        """
        for guild_id, grinder_data in self.data.copy().items():
            if grinder_data:
                for member_id in grinder_data.keys():
                    if user_id == int(member_id):
                        if self.data.get(guild_id, {}).get(member_id):
                            self.data[guild_id].pop(member_id)
                        await self.config.member_from_ids(
                            int(guild_id), int(member_id)
                        ).clear()

        await self.back_to_config()

    async def cog_load(self):
        self.bot.add_dev_env_value("grinderlogger", lambda _: self)
        if self.init_done:
            return

        if data := (await self.config.custom("Grinders").all()).copy():
            before_time = time.perf_counter()
            self.data = data
            after_time = time.perf_counter()
            self.log.info(
                f"GrinderLogger data initialized in {round(after_time - before_time, 3)}s."
            )

        self.init_done = True
        self.due_reminder_loop.start()
        self.save_data_to_config.start()
        self.log.info("Due reminder loop task and Save data to config task started.")

    async def cog_unload(self):
        self.bot.remove_dev_env_value("grinderlogger")
        self.init_done = False
        self.due_reminder_loop.cancel()
        self.save_data_to_config.cancel()
        await self.back_to_config()
        self.log.info("Due reminder loop task and Save data to config task cancelled.")

    async def back_to_config(self):
        old_data = (await self.config.custom("Grinders").all()).copy()
        old_data.update(self.data)
        await self.config.custom("Grinders").set(old_data)

    def add_to_data(self, guild_id: str, member_id: str, member_data: dict):
        self.data.setdefault(guild_id, {})
        self.data[guild_id].update({member_id: member_data})

    def remove_from_data(self, guild_id: str, member_id: str):
        with contextlib.suppress(KeyError):
            self.data[guild_id].pop(member_id)

    async def add_or_remove_grinder_roles(
        self, _type: str, member: discord.Member, roles: list, reason: str
    ) -> List[discord.Role]:
        action = member.add_roles if _type == "add" else member.remove_roles
        hybrid_roles = [
            role
            for x in roles
            if (role := member.guild.get_role(x))
            and (role in member.roles) == (_type == "remove")
        ]
        await action(*hybrid_roles, reason=reason)
        return hybrid_roles

    async def dm_grinder(
        self,
        member: discord.Member,
        amount: str,
        role_list: List[discord.Role],
        tier: str,
        _type: str,
        reason: str = None,
    ):
        if _type == "added":
            desc = (
                f"- Congratulations! You have been accepted as a grinder in **{member.guild.name}**.\n\n"
                f"__**Details:**__\n`{'Tier':<15}`: **{tier}**\n`{'Amount per day':<15}`: "
                f"{cf.humanize_number(amount)}/day\n`{'Recieved Roles':<15}`: "
                f"{cf.humanize_list([f'`@{role.name}`' for role in role_list]) if role_list else '`None`'}\n"
            )
            if reason:
                desc += f"`{'Reason':<15}`: {reason}\n"
            embed = (
                discord.Embed(
                    title="You are now a grinder!",
                    colour=discord.Colour.green(),
                    timestamp=dt.datetime.now(dt.timezone.utc),
                    description=desc,
                )
                .set_thumbnail(url=nu.is_have_avatar(member.guild))
                .set_footer(
                    text=member.guild.name, icon_url=nu.is_have_avatar(member.guild)
                )
            )
        else:
            _desc = (
                f"You have been removed from the grinders in **{member.guild.name}**.\n\n"
                f"__**Details:**__\n`{'Tier':<15}`: {tier}\n`{'Removed Roles':<15}`: "
                f"{cf.humanize_list([f'`@{role.name}`' for role in role_list]) if role_list else '`None`'}\n"
            )
            if reason:
                _desc += f"`{'Reason':<15}`: {reason}\n"
            embed = (
                discord.Embed(
                    title="You are no longer a grinder!",
                    colour=discord.Colour.red(),
                    timestamp=dt.datetime.now(dt.timezone.utc),
                    description=_desc,
                )
                .set_thumbnail(url=nu.is_have_avatar(member.guild))
                .set_footer(
                    text=member.guild.name, icon_url=nu.is_have_avatar(member.guild)
                )
            )
        with contextlib.suppress(
            (discord.errors.Forbidden, discord.errors.HTTPException)
        ):
            await member.send(embed=embed)

    async def remind_member(self, guild: discord.Guild, member_id: str):
        tiers = await self.config.guild(guild).tiers()
        managers = await self.config.guild(guild).managers()
        channels = await self.config.guild(guild).channels()
        member = guild.get_member(int(member_id))
        member_data = self.data[str(guild.id)][str(member.id)]
        member_data["last_due"] = member_data["due_timestamp"]
        member_data["due_timestamp"] = None
        await self.back_to_config()
        tier = member_data.get("tier")
        man_roles: List[discord.Role] = []
        for rid in managers:
            if role := guild.get_role(rid):
                man_roles.append(role)
        try:
            at = f"**{tier}** ({cf.humanize_number(tiers[tier]['amount'])}/day)"
        except KeyError:
            at = "It seems this tier is not defined please report this to the admins."
        ada = round(dt.datetime.now(dt.timezone.utc).timestamp())
        ad = f"<t:{ada}:R> (<t:{ada}:D>)"

        dms_off = []
        try:
            grindembed = discord.Embed(
                description=(
                    "# 🔔 Grinder Payment Reminder 🔔\n"
                    "- Just a friendly reminder that today is the **due date** for your grinder payment.\n"
                    "- Please ensure your payment is made promptly to maintain your grinder status in "
                    f"**{guild.name}**.\n\n__**Details**__\n- `{'Tier':<4}`: {at}\n"
                    f"- `{'Date':<4}`: {ad}\n\n"
                    "⚠️ `Note`: Feel free to pay early!"
                ),
                timestamp=dt.datetime.now(dt.timezone.utc),
                colour=member.colour,
            )
            grindembed.set_thumbnail(url=nu.is_have_avatar(guild))
            grindembed.set_footer(text=guild.name, icon_url=nu.is_have_avatar(guild))
            await member.send(embed=grindembed)
        except (discord.errors.Forbidden, discord.errors.HTTPException):
            dms_off.append(True)
        if not channels["notifying"]:
            return
        notifchan = self.bot.get_channel(channels["notifying"])
        with contextlib.suppress(
            (discord.errors.Forbidden, discord.errors.HTTPException)
        ):
            warn = (
                "⚠️ Warning: I could not DM this member they might have DM's closed."
                if dms_off
                else ""
            )
            adminembed = discord.Embed(
                colour=member.colour,
                description=(
                    "# 🔔 Grinder Manager Reminder 🔔\nHey **Grinder Managers.**\n\n"
                    f"Notifying you that: {member.mention} (`{member.id}`) is due for payment.\n"
                    "- Please verify their payment status, **update** the grinder log, "
                    "and ensure their status remains intact.\n\n__**Payment Details**__\n"
                    f"- `{'Member':<6}`: {member.mention}\n- `{'Tier':<6}`: {at}\n"
                    f"- `{'Date':<6}`: {ad}\n\nThanks for your attention!\n{warn}"
                ),
                timestamp=dt.datetime.now(dt.timezone.utc),
            )
            adminembed.set_footer(text=guild.name, icon_url=nu.is_have_avatar(guild))
            adminembed.set_thumbnail(url=nu.is_have_avatar(member))
            for role in man_roles:
                with contextlib.suppress(Exception):
                    await role.edit(mentionable=True)
            with contextlib.suppress(Exception):
                await notifchan.send(
                    content=cf.humanize_list([ro.mention for ro in man_roles]),
                    embed=adminembed,
                    allowed_mentions=discord.AllowedMentions(roles=True),
                )
            for r in man_roles:
                with contextlib.suppress(Exception):
                    await r.edit(mentionable=False)

    async def log_grinder_history(
        self,
        context: commands.Context,
        member: discord.Member,
        tier: str,
        amount: int,
        _type: str,
        sec: int = None,
        reason: str = None,
    ):
        desc = (
            "- A new Grinder has joined the ranks, reaching a new tier. Welcome Aboard!"
            if _type == "added"
            else "- Farewell to a Grinder. They've been removed from the roster. Wishing them all the best!"
        )
        gfor = (
            f"\n- `{'Grinder For':<11}`: **{cf.humanize_timedelta(seconds=sec)}**"
            if _type == "removed" and sec
            else ""
        )
        res = f"\n- `{'Reason':<11}`: {reason}" if reason else ""
        chan = await self.config.guild(context.guild).channels.history()
        if not chan:
            return
        hchan = self.bot.get_channel(chan)
        emo = "🗑️" if _type == "removed" else "📥"
        embed = discord.Embed(
            title=f"**__GRINDER {_type.upper()}__**",
            description=f"{desc}\n\n**__Details:__**\n"
            f"- `{'Member':<11}`: {member.mention} (`{member.id}`)\n- `{'Tier':<11}`: "
            f"**{tier}** ({cf.humanize_number(amount)}/day)\n- `{'Date':<11}`: "
            f"<t:{round(dt.datetime.now(dt.timezone.utc).timestamp())}:F> {emo}{gfor}{res}",
            colour=member.colour,
            timestamp=dt.datetime.now(dt.timezone.utc),
        )
        embed.set_thumbnail(url=nu.is_have_avatar(member))
        embed.set_footer(
            text=f"Authorized by: {context.author.name} ({context.author.id})",
            icon_url=nu.is_have_avatar(context.author),
        )
        embed.set_author(
            name=f"{member.name} ({member.id})", icon_url=nu.is_have_avatar(member)
        )
        try:
            await hchan.send(embed=embed)
        except Exception:
            await context.send(
                content="Grinder History Log Channel not found, report this to the admins.",
                embed=embed,
            )

    async def log_grinder_promotion_or_demotion(
        self,
        context: commands.Context,
        _type: str,
        member: discord.Member,
        before_tier: str,
        after_tier: str,
        amount: int,
        reason: str = None,
    ):
        chan = await self.config.guild(context.guild).channels.history()
        if not chan:
            return
        hchan = context.guild.get_channel(chan)
        dat = dt.datetime.now(dt.timezone.utc)
        res = f"- `{'Reason':<9}`: {reason}" if reason else ""
        if _type == "promote":
            title = "__GRINDER PROMOTION__"
            description = (
                "- A grinder has **leveled up**! They've been **upgraded** to a higher tier. "
                f"Congratulations!\n\n__**Details:**__\n- `{'Member':<9}`: {member.mention} (`{member.id}`)"
                f"\n- `{'From Tier':<9}`: **{before_tier}**\n- `{'To Tier':<9}`: **{after_tier}** "
                f"({cf.humanize_number(amount)}/day) ⬆️\n- `{'Date':<9}`: <t:{round(dat.timestamp())}:F>\n"
                f"{res}"
            )
        else:
            title = "__GRINDER DEMOTION__"
            description = (
                "- Oops! A grinder has been **demoted** to a __lower tier__. "
                f"Let's support them on their journey back up.\n\n__**Details:**__\n- `{'Member':<9}`: "
                f"{member.mention} (`{member.id}`)\n- `{'From Tier':<9}`: **{before_tier}**\n"
                f"- `{'To Tier':<9}`: **{after_tier}** ({cf.humanize_number(amount)}/day) ⬇️\n"
                f"- `{'Date':<9}`: <t:{round(dat.timestamp())}:F>\n{res}"
            )

        embed = discord.Embed(
            title=title, description=description, colour=member.colour, timestamp=dat
        )
        embed.set_thumbnail(url=nu.is_have_avatar(member))
        embed.set_footer(
            text=f"Authorized by: {context.author} ({context.author.id}) | {context.guild.name}",
            icon_url=nu.is_have_avatar(context.author),
        )
        embed.set_author(
            name=f"{member.name} ({member.id})", icon_url=nu.is_have_avatar(member)
        )
        try:
            await hchan.send(embed=embed)
        except Exception:
            await context.send(
                content="Grinder history channel not found please report this to the admins.",
                embed=embed,
            )

    async def dm_on_promote_or_demote(
        self,
        member: discord.Member,
        _type: str,
        roles: List[discord.Role],
        amount: int,
        before_tier: str,
        after_tier: str,
        reason: str = None,
    ):
        res = (
            f"- `{'Reason':<14}`: {reason}"
            if reason and _type == "promote"
            else f"- `{'Reason':<13}`: {reason}"
            if reason
            else ""
        )
        rs = cf.humanize_list([f"`@{r.name}`" for r in roles]) if roles else "`None`"
        if _type == "promote":
            title = "Grinder Promotion"
            desc = (
                f"You have been promoted from the grinders in **{member.guild.name}**.\n\n__**Details:**__\n"
                f"- `{'From Tier':<14}` : **{before_tier}**\n- `{'To tier':<14}`: **{after_tier}** "
                f"({cf.humanize_number(amount)}/day) ⬆️\n- `{'Recieved Roles':<14}`: {rs}\n{res}"
            )
        else:
            title = "Grinder Demotion"
            desc = (
                f"You have been demoted from the grinders in **{member.guild.name}**.\n\n__**Details:**__\n"
                f"- `{'From Tier':<13}` : **{before_tier}**\n- `{'To tier':<13}`: **{after_tier}** "
                f"({cf.humanize_number(amount)}/day) ⬇️\n- `{'Removed Roles':<13}`: {rs}\n{res}"
            )
        embed = discord.Embed(
            title=title,
            description=desc,
            colour=member.colour,
            timestamp=dt.datetime.now(dt.timezone.utc),
        )
        embed.set_thumbnail(url=nu.is_have_avatar(member.guild))
        embed.set_footer(
            text=member.guild.name, icon_url=nu.is_have_avatar(member.guild)
        )
        with contextlib.suppress(
            discord.errors.HTTPException, discord.errors.Forbidden
        ):
            await member.send(embed=embed)

    async def send_to_log_channel(
        self,
        context: commands.Context,
        member: discord.Member,
        b_amount: int,
        a_amount: int,
        o_amount: int,
        _type: str,
        due_time: int = None,
    ):
        logchan = await self.config.guild(context.guild).channels.logging()
        if not logchan:
            return
        lchan = self.bot.get_channel(logchan)
        tier = self.data[str(context.guild.id)][str(member.id)]["tier"]
        view = discord.ui.View().add_item(
            discord.ui.Button(label="Jump To Command", url=context.message.jump_url)
        )
        embed = discord.Embed(
            title=f"__Grinder Payment {_type.title()}__",
            description=f"{cf.humanize_number(o_amount)} was "
            f"{'added to' if _type == 'added' else 'removed from'} **{member.name}**'s grinder balance.",
            timestamp=dt.datetime.now(dt.timezone.utc),
            colour=await context.embed_colour(),
        )
        embed.add_field(name="Tier:", value=tier, inline=True)
        embed.add_field(
            name="Before Balance:", value=cf.humanize_number(b_amount), inline=True
        )
        embed.add_field(
            name="After Balance:", value=cf.humanize_number(a_amount), inline=True
        )
        if due_time:
            embed.add_field(
                name="Due Date:",
                value=f"<t:{due_time}:R> (<t:{due_time}:F>)",
                inline=True,
            )
        embed.set_author(
            name=f"{member.name} ({member.id})", icon_url=nu.is_have_avatar(member)
        )
        embed.set_footer(
            text=f"Authorized by: {context.author} ({context.author.id})",
            icon_url=nu.is_have_avatar(context.author),
        )
        if not logchan:
            return await context.send(embed=embed, view=view)
        try:
            await lchan.send(embed=embed, view=view)
        except Exception:
            await context.send(
                content="⚠️ Log channel not found.", embed=embed, view=view
            )

    async def donoadd(
        self,
        context: commands.Context,
        member: discord.Member,
        amount: int,
        due_duration: dt.timedelta = None,
    ):
        """
        Add donation and set due duration on a grinder.
        """
        bank = await self.config.guild(context.guild).bank()

        if member.bot:
            return await context.send(content="Bots are not allowed.")
        if guild := self.data.get(str(context.guild.id), {}):
            if member_data := guild.get(str(member.id)):
                if due_duration:
                    dat = (
                        dt.datetime.fromtimestamp(
                            member_data["due_timestamp"], dt.timezone.utc
                        )
                        if member_data["due_timestamp"]
                        else dt.datetime.now(dt.timezone.utc)
                    )
                    stamp = dat + due_duration
                    member_data["due_timestamp"] = round(stamp.timestamp())
                before = await self.config.member(member).donations()
                after = before + amount
                await self.config.member(member).donations.set(after)
                member_data["last_payed"] = round(
                    dt.datetime.now(dt.timezone.utc).timestamp()
                )
                await self.back_to_config()
                await context.tick()
                await self.send_to_log_channel(
                    context,
                    member,
                    before,
                    after,
                    amount,
                    "added",
                    member_data["due_timestamp"],
                )
                if bank and context.bot.get_cog("DonationLogger"):
                    if cmd := self.bot.get_command("donationlogger add"):
                        await context.invoke(
                            cmd, bank_name=bank, amount=amount, member=member
                        )
            else:
                await context.send(content="This member is not a grinder.")
        else:
            await context.send(content="This guild has no grinders.")

    async def donoremove(
        self,
        context: commands.Context,
        member: discord.Member,
        amount: int,
        time_to_remove: dt.timedelta = None,
    ):  # sourcery skip: low-code-quality
        """
        Remove donation from a grinder.
        """
        if member.bot:
            return await context.send(content="Bots are not allowed.")
        bank = await self.config.guild(context.guild).bank()
        if guild := self.data.get(str(context.guild.id), {}):
            if member_data := guild.get(str(member.id)):
                before = await self.config.member(member).donations()
                if before == 0:
                    return await context.send(
                        content="This grinder has 0 donation amount."
                    )
                if time_to_remove and member_data["due_timestamp"]:
                    due_date = dt.datetime.fromtimestamp(
                        member_data.get("due_timestamp"), dt.timezone.utc
                    )
                    new_date = due_date - time_to_remove
                    if new_date < dt.datetime.now(dt.timezone.utc):
                        member_data["due_timestamp"] = None
                        await context.send(
                            content="You have removed more time than the set due duration for this member so "
                            "the due duration is removed."
                        )
                    else:
                        member_data["due_timestamp"] = round(new_date.timestamp())
                after = max(before - amount, 0)
                await self.config.member(member).donations.set(after)
                await self.back_to_config()
                await context.tick()
                await self.send_to_log_channel(
                    context,
                    member,
                    before,
                    after,
                    amount,
                    "removed",
                )
                if bank and context.bot.get_cog("DonationLogger"):
                    if cmd := self.bot.get_command("donationlogger remove"):
                        await context.invoke(
                            cmd, bank_name=bank, amount=amount, member=member
                        )
            else:
                await context.send(content="This member is not a grinder.")
        else:
            await context.send(content="This guild has no grinders.")

    @tasks.loop(seconds=5)
    async def due_reminder_loop(self):
        if not self.init_done:
            return
        for guild_id, grinder_data in self.data.copy().items():
            if guild := self.bot.get_guild(int(guild_id)):
                for member_id in grinder_data.keys():
                    if member_data := self.data.get(guild_id, {}).get(member_id):
                        if member_data["due_timestamp"] and (
                            dt.datetime.fromtimestamp(
                                member_data["due_timestamp"], dt.timezone.utc
                            )
                            < dt.datetime.now(dt.timezone.utc)
                        ):
                            try:
                                await self.remind_member(guild, member_id)
                            except Exception as e:
                                self.log.exception(str(e), exc_info=e)

    @tasks.loop(minutes=5)
    async def save_data_to_config(self):
        if not self.init_done:
            return
        await self.back_to_config()

    @due_reminder_loop.before_loop
    @save_data_to_config.before_loop
    async def tasks_before_loop(self):
        await self.bot.wait_until_red_ready()

    @staticmethod
    def is_a_grinder_manager():
        async def check_if_is_a_grinder_manager_or_higher(context: commands.Context):
            if not context.guild:
                return False

            cog: "GrinderLogger" = context.bot.get_cog("GrinderLogger")

            return (
                context.author.guild_permissions.manage_guild
                or context.author.guild_permissions.administrator
                or await mod.is_mod_or_superior(context.bot, context.author)
                or any(
                    role_id in context.author._roles
                    for role_id in await cog.config.guild(context.guild).managers()
                )
                or False
            )

        return commands.check(check_if_is_a_grinder_manager_or_higher)

    @commands.Cog.listener("on_guild_remove")
    async def on_guild_remove(self, guild: discord.Guild):
        if guild_data := self.data.get(str(guild.id), {}):
            for member_id in guild_data.copy().keys():
                if mem_data := self.data.get(str(guild.id), {}).get(member_id):
                    mem_data["last_due"] = mem_data.get("due_timestamp")
                    mem_data["due_timestamp"] = None

    @commands.Cog.listener("on_guild_join")
    async def on_guild_join(self, guild: discord.Guild):
        if guild_data := self.data.get(str(guild.id), {}):
            for member_id in guild_data.copy().keys():
                if mem_data := self.data.get(str(guild.id), {}).get(member_id):
                    if (
                        mem_data["last_due"]
                        and (
                            dt.datetime.fromtimestamp(
                                mem_data["last_due"], dt.timezone.utc
                            )
                            > dt.datetime.now(dt.timezone.utc)
                        )
                    ):
                        mem_data["due_timestamp"] = mem_data["last_due"]

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
        tier: Literal["1", "2", "3", "4", "5"],
        *,
        reason: str = None,
    ):  # sourcery skip: low-code-quality
        """
        Promote a grinder to a higher tier/level. 

        Grinder will get a DM depending on the status of `[p]grlogset dmstatus`.
        """
        if member.bot:
            return await context.send(content="Bots are not allowed.")
        if reason and len(reason) > 2000:
            return await context.send(
                content="Limit your damn reason to 2k characters."
            )
        tiers = await self.config.guild(context.guild).tiers()

        if not tiers[tier]:
            return await context.send(
                content="You haven't set any amount and role for this tier yet."
            )

        if guild := self.data.get(str(context.guild.id), {}):
            if member_data := guild.get(str(member.id)):
                if member_data["tier"] == tier:
                    return await context.send(
                        content="That grinder is already that tier."
                    )
                if int(tier) < int(member_data["tier"]):
                    return await context.send(
                        content="That tier is lower than this grinders tier did you mean to demote them"
                        f" instead?\n`{context.prefix}grinderlogger demote`"
                    )
                before = member_data.get("tier")
                member_data["tier"] = tier
                after = member_data.get("tier")
                await self.back_to_config()
                audit_reason = mod.get_audit_reason(
                    context.author, reason=f"Member promoted to a Tier {tier} grinder."
                )
                roles = []
                for tier_number in range(int(tier)):
                    tn = str(tier_number + 1)
                    if tiers[tn]:
                        roles.append(tiers[tn]["role"])
                added_roles = await self.add_or_remove_grinder_roles(
                    "add", member, roles, audit_reason
                )
                await self.log_grinder_promotion_or_demotion(
                    context,
                    "promote",
                    member,
                    before,
                    after,
                    tiers[tier]["amount"],
                    reason,
                )
                if await self.config.guild(context.guild).dm_status():
                    await self.dm_on_promote_or_demote(
                        member,
                        "promote",
                        added_roles,
                        tiers[tier]["amount"],
                        before,
                        after,
                        reason,
                    )
                await context.send(
                    content=f"Promoted **{member.name}** to a Tier {tier} grinder."
                )
            else:
                await context.send(content="This member is not a grinder.")
        else:
            await context.send(content="This guild has no grinders.")

    @grinderlogger.command(name="demote")
    @is_a_grinder_manager()
    async def grinderlogger_demote(
        self,
        context: commands.Context,
        member: discord.Member,
        tier: Literal["1", "2", "3", "4", "5"],
        *,
        reason: str = None,
    ):  # sourcery skip: low-code-quality
        """
        Demote a grinder to a lower tier/level.

        Grinder will be DM-ed upon the status of `[p]grlogset dmstatus`.
        """
        if member.bot:
            return await context.send(content="Bots are not allowed.")
        if reason and len(reason) > 2000:
            return await context.send(
                content="Limit your damn reason to 2k characters."
            )
        tiers = await self.config.guild(context.guild).tiers()

        if not tiers[tier]:
            return await context.send(
                content="You haven't set any amount and role for this tier yet."
            )

        if guild := self.data.get(str(context.guild.id), {}):
            if member_data := guild.get(str(member.id)):
                if member_data["tier"] == tier:
                    return await context.send(
                        content="That grinder is already that tier."
                    )
                if int(tier) > int(member_data["tier"]):
                    return await context.send(
                        content="That tier is higher than this grinders tier did you mean to promote them"
                        f" instead?\n`{context.prefix}grinderlogger promote`"
                    )
                before = member_data.get("tier")
                member_data["tier"] = tier
                after = member_data.get("tier")
                await self.back_to_config()
                audit_reason = mod.get_audit_reason(
                    context.author, reason=f"Member demoted to a Tier {tier} grinder."
                )
                roles = []
                for tier_number in range(int(tier)):
                    tn = str(tier_number + 1)
                    if tiers[tn]:
                        roles.append(tiers[tn]["role"])
                removed_roles = await self.add_or_remove_grinder_roles(
                    "remove", member, roles, audit_reason
                )
                await self.log_grinder_promotion_or_demotion(
                    context,
                    "demote",
                    member,
                    before,
                    after,
                    tiers[tier]["amount"],
                    reason,
                )
                if await self.config.guild(context.guild).dm_status():
                    await self.dm_on_promote_or_demote(
                        member,
                        "demote",
                        removed_roles,
                        tiers[tier]["amount"],
                        before,
                        after,
                        reason,
                    )
                await context.send(
                    content=f"Demoted **{member.name}** to a Tier {tier} grinder."
                )
            else:
                await context.send(content="This member is not a grinder.")
        else:
            await context.send(content="This guild has no grinders.")

    @grinderlogger.command(name="stats")
    async def grinderlogger_stats(
        self, context: commands.Context, member: discord.Member = None
    ):  # sourcery skip: low-code-quality
        """
        Check your or someone else's grinder stats.
        """
        member = member or context.author
        if member.bot:
            return await context.send(content="Bots are not allowed.")

        donations = await self.config.member(member).donations()
        times = await self.config.member(member).times_as_grinder()

        guild_data = self.data.get(str(context.guild.id), {})
        if member_data := guild_data.get(str(member.id)):
            tier, due_stamp, grinder_since, last_pay = (
                member_data.get("tier"),
                (member_data.get("due_timestamp") or member_data.get("last_due")),
                member_data.get("grinder_since"),
                member_data.get("last_payed"),
            )
            description = (
                f"`{'Tier':<13}`: {tier}\n`{'Donations':<13}`: {cf.humanize_number(donations)}\n"
                f"`{'Times Joined':<13}`: {f'{times} times' if times > 1 else f'{times} time'}\n"
                f"`{'Last Payed':<13}`: {f'<t:{last_pay}:R> (<t:{last_pay}:f>)' if last_pay else 'None'}\n"
                f"`{'Due Date':<13}`: {f'<t:{due_stamp}:R> (<t:{due_stamp}:f>)' if due_stamp else 'None'}\n"
                f"`{'Grinder Since':<13}`: <t:{grinder_since}:R> (<t:{grinder_since}:f>)"
            )
        else:
            last_time = await self.config.member(member).last_time_as_grinder()
            description = (
                f"`{'Donations':<12}`: {donations}\n"
                f"`{'Times Joined':<12}`: {f'{times} times' if times > 1 else f'{times} time'}\n"
                f"`{'Grinder Left':<12}`: <t:{last_time}:R> (<t:{last_time}:f>)"
                if last_time
                else None
            )

        if description:
            embed = discord.Embed(
                title="Grinder Stats",
                colour=member.colour,
                timestamp=dt.datetime.now(dt.timezone.utc),
                description=description,
            )
            embed.set_footer(
                text=context.guild.name, icon_url=nu.is_have_avatar(context.guild)
            )
            embed.set_thumbnail(url=nu.is_have_avatar(member))
            embed.set_author(
                name=f"{member.name} ({member.id})", icon_url=nu.is_have_avatar(member)
            )
            await context.send(embed=embed)
        else:
            await context.send(
                content="This member is not a grinder or a former grinder."
            )

    @grinderlogger.command(name="dono")
    @is_a_grinder_manager()
    async def grinderlogger_dono(
        self,
        context: commands.Context,
        _type: Literal["add", "remove"],
        member: discord.Member,
        amount: AmountConverter,
        time: commands.TimedeltaConverter = None,
    ):
        """
        Add or remove grinder donation amount and time.

        Mention the time till which the payment is made upto.
        Bot will remind the **user** and **grinder manager** in that exact time.
        `[p]grlogset dmstatus` Enables grinders to be reminded in DMs
        """
        if _type == "add":
            await self.donoadd(context, member, amount, time)
        else:
            await self.donoremove(context, member, amount, time)

    @grinderlogger.command(name="leaderboard", aliases=["lb"])
    @commands.bot_has_permissions(embed_links=True)
    async def grinderlogger_leaderboard(self, context: commands.Context):
        """
        Show the grinderlogger leaderboard.
        """
        all_members = self.data.get(str(context.guild.id), {})
        if not all_members:
            return await context.send(content="This guild has no grinders.")

        all_m = {}
        for mid, md in all_members.copy().items():
            member = context.guild.get_member(int(mid))
            donations = await self.config.member_from_ids(
                context.guild.id, int(mid)
            ).donations()
            all_m[member or mid] = {
                "donations": donations,
                "due": md["due_timestamp"] or md["last_due"],
                "tier": md["tier"],
            }

        all_mem = []
        for index, (mem, mem_dono) in enumerate(
            sorted(all_m.items(), key=lambda x: x[1]["donations"], reverse=True), 1
        ):
            if isinstance(mem, discord.Member):
                msg = (
                    f"` {index}. ` {mem.mention} ({mem.id}):\n"
                    f"- Tier: **{mem_dono['tier']}**\n"
                    f"- Donations: {cf.humanize_number(mem_dono['donations'])}"
                )
            else:
                msg = (
                    f"` {index}. ` Member not found in guild ({mem}):\n"
                    f"- Tier: **{mem_dono['tier']}**\n"
                    f"- Donations: {cf.humanize_number(mem_dono['donations'])}"
                )
            if mem_dono["due"]:
                msg += f"\n- Due: <t:{mem_dono['due']}:R>"
            all_mem.append(msg)

        pagified = await nu.pagify_this(
            "\n".join(all_mem),
            "\n",
            embed_title=f"GrinderLogger Leaderboard fpr [{context.guild.name}]",
            embed_timestamp=dt.datetime.now(dt.timezone.utc),
            embed_colour=context.bot._color,
        )
        await nu.NoobPaginator(pagified).start(context)

    @commands.group(name="grinderloggerset", aliases=["grlogset"])
    @commands.admin_or_permissions(manage_guild=True)
    @commands.bot_has_permissions(embed_links=True)
    @commands.guild_only()
    async def grinderloggerset(self, context: commands.Context):
        """
        GrinderLogger settings commands.
        """
        pass

    @grinderloggerset.command(name="donationloggersupport", aliases=["dlsupport"])
    async def grinderloggerset_donationloggersupport(
        self, context: commands.Context, bank_name: str = None
    ):
        """
        Add support for DonationLogger.
        """
        cog: "DonationLogger" = context.bot.get_cog("DonationLogger")
        if not cog:
            return await context.send(
                content="DonationLogger is not loaded/installed report this to the bot owner."
            )
        if not await cog.config.guild(context.guild).setup():
            return await context.send(
                content="It seems DonationLogger has not been setup in this guild yet."
            )
        banks = await cog.config.guild(context.guild).banks()
        if bank_name:
            try:
                banks[bank_name]
            except KeyError:
                return await context.send(content="That bank does not seem to exist.")
            await self.config.guild(context.guild).bank.set(bank_name)
            await context.send(
                content="Grinder donations will now get auto add/remove from donationlogger.\n"
                f"Donations will be added from bank **{bank_name.title()}**."
            )
        else:
            await self.config.guild(context.guild).bank.set(None)
            await context.send(
                content="The bank to auto add/remove from has been cleared."
            )

    @grinderloggerset.command(name="dmstatus")
    async def grinderloggerset_dmstatus(self, context: commands.Context):
        """
        Toggle whether to DM the member for their grinder promotion/demotion.
        """
        current = await self.config.guild(context.guild).dm_status()
        await self.config.guild(context.guild).dm_status.set(not current)
        state = "will no longer" if current else "will now"
        await context.send(content=f"I {state} DM grinders their promotion/demotion.")

    @grinderloggerset.command(name="addmember")
    @commands.bot_has_permissions(manage_roles=True)
    async def grinderloggerset_addmember(
        self,
        context: commands.Context,
        member: discord.Member,
        tier: Literal["1", "2", "3", "4", "5"],
        *,
        reason: str = None,
    ):
        """
        Add a member as a grinder.

        User will be DM-ed upon acceptance/rejection.
        """
        if reason and len(reason) > 2000:
            return await context.send(
                content="Limit your damn reason to 2k characters."
            )

        tiers = await self.config.guild(context.guild).tiers()

        if not tiers[tier]:
            return await context.send(
                content="You haven't set any amount and role for this tier yet."
            )
        if member.bot:
            return await context.send(content="Bots are not allowed.")

        if self.data.get(str(context.guild.id), {}).get(str(member.id)):
            return await context.send(content="This member is already a grinder.")

        member_data = {
            "tier": tier,
            "due_timestamp": None,
            "grinder_since": round(dt.datetime.now(dt.timezone.utc).timestamp()),
            "last_payed": None,
            "last_due": None,
        }

        times = await self.config.member(member).times_as_grinder()
        await self.config.member(member).times_as_grinder.set(times + 1)
        self.add_to_data(str(context.guild.id), str(member.id), member_data)

        await self.back_to_config()

        audit_reason = mod.get_audit_reason(
            context.author, reason=f"Member is a Tier {tier} grinder."
        )
        roles = []
        for tier_number in range(int(tier)):
            tn = str(tier_number + 1)
            if tiers[tn]:
                roles.append(tiers[tn]["role"])
        added_roles = await self.add_or_remove_grinder_roles(
            "add", member, roles, audit_reason
        )
        await context.send(content=f"Added **{member.name}** as a Tier {tier} grinder.")
        await self.dm_grinder(
            member, tiers[tier]["amount"], added_roles, tier, "added", reason
        )
        await self.log_grinder_history(
            context, member, tier, tiers[tier]["amount"], "added", None, reason
        )

    @grinderloggerset.command(name="removemember")
    @commands.bot_has_permissions(manage_roles=True)
    async def grinderloggerset_removemember(
        self, context: commands.Context, member: discord.Member, *, reason: str = None
    ):
        """
        Remove a grinder.

        User will be DM-ed upon acceptance/rejection.
        """
        if member.bot:
            return await context.send(content="Bots are not allowed.")
        if reason and len(reason) > 2000:
            return await context.send(
                content="Limit your damn reason to 2k characters."
            )
        tiers = await self.config.guild(context.guild).tiers()
        if member_data := self.data.get(str(context.guild.id), {}).get(str(member.id)):
            tier = member_data["tier"]
            await self.log_grinder_history(
                context,
                member,
                tier,
                tiers[tier]["amount"],
                "removed",
                dt.datetime.now(dt.timezone.utc).timestamp()
                - member_data["grinder_since"],
                reason,
            )
            self.remove_from_data(str(context.guild.id), str(member.id))
            await self.back_to_config()
            await self.config.member(member).last_time_as_grinder.set(
                round(dt.datetime.now(dt.timezone.utc).timestamp())
            )
            audit_reason = mod.get_audit_reason(
                context.author, reason=f"Member is no longer a Tier {tier} grinder."
            )
            roles = []
            for tier_number in range(int(tier)):
                tn = str(tier_number + 1)
                if tiers[tn]:
                    roles.append(tiers[tn]["role"])
            removed_roles = await self.add_or_remove_grinder_roles(
                "remove", member, roles, audit_reason
            )
            await self.dm_grinder(
                member, tiers[tier]["amount"], removed_roles, tier, "removed", reason
            )
            await context.send(content=f"Removed **{member.name}** from grinders.")
        else:
            await context.send(content="This member is not a grinder.")

    @grinderloggerset.command(name="manager")
    @commands.bot_has_permissions(manage_roles=True)
    async def grinderloggerset_manager(
        self,
        context: commands.Context,
        add_or_remove_or_list: Literal["add", "remove", "list"],
        *roles: nu.NoobFuzzyRole,
    ):
        """
        Add, remove, or check the list of grinder managers.

        Multiple roles are accepted, spaced by a space. 
        Role ID/name/@mention all are accepted.

        Examples: 
        `[p]grlogset manager list Shows the list of manager roles`
        `[p]grlogset manager add @moderator @admin `
        `[p]grlogset manager remove staff_role_ID`
        """
        if add_or_remove_or_list == "list":
            managers = await self.config.guild(context.guild).managers()
            embed = discord.Embed(
                title=f"Grinder Manager Roles for [{context.guild.name}]",
                timestamp=dt.datetime.now(dt.timezone.utc),
                colour=await context.embed_colour(),
                description=cf.humanize_list([f"<@&{r}>" for r in managers]),
            )
            return await context.send(embed=embed)

        if not roles:
            return await context.send_help()

        success = []
        failed = []
        async with self.config.guild(context.guild).managers() as managers:
            for role in roles:
                if (add_or_remove_or_list == "add" and role.id in managers) or (
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

    @grinderloggerset.command(name="channel", aliases=["chan"])
    async def grinderloggerset_channel(
        self,
        context: commands.Context,
        _type: Literal["logs", "notify", "history"],
        channel: Union[discord.TextChannel, discord.Thread] = None,
    ):
        """
        Add or remove grinder related channels idk.

        Channel, threads are accepted. 
        Channel mention/ID all are valid.
        Run the command again mentioning a different channel to override the previous set-channel.

        Examples:
        `[p]grlogset channel logs #grinder-logs`
        `[p]grlogset channel notify #notified`
        """
        _config = self.config.guild(context.guild).channels

        if _type == "logs":
            await _config.logging.set(channel.id if channel else None)
            await context.send(
                content=f"Set {channel.mention} as the grinder logging channel."
                if channel
                else "The grinders logging channel has been cleared."
            )
        elif _type == "notify":
            await _config.notifying.set(channel.id if channel else None)
            await context.send(
                content=f"Set {channel.mention} as the grinder notification channel."
                if channel
                else "The due grinders notification channel has been cleared."
            )
        else:
            await _config.history.set(channel.id if channel else None)
            await context.send(
                content=f"Set {channel.mention} as the grinder history channel."
                if channel
                else "The grinders history channel has been cleared."
            )

    @grinderloggerset.command(name="tier", aliases=["t"])
    async def grinderloggerset_tier(
        self,
        context: commands.Context,
        _type: Literal["add", "remove"],
        tier: Literal["1", "2", "3", "4", "5"],
        role: nu.NoobFuzzyRole = None,
        amount: AmountConverter = None,
    ):
        """
        Add or remove tier amount roles.

        Add or remove tier amount roles.
        Tier goes from 1 to 5, where 1 = Lowest Tier and 5 = Highest Tier.
        Define all your grinder tier one-by-one.
        Amount acronyms are accepted - k/m/b/t

        Example:
        `[p]grlogset tier add 1 @coolrole 2m`: 2m = 2 million/day
        `[p]grlogset tier add 2 another_role 5m`: 5m = 5 million/day
        `[p]grlogset tier remove 2`
        """
        if _type == "add":
            if not role or not amount:
                return await context.send_help()
            async with self.config.guild(context.guild).tiers() as tiers:
                if tiers[tier]:
                    return await context.send(
                        content="That tier already has an amount roles setup."
                    )
                tiers[tier] = {"amount": amount, "role": role.id}
            await context.send(
                content=f"Set Tier {tier} with the role {role.mention} and {cf.humanize_number(amount)}/day."
            )
        else:
            async with self.config.guild(context.guild).tiers() as tiers:
                if not tiers[tier]:
                    return await context.send(
                        content="That tier does not have any amount roles setup."
                    )
                tiers[tier] = {}
            await context.send(content="That tier has been cleared.")

    @grinderloggerset.command(name="resetguild")
    async def grinderloggerset_resetguild(self, context: commands.Context):
        """
        Reset the guild GrinderLogger system.
        """
        act = "Done. This guild data has been reset."
        conf = "Are you sure you want to reset the data of this guild?"
        view = nu.NoobConfirmation()
        await view.start(context, act, content=conf)
        await view.wait()
        if view.value:
            with contextlib.suppress(KeyError):
                self.data.pop(str(context.guild.id))
            old_data = (await self.config.custom("Grinders").all()).copy()
            with contextlib.suppress(KeyError):
                old_data.pop(str(context.guild.id))
            await self.config.custom("Grinders").set(old_data)
            await self.config.guild(context.guild).clear()
            await self.config.clear_all_members(context.guild)

    @grinderloggerset.command(name="resetcog")
    @commands.is_owner()
    async def grinderloggerset_resetcog(self, context: commands.Context):
        """
        Reset cog config.
        """
        act = "Done. The config has been cleared."
        conf = "Are you sure you want to clear the config?"
        view = nu.NoobConfirmation()
        await view.start(context, act, content=conf)
        await view.wait()
        if view.value:
            self.init_done = False
            self.save_data_to_config.restart()
            self.due_reminder_loop.restart()
            self.data.clear()
            await self.back_to_config()
            await self.config.clear_all_guilds()
            await self.config.clear_all_custom("Grinders")
            await self.config.clear_all_members()
            await self.config.clear_all()
            self.init_done = True

    @grinderloggerset.command(name="showsettings", aliases=["ss"])
    async def grinderloggerset_showsettings(self, context: commands.Context):
        """
        Show GrinderLogger settings.
        """
        managers = await self.config.guild(context.guild).managers()
        channels = await self.config.guild(context.guild).channels()
        tiers = await self.config.guild(context.guild).tiers()
        bank = await self.config.guild(context.guild).bank()
        dm_status = await self.config.guild(context.guild).dm_status()
        logchan = f'<#{channels["logging"]}>' if channels["logging"] else "**None**"
        notifychan = (
            f'<#{channels["notifying"]}>' if channels["notifying"] else "**None**"
        )
        hischan = f'<#{channels["history"]}>' if channels["history"] else "**None**"
        desc = []
        for tier_number in range(1, 6):
            tier = tiers[str(tier_number)]
            role = f"<@&{tier['role']}>" if tier else "**None**"
            amount = cf.humanize_number(tier["amount"]) if tier else "**None**"
            desc.append(f"`Tier {tier_number}` - Role: {role}, Amount: {amount}")

        embed = discord.Embed(
            title=f"GrinderLogger settings for [{context.guild.name}]",
            colour=await context.embed_colour(),
            timestamp=dt.datetime.now(dt.timezone.utc),
        )
        embed.add_field(
            name="Managers:",
            value=cf.humanize_list([f"<@&{i}>" for i in managers])
            if managers
            else "**None**",
            inline=False,
        )
        embed.add_field(name="DM Status:", value=dm_status, inline=False)
        embed.add_field(name="Bank name to auto add/remove:", value=bank, inline=False)
        embed.add_field(
            name="Channels:",
            value=f"` - ` Donation Log Channel: {logchan}\n"
            f"` - ` Due Notifications Channel: {notifychan}\n"
            f"` - ` Grinder History Channel: {hischan}\n",
            inline=False,
        )
        embed.add_field(name="Tiers:", value="\n".join(desc), inline=False)
        await context.send(embed=embed)
