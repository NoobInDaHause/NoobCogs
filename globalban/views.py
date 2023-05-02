import discord

from redbot.core import commands, Config
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
        
class GbanViewReset(discord.ui.View):
    def __init__(
        self,
        timeout: Optional[float] = 60,
    ):
        super().__init__(timeout=timeout)
        self.bot: Red = None
        self.author: discord.Member = None
        self.message: discord.Message = None
        self.context: commands.Context = None
        self.select_value = None
        
    async def start(self, context: commands.Context, msg: str):
        msg = await context.send(content=msg, view=self)
        self.context = context
        self.bot = context.bot
        self.author = context.author
        self.message = msg
    
    @discord.ui.select(
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="List", emoji="📰", description="Reset the cogs banlist config."),
            discord.SelectOption(label="Logs", emoji="📜", description="Reset the cogs banlogs config."),
            discord.SelectOption(label="Cog", emoji="⚙️", description="Reset the whole cogs config.")
        ]
    )
    
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        select.disabled = True
        await interaction.response.edit_message(content="Menu no longer available.", view=self)
        await interaction.response.defer()
        
        if select.values[0] == "List":
            confirm_msg = "Are you sure you want to reset the globalban banlist?"
            confirm_action = "Successfully resetted the globalban banlist."
            confview = Confirmation(timeout=30)
            await confview.start(context=self.context, confirmation_msg=confirm_msg, confirm_action=confirm_action)
            
            await confview.wait()
            
            if confview.value == "yes":
                self.select_value = "banlist"
        
        if select.values[0] == "Logs":
            confirm_msg = "Are you sure you want to reset the globalban banlogs?"
            confirm_action = "Successfully resetted the globalban banlogs."
            confview = Confirmation(timeout=30)
            await confview.start(context=self.context, confirmation_msg=confirm_msg, confirm_action=confirm_action)
            
            await confview.wait()
            
            if confview.value == "yes":
                self.select_value = "banlogs"
        
        if select.values[0] == "Cog":
            confirm_msg = "This will reset the globalban cogs whole configuration, do you want to continue?"
            confirm_action = "Successfully cleared the globalban cogs configuration."
            confview = Confirmation(timeout=30)
            await confview.start(context=self.context, confirmation_msg=confirm_msg, confirm_action=confirm_action)

            await confview.wait()
            
            if confview.value == "yes":
                self.select_value = "cog"
            
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
        await self.message.edit(view=self)