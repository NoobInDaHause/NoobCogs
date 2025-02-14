import noobutils as nu

from typing import Literal

from .views import PressFView


DEFAULT_GUILD = {"emoji": "🇫", "buttoncolour": "blurple"}


class PressF(nu.Cog):
    """
    F.

    Press F to pay respect on something using buttons.
    """

    def __init__(self, bot: nu.Red, *args, **kwargs) -> None:
        super().__init__(
            bot=bot,
            cog_name=self.__class__.__name__,
            version="1.2.3",
            authors=["NoobInDaHause"],
            use_config=True,
            identifier=5434354373844151563453,
            force_registration=True,
            *args,
            **kwargs,
        )
        self.config.register_guild(**DEFAULT_GUILD)
        self.active_cache = []

    async def red_delete_data_for_user(
        self,
        *,
        requester: Literal["discord_deleted_user", "owner", "user", "user_strict"],
        user_id: int,
    ):
        """
        No EUD to delete.
        """
        return await super().red_delete_data_for_user(
            requester=requester, user_id=user_id
        )

    @nu.commands.hybrid_command(name="pressf")
    @nu.commands.guild_only()
    @nu.commands.bot_has_permissions(embed_links=True, use_external_emojis=True)
    @nu.app_commands.guild_only()
    @nu.app_commands.describe(thing="The thing that you want to pay respects to.")
    async def pressf(self, context: nu.commands.Context, *, thing: str):
        """
        Pay respects on something.
        """
        if context.channel.id in self.active_cache:
            return await context.send(
                content="You are already paying respects on something in this channel, wait for it to finish."
            )
        self.active_cache.append(context.channel.id)
        e = await self.config.guild(context.guild).emoji()
        c = await self.config.guild(context.guild).buttoncolour()
        view = PressFView(obj=context, cog=self, thing=thing)
        view.press_f_button.emoji = e
        view.press_f_button.style = nu.get_button_colour(c)
        await view.start()

    @nu.commands.group(name="pressfset")
    @nu.commands.guild_only()
    @nu.commands.admin_or_permissions(manage_guild=True)
    @nu.commands.bot_has_permissions(use_external_emojis=True)
    async def pressfset(self, context: nu.commands.Context):
        """
        Configure the cogs settings.
        """
        pass

    @pressfset.command(name="emoji")
    async def pressfset_emoji(
        self, context: nu.commands.Context, emoji: nu.NoobEmojiConverter = None
    ):
        """
        Change the F emoji.

        Leave `emoji` blank to see current set emoji.
        """
        if not emoji:
            e = await self.config.guild(context.guild).emoji()
            return await context.send(content=f"The current Press F emoji is {e}.")
        await self.config.guild(context.guild).emoji.set(str(emoji))
        await context.send(content=f"The new Press F emoji has been set to {emoji}.")

    @pressfset.command(name="buttoncolour", aliases=["buttoncolor"])
    async def pressfset_buttoncolour(
        self,
        context: nu.commands.Context,
        colour: Literal["red", "green", "blurple", "grey"] = None,
    ):
        """
        Change the Press F button colour.

        Leave `colour` blank to see current set colour.
        """
        if not colour:
            c = await self.config.guild(context.guild).buttoncolour()
            return await context.send(
                content=f"The current Press F button colour is {c}"
            )
        await self.config.guild(context.guild).buttoncolour.set(colour)
        await context.send(
            content=f"The new Press F button colour has been set to {colour}."
        )

    @pressfset.command(name="resetcog")
    @nu.commands.is_owner()
    async def pressfset_resetcog(self, context: nu.commands.Context):
        """
        Reset the cogs configuration.
        """
        conf_msg = "Are you sure you want to reset the cogs config?"
        conf_act = "Successfully reset the cogs config."

        view = nu.NoobConfirmation(obj=context, confirm_action=conf_act)
        await view.start(content=conf_msg)

        await view.wait()

        if view.value is True:
            await self.config.clear_all()

    @pressfset.command(name="reset")
    async def pressfset_reset(self, context: nu.commands.Context):
        """
        Reset the Press F current guild settings to default.
        """
        confirmation_msg = "Are you sure you want to reset the current guild settings?"
        confirm_action = "Successfully reset the guilds settings."

        view = nu.NoobConfirmation(obj=context, confirm_action=confirm_action)
        await view.start(content=confirmation_msg)

        await view.wait()

        if view.value is True:
            await self.config.guild(context.guild).clear()
