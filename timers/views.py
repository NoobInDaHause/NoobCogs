import discord
import noobutils as nu

from redbot.core.bot import Red

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

from .utilities import FollowupItem, MessageEditItem

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
        conf = await self.cog.config.guild(interaction.guild).all()
        if timer := discord.utils.get(
            self.cog.active_timers, message_id=interaction.message.id
        ):
            if timer.host.id == interaction.user.id:
                return await interaction.response.send_message(
                    content="You are the host you will be notified whenever this timer ends no matter what.",
                    ephemeral=True,
                )
            if timer.ended or timer.cancelled:
                return await interaction.response.send_message(
                    content="It seems this timer is already over.", ephemeral=True
                )
            await interaction.response.defer()
            if timer.add_member(interaction.user):
                message = "You will now get notified when this timer ends."
            elif timer.remove_member(interaction.user):
                message = "You will `no longer` be notified when this timer ends."
            button.emoji = conf["timer_emoji"]
            button.label = str(len(timer.members))
            button.style = nu.get_button_colour(conf["timer_button_colour"]["started"])
            await self.cog.to_config()
            priority = 1
            timeout = datetime.now(timezone.utc) + timedelta(minutes=15)
            self.cog.message_edit_queue.put_nowait(
                MessageEditItem(
                    timer.message_id,
                    priority,
                    timeout,
                    interaction.message.edit(view=self),
                )
            )
            self.cog.followup_queue.put_nowait(
                FollowupItem(
                    priority,
                    timeout,
                    interaction.followup.send(content=message, ephemeral=True),
                )
            )
        else:
            await interaction.response.send_message(
                content="It seems this timer does not exist in my database.",
                ephemeral=True,
            )
