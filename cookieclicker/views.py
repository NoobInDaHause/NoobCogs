import discord
import noobutils as nu

from redbot.core import commands

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import CookieClicker


class CookieClickerView(nu.NoobView):
    def __init__(
        self, context: commands.Context, cog: "CookieClicker", timeout: float = 60.0
    ):
        super().__init__(obj=context, timeout=timeout)
        self.cog = cog
        self.message: discord.Message = None
        self.clicked = 0

    async def start(self):
        self.message = await self.context.send(view=self)

    @discord.ui.button(label="0")
    async def cookieclicker(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """Cookie clicker."""
        async with self.cog.config.guild(interaction.guild).user_lb() as ulb:
            ulb[str(self.context.author.id)] += 1
        self.clicked += 1
        button.label = str(self.clicked)
        await interaction.response.edit_message(view=self)

    @discord.ui.button(emoji="✖️", label="Quit", style=discord.ButtonStyle.danger)
    async def quit(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Quit cookie clicker."""
        for x in self.children:
            x.disabled = True
        self.stop()
        await interaction.response.edit_message(view=self)
