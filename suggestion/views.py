import discord

from redbot.core import commands, Config

from typing import Optional

from .utils import access_denied

class Confirmation(discord.ui.View):
    def __init__(
        self,
        timeout: Optional[float] = 60
    ):
        super().__init__(timeout=timeout)
        self.confirm_action: str = None
        self.context: commands.Context = None
        self.message: discord.Message = None
        self.value = None

    async def start(self, context: commands.Context, confirmation_msg: str, confirm_action: str):
        msg = await context.send(content=confirmation_msg, view=self)
        self.confirm_action = confirm_action
        self.context = context
        self.message = msg

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        for x in self.children:
            x.disabled = True
        self.value = "yes"
        self.stop()
        await interaction.response.edit_message(content=self.confirm_action, view=self)

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        for x in self.children:
            x.disabled = True
        self.value = "no"
        self.stop()
        await interaction.response.edit_message(content="Alright not doing that then.", view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if await self.context.bot.is_owner(interaction.user):
            return True
        elif interaction.user != self.context.author:
            await interaction.response.send_message(content=access_denied(), ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        for x in self.children:
            x.disabled = True
        self.stop()
        await self.message.edit(content="You took too long to respond.", view=self)

class SuggestView(discord.ui.View):
    def __init__(self, downemoji: str, upemoji: str):
        super().__init__(timeout=None)
        self.channel: discord.TextChannel = None
        self.message: discord.Message = None
        self.context: commands.Context = None
        self.config: Config = None
        self.up_button.emoji = upemoji
        self.down_button.emoji = downemoji

    async def start(
        self, context: commands.Context, channel: discord.TextChannel, config: Config, *args, **kwargs
    ):
        msg = await channel.send(view=self, *args, **kwargs)
        self.channel = channel
        self.config = config
        self.context = context
        self.message = msg

    @discord.ui.button(label="0", style=discord.ButtonStyle.blurple, custom_id="up_button")
    async def up_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with self.config.guild(interaction.guild).suggestions() as s:
            for i in s:
                if interaction.message.id != i["msg_id"]:
                    continue
                if interaction.user.id in i["downvotes"] and interaction.user.id not in i["upvotes"]:
                    index = i["downvotes"].index(interaction.user.id)
                    i["downvotes"].pop(index)
                    i["upvotes"].append(interaction.user.id)
                    button.label = str(len(i["upvotes"]))
                    self.down_button.label = str(len(i["downvotes"]))
                    await self.message.edit(view=self)
                    return await interaction.response.send_message(
                        content="You have changed your vote to upvote.", ephemeral=True
                    )

                if interaction.user.id in i["upvotes"]:
                    return await interaction.response.send_message(
                        content="You already upvoted this suggestion feel free to change vote by clicking "
                        "the downvote button.", ephemeral=True
                    )

                i["upvotes"].append(interaction.user.id)
                button.label = str(len(i["upvotes"]))
                await self.message.edit(view=self)
                await interaction.response.send_message(
                    content="You have upvoted this suggestion.", ephemeral=True
                )

    @discord.ui.button(label="0", style=discord.ButtonStyle.blurple, custom_id="down_button")
    async def down_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        async with self.config.guild(interaction.guild).suggestions() as s:
            for i in s:
                if interaction.message.id != i["msg_id"]:
                    continue
                if interaction.user.id in i["upvotes"] and interaction.user.id not in i["downvotes"]:
                    index = i["upvotes"].index(interaction.user.id)
                    i["upvotes"].pop(index)
                    i["downvotes"].append(interaction.user.id)
                    button.label = str(len(i["downvotes"]))
                    self.down_button.label = str(len(i["upvotes"]))
                    await self.message.edit(view=self)
                    return await interaction.response.send_message(
                        content="You have changed your vote to downvote.", ephemeral=True
                    )

                if interaction.user.id in i["downvotes"]:
                    return await interaction.response.send_message(
                        content="You already downvoted this suggestion feel free to change vote by clicking "
                        "the upvote button.", ephemeral=True
                    )

                i["downvotes"].append(interaction.user.id)
                button.label = str(len(i["downvotes"]))
                await self.message.edit(view=self)
                await interaction.response.send_message(
                    content="You have downvoted this suggestion.", ephemeral=True
                )
