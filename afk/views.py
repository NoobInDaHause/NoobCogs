import discord

from redbot.core import commands
from redbot.core.bot import Red

from typing import Optional

class Confirmation(discord.ui.View):
    def __init__(
        self,
        timeout: Optional[float] = 60
    ):
        super().__init__(timeout=timeout)
        self.bot: Red = None
        self.author: discord.Member = None
        self.confirm_action: str = None
        self.message: discord.Message = None
        self.value = None
        
    async def start(self, context: commands.Context, confirmation_msg: str, confirm_action: str):
        msg = await context.send(content=confirmation_msg, view=self)
        self.confirm_action = confirm_action
        self.bot = context.bot
        self.author = context.author
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
        if await self.bot.is_owner(interaction.user):
            return True
        elif interaction.user.id != self.author.id:
            await interaction.response.send_message(content="You are not the author of this interaction.", ephemeral=True)
            return False
        return True
    
    async def on_timeout(self):
        for x in self.children:
            x.disabled = True
        self.stop()
        await self.message.edit(content="You took too long to respond.", view=self)
