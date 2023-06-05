import contextlib
import datetime
import discord
import logging

from redbot.core import commands, app_commands, Config
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list, box

from typing import Literal, Optional

from .utils import EmojiConverter, is_have_avatar
from .views import SuggestView, Confirmation

class Suggestion(commands.Cog):
    """
    Suggestion system.
    
    Have users submit suggestions to help improve some things.
    """
    def __init__(self, bot: Red) -> None:
        self.bot = bot

        self.config = Config.get_conf(self, identifier=8642187646324, force_registration=True)
        default_guild = {
            "autodel": True,
            "emojis": {
                "upvote": "⬆️",
                "downvote": "⬇️"
            },
            "suggest_channel": None,
            "reject_channel": None,
            "approve_channel": None,
            "suggestions": []
        }
        self.config.register_guild(**default_guild)
        self.log = logging.getLogger("red.NoobCogs.Suggestion")

    __version__ = "1.0.0"
    __author__ = ["Noobindahause#2808"]
    __docs__ = "https://github.com/NoobInDaHause/NoobCogs/blob/red-3.5/suggestion/README.md"

    def format_help_for_context(self, context: commands.Context) -> str:
        """
        Thanks Sinbad and sravan!
        """
        plural = "s" if len(self.__author__) != 0 or 1 else ""
        return f"""{super().format_help_for_context(context)}

        Cog Version: **{self.__version__}**
        Cog Author{plural}: {humanize_list([f'**{auth}**' for auth in self.__author__])}
        Cog Documentation: [[Click here]]({self.__docs__})"""

    async def red_delete_data_for_user(
        self, *, requester: Literal['discord_deleted_user', 'owner', 'user', 'user_strict'], user_id: int
    ):
        for guild in self.bot.guilds:
            async with self.config.guild(guild).suggestions() as s:
                if not s:
                    continue
                for i in s:
                    if user_id == i["suggester_id"]:
                        i["suggester_id"] = None
                    if user_id == i["reviewer_id"]:
                        i["reviewer_id"] = None
                    if user_id in i["upvotes"]:
                        index = i["upvotes"].index(user_id)
                        i["upvotes"].pop(index)
                    if user_id in i["downvotes"]:
                        index = i["downvotes"].index(user_id)
                        i["downvotes"].pop(index)

    async def initialize(self):
        for guild in self.bot.guilds:
            data = await self.config.guild(guild).all()
            if not data["suggestions"]:
                continue
            async with self.config.guild(guild).suggestions() as s:
                for i in s:
                    if i["status"] == "running":
                        channel = guild.get_channel(data["suggest_channel"])
                        msg = await channel.fetch_message(i["msg_id"])
                        context = await self.bot.get_context(msg)
                        self.bot.add_view(
                            SuggestView(
                                downemoji=data["emojis"]["downvote"],
                                upemoji=data["emojis"]["upvote"],
                                ctx=context,
                                msg=msg
                            ),
                            message_id=i["msg_id"]
                        )

    async def maybe_send_to_author(self, member: discord.Member, url: str = None, *args, **kwargs):
        if url:
            view = discord.ui.View()
            view.add_item(discord.ui.Button(label="Jump To Suggestion", url=url))
            await member.send(view=view, *args, **kwargs)
        else:
            await member.send(*args, **kwargs)

    async def maybe_edit_msg(self, msg: discord.Message, embed: discord.Embed, label1: str, label2: str):
        data = await self.config.guild(msg.guild).all()
        view = discord.ui.View()
        but1 = discord.ui.Button(label=label1, style=discord.ButtonStyle.blurple)
        but2 = discord.ui.Button(label=label2, style=discord.ButtonStyle.blurple)
        but1.disabled = True
        but2.disabled = True
        but1.emoji = data["emojis"]["upvote"]
        but2.emoji = data["emojis"]["downvote"]
        view.add_item(but1)
        view.add_item(but2)
        await msg.edit(embed=embed, view=view)

    async def maybe_make_embed(
        self,
        title: str,
        desc: str,
        colour: discord.Colour,
        authname: str,
        authic: str,
        reviewer: str = None,
        stattype: str = None,
        reason: str = None
    ) -> discord.Embed:
        e = discord.Embed(
            title=title,
            description=desc,
            colour=colour,
        )
        e.set_author(name=authname, icon_url=authic)
        if reviewer:
            e.add_field(
                name="Reviewer:",
                value=reviewer,
                inline=True
            )
        if stattype:
            e.add_field(name="Status:", value=stattype.title(), inline=True)
        if reason:
            e.add_field(name="Reason:", value=reason, inline=False)
        return e

    async def add_suggestion(self, context: commands.Context, suggest_msg: discord.Message, suggestion: str):
        async with self.config.guild(context.guild).suggestions() as s:
            sug = {
                "id": len(s) + 1,
                "suggester_id": context.author.id,
                "msg_id": suggest_msg.id,
                "suggestion": suggestion,
                "status": "running",
                "upvotes": [],
                "downvotes": [],
                "reviewer_id": None,
                "reason": None
            }
            s.append(sug)

    async def send_suggestion(self, context: commands.Context, suggestion: str):
        data = await self.config.guild(context.guild).all()
        channel = context.guild.get_channel(data["suggest_channel"])
        embed = await self.maybe_make_embed(
            title=f"Suggestion **#{len(data['suggestions']) + 1}**",
            desc=suggestion,
            colour=await context.embed_colour(),
            authname=f"{context.author} ({context.author.id})",
            authic=is_have_avatar(context.author)
        )
        view = SuggestView(
            downemoji=data["emojis"]["downvote"],
            upemoji=data["emojis"]["upvote"],
            ctx=context
        )
        view.message = await channel.send(embed=embed, view=view)
        await self.add_suggestion(context=context, suggest_msg=view.message, suggestion=suggestion)
        return [embed, view.message.jump_url]

    async def end_suggestion(self, context: commands.Context, status_type: str, id: int, reason: str):
        # sourcery skip: low-code-quality
        data = await self.config.guild(context.guild).all()
        channel = context.guild.get_channel(data["suggest_channel"])
        async with self.config.guild(context.guild).suggestions() as s:
            for i in s:
                if i["id"] == id:
                    if i["status"] != "running":
                        return "done"
                    i["reviewer_id"] = context.author.id
                    i["reason"] = reason
                    i["status"] = status_type
                    try:
                        msg = await channel.fetch_message(i["msg_id"])
                    except discord.errors.NotFound:
                        return "notfound"
                    mem = context.guild.get_member(i["suggester_id"])
                    embed = await self.maybe_make_embed(
                        title=f"Suggestion **#{id}**",
                        desc=i["suggestion"],
                        colour=discord.Colour.green()
                        if status_type == "approved"
                        else discord.Colour.red(),
                        authname=f"{mem} ({mem.id})"
                        if mem
                        else "[Unknown or Deleted User]",
                        authic=is_have_avatar(mem or context.guild),
                        reviewer=str(context.author.mention),
                        stattype=status_type,
                        reason=reason
                    )
                    r = context.guild.get_channel(data["reject_channel"])
                    a = context.guild.get_channel(data["approve_channel"])
                    if r and status_type == "rejected":
                        with contextlib.suppress(discord.errors.Forbidden):
                            viewr = discord.ui.View()
                            viewr.add_item(discord.ui.Button(label="Jump To Suggestion", url=msg.jump_url))
                            await r.send(embed=embed, view=viewr)
                    if a and status_type == "approved":
                        with contextlib.suppress(discord.errors.Forbidden):
                            views = discord.ui.View()
                            views.add_item(discord.ui.Button(label="Jump To Suggestion", url=msg.jump_url))
                            await a.send(embed=embed, view=views)
                    if mem:
                        cont = (
                            f"Your suggestion **#{id}** was `{status_type}` by {context.author} "
                            f"({context.author.id}).\nReason: {reason}"
                        )
                        with contextlib.suppress(discord.errors.Forbidden):
                            await self.maybe_send_to_author(mem, msg.jump_url, cont)
                    try:
                        await self.maybe_edit_msg(msg, embed, str(len(i["upvotes"])), str(len(i["downvotes"])))
                    except discord.errors.Forbidden:
                        return "error"
                    break

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
        data = await self.config.guild(context.guild).all()
        if not data["suggest_channel"]:
            return await context.reply(
                content="No suggestion channel found. Ask an admin to set one.",
                ephemeral=True,
                mention_author=False
            )

        try:
            em = await self.send_suggestion(context=context, suggestion=suggestion)
            if context.prefix == "/":
                await context.reply(
                    content="Successfully submitted.",
                    ephemeral=True
                )
            with contextlib.suppress(discord.errors.Forbidden):
                await self.maybe_send_to_author(
                    context.author,
                    em[1],
                    content="Your suggestion has been submitted for votes and review.",
                    embed=em[0]
                )
        except Exception as e:
            return await context.reply(
                content="An error has occurred while sending the suggestion.\n"
                f"Here is the traceback: {box(e, 'py')}",
                ephemeral=True,
                mention_author=False
            )

        if data["autodel"] and context.prefix != "/":
            with contextlib.suppress(discord.errors.HTTPException):
                await context.message.delete()

    @commands.command(name="approve")
    @commands.admin_or_permissions(manage_guild=True)
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def approve(
        self, context: commands.Context, suggestion_id: int, *, reason: Optional[str] = "No reason given."
    ):
        """
        Approve a suggestion.
        """
        data = await self.config.guild(context.guild).all()

        if suggestion_id > len(data["suggestions"]) or suggestion_id <= 0:
            return await context.send(content="It appears the suggestion with that ID does not exist.")
        if data["autodel"]:
            with contextlib.suppress(discord.errors.Forbidden):
                await context.message.delete()
        et = await self.end_suggestion(context, "approved", suggestion_id, reason)
        if not et:
            return
        if et == "done":
            await context.send(
                content="It appears this suggestion was already approved or rejected."
            )
        elif et == "notfound":
            await context.send(
                content="The suggestion message for this ID could not be found."
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
        self, context: commands.Context, suggestion_id: int, *, reason: Optional[str] = "No reason given."
    ):
        """
        Reject a suggestion.
        """
        data = await self.config.guild(context.guild).all()

        if suggestion_id > len(data["suggestions"]) or suggestion_id <= 0:
            return await context.send(content="It appears the suggestion with that ID does not exist.")
        if data["autodel"]:
            with contextlib.suppress(discord.errors.Forbidden):
                await context.message.delete()
        et = await self.end_suggestion(context, "rejected", suggestion_id, reason)
        if not et:
            return
        elif et == "done":
            return await context.send(
                content="It appears this suggestion was already approved or rejected."
            )
        elif et == "notfound":
            return await context.send(
                content="The suggestion message for this ID could not be found."
            )
        elif et == "error":
            return await context.send(
                content="Error occurred while editting suggestion, please check my permissions."
            )

    @commands.command(name="viewsuggestion")
    @commands.bot_has_permissions(embed_links=True)
    @commands.guild_only()
    async def showsuggestion(self, context: commands.Context, suggestion_id: int):
        # sourcery skip: low-code-quality
        """
        View a suggestion.
        """
        if suggestion_id <= 0:
            return await context.send(content="Suggestion for this ID was not found.")
        data = await self.config.guild(context.guild).all()
        if not data["suggest_channel"]:
            return await context.send(content="No suggestion channel found, ask an admin to set one,")
        channel = context.guild.get_channel(data["suggest_channel"])
        async with self.config.guild(context.guild).suggestions() as s:
            if not s:
                return await context.send(content="No suggestions have been submitted yet.")
            if suggestion_id > len(s):
                return await context.send(content="It appears this suggestion does not exist.")
            for i in s:
                if i["id"] == suggestion_id:
                    try:
                        msg = await channel.fetch_message(i["msg_id"])
                    except discord.errors.NotFound:
                        return await context.send(
                            content="The suggestion message for this ID could not be found."
                        )
                    mem = context.guild.get_member(i["suggester_id"])
                    rev = context.guild.get_member(i["reviewer_id"])
                    embed = await self.maybe_make_embed(
                        title=f"Suggestion **#{suggestion_id}**",
                        desc=i["suggestion"],
                        colour=await context.embed_colour()
                        if i["status"] == "running"
                        else discord.Colour.green()
                        if i["status"] == "approved"
                        else discord.Colour.red(),
                        authname=f"{mem}, ({mem.id})"
                        if mem
                        else "[Unknown or Deleted User]",
                        authic=is_have_avatar(mem or context.guild),
                        reviewer=None
                        if i["status"] == "running"
                        else str(rev.mention)
                        if rev
                        else "[Unknown or Deleted User]",
                        stattype=i["status"]
                        if i["status"] != "running"
                        else None,
                        reason=i["reason"]
                    )
                    view = discord.ui.View()
                    u = f"https://discord.com/channels/{context.guild.id}/{channel.id}/{msg.id}"
                    but1 = discord.ui.Button(label=str(len(i["upvotes"])), style=discord.ButtonStyle.blurple)
                    but2 = discord.ui.Button(
                        label=str(len(i["downvotes"])), style=discord.ButtonStyle.blurple
                    )
                    but1.disabled = True
                    but2.disabled = True
                    but1.emoji = data["emojis"]["upvote"]
                    but2.emoji = data["emojis"]["downvote"]
                    view.add_item(but1)
                    view.add_item(but2)
                    view.add_item(discord.ui.Button(label="Jump To Suggestion", url=u))
                    await context.send(embed=embed, view=view)
                    break

    @commands.group(name="suggestionset", aliases=["suggestset"])
    @commands.admin_or_permissions(manage_guild=True)
    @commands.guild_only()
    async def suggestionset(self, context: commands.Context):
        """
        Configure the suggestion cog.
        """
        pass

    @suggestionset.command(name="editreason")
    async def suggestionset_editreason(self, context: commands.Context, suggestion_id: int, *, reason: str):
        # sourcery skip: low-code-quality
        """
        Edit a suggestions reason.
        """
        data = await self.config.guild(context.guild).all()
        if not data["suggest_channel"]:
            return await context.send(content="No suggestion channel found, ask an admin to set one,")
        if suggestion_id > len(data["suggestions"]) or suggestion_id <= 0:
            return await context.send(content="It appears the suggestion with this ID does not exist.")
        channel = context.guild.get_channel(data["suggest_channel"])
        async with self.config.guild(context.guild).suggestions() as s:
            for i in s:
                if i["id"] == suggestion_id:
                    if i["status"] == "running":
                        return await context.send(
                            content="It appears that suggestion has not been rejected or approved yet."
                        )
                    i["reason"] = reason
                    try:
                        msg = await channel.fetch_message(i["msg_id"])
                    except discord.errors.NotFound:
                        return await context.send(
                            content="The suggestion message for this ID could not be found."
                        )
                    rev = context.guild.get_member(i["reviewer_id"])
                    mem = context.guild.get_member(i["suggester_id"])
                    embed = await self.maybe_make_embed(
                        title=f"Suggestion **#{suggestion_id}**",
                        desc=i["suggestion"],
                        colour=discord.Colour.green()
                        if i["status"] == "approved"
                        else discord.Colour.red(),
                        authname=f"{mem} ({mem.id})"
                        if mem
                        else "[Unknown or Deleted User]",
                        authic=is_have_avatar(mem or context.guild),
                        reviewer=str(rev.mention)
                        if rev
                        else "[Unknown or Deleted User]",
                        stattype=i["status"],
                        reason=i["reason"]
                    )
                    try:
                        await self.maybe_edit_msg(
                            msg, embed, label1=str(len(i["upvotes"])), label2=str(len(i["downvotes"]))
                        )
                    except discord.errors.Forbidden:
                        return await context.send(
                            content="Error has occurred while editting the suggestion message."
                        )

        if data["autodel"]:
            with contextlib.suppress(discord.errors.Forbidden):
                await context.message.delete()

    @suggestionset.command(name="channel", aliases=["chan"])
    async def suggestionset_channel(
        self,
        context: commands.Context,
        type: Literal["suggest", "reject", "approve"],
        channel: Optional[discord.TextChannel]
    ):
        """
        Set the suggestion channel.

        Leave channel blank to remove the current set channel on what type you used.
        """
        if channel and not channel.permissions_for(context.guild.me).send_messages:
            return await context.send("I do not have permission to send messages in that channel.")
        if type == "suggest":
            if not channel:
                await self.config.guild(context.guild).suggest_channel.clear()
                return await context.send(content="The suggestion channel has been removed.")
            await self.config.guild(context.guild).suggest_channel.set(channel.id)
            await context.send(f"Successfully set {channel.mention} as the suggestion channel.")
        elif type == "reject":
            if not channel:
                await self.config.guild(context.guild).reject_channel.clear()
                return await context.send(content="The rejected suggestions channel has been removed.")
            await self.config.guild(context.guild).reject_channel.set(channel.id)
            await context.send(f"Successfully set {channel.mention} as the rejected suggestions channel.")
        elif type == "approve":
            if not channel:
                await self.config.guild(context.guild).approve_channel.clear()
                return await context.send(content="The approved suggestions channel has been removed.")
            await self.config.guild(context.guild).approve_channel.set(channel.id)
            await context.send(f"Successfully set {channel.mention} as the approved suggestions channel.")

    @suggestionset.command(name="emoji")
    @commands.bot_has_permissions(use_external_emojis=True)
    async def suggestionset_emoji(
        self,
        context: commands.Context,
        vote: Literal["upvote", "downvote"],
        emoji: Optional[EmojiConverter]
    ):
        """
        Change the UpVote or DownVote emoji.
        """
        if vote == "upvote":
            if not emoji:
                await self.config.guild(context.guild).emojis.upvote.clear()
                up = await self.config.guild(context.guild).emojis.upvote()
                return await context.send(f"The UpVote emoji has been reset to: {up}")
            await self.config.guild(context.guild).emojis.upvote.set(str(emoji))
            await context.send(f"Successfully set the UpVote emoji to: {emoji}")
        if vote == "downvote":
            if not emoji:
                await self.config.guild(context.guild).emojis.downvote.clear()
                down = await self.config.guild(context.guild).emojis.downvote()
                return await context.send(f"The DownVote emoji has been reset to: {down}")
            await self.config.guild(context.guild).emojis.downvote.set(str(emoji))
            await context.send(f"Successfully set the DownVote emoji to: {emoji}")

    @suggestionset.command(name="reset")
    async def suggestionset_reset(self, context: commands.Context):
        """
        Reset the guilds settings to default.
        """
        act = "Successfully reset the guilds whole configuration."
        conf = "Are you sure you want to reset the guilds whole confirguration?"
        view = Confirmation()
        await view.start(context=context, confirm_action=act, confirmation_msg=conf)

        await view.wait()

        if view.value == "yes":
            await self.config.guild(context.guild).clear()

    @suggestionset.command(name="resetcog")
    @commands.is_owner()
    async def suggestionset_resetcog(self, context: commands.Context):
        """
        Reset the whole cogs configuration.
        """
        act = "Successfully reset the cogs whole configuration."
        conf = "Are you sure you want to reset the cogs whole confirguration?"
        view = Confirmation()
        await view.start(context=context, confirm_action=act, confirmation_msg=conf)

        await view.wait()

        if view.value == "yes":
            await self.config.clear_all()

    @suggestionset.command(name="showsettings", aliases=["ss"])
    async def suggestionset_showsettings(self, context: commands.Context):
        """
        Show the current suggestion cogs guild settings.
        """
        data = await self.config.guild(context.guild).all()
        embed = discord.Embed(
            title=f"{context.guild}'s current suggestion settings",
            description=f"""
            Auto delete commands: {data["autodel"]}
            Upvote emoji: {data['emojis']['upvote']}
            Downvote emoji: {data['emojis']['downvote']}
            Suggestion channel: {f'<#{data["suggest_channel"]}>' if data["suggest_channel"] else 'None'}
            Rejection channel: {f'<#{data["reject_channel"]}>' if data["reject_channel"] else 'None'}
            Approved channel: {f'<#{data["approve_channel"]}>' if data["approve_channel"] else 'None'}
            """,
            colour=await context.embed_colour(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        await context.send(embed=embed)
