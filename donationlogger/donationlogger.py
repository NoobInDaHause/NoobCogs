import asyncio
import contextlib
import discord
import noobutils as nu
import random

from redbot.core.utils import mod

from typing import Dict, Literal, List, Optional, TYPE_CHECKING, Union

from .converters import (
    AmountConverter as AC,
    BankConverter as BC,
    DLEmojiConverter,
    MemberOrUserConverter as MoUC,
)
from .utilities import (
    donationlogger_check,
    inter_send,
    manager_or_higher,
    verify_amount_roles,
)
from .views import (
    BankNameModal,
    DonationLoggerSetupView,
    DonoAddOrRemoveCtxMenu,
    TotalDonoView,
)

if TYPE_CHECKING:
    AmountConverter = int
    BankConverter = str
    MemberOrUserConverter = Union[discord.Member, discord.User]
else:
    AmountConverter = AC
    BankConverter = BC
    MemberOrUserConverter = MoUC


DEFAULT_GUILD = {
    "managers": [],
    "banks": {},
    "log_channel": None,
    "auto_role": False,
    "setup": False,
}


class DonationLogger(nu.Cog):
    """
    Donation Logger System.

    Log any donations from your server.
    """

    def __init__(self, bot: nu.Red, *args, **kwargs) -> None:
        super().__init__(
            bot=bot,
            cog_name=self.__class__.__name__,
            version="1.12.1",
            authors=["NoobInDaHause"],
            use_config=True,
            identifier=657668242451927167510,
            force_registration=True,
            *args,
            **kwargs,
        )
        self.config.register_guild(**DEFAULT_GUILD)
        self.check_member_balance_ctx_menu = nu.app_commands.ContextMenu(
            name="DonationLogger Balance",
            callback=self.balance_or_resetuser_ctx_callback,
            type=discord.AppCommandType.user,
        )
        self.resetuser_ctx_menu = nu.app_commands.ContextMenu(
            name="DonationLogger ResetUser",
            callback=self.balance_or_resetuser_ctx_callback,
            type=discord.AppCommandType.user,
        )
        self.add_member_donation_ctx_menu = nu.app_commands.ContextMenu(
            name="DonationLogger Add",
            callback=self.add_set_or_remove_ctx_callback,
            type=discord.AppCommandType.user,
        )
        self.remove_member_donation_ctx_menu = nu.app_commands.ContextMenu(
            name="DonationLogger Remove",
            callback=self.add_set_or_remove_ctx_callback,
            type=discord.AppCommandType.user,
        )
        self.set_member_donation_ctx_menu = nu.app_commands.ContextMenu(
            name="DonationLogger Set",
            callback=self.add_set_or_remove_ctx_callback,
            type=discord.AppCommandType.user,
        )
        self.setupcache = []

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
                if not banks:
                    continue
                for bank in banks.values():
                    if str(user_id) in bank["donators"]:
                        del bank["donators"][str(user_id)]

    async def cog_load(self):
        self.bot.tree.add_command(self.check_member_balance_ctx_menu)
        self.bot.tree.add_command(self.add_member_donation_ctx_menu)
        self.bot.tree.add_command(self.remove_member_donation_ctx_menu)
        self.bot.tree.add_command(self.resetuser_ctx_menu)
        self.bot.tree.add_command(self.set_member_donation_ctx_menu)
        self.bot.add_dev_env_value("donationlogger", lambda _: self)

    async def cog_unload(self):
        self.bot.tree.remove_command(
            self.check_member_balance_ctx_menu,
            type=self.check_member_balance_ctx_menu.type,
        )
        self.bot.tree.remove_command(
            self.add_member_donation_ctx_menu,
            type=self.add_member_donation_ctx_menu.type,
        )
        self.bot.tree.remove_command(
            self.remove_member_donation_ctx_menu,
            type=self.remove_member_donation_ctx_menu.type,
        )
        self.bot.tree.remove_command(
            self.resetuser_ctx_menu, type=self.resetuser_ctx_menu.type
        )
        self.bot.tree.remove_command(
            self.set_member_donation_ctx_menu,
            type=self.set_member_donation_ctx_menu.type,
        )
        self.bot.remove_dev_env_value("donationlogger")

    async def balance_or_resetuser_ctx_callback(
        self, interaction: discord.Interaction[nu.Red], member: discord.Member
    ):
        if member.bot:
            return await inter_send(
                interaction,
                content="Bots are prohibited from donations. (For obvious reasons)",
                ephemeral=True,
            )
        if not await self.config.guild(interaction.guild).setup():
            return await inter_send(
                interaction,
                content="DonationLogger has not been setup in this guild yet.",
                ephemeral=True,
            )
        cmd_name = interaction.command.qualified_name
        if cmd_name == "DonationLogger ResetUser":
            managers = await self.config.guild(interaction.guild).managers()
            if not await manager_or_higher(
                interaction.client, interaction.user, managers
            ):
                return await inter_send(
                    interaction,
                    content="You must have the set donation manager role or higher to run this command.",
                    ephemeral=True,
                )

        title = (
            "Would you like to check a specific bank?"
            if cmd_name == "DonationLogger Balance"
            else "Reset this member's donation balance."
        )
        dlrumodal = BankNameModal(title=title, timeout=60.0)
        await interaction.response.send_modal(dlrumodal)
        await dlrumodal.wait()
        bank_name = dlrumodal.bank_name.value

        if bank_name:
            bank_name = await BC().transform(interaction, bank_name)

        context: nu.commands.Context = await interaction.client.get_context(interaction)

        if cmd_name == "DonationLogger ResetUser":
            command = interaction.client.get_command("donationlogger resetuser")
            return await context.invoke(command, bank_name=bank_name, user=member)
        else:
            command = interaction.client.get_command("donationlogger balance")
            return await context.invoke(command, member=member, bank_name=bank_name)

    async def add_set_or_remove_ctx_callback(
        self, interaction: discord.Interaction[nu.Red], member: discord.Member
    ):
        if member.bot:
            return await inter_send(
                interaction,
                content="Bots are prohibited from donations. (For obvious reasons)",
                ephemeral=True,
            )
        if not await self.config.guild(interaction.guild).setup():
            return await inter_send(
                interaction,
                content="DonationLogger has not been setup in this guild yet.",
                ephemeral=True,
            )
        managers = await self.config.guild(interaction.guild).managers()
        if not await manager_or_higher(interaction.client, interaction.user, managers):
            return await inter_send(
                interaction,
                content="You must have the set donation manager role or higher to run this command.",
                ephemeral=True,
            )
        cmd_name = interaction.command.qualified_name

        t = (
            "Add"
            if cmd_name == "DonationLogger Add"
            else "Remove" if cmd_name == "DonationLogger Remove" else "Set"
        )
        dlamodal = DonoAddOrRemoveCtxMenu(
            title=f"{t} member donation balance.", timeout=60.0
        )
        await interaction.response.send_modal(dlamodal)
        await dlamodal.wait()
        bank_name = dlamodal.bank_name.value
        amount = dlamodal.amount.value

        if not bank_name or not amount:
            return
        try:
            bank_name = await BC().transform(interaction, bank_name)
            amount = await AC().transform(interaction, amount)
        except nu.commands.BadArgument as e:
            return await inter_send(interaction, content=str(e))

        if cmd_name == "DonationLogger Add":
            command = interaction.client.get_command("donationlogger add")
        elif cmd_name == "DonationLogger Remove":
            command = interaction.client.get_command("donationlogger remove")
        else:
            command = interaction.client.get_command("donationlogger set")

        context: nu.commands.Context = await interaction.client.get_context(interaction)
        return await context.invoke(
            command,
            bank_name=bank_name,
            amount=amount,
            member=member,
            note=dlamodal.note.value,
        )

    async def get_dc_from_bank(
        self, context: nu.commands.Context, bank_name: str
    ) -> List[discord.Embed]:
        banks: Dict[str, Dict[str, dict]] = await self.config.guild(
            context.guild
        ).banks()
        bank_info = banks.get(bank_name)

        if not bank_info or bank_info["hidden"]:
            return []

        total_member_donated = bank_info["donators"].get(str(context.author.id))
        auth = (
            f"You have donated a total of: {nu.cf.humanize_number(total_member_donated)}"
            if total_member_donated
            else "You do not have any donation data for this bank."
        )
        sorted_donators = sorted(
            bank_info["donators"].items(), key=lambda x: x[1], reverse=True
        )
        total_donated = sum(bank_info["donators"].values())

        final = [
            f"### > - Overall Donated Amount: {nu.cf.humanize_number(total_donated)}\n"
        ]
        for index, (k, v) in enumerate(sorted_donators, 1):
            member = context.guild.get_member(int(k))
            e = "➡️ " if member == context.author else ""
            final.append(
                f"{e}{index}. {member.mention} (`{member.id}`): **{nu.cf.humanize_number(v)}**"
                if member
                else f"{index}. [Member not found in guild] (`{k}`): **{nu.cf.humanize_number(v)}**"
            )

        return await nu.pagify_this(
            "\n".join(final),
            "\n" "".join([f"{context.guild.name}", " | Page ({index}/{pages})"]),
            page_char=1500,
            embed_title=f"All of the donors for [{bank_name.title()}]",
            embed_colour=await context.embed_colour(),
            author_name=auth,
            footer_icon=nu.is_have_avatar(context.guild),
        )

    async def get_user_balance(
        self, guild: discord.Guild, user_id: int, bank_name: str = None
    ) -> discord.Embed:
        banks: Dict[str, Dict[str, dict]] = await self.config.guild(guild).banks()
        if bank_name:
            bank = banks[bank_name.lower()]
            donations = bank["donators"].get(str(user_id))
            embed = discord.Embed(
                title=f"[Member not found in guild] ({user_id})",
                timestamp=discord.utils.utcnow(),
            )
            if donations is not None:
                embed.description = (
                    f"Bank: {bank_name.title()}\n"
                    f"Total amount donated: {bank['emoji']} {nu.cf.humanize_number(donations)}"
                )
            else:
                embed.description = "This uesr has no data in this guild."
            return embed

        _dict: Dict[str, Dict[str, Union[str, int]]] = {}
        for k, v in banks.items():
            if v["hidden"]:
                continue
            donos = v["donators"].get(str(user_id), 0)
            _dict[k] = {"donations": donos, "emoji": v["emoji"]}

        new_dict = dict(filter(lambda x: x[1]["donations"], _dict.items()))
        if not new_dict:
            return discord.Embed(
                title=f"[Member not found in guild] ({user_id})",
                description="This user has no data in this guild.",
                timestamp=discord.utils.utcnow(),
            )

        final: Dict[str, str] = {}
        final_overall = []
        for key, value in _dict.items():
            donos = value["donations"]
            final[key] = f"{value['emoji']} {nu.cf.humanize_number(donos)}"
            final_overall.append(donos)

        overall = sum(final_overall)
        embed = discord.Embed(
            description=f"Overall combined bank donation amount: {nu.cf.humanize_number(overall)}",
            timestamp=discord.utils.utcnow(),
        )
        embed.set_author(name=f"[Member not found in guild] ({user_id})")
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

    async def get_all_bank_member_dono(
        self, guild: discord.Guild, member: discord.Member
    ) -> discord.Embed:
        final: Dict[str, str] = {}
        final_overall = []
        async with self.config.guild(guild).banks() as banks:
            for k, v in banks.items():
                if v["hidden"]:
                    continue
                donations = v["donators"].get(str(member.id), 0)
                final[k] = f"{v['emoji']} {nu.cf.humanize_number(donations)}"
                final_overall.append(donations)

        overall = sum(final_overall)
        embed = discord.Embed(
            description=f"Overall combined bank donation amount: {nu.cf.humanize_number(overall)}",
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
        context: nu.commands.Context,
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
        context: nu.commands.Context,
        d_type: str,
        bank_name: str,
        emoji: str,
        amount: int,
        previous: int,
        updated: int,
        member: discord.Member,
        roles: str = None,
        note: str = None,
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
                f"{emoji} {nu.cf.humanize_number(amount)} {ar} **{member.display_name}**'s donation balance."
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
            value=f"{emoji} {nu.cf.humanize_number(previous)}",
            inline=True,
        )
        embed.add_field(
            name="Updated balance:",
            value=f"{emoji} {nu.cf.humanize_number(updated)}",
            inline=True,
        )
        if note:
            embed.add_field(name="Note:", value=note, inline=False)

        if roles:
            added = []
            removed = []
            split_roles = roles.split(",")
            for splitted_role in split_roles:
                more_split = splitted_role.split(":")
                if more_split[1].strip() == "A":
                    added.append(more_split[0])
                else:
                    removed.append(more_split[0])
            if added:
                true_added_name = ra.replace(" and/or Removed", "")
                embed.add_field(name=true_added_name, value=added, inline=False)
            if removed:
                true_removed_name = ra.replace(" Added and/or", "")
                embed.add_field(name=true_removed_name, value=removed, inline=False)
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

    @nu.commands.hybrid_group(
        name="donationlogger", aliases=["d", "dl", "dono", "donolog"]
    )
    @nu.commands.bot_has_permissions(embed_links=True)
    @nu.commands.guild_only()
    async def donationlogger(self, context: nu.commands.Context):
        """
        DonationLogger base commands.
        """
        pass

    @donationlogger.command(name="resetcog")
    @donationlogger_check(owner_only=True)
    async def donationlogger_resetcog(self, context: nu.commands.Context):
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
    @donationlogger_check(setup_check=True)
    async def donationlogger_setup(self, context: nu.commands.Context):
        """
        Setup the donation logger system in this guild.
        """
        if await self.config.guild(context.guild).setup():
            return await context.send(
                content="DonationLogger has already been setup in this server."
            )
        conf = (
            "You are about to set up DonationLogger system in your server.\n"
            "Click Yes to continue or No to abort."
        )
        act = "Alright sending set up interactions, please wait..."
        view = nu.NoobConfirmation()
        await view.start(context, act, content=conf)
        await view.wait()
        await asyncio.sleep(3)
        if view.value:
            if context.guild.id in self.setupcache:
                return await context.send(
                    content="Only one setup interaction per guild.", ephemeral=True
                )
            self.setupcache.append(context.guild.id)
            await DonationLoggerSetupView(self).start(context)

    @donationlogger.command(name="resetuser")
    @donationlogger_check(check_if_setup_done=True, check_if_manager_or_higher=True)
    @nu.app_commands.describe(
        bank_name="The name of the registered bank.",
        user="The member or user that you want to reset donations. (leave blank to choose yourself)",
    )
    async def donationlogger_resetuser(
        self,
        context: nu.commands.Context,
        bank_name: Optional[BankConverter] = None,
        user: MemberOrUserConverter = None,
    ):
        """
        Reset a member or user's specific bank or all bank donations.
        """
        user = user or context.author
        if user.bot:
            return await context.send(content="Bots are not allowed.")

        if bank_name:
            act = f"Successfully cleared **{bank_name.title()}** donations from **{user.name}**."
            conf = f"Are you sure you want to clear **{bank_name.title()}** donations from **{user.name}**"
            view = nu.NoobConfirmation()
            await view.start(context, act, content=conf)
            await view.wait()
            if view.value:
                async with self.config.guild(context.guild).banks() as banks:
                    bank = banks[bank_name.lower()]
                    donations = bank["donators"].get(str(user.id))
                    if donations is not None:
                        del bank["donators"][str(user.id)]
                        if isinstance(user, discord.Member):
                            await self.update_dono_roles(
                                context, "remove", 0, user, bank["roles"]
                            )
            return

        act = f"Successfully cleared all bank donations from **{user.name}**."
        conf = (
            f"Are you sure you want to erase all bank donations from **{user.name}**?"
        )
        view = nu.NoobConfirmation()
        await view.start(context, act, content=conf)
        await view.wait()
        if view.value:
            async with self.config.guild(context.guild).banks() as banks:
                for bank in banks.values():
                    donos = bank["donators"].get(str(user.id))
                    if donos is not None:
                        del bank["donators"][str(user.id)]
                        if isinstance(user, discord.Member):
                            await self.update_dono_roles(
                                context, "remove", 0, user, bank["roles"]
                            )

    @donationlogger.command(name="balance", aliases=["bal", "c", "check"])
    @donationlogger_check(check_if_setup_done=True)
    @nu.app_commands.describe(
        member="The member or user that you want to check donations. (leave blank to choose yourself)",
        bank_name="The name of the registered bank.",
    )
    async def donationlogger_balance(
        self,
        context: nu.commands.Context,
        member: Optional[MemberOrUserConverter] = None,
        bank_name: BankConverter = None,
    ):
        """
        Check your or some one else's donation balance.
        """
        member = member or context.author
        if member.bot:
            return await context.send(
                content="Bots are prohibited from donations. (For obvious reasons)"
            )

        if isinstance(member, discord.Member):
            if bank_name:
                async with self.config.guild(context.guild).banks() as banks:
                    bank = banks[bank_name.lower()]
                    if bank["hidden"]:
                        return await context.send(content="This bank is hidden")
                    donations = bank["donators"].get(str(member.id), 0)
                    embed = discord.Embed(
                        title=f"{member.name} ({member.id})",
                        description=(
                            f"Bank: {bank_name.title()}\n"
                            f"Total amount donated: {bank['emoji']} {nu.cf.humanize_number(donations)}"
                        ),
                        timestamp=discord.utils.utcnow(),
                        colour=member.colour,
                    )
                    embed.set_thumbnail(url=nu.is_have_avatar(member))
                    embed.set_footer(
                        text=f"{context.guild.name} admires your donations!",
                        icon_url=nu.is_have_avatar(context.guild),
                    )
            else:
                embed = await self.get_all_bank_member_dono(context.guild, member)
        else:
            embed = await self.get_user_balance(context.guild, member.id, bank_name)

        await context.send(embed=embed)

    @donationlogger.command(name="donationcheck", aliases=["dc"])
    @donationlogger_check(check_if_setup_done=True)
    @nu.app_commands.rename(mla="more_less_all")
    @nu.app_commands.describe(
        bank_name="The name of the registered bank.",
        mla="Check More, Less or All donations from the bank.",
        amount="The amount to check. (leave blank if you will check all) (examples: 10k, 1e6, 6900)",
    )
    async def donationlogger_donationcheck(
        self,
        context: nu.commands.Context,
        bank_name: BankConverter,
        mla: Literal["more", "less", "all"],
        amount: AmountConverter = None,
    ):
        """
        See who has donated more or less or all from a bank.
        """
        if mla == "all":
            embeds = await self.get_dc_from_bank(context, bank_name)
            if not embeds:
                return await context.send(content="This bank is hidden.")
            await nu.NoobPaginator(embeds).start(context)
            return

        if not amount:
            return await context.send_help()

        banks_config: Dict[str, Dict[str, dict]] = await self.config.guild(
            context.guild
        ).banks()
        bank_data = banks_config.get(bank_name.lower(), {})
        if bank_data.get("hidden"):
            return await context.send(content="This bank is hidden.")

        donators = bank_data.get("donators", {})
        filtered_donators = {
            k: v
            for k, v in donators.items()
            if (mla == "more" and v >= amount) or (mla == "less" and v < amount)
        }

        sorted_donators = sorted(
            filtered_donators.items(), key=lambda u: u[1], reverse=(mla == "more")
        )

        output_list = []
        for index, (donator_id, donation_amount) in enumerate(sorted_donators, 1):
            member = context.guild.get_member(int(donator_id))
            mention = (
                f"{member.mention} (`{member.id}`)"
                if member
                else f"Member not found in server. (`{donator_id}`)"
            )
            e = "➡️ " if member and member.id == context.author.id else ""
            output_list.append(
                f"{e}{index}. {mention}: **{nu.cf.humanize_number(donation_amount)}**"
            )

        output_text = "\n".join(
            output_list
            or [
                f"No one has donated {mla} than **{nu.cf.humanize_number(amount)}** yet."
            ]
        )

        paginated_output = await nu.pagify_this(
            output_text,
            "\n",
            "Page ({index}/{pages})",
            embed_title=f"All members who have donated {mla} than {nu.cf.humanize_number(amount)} "
            f"for [{bank_name.title()}]",
            embed_colour=await context.embed_colour(),
        )

        await nu.NoobPaginator(paginated_output).start(context)

    @donationlogger.command(name="leaderboard", aliases=["lb"])
    @donationlogger_check(check_if_setup_done=True)
    @nu.app_commands.describe(
        bank_name="The name of the registered bank.",
        top="The top number. (min: 1, max: 25, default: 10)",
        show_left_users="Whether to show the users who are not in the guild.",
    )
    async def donationlogger_leaderboard(
        self,
        context: nu.commands.Context,
        bank_name: BankConverter,
        top: Optional[int] = 10,
        show_left_users: bool = False,
    ):
        """
        See who has donated the most from a bank.

        **top**: The top number to show. (max 25)
        **show_left_users**: Whether to show the users who are not in the guild.
        """
        if top > 25 or top < 1:
            return await context.send(content="Top number must be between 1-25.")
        banks: Dict[str, Dict[str, dict]] = await self.config.guild(
            context.guild
        ).banks()
        if banks[bank_name.lower()]["hidden"]:
            return await context.send(content="This bank is hidden.")
        donors = banks[bank_name.lower()]["donators"]
        emoji = banks[bank_name.lower()]["emoji"]
        filtered_donors = {}
        for i, j in donors.items():
            if j <= 0:
                continue
            memb = context.guild.get_member(int(i))
            if not memb and not show_left_users:
                continue
            member = memb.name if memb else f"[Member not found in guild] ({i})"
            filtered_donors[member] = j

        sorted_donors = dict(
            sorted(filtered_donors.items(), key=lambda m: m[1], reverse=True)
        )
        embed = discord.Embed(
            title=f"Top {top} donators for [{bank_name.title()}]",
            colour=random.randint(0, 0xFFFFFF),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_footer(text=context.guild.name)
        embed.set_thumbnail(url=nu.is_have_avatar(context.guild))
        if not sorted_donors:
            embed.description = "It seems no one has donated from this bank yet."
        for index, (k, v) in enumerate(sorted_donors.items(), 1):
            if index > top:
                break
            embed.add_field(
                name=f"{index}. {k}",
                value=f"{emoji} {nu.cf.humanize_number(v)}",
                inline=False,
            )
        await context.send(embed=embed)

    @donationlogger.command(name="add", aliases=["+", "a"])
    @donationlogger_check(check_if_setup_done=True, check_if_manager_or_higher=True)
    @nu.app_commands.describe(
        bank_name="The name of the registered bank.",
        amount="The amount that you want to add. (examples: 10k, 1e6, 6900)",
        member="The member that you want to add donations to.",
        note="Add an optional note as to why you added this donation.",
    )
    async def donationlogger_add(
        self,
        context: nu.commands.Context,
        bank_name: BankConverter,
        amount: AmountConverter,
        member: Optional[discord.Member] = None,
        *,
        note: Optional[str] = None,
    ):
        """
        Add bank donation amount to a member or yourself.
        """
        member = member or context.author
        if member.bot:
            return await context.send(
                content="Bots are prohibited from donations. (For obvious reasons)"
            )
        if note and len(note) > 1024:
            return await context.send(
                content="Limit your note into 1024 characters due to embed field limits."
            )

        async with self.config.guild(context.guild).banks() as banks:
            bank: Dict[str, dict] = banks[bank_name.lower()]
            emoji = bank["emoji"]
            if bank["hidden"]:
                return await context.send(content="This bank is hidden.")
            multi = bank.get("multi")
            if multi:
                amount = round(amount * multi)
            if amount > 999999999999999:
                return await context.send(
                    content="The amount you provided is way too high, consider adding something reasonable.",
                )
            bank["donators"].setdefault(str(member.id), 0)
            bank["donators"][str(member.id)] += amount
            updated = bank["donators"][str(member.id)]
            previous = updated - amount
            donated = nu.cf.humanize_number(amount)
            total = nu.cf.humanize_number(updated)
            roles = await self.update_dono_roles(
                context, "add", updated, member, bank["roles"]
            )
            humanized_roles = nu.cf.humanize_list([role.mention for role in roles])
            rep = (
                f"{emoji} **{donated}** was added to **{member.name}**'s **__{bank_name.title()}__** "
                f"donation balance.\nTheir total donation balance is now **{emoji} {total}** on "
                f"**__{bank_name.title()}__**."
            )
            embed = discord.Embed(
                title="Successfully Added",
                description=rep,
                colour=member.colour,
                timestamp=discord.utils.utcnow(),
            )
            if multi:
                embed.set_footer(text=f"Donation Multiplier: x{multi}")
            if humanized_roles:
                embed.add_field(
                    name="Added Donation Roles:", value=humanized_roles, inline=False
                )
            await TotalDonoView(self).start(
                context, member, content=member.mention, embed=embed
            )
            await self.send_to_log_channel(
                context,
                "add",
                bank_name,
                emoji,
                amount,
                previous,
                updated,
                member,
                humanized_roles,
                note,
            )

    @donationlogger.command(name="remove", aliases=["-", "r"])
    @donationlogger_check(check_if_setup_done=True, check_if_manager_or_higher=True)
    @nu.app_commands.describe(
        bank_name="The name of the registered bank.",
        amount="The amount that you want to add. (examples: 10k, 1e6, 6900)",
        member="The member that you want to remove donations from.",
        note="Add an optional note as to why you removed this donation.",
    )
    async def donationlogger_remove(
        self,
        context: nu.commands.Context,
        bank_name: BankConverter,
        amount: AmountConverter,
        member: Optional[discord.Member] = None,
        *,
        note: Optional[str] = None,
    ):
        """
        Remove bank donation amount to a member or yourself.
        """
        member = member or context.author
        if member.bot:
            return await context.send(
                content="Bots are prohibited from donations. (For obvious reasons)"
            )
        if note and len(note) > 1024:
            return await context.send(
                content="Limit your note into 1024 characters due to embed field limits."
            )

        async with self.config.guild(context.guild).banks() as banks:
            bank: Dict[str, dict] = banks[bank_name.lower()]
            donators = bank["donators"]
            emoji = bank["emoji"]
            member_id = str(member.id)
            if bank["hidden"]:
                return await context.send(content="This bank is hidden.")
            d = donators.get(member_id)
            if d == 0 or d is None:
                return await context.send(
                    content="This member has 0 donation balance for this bank."
                )
            donators[member_id] -= amount
            updated1 = donators[member_id]
            if updated1 < 0:
                del donators[member_id]
            updated2 = donators.get(member_id, 0)
            previous = updated1 + amount
            donated = nu.cf.humanize_number(amount)
            total = nu.cf.humanize_number(updated2)
            roles = await self.update_dono_roles(
                context, "remove", updated2, member, bank["roles"]
            )
            humanized_roles = nu.cf.humanize_list([role.mention for role in roles])
            rep = (
                f"{emoji} **{donated}** was removed from **{member.name}**'s **__{bank_name.title()}__** "
                f"donation balance.\nTheir total donation balance is now **{emoji} {total}** on "
                f"**__{bank_name.title()}__**."
            )
            embed = discord.Embed(
                title="Successfully Removed",
                description=rep,
                colour=member.colour,
                timestamp=discord.utils.utcnow(),
            )
            if humanized_roles:
                embed.add_field(
                    name="Removed Donation Roles:", value=humanized_roles, inline=False
                )
            await TotalDonoView(self).start(
                context, member, content=member.mention, embed=embed
            )
            await self.send_to_log_channel(
                context,
                "remove",
                bank_name,
                emoji,
                amount,
                previous,
                updated2,
                member,
                humanized_roles,
                note,
            )

    @donationlogger.command(name="set")
    @donationlogger_check(check_if_setup_done=True, check_if_manager_or_higher=True)
    @nu.app_commands.describe(
        bank_name="The name of the registered bank.",
        amount="The amount that you want to add. (examples: 10k, 1e6, 6900)",
        member="The member that you want to set donations.",
        note="Add an optional note as to why you removed this donation.",
    )
    async def donationlogger_set(
        self,
        context: nu.commands.Context,
        bank_name: BankConverter,
        amount: AmountConverter,
        member: Optional[discord.Member] = None,
        *,
        note: str = None,
    ):
        """
        Set someone's donation balance to the amount of your choice.
        """
        member = member or context.author
        if member.bot:
            return await context.send(
                content="Bots are prohibited from donations. (For obvious reasons)"
            )
        if note and len(note) > 1024:
            return await context.send(
                content="Limit your note into 1024 characters due to embed field limits."
            )

        async with self.config.guild(context.guild).banks() as banks:
            bank: Dict[str, dict] = banks[bank_name.lower()]
            donators = bank["donators"]
            emoji = bank["emoji"]
            if bank["hidden"]:
                return await context.send(content="This bank is hidden.")
            donators.setdefault(str(member.id), 0)
            previous = donators[str(member.id)]
            donators[str(member.id)] = amount
            aroles = await self.update_dono_roles(
                context, "add", amount, member, bank["roles"]
            )
            rrole = await self.update_dono_roles(
                context, "remove", amount, member, bank["roles"]
            )
            humanized_added_roles = nu.cf.humanize_list([har.mention for har in aroles])
            humanized_removed_roles = nu.cf.humanize_list(
                [hre.mention for hre in rrole]
            )
            rep = (
                f"{emoji} **{nu.cf.humanize_number(amount)}** was set as **{member.name}**'s "
                f"**__{bank_name.title()}__** donation balance."
            )
            embed = discord.Embed(
                title="Successfully Set",
                description=rep,
                colour=member.colour,
                timestamp=discord.utils.utcnow(),
            )
            if humanized_added_roles:
                embed.add_field(
                    name="Added Donation Roles:",
                    value=humanized_added_roles,
                    inline=False,
                )
            if humanized_removed_roles:
                embed.add_field(
                    name="Removed Donation Roles:",
                    value=humanized_removed_roles,
                    inline=False,
                )
            await TotalDonoView(self).start(
                context, member, content=member.mention, embed=embed
            )
            humanized_roles = nu.cf.humanize_list(
                [f"{lrr.mention}: A" for lrr in aroles]
                + [f"{lar.mention}: R" for lar in rrole]
            )
            await self.send_to_log_channel(
                context,
                "set",
                bank_name,
                emoji,
                amount,
                previous,
                amount,
                member,
                humanized_roles,
                note,
            )

    @nu.commands.group(
        name="donationloggerset", aliases=["dlset", "donologset", "donoset"]
    )
    @nu.commands.admin_or_permissions(manage_guild=True)
    @nu.commands.bot_has_permissions(embed_links=True)
    @donationlogger_check(check_if_setup_done=True)
    async def donationloggerset(self, context: nu.commands.Context):
        """
        DonationLogger settings commands.
        """
        pass

    @donationloggerset.group(name="bank")
    async def donationloggerset_bank(self, context: nu.commands.Context):
        """
        Bank settings commands.
        """
        pass

    @donationloggerset_bank.command(name="multiplier", aliases=["multi"])
    async def donationloggerset_bank_multiplier(
        self,
        context: nu.commands.Context,
        set_or_list: Literal["set", "list"],
        bank_name: BankConverter = None,
        multiplier: float = None,
    ):
        """
        Manage setting donation multipliers from banks.

        Every donation multiplier defaults to 1.

        Example:
        `[p]donoset bank multi set dank 2.0`
        """
        if set_or_list == "list":
            banks: Dict[str, Dict[str, dict]] = await self.config.guild(
                context.guild
            ).banks()
            desc = [
                f"{k}: **x{v['multi']}**" for k, v in banks.items() if v.get("multi")
            ]
            embed = discord.Embed(
                title="List of banks with mutipliers",
                description="\n".join(
                    desc or ["There are no banks with multipliers yet."]
                ),
                colour=self.bot._color,
                timestamp=discord.utils.utcnow(),
            )
            return await context.send(embed=embed)
        else:
            if not bank_name:
                return await context.send_help()

            if multiplier:
                if multiplier <= 1.0:
                    return await context.send(
                        content="You can not set the multiplier below or equal to 1.0."
                    )
                if multiplier > 10.0:
                    return await context.send(
                        content="You can only set up to a maximum of x10.0 multiplier per bank."
                    )
                await context.send(
                    content=f"Successfully set **x{multiplier}** multiplier from **__{bank_name.title()}__**."
                )
            else:
                await context.send(content="The multi for that bank has been removed.")

            async with self.config.guild(context.guild).banks() as banks:
                if multiplier == 1.0:
                    with contextlib.suppress(KeyError):
                        del banks[bank_name]["multi"]
                else:
                    banks[bank_name]["multi"] = multiplier

    @donationloggerset_bank.command(name="add")
    async def donationloggerset_bank_add(
        self,
        context: nu.commands.Context,
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
        self, context: nu.commands.Context, bank_name: BankConverter
    ):
        """
        Remove a bank.
        """
        async with self.config.guild(context.guild).banks() as banks:
            if len(banks) == 1:
                return await context.send(
                    content="This bank is the guild's only bank, you can not remove it."
                )
            del banks[bank_name]
        await context.send(content="That bank is deleted.")

    @donationloggerset_bank.command(name="list")
    async def donationloggerset_bank_list(self, context: nu.commands.Context):
        """
        See the list of registered banks.
        """
        all_banks: Dict[str, Dict[str, dict]] = await self.config.guild(
            context.guild
        ).banks()
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
    async def donationloggerset_bank_amountroles(self, context: nu.commands.Context):
        """
        Bank Amount-Roles settings commands.
        """
        pass

    @donationloggerset_bank_amountroles.command(name="set", aliases=["add"])
    async def donationloggerset_bank_amountroles_set(
        self,
        context: nu.commands.Context,
        bank_name: BankConverter,
        *,
        amountroles: str,
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
                banks[bank_name]["roles"] |= {
                    k: [r.id for r in v] for k, v in arole.items()
                }

            embed = discord.Embed(
                title="Amount roles has been set.",
                description="\n".join(
                    [
                        f"{nu.cf.humanize_number(int(k))}: {nu.cf.humanize_list([r.mention for r in v])}"
                        for k, v in arole.items()
                    ]
                ),
                colour=await context.embed_colour(),
                timestamp=discord.utils.utcnow(),
            )
            await context.send(embed=embed)
        except nu.commands.BadArgument:
            return await context.send(
                content="The maximum roles you can assign to an amount should be no more than 3."
            )

    @donationloggerset_bank_amountroles.command(name="remove")
    async def donationloggerset_bank_amountroles_add(
        self,
        context: nu.commands.Context,
        bank_name: BankConverter,
        amount: AmountConverter,
    ):
        """
        Remove an amount from the roles milestone.
        """
        async with self.config.guild(context.guild).banks() as banks:
            try:
                del banks[bank_name]["roles"][str(amount)]
                await context.send(content="That amount has been removed.")
            except KeyError:
                await context.send(content="You haven't registered that amount yet.")

    @donationloggerset_bank_amountroles.command(name="list")
    async def donationloggerset_bank_amountroles_list(
        self, context: nu.commands.Context, bank_name: BankConverter
    ):
        """
        See the list of amountroles on a bank.
        """
        banks: Dict[str, Dict[str, dict]] = await self.config.guild(
            context.guild
        ).banks()
        aroles = banks[bank_name]["roles"]
        sorted_aroles = dict(sorted(aroles.items(), key=lambda j: int(j[0])))
        aroles2 = [
            f"**{nu.cf.humanize_number(int(k))}**: {nu.cf.humanize_list([f'<@&{i}>' for i in v])}"
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
        context: nu.commands.Context,
        roles_or_donators: Literal["amountroles", "donators", "both"],
        bank_name: BankConverter,
    ):
        """
        Reset a banks donations or amountroles.
        """
        async with self.config.guild(context.guild).banks() as banks:
            if roles_or_donators == "amountroles":
                banks[bank_name]["roles"] = {}
            elif roles_or_donators == "donators":
                banks[bank_name]["donators"] = {}
            else:
                banks[bank_name]["roles"] = {}
                banks[bank_name]["donators"] = {}
        _type = (
            roles_or_donators
            if roles_or_donators == "amountroles"
            else (
                roles_or_donators
                if roles_or_donators == "donators"
                else "both amountroles and donators"
            )
        )
        await context.send(content=f"Bank **{bank_name}** {_type} has been reset.")

    @donationloggerset_bank.command(name="emoji")
    async def donationloggerset_bank_emoji(
        self,
        context: nu.commands.Context,
        bank_name: BankConverter,
        emoji: DLEmojiConverter,
    ):
        """
        Change a bank's emoji.
        """
        async with self.config.guild(context.guild).banks() as banks:
            banks[bank_name]["emoji"] = str(emoji)
            await context.send(
                content=f"Successfully changed **{bank_name}**'s emoji to {str(emoji)}"
            )

    @donationloggerset_bank.command(name="hidden")
    async def donationloggerset_bank_hidden(
        self,
        context: nu.commands.Context,
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
                banks[bank_name]["hidden"] = hidden == "hide"
                status = "is now" if hidden == "hide" else "is no longer"
                await context.send(content=f"Bank **{bank_name}** {status} hidden.")
        else:
            all_banks: Dict[str, Dict[str, dict]] = await self.config.guild(
                context.guild
            ).banks()
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
        context: nu.commands.Context,
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
                description=nu.cf.humanize_list([f"<@&{i}>" for i in managers]),
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
                    content=f"Successfully {_type} {nu.cf.humanize_list(success)} {_type2} the list of "
                    "manager roles."
                )
            if failed:
                await context.send(
                    content=f"Failed to {add_remove_list} {nu.cf.humanize_list(failed)} {_type2} the list of "
                    "manager roles since they are already manager roles."
                )

    @donationloggerset.command(name="logchannel")
    async def donationloggerset_logchannel(
        self, context: nu.commands.Context, channel: discord.TextChannel = None
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
    async def donationloggerset_resetguild(self, context: nu.commands.Context):
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
    async def donationloggerset_autorole(self, context: nu.commands.Context):
        """
        Enable or Disable automatic role additon or removal.
        """
        current = await self.config.guild(context.guild).auto_role()
        await self.config.guild(context.guild).auto_role.set(not current)
        status = "will no longer" if current else "will now"
        await context.send(content=f"I {status} automatically add or remove roles.")

    @donationloggerset.command(name="showsettings", aliases=["ss", "showallsettings"])
    async def donationloggerset_showsettings(self, context: nu.commands.Context):
        """
        See all the current set settings for this guild's DonationLogger system.
        """
        managers = await self.config.guild(context.guild).managers()
        autorole = await self.config.guild(context.guild).auto_role()
        banks: Dict[str, Dict[str, dict]] = await self.config.guild(
            context.guild
        ).banks()
        log_channel = await self.config.guild(context.guild).log_channel()
        bank_list = [f"{k.title()}" for k in banks]
        banks_list_hidden = [f"{k.title()}" for k, v in banks.items() if v["hidden"]]
        embed = discord.Embed(
            title=f"Current DonationLogger settings for [{context.guild.name}]",
            colour=await context.embed_colour(),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_thumbnail(url=nu.is_have_avatar(context.guild))
        embed.add_field(
            name="DonationLogger Managers:",
            value=nu.cf.humanize_list([f"<@&{i}>" for i in managers]),
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
            value=nu.cf.humanize_list(
                bank_list or ["There are no registered banks yet, or banks are hidden."]
            ),
            inline=False,
        )
        if banks_list_hidden:
            embed.add_field(
                name="Hidden Banks:",
                value=nu.cf.humanize_list(banks_list_hidden),
                inline=False,
            )
        await context.send(embed=embed)
