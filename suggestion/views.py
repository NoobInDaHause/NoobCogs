import discord
import noobutils as nu

from redbot.core import commands

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from . import Suggestion


class SuggestView(discord.ui.View):
    def __init__(self, cog: commands.Cog):
        super().__init__(timeout=None)
        self.cog: Suggestion = cog

    @discord.ui.button(custom_id="up_persistent_button")
    async def up_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        data = await self.cog.config.guild(interaction.guild).all()
        async with self.cog.config.guild(interaction.guild).suggestions() as s:
            for i in s:
                if interaction.message.id == i["msg_id"]:
                    if (
                        interaction.user.id in i["downvotes"]
                        and interaction.user.id not in i["upvotes"]
                    ):
                        index = i["downvotes"].index(interaction.user.id)
                        i["downvotes"].pop(index)
                        i["upvotes"].append(interaction.user.id)
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
                        return await interaction.followup.send(
                            content="You have changed your vote to upvote.",
                            ephemeral=True,
                        )

                    elif interaction.user.id in i["upvotes"]:
                        upindex = i["upvotes"].index(interaction.user.id)
                        i["upvotes"].pop(upindex)
                        button.label = str(len(i["upvotes"]))
                        button.emoji = data["emojis"]["upvote"]
                        button.style = nu.get_button_colour(
                            data["button_colour"]["upbutton"]
                        )
                        await interaction.response.edit_message(view=self)
                        return await interaction.followup.send(
                            content="You have removed your vote on this suggestion.",
                            ephemeral=True,
                        )
                    else:
                        i["upvotes"].append(interaction.user.id)
                        button.label = str(len(i["upvotes"]))
                        button.emoji = data["emojis"]["upvote"]
                        button.style = nu.get_button_colour(
                            data["button_colour"]["upbutton"]
                        )
                        await interaction.response.edit_message(view=self)
                        await interaction.followup.send(
                            content="You have upvoted this suggestion.", ephemeral=True
                        )

    @discord.ui.button(custom_id="down_persistent_button")
    async def down_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        data = await self.cog.config.guild(interaction.guild).all()
        async with self.cog.config.guild(interaction.guild).suggestions() as s:
            for i in s:
                if interaction.message.id == i["msg_id"]:
                    if (
                        interaction.user.id in i["upvotes"]
                        and interaction.user.id not in i["downvotes"]
                    ):
                        index = i["upvotes"].index(interaction.user.id)
                        i["upvotes"].pop(index)
                        i["downvotes"].append(interaction.user.id)
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
                        await interaction.followup.send(
                            content="You have changed your vote to downvote.",
                            ephemeral=True,
                        )

                    elif interaction.user.id in i["downvotes"]:
                        downindex = i["downvotes"].index(interaction.user.id)
                        i["downvotes"].pop(downindex)
                        button.label = str(len(i["downvotes"]))
                        button.emoji = data["emojis"]["downvote"]
                        button.style = nu.get_button_colour(
                            data["button_colour"]["downbutton"]
                        )
                        await interaction.response.edit_message(view=self)
                        await interaction.followup.send(
                            content="You have removed your vote on this suggestion.",
                            ephemeral=True,
                        )
                    else:
                        i["downvotes"].append(interaction.user.id)
                        button.label = str(len(i["downvotes"]))
                        button.emoji = data["emojis"]["downvote"]
                        button.style = nu.get_button_colour(
                            data["button_colour"]["downbutton"]
                        )
                        await interaction.response.edit_message(view=self)
                        await interaction.followup.send(
                            content="You have downvoted this suggestion.",
                            ephemeral=True,
                        )


class SuggestVotersView(discord.ui.View):
    def __init__(self, timeout: Optional[float] = 60.0):
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

    @discord.ui.button(label="Down Voters")
    async def DownVotesButton(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        dv = "\n".join(
            [f"<@{i}> ({i})" for i in self.downvotes]
            if self.downvotes
            else ["No one has downvoted this sugegstion yet."]
        )
        pages = await nu.pagify_this(
            dv,
            ["\n"],
            "Page ({index}/{pages})",
            embed_colour=await self.context.embed_colour(),
            embed_title=f"List of members who downvoted suggestion #{self.suggestion_id}",
            footer_icon=nu.is_have_avatar(interaction.guild),
        )
        pag = nu.NoobPaginator(pages)
        await pag.start(interaction, ephemeral=True)

    @discord.ui.button(label="Up Voters")
    async def UpVotesButton(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        du = "\n".join(
            [f"<@{i}> ({i})" for i in self.upvotes]
            if self.upvotes
            else ["No one has upvoted this suggestion yet."]
        )
        pages = await nu.pagify_this(
            du,
            ["\n"],
            "Page ({index}/{pages})",
            embed_colour=await self.context.embed_colour(),
            embed_title=f"List of members who upvoted suggestion #{self.suggestion_id}",
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
        for x in self.children:
            x.disabled = True
        self.stop()
        await self.message.edit(view=self)
