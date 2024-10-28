import noobutils as nu

from redbot.core.bot import app_commands, commands, Red

from typing import Literal

from .views import CookieClickerView


DEFAULT_GUILD = {"emoji": "🍪", "buttoncolour": "blurple", "user_lb": {}}


class CookieClicker(nu.Cog):
    """
    Play a cookie clicker.

    Anti stress 100%.
    """

    def __init__(self, bot: Red, *args, **kwargs) -> None:
        super().__init__(
            bot=bot,
            cog_name=self.__class__.__name__,
            version="1.2.4",
            authors=["NoobInDaHause"],
            use_config=True,
            identifier=348468464655768,
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
        """
        This cog stores user ids for cookie clicker leaderboard purposes.
        """
        for g in (await self.config.all_guilds()).keys():
            if guild := self.bot.get_guild(g):
                user_lb: dict = await self.config.guild(guild).user_lb()
                if user_id not in set(user_lb):
                    continue
                async with self.config.guild(guild).user_lb() as ulb:
                    del ulb[user_id]

    @commands.hybrid_command(name="cookieclicker")
    @commands.bot_has_permissions(embed_links=True)
    @commands.guild_only()
    @app_commands.guild_only()
    async def cookieclicker(self, context: commands.Context):
        """
        Cookie clicker.

        Anti stress guaranteed.
        """
        user_lb = await self.config.guild(context.guild).user_lb()
        if str(context.author.id) not in user_lb:
            async with self.config.guild(context.guild).user_lb() as ulb:
                ul: dict = ulb
                ul.setdefault(str(context.author.id), 0)
        e = await self.config.guild(context.guild).emoji()
        c = await self.config.guild(context.guild).buttoncolour()
        view = CookieClickerView(context, self, timeout=15.0)
        view.cookieclicker.emoji = e
        view.cookieclicker.style = nu.get_button_colour(c)
        await view.start()

    @commands.command(name="cookieclickerlb", aliases=["cclb"])
    @commands.bot_has_permissions(embed_links=True)
    async def cookieclickerlb(self, context: commands.Context):
        """
        See this guild's leaderboard.

        Check members with their clicking milestones.
        """
        user_lb: dict = await self.config.guild(context.guild).user_lb()
        if not user_lb:
            return await context.send(
                content="Nobody is in the leaderboard yet. "
                f"Why don't you be the first one in the leaderboard. `{context.prefix}cookieclicker`"
            )

        sorted_members = dict(sorted(user_lb.items(), key=lambda i: i[1], reverse=True))

        ctop = "\n".join(
            [
                f"` {g}. ` <@{k}> - **{v} :cookie:**"
                for g, (k, v) in enumerate(sorted_members.items(), 1)
            ]
        )

        pages = await nu.pagify_this(
            ctop,
            ["\n"],
            "Page ({index}/{pages})",
            embed_title=f"Top cookie clickers in [{context.guild.name}]",
            embed_colour=await context.embed_colour(),
            footer_icon=nu.is_have_avatar(context.guild),
        )

        await nu.NoobPaginator(obj=context, pages=pages).start()

    @commands.group(name="cookieclickerset", aliases=["ccset"])
    @commands.guild_only()
    @commands.bot_has_permissions(use_external_emojis=True, embed_links=True)
    async def cookieclickerset(self, context: commands.Context):
        """
        Configure the cogs settings.
        """
        pass

    @cookieclickerset.command(name="forgetme")
    async def cookieclickerset_forgetme(self, context: commands.Context):
        """
        Remove yourself from this guild's cookie clicker leaderboard.

        Don't know why you would want this but hey who am I to judge.
        """
        user_lb = await self.config.guild(context.guild).user_lb()
        if str(context.author.id) not in user_lb:
            return await context.send(content="You are not in the leaderboard.")

        act = "You are no longer on this guild's cookie clicker leaderboard."
        conf = "Are you sure you want to remove yourself from this guild's leaderboard?"

        view = nu.NoobConfirmation(obj=context, confirm_action=act)
        await view.start(content=conf)

        await view.wait()

        if view.value:
            async with self.config.guild(context.guild).user_lb() as ulb:
                del ulb[str(context.author.id)]

    @cookieclickerset.command(name="emoji")
    @commands.admin_or_permissions(manage_guild=True)
    async def cookieclickerset_emoji(
        self, context: commands.Context, emoji: nu.NoobEmojiConverter = None
    ):
        """
        Change the cookie emoji.

        Leave `emoji` blank to see current set emoji.
        """
        if not emoji:
            e = await self.config.guild(context.guild).emoji()
            return await context.send(
                content=f"The current CookieClicker emoji is {e}."
            )
        await self.config.guild(context.guild).emoji.set(str(emoji))
        await context.send(
            content=f"The new CookieClicker emoji has been set to {emoji}."
        )

    @cookieclickerset.command(name="buttoncolour", aliases=["buttoncolor"])
    @commands.admin_or_permissions(manage_guild=True)
    async def cookieclickerset_buttoncolour(
        self,
        context: commands.Context,
        colour: Literal["red", "green", "blurple", "grey"] = None,
    ):
        """
        Change the CookieClicker button colour.

        Leave `colour` blank to see current set colour.
        """
        if not colour:
            c = await self.config.guild(context.guild).buttoncolour()
            return await context.send(
                content=f"The current CookieClicker button colour is {c}"
            )
        await self.config.guild(context.guild).buttoncolour.set(colour)
        await context.send(
            content=f"The new CookieClicker button colour has been set to {colour}."
        )

    @cookieclickerset.command(name="reset")
    @commands.admin_or_permissions(manage_guild=True)
    async def cookieclickerset_reset(self, context: commands.Context):
        """
        Reset the CookieClicker current guild settings to default.
        """
        confirmation_msg = "Are you sure you want to reset the current guild settings?"
        confirm_action = "Successfully reset the guilds settings."

        view = nu.NoobConfirmation(obj=context, confirm_action=confirm_action)
        await view.start(content=confirmation_msg)

        await view.wait()

        if view.value is True:
            await self.config.guild(context.guild).clear()

    @cookieclickerset.command(name="resetcog")
    @commands.is_owner()
    async def cookieclickerset_resetcog(self, context: commands.Context):
        """
        Reset the whole cogs data.

        (Bot owner only.)
        """
        conf = "Are you sure you want to reset the whole cog settings?"
        act = "The cog settings have been reset."

        view = nu.NoobConfirmation(obj=context, confirm_action=act)
        await view.start(content=conf)

        await view.wait()

        if view.value:
            await self.config.clear_all()
