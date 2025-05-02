import noobutils as nu
import typing as t

if t.TYPE_CHECKING:
    from . import GlobalBan


class GbanViewReset(nu.NoobView):
    def __init__(
        self,
        obj: t.Union[nu.Context, nu.Interaction],
        timeout: float = 60.0,
    ):
        super().__init__(obj=obj, timeout=timeout)
        self.message: nu.discord.Message = None

    async def start(self, msg: str):
        self.message = await self.context.send(content=msg, view=self)

    @nu.discord.ui.select(
        min_values=1,
        max_values=1,
        options=[
            nu.discord.SelectOption(
                label="List", emoji="📰", description="Reset the cogs banlist config."
            ),
            nu.discord.SelectOption(
                label="Logs", emoji="📜", description="Reset the cogs banlogs config."
            ),
            nu.discord.SelectOption(
                label="Cog", emoji="⚙️", description="Reset the whole cogs config."
            ),
        ],
    )
    async def select_callback(
        self, interaction: nu.Interaction, select: nu.discord.ui.Select
    ):
        cog: "GlobalBan" = interaction.client.get_cog("GlobalBan")
        for x in self.children:
            x.disabled = True
        await interaction.response.defer()
        await self.message.edit(content="Menu no longer available.", view=self)

        if select.values[0] == "List":
            confirm_msg = "Are you sure you want to reset the globalban banlist?"
            confirm_action = "Successfully resetted the globalban banlist."

            confview = nu.NoobConfirmation(
                obj=interaction, confirm_action=confirm_action, timeout=30
            )
            await confview.start(content=confirm_msg)

            await confview.wait()

            if confview.value:
                await cog.config.banlist.clear()
        elif select.values[0] == "Logs":
            confirm_msg = "Are you sure you want to reset the globalban banlogs?"
            confirm_action = "Successfully resetted the globalban banlogs."

            confview = nu.NoobConfirmation(
                obj=interaction, confirm_action=confirm_action, timeout=30
            )
            await confview.start(content=confirm_msg)

            await confview.wait()

            if confview.value:
                await cog.config.banlogs.clear()
        else:
            confirm_msg = "This will reset the globalban cogs whole configuration, do you want to continue?"
            confirm_action = "Successfully cleared the globalban cogs configuration."

            confview = nu.NoobConfirmation(
                obj=interaction, confirm_action=confirm_action, timeout=30
            )
            await confview.start(content=confirm_msg)

            await confview.wait()

            if confview.value:
                await cog.config.clear_all()
