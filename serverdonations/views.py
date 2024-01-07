import contextlib
import discord
import noobutils as nu
import traceback

from redbot.core.bot import commands, Red
from redbot.core.utils import mod

from typing import Literal, List, TYPE_CHECKING

from .converters import format_amount

if TYPE_CHECKING:
    from . import ServerDonations
    from donationlogger.donationlogger import DonationLogger


class SelectView(discord.ui.View):
    def __init__(
        self,
        cog: "ServerDonations",
        placeholder: str,
        options: List[discord.SelectOption],
        member: discord.Member,
        claimer: discord.Member,
        orig_inter: discord.Interaction[Red],
        timeout: float = 300.0,
    ):
        super().__init__(timeout=timeout)
        select = SelectBank(
            cog=cog,
            placeholder=placeholder,
            options=options,
            member=member,
            claimer=claimer,
        )
        self.add_item(select)
        self.claimer = claimer
        self.orig_inter = orig_inter
        self.message: discord.Message = None

    async def start(self, content: str):
        msg = await self.orig_inter.message.reply(content=content, view=self)
        self.message = msg

    async def interaction_check(self, interaction: discord.Interaction[Red]):
        if interaction.user.id != self.claimer.id:
            await interaction.response.send_message(
                content=f"You are not {self.claimer.mention}.", ephemeral=True
            )
            return False
        return True

    async def on_timeout(self) -> None:
        for x in self.children:
            x.disabled = True
        with contextlib.suppress(Exception):
            await self.message.edit(view=self)
        self.stop()


class DonationsView(discord.ui.View):
    def __init__(
        self,
        cog: "ServerDonations",
        context: commands.Context,
        channel: discord.TextChannel,
        _type: Literal["giveaway", "event", "heist"],
        timeout: float = 600.0,
    ):
        super().__init__(timeout=timeout)
        self.cog = cog
        self._type = _type
        self.context = context
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

    @discord.ui.button(emoji="✔️", style=nu.get_button_colour("green"))
    async def accept_donation_button(
        self, interaction: discord.Interaction[Red], button: discord.ui.Button
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
        dono_cog: "DonationLogger" = interaction.client.get_cog("DonationLogger")
        claimed = f"{self._type.title()} donation claimed by {self.claimer.mention}."
        if not dono_cog:
            return await interaction.response.send_message(content=claimed)
        if not await dono_cog.config.guild(interaction.guild).setup():
            return await interaction.response.send_message(content=claimed)
        banks = await dono_cog.config.guild(interaction.guild).banks()
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
            self.cog, "Select Bank to add donations.", select_options, self.context.author, self.claimer
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
        self.stop()

    @discord.ui.button(emoji="✖️", style=nu.get_button_colour("red"))
    async def deny_donation_button(
        self, interaction: discord.Interaction[Red], button: discord.ui.Button
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
            m[0].colour = discord.Colour.red()
            await interaction.message.edit(view=self, embeds=m)
        else:
            await interaction.message.edit(view=self)
        await interaction.response.send_message(
            content=f"{self._type.title()} donation denied by {interaction.user.mention}."
        )
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction[Red]):
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

    async def on_timeout(self) -> None:
        for x in self.children:
            x.disabled = True
        with contextlib.suppress(Exception):
            await self.message.edit(view=self)
        self.stop()


class DonoModal(discord.ui.Modal):
    def __init__(self, cog: "ServerDonations", title: str, timeout: float):
        super().__init__(title=title, timeout=timeout)
        self.cog = cog

    amount = discord.ui.TextInput(
        label="The amount that you want to add. (you have 10 seconds to answer)",
        placeholder="Ex: 10m, 69, 420000",
        style=discord.TextStyle.short,
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction[Red]):
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
        super().__init__(placeholder=placeholder, options=options, min_values=1, max_values=1)
        self.member = member
        self.cog = cog
        self.claimer = claimer

    async def callback(self, interaction: discord.Interaction[Red]):
        modal = DonoModal(self.cog, "Amount", 10.0)
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
                cmd, bank_name=self.values[0].lower(), amount=amount, member=self.member
            )
        else:
            return await interaction.followup.send(
                content="It seems the DonationLogger cog is not loaded/missing. "
                "Please report this to the bot owner.",
                ephemeral=True,
            )
        view.stop()
