import datetime
import noobutils as nu
import typing as t


DEFAULT_GLOBAL = {"default_channel": None, "bypass": []}


class DevLogs(nu.Cog):
    """
    Keep a log of all that evals and debugs.

    Logs all the Dev commands in a channel.
    Originally and formerly from sravan but I got permission to maintain it now.
    """

    __version__ = "1.1.4"
    __authors__ = ["sravan", "NoobInDaHause"]

    def __init__(self, *args, **kwargs):
        super().__init__(
            bot=kwargs.pop("bot"),
            use_config=True,
            identifier=0x2_412_214_4315312_9,
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
        This cog stores user ID's for the logging bypass, users can delete their data.
        """
        async with self.config.bypass() as bypass:
            b: list = bypass
            if user_id in b:
                index = b.index(user_id)
                b.pop(index)

    @nu.listener("on_command_completion")
    async def on_command_completion(self, context: nu.Context) -> None:
        """
        Log the command and send it to the channel.
        """
        if (
            await context.bot.is_owner(context.author)
            and context.author.id not in await self.config.bypass()
            and context.command.name in ["eval", "debug"]
        ):
            await self.send_log(context)

    async def send_log(self, context: nu.Context) -> None:
        """
        sends a embed in the channel and also returns DM if the command was ran in Dms.
        """
        partialchannel = await self.config.default_channel()
        if partialchannel is None:
            return
        # remove the codeblock in the message if it exists or add a codeblock if it doesn't
        content = context.message.content.replace("```", "")
        if content.startswith("```"):
            content = content.replace("```", "")
        embed = nu.discord.Embed(
            title=f"{context.command.name.upper()} Logs",
            description=nu.cf.box(content, lang="py"),
            color=await context.embed_colour(),
            timestamp=datetime.datetime.now(datetime.timezone.utc),
        )
        embed.set_author(
            name=context.author, icon_url=nu.is_have_avatar(context.author)
        )
        try:
            embed.add_field(
                name="Channel",
                value=f"{context.channel.mention}\n{context.channel.name}\n({context.channel.id})",
                inline=True,
            )
            embed.add_field(
                name="Guild",
                value=f"{context.guild.name}\n({context.guild.id})",
                inline=True,
            )
        except AttributeError:
            embed.add_field(name="Channel", value="DMs", inline=True)
        embed.add_field(
            name="Author",
            value=f"{context.author.name}\n({context.author.id})",
            inline=True,
        )
        try:
            view = nu.discord.ui.View()
            view.add_item(
                nu.discord.ui.Button(
                    label="Jump To Command", url=context.message.jump_url
                )
            )
            await self.bot.get_channel(partialchannel).send(embed=embed, view=view)
        except (nu.discord.errors.Forbidden, nu.discord.errors.HTTPException) as e:
            self.log.exception(
                "Error occurred while sending eval/debug logs.", exc_info=e
            )

    @nu.group(name="devlogset", aliases=["devset"])
    @nu.commands.guild_only()
    @nu.commands.is_owner()
    async def devlogset(self, context: nu.Context) -> None:
        """
        Configure DevLogs settings.
        """
        pass

    @devlogset.command(name="channel", aliases=["chan"])
    async def devlogset_channel(
        self, context: nu.Context, channel: nu.discord.TextChannel = None
    ) -> None:
        """
        Set the channel to log to.
        """
        if not channel:
            await self.config.default_channel.clear()
            return await context.send(
                content="The DevLogs logging channel has been cleared."
            )

        await self.config.default_channel.set(channel.id)
        await context.send(
            content=f"Successfully set the DevLogs logging channel to {channel.mention}."
        )

    @devlogset.group(name="bypass")
    async def devlogset_bypass(self, context: nu.Context) -> None:
        """
        Manage the bypass list.
        """
        pass

    @devlogset_bypass.command(name="add", aliases=["+"])
    async def devlogset_bypass_add(
        self, context: nu.Context, user: nu.discord.User
    ) -> None:
        """
        Add a user to the bypass list.
        """
        async with self.config.bypass() as bypass:
            b: list = bypass
            if user.id in b:
                return await context.send(content="User is already in the bypass list.")

            b.append(user.id)
            await context.send(content=f"{user.mention} added to the bypass list.")

    @devlogset_bypass.command(name="remove", aliases=["-"])
    async def devlogset_bypass_remove(
        self, context: nu.Context, user: nu.discord.User
    ) -> None:
        """
        Remove a user from the bypass list.
        """
        async with self.config.bypass() as bypass:
            b: list = bypass
            if user.id not in b:
                return await context.send(content="User is not in the bypass list.")

            b.remove(user.id)
            await context.send(content=f"{user.mention} removed from the bypass list.")

    @devlogset_bypass.command(name="list")
    async def devlogset_bypass_list(self, context: nu.Context) -> None:
        """
        list the users in the bypass list.
        """
        b: list = await self.config.bypass()
        if not b:
            return await context.send(content="There are no users in the bypass list.")

        users = ""
        for user in b:
            try:
                user_obj = await context.bot.get_or_fetch_user(user)
                users += f"` - ` {user_obj} (`{user_obj.id}`).\n"
            except nu.discord.errors.NotFound:
                users += f"` - ` Unknown User (`{user}`).\n"
        text = f"Command executed by {context.author} |" " Page ({index}/{pages})"
        title = "A list of users that bypasses the DevLogs cog"
        final_page = nu.pagify_this(
            users,
            ["` - `"],
            text,
            embed_title=title,
            embed_colour=context.author.colour,
            footer_icon=nu.is_have_avatar(context.author),
        )
        await nu.NoobPaginator(obj=context, pages=final_page, timeout=60.0).start()
