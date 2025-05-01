from __future__ import annotations

import noobutils as nu

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from . import PressF


class PressFView(nu.NoobView):
    def __init__(
        self,
        *,
        obj: Union[nu.commands.Context, nu.discord.Interaction[nu.Red]],
        cog: "PressF",
        thing: str,
        timeout: float = 180,
    ):
        super().__init__(obj=obj, timeout=timeout)
        self.cog = cog
        self.thing = thing
        self.paid_users = []

    async def start(self):
        embed = nu.discord.Embed(
            description=f"Everyone, let's pay our respects to **{self.thing}**!",
            colour=await self.context.embed_colour(),
        )
        self.message = await self.context.send(embed=embed, view=self)

    @nu.discord.ui.button(label="0")
    async def press_f_button(
        self,
        interaction: nu.discord.Interaction,
        button: nu.discord.ui.Button[PressFView],
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

    async def interaction_check(self, _: nu.discord.Interaction[nu.Red]) -> bool:
        return True

    async def on_timeout(self):
        for x in self.children:
            x.disabled = True

        await self.message.edit(view=self)

        if len(self.paid_users) == 0:
            return await self.context.channel.send(
                content=f"No one has paid respects to **{self.thing}**.",
                allowed_mentions=nu.discord.AllowedMentions.none(),
            )
        plural = "s" if len(self.paid_users) != 1 else ""
        await self.context.channel.send(
            content=f"**{len(self.paid_users)}** member{plural} has paid their respects to **{self.thing}**.",
            allowed_mentions=nu.discord.AllowedMentions.none(),
        )
        act_chan: list = self.cog.active_cache
        if self.context.channel.id in act_chan:
            index = act_chan.index(self.context.channel.id)
            act_chan.pop(index)
