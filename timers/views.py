import discord
import noobutils as nu

from redbot.core.bot import Red

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Timers


class TimersView(discord.ui.View):
    def __init__(self, cog: "Timers"):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(custom_id="notify_button_yeah_idk")
    async def notify_button(
        self, interaction: discord.Interaction[Red], button: discord.ui.Button
    ):
        await interaction.response.defer(ephemeral=True, thinking=True)
        conf = await self.cog.config.guild(interaction.guild).all()
        async with self.cog.config.guild(interaction.guild).timers() as timers:
            msg_id = timers[str(interaction.message.id)]
            if interaction.user.id == msg_id["host_id"]:
                return await interaction.followup.send(
                    content="You are the host you will be notified whenever this timer ends no matter what.",
                    ephemeral=True,
                )
            elif interaction.user.id in msg_id["members"]:
                msg_id["members"].remove(interaction.user.id)
                resp = "You will `no longer` be notified when this timer ends."
            else:
                msg_id["members"].append(interaction.user.id)
                resp = "You will now get notified when this timer ends."
            button.label = str(len(msg_id["members"]))
            button.emoji = conf["timer_emoji"]
            button.style = nu.get_button_colour(conf["time_button_colour"]["started"])
        await interaction.message.edit(view=self)
        await interaction.followup.send(content=resp)
