import contextlib
import noobutils as nu
import re
import typing as t

DEFAULT_GUILD = {"autoreactions": {}}


class AutomaticReaction(nu.Cog):
    """
    Automatic emoji reactions.

    Add words that get automatically reacted by the bot with any emoji.
    """

    __version__ = "1.0.10"
    __authors__ = ["NoobInDaHause"]

    def __init__(self, *args, **kwargs):
        super().__init__(
            bot=kwargs.pop("bot"),
            use_config=True,
            force_registration=True,
            *args,
            **kwargs,
        )
        self.config.register_guild(**DEFAULT_GUILD)

    async def red_delete_data_for_user(
        self,
        *,
        requester: t.Literal["discord_deleted_user", "owner", "user", "user_strict"],
        user_id: int,
    ):
        return await super().red_delete_data_for_user(
            requester=requester, user_id=user_id
        )

    @staticmethod
    def contains_word(string: str, word: str) -> bool:
        pattern = re.escape(word)
        return bool(re.search(pattern, string))

    @nu.listener(name="on_message")
    async def auto_reaction_listener(self, message: nu.discord.Message):
        if (
            not message.guild
            or await self.bot.cog_disabled_in_guild(self, message.guild)
            or not message.channel.permissions_for(message.guild.me).add_reactions
            or isinstance(message.author, nu.discord.User)
            or not message.content
        ):
            return

        ar: dict = await self.config.guild(message.guild).autoreactions()
        for word, emoji in ar.items():
            if self.contains_word(message.content, word):
                with contextlib.suppress(
                    nu.discord.errors.HTTPException, nu.discord.errors.Forbidden
                ):
                    await message.add_reaction(emoji)

    @nu.group(name="automaticreaction", aliases=["autoreact"])
    @nu.commands.bot_has_permissions(embed_links=True)
    @nu.commands.mod_or_permissions(manage_guild=True)
    async def automaticreaction(self, context: nu.Context):
        """
        Base commands for automatic reaction cog.
        """
        pass

    @automaticreaction.command(name="add")
    @nu.commands.bot_has_permissions(add_reactions=True)
    async def automaticreaction_add(
        self, context: nu.Context, emoji: nu.NoobEmojiConverter, *, word: str
    ):
        """
        Add an automatic reaction.
        """
        async with self.config.guild(context.guild).autoreactions() as _ar:
            ar: dict = _ar
            if ar.get(word):
                return await context.send(
                    content="That word seems to already have an automatic reaction on it."
                )
            ar[word] = str(emoji)
        await context.send(
            content=f"Successfully Added {emoji} automatic reaction for the word `{word}`."
        )

    @automaticreaction.command(name="remove")
    async def automaticreaction_remove(self, context: nu.Context, *, word: str):
        """
        Remove an automatic reaction.
        """
        async with self.config.guild(context.guild).autoreactions() as _ar:
            ar: dict = _ar
            if not ar.get(word):
                return await context.send(
                    content="That word does not have any automatic reactions set."
                )
            ar.pop(word)
        await context.send(
            content="Successfully Removed automatic reaction for that word."
        )

    @automaticreaction.command(name="list")
    async def automaticreaction_list(self, context: nu.Context):
        """
        See the list of automatic reactions.
        """
        ar: dict = await self.config.guild(context.guild).autoreactions()
        if not ar:
            return await context.send(content="This guild has no automatic reactions.")
        string = ""
        for word, emoji in ar.items():
            try:
                e = await nu.NoobEmojiConverter().convert(context, emoji)
                if _id := getattr(e, "id", None):
                    string += f"{emoji} **{_id}**: `{word}`\n"
                else:
                    string += f"{emoji}: `{word}`\n"
            except nu.commands.BadArgument:
                string += f"{emoji}: `{word}`\n"

        pagified = nu.pagify_this(
            string,
            embed_title=f"List of automatic reactions for [{context.guild.name}]",
            embed_colour=self.bot._color,
            embed_timestamp=nu.discord.utils.utcnow(),
            embed_thumbnail=nu.is_have_avatar(context.guild),
        )
        await nu.NoobPaginator(obj=context, pages=pagified).start()

    @automaticreaction.command(name="clearremoved")
    @nu.commands.admin_or_permissions(manage_guild=True)
    async def automaticreaction_clearremoved(self, context: nu.Context):
        """
        Clear all the emojis that are no longer available.
        """
        async with context.typing():
            async with self.config.guild(context.guild).autoreactions() as _ar:
                ar: dict = _ar
                copied = ar.copy()
                for word, emoji in copied.items():
                    try:
                        e = await nu.NoobEmojiConverter().convert(context, emoji)
                        if not getattr(e, "available", True):
                            ar.pop(word)
                    except nu.commands.BadArgument:
                        ar.pop(word)

            await context.send(
                content="Successfully cleared all the unavailable emojis from automatic reactions."
            )

    @automaticreaction.command(name="resetguild")
    @nu.commands.admin_or_permissions(manage_guild=True)
    async def automaticreaction_resetguild(self, context: nu.Context):
        """
        Reset the automatic reactions for this guild.
        """
        act = "This guilds automatic reaction has been cleared."
        conf = "Are you sure you want to reset this guilds automatic reactions?"

        view = nu.NoobConfirmation(obj=context, confirm_action=act)
        await view.start(content=conf)

        await view.wait()

        if view.value:
            await self.config.guild(context.guild).clear()

    @automaticreaction.command(name="resetcog")
    @nu.commands.is_owner()
    async def automaticreaction_resetcog(self, context: nu.Context):
        """
        Reset the automaticreaction cog config.
        """
        act = "Successfully cleared the automaticreaction config."
        conf = "Are you sure you want to reset the cog config?"

        view = nu.NoobConfirmation(obj=context, confirm_action=act)
        await view.start(content=conf)

        await view.wait()

        if view.value:
            await self.config.clear_all()
