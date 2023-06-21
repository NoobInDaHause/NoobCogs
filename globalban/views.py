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
        await self.message.edit(content="You took too long to respond.", view=self)

class GbanViewReset(discord.ui.View):
    def __init__(self, timeout: Optional[float] = 60.0):
        super().__init__(timeout=timeout)
        self.message: discord.Message = None
        self.context: commands.Context = None

    async def start(self, context: commands.Context, msg: str):
        msg = await context.send(content=msg, view=self)
        self.context = context
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
        for x in self.children:
            x.disabled = True
        await interaction.response.defer()
        await self.message.edit(content="Menu no longer available.", view=self)

        if select.values[0] == "List":
            confirm_msg = "Are you sure you want to reset the globalban banlist?"
            confirm_action = "Successfully resetted the globalban banlist."
            confview = Confirmation(timeout=30)
            await confview.start(
                context=self.context, confirmation_msg=confirm_msg, confirm_action=confirm_action
            )

            await confview.wait()

            if confview.value == "yes":
                await self.context.cog.config.banlist.clear()

        if select.values[0] == "Logs":
            confirm_msg = "Are you sure you want to reset the globalban banlogs?"
            confirm_action = "Successfully resetted the globalban banlogs."
            confview = Confirmation(timeout=30)
            await confview.start(
                context=self.context, confirmation_msg=confirm_msg, confirm_action=confirm_action
            )

            await confview.wait()

            if confview.value == "yes":
                await self.context.cog.banlogs.clear()

        if select.values[0] == "Cog":
            confirm_msg = "This will reset the globalban cogs whole configuration, do you want to continue?"
            confirm_action = "Successfully cleared the globalban cogs configuration."
            confview = Confirmation(timeout=30)
            await confview.start(
                context=self.context, confirmation_msg=confirm_msg, confirm_action=confirm_action
            )

            await confview.wait()

            if confview.value == "yes":
                await self.context.cog.config.clear_all()

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
