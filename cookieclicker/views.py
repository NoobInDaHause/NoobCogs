import discord

from redbot.core import commands

from typing import TYPE_CHECKING

from noobutils import access_denied

if TYPE_CHECKING:
    from . import CookieClicker


class CookieClickerView(discord.ui.View):
    def __init__(self, cog: "CookieClicker", timeout: float = 60.0):
        super().__init__(timeout=timeout)
        self.cog = cog
        self.message: discord.Message = None
        self.context: commands.Context = None
        self.clicked = 0

    async def start(self, context: commands.Context):
        msg = await context.send(view=self)
        self.message = msg
        self.context = context

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

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if await self.context.bot.is_owner(interaction.user):
            return True
        elif interaction.user != self.context.author:
            await interaction.response.send_message(
                content=access_denied(), ephemeral=True
            )
            return False
        else:
            return True

    async def on_timeout(self):
        for x in self.children:
            x.disabled = True
        self.stop()
        await self.message.edit(view=self)
