import discord
import noobutils as nu

from redbot.core import commands

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Suggestion


class SuggestView(discord.ui.View):
    def __init__(self, cog: "Suggestion"):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(custom_id="up_persistent_button")
    async def up_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        data = await self.cog.config.guild(interaction.guild).all()
        async with self.cog.config.guild(interaction.guild).suggestions() as s:
            for i in s:
                if interaction.message.id == i["msg_id"]:
                    if interaction.user.id in i["downvotes"]:
                        i["downvotes"].remove(interaction.user.id)
                        i["upvotes"].append(interaction.user.id)
                        message = "You have changed your vote to upvote."
                    elif interaction.user.id in i["upvotes"]:
                        i["upvotes"].remove(interaction.user.id)
                        message = "You have removed your vote on this suggestion."
                    else:
                        i["upvotes"].append(interaction.user.id)
                        message = "You have upvoted this suggestion."

                    button.label = str(len(i["upvotes"]))
                    button.emoji = data["emojis"]["upvote"]
                    button.style = nu.get_button_colour(
                        data["button_colour"]["upbutton"]
                    )

                    self.down_button.label = str(len(i["downvotes"]))
                    self.down_button.emoji = data["emojis"]["downvote"]
                    self.down_button.style = nu.get_button_colour(
                        data["button_colour"]["downbutton"]
                    )

                    await interaction.response.edit_message(view=self)
                    await interaction.followup.send(content=message, ephemeral=True)

    @discord.ui.button(custom_id="down_persistent_button")
    async def down_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        data = await self.cog.config.guild(interaction.guild).all()
        async with self.cog.config.guild(interaction.guild).suggestions() as s:
            for i in s:
                if interaction.message.id == i["msg_id"]:
                    if interaction.user.id in i["upvotes"]:
                        i["upvotes"].remove(interaction.user.id)
                        i["downvotes"].append(interaction.user.id)
                        message = "You have changed your vote to downvote."
                    elif interaction.user.id in i["downvotes"]:
                        i["downvotes"].remove(interaction.user.id)
                        message = "You have removed your vote on this suggestion."
                    else:
                        i["downvotes"].append(interaction.user.id)
                        message = "You have downvoted this suggestion."

                    button.label = str(len(i["downvotes"]))
                    button.emoji = data["emojis"]["downvote"]
                    button.style = nu.get_button_colour(
                        data["button_colour"]["downbutton"]
                    )

                    self.up_button.label = str(len(i["upvotes"]))
                    self.up_button.emoji = data["emojis"]["upvote"]
                    self.up_button.style = nu.get_button_colour(
                        data["button_colour"]["upbutton"]
                    )

                    await interaction.response.edit_message(view=self)
                    await interaction.followup.send(content=message, ephemeral=True)

    async def interaction_check(self, interaction: discord.Interaction):
        if await self.cog.config.guild(interaction.guild).self_vote():
            return True
        if suggestions := await self.cog.config.guild(interaction.guild).suggestions():
            for i in suggestions:
                if interaction.message.id == i["msg_id"]:
                    if interaction.user.id != i["suggester_id"]:
                        return True
                    await interaction.response.send_message(
                        content="Admins have restricted suggestion self voting in this guild so "
                        "you can not upvote or downvote your own suggestion.",
                        ephemeral=True,
                    )
                    return False


class SuggestViewView(discord.ui.View):
    def __init__(self, timeout: float = 60.0):
        super().__init__(timeout=timeout)
        self.suggestion_id: int = None
        self.upvotes: list = None
        self.downvotes: list = None
        self.message: discord.Message = None
        self.context: commands.Context = None

    async def start(
        self,
        context: commands.Context,
        suggestion_id: int,
        upvotes: list,
        downvotes: list,
        *args,
        **kwargs,
    ):
        msg = await context.send(view=self, *args, **kwargs)
        self.suggestion_id = suggestion_id
        self.upvotes = upvotes
        self.downvotes = downvotes
        self.context = context
        self.message = msg

    @discord.ui.button()
    async def UpVotesButton(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        upvoters = [
            f"{member.mention} {member.name} ({member.id})"
            for x in self.upvotes
            if (member := interaction.guild.get_member(x))
        ] or ["No one has upvoted this suggestion yet."]

        du = "\n".join(upvoters)

        pages = await nu.pagify_this(
            du,
            ["\n"],
            "Page ({index}/{pages})",
            embed_colour=await self.context.embed_colour(),
            embed_title=f"{len(self.upvotes)} members have upvoted the suggestion **#{self.suggestion_id}**",
        )
        pag = nu.NoobPaginator(pages)
        await pag.start(interaction, ephemeral=True)

    @discord.ui.button(emoji="✖️", style=discord.ButtonStyle.danger)
    async def quit_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.stop()
        await interaction.message.delete()

    @discord.ui.button()
    async def DownVotesButton(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        downvoters = [
            f"{member.mention} {member.name} ({member.id})"
            for x in self.downvotes
            if (member := interaction.guild.get_member(x))
        ] or ["No one has upvoted this suggestion yet."]

        dv = "\n".join(downvoters)

        pages = await nu.pagify_this(
            dv,
            ["\n"],
            "Page ({index}/{pages})",
            embed_colour=await self.context.embed_colour(),
            embed_title=f"{len(self.downvotes)} members have downvoted the suggestion **#{self.suggestion_id}**",
            footer_icon=nu.is_have_avatar(interaction.guild),
        )
        pag = nu.NoobPaginator(pages)
        await pag.start(interaction, ephemeral=True)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if await self.context.bot.is_owner(interaction.user):
            return True

        if interaction.user != self.context.author:
            await interaction.response.send_message(
                content=nu.access_denied(), ephemeral=True
            )
            return False

        return True

    async def on_timeout(self):
        self.DownVotesButton.disabled = True
        self.UpVotesButton.disabled = True
        self.quit_button.disabled = True
        self.stop()
        await self.message.edit(view=self)
