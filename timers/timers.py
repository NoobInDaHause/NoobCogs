import asyncio
import contextlib
import discord
import logging
import noobutils as nu

from redbot.core.bot import commands, Config, Red
from redbot.core.utils import chat_formatting as cf

from datetime import datetime, timezone
from discord.ext import tasks
from typing import Literal, List, TYPE_CHECKING, Union

from .objects import TimerObject
from .views import TimersView

if TYPE_CHECKING:
    from .utilities import FollowupItem, MessageEditItem


class Timers(commands.Cog):
    """
    Start a timer countdown.

    All purpose timer countdown.
    """

    def __init__(self, bot: Red, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.bot = bot

        self.config = Config.get_conf(
            self, identifier=65466546, force_registration=True
        )
        default_guild = {
            "timer_button_colour": {"ended": "grey", "started": "green"},
            "notify_members": True,
            "timer_emoji": "⏰",
            "auto_delete": False,
        }
        default_global = {"maximum_duration": 1209600}
        self.config.register_guild(**default_guild)
        self.config.register_global(**default_global)
        self.config.init_custom("TIMERS", 1)
        self.log = logging.getLogger("red.NoobCogs.Timers")
        self.running = True
        self.active_timers: List[TimerObject] = []
        self.folloup_queue_task = asyncio.create_task(self.followup_runner())
        self.message_edit_queue_task = asyncio.create_task(self.message_edit_runner())
        self.followup_queue: asyncio.Queue[FollowupItem] = asyncio.Queue()
        self.message_edit_queue: asyncio.Queue[MessageEditItem] = asyncio.Queue()
        self.view = TimersView(self)
        bot.add_view(self.view)

    __version__ = "2.2.0"
    __author__ = ["NoobInDaHause"]
    __docs__ = "https://github.com/NoobInDaHause/NoobCogs/blob/red-3.5/timers/README.md"

    def format_help_for_context(self, context: commands.Context) -> str:
        plural = "s" if len(self.__author__) > 1 else ""
        return (
            f"{super().format_help_for_context(context)}\n\n"
            f"Cog Version: **{self.__version__}**\n"
            f"Cog Author{plural}: {cf.humanize_list([f'**{auth}**' for auth in self.__author__])}\n"
            f"Cog Documentation: [[Click here]]({self.__docs__})\n"
            f"Utils Version: **{nu.__version__}**"
        )

    async def red_delete_data_for_user(
        self,
        *,
        requester: Literal["discord_deleted_user", "owner", "user", "user_strict"],
        user_id: int,
    ) -> None:
        """
        This cog stores user ID's for timer host and users who get notified when timer ends if enabled.

        Users can delete their data at any time.
        """
        for t in self.active_timers.copy():
            if timer := discord.utils.get(self.active_timers, message_id=t.message_id):
                if timer.host_id == user_id:
                    timer.host_id = None
                if user_id in timer._members:
                    timer._members.remove(user_id)
            await self.to_config()

    async def cog_load(self) -> None:
        self.bot.add_dev_env_value("timers", lambda _: self)
        if old_data := (await self.config.custom("TIMERS").all()).copy():
            for message_id, timer_data in old_data.items():
                timer = TimerObject.from_dict(self, int(message_id), timer_data)
                self.add_timer(timer)
            self.log.debug("Timer data initialized.")
        await self.initialize()

    async def cog_unload(self) -> None:
        self.running = False
        self.view.stop()
        self.bot.remove_dev_env_value("timers")
        await self.to_config()
        self.timer_ending_loop.cancel()
        self.save_timers_loop.cancel()
        self.log.info("Timer ending and timer saving loop task cancelled.")

    async def initialize(self):
        self.timer_ending_loop.start()
        self.save_timers_loop.start()
        self.log.info("Timer ending and timer saving loop task started.")

    async def followup_runner(self):
        while self.running:
            item = await self.followup_queue.get()
            if not item.is_valid():
                item.coro.close()
                self.followup_queue.task_done()
                del item
                continue
            coro = item.coro
            try:
                await coro
                await asyncio.sleep(0.5)
            except discord.errors.HTTPException as e:
                await asyncio.sleep(e.response.headers.get("Retry-After", 20))
                await coro
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.log.exception("Error sending followup: ", exc_info=e)
            del item
            self.followup_queue.task_done()

    async def message_edit_runner(self):
        while self.running:
            item = await self.message_edit_queue.get()
            if not item.is_valid():
                item.coro.close()
                self.message_edit_queue.task_done()
                del item
                continue
            if timer := discord.utils.get(self.active_timers, message_id=item.timer_id):
                if timer.ended or timer.cancelled:
                    item.coro.close()
                    self.message_edit_queue.task_done()
                    del item
                    continue
            else:
                item.coro.close()
                self.message_edit_queue.task_done()
                del item
                continue
            coro = item.coro
            try:
                await coro
                await asyncio.sleep(0.5)
            except discord.errors.HTTPException as e:
                await asyncio.sleep(e.response.headers.get("Retry-After", 20))
                await coro
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.log.exception("Error editing message: ", exc_info=e)
            del item
            self.message_edit_queue.task_done()

    async def to_config(self):
        if not self.active_timers:
            await self.config.custom("TIMERS").clear()
            return
        new_data = {}
        for timer in self.active_timers.copy():
            timer_data = timer.to_dict()
            new_data |= timer_data
        await self.config.custom("TIMERS").set(new_data)

    def add_timer(self, timer: TimerObject) -> bool:
        if discord.utils.get(self.active_timers, message_id=timer.message_id):
            return False
        self.active_timers.append(timer)
        return True

    def remove_timer(self, timer: TimerObject) -> bool:
        if t := discord.utils.get(self.active_timers, message_id=timer.message_id):
            index = self.active_timers.index(t)
            self.active_timers.pop(index)
            return True
        return False

    async def get_timers(
        self, context: commands.Context, _all: bool
    ) -> List[discord.Embed]:
        timers = []
        if _all:
            timers.extend(
                (
                    f"**{index}.** {timer.title}\n` - ` Message ID: {timer.message_id}\n"
                    f"` - ` Guild: {timer.guild} (`{timer.guild_id}`)\n"
                    f"` - ` Jump URL: [[HERE]]({timer.jump_url})\n"
                    f"` - ` Host: {timer.host} (`{timer.host_id}`)\n"
                    f"` - ` Channel: {timer.channel} (`{timer.channel_id}`)\n"
                    f"` - ` Ends: <t:{timer.end_timestamp}:R> (<t:{timer.end_timestamp}:F>)"
                )
                for index, timer in enumerate(self.active_timers.copy(), 1)
            )
        else:
            guild_timers = list(
                filter(
                    lambda x: x.guild_id == context.guild.id, self.active_timers.copy()
                )
            )
            timers.extend(
                (
                    f"**{index}.** {timer.title}\n` - ` Message ID: {timer.message_id}\n"
                    f"` - ` Jump URL: [[HERE]]({timer.jump_url})\n"
                    f"` - ` Host: {timer.host} (`{timer.host_id}`)\n"
                    f"` - ` Channel: {timer.channel} (`{timer.channel_id}`)\n"
                    f"` - ` Ends: <t:{timer.end_timestamp}:R> (<t:{timer.end_timestamp}:F>)"
                )
                for index, timer in enumerate(guild_timers, 1)
            )
        no_timers = (
            ["There are no active timers globally."]
            if _all
            else ["There are no active timers in this guild."]
        )
        bot = context.guild.get_member(context.bot.user.id)
        title = (
            "List of active timers globally."
            if _all
            else f"List of active timers in [{context.guild.name}]"
        )
        return await nu.pagify_this(
            "\n".join(timers or no_timers),
            "\n",
            embed_colour=self.bot._color,
            embed_title=title,
            embed_thumbnail=nu.is_have_avatar(bot)
            if _all
            else nu.is_have_avatar(context.guild),
        )

    @tasks.loop(seconds=5)
    async def timer_ending_loop(self):
        if not self.running:
            return
        for t in self.active_timers.copy():
            if timer := discord.utils.get(self.active_timers, message_id=t.message_id):
                if timer.ended or timer.cancelled:
                    continue
                if timer.ends_at < datetime.now(timezone.utc):
                    if not timer.guild:
                        self.remove_timer(timer)
                        continue
                    await timer.end()

    @tasks.loop(minutes=5)
    async def save_timers_loop(self):
        if not self.running:
            return
        await self.to_config()

    @timer_ending_loop.before_loop
    @save_timers_loop.before_loop
    async def before_loop(self):
        await self.bot.wait_until_red_ready()

    @commands.Cog.listener("on_raw_message_delete")
    @commands.Cog.listener("on_raw_bulk_message_delete")
    async def message_delete_handler(
        self,
        payload: Union[
            discord.RawMessageDeleteEvent, discord.RawBulkMessageDeleteEvent
        ],
    ):
        if not payload.guild_id:
            return

        try:
            if isinstance(payload, discord.RawMessageDeleteEvent):
                msg_ids = [payload.message_id]
            else:
                msg_ids = payload.message_ids

            for msg_id in msg_ids:
                if timer := discord.utils.get(self.active_timers, message_id=msg_id):
                    self.remove_timer(timer)
            await self.to_config()
        except Exception as e:
            self.log.exception(
                "Error occurred while handling message delete event.", exc_info=e
            )

    @commands.group(name="timer", invoke_without_command=True)
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True, manage_messages=True)
    @commands.mod_or_permissions(manage_messages=True)
    async def timer(
        self,
        context: commands.Context,
        duration: commands.TimedeltaConverter,
        *,
        title: str = "New Timer!",
    ):
        """
        Timer.
        """
        _max = await self.config.maximum_duration()
        autodel = await self.config.guild(context.guild).auto_delete()
        if int(duration.total_seconds()) > _max:
            return await context.send(
                content=f"Max duration for timers is: **{cf.humanize_timedelta(seconds=_max)}**."
            )
        if int(duration.total_seconds()) < 10:
            return await context.send(
                content="Duration must be greater than **10 Seconds**."
            )
        if len(title) > 256:
            return await context.send(
                content="Your timer title should be less than 256 characters due to embed limits."
            )
        timer_data = {
            "cog": self,
            "guild_id": context.guild.id,
            "host_id": context.author.id,
            "channel_id": context.channel.id,
            "end_timestamp": round((datetime.now(timezone.utc) + duration).timestamp()),
            "title": title,
        }
        timer = TimerObject(**timer_data)
        await timer.start()
        if autodel:
            with contextlib.suppress(Exception):
                await context.message.delete()

    @timer.command(name="end")
    async def timer_end(
        self, context: commands.Context, message: discord.Message = None
    ):
        """
        Manually end a timer.
        """
        autodel = await self.config.guild(context.guild).auto_delete()
        if not message and not context.message.reference:
            return await context.send_help()
        msg_id = message.id if message else context.message.reference.resolved.id
        if timer := discord.utils.get(self.active_timers, message_id=msg_id):
            if timer.cancelled:
                return await context.send(content="This timer was cancelled.")
            if timer.ended:
                return await context.send(content="This timer has already ended.")
            if autodel:
                with contextlib.suppress(Exception):
                    await context.message.delete()
            await timer.end(context.author)
        else:
            await context.send(
                content="That does not seem to be a valid timer or it was already over."
            )

    @timer.command(name="cancel")
    async def timer_cancel(
        self, context: commands.Context, message: discord.Message = None
    ):
        """
        Cancel a timer.
        """
        autodel = await self.config.guild(context.guild).auto_delete()
        if not message and not context.message.reference:
            return await context.send_help()
        msg_id = message.id if message else context.message.reference.resolved.id
        if timer := discord.utils.get(self.active_timers, message_id=msg_id):
            if timer.cancelled:
                return await context.send(content="This timer was already cancelled.")
            if timer.ended:
                return await context.send(content="This timer has ended.")
            if autodel:
                with contextlib.suppress(Exception):
                    await context.message.delete()
            await timer.cancel(context.author)
        else:
            await context.send(
                content="That does not seem to be a valid timer or it was already over."
            )

    @timer.command(name="list", usage="")
    async def timer_list(self, context: commands.Context, _all: bool = False):
        """
        See all the active timers in this guild.
        """
        if _all and not await context.bot.is_owner(context.author):
            embeds = await self.get_timers(context, False)
        elif _all and await context.bot.is_owner(context.author):
            embeds = await self.get_timers(context, True)
        else:
            embeds = await self.get_timers(context, False)
        await nu.NoobPaginator(embeds).start(context)

    @commands.group(name="timerset")
    @commands.admin_or_permissions(manage_guild=True)
    @commands.bot_has_permissions(embed_links=True)
    @commands.guild_only()
    async def timerset(self, context: commands.Context):
        """
        Configure timer settings.
        """
        pass

    @timerset.command(name="buttoncolour", aliases=["buttoncolor"])
    async def timerset_buttoncolour(
        self,
        context: commands.Context,
        button_type: Literal["ended", "started"],
        colour_type: Literal["green", "grey", "blurple", "red", "reset"] = None,
    ):
        """
        Change the timer ended or started button colour.

        Pass without colour to check current set colour.
        Pass `reset` in colour to reset.
        """
        if button_type == "started":
            if not colour_type:
                col = await self.config.guild(
                    context.guild
                ).timer_button_colour.started()
                return await context.send(
                    content=f"Your current timer started button colour is: {col}"
                )
            if colour_type == "reset":
                await self.config.guild(
                    context.guild
                ).timer_button_colour.started.clear()
                return await context.send(
                    content="The timer started button colour has been reset."
                )
            await self.config.guild(context.guild).timer_button_colour.started.set(
                colour_type
            )
            await context.send(
                content=f"The timer started button colour has been set to: {colour_type}"
            )
        else:
            if not colour_type:
                col = await self.config.guild(context.guild).timer_button_colour.ended()
                return await context.send(
                    content=f"Your current timer ended button colour is: {col}"
                )
            if colour_type == "reset":
                await self.config.guild(context.guild).timer_button_colour.ended.clear()
                return await context.send(
                    content="The timer ended button colour has been reset."
                )
            await self.config.guild(context.guild).timer_button_colour.ended.set(
                colour_type
            )
            await context.send(
                content=f"The timer endeded button colour has been set to: {colour_type}"
            )

    @timerset.command(name="emoji")
    async def timerset_emoji(
        self, context: commands.Context, emoji: nu.NoobEmojiConverter = None
    ):
        """
        Change or reset the timer emoji.
        """
        if not emoji:
            await self.config.guild(context.guild).timer_emoji.clear()
            return await context.send(content="The timer emoji has been reset.")
        await self.config.guild(context.guild).timer_emoji.set(str(emoji))
        await context.send(content=f"Set {str(emoji)} as the timer emoji.")

    @timerset.command(name="notifymembers")
    async def timerset_notifymembers(self, context: commands.Context):
        """
        Toggle whether to notify members when the timer ends or not.
        """
        current = await self.config.guild(context.guild).notify_members()
        await self.config.guild(context.guild).notify_members.set(not current)
        status = "will no longer" if current else "will now"
        await context.send(content=f"I {status} notify members whenever a timer ends.")

    @timerset.command(name="maxduration", aliases=["md"])
    @commands.is_owner()
    async def timerset_maxduration(
        self, context: commands.Context, maxduration: commands.TimedeltaConverter
    ):
        """
        Set the maximum duration a timer can countdown.
        """
        md = int(maxduration.total_seconds())
        if md < 10 or md > (14 * 86400):
            return await context.send(
                content="The max duration time must be greater than 10 seconds or less than 14 days."
            )
        await self.config.maximum_duration.set(md)
        await context.send(
            content=f"The maximum duration is now: **{cf.humanize_timedelta(timedelta=maxduration)}**"
        )

    @timerset.command(name="autodelete", aliases=["autodel"])
    async def timerset_autodelete(self, context: commands.Context):
        """
        Toggle auto deletion on timer command completion.
        """
        current = await self.config.guild(context.guild).auto_delete()
        await self.config.guild(context.guild).auto_delete.set(not current)
        state = "will no longer" if current else "will now"
        await context.send(
            content=f"I {state} automatically delete timer commands invocation."
        )

    @timerset.command(name="resetguild")
    async def timerset_resetguild(self, context: commands.Context):
        """
        Reset this guild's timer settings.
        """
        act = "This guilds timer settings has been cleared."
        conf = "Are you sure you want to clear this guilds timer settings?"
        view = nu.NoobConfirmation()
        await view.start(context, act, content=conf)
        await view.wait()
        if view.value:
            await self.config.guild(context.guild).clear()
            for timer in self.active_timers.copy():
                if timer.guild_id == context.guild.id:
                    self.remove_timer(timer)
            await self.to_config()

    @timerset.command(name="resetcog")
    @commands.is_owner()
    async def timerset_resetcog(self, context: commands.Context):
        """
        Reset this cogs whole config.
        """
        act = "This cogs config has been cleared."
        conf = "Are you sure you want to clear this cogs config?"
        view = nu.NoobConfirmation()
        await view.start(context, act, content=conf)
        await view.wait()
        if view.value:
            self.active_timers.clear()
            await self.config.clear_all_guilds()
            await self.config.clear_all()
            await self.config.clear_all_custom("TIMERS")

    @timerset.command(name="showsettings", aliases=["ss"])
    async def timerset_showsettings(self, context: commands.Context):
        """
        Show current timer settings.
        """
        config = await self.config.guild(context.guild).all()
        ended = config["timer_button_colour"]["ended"]
        started = config["timer_button_colour"]["started"]
        autodel = config["auto_delete"]
        md = await self.config.maximum_duration()
        c = (
            f"Max Duration: **{cf.humanize_timedelta(seconds=md)}**"
            if await context.bot.is_owner(context.author)
            else ""
        )
        embed = discord.Embed(
            title=f"Timer settings for [{context.guild.name}]",
            description=f"Notify Members: {config['notify_members']}\n"
            f"Timer Emoji: {config['timer_emoji']}\nTimer Button Colour:\n` - ` Ended: {ended}\n"
            f"` - ` Started: {started}\nAuto Delete: {autodel}\n{c}",
            timestamp=datetime.now(timezone.utc),
            colour=await context.embed_colour(),
        )
        await context.send(embed=embed)
