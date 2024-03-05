import asyncio
import discord
import noobutils as nu

from redbot.core.utils import chat_formatting as cf

from datetime import datetime, timezone
from typing import List, Optional, Self, TYPE_CHECKING, Union

from .views import TimersView

if TYPE_CHECKING:
    from . import Timers


class TimerObject:
    def __init__(self, **payload) -> None:
        self.cog: "Timers" = payload.get("cog", None)
        self.guild_id: int = payload.get("guild_id", None)
        self.message_id: int = payload.get("message_id", None)
        self.host_id: int = payload.get("host_id", None)
        self.channel_id: int = payload.get("channel_id", None)
        self.end_timestamp: int = payload.get("end_timestamp", None)
        self.title: str = payload.get("title", None)
        self.ended: bool = payload.get("ended", False)
        self.cancelled: bool = payload.get("cancelled", False)
        self._members: List[int] = payload.get("members", [])

    async def timer_embed_msg(
        self, emoji: str, responsible: discord.Member = None
    ) -> discord.Embed:
        h = (
            self.host.mention
            if self.host
            else f"[Host not found in guild] ({self.host_id})"
        )
        if self.cancelled:
            desc = f"This timer was cancelled.\nHosted by: {h}"
            if responsible:
                desc += f"\nCancelled by: {responsible.mention}"
        elif self.ended:
            desc = f"This timer has ended.\nHosted by: {h}"
            if responsible:
                desc += f"\nEnded early by: {responsible.mention}"
        else:
            m = (
                f"Click the {emoji} button to get notified when this timer ends.\n"
                if await self.cog.config.guild(self.guild).notify_members()
                else ""
            )
            desc = f"{m}Time left: <t:{self.end_timestamp}:R> (<t:{self.end_timestamp}:F>)\nHosted by: {h}"
        embed = discord.Embed(
            title=self.title,
            description=desc,
            colour=discord.Colour.red()
            if self.cancelled
            else 0x2F3136
            if self.ended
            else self.cog.bot._color,
            timestamp=datetime.now(timezone.utc)
            if self.ended
            else datetime.fromtimestamp(self.end_timestamp, timezone.utc),
        )
        embed.set_footer(
            text="Cancelled at"
            if self.cancelled
            else "Ended at"
            if self.ended
            else "Ends at"
        )
        embed.set_thumbnail(url=nu.is_have_avatar(self.guild))
        return embed

    async def get_message(self) -> Optional[discord.Message]:
        try:
            return await self.channel.fetch_message(self.message_id)
        except discord.errors.NotFound:
            return None

    async def start(self) -> None:
        self.ended = False
        self.cancelled = False
        emoji = await self.cog.config.guild(self.guild).timer_emoji()
        notif = await self.cog.config.guild(self.guild).notify_members()
        started = await self.cog.config.guild(self.guild).timer_button_colour.started()
        embed = await self.timer_embed_msg(emoji)
        view = TimersView(
            self.cog,
            "0" if notif else "Disabled",
            emoji,
            nu.get_button_colour(started),
            not notif
        )
        msg = await self.channel.send(embed=embed, view=view)
        view.stop()
        self.message_id = msg.id
        self.cog.add_timer(self)
        await self.cog.to_config()

    async def cancel(self, responsible: discord.Member = None) -> None:
        self.ended = True
        self.cancelled = True
        emoji = await self.cog.config.guild(self.guild).timer_emoji()
        end = await self.cog.config.guild(self.guild).timer_button_colour.ended()
        if message := await self.get_message():
            embed = await self.timer_embed_msg(emoji, responsible)
            cancel_view = discord.ui.View().add_item(
                discord.ui.Button(
                    emoji=emoji,
                    disabled=True,
                    style=nu.get_button_colour(end),
                    label=str(len(self.members)),
                )
            )
            await message.edit(embed=embed, view=cancel_view)
        self.cog.remove_timer(self)
        await self.cog.to_config()

    async def end(self, responsible: discord.Member = None) -> None:
        self.ended = True
        self.cancelled = False
        emoji = await self.cog.config.guild(self.guild).timer_emoji()
        notif = await self.cog.config.guild(self.guild).notify_members()
        end = await self.cog.config.guild(self.guild).timer_button_colour.ended()
        try:
            if message := await self.get_message():
                members = [self.host] + self.members if self.host else self.members
                members_to_notify = [member.mention for member in members]
                member_length = len(members_to_notify)
                end_view = discord.ui.View().add_item(
                    discord.ui.Button(
                        label=str(member_length - 1)  # minus host
                        if self.host
                        else str(member_length),
                        emoji=emoji,
                        disabled=True,
                        style=nu.get_button_colour(end),
                    )
                )
                embed = await self.timer_embed_msg(emoji, responsible)
                await message.edit(embed=embed, view=end_view)
                if notif:
                    c = ",".join(members_to_notify)
                    for page in cf.pagify(c, delims=[","], page_length=1900):
                        await asyncio.sleep(0.5)
                        await self.channel.send(page, delete_after=3)
                else:
                    await self.channel.send(content=self.host.mention, delete_after=3)
                jump_view = discord.ui.View().add_item(
                    discord.ui.Button(label="Jump To Timer", url=self.jump_url)
                )
                await message.reply(
                    content=f"The timer for **{self.title}** has ended!",
                    view=jump_view,
                    allowed_mentions=discord.AllowedMentions.none(),
                )
            self.cog.remove_timer(self)
            await self.cog.to_config()
        except Exception as e:
            self.cog.log.exception(
                f"Error ending timer with message ID: {self.message_id}", exc_info=e
            )

    @property
    def guild(self) -> Optional[discord.Guild]:
        return self.cog.bot.get_guild(self.guild_id)

    @property
    def host(self) -> Optional[discord.Member]:
        return self.guild.get_member(self.host_id)

    @property
    def channel(
        self,
    ) -> Optional[Union[discord.TextChannel, discord.VoiceChannel, discord.Thread]]:
        return self.guild.get_channel_or_thread(self.channel_id)

    @property
    def ends_at(self) -> datetime:
        return datetime.fromtimestamp(self.end_timestamp, timezone.utc)

    @property
    def members(self) -> List[discord.Member]:
        return [member for i in self._members if (member := self.guild.get_member(i))]

    @property
    def jump_url(self) -> str:
        return f"https://discord.com/channels/{self.guild_id}/{self.channel_id}/{self.message_id}"

    def __str__(self) -> str:
        return (
            f"<guild_id={self.guild_id}> <channel_id={self.channel_id}> <message_id={self.message_id}> "
            f"<host_id={self.host_id}> <title={self.title}> <end_timestamp={self.end_timestamp}> "
            f"<ended={self.ended}> <cancelled={self.cancelled}>"
        )

    def add_member(self, member: discord.Member) -> bool:
        if member.id in self._members:
            return False
        self._members.append(member.id)
        return True

    def remove_member(self, member: discord.Member) -> bool:
        if member.id not in self._members:
            return False
        self._members.remove(member.id)
        return True

    @classmethod
    def from_dict(cls, cog: "Timers", message_id: int, timer_dict: dict) -> Self:
        timer_dict |= {
            "cog": cog,
            "message_id": message_id,
        }
        return cls(**timer_dict)

    def to_dict(self) -> dict:
        return {
            str(self.message_id): {
                "guild_id": self.guild_id,
                "host_id": self.host_id,
                "channel_id": self.channel_id,
                "end_timestamp": self.end_timestamp,
                "title": self.title,
                "members": self._members,
                "ended": self.ended,
                "cancelled": self.cancelled,
            }
        }
