import discord
import noobutils as nu
import traceback

from redbot.core.bot import commands
from redbot.core.utils import mod

from typing import Any, Dict, Literal, List, TYPE_CHECKING, Union

from .converters import format_amount

if TYPE_CHECKING:
    from . import ServerDonations
    from donationlogger.donationlogger import DonationLogger


class SelectView(nu.NoobView):
    def __init__(
        self,
        cog: "ServerDonations",
        placeholder: str,
        options: List[discord.SelectOption],
        member: discord.Member,
        claimer: discord.Member,
        orig_inter: discord.Interaction[nu.Red],
        timeout: float = 300.0,
    ):
        super().__init__(obj=orig_inter, timeout=timeout)
        select = SelectBank(
            cog=cog,
            placeholder=placeholder,
            options=options,
            member=member,
            claimer=claimer,
        )
        self.add_item(select)
        self.claimer = claimer
        self.message: discord.Message = None

    async def start(self, content: str):
        msg = await self.interaction.message.reply(content=content, view=self)
        self.message = msg

    async def interaction_check(self, interaction: discord.Interaction[nu.Red]):
        if interaction.user.id != self.claimer.id:
            await interaction.response.send_message(
                content=f"You are not {self.claimer.mention}.", ephemeral=True
            )
            return False
        return True


class DonationsView(nu.NoobView):
    def __init__(
        self,
        cog: "ServerDonations",
        obj: Union[commands.Context, discord.Interaction[nu.Red]],
        channel: discord.TextChannel,
        _type: Literal["giveaway", "event", "heist"],
        timeout: float = 600.0,
    ):
        super().__init__(obj=obj, timeout=timeout)
        self.cog = cog
        self._type = _type
        self.channel = channel
        self.message: discord.Message = None
        self.claimer: discord.Member = None

    async def start(
        self,
        content: str,
        embed: discord.Embed,
        allowed_mentions: discord.AllowedMentions,
    ):
        msg = await self.channel.send(
            content=content, embed=embed, allowed_mentions=allowed_mentions, view=self
        )
        self.message = msg

    async def donationlogger_support(self, interaction: discord.Interaction[nu.Red]):
        dono_cog: "DonationLogger" = interaction.client.get_cog("DonationLogger")
        claimed = (
            f"{self._type.title()} donation claimed by {self.claimer.mention}.\n"
            f"{self.context.author.mention} your {self._type} donation has been accepted.\n"
        )
        if not await self.cog.config.guild(interaction.guild).dl_support():
            return await interaction.response.send_message(content=claimed)
        if not dono_cog:
            claimed += (
                "`It seem DonationLogger is not loaded, report this to the bot owner.`"
            )
            return await interaction.response.send_message(content=claimed)
        if not await dono_cog.config.guild(interaction.guild).setup():
            claimed += (
                "`DonationLogger is not set up in this guild yet ask an admin to set it up first so "
                "it supports adding donations to DonationLogger.`"
            )
            return await interaction.response.send_message(content=claimed)
        banks: Dict[str, Any] = await dono_cog.config.guild(interaction.guild).banks()
        select_options = []
        for k, v in banks.items():
            if not v["hidden"]:
                emote = v["emoji"] if v["emoji"] != "⏣" else None
                titolo = f"⏣ {k.title()}" if v["emoji"] == "⏣" else k.title()
                option = discord.SelectOption(label=titolo, value=k, emoji=emote)
                select_options.append(option)
        if not select_options:
            return await interaction.response.send_message(content=claimed)
        await interaction.response.defer()
        view = SelectBank(
            self.cog,
            "Select Bank to add donations.",
            select_options,
            self.context.author,
            self.claimer,
        )
        view = SelectView(
            self.cog,
            "Select Bank",
            select_options,
            self.context.author,
            self.claimer,
            interaction,
        )
        await view.start(claimed)

    @discord.ui.button(emoji="✔️", style=nu.get_button_colour("green"))
    async def accept_donation_button(
        self, interaction: discord.Interaction[nu.Red], button: discord.ui.Button
    ):
        if self.claimer:
            return await interaction.response.send_message(
                content=f"This donation has already been claimed/denied by {self.claimer.mention}.",
                ephemeral=True,
            )
        self.claimer = interaction.user
        for x in self.children:
            x.disabled = True
        if interaction.message.embeds:
            m = interaction.message.embeds
            m[0].colour = discord.Colour.green()
            await interaction.message.edit(view=self, embeds=m)
        else:
            await interaction.message.edit(view=self)
        await self.donationlogger_support(interaction)
        self.stop()

    @discord.ui.button(emoji="✖️", style=nu.get_button_colour("red"))
    async def deny_donation_button(
        self, interaction: discord.Interaction[nu.Red], button: discord.ui.Button
    ):
        if self.claimer:
            return await interaction.response.send_message(
                content=f"This donation has already been claimed/denied by {self.claimer.mention}.",
                ephemeral=True,
            )

        modal = DenyModal()
        await interaction.response.send_modal(modal)
        await modal.wait()
        if not modal.reason.value:
            return
        self.claimer = interaction.user
        reason = (
            f"- {self._type.title()} donation denied by {interaction.user.mention}.\n"
            f"- {self.context.author.mention} your {self._type} donation has been denied.\n"
        )
        if modal.reason.value.lower() != "none":
            reason += f"- `Reason:` {modal.reason.value}"
        await interaction.followup.send(content=reason)

        for x in self.children:
            x.disabled = True
        if interaction.message.embeds:
            m = interaction.message.embeds
            m[0].colour = discord.Colour.red()
            await interaction.message.edit(view=self, embeds=m)
        else:
            await interaction.message.edit(view=self)
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction[nu.Red]):
        if self._type == "giveaway":
            managers = await self.cog.config.guild(interaction.guild).managers.gmans()
        elif self._type == "event":
            managers = await self.cog.config.guild(interaction.guild).managers.emans()
        else:
            managers = await self.cog.config.guild(interaction.guild).managers.hmans()
        if (
            not await interaction.client.is_owner(interaction.user)
            and not await mod.is_mod_or_superior(interaction.client, interaction.user)
            and all(role_id not in interaction.user._roles for role_id in managers)
        ):
            await interaction.response.send_message(
                content="You do not have permission to accept or deny donations.",
                ephemeral=True,
            )
            return False
        return True


class DenyModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Reason for denial.", timeout=60.0)

    reason = discord.ui.TextInput(
        label="Ex: This is a joke donation.",
        placeholder="Put `none` if you don't want any reason.",
        style=discord.TextStyle.long,
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction[nu.Red]):
        await interaction.response.defer()

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        msg = "".join(
            traceback.format_exception(type(error), error, error.__traceback__)
        )
        self.cog.log.exception(msg, exc_info=error)
        await interaction.response.send_message(
            content="Something went wrong. Please report this to the bot owner.",
            ephemeral=True,
        )


class DonoModal(discord.ui.Modal):
    def __init__(self, cog: "ServerDonations", title: str, timeout: float):
        super().__init__(title=title, timeout=timeout)
        self.cog = cog

    amount = discord.ui.TextInput(
        label="You have 20 seconds to answer.",
        placeholder="Ex: 10m, 69, 420000",
        style=discord.TextStyle.short,
        required=True,
        max_length=1500,
    )

    note = discord.ui.TextInput(
        label="Note:",
        placeholder="Add an optional note.",
        style=discord.TextStyle.short,
        required=False,
        max_length=1024,
    )

    async def on_submit(self, interaction: discord.Interaction[nu.Red]):
        await interaction.response.defer()

    async def on_error(self, interaction: discord.Interaction, error: Exception):
        msg = "".join(
            traceback.format_exception(type(error), error, error.__traceback__)
        )
        self.cog.log.exception(msg, exc_info=error)
        await interaction.response.send_message(
            content="Something went wrong. Please report this to the bot owner.",
            ephemeral=True,
        )


class SelectBank(discord.ui.Select):
    def __init__(
        self,
        cog: "ServerDonations",
        placeholder: str,
        options: List[discord.SelectOption],
        member: discord.Member,
        claimer: discord.Member,
    ):
        super().__init__(
            placeholder=placeholder, options=options, min_values=1, max_values=1
        )
        self.member = member
        self.cog = cog
        self.claimer = claimer

    async def callback(self, interaction: discord.Interaction[nu.Red]):
        modal = DonoModal(self.cog, "The amount that you want to add.", 20.0)
        view: "SelectView" = self.view
        await interaction.response.send_modal(modal)
        await modal.wait()
        if not modal.amount.value:
            await view.message.edit(view=view)
            return
        amount = format_amount(modal.amount.value)
        if not amount:
            await view.message.edit(view=view)
            return await interaction.followup.send(
                content=f'Could not convert "{modal.amount.value}" into a valid amount.',
                ephemeral=True,
            )
        self.disabled = True
        await view.message.edit(view=view)
        ctx: commands.Context = await interaction.client.get_context(
            interaction.message
        )
        if cmd := interaction.client.get_command("donationlogger add"):
            await ctx.invoke(
                cmd,
                bank_name=self.values[0].lower(),
                amount=amount,
                member=self.member,
                note=modal.note.value,
            )
        else:
            return await interaction.followup.send(
                content="It seems the DonationLogger cog is not loaded/missing. "
                "Please report this to the bot owner.",
                ephemeral=True,
            )
        view.stop()
