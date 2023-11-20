import discord

from redbot.core import commands

from noobutils import access_denied, NoobConfirmation


class GbanViewReset(discord.ui.View):
    def __init__(self, timeout: float = 60.0):
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
            discord.SelectOption(
                label="List", emoji="📰", description="Reset the cogs banlist config."
            ),
            discord.SelectOption(
                label="Logs", emoji="📜", description="Reset the cogs banlogs config."
            ),
            discord.SelectOption(
                label="Cog", emoji="⚙️", description="Reset the whole cogs config."
            ),
        ],
    )
    async def select_callback(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        for x in self.children:
            x.disabled = True
        await interaction.response.defer()
        await self.message.edit(content="Menu no longer available.", view=self)

        if select.values[0] == "List":
            confirm_msg = "Are you sure you want to reset the globalban banlist?"
            confirm_action = "Successfully resetted the globalban banlist."
            confview = NoobConfirmation(timeout=30)
            await confview.start(interaction, confirm_action, content=confirm_msg)

            await confview.wait()

            if confview.value:
                await self.context.cog.config.banlist.clear()

        if select.values[0] == "Logs":
            confirm_msg = "Are you sure you want to reset the globalban banlogs?"
            confirm_action = "Successfully resetted the globalban banlogs."
            confview = NoobConfirmation(timeout=30)
            await confview.start(
                interaction,
                confirm_action=confirm_action,
                content=confirm_msg
            )

            await confview.wait()

            if confview.value:
                await self.context.cog.banlogs.clear()

        if select.values[0] == "Cog":
            confirm_msg = "This will reset the globalban cogs whole configuration, do you want to continue?"
            confirm_action = "Successfully cleared the globalban cogs configuration."
            confview = NoobConfirmation(timeout=30)
            await confview.start(
                interaction,
                confirm_action=confirm_action,
                content=confirm_msg
            )

            await confview.wait()

            if confview.value:
                await self.context.cog.config.clear_all()

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
