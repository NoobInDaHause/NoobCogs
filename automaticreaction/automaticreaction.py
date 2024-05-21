import contextlib
import discord
import noobutils as nu
import re

from redbot.core.bot import commands, Red

from typing import Literal

DEFAULT_GUILD = {"autoreactions": {}}


class AutomaticReaction(nu.Cog):
    """
    Automatic emoji reactions.

    Add words that get automatically reacted by the bot with any emoji.
    """

    def __init__(self, bot: Red, *args, **kwargs):
        super().__init__(
            bot=bot,
            cog_name=self.__class__.__name__,
            version="1.0.0",
            authors=["NoobInDaHause"],
            use_config=True,
            force_registration=True,
            *args,
            **kwargs,
        )
        self.config.register_guild(**DEFAULT_GUILD)

    async def red_delete_data_for_user(
        self,
        *,
        requester: Literal["discord_deleted_user", "owner", "user", "user_strict"],
        user_id: int,
    ):
        return await super().red_delete_data_for_user(
            requester=requester, user_id=user_id
        )

    @staticmethod
    def contains_word(string: str, word: str) -> bool:
        pattern = re.escape(word)
        return bool(re.search(pattern, string))

    @commands.Cog.listener(name="on_message")
    async def auto_reaction_listener(self, message: discord.Message):
        if (
            not message.guild
            or await self.bot.cog_disabled_in_guild(self, message.guild)
            or not message.channel.permissions_for(message.guild.me).add_reactions
            or isinstance(message.author, discord.User)
            or not message.content
        ):
            return

        ar = await self.config.guild(message.guild).autoreactions()
        for word, emoji in ar.items():
            if self.contains_word(message.content, word):
                with contextlib.suppress(discord.errors.HTTPException):
                    await message.add_reaction(emoji)

    @commands.group(name="automaticreaction", aliases=["autoreact"])
    @commands.bot_has_permissions(embed_links=True)
    @commands.mod_or_permissions(manage_guild=True)
    async def automaticreaction(self, context: commands.Context):
        """
        Base commands for automatic reaction cog.
        """
        pass

    @automaticreaction.command(name="add")
    @commands.bot_has_permissions(add_reactions=True)
    async def automaticreaction_add(
        self, context: commands.Context, emoji: nu.NoobEmojiConverter, *, word: str
    ):
        """
        Add an automatic reaction.
        """
        async with self.config.guild(context.guild).autoreactions() as ar:
            if ar.get(word):
                return await context.send(
                    content="That word seems to already have an automatic reaction on it."
                )
            ar[word] = str(emoji)
        await context.send(
            content=f"Successfully Added {emoji} automatic reaction for the word `{word}`."
        )

    @automaticreaction.command(name="remove")
    async def automaticreaction_remove(self, context: commands.Context, *, word: str):
        """
        Remove an automatic reaction.
        """
        async with self.config.guild(context.guild).autoreactions() as ar:
            if not ar.get(word):
                return await context.send(
                    content="That word does not have any automatic reactions set."
                )
            ar.pop(word)
        await context.send(
            content="Successfully Removed automatic reaction for that word."
        )

    @automaticreaction.command(name="list")
    async def automaticreaction_list(self, context: commands.Context):
        """
        See the list of automatic reactions.
        """
        ar = await self.config.guild(context.guild).autoreactions()
        if not ar:
            return await context.send(content="This guild has no automatic reactions.")
        string = ""
        for word, emoji in ar.items():
            try:
                e = await nu.NoobEmojiConverter().convert(context, emoji)
                _id = getattr(e, "id", None)
                if _id:
                    string += f"{emoji} **{_id}**: `{word}`\n"
                else:
                    string += f"{emoji}: `{word}`\n"
            except commands.BadArgument:
                string += f"{emoji}: `{word}`\n"

        pagified = await nu.pagify_this(
            string,
            embed_title=f"List of automatic reactions for [{context.guild.name}]",
            embed_colour=self.bot._color,
            embed_timestamp=discord.utils.utcnow(),
            embed_thumbnail=nu.is_have_avatar(context.guild),
        )
        await nu.NoobPaginator(pagified).start(context)

    @automaticreaction.command(name="clearremoved")
    @commands.admin_or_permissions(manage_guild=True)
    async def automaticreaction_clearremoved(self, context: commands.Context):
        """
        Clear all the emojis that are no longer available.
        """
        async with context.typing():
            ar = await self.config.guild(context.guild).autoreactions()
            for word, emoji in ar.items():
                try:
                    e = await nu.NoobEmojiConverter().convert(context, emoji)
                    available = getattr(e, "available", True)
                    if available is False:
                        ar.pop(word)
                except commands.BadArgument:
                    ar.pop(word)
            await self.config.guild(context.guild).set(ar)
            await context.send(
                content="Successfully cleared all the unavailable emojis from automatic reactions."
            )

    @automaticreaction.command(name="resetguild")
    @commands.admin_or_permissions(manage_guild=True)
    async def automaticreaction_resetguild(self, context: commands.Context):
        """
        Reset the automatic reactions for this guild.
        """
        act = "This guilds automatic reaction has been cleared."
        conf = "Are you sure you want to reset this guilds automatic reactions?"
        view = nu.NoobConfirmation()
        await view.start(context, act, content=conf)
        await view.wait()

        if view.value:
            await self.config.guild(context.guild).clear()

    @automaticreaction.command(name="resetcog")
    @commands.is_owner()
    async def automaticreaction_resetcog(self, context: commands.Context):
        """
        Reset the automaticreaction cog config.
        """
        act = "Successfully cleared the automaticreaction config."
        conf = "Are you sure you want to reset the cog config?"
        view = nu.NoobConfirmation()
        await view.start(context, act, content=conf)
        await view.wait()

        if view.value:
            await self.config.clear_all()
