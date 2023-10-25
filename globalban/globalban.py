import asyncio
import contextlib
import discord
import logging
import noobutils as nu

from redbot.core.bot import commands, Config, modlog, Red
from redbot.core.utils import chat_formatting as cf

from datetime import datetime, timezone
from typing import Literal, Union

from .views import GbanViewReset


class GlobalBan(commands.Cog):
    """
    Globally ban a user from all the guilds the bot is in.
    """

    def __init__(self, bot: Red) -> None:
        self.bot = bot

        self.config = Config.get_conf(
            self, identifier=74654871231365754648, force_registration=True
        )
        default_global = {"banlist": [], "banlogs": [], "create_modlog": False}
        self.config.register_global(**default_global)
        self.log = logging.getLogger("red.NoobCogs.GlobalBan")

    __version__ = "1.1.11"
    __author__ = ["NoobInDaHause"]
    __docs__ = (
        "https://github.com/NoobInDaHause/NoobCogs/blob/red-3.5/globalban/README.md"
    )

    def format_help_for_context(self, context: commands.Context) -> str:
        """
        Thanks Sinbad and sravan!
        """
        plural = "s" if len(self.__author__) > 1 else ""
        return f"""{super().format_help_for_context(context)}

        Cog Version: **{self.__version__}**
        Cog Author{plural}: {cf.humanize_list([f'**{auth}**' for auth in self.__author__])}
        Cog Documentation: [[Click here]]({self.__docs__})"""

    async def red_delete_data_for_user(
        self,
        *,
        requester: Literal["discord_deleted_user", "owner", "user", "user_strict"],
        user_id: int,
    ):
        """
        This cog stores user id for the purpose of ban logs and ban list and some other.

        People can remove their data but offenders who are in the ban logs or list can't.
        """
        async with self.config.banlogs() as gblog:
            if not gblog:
                return
            for i in gblog:
                if user_id == i["authorizer"]:
                    i["authorizer"] = None
                if user_id == i["amender"]:
                    i["amender"] = None

    async def cog_load(self):
        await self.register_casetypes()

    @staticmethod
    async def register_casetypes():
        globalban_types = [
            {
                "name": "globalban",
                "default_setting": True,
                "image": ":earth_americas::hammer:",
                "case_str": "GlobalBan",
            },
            {
                "name": "globalunban",
                "default_setting": True,
                "image": ":earth_americas::dove:",
                "case_str": "GlobalUnBan",
            },
        ]
        with contextlib.suppress(RuntimeError):
            await modlog.register_casetypes(globalban_types)

    async def log_bans(
        self, context: commands.Context, gtype: str, user_id: int, reason: str
    ):
        async with self.config.banlogs() as gblog:
            log = {
                "case": len(gblog) + 1,
                "type": gtype,
                "offender": user_id,
                "authorizer": context.author.id,
                "reason": reason,
                "timestamp": round(datetime.now(timezone.utc).timestamp()),
                "last_modified": None,
                "amender": None,
            }
            gblog.append(log)

    async def _globalban_user(
        self, context: commands.Context, member: discord.Member, reason: str
    ):
        """
        Global ban the user.
        """
        await self.log_bans(context, "GlobalBan", member.id, reason)

        async with self.config.banlist() as gblist:
            gl: list = gblist
            gl.append(member.id)

        errors = []
        guilds = []
        for guild in self.bot.guilds:
            await asyncio.sleep(10)
            try:
                entry = await guild.fetch_ban(member)
                if entry:
                    errors.append(f"{guild} (ID: `{guild.id}`)")
            except discord.errors.NotFound:
                try:
                    res = f"GlobalBan Authorized by {context.author} (ID: {context.author.id}). Reason: {reason}"
                    await guild.ban(member, reason=res)
                    guilds.append(guild.id)
                    if await self.config.create_modlog():
                        await modlog.create_case(
                            bot=context.bot,
                            guild=guild,
                            created_at=datetime.now(timezone.utc),
                            action_type="globalban",
                            user=member,
                            moderator=context.bot.user,
                            reason=res,
                            until=None,
                            channel=None,
                        )
                except discord.errors.HTTPException:
                    errors.append(f"{guild} (ID: `{guild.id}`)")

        await context.send(
            content=f"Globally banned **{member}** in **{len(guilds)}** guilds."
        )
        self.log.info(
            f"{context.author} (ID: {context.author.id}) Globally Banned "
            f"{member} (ID: {member.id}) in {len(guilds)} guilds."
        )

        if errors:
            em = ", ".join(errors)
            final_page = await nu.pagify_this(
                em,
                ", ",
                "Page {index}/{pages}",
                embed_title=(
                    "It's either I do not have ban permission or "
                    f"{member} is already banned in these guilds."
                ),
                embed_colour=await context.embed_colour(),
            )

            paginator = nu.NoobPaginator(final_page, timeout=60.0)
            await paginator.start(context)

    async def _globalunban_user(
        self, context: commands.Context, member: discord.Member, reason: str
    ):
        """
        Global Unban a user.
        """
        await self.log_bans(context, "GlobalUnBan", member.id, reason)

        async with self.config.banlist() as gblist:
            gl: list = gblist
            index = gl.index(member.id)
            gl.pop(index)

        errors = []
        guilds = []
        for guild in self.bot.guilds:
            await asyncio.sleep(10)
            try:
                res = f"GlobalUnBan Authorized by {context.author} (ID: {context.author.id}). Reason: {reason}"
                await guild.unban(member, reason=res)
                guilds.append(guild.id)
                if await self.config.create_modlog():
                    await modlog.create_case(
                        bot=context.bot,
                        guild=guild,
                        created_at=datetime.now(timezone.utc),
                        action_type="globalunban",
                        user=member,
                        moderator=context.bot.user,
                        reason=res,
                        until=None,
                        channel=None,
                    )
            except discord.errors.HTTPException:
                errors.append(f"{guild} (ID: `{guild.id}`)")

        await context.send(
            content=f"Globally unbanned **{member}** in **{len(guilds)}** guilds."
        )
        self.log.info(
            f"{context.author} (ID: {context.author.id}) Globally UnBanned"
            f" {member} (ID: {member.id}) in {len(guilds)} guilds."
        )

        if errors:
            em = ", ".join(errors)
            final_page = await nu.pagify_this(
                em,
                ", ",
                "Page {index}/{pages}",
                embed_title=(
                    "It's either I do not have ban permission or "
                    f"{member} is not banned in these guilds."
                ),
                embed_colour=await context.embed_colour(),
            )

            paginator = nu.NoobPaginator(final_page, timeout=60.0)
            await paginator.start(context)

    @commands.group(name="globalban", aliases=["gban"])
    @commands.is_owner()
    @commands.bot_has_permissions(embed_links=True)
    async def globalban(self, context: commands.Context):
        """
        Base commands for the GlobalBan Cog.

        Bot owners only.
        """
        pass

    @globalban.command(name="editreason")
    async def globalban_editreason(
        self, context: commands.Context, case_id: int, *, reason: str
    ):
        """
        Edit a global ban case reason.

        Bot owners only.
        """
        await context.typing()
        async with self.config.banlogs() as gblog:
            if not gblog:
                return await context.send(
                    content="It appears there are no cases logged yet."
                )
            if case_id <= 0 or case_id > len(gblog):
                return await context.send(
                    content="It appears the case for this ID does not exist."
                )
            for i in gblog:
                if case_id == i["case"]:
                    i["reason"] = reason
                    i["amender"] = context.author.id
                    i["last_modified"] = round(discord.utils.utcnow().timestamp())
                    break
        await context.tick()

    @globalban.command(name="ban")
    async def globalban_ban(
        self,
        context: commands.Context,
        user: Union[discord.Member, int],
        *,
        reason: str = "No reason provided.",
    ):
        """
        Globally ban a user.

        Bot owners only.
        """
        if isinstance(user, int):
            try:
                member = await context.bot.get_or_fetch_user(user)
            except discord.errors.NotFound:
                return await context.send(
                    content=(
                        "I could not find a user with this ID. Perhaps the user was deleted or ID is invalid."
                    )
                )
        else:
            member = user

        if member.id in await self.config.banlist():
            return await context.send(
                content=f"It appears **{member}** is already globally banned."
            )
        if member.id == context.author.id:
            return await context.send(
                content="I can not let you globally ban yourself."
            )
        if await context.bot.is_owner(member):
            return await context.send(
                content="You can not globally ban other bot owners."
            )
        if member.id == context.bot.user.id:
            return await context.send(
                content="You can not globally ban me... Dumbass. >:V"
            )

        confirmation_msg = f"Are you sure you want to globally ban **{member}**?"
        confirm_action = "Alright this might take a while."
        view = nu.NoobConfirmation(timeout=30)
        await view.start(context, confirm_action, content=confirmation_msg)

        await view.wait()

        if view.value is True:
            await context.typing()
            await self._globalban_user(context=context, member=member, reason=reason)

    @globalban.command(name="createmodlog", aliases=["cml"])
    async def globalban_createmodlog(self, context: commands.Context, state: bool):
        """
        Toggle whether to make a modlog case when you globally ban or unban a user.

        Bot owners only.
        """
        await self.config.create_modlog.set(state)
        status = "will now" if state else "will not"
        await context.send(
            content=f"I {status} create a modlog case on guilds "
            "if a modlog is set whenever you globally ban or unban a user."
        )

    @globalban.command(name="list")
    async def globalban_list(self, context: commands.Context):
        """
        Show the globalban ban list.

        Bot owners only.
        """
        bans = await self.config.banlist()

        if not bans:
            return await context.send(content="No users were globally banned.")

        users = []
        for mem in bans:
            try:
                member = await context.bot.get_or_fetch_user(mem)
                l = f"` #{len(users) + 1} ` {member} (ID: {member.id})"
                users.append(l)
            except discord.errors.NotFound:
                l = f"` #{len(users) + 1} ` Unknown or Deleted User (ID: {mem})"
                users.append(l)

        banlist = "\n".join(users)
        final_page = await nu.pagify_this(
            banlist,
            "\n",
            "Page {index}/{pages}",
            embed_title="GlobalBan Ban List",
            embed_colour=await context.embed_colour(),
        )

        paginator = nu.NoobPaginator(final_page, timeout=60.0)
        await paginator.start(context)

    @globalban.command(name="logs")
    async def globalban_logs(self, context: commands.Context):
        """
        Show the globalban logs.

        Bot owners only.
        """
        logs = await self.config.banlogs()

        if not logs:
            return await context.send(
                content="It appears there are no cases logged yet."
            )

        gl = []
        for i in logs:
            try:
                m = await context.bot.get_or_fetch_user(i["offender"])
                off = f"{m} ({m.id})"
            except (discord.errors.NotFound, discord.errors.HTTPException):
                off = f"Unknown or Deleted User ({i['offender']})"
            try:
                a = await context.bot.get_or_fetch_user(i["authorizer"])
                aff = f"{a} ({a.id})"
            except (discord.errors.NotFound, discord.errors.HTTPException):
                aff = f"Unknown or Deleted User ({i['authorizer']})"
            if i["amender"]:
                try:
                    e = await context.bot.get_or_fetch_user(i["amender"])
                    eff = f"\n`Amended by:` {e} ({e.id})"
                except (discord.errors.NotFound, discord.errors.HTTPException):
                    eff = f"\n`Amended by:` Unknown or Deleted User ({i['amender']})"
            else:
                eff = ""
            if i["last_modified"]:
                ts = f"\n`Last modified:` <t:{i['last_modified']}:F>"
            else:
                ts = ""
            l = (
                f"> Globalban Logs Case `#{i['case']}`\n`Type:` {i['type']}\n`Offender:` {off}\n"
                f"`Authorized by:` {aff}\n`Reason:` {i['reason']}\n"
                f"`Timestamp:` <t:{i['timestamp']}:F>{eff}{ts}"
            )
            gl.append(l)

        banlogs = """\n\n""".join(gl)
        final_page = await nu.pagify_this(
            banlogs,
            "> ",
            "Page {index}/{pages}",
            embed_title="GlobalBan Ban Logs",
            embed_colour=await context.embed_colour(),
        )

        paginator = nu.NoobPaginator(final_page, timeout=60.0)
        await paginator.start(context)

    @globalban.command(name="reset")
    async def globalban_reset(self, context: commands.Context):
        """
        Reset any of the globalban config.

        Bot owners only.
        """
        msg = "Choose what config to reset."
        view = GbanViewReset(timeout=30)
        await view.start(context=context, msg=msg)

    @globalban.command(name="unban")
    async def globalban_unban(
        self,
        context: commands.Context,
        user: Union[discord.Member, int],
        *,
        reason: str = "No reason provided.",
    ):
        """
        Globally unban a user.

        Bot owners only.
        """
        if isinstance(user, int):
            try:
                member = await context.bot.get_or_fetch_user(user)
            except discord.errors.NotFound:
                return await context.send(
                    content=(
                        "I could not find a user with this ID. Perhaps the user was deleted or ID is invalid."
                    )
                )
        else:
            member = user

        if member.id not in await self.config.banlist():
            return await context.send(
                content=f"It appears **{member}** is not globally banned."
            )

        confirm_msg = f"Are you sure you want to globally unban **{member}**?"
        confirm_action = "Alright this might take a while."
        view = nu.NoobConfirmation(timeout=30.0)
        await view.start(context, confirm_action, content=confirm_msg)

        await view.wait()

        if view.value is True:
            await context.typing()
            await self._globalunban_user(context=context, member=member, reason=reason)
