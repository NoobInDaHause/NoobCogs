import discord
import noobutils as nu

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Timers


class TimersView(discord.ui.View):
    def __init__(self, cog: "Timers"):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(
        style=nu.get_button_colour("green"), custom_id="notify_button_yeah_idk"
    )
    async def notify_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        async with self.cog.config.guild(interaction.guild).timers() as timers:
            msg_id = timers[str(interaction.message.id)]
            if interaction.user.id == msg_id["host_id"]:
                return await interaction.response.send_message(
                    content="You are the host you will be notified whenever this timer ends no matter what."
                )
            elif interaction.user.id in msg_id["members"]:
                msg_id["members"].remove(interaction.user.id)
                resp = "You will `no longer` be notified when this timer ends."
            else:
                msg_id["members"].append(interaction.user.id)
                resp = "You will now get notified when this timer ends."
            button.label = str(len(msg_id["members"]))
            button.emoji = await self.cog.config.guild(interaction.guild).timer_emoji()
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(content=resp, ephemeral=True)
