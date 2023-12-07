import contextlib
import discord
import noobutils as nu

from redbot.core.bot import commands, Red
from redbot.core.utils import mod

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import NoobTools


class AuditModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Set audit_reason.")

    wreason = discord.ui.TextInput(
        label="With Reason:",
        style=discord.TextStyle.long,
        required=True,
        placeholder="Action requested by {author_name} (ID {author_id}). Reason: {reason}",
    )

    woreason = discord.ui.TextInput(
        label="Without Reason:",
        style=discord.TextStyle.long,
        required=True,
        placeholder="Action requested by {author_name} (ID {author_id}).",
    )

    async def on_submit(self, interaction: discord.Interaction[Red]):
        await interaction.response.defer()


class ChangeAuditReasonView(discord.ui.View):
    def __init__(self, cog: "NoobTools", timeout: float = 180.0):
        super().__init__(timeout=timeout)
        self.cog = cog
        self.context: commands.Context = None
        self.message: discord.Message = None
        self.wreason: str = None
        self.woreason: str = None

    def update_embed(self, colour: discord.Colour) -> discord.Embed:
        embed = discord.Embed(colour=colour, timestamp=discord.utils.utcnow())
        embed.add_field(name="With Reason:", value=self.wreason, inline=False)
        embed.add_field(name="Without Reason:", value=self.woreason, inline=False)
        return embed

    async def start(self, context: commands.Context):
        embed = self.update_embed(await context.embed_colour())
        msg = await context.send(embed=embed, view=self)
        self.context = context
        self.message = msg

    @discord.ui.button(label="Set Reason", style=nu.get_button_colour("blurple"))
    async def set_reason(
        self, interaction: discord.Interaction[Red], button: discord.ui.Button
    ):
        modal = AuditModal()
        await interaction.response.send_modal(modal)
        await modal.wait()

        wr = modal.wreason.value
        wor = modal.woreason.value

        if not wr or not wor:
            return

        if "{author_name}" not in wr:
            return await interaction.followup.send(
                content="With reason is missing the '{author_name}' variable. Please try again.",
                ephemeral=True,
            )
        if "{author_id}" not in wr:
            return await interaction.followup.send(
                content="With reason is missing the '{author_id}' variable. Please try again.",
                ephemeral=True,
            )
        if "{reason}" not in wr:
            return await interaction.followup.send(
                content="With reason is missing the '{reason}' variable. Please try again.",
                ephemeral=True,
            )
        if "{author_name}" not in wor:
            return await interaction.followup.send(
                content="Without reason is missing the '{author_name}' variable. Please try again.",
                ephemeral=True,
            )
        if "{author_id}" not in wor:
            return await interaction.followup.send(
                content="Without reason is missing the '{author_id}' variable. Please try again.",
                ephemeral=True,
            )
        self.wreason = wr
        self.woreason = wor
        embed = self.update_embed(await self.context.embed_colour())
        await self.message.edit(embed=embed, view=self)

    @discord.ui.button(label="✔️", style=nu.get_button_colour("green"))
    async def complete(
        self, interaction: discord.Interaction[Red], button: discord.ui.Button
    ):
        if not self.wreason or not self.woreason:
            return await interaction.response.send_message(
                content="You need to set both with and without reason first."
            )

        def get_audit_reason(
            author: discord.Member, reason: str = None, *, shorten: bool = False
        ):
            audit_reason = (
                self.wreason.format(
                    author_name=author.name, author_id=author.id, reason=reason
                )
                if reason
                else self.woreason.format(author_name=author.name, author_id=author.id)
            )
            if shorten and len(audit_reason) > 512:
                audit_reason = f"{audit_reason[:509]}..."
            return audit_reason

        mod.get_audit_reason = get_audit_reason
        for x in self.children:
            x.disabled = True
        await self.message.edit(view=self)
        with_audit_reason = mod.get_audit_reason(
            interaction.user, "This is with reason"
        )
        without_audit_reason = mod.get_audit_reason(interaction.user)
        await self.cog.config.audit_reason.with_reason.set(self.wreason)
        await self.cog.config.audit_reason.without_reason.set(self.woreason)
        await interaction.response.send_message(
            content="Successfully changed the audit reason.\n\n"
            f"Here is the preview:\n**With Reason:**\n```{with_audit_reason}```\n"
            f"**Without reason:**\n```{without_audit_reason}```",
            ephemeral=True,
        )

    @discord.ui.button(emoji="✖️", style=nu.get_button_colour("red"))
    async def stop_button(
        self, interaction: discord.Interaction[Red], button: discord.ui.Button
    ):
        self.stop()
        await interaction.message.delete()

    async def interaction_check(self, interaction: discord.Interaction[Red]) -> bool:
        return await interaction.client.is_owner(interaction.user)

    async def on_timeout(self) -> None:
        for x in self.children:
            x.disabled = True
        self.stop()
        with contextlib.suppress(Exception):
            await self.message.edit(view=self)
