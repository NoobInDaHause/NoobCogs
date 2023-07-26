import discord

from redbot.core import commands

from noobutils import get_button_colour

class SuggestView(discord.ui.View):
    def __init__(self, cog: commands.Cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(label="0", custom_id="up_suggest_button")
    async def up_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = await self.cog.config.guild(interaction.guild).all()
        async with self.cog.config.guild(interaction.guild).suggestions() as s:
            for i in s:
                if interaction.message.id == i["msg_id"]:
                    if interaction.user.id in i["downvotes"] and interaction.user.id not in i["upvotes"]:
                        index = i["downvotes"].index(interaction.user.id)
                        i["downvotes"].pop(index)
                        i["upvotes"].append(interaction.user.id)
                        button.label = str(len(i["upvotes"]))
                        button.emoji = data["emojis"]["upvote"]
                        button.style = get_button_colour(data["button_colour"]["upbutton"])
                        self.down_button.label = str(len(i["downvotes"]))
                        self.down_button.emoji = data["emojis"]["downvote"]
                        self.down_button.style = get_button_colour(data["button_colour"]["downbutton"])
                        await interaction.response.edit_message(view=self)
                        return await interaction.followup.send(
                            content="You have changed your vote to upvote.", ephemeral=True
                        )

                    if interaction.user.id in i["upvotes"]:
                        return await interaction.response.send_message(
                            content="You already upvoted this suggestion feel free to change vote by clicking "
                            "the downvote button.", ephemeral=True
                        )

                    i["upvotes"].append(interaction.user.id)
                    button.label = str(len(i["upvotes"]))
                    button.emoji = data["emojis"]["upvote"]
                    button.style = get_button_colour(data["button_colour"]["upbutton"])
                    await interaction.response.edit_message(view=self)
                    await interaction.followup.send(
                        content="You have upvoted this suggestion.", ephemeral=True
                    )

    @discord.ui.button(label="0", custom_id="down_suggest_button")
    async def down_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = await self.cog.config.guild(interaction.guild).all()
        async with self.cog.config.guild(interaction.guild).suggestions() as s:
            for i in s:
                if interaction.message.id == i["msg_id"]:
                    if interaction.user.id in i["upvotes"] and interaction.user.id not in i["downvotes"]:
                        index = i["upvotes"].index(interaction.user.id)
                        i["upvotes"].pop(index)
                        i["downvotes"].append(interaction.user.id)
                        button.label = str(len(i["downvotes"]))
                        button.emoji = data["emojis"]["downvote"]
                        button.style = get_button_colour(data["button_colour"]["downbutton"])
                        self.up_button.label = str(len(i["upvotes"]))
                        self.up_button.emoji = data["emojis"]["upvote"]
                        self.up_button.style = get_button_colour(data["button_colour"]["upbutton"])
                        await interaction.response.edit_message(view=self)
                        return await interaction.followup.send(
                            content="You have changed your vote to downvote.", ephemeral=True
                        )

                    if interaction.user.id in i["downvotes"]:
                        return await interaction.response.send_message(
                            content="You already downvoted this suggestion feel free to change vote by clicking "
                            "the upvote button.", ephemeral=True
                        )

                    i["downvotes"].append(interaction.user.id)
                    button.label = str(len(i["downvotes"]))
                    button.emoji = data["emojis"]["downvote"]
                    button.style = get_button_colour(data["button_colour"]["downbutton"])
                    await interaction.response.edit_message(view=self)
                    await interaction.followup.send(
                        content="You have downvoted this suggestion.", ephemeral=True
                    )
