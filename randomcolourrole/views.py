import discord

from redbot.core import commands

from typing import Optional

from .noobutils import access_denied

class Confirmation(discord.ui.View):
    def __init__(self, timeout: Optional[float] = 60.0):
        super().__init__(timeout=timeout)
        self.confirm_action: str = None
        self.context: commands.Context = None
        self.message: discord.Message = None
        self.value = None

    async def start(self, context: commands.Context, confirmation_msg: str, confirm_action: str):
        msg = await context.send(content=confirmation_msg, view=self)
        self.confirm_action = confirm_action
        self.context = context
        self.message = msg

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        for x in self.children:
            x.disabled = True
        self.value = "yes"
        self.stop()
        await interaction.response.edit_message(content=self.confirm_action, view=self)

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        for x in self.children:
            x.disabled = True
        self.value = "no"
        self.stop()
        await interaction.response.edit_message(content="Alright not doing that then.", view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if await self.context.bot.is_owner(interaction.user):
            return True
        elif interaction.user != self.context.author:
            await interaction.response.send_message(content=access_denied(), ephemeral=True)
            return False
        else:
            return True

    async def on_timeout(self):
        for x in self.children:
            x.disabled = True
        self.stop()
        await self.message.edit(view=self)
