import asyncio
import contextlib
import noobutils as nu
import typing as t

from redbot.core import modlog

from .views import GbanViewReset


DEFAULT_GLOBAL = {
    "banlist": [],
    "banlogs": {},
    "create_modlog": False,
    "next_id": 1,
}


class GlobalBan(nu.Cog):
    """
    Globally ban a user from all the guilds the bot is in.
    """

    __version__ = "1.3.5"
    __authors__ = ["NoobInDaHause"]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            bot=kwargs.pop("bot"),
            use_config=True,
            force_registration=True,
            *args,
            **kwargs,
        )
        self.config.register_global(**DEFAULT_GLOBAL)

    async def red_delete_data_for_user(
        self,
        *,
        requester: t.Literal["discord_deleted_user", "owner", "user", "user_strict"],
        user_id: int,
    ):
        """
        This cog stores user id for the purpose of ban logs and ban list and some other.

        People can remove their data but offenders who are in the ban logs or list can't.
        """
        async with self.config.banlogs() as gblog:
            if not gblog:
                return
            for v in gblog.values():
                if user_id == v["authorizer"]:
                    v["authorizer"] = None
                if user_id == v["amender"]:
                    v["amender"] = None

    async def cog_load(self):
        await super().cog_load()
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
        self, context: nu.Context, gtype: str, user_id: int, reason: str
    ):
        nid = await self.config.next_id()
        await self.config.next_id.set(nid + 1)
        async with self.config.banlogs() as gblog:
            gblog.setdefault(str(nid), {})
            gblog[str(nid)] |= {
                "offender": user_id,
                "type": gtype,
                "authorizer": context.author.id,
                "reason": reason,
                "timestamp": round(nu.discord.utils.utcnow().timestamp()),
                "last_modified": None,
                "amender": None,
            }

    async def _globalban_user(
        self, context: nu.Context, member: nu.discord.Member, reason: str
    ):
        """
        Global ban the user.
        """
        await self.log_bans(context, "GlobalBan", member.id, reason)

        async with self.config.banlist() as gblist:
            gblist.append(member.id)

        errors = []
        guilds = []
        for guild in self.bot.guilds:
            await asyncio.sleep(5.0)
            try:
                if await guild.fetch_ban(member):
                    errors.append(f"{guild} (ID: `{guild.id}`)")
            except nu.discord.errors.NotFound:
                try:
                    res = f"GlobalBan Authorized by {context.author} (ID: {context.author.id}). Reason: {reason}"
                    await guild.ban(member, reason=res)
                    guilds.append(guild.id)
                    if await self.config.create_modlog():
                        await modlog.create_case(
                            bot=context.bot,
                            guild=guild,
                            created_at=nu.discord.utils.utcnow(),
                            action_type="globalban",
                            user=member,
                            moderator=context.bot.user,
                            reason=res,
                            until=None,
                            channel=None,
                        )
                except nu.discord.errors.HTTPException:
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
            final_page = nu.pagify_this(
                em,
                [", "],
                "Page {index}/{pages}",
                embed_title=(
                    "It's either I do not have ban permission or "
                    f"{member} is already banned in these guilds."
                ),
                embed_colour=await context.embed_colour(),
            )

            await nu.NoobPaginator(obj=context, pages=final_page).start()

    async def _globalunban_user(
        self, context: nu.Context, member: nu.discord.Member, reason: str
    ):
        """
        Global Unban a user.
        """
        await self.log_bans(context, "GlobalUnBan", member.id, reason)

        async with self.config.banlist() as gblist:
            gblist.remove(member.id)

        errors = []
        guilds = []
        for guild in self.bot.guilds:
            await asyncio.sleep(5)
            try:
                res = f"GlobalUnBan Authorized by {context.author} (ID: {context.author.id}). Reason: {reason}"
                await guild.unban(member, reason=res)
                guilds.append(guild.id)
                if await self.config.create_modlog():
                    await modlog.create_case(
                        bot=context.bot,
                        guild=guild,
                        created_at=nu.discord.utils.utcnow(),
                        action_type="globalunban",
                        user=member,
                        moderator=context.bot.user,
                        reason=res,
                        until=None,
                        channel=None,
                    )
            except nu.discord.errors.HTTPException:
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
            final_page = nu.pagify_this(
                em,
                [", "],
                "Page {index}/{pages}",
                embed_title=(
                    "It's either I do not have ban permission or "
                    f"{member} is not banned in these guilds."
                ),
                embed_colour=await context.embed_colour(),
            )
            await nu.NoobPaginator(obj=context, pages=final_page, timeout=60).start()

    @nu.group(name="globalban", aliases=["gban"])
    @nu.commands.is_owner()
    @nu.commands.bot_has_permissions(embed_links=True)
    async def globalban(self, context: nu.Context):
        """
        Base commands for the GlobalBan Cog.

        Bot owners only.
        """
        pass

    @globalban.command(name="editreason")
    async def globalban_editreason(
        self, context: nu.Context, case_id: int, *, reason: str
    ):
        """
        Edit a global ban case reason.

        Bot owners only.
        """
        nid = await self.config.next_id()
        async with context.typing():
            async with self.config.banlogs() as gblog:
                if not gblog:
                    return await context.send(
                        content="It appears there are no cases logged yet."
                    )
                if case_id <= 0 or case_id > (nid - 1):
                    return await context.send(
                        content="It appears the case for this ID does not exist."
                    )
                gblog[str(case_id)]["reason"] = reason
                gblog[str(case_id)]["amender"] = context.author.id
                gblog[str(case_id)]["last_modified"] = round(
                    nu.discord.utils.utcnow().timestamp()
                )

            await context.tick()

    @globalban.command(name="ban")
    async def globalban_ban(
        self,
        context: nu.Context,
        user: t.Union[nu.discord.Member, int],
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
            except nu.discord.errors.NotFound:
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

        view = nu.NoobConfirmation(
            obj=context, confirm_action=confirm_action, timeout=30
        )
        await view.start(content=confirmation_msg)

        await view.wait()

        if view.value:
            await context.typing()
            await self._globalban_user(context=context, member=member, reason=reason)

    @globalban.command(name="createmodlog", aliases=["cml"])
    async def globalban_createmodlog(self, context: nu.Context, state: bool):
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
    async def globalban_list(self, context: nu.Context):
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
            except nu.discord.errors.NotFound:
                l = f"` #{len(users) + 1} ` Unknown or Deleted User (ID: {mem})"
                users.append(l)

        banlist = "\n".join(users)
        final_page = nu.pagify_this(
            banlist,
            ["\n"],
            "Page {index}/{pages}",
            embed_title="GlobalBan Ban List",
            embed_colour=await context.embed_colour(),
        )

        await nu.NoobPaginator(obj=context, pages=final_page).start()

    @globalban.command(name="logs")
    async def globalban_logs(self, context: nu.Context):
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
        for k, v in logs.items():
            try:
                m = await context.bot.get_or_fetch_user(v["offender"])
                off = f"{m} ({m.id})"
            except (nu.discord.errors.NotFound, nu.discord.errors.HTTPException):
                off = f"Unknown or Deleted User ({v['offender']})"
            try:
                a = await context.bot.get_or_fetch_user(v["authorizer"])
                aff = f"{a} ({a.id})"
            except (nu.discord.errors.NotFound, nu.discord.errors.HTTPException):
                aff = f"Unknown or Deleted User ({v['authorizer']})"
            if v["amender"]:
                try:
                    e = await context.bot.get_or_fetch_user(v["amender"])
                    eff = f"\n`Amended by:` {e} ({e.id})"
                except (nu.discord.errors.NotFound, nu.discord.errors.HTTPException):
                    eff = f"\n`Amended by:` Unknown or Deleted User ({v['amender']})"
            else:
                eff = ""
            ts = (
                f"\n`Last modified:` <t:{v['last_modified']}:F>"
                if v["last_modified"]
                else ""
            )
            l = (
                f"> Globalban Logs Case `#{k}`\n`Type:` {v['type']}\n`Offender:` {off}\n"
                f"`Authorized by:` {aff}\n`Reason:` {v['reason']}\n"
                f"`Timestamp:` <t:{v['timestamp']}:F>{eff}{ts}"
            )
            gl.append(l)

        banlogs = "\n\n".join(gl)
        final_page = nu.pagify_this(
            banlogs,
            ["> "],
            "Page {index}/{pages}",
            embed_title="GlobalBan Ban Logs",
            embed_colour=await context.embed_colour(),
        )

        await nu.NoobPaginator(obj=context, pages=final_page).start()

    @globalban.command(name="reset")
    async def globalban_reset(self, context: nu.Context):
        """
        Reset any of the globalban config.

        Bot owners only.
        """
        await GbanViewReset(context, timeout=30).start("Choose what config to reset.")

    @globalban.command(name="unban")
    async def globalban_unban(
        self,
        context: nu.Context,
        user: t.Union[nu.discord.Member, int],
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
            except nu.discord.errors.NotFound:
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

        view = nu.NoobConfirmation(
            obj=context, confirm_action=confirm_action, timeout=30.0
        )
        await view.start(content=confirm_msg)

        await view.wait()

        if view.value:
            await context.typing()
            await self._globalunban_user(context=context, member=member, reason=reason)
