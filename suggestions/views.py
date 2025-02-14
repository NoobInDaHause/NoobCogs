import discord
import noobutils as nu

from redbot.core.bot import commands, Red

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from . import Suggestions


class SuggestionView(discord.ui.View):
    def __init__(self, cog: "Suggestions", suggestion_id: str):
        super().__init__(timeout=None)
        self.cog = cog
        self.suggestion_id: str = suggestion_id

    @discord.ui.button(custom_id="upbutton")
    async def upvote_button(
        self, interaction: discord.Interaction[Red], button: discord.ui.Button
    ):
        guild_data = await self.cog.config.guild(interaction.guild).all()
        async with self.cog.config.guild(
            interaction.guild
        ).suggestions() as suggestions:
            suggest_data = suggestions[self.suggestion_id]
            if interaction.user.id in suggest_data["downvotes"]:
                suggest_data["downvotes"].remove(interaction.user.id)
                suggest_data["upvotes"].append(interaction.user.id)
                message = "You have changed your vote to upvote."
            elif interaction.user.id in suggest_data["upvotes"]:
                suggest_data["upvotes"].remove(interaction.user.id)
                message = "You have removed your vote on this suggestion."
            else:
                suggest_data["upvotes"].append(interaction.user.id)
                message = "You have upvoted this suggestion."

            button.label = str(len(suggest_data["upvotes"]))
            button.emoji = guild_data["emojis"]["upvote"]
            button.style = nu.get_button_colour(guild_data["button_colour"]["upbutton"])

            self.downvote_button.label = str(len(suggest_data["downvotes"]))
            self.downvote_button.emoji = guild_data["emojis"]["downvote"]
            self.downvote_button.style = nu.get_button_colour(
                guild_data["button_colour"]["downbutton"]
            )

            await interaction.response.edit_message(view=self)
            await interaction.followup.send(content=message, ephemeral=True)

    @discord.ui.button(custom_id="downbutton")
    async def downvote_button(
        self, interaction: discord.Interaction[Red], button: discord.ui.Button
    ):
        guild_data = await self.cog.config.guild(interaction.guild).all()
        async with self.cog.config.guild(
            interaction.guild
        ).suggestions() as suggestions:
            suggest_data = suggestions[self.suggestion_id]
            if interaction.user.id in suggest_data["upvotes"]:
                suggest_data["upvotes"].remove(interaction.user.id)
                suggest_data["downvotes"].append(interaction.user.id)
                message = "You have changed your vote to downvote."
            elif interaction.user.id in suggest_data["downvotes"]:
                suggest_data["downvotes"].remove(interaction.user.id)
                message = "You have removed your vote on this suggestion."
            else:
                suggest_data["downvotes"].append(interaction.user.id)
                message = "You have downvoted this suggestion."

            button.label = str(len(suggest_data["downvotes"]))
            button.emoji = guild_data["emojis"]["downvote"]
            button.style = nu.get_button_colour(
                guild_data["button_colour"]["downbutton"]
            )

            self.upvote_button.label = str(len(suggest_data["upvotes"]))
            self.upvote_button.emoji = guild_data["emojis"]["upvote"]
            self.upvote_button.style = nu.get_button_colour(
                guild_data["button_colour"]["upbutton"]
            )

            await interaction.response.edit_message(view=self)
            await interaction.followup.send(content=message, ephemeral=True)

    async def interaction_check(self, interaction: discord.Interaction[Red]) -> bool:
        if await self.cog.config.guild(interaction.guild).self_vote():
            return True
        suggestions = await self.cog.config.guild(interaction.guild).suggestions()
        data = suggestions[self.suggestion_id]
        if interaction.user.id != data["suggester_id"]:
            return True
        await interaction.response.send_message(
            content="Admins have disabled suggestion self voting in this guild so "
            "you can not upvote or downvote your own suggestion.",
            ephemeral=True,
        )
        return False


class SuggestionViewView(nu.NoobView):
    def __init__(self, context: commands.Context, timeout: float = 180.0):
        super().__init__(obj=context, timeout=timeout)
        self.suggestion_id: str = None
        self.message: discord.Message = None
        self.upvotes: List[discord.Member] = None
        self.downvotes: List[discord.Member] = None

    async def start(
        self,
        suggestion_id,
        upvotes,
        downvotes,
        *args,
        **kwargs,
    ):
        self.message = await self.context.send(view=self, *args, **kwargs)
        self.suggestion_id = suggestion_id
        self.upvotes = [m for mm in upvotes if (m := self.context.guild.get_member(mm))]
        self.downvotes = [n for nn in downvotes if (n := self.context.guild.get_member(nn))]

    @discord.ui.button()
    async def UpVotesButton(
        self, interaction: discord.Interaction[Red], button: discord.ui.Button
    ):
        du = "\n".join(
            [f"{member.mention} {member.name} ({member.id})" for member in self.upvotes]
            or ["No one has upvoted this suggestion yet."]
        )

        pages = nu.pagify_this(
            du,
            ["\n"],
            "Page ({index}/{pages})",
            embed_colour=await self.context.embed_colour(),
            embed_title=f"{len(self.upvotes)} members have upvoted the suggestion **#{self.suggestion_id}**",
        )
        await nu.NoobPaginator(obj=interaction, pages=pages, is_ephemeral=True).start()

    @discord.ui.button(emoji="✖️", style=nu.get_button_colour("red"))
    async def quit_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()
        await self.message.delete()
        self.stop()

    @discord.ui.button()
    async def DownVotesButton(
        self, interaction: discord.Interaction[Red], button: discord.ui.Button
    ):
        dv = "\n".join(
            [
                f"{member.mention} {member.name} ({member.id})"
                for member in self.downvotes
            ]
            or ["No one has upvoted this suggestion yet."]
        )

        pages = nu.pagify_this(
            dv,
            ["\n"],
            "Page ({index}/{pages})",
            embed_colour=await self.context.embed_colour(),
            embed_title=f"{len(self.downvotes)} members have downvoted the suggestion **#{self.suggestion_id}**",
            footer_icon=nu.is_have_avatar(interaction.guild),
        )
        await nu.NoobPaginator(obj=interaction, pages=pages, is_ephemeral=True).start()

    async def on_timeout(self):
        self.DownVotesButton.disabled = True
        self.UpVotesButton.disabled = True
        self.quit_button.disabled = True
        await self.message.edit(view=self)
        self.stop()
