import discord
import noobutils as nu

from redbot.core.bot import Red

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any, Union

from .utilities import FollowupItem, MessageEditItem

if TYPE_CHECKING:
    from . import Timers


class JoinButton(discord.ui.Button):
    def __init__(
        self,
        label: str,
        style: discord.ButtonStyle,
        emoji: Union[discord.Emoji, str],
        disabled: bool,
    ):
        super().__init__(
            label=label,
            style=style,
            emoji=emoji,
            custom_id="notify_button_yeah_idk",
            disabled=disabled,
        )

    async def callback(self, interaction: discord.Interaction[Red]) -> Any:
        view: "TimersView" = self.view
        conf = await view.cog.config.guild(interaction.guild).all()
        if timer := discord.utils.get(
            view.cog.active_timers, message_id=interaction.message.id
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
            self.emoji = conf["timer_emoji"]
            self.label = str(len(timer.members))
            self.style = nu.get_button_colour(conf["timer_button_colour"]["started"])
            await view.cog.to_config()
            priority = 1
            timeout = datetime.now(timezone.utc) + timedelta(minutes=15)
            view.cog.message_edit_queue.put_nowait(
                MessageEditItem(
                    timer.message_id,
                    priority,
                    timeout,
                    interaction.message.edit(view=view),
                )
            )
            view.cog.followup_queue.put_nowait(
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


class TimersView(discord.ui.View):
    def __init__(
        self,
        cog: "Timers",
        label: str = "0",
        emoji: Union[discord.Emoji, str] = "⏰",
        style: discord.ButtonStyle = nu.get_button_colour("green"),
        disabled: bool = False,
    ):
        super().__init__(timeout=None)
        self.cog = cog
        self.join_button = JoinButton(label, style, emoji, disabled)
        self.add_item(self.join_button)
