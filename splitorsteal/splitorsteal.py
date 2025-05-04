import asyncio
import noobutils as nu
import random
import typing as t

from redbot.core.utils import mod

from datetime import datetime, timedelta, timezone

from .views import Commence, DuelView, SplitOrStealView


DEFAULT_GUILD = {"managers": []}


class SplitOrSteal(nu.Cog):
    """
    A fun split or steal game.

    This game can shatter friendships.
    """

    __version__ = "3.1.4"
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
        self.active_cache: t.Dict[str, t.List[int]] = {}

    async def red_delete_data_for_user(
        self,
        *,
        requester: t.Literal["discord_deleted_user", "owner", "user", "user_strict"],
        user_id: int,
    ) -> None:
        """
        This cog does not store any end user data whatsoever.
        """
        return await super().red_delete_data_for_user(
            requester=requester, user_id=user_id
        )

    @nu.hybrid_command(name="splitorsteal", aliases=["sos"])
    @nu.commands.bot_has_permissions(embed_links=True)
    @nu.commands.cooldown(1, 10, nu.commands.BucketType.channel)
    @nu.commands.guild_only()
    @nu.app_commands.describe(prize="The prize for the game.")
    async def splitorsteal(self, context: nu.Context, *, prize: str):
        """
        Start a split or steal game event.

        Fun game to play.
        """
        managers = await self.config.guild(context.guild).managers()

        if (
            not await context.bot.is_owner(context.author)
            and not await mod.is_mod_or_superior(context.bot, context.author)
            and all(role_id not in context.author._roles for role_id in managers)
        ):
            return await context.reply(
                content="Only a SplitOrSteal manager or higher can run this command. "
                f"Use `{context.prefix}sosduel` instead.",
                mention_author=False,
                ephemeral=True,
            )

        if context.interaction:
            await context.interaction.response.send_message(
                content="Successfully started a SplitOrSteal game.", ephemeral=True
            )

        self.active_cache.setdefault(str(context.guild.id), [])
        if context.channel.id in self.active_cache[str(context.guild.id)]:
            return await context.reply(
                content="A game of SplitOrSteal is currently ongoing in this channel.",
                ephemeral=True,
                mention_author=False,
            )
        self.active_cache[str(context.guild.id)].append(context.channel.id)
        dt = datetime.now(timezone.utc) + timedelta(seconds=60)
        embed = nu.discord.Embed(
            title="A game of SplitOrSteal has begun!",
            description="Click the button below to get a chance to play and win a prize.",
            colour=await context.embed_colour(),
        )
        embed.set_image(
            url="https://cdn.discordapp.com/attachments/1035334209818071161/1183354734304837662/j.jpg"
        )
        embed.add_field(name="Prize:", value=prize, inline=True)
        embed.add_field(name="Hosted by:", value=context.author.mention, inline=True)
        embed.add_field(
            name="Time left:", value=f"<t:{round(dt.timestamp())}:R>", inline=True
        )

        commence_view = Commence()
        msg = await context.channel.send(embed=embed, view=commence_view)

        await asyncio.sleep(60)

        if len(commence_view.players) < 2:
            if context.channel.id in self.active_cache[str(context.guild.id)]:
                self.active_cache[str(context.guild.id)].remove(context.channel.id)
            return await msg.edit(
                content="SplitOrSteal game needs at least 2 players.",
                view=None,
                embed=None,
            )

        random.shuffle(commence_view.players)
        p1 = random.choice(commence_view.players)
        commence_view.players.remove(p1)
        p2 = random.choice(commence_view.players)
        await msg.delete()

        await SplitOrStealView(context, self).start(p1, p2, prize)

    @nu.hybrid_command(name="splitorstealduel", aliases=["sosduel"])
    @nu.commands.bot_has_permissions(embed_links=True)
    @nu.commands.cooldown(1, 10, nu.commands.BucketType.channel)
    @nu.commands.guild_only()
    @nu.app_commands.describe(
        opponent="Your splitorsteal opponent.", prize="The prize for the game."
    )
    async def splitorstealduel(
        self, context: nu.Context, opponent: nu.discord.Member, *, prize: str
    ):
        """
        SplitOrStealDuel someone.
        """
        if opponent.bot:
            return await context.reply(
                content="Bots are not allowed.", ephemeral=True, mention_author=False
            )

        self.active_cache.setdefault(str(context.guild.id), [])
        if context.channel.id in self.active_cache[str(context.guild.id)]:
            return await context.reply(
                content="A game of SplitOrSteal is currently ongoing in this channel.",
                ephemeral=True,
                mention_author=False,
            )

        if context.interaction:
            await context.interaction.response.send_message(
                content="Successfully started a SplitOrStealDuel game.", ephemeral=True
            )

        view = DuelView(context, opponent)
        await view.start()

        await view.wait()

        if view.value:
            if context.channel.id not in self.active_cache[str(context.guild.id)]:
                self.active_cache[str(context.guild.id)].append(context.channel.id)
            await SplitOrStealView(context, self).start(context.author, opponent, prize)
        elif context.channel.id in self.active_cache[str(context.guild.id)]:
            self.active_cache[str(context.guild.id)].remove(context.channel.id)

    @nu.group(name="splitorstealset", aliases=["sosset"])
    @nu.commands.admin_or_permissions(manage_guild=True)
    @nu.commands.guild_only()
    @nu.commands.bot_has_permissions(embed_links=True)
    async def splitorstealset(self, context: nu.Context):
        """
        Configure your splitorsteal guild settings.
        """
        pass

    @splitorstealset.command(name="manager")
    async def splitorstealset_manager(
        self,
        context: nu.Context,
        _types: t.Literal["add", "remove", "list"],
        *roles: nu.NoobFuzzyRole,
    ):
        """
        See, Add or Remove SplitOrSteal managers.

        These roles can run the `[p]splitorsteal` command.
        """
        if _types == "list":
            man = await self.config.guild(context.guild).managers()
            embed = nu.discord.Embed(
                title=f"List of SplitOrSteal managers for [{context.guild.name}]",
                description=nu.cf.humanize_list(
                    [f"<@&{r_id}>" for r_id in man] if man else ["None"]
                ),
                colour=await context.embed_colour(),
                timestamp=datetime.now(timezone.utc),
            )
            return await context.send(embed=embed)

        if not roles:
            return await context.send_help()

        s = []
        f = []
        async with self.config.guild(context.guild).managers() as m:
            for role in roles:
                if (
                    _types == "add"
                    and role.id in m
                    or _types != "add"
                    and role.id not in m
                ):
                    f.append(role.mention)
                    continue
                if _types == "add":
                    m.append(role.id)
                else:
                    m.remove(role.id)
                s.append(role.mention)

        _type = "added" if _types == "add" else "removed"
        _type2 = "to" if _types == "add" else "from"

        if s:
            await context.send(
                content=f"Successfully {_type} {nu.cf.humanize_list(s)} {_type2} the list of manager"
                " roles."
            )

        if f:
            await context.send(
                content=f"Failed to {_types} {nu.cf.humanize_list(f)} {_type2} the list of "
                "manager roles since they are already manager roles."
            )

    @splitorstealset.command(name="resetguild")
    async def splitorstealset_resetguild(self, context: nu.Context):
        """
        Reset your guild settings.
        """
        act = "Your splitorsteal guild settings has been cleared."
        conf = "Are you sure you want to reset your guild settings?"

        view = nu.NoobConfirmation(obj=context, confirm_action=act)
        await view.start(content=conf)

        await view.wait()

        if view.value:
            await self.config.guild(context.guild).clear()

    @splitorstealset.command(name="resetcog")
    @nu.commands.is_owner()
    async def splitorstealset_resetcog(self, context: nu.Context):
        """
        Reset the cogs config.
        """
        act = "SplitOrSteal cog config has been cleared."
        conf = "Are you sure you want to reset SplitOrSteal cog config?"

        view = nu.NoobConfirmation(obj=context, confirm_action=act)
        await view.start(content=conf)

        await view.wait()

        if view.value:
            await self.config.clear_all_guilds()
