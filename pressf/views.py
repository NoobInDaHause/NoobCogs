import discord

from redbot.core import commands

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import PressF


class PressFView(discord.ui.View):
    def __init__(self, cog: "PressF", timeout: float = 180.0):
        super().__init__(timeout=timeout)
        self.message: discord.Message = None
        self.cog = cog
        self.context: commands.Context = None
        self.thing: str = None
        self.paid_users = []

    async def start(self, context: commands.Context, thing: str):
        embed = discord.Embed(
            description=f"Everyone, let's pay our respects to **{thing}**!",
            colour=await context.embed_colour(),
        )
        msg = await context.send(embed=embed, view=self)
        self.message = msg
        self.context = context
        self.thing = thing

    @discord.ui.button(label="0")
    async def press_f_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id in self.paid_users:
            return await interaction.response.send_message(
                content="You already paid your respects!", ephemeral=True
            )
        self.paid_users.append(interaction.user.id)
        button.label = str(len(self.paid_users))
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(
            content=f"**{interaction.user}** has paid their respects."
        )

    async def on_timeout(self):
        for x in self.children:
            x.disabled = True
        self.stop()
        await self.message.edit(view=self)
        if len(self.paid_users) == 0:
            return await self.context.channel.send(
                content=f"No one has paid respects to **{self.thing}**.",
                allowed_mentions=discord.AllowedMentions.none(),
            )
        plural = "s" if len(self.paid_users) != 1 else ""
        await self.context.channel.send(
            content=f"**{len(self.paid_users)}** member{plural} has paid their respects to **{self.thing}**.",
            allowed_mentions=discord.AllowedMentions.none(),
        )
        act_chan: list = self.cog.active_cache
        if self.context.channel.id in act_chan:
            index = act_chan.index(self.context.channel.id)
            act_chan.pop(index)
