import discord
import noobutils as nu
import logging

from redbot.core.bot import app_commands, commands, Config, Red
from redbot.core.utils import chat_formatting as cf, mod

from typing import Dict, Literal, List, Optional

from .checks import is_a_dono_manager_or_higher, is_setup_done
from .converters import AmountConverter, BankConverter, DLEmojiConverter
from .exceptions import MoreThanThreeRoles
from .hybrids import HYBRIDS
from .utilities import verify_amount_roles


class DonationLogger(commands.Cog):
    """
    Donation Logger System.

    Log any donations from your server.
    """

    def __init__(self, bot: Red, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.bot = bot

        self.config = Config.get_conf(
            self, identifier=657668242451927167510, force_registration=True
        )
        default_guild = {
            "managers": [],
            "banks": {},
            "log_channel": None,
            "auto_role": False,
            "setup": False,
        }
        self.config.register_guild(**default_guild)
        self.log = logging.getLogger("red.NoobCogs.DonationLogger")
        self.setupcache = []

    __version__ = "1.2.4"
    __author__ = ["NoobInDaHause"]
    __docs__ = "https://github.com/NoobInDaHause/NoobCogs/blob/red-3.5/donationlogger/README.md"

    def format_help_for_context(self, context: commands.Context) -> str:
        plural = "s" if len(self.__author__) > 1 else ""
        return (
            f"{super().format_help_for_context(context)}\n\n"
            f"Cog Version: **{self.__version__}**\n"
            f"Cog Author{plural}: {cf.humanize_list([f'**{auth}**' for auth in self.__author__])}\n"
            f"Cog Documentation: [[Click here]]({self.__docs__})"
        )

    async def red_delete_data_for_user(
        self,
        *,
        requester: Literal["discord_deleted_user", "owner", "user", "user_strict"],
        user_id: int,
    ):
        """
        This cog stores user ID for donation logs.

        Users can remove their data at anytime.
        """
        for g in (await self.config.all_guilds()).keys():
            async with self.config.guild_from_id(g).banks() as banks:
                for bank in banks.values():
                    try:
                        del bank["donators"][str(user_id)]
                    except KeyError:
                        continue

    async def get_dc_from_bank(
        self, context: commands.Context, bank_name: str
    ) -> List[discord.Embed]:
        banks = await self.config.guild(context.guild).banks()
        bank_info = banks.get(bank_name.lower())

        if not bank_info or bank_info["hidden"]:
            return []

        sorted_donators = sorted(
            bank_info["donators"].items(), key=lambda x: x[1], reverse=True
        )

        final = ""
        for index, (k, v) in enumerate(sorted_donators, 1):
            member = context.guild.get_member(int(k))
            e = "➡️ " if member == context.author else ""
            final += (
                f"{e}{index}. {member.mention} (`{member.id}`): **{cf.humanize_number(v)}**\n"
                if member
                else f"{index}. [Member not found in guild] (`{k}`): **{cf.humanize_number(v)}**\n"
            )

        return await nu.pagify_this(
            final,
            "\n",
            "".join([f"{context.guild.name}", " | Page ({index}/{pages})"]),
            embed_title=f"All of the donors for [{bank_name.title()}]",
            embed_colour=await context.embed_colour(),
            footer_icon=nu.is_have_avatar(context.guild),
        )

    async def get_all_bank_member_dono(
        self, guild: discord.Guild, member: discord.Member
    ) -> discord.Embed:
        final: Dict[str, str] = {}
        final_overall = []
        async with self.config.guild(guild).banks() as banks:
            for k, v in banks.items():
                if v["hidden"]:
                    continue
                donations = v["donators"].setdefault(str(member.id), 0)
                final[k] = f"{v['emoji']} {cf.humanize_number(donations)}"
                final_overall.append(donations)

        overall = sum(final_overall)
        embed = discord.Embed(
            description=f"Overall combined bank donation amount: {cf.humanize_number(overall)}",
            timestamp=discord.utils.utcnow(),
            colour=member.colour,
        )
        embed.set_author(
            name=f"{member} ({member.id})", icon_url=nu.is_have_avatar(member)
        )
        embed.set_footer(
            text=f"{guild.name} admires your donations!",
            icon_url=nu.is_have_avatar(guild),
        )
        if final:
            for k, v in final.items():
                embed.add_field(name=k.title(), value=v, inline=True)
        else:
            embed.description = (
                "There are no banks registered yet, or banks are hidden."
            )
        return embed

    async def update_dono_roles(
        self,
        context: commands.Context,
        d_type: str,
        donated_amount: int,
        member: discord.Member,
        roles: Dict[str, List[int]],
    ) -> List[discord.Role]:
        if not await self.config.guild(context.guild).auto_role():
            return []
        audit_reason = mod.get_audit_reason(
            author=context.author,
            reason=(
                "Automatically added donation roles on member after reaching a donation milestone."
                if d_type == "add"
                else (
                    "Automatically removed donation roles on member after deduction of "
                    "donation amount and no longer in said donation milestone."
                )
            ),
        )
        action = member.add_roles if d_type == "add" else member.remove_roles
        roles_to_modify: List[discord.Role] = []
        for k, v in roles.items():
            for r in v:
                role = context.guild.get_role(r)
                if role and (
                    (
                        d_type == "add"
                        and donated_amount >= int(k)
                        and role not in member.roles
                    )
                    or (
                        d_type == "remove"
                        and donated_amount < int(k)
                        and role in member.roles
                    )
                ):
                    roles_to_modify.append(role)

        if not roles_to_modify:
            return []

        await action(*roles_to_modify, reason=audit_reason)
        return roles_to_modify

    async def send_to_log_channel(
        self,
        context: commands.Context,
        d_type: str,
        bank_name: str,
        emoji: str,
        amount: int,
        previous: int,
        updated: int,
        member: discord.Member,
        roles: str = None,
    ):
        logchan = await self.config.guild(context.guild).log_channel()
        if not logchan:
            return

        channel = context.guild.get_channel(logchan)

        actions = {
            "add": ("was added to", "Roles Added:", "**__Donation Added!__**"),
            "remove": (
                "was removed from",
                "Roles Removed:",
                "**__Donation Removed!__**",
            ),
            "default": (
                "was set as",
                "Roles Added and/or Removed:",
                "**__Donation Set!__**",
            ),
        }

        ar, ra, title = actions.get(d_type, actions["default"])

        embed = discord.Embed(
            title=title,
            description=(
                f"{emoji} {cf.humanize_number(amount)} {ar} **{member.display_name}**'s donation balance."
            ),
            colour=await context.embed_colour(),
            timestamp=discord.utils.utcnow(),
        )

        embed.set_footer(
            text=f"Authorized by: {context.author} ({context.author.id})",
            icon_url=nu.is_have_avatar(context.author),
        )

        embed.set_author(
            name=f"{member.name} ({member.id})", icon_url=nu.is_have_avatar(member)
        )

        embed.add_field(name="Bank:", value=bank_name.title(), inline=True)
        embed.add_field(
            name="Previous balance:",
            value=f"{emoji} {cf.humanize_number(previous)}",
            inline=True,
        )
        embed.add_field(
            name="Updated balance:",
            value=f"{emoji} {cf.humanize_number(updated)}",
            inline=True,
        )

        if roles:
            embed.add_field(name=ra, value=roles, inline=False)
        elif not await self.config.guild(context.guild).auto_role():
            embed.add_field(
                name=ra,
                value=f"> Autorole is currently disabled. `{context.prefix}dlset autorole`",
                inline=False,
            )

        view = discord.ui.View().add_item(
            discord.ui.Button(label="Jump To Command", url=context.message.jump_url)
        )

        try:
            await channel.send(embed=embed, view=view)
        except Exception:
            await context.send(
                content="⚠️ Warning: `Log channel not found or I do not have permission to "
                "send message in the log channel please report this to the admins.`",
                embed=embed,
                view=view,
            )

    @commands.group(name="donationlogger", aliases=["d", "dl", "dono", "donolog"])
    @commands.bot_has_permissions(embed_links=True)
    @commands.guild_only()
    async def donationlogger(self, context: commands.Context):
        """
        DonationLogger base commands.
        """
        pass

    @donationlogger.command(name="resetcog")
    @commands.is_owner()
    async def donationlogger_resetcog(self, context: commands.Context):
        """
        Reset the cog's whole config.
        """
        act = "The cog's config has been cleared."
        conf = "Are you sure you want to clear the whole cog's config?"
        view = nu.NoobConfirmation()
        await view.start(context, act, content=conf)

        await view.wait()

        if view.value:
            await self.config.clear_all_guilds()

    @donationlogger.command(name="setup")
    @commands.admin_or_permissions(manage_guild=True)
    async def donationlogger_setup(self, context: commands.Context):
        """
        Setup the donation logger system in this guild.
        """
        await HYBRIDS.hybrid_setup(self, context)

    @donationlogger.command(name="resetmember")
    @is_setup_done()
    @is_a_dono_manager_or_higher()
    async def donationlogger_resetmember(
        self,
        context: commands.Context,
        bank_name: Optional[BankConverter] = None,
        member: discord.Member = None,
    ):
        """
        Reset a member's specific bank or all bank donations.
        """
        if not member:
            member = context.author
        if member.bot:
            return await context.send(content="Bots are not allowed.")
        await HYBRIDS.hybrid_resetmember(self, context, member, bank_name)

    @donationlogger.command(name="balance", aliases=["bal", "c", "check"])
    @is_setup_done()
    async def donationlogger_check(
        self,
        context: commands.Context,
        bank_name: Optional[BankConverter] = None,
        member: discord.Member = None,
    ):
        """
        Check your or some one else's donation balance.
        """
        if not member:
            member = context.author
        if member.bot:
            return await context.send(
                content="Bots are prohibited from donations. (For obvious reasons)"
            )

        await HYBRIDS.hybrid_balance(self, context, member, bank_name)

    @donationlogger.command(name="donationcheck", aliases=["dc"])
    @is_setup_done()
    async def donationlogger_donationcheck(
        self,
        context: commands.Context,
        bank_name: BankConverter,
        mla: Literal["more", "less", "all"],
        amount: AmountConverter = None,
    ):
        """
        See who has donated more or less or all from a bank.
        """
        await HYBRIDS.hybrid_donationcheck(self, context, bank_name, mla, amount)

    @donationlogger.command(name="leaderboard", aliases=["lb"])
    @is_setup_done()
    async def donationlogger_leaderboard(
        self, context: commands.Context, bank_name: BankConverter, top: int = 10
    ):
        """
        See who has donated the most from a bank.
        """
        if top > 25 or top < 1:
            return await context.send(content="Top number must be between 1-25.")
        await HYBRIDS.hybrid_leaderboard(self, context, bank_name, top)

    @donationlogger.command(name="add", aliases=["+", "a"])
    @is_setup_done()
    @is_a_dono_manager_or_higher()
    async def donationlogger_add(
        self,
        context: commands.Context,
        bank_name: BankConverter,
        amount: AmountConverter,
        member: discord.Member = None,
    ):
        """
        Add bank donation amount to a member or yourself.
        """
        if not member:
            member = context.author
        if member.bot:
            return await context.send(
                content="Bots are prohibited from donations. (For obvious reasons)"
            )

        await HYBRIDS.hybrid_add(self, context, bank_name, amount, member)

    @donationlogger.command(name="remove", aliases=["-", "r"])
    @is_setup_done()
    @is_a_dono_manager_or_higher()
    async def donationlogger_remove(
        self,
        context: commands.Context,
        bank_name: BankConverter,
        amount: AmountConverter,
        member: discord.Member = None,
    ):
        """
        Remove bank donation amount to a member or yourself.
        """
        if not member:
            member = context.author
        if member.bot:
            return await context.send(
                content="Bots are prohibited from donations. (For obvious reasons)"
            )

        await HYBRIDS.hybrid_remove(self, context, bank_name, amount, member)

    @donationlogger.command(name="set")
    @is_setup_done()
    @is_a_dono_manager_or_higher()
    async def donationlogger_set(
        self,
        context: commands.Context,
        bank_name: BankConverter,
        amount: AmountConverter,
        member: discord.Member = None,
    ):
        """
        Set someone's donation balance to the amount of your choice.
        """
        if not member:
            member = context.author
        if member.bot:
            return await context.send(
                content="Bots are prohibited from donations. (For obvious reasons)"
            )

        await HYBRIDS.hybrid_set(self, context, bank_name, amount, member)

    @commands.group(
        name="donationloggerset", aliases=["dlset", "donologset", "donoset"]
    )
    @commands.admin_or_permissions(manage_guild=True)
    @commands.bot_has_permissions(embed_links=True)
    @is_setup_done()
    async def donationloggerset(self, context: commands.Context):
        """
        DonationLogger settings commands.
        """
        pass

    @donationloggerset.group(name="bank")
    async def donationloggerset_bank(self, context: commands.Context):
        """
        Bank settings commands.
        """
        pass

    @donationloggerset_bank.command(name="add")
    async def donationloggerset_bank_add(
        self,
        context: commands.Context,
        bank_name: str,
        emoji: DLEmojiConverter,
        hidden: bool = False,
    ):
        """
        Add a new bank.
        """
        async with self.config.guild(context.guild).banks() as banks:
            if len(banks) > 25:
                return await context.send(
                    content="You can only have a maximum of 25 banks per guild."
                )
            if bank_name in banks:
                return await context.send(content="This bank already exists.")
            banks |= {
                bank_name.lower(): {
                    "hidden": hidden,
                    "emoji": str(emoji),
                    "roles": {},
                    "donators": {},
                }
            }
        await context.send(
            content=f"Added {bank_name} with the emoji {str(emoji)} to the banks list."
        )

    @donationloggerset_bank.command(name="remove")
    async def donationloggerset_bank_remove(
        self, context: commands.Context, bank_name: BankConverter
    ):
        """
        Remove a bank.
        """

        async with self.config.guild(context.guild).banks() as banks:
            if len(list(banks.keys())) == 1:
                return await context.send(
                    content="This bank is the guild's only bank, you can not remove it."
                )
            del banks[bank_name.lower()]
        await context.send(content="That bank is deleted.")

    @donationloggerset_bank.command(name="list")
    async def donationloggerset_bank_list(self, context: commands.Context):
        """
        See the list of registered banks.
        """
        all_banks = await self.config.guild(context.guild).banks()
        banks = {k: v for k, v in all_banks.items() if not v["hidden"]}
        enumerated_banks = [
            f"{index}. {v['emoji']} {k.title()}"
            for index, (k, v) in enumerate(banks.items(), 1)
        ]
        embed = discord.Embed(
            title=f"List of registered banks for [{context.guild.name}]",
            description="\n".join(
                enumerated_banks
                or ["There are no registered banks yet, or banks are hidden."]
            ),
            timestamp=discord.utils.utcnow(),
            colour=await context.embed_colour(),
        )
        await context.send(embed=embed)

    @donationloggerset_bank.group(name="amountroles", aliases=["ar"])
    async def donationloggerset_bank_amountroles(self, context: commands.Context):
        """
        Bank Amount-Roles settings commands.
        """
        pass

    @donationloggerset_bank_amountroles.command(name="set", aliases=["add"])
    async def donationloggerset_bank_amountroles_set(
        self, context: commands.Context, bank_name: BankConverter, amountroles: str
    ):
        """
        Set roles milestone to an amount.

        Example: `10m:@role:@role,10k:(role_id),12.5e6:(role_name)`
        You can only set a maximum of 3 roles per amount.
        """
        _ar = amountroles.strip().split(",")
        try:
            arole = await verify_amount_roles(context, _ar)

            if not arole:
                return await context.send(
                    content="Those do not seem to be valid roles or invalid amount."
                )

            async with self.config.guild(context.guild).banks() as banks:
                banks[bank_name.lower()]["roles"] |= {
                    k: [r.id for r in v] for k, v in arole.items()
                }

            embed = discord.Embed(
                title="Amount roles has been set.",
                description="\n".join(
                    [
                        f"{cf.humanize_number(int(k))}: {cf.humanize_list([r.mention for r in v])}"
                        for k, v in arole.items()
                    ]
                ),
                colour=await context.embed_colour(),
                timestamp=discord.utils.utcnow(),
            )
            await context.send(embed=embed)
        except MoreThanThreeRoles:
            return await context.send(
                content="The maximum roles you can assign to an amount should be no more than 3."
            )

    @donationloggerset_bank_amountroles.command(name="remove")
    async def donationloggerset_bank_amountroles_add(
        self,
        context: commands.Context,
        bank_name: BankConverter,
        amount: AmountConverter,
    ):
        """
        Remove an amount from the roles milestone.
        """
        async with self.config.guild(context.guild).banks() as banks:
            try:
                del banks[bank_name.lower()]["roles"][str(amount)]
                await context.send(content="That amount has been removed.")
            except KeyError:
                await context.send(content="You haven't registered that amount yet.")

    @donationloggerset_bank_amountroles.command(name="list")
    async def donationloggerset_bank_amountroles_list(
        self, context: commands.Context, bank_name: BankConverter
    ):
        """
        See the list of amountroles on a bank.
        """
        banks = await self.config.guild(context.guild).banks()
        aroles = banks[bank_name.lower()]["roles"]
        sorted_aroles = dict(sorted(aroles.items(), key=lambda j: int(j[0])))
        aroles2 = [
            f"**{cf.humanize_number(int(k))}**: {cf.humanize_list([f'<@&{i}>' for i in v])}"
            for k, v in sorted_aroles.items()
            if aroles
        ]
        embed = discord.Embed(
            title=f"List of Amount-Roles for [{bank_name.title()}]",
            description="\n".join(aroles2 or ["This bank has no amountroles."]),
            timestamp=discord.utils.utcnow(),
            colour=await context.embed_colour(),
        )
        await context.send(embed=embed)

    @donationloggerset_bank.command(name="resetbank")
    async def donationloggerset_bank_resetbank(
        self,
        context: commands.Context,
        roles_or_donators: Literal["amountroles", "donators", "both"],
        bank_name: BankConverter,
    ):
        """
        Reset a banks donations or amountroles.
        """
        async with self.config.guild(context.guild).banks() as banks:
            if roles_or_donators == "amountroles":
                banks[bank_name.lower()]["roles"] = {}
            elif roles_or_donators == "donators":
                banks[bank_name.lower()]["donators"] = {}
            else:
                banks[bank_name.lower()]["roles"] = {}
                banks[bank_name.lower()]["donators"] = {}
        _type = (
            roles_or_donators
            if roles_or_donators == "amountroles"
            else roles_or_donators
            if roles_or_donators == "donators"
            else "both amountroles and donators"
        )
        await context.send(content=f"Bank **{bank_name}** {_type} has been reset.")

    @donationloggerset_bank.command(name="emoji")
    async def donationloggerset_bank_emoji(
        self,
        context: commands.Context,
        bank_name: BankConverter,
        emoji: DLEmojiConverter,
    ):
        """
        Change a bank's emoji.
        """
        async with self.config.guild(context.guild).banks() as banks:
            banks[bank_name.lower()]["emoji"] = str(emoji)
            await context.send(
                content=f"Successfully changed **{bank_name}**'s emoji to {str(emoji)}"
            )

    @donationloggerset_bank.command(name="hidden")
    async def donationloggerset_bank_hidden(
        self,
        context: commands.Context,
        hidden: Literal["hide", "unhide", "list"],
        bank_name: BankConverter = None,
    ):
        """
        Hide, UnHide or see the list of hidden banks.
        """
        if hidden in ["hide", "unhide"]:
            if not bank_name:
                return await context.send_help()
            async with self.config.guild(context.guild).banks() as banks:
                banks[bank_name.lower()]["hidden"] = hidden == "hide"
                status = "is now" if hidden == "hide" else "is no longer"
                await context.send(content=f"Bank **{bank_name}** {status} hidden.")
        else:
            all_banks = await self.config.guild(context.guild).banks()
            banks = {k: v for k, v in all_banks.items() if v["hidden"]}
            enumerated_banks = [
                f"{index}. {v['emoji']} {k.title()}"
                for index, (k, v) in enumerate(banks.items(), 1)
            ]
            embed = discord.Embed(
                title=f"List of all hidden banks in [{context.guild.name}]",
                description="\n".join(
                    enumerated_banks or ["There are no hidden banks."]
                ),
                timestamp=discord.utils.utcnow(),
                colour=await context.embed_colour(),
            )
            await context.send(embed=embed)

    @donationloggerset.command(name="manager")
    async def donationloggerset_manager(
        self,
        context: commands.Context,
        add_remove_list: Literal["add", "remove", "list"],
        *roles: nu.NoobFuzzyRole,
    ):
        """
        Add, Remove or check the list of managers.
        """
        if add_remove_list == "list":
            managers = await self.config.guild(context.guild).managers()
            embed = discord.Embed(
                title=f"List of DonationLogger managers for [{context.guild.name}]",
                description=cf.humanize_list([f"<@&{i}>" for i in managers]),
                timestamp=discord.utils.utcnow(),
                colour=await context.embed_colour(),
            )
            return await context.send(embed=embed)

        if not roles:
            return await context.send_help()

        if add_remove_list in ["add", "remove"]:
            success = []
            failed = []
            async with self.config.guild(context.guild).managers() as managers:
                for role in roles:
                    if (
                        add_remove_list == "add"
                        and role.id in managers
                        or add_remove_list != "add"
                        and role.id not in managers
                    ):
                        failed.append(role.mention)
                        continue
                    if add_remove_list == "add":
                        managers.append(role.id)
                    else:
                        managers.remove(role.id)
                    success.append(role.mention)
            _type = "added" if add_remove_list == "add" else "removed"
            _type2 = "to" if add_remove_list == "add" else "from"
            if success:
                await context.send(
                    content=f"Successfully {_type} {cf.humanize_list(success)} {_type2} the list of manager"
                    " roles."
                )
            if failed:
                await context.send(
                    content=f"Failed to {add_remove_list} {cf.humanize_list(failed)} {_type2} the list of "
                    "manager roles since they are already manager roles."
                )

    @donationloggerset.command(name="logchannel")
    async def donationloggerset_logchannel(
        self, context: commands.Context, channel: discord.TextChannel = None
    ):
        """
        Set or remove the log channel.
        """
        if not channel:
            await self.config.guild(context.guild).log_channel.clear()
            return await context.send(content="The log channel has been cleared.")
        await self.config.guild(context.guild).log_channel.set(channel.id)
        await context.send(content=f"Set {channel.mention} as the log channel.")

    @donationloggerset.command(name="resetguild")
    async def donationloggerset_resetguild(self, context: commands.Context):
        """
        Reset the guild's DonationLogger system.
        """
        act = "This guild's DonationLogger system has been reset."
        conf = "Are you sure you want to reset this guild's DonationLogger system?"
        view = nu.NoobConfirmation()
        await view.start(context, act, content=conf)
        await view.wait()
        if view.value:
            await self.config.guild(context.guild).clear()

    @donationloggerset.command(name="autorole")
    async def donationloggerset_autorole(self, context: commands.Context):
        """
        Enable or Disable automatic role additon or removal.
        """
        current = await self.config.guild(context.guild).auto_role()
        await self.config.guild(context.guild).auto_role.set(not current)
        status = "will no longer" if current else "will now"
        await context.send(content=f"I {status} automatically add or remove roles.")

    @donationloggerset.command(name="showsettings", aliases=["ss", "showallsettings"])
    async def donationloggerset_showsettings(self, context: commands.Context):
        """
        See all the current set settings for this guild's DonationLogger system.
        """
        managers = await self.config.guild(context.guild).managers()
        autorole = await self.config.guild(context.guild).auto_role()
        banks = await self.config.guild(context.guild).banks()
        log_channel = await self.config.guild(context.guild).log_channel()
        bank_list = [f"{k.title()}" for k in banks.keys()]
        banks_list_hidden = [f"{k.title()}" for k, v in banks.items() if v["hidden"]]
        embed = discord.Embed(
            title=f"Current DonationLogger settings for [{context.guild.name}]",
            colour=await context.embed_colour(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=nu.is_have_avatar(context.guild))
        embed.add_field(
            name="DonationLogger Managers:",
            value=cf.humanize_list([f"<@&{i}>" for i in managers]),
            inline=False,
        )
        embed.add_field(
            name="Automatically Add or Remove roles:", value=autorole, inline=False
        )
        embed.add_field(
            name="Log Channel:",
            value=f"<#{log_channel}>" if log_channel else "None",
            inline=False,
        )
        embed.add_field(
            name="Registered Banks:",
            value=cf.humanize_list(
                bank_list or ["There are no registered banks yet, or banks are hidden."]
            ),
            inline=False,
        )
        if banks_list_hidden:
            embed.add_field(
                name="Hidden Banks:",
                value=cf.humanize_list(banks_list_hidden),
                inline=False,
            )
        await context.send(embed=embed)

    # <------------------------------------- SLASH COMMANDS ---------------------------------------------->

    slash_donologger = app_commands.Group(
        name="donationlogger", description="DonationLogger base commands.", guild_only=True
    )

    @slash_donologger.command(
        name="setup", description="Setup the donation logger system in this guild."
    )
    async def slash_donationlogger(self, interaction: discord.Interaction[Red]):
        """_summary_

        Args:
            interaction (discord.Interaction[Red]): _description_
        """
        await HYBRIDS.hybrid_setup(self, interaction)

    @slash_donologger.command(
        name="resetmember",
        description="Reset a member's specific bank or all bank donations.",
    )
    @app_commands.describe(
        bank_name="The name of the registered bank.",
        member="The member that you want to reset donations. (leave blank to choose yourself)",
    )
    async def slash_donationlogger_resetmember(
        self,
        interaction: discord.Interaction[Red],
        bank_name: Optional[app_commands.Transform[str, BankConverter]],
        member: Optional[discord.Member],
    ):
        """_summary_

        Args:
            interaction (discord.Interaction[Red]): _description_
            bank_name (Optional[app_commands.Transform[str, BankConverter]]): _description_
            member (Optional[discord.Member]): _description_
        """
        if not member:
            member = interaction.user
        if member.bot:
            return await interaction.response.send_message(
                content="Bots are not allowed."
            )
        if isinstance(bank_name, list):
            if bank_name[1]:
                return await interaction.response.send_message(
                    content=bank_name[0], ephemeral=True
                )
            else:
                return await interaction.response.send_message(content=bank_name[0])
        await HYBRIDS.hybrid_resetmember(self, interaction, member, bank_name)

    @slash_donologger.command(
        name="balance", description="Check your or some one else's donation balance."
    )
    @app_commands.describe(
        bank_name="The name of the registered bank.",
        member="The member that you want to check donations. (leave blank to choose yourself)",
    )
    async def slash_donationlogger_balance(
        self,
        interaction: discord.Interaction[Red],
        bank_name: Optional[app_commands.Transform[str, BankConverter]],
        member: Optional[discord.Member],
    ):
        """_summary_

        Args:
            interaction (discord.Interaction[Red]): _description_
            bank_name (Optional[app_commands.Transform[str, BankConverter]]): _description_
            member (discord.Member, optional): _description_. Defaults to None.
        """
        if not member:
            member = interaction.user
        if member.bot:
            return await interaction.response.send_message(
                content="Bots are not allowed."
            )
        if isinstance(bank_name, list):
            if bank_name[1]:
                return await interaction.response.send_message(
                    content=bank_name[0], ephemeral=True
                )
            else:
                return await interaction.response.send_message(content=bank_name[0])
        await HYBRIDS.hybrid_balance(self, interaction, member, bank_name)

    @slash_donologger.command(
        name="donationcheck",
        description="See who has donated more or less or all from a bank.",
    )
    @app_commands.rename(mla="more_less_all")
    @app_commands.describe(
        bank_name="The name of the registered bank.",
        mla="Check More, Less or All donations from the bank.",
        amount="The amount to check. (leave blank if you will check all) (examples: 10k, 1e6, 6900)",
    )
    async def slash_donationlogger_donationcheck(
        self,
        interaction: discord.Interaction[Red],
        bank_name: app_commands.Transform[str, BankConverter],
        mla: Literal["More", "Less", "All"],
        amount: Optional[app_commands.Transform[str, AmountConverter]],
    ):
        """_summary_

        Args:
            interaction (discord.Interaction[Red]): _description_
            bank_name (app_commands.Transform[str, BankConverter]): _description_
            mla (Literal[&quot;More&quot;, &quot;Less&quot;, &quot;All&quot;]): _description_
            amount (Optional[app_commands.Transform[str, AmountConverter]]): _description_
        """
        if isinstance(bank_name, list):
            if bank_name[1]:
                return await interaction.response.send_message(
                    content=bank_name[0], ephemeral=True
                )
            else:
                return await interaction.response.send_message(content=bank_name[0])
        if isinstance(amount, list):
            if amount[1]:
                return await interaction.response.send_message(
                    content=amount[0], ephemeral=True
                )
            else:
                return await interaction.response.send_message(content=amount[0])
        if mla.lower() != "all" and not amount:
            return await interaction.response.send_message(
                content="You need to pass an amount if you choose to check more or less."
            )
        await HYBRIDS.hybrid_donationcheck(
            self, interaction, bank_name, mla.lower(), amount
        )

    @slash_donologger.command(
        name="leaderboard", description="See who has donated the most from a bank."
    )
    @app_commands.describe(
        bank_name="The name of the registered bank.",
        top="The top number. (min: 1, max: 25, default: 10)",
    )
    async def slash_donationlogger_leaderboard(
        self,
        interaction: discord.Interaction[Red],
        bank_name: app_commands.Transform[str, BankConverter],
        top: app_commands.Range[int, 1, 25] = 10,
    ):
        """_summary_

        Args:
            interaction (discord.Interaction[Red]): _description_
            bank_name (app_commands.Transform[str, BankConverter]): _description_
            top (app_commands.Range[int, 1, 25]): _description_
        """
        if isinstance(bank_name, list):
            if bank_name[1]:
                return await interaction.response.send_message(
                    content=bank_name[0], ephemeral=True
                )
            else:
                return await interaction.response.send_message(content=bank_name[0])
        await HYBRIDS.hybrid_leaderboard(self, interaction, bank_name, top)

    @slash_donologger.command(
        name="add", description="Add bank donation amount to a member or yourself."
    )
    @app_commands.describe(
        bank_name="The name of the registered bank.",
        amount="The amount that you want to add. (examples: 10k, 1e6, 6900)",
        member="The member that you want to add donations to.",
    )
    async def slash_donationlogger_add(
        self,
        interaction: discord.Interaction[Red],
        bank_name: app_commands.Transform[str, BankConverter],
        amount: app_commands.Transform[str, AmountConverter],
        member: Optional[discord.Member],
    ):
        """_summary_

        Args:
            interaction (discord.Interaction[Red]): _description_
            bank_name (app_commands.Transform[str, BankConverter]): _description_
            amount (app_commands.Transform[str, AmountConverter]): _description_
            member (Optional[discord.Member]): _description_
        """
        if not member:
            member = interaction.user
        if member.bot:
            return await interaction.response.send_message(
                content="Bots are prohibited from donations. (For obvious reasons)"
            )
        if isinstance(bank_name, list):
            if bank_name[1]:
                return await interaction.response.send_message(
                    content=bank_name[0], ephemeral=True
                )
            else:
                return await interaction.response.send_message(content=bank_name[0])
        if isinstance(amount, list):
            if amount[1]:
                return await interaction.response.send_message(
                    content=amount[0], ephemeral=True
                )
            else:
                return await interaction.response.send_message(content=amount[0])
        await HYBRIDS.hybrid_add(self, interaction, bank_name, amount, member)

    @slash_donologger.command(
        name="remove",
        description="Remove bank donation amount to a member or yourself.",
    )
    @app_commands.describe(
        bank_name="The name of the registered bank.",
        amount="The amount that you want to add. (examples: 10k, 1e6, 6900)",
        member="The member that you want to remove donations from.",
    )
    async def slash_donationlogger_remove(
        self,
        interaction: discord.Interaction[Red],
        bank_name: app_commands.Transform[str, BankConverter],
        amount: app_commands.Transform[str, AmountConverter],
        member: Optional[discord.Member],
    ):
        """_summary_

        Args:
            context (commands.Context): _description_
            bank_name (BankConverter): _description_
            amount (AmountConverter): _description_
            member (discord.Member, optional): _description_. Defaults to None.
        """
        if not member:
            member = interaction.user
        if member.bot:
            return await interaction.response.send_message(
                content="Bots are prohibited from donations. (For obvious reasons)"
            )
        if isinstance(bank_name, list):
            if bank_name[1]:
                return await interaction.response.send_message(
                    content=bank_name[0], ephemeral=True
                )
            else:
                return await interaction.response.send_message(content=bank_name[0])
        if isinstance(amount, list):
            if amount[1]:
                return await interaction.response.send_message(
                    content=amount[0], ephemeral=True
                )
            else:
                return await interaction.response.send_message(content=amount[0])
        await HYBRIDS.hybrid_remove(self, interaction, bank_name, amount, member)

    @slash_donologger.command(
        name="set",
        description="Set someone's donation balance to the amount of your choice.",
    )
    @app_commands.describe(
        bank_name="The name of the registered bank.",
        amount="The amount that you want to add. (examples: 10k, 1e6, 6900)",
        member="The member that you want to set donations.",
    )
    async def slash_donationlogger_set(
        self,
        interaction: discord.Interaction[Red],
        bank_name: app_commands.Transform[str, BankConverter],
        amount: app_commands.Transform[str, AmountConverter],
        member: Optional[discord.Member],
    ):
        """_summary_

        Args:
            context (commands.Context): _description_
            bank_name (BankConverter): _description_
            amount (AmountConverter): _description_
            member (discord.Member, optional): _description_. Defaults to None.
        """
        if not member:
            member = interaction.user
        if member.bot:
            return await interaction.response.send_message(
                content="Bots are prohibited from donations. (For obvious reasons)"
            )
        if isinstance(bank_name, list):
            if bank_name[1]:
                return await interaction.response.send_message(
                    content=bank_name[0], ephemeral=True
                )
            else:
                return await interaction.response.send_message(content=bank_name[0])
        if isinstance(amount, list):
            if amount[1]:
                return await interaction.response.send_message(
                    content=amount[0], ephemeral=True
                )
            else:
                return await interaction.response.send_message(content=amount[0])
        await HYBRIDS.hybrid_set(self, interaction, bank_name, amount, member)
