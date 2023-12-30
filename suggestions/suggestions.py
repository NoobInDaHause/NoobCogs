import asyncio
import contextlib
import discord
import logging
import noobutils as nu

from redbot.core.bot import app_commands, commands, Config, Red
from redbot.core.utils import chat_formatting as cf

from typing import Literal

from .views import SuggestionView, SuggestionViewView


class Suggestions(commands.Cog):
    """
    Suggestion system.

    Have users submit suggestions to help improve some things.
    """

    def __init__(self, bot: Red, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.config = Config.get_conf(
            self, identifier=1234567890, force_registration=True
        )
        default_guild = {
            "auto_delete": True,
            "emojis": {"upvote": "⬆️", "downvote": "⬇️"},
            "button_colour": {"upbutton": "blurple", "downbutton": "blurple"},
            "channels": {"suggest": None, "reject": None, "approve": None},
            "self_vote": True,
            "next_id": 1,
            "suggestions": {},
        }
        self.config.register_guild(**default_guild)

        self.log = logging.getLogger("red.NoobCogs.Suggestions")

    __version__ = "2.0.2"
    __author__ = ["NooInDaHause"]
    __docs__ = (
        "https://github.com/NoobInDaHause/NoobCogs/blob/red-3.5/suggestions/README.md"
    )

    def format_help_for_context(self, context: commands.Context) -> str:
        plural = "s" if len(self.__author__) > 1 else ""
        return (
            f"{super().format_help_for_context(context)}\n\n"
            f"Cog Version: **{self.__version__}**\n"
            f"Cog Author{plural}: {cf.humanize_list([f'**{auth}**' for auth in self.__author__])}\n"
            f"Cog Documentation: [[Click here]]({self.__docs__})"
        )

    async def red_delete_data_for_user(
        self,
        *,
        requester: Literal["discord_deleted_user", "owner", "user", "user_strict"],
        user_id: int,
    ):
        """
        This cog stores data provided by users for the express purpose of submitting suggestions.
        It does not store user data which was not provided through a command.
        Users may remove their own content without making a data removal request.
        This cog does not support data requests, but will respect deletion requests.
        """
        for guild_id in (await self.config.all_guilds()).keys():
            async with self.config.guild_from_id(guild_id).suggestions() as suggestions:
                for suggest_data in suggestions.values():
                    if suggest_data["suggester_id"] == user_id:
                        suggest_data["suggester_id"] = None
                    if suggest_data["reviewer_id"] == user_id:
                        suggest_data["reviewer_id"] = None
                    if user_id in suggest_data["upvotes"]:
                        suggest_data["upvotes"].remove(user_id)
                    if user_id in suggest_data["downvotes"]:
                        suggest_data["downvotes"].remove(user_id)

    async def cog_load(self) -> None:
        asyncio.create_task(self.initialize_views())

    async def cog_unload(self) -> None:
        for guild_data in (await self.config.all_guilds()).values():
            for suggest_data in guild_data["suggestions"].values():
                if suggest_data["status"] == "running":
                    if view := discord.utils.get(
                        self.bot.persistent_views, _cache_key=suggest_data["message_id"]
                    ):
                        view.stop()

    async def initialize_views(self):
        await self.bot.wait_until_red_ready()
        for guild_id, guild_data in (await self.config.all_guilds()).items():
            if guild := self.bot.get_guild(guild_id):
                if sug := guild_data.get("suggestions"):
                    for suggest_id, suggest_data in sug.items():
                        if suggest_data["status"] == "running":
                            channel = guild.get_channel(suggest_data["channel_id"])
                            with contextlib.suppress(Exception):
                                msg = await channel.fetch_message(
                                    suggest_data["message_id"]
                                )
                                self.bot.add_view(
                                    view=SuggestionView(
                                        cog=self, suggestion_id=suggest_id
                                    ),
                                    message_id=msg.id,
                                )

    async def add_suggestion(
        self,
        context: commands.Context,
        chan: discord.TextChannel,
        suggest_msg: discord.Message,
        suggestion: str,
    ):
        sug_id = await self.config.guild(context.guild).next_id()
        async with self.config.guild(context.guild).suggestions() as s:
            s |= {
                str(sug_id): {
                    "suggester_id": context.author.id,
                    "message_id": suggest_msg.id,
                    "channel_id": chan.id,
                    "suggestion": suggestion,
                    "status": "running",
                    "upvotes": [],
                    "downvotes": [],
                    "reviewer_id": None,
                    "reason": None,
                }
            }
        await self.config.guild(context.guild).next_id.set(sug_id + 1)

    async def edit_message(
        self, msg: discord.Message, embed: discord.Embed, label1: str, label2: str
    ):
        data = await self.config.guild(msg.guild).all()
        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                label=label1,
                disabled=True,
                emoji=data["emojis"]["upvote"],
                style=nu.get_button_colour(data["button_colour"]["upbutton"]),
            )
        )
        view.add_item(
            discord.ui.Button(
                label=label2,
                disabled=True,
                emoji=data["emojis"]["downvote"],
                style=nu.get_button_colour(data["button_colour"]["downbutton"]),
            )
        )
        await msg.edit(embed=embed, view=view)

    async def make_embed(
        self,
        title: str,
        desc: str,
        colour: discord.Colour,
        authname: str,
        authic: str,
        stattype: str,
        reviewer: str = None,
        reason: str = None,
        results: str = None,
    ) -> discord.Embed:
        e = discord.Embed(
            title=title,
            description=desc,
            colour=colour,
        )
        e.set_author(name=authname, icon_url=authic)
        if reviewer:
            e.add_field(name="Reviewer:", value=reviewer, inline=True)
        if stattype != "running":
            e.add_field(name="Status:", value=f"**{stattype.title()}**", inline=True)
        if results:
            e.add_field(name="Results:", value=results, inline=True)
        if reason:
            e.add_field(name="Reason:", value=reason, inline=False)
        return e

    async def send_suggestion(self, context: commands.Context, suggestion: str):
        data = await self.config.guild(context.guild).all()
        channel = context.guild.get_channel(data["channels"]["suggest"])
        embed = await self.make_embed(
            title=f"Suggestion **#{data['next_id']}**",
            desc=suggestion,
            colour=await context.embed_colour(),
            authname=f"{context.author} ({context.author.id})",
            authic=nu.is_have_avatar(context.author),
            stattype="running",
        )
        view = SuggestionView(self, str(data["next_id"]))
        view.upvote_button.style = nu.get_button_colour(
            data["button_colour"]["upbutton"]
        )
        view.upvote_button.emoji = data["emojis"]["upvote"]
        view.upvote_button.label = "0"
        view.downvote_button.style = nu.get_button_colour(
            data["button_colour"]["downbutton"]
        )
        view.downvote_button.emoji = data["emojis"]["downvote"]
        view.downvote_button.label = "0"
        msg = await channel.send(embed=embed, view=view)
        await self.add_suggestion(context, channel, msg, suggestion)
        return msg.jump_url, embed

    async def dm_suggester(
        self,
        member: discord.Member,
        url: str = None,
        b1: str = None,
        b2: str = None,
        *args,
        **kwargs,
    ):
        data = await self.config.guild(member.guild).all()
        style1 = nu.get_button_colour(data["button_colour"]["upbutton"])
        style2 = nu.get_button_colour(data["button_colour"]["downbutton"])
        if url and b1 and b2:
            view = discord.ui.View()
            view.add_item(
                discord.ui.Button(
                    label=b1,
                    emoji=data["emojis"]["upvote"],
                    style=style1,
                    disabled=True,
                )
            )
            view.add_item(
                discord.ui.Button(
                    label=b2,
                    emoji=data["emojis"]["downvote"],
                    style=style2,
                    disabled=True,
                )
            )
            view.add_item(discord.ui.Button(label="Jump To Suggestion", url=url))
            await member.send(view=view, *args, **kwargs)
        elif url is not None and b1 is None and b2 is None:
            viewurl = discord.ui.View()
            viewurl.add_item(discord.ui.Button(label="Jump To Suggestion", url=url))
            await member.send(view=viewurl, *args, **kwargs)
        else:
            await member.send(*args, **kwargs)

    async def send_to_reject_or_approve_channel(
        self,
        context: commands.Context,
        channel_id: int,
        jump_url: str,
        embed: discord.Embed,
    ):
        a = context.guild.get_channel(channel_id)
        if not a:
            return
        with contextlib.suppress(discord.errors.Forbidden):
            view = discord.ui.View()
            view.add_item(discord.ui.Button(label="Jump To Suggestion", url=jump_url))
            await a.send(embed=embed, view=view)

    async def end_suggestion(
        self, context: commands.Context, status_type: str, suggest_id: str, reason: str
    ):
        data = await self.config.guild(context.guild).all()
        async with self.config.guild(context.guild).suggestions() as s:
            suggest_data = s[suggest_id]
            if suggest_data["status"] != "running":
                return "done"
            channel = context.guild.get_channel(suggest_data["channel_id"])
            if not channel:
                return "nochan"
            if vi := discord.utils.get(
                self.bot.persistent_views, _cache_key=suggest_data["message_id"]
            ):
                vi.stop()
            try:
                msg = await channel.fetch_message(suggest_data["message_id"])
            except (discord.errors.NotFound, discord.errors.Forbidden):
                return "notfound"
            suggest_data["reviewer_id"] = context.author.id
            suggest_data["reason"] = reason
            suggest_data["status"] = status_type
            stit = f"Suggestion **#{suggest_id}**"
            sdesc = suggest_data["suggestion"]
            col = (
                discord.Colour.green()
                if status_type == "approved"
                else discord.Colour.red()
            )
            mem = context.guild.get_member(suggest_data["suggester_id"])
            authe = f"{mem} ({mem.id})" if mem else "[Unknown or Deleted User]"
            b = [str(len(suggest_data["upvotes"])), str(len(suggest_data["downvotes"]))]
            results = f"{data['emojis']['upvote']}: **{b[0]}**\n{data['emojis']['downvote']}: **{b[1]}**"
            embed = await self.make_embed(
                title=stit,
                desc=sdesc,
                colour=col,
                authname=authe,
                authic=nu.is_have_avatar(mem or context.guild),
                stattype=status_type,
                reviewer=str(context.author.mention),
                reason=reason,
                results=results,
            )
            await self.send_to_reject_or_approve_channel(
                context,
                data["channels"]["approve"]
                if status_type == "approved"
                else data["channels"]["reject"],
                msg.jump_url,
                embed,
            )
            if mem:
                cont = (
                    f"Your suggestion **#{suggest_id}** was `{status_type}` by {context.author} "
                    f"({context.author.id}).\nReason: {reason}"
                )
                with contextlib.suppress(discord.errors.Forbidden):
                    await self.dm_suggester(mem, msg.jump_url, b[0], b[1], content=cont)
            try:
                await self.edit_message(msg, embed, b[0], b[1])
            except discord.errors.Forbidden:
                return "error"

    @commands.hybrid_command(name="suggest")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @app_commands.guild_only()
    @app_commands.describe(suggestion="Your suggestion.")
    async def suggest(self, context: commands.Context, *, suggestion: str):
        """
        Suggest stuff.
        """
        if len(suggestion) > 4000:
            return await context.reply(
                content="Your suggestion must be less than 4000 characters.",
                ephemeral=True,
                mention_author=False,
            )

        data = await self.config.guild(context.guild).all()
        if not data["channels"]["suggest"]:
            return await context.reply(
                content="No suggestion channel found. Ask an admin to set one.",
                ephemeral=True,
                mention_author=False,
            )

        try:
            em = await self.send_suggestion(context=context, suggestion=suggestion)
            if context.prefix == "/":
                await context.reply(content="Successfully submitted.", ephemeral=True)
            with contextlib.suppress(discord.errors.Forbidden):
                await self.dm_suggester(
                    context.author,
                    em[0],
                    content="Your suggestion has been submitted for votes and review.",
                    embed=em[1],
                )
        except Exception as e:
            return await context.reply(
                content="An error has occurred while sending the suggestion.\n"
                f"Here is the traceback: {cf.box(e, 'py')}",
                ephemeral=True,
                mention_author=False,
            )

        if data["auto_delete"] and context.prefix != "/":
            with contextlib.suppress(
                discord.errors.HTTPException, discord.errors.Forbidden
            ):
                await context.message.delete()

    @commands.command(name="approve")
    @commands.admin_or_permissions(manage_guild=True)
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def approve(
        self,
        context: commands.Context,
        suggestion_id: int,
        *,
        reason="No reason given.",
    ):
        """
        Approve a suggestion.
        """
        if len(reason) > 1024:
            return await context.send(
                content="Your reason must be less than 1024 characters."
            )

        suggestion_id = str(suggestion_id)
        data = await self.config.guild(context.guild).all()
        if not data["suggestions"].get(suggestion_id):
            return await context.send(
                content="It appears the suggestion with that ID does not exist."
            )
        if data["auto_delete"]:
            with contextlib.suppress(discord.errors.Forbidden):
                await context.message.delete()
        et = await self.end_suggestion(context, "approved", suggestion_id, reason)
        if et == "done":
            await context.send(
                content="It appears this suggestion was already approved or rejected."
            )
        elif et == "notfound":
            await context.send(
                content="The suggestion message for this ID could not be found. "
                "Perhaps it was deleted or I do not have permission to view, edit or send in the "
                "suggestion channel."
            )
        elif et == "nochan":
            await context.send(
                content="The suggestion channel for this ID could not be found."
            )
        elif et == "error":
            await context.send(
                content="Error occurred while editting suggestion, please check my permissions."
            )

    @commands.command(name="reject")
    @commands.admin_or_permissions(manage_guild=True)
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def reject(
        self,
        context: commands.Context,
        suggestion_id: int,
        *,
        reason="No reason given.",
    ):
        """
        Reject a suggestion.
        """
        if len(reason) > 1024:
            return await context.send(
                content="Your reason must be less than 1024 characters."
            )

        suggestion_id = str(suggestion_id)
        data = await self.config.guild(context.guild).all()
        if not data["suggestions"].get(suggestion_id):
            return await context.send(
                content="It appears the suggestion with that ID does not exist."
            )
        if data["auto_delete"]:
            with contextlib.suppress(discord.errors.Forbidden):
                await context.message.delete()
        et = await self.end_suggestion(context, "rejected", suggestion_id, reason)
        if et == "done":
            return await context.send(
                content="It appears this suggestion was already approved or rejected."
            )
        elif et == "notfound":
            await context.send(
                content="The suggestion message for this ID could not be found. "
                "Perhaps it was deleted or I do not have permission to view, edit or send in the "
                "suggestion channel."
            )
        elif et == "nochan":
            await context.send(
                content="The suggestion channel for this ID could not be found."
            )
        elif et == "error":
            await context.send(
                content="Error occurred while editting suggestion, please check my permissions."
            )

    @commands.command(name="suggestview", aliases=["sv"])
    async def suggestview(self, context: commands.Context, suggestion_id: int):
        """
        Check who downvoted or upvoted from a suggestion.
        """
        suggestion_id = str(suggestion_id)
        data = await self.config.guild(context.guild).all()
        if not data["channels"]["suggest"]:
            return await context.send(
                content="No suggestion channel found, ask an admin to set one,"
            )
        suggestions: dict = data["suggestions"]
        if not suggestions:
            return await context.send(content="No suggestions have been submitted yet.")
        suggest_data = suggestions.get(suggestion_id)
        if not suggest_data:
            return await context.send(content="Suggestion for this ID does not exist.")
        channel = context.guild.get_channel(suggest_data["channel_id"])
        if not channel:
            return await context.send(
                content="The suggestion channel for this ID could not be found."
            )
        try:
            msg = await channel.fetch_message(suggest_data["message_id"])
        except (discord.errors.NotFound, discord.errors.Forbidden):
            return await context.send(
                content="The suggestion message for this ID could not be found. "
                "Perhaps it was deleted or I do not have permission to view, edit or send in the "
                "suggestion channel."
            )
        mem = context.guild.get_member(suggest_data["suggester_id"])
        rev = context.guild.get_member(suggest_data["reviewer_id"])
        embed = await self.make_embed(
            title=f"Suggestion **#{suggestion_id}**",
            desc=suggest_data["suggestion"],
            colour=await context.embed_colour()
            if suggest_data["status"] == "running"
            else discord.Colour.green()
            if suggest_data["status"] == "approved"
            else discord.Colour.red(),
            authname=f"{mem} ({mem.id})" if mem else "[Unknown or Deleted User]",
            authic=nu.is_have_avatar(mem or context.guild),
            stattype=suggest_data["status"],
            reviewer=None
            if suggest_data["status"] == "running"
            else rev.mention
            if rev
            else "[Unknown or Deleted User]",
            reason=suggest_data["reason"],
            results=(
                f"{data['emojis']['upvote']}: {len(suggest_data['upvotes'])}\n"
                f"{data['emojis']['downvote']}: {len(suggest_data['downvotes'])}"
            )
            if suggest_data["status"] != "running"
            else None,
        )
        u = f"https://discord.com/channels/{context.guild.id}/{channel.id}/{msg.id}"
        view = SuggestionViewView()
        view.DownVotesButton.emoji = data["emojis"]["downvote"]
        view.UpVotesButton.emoji = data["emojis"]["upvote"]
        view.DownVotesButton.label = f"{len(suggest_data['downvotes'])} Down Voters"
        view.UpVotesButton.label = f"{len(suggest_data['upvotes'])} Up Voters"
        view.DownVotesButton.style = nu.get_button_colour(
            data["button_colour"]["downbutton"]
        )
        view.UpVotesButton.style = nu.get_button_colour(
            data["button_colour"]["upbutton"]
        )
        view.add_item(discord.ui.Button(label="Jump To Suggestion", url=u))
        await view.start(
            context,
            suggestion_id,
            suggest_data["upvotes"],
            suggest_data["downvotes"],
            embed=embed,
        )

    @commands.group(name="suggestionset", aliases=["suggestset"])
    @commands.admin_or_permissions(manage_guild=True)
    @commands.bot_has_permissions(embed_links=True)
    @commands.guild_only()
    async def suggestionset(self, context: commands.Context):
        """
        Configure the suggestion cog.
        """
        pass

    @suggestionset.command(name="editreason")
    async def suggestionset_editreason(
        self, context: commands.Context, suggestion_id: int, *, reason: str
    ):
        """
        Edit a suggestions reason.
        """
        if len(reason) > 1024:
            return await context.send(
                content="Your reason must be less than 1024 characters."
            )

        suggestion_id = str(suggestion_id)
        data = await self.config.guild(context.guild).all()
        if not data["channels"]["suggest"]:
            return await context.send(
                content="No suggestion channel found, ask an admin to set one,"
            )
        if not data["suggestions"]:
            return await context.send(content="No suggestions have been submitted yet.")
        if not data["suggestions"].get(suggestion_id):
            return await context.send(content="Suggestion for this ID does not exist.")

        async with self.config.guild(context.guild).suggestions() as s:
            suggest_data = s[suggestion_id]
            if suggest_data["status"] == "running":
                return await context.send(
                    content="It appears that suggestion has not been rejected or approved yet."
                )
            channel = context.guild.get_channel(suggest_data["channel_id"])
            if not channel:
                return await context.send(
                    content="The suggestion channel for this ID could not be found."
                )
            try:
                msg = await channel.fetch_message(suggest_data["message_id"])
            except (discord.errors.NotFound, discord.errors.Forbidden):
                return await context.send(
                    content="The suggestion message for this ID could not be found. "
                    "Perhaps it was deleted or I do not have permission to view, edit or send in the "
                    "suggestion channel."
                )
            suggest_data["reason"] = reason
            rev = context.guild.get_member(suggest_data["reviewer_id"])
            mem = context.guild.get_member(suggest_data["suggester_id"])
            embed = await self.make_embed(
                title=f"Suggestion **#{suggestion_id}**",
                desc=suggest_data["suggestion"],
                colour=discord.Colour.green()
                if suggest_data["status"] == "approved"
                else discord.Colour.red(),
                authname=f"{mem} ({mem.id})" if mem else "[Unknown or Deleted User]",
                authic=nu.is_have_avatar(mem or context.guild),
                stattype=suggest_data["status"],
                reviewer=rev.mention if rev else "[Unknown or Deleted User]",
                reason=reason,
            )
            try:
                await self.edit_message(
                    msg,
                    embed,
                    label1=str(len(suggest_data["upvotes"])),
                    label2=str(len(suggest_data["downvotes"])),
                )
            except discord.errors.Forbidden:
                return await context.send(
                    content="Error has occurred while editting the suggestion message."
                )

        if data["auto_delete"]:
            with contextlib.suppress(discord.errors.Forbidden):
                await context.message.delete()
                await context.channel.send(
                    content=f"The reason for suggestion **#{suggestion_id}** has been successfully changed.",
                    delete_after=5,
                )
            return
        await context.send(
            content=f"The reason for suggestion **#{suggestion_id}** has been successfully changed."
        )

    @suggestionset.command(name="buttoncolor", aliases=["buttoncolour"])
    async def suggestionset_buttoncolor(
        self,
        context: commands.Context,
        types: Literal["upvote", "downvote"],
        colour: Literal["red", "green", "blurple", "grey"] = None,
    ):
        """
        Change the upvote or downvotes button colour.

        Leave `colour` blank to reset the colour of the type you put.

        Available colours:
        - red
        - green
        - blurple
        - grey
        """
        if types == "upvote":
            if not colour:
                await self.config.guild(context.guild).button_colour.upbutton.clear()
                return await context.send(
                    content="Successfully reset the upvote button color to blurple."
                )
            await self.config.guild(context.guild).button_colour.upbutton.set(colour)
            await context.send(
                content=f"The upvote button colour has been set to {colour}."
            )
        if types == "downvote":
            if not colour:
                await self.config.guild(context.guild).button_colour.downbutton.clear()
                return await context.send(
                    content="Successfully reset the downvote button color to blurple."
                )
            await self.config.guild(context.guild).button_colour.downbutton.set(colour)
            await context.send(
                content=f"The downvote button colour has been set to {colour}."
            )

    @suggestionset.command(name="channel", aliases=["chan"])
    async def suggestionset_channel(
        self,
        context: commands.Context,
        type: Literal["suggest", "reject", "approve"],
        channel: discord.TextChannel = None,
    ):
        """
        Set the suggestion channel.

        Leave channel blank to remove the current set channel on what type you used.
        Rejection channel and Approved channel are optional.
        """
        if channel and not channel.permissions_for(context.guild.me).send_messages:
            return await context.send(
                "I do not have permission to send messages in that channel."
            )
        if type == "suggest":
            if not channel:
                await self.config.guild(context.guild).channels.suggest.clear()
                return await context.send(
                    content="The suggestion channel has been removed."
                )
            await self.config.guild(context.guild).channels.suggest.set(channel.id)
            await context.send(
                f"Successfully set {channel.mention} as the suggestion channel."
            )
        elif type == "reject":
            if not channel:
                await self.config.guild(context.guild).channels.reject.clear()
                return await context.send(
                    content="The rejected suggestions channel has been removed."
                )
            await self.config.guild(context.guild).channels.reject.set(channel.id)
            await context.send(
                f"Successfully set {channel.mention} as the rejected suggestions channel."
            )
        elif type == "approve":
            if not channel:
                await self.config.guild(context.guild).channels.approve.clear()
                return await context.send(
                    content="The approved suggestions channel has been removed."
                )
            await self.config.guild(context.guild).channels.approve.set(channel.id)
            await context.send(
                f"Successfully set {channel.mention} as the approved suggestions channel."
            )

    @suggestionset.command(name="emoji")
    @commands.bot_has_permissions(use_external_emojis=True)
    async def suggestionset_emoji(
        self,
        context: commands.Context,
        vote: Literal["upvote", "downvote"],
        emoji: nu.NoobEmojiConverter = None,
    ):
        """
        Change the UpVote or DownVote emoji.
        """
        if vote not in ["upvote", "downvote"]:
            return await context.send_help()

        vote_emojis = self.config.guild(context.guild).emojis

        if not emoji:
            await vote_emojis.upvote.clear() if vote == "upvote" else await vote_emojis.downvote.clear()
            emoji_name = "UpVote" if vote == "upvote" else "DownVote"
            emoji_value = (
                await vote_emojis.upvote()
                if vote == "upvote"
                else await vote_emojis.downvote()
            )
            return await context.send(
                f"The {emoji_name} emoji has been reset to: {emoji_value}"
            )

        await vote_emojis.upvote.set(
            str(emoji)
        ) if vote == "upvote" else await vote_emojis.downvote.set(str(emoji))
        emoji_name = "UpVote" if vote == "upvote" else "DownVote"
        await context.send(f"Successfully set the {emoji_name} emoji to: {emoji}")

    @suggestionset.command(name="reset")
    async def suggestionset_reset(self, context: commands.Context):
        """
        Reset the guilds settings to default.
        """
        act = "Successfully reset the guilds whole configuration."
        conf = "Are you sure you want to reset the guilds whole confirguration?"
        view = nu.NoobConfirmation()
        await view.start(context, act, content=conf)

        await view.wait()

        if view.value is True:
            await self.config.guild(context.guild).clear()

    @suggestionset.command(name="resetcog")
    @commands.is_owner()
    async def suggestionset_resetcog(self, context: commands.Context):
        """
        Reset the whole cogs configuration.
        """
        act = "Successfully reset the cogs whole configuration."
        conf = "Are you sure you want to reset the cogs whole confirguration?"
        view = nu.NoobConfirmation()
        await view.start(context, act, content=conf)

        await view.wait()

        if view.value:
            await self.config.clear_all_guilds()

    @suggestionset.command(name="autodelete", aliases=["autodel"])
    async def suggestionset_autodelete(self, context: commands.Context):
        """
        Toggle whether to automatically delete suggestion commands or not.
        """
        current = await self.config.guild(context.guild).auto_delete()
        await self.config.guild(context.guild).auto_delete.set(not current)
        status = "will not" if current else "will now"
        await context.send(
            content=f"I {status} automatically delete the suggestion commands."
        )

    @suggestionset.command(name="allowselfvote", aliases=["asv"])
    async def suggestionset_allowselfvote(self, context: commands.Context):
        """
        Toggle whether to allow suggestion authors to upvote or downvote their own suggestion or not.
        """
        current = await self.config.guild(context.guild).self_vote()
        await self.config.guild(context.guild).self_vote.set(not current)
        status = "can no longer" if current else "can now"
        await context.send(
            content=f"Suggestion authors {status} upvote or downvote their own suggestion."
        )

    @suggestionset.command(name="showsettings", aliases=["ss"])
    async def suggestionset_showsettings(self, context: commands.Context):
        """
        Show the current suggestion cogs guild settings.
        """
        data = await self.config.guild(context.guild).all()
        emojis = data["emojis"]
        button_colour = data["button_colour"]
        channels = {
            "Suggestion": data["channels"]["suggest"],
            "Rejection": data["channels"]["reject"],
            "Approved": data["channels"]["approve"],
        }

        channels_text = {
            key: f"<#{value}>" if value else "None" for key, value in channels.items()
        }

        embed = discord.Embed(
            title=f"{context.guild}'s current suggestion settings",
            description=f"**Auto delete commands:** {data['auto_delete']}\n"
            f"**Allow Self Vote:** {data['self_vote']}\n"
            f"**Upvote Button:**\n"
            f"` - ` Emoji: {emojis['upvote']}\n"
            f"` - ` Colour: {button_colour['upbutton']}\n"
            f"**Downvote emoji:**\n"
            f"` - ` Emoji: {emojis['downvote']}\n"
            f"` - ` Colour: {button_colour['downbutton']}\n"
            f"**Suggestion channel:** {channels_text['Suggestion']}\n"
            f"**Rejection channel:** {channels_text['Rejection']}\n"
            f"**Approved channel:** {channels_text['Approved']}",
            colour=await context.embed_colour(),
            timestamp=discord.utils.utcnow(),
        )

        await context.send(embed=embed)
