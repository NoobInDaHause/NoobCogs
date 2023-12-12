import asyncio
import discord
import noobutils as nu

from redbot.core.bot import commands, Red

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

from .sosgifs import forfeit_gifs, win_gifs, lose_gifs, betray_gifs

if TYPE_CHECKING:
    from . import SplitOrSteal


class Commence(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180.0)
        self.players = []

    @discord.ui.button(label="0", style=nu.get_button_colour("green"))
    async def commence_button(
        self, interaction: discord.Interaction[Red], button: discord.ui.Button
    ):
        if interaction.user in self.players:
            self.players.remove(interaction.user)
            message = "You have left this SplitOrSteal game."
        else:
            self.players.append(interaction.user)
            message = "You have joined this SplitOrSteal game."

        button.label = str(len(self.players))
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(content=message, ephemeral=True)

    async def on_timeout(self) -> None:
        self.stop()


class SplitOrStealView(discord.ui.View):
    def __init__(self, cog: "SplitOrSteal"):
        super().__init__(timeout=200.0)
        self.cog = cog
        self.prize: str = None
        self.message: discord.Message = None
        self.context: commands.Context = None
        self.player_1: discord.Member = None
        self.player_2: discord.Member = None
        self.choices = {"player_1": None, "player_2": None}

    async def start(
        self,
        context: commands.Context,
        p1: discord.Member,
        p2: discord.Member,
        prize: str,
    ):
        self.context = context
        self.prize = prize
        self.player_1 = p1
        self.player_2 = p2
        t = datetime.now(timezone.utc) + timedelta(seconds=60)
        sotembed = discord.Embed(
            title="Split or Steal Game",
            description="The split or steal game has begun!\n"
            "Players can now discuss if they want to either `Split 🤝` or `Steal ⚔️` before the timer ends.\n"
            "Think very carefully and make your decisions precise!",
            colour=await context.embed_colour(),
        )
        sotembed.add_field(name="Prize:", value=prize, inline=True)
        sotembed.add_field(
            name="Time left:", value=f"<t:{round(t.timestamp())}:R>", inline=True
        )
        sotembed.set_footer(
            text="Remember trust no one in this game. ;)",
            icon_url=nu.is_have_avatar(context.guild),
        )
        sotembed.set_author(
            name=f"Hosted by: {context.author} ({context.author.id})",
            icon_url=nu.is_have_avatar(context.author),
        )
        sotembed.set_image(
            url="https://cdn.discordapp.com/attachments/1035334209818071161/1183346867497599076/sos.jpg"
        )
        await self.context.channel.send(
            content=f"{self.player_1.mention} and {self.player_2.mention}",
            embed=sotembed,
        )
        await asyncio.sleep(
            round(t.timestamp() - datetime.now(timezone.utc).timestamp())
        )
        await self.game()

    async def game(self):
        await self.update_embed()

        dt = datetime.now(timezone.utc) + timedelta(seconds=60)
        while datetime.now(timezone.utc) < dt:
            if self.choices["player_1"] and self.choices["player_2"]:
                break
            await asyncio.sleep(1.0)

        await self.end_game()

    def get_gifs_and_stuff(self):
        if self.choices["player_1"] is None and self.choices["player_2"] is None:
            return (
                "Both players did not choose anything. Nobody has won the prize 🚫!",
                lose_gifs(),
                0x2F3136,
            )
        if self.choices["player_1"] is None:
            return (
                (
                    f"{self.player_2.mention} has won the prize since "
                    f"{self.player_1.mention} forfeited for taking too long to answer."
                ),
                forfeit_gifs(),
                0x00FF00,
            )
        if self.choices["player_2"] is None:
            return (
                (
                    f"{self.player_1.mention} has won the prize since "
                    f"{self.player_2.mention} forfeited for taking too long to answer."
                ),
                forfeit_gifs(),
                0x00FF00,
            )
        if self.choices["player_1"] == "split" and self.choices["player_2"] == "split":
            return (
                "Both players chose Split! They can now split the prize 🤝!",
                win_gifs(),
                0x00FF00,
            )
        if self.choices["player_1"] == "split" and self.choices["player_2"] == "steal":
            return (
                f"Player {self.player_2.mention} steals the prize for themselves ⚔️!",
                betray_gifs(),
                0xFF0000,
            )
        if self.choices["player_1"] == "steal" and self.choices["player_2"] == "split":
            return (
                f"Player {self.player_1.mention} steals the prize for themselves ⚔️!",
                betray_gifs(),
                0xFF0000,
            )
        if self.choices["player_1"] == "steal" and self.choices["player_2"] == "steal":
            return (
                "Both players chose Steal! Nobody has won the prize 🚫!",
                lose_gifs(),
                0x2F3136,
            )

    async def end_game(self):
        for x in self.children:
            x.disabled = True
        await self.message.edit(view=self)
        results = []
        for k, v in self.choices.items():
            p = self.player_1 if k == "player_1" else self.player_2
            if v:
                results.append(f"{p.mention} has chosen **{v}!**\n")
            else:
                results.append(f"{p.mention} did not choose anything!\n")
        res, gif, col = self.get_gifs_and_stuff()
        last_embed = discord.Embed(
            title="SplitOrSteal game ended.",
            description=res,
            colour=col,
            timestamp=discord.utils.utcnow(),
        )
        last_embed.set_author(
            name=f"Hosted by: {self.context.author} ({self.context.author.id})",
            icon_url=nu.is_have_avatar(self.context.author),
        )
        last_embed.set_image(url=gif)
        last_embed.add_field(name="Prize:", value=self.prize, inline=False)
        last_embed.add_field(name="Results:", value="".join(results), inline=False)
        await self.context.send(content=self.context.author.mention, embed=last_embed)
        self.stop()
        if self.context.channel.id in self.cog.active_cache[str(self.context.guild.id)]:
            self.cog.active_cache[str(self.context.guild.id)].remove(
                self.context.channel.id
            )

    async def update_embed(self):
        stat = []
        for k, v in self.choices.items():
            p = self.player_1 if k == "player_1" else self.player_2
            if v:
                stat.append(f"**✅ {p.mention} Ready.**\n")
            else:
                stat.append(f"**❌ {p.mention} Not ready.**\n")
        sembed = discord.Embed(
            description="Players can now choose `Split 🤝` or `Steal ⚔️`.",
            colour=await self.context.embed_colour(),
        )
        sembed.set_footer(
            text="Remember trust no one in this game. ;)",
            icon_url=nu.is_have_avatar(self.context.guild),
        )
        sembed.set_author(
            name=f"Hosted by: {self.context.author} ({self.context.author.id})",
            icon_url=nu.is_have_avatar(self.context.author),
        )
        sembed.add_field(name="Prize:", value=self.prize, inline=False)
        sembed.add_field(name="Awaiting responses:", value="".join(stat), inline=False)
        if self.message is not None:
            await self.message.edit(embed=sembed, view=self)
            return
        self.message = await self.context.send(
            content=f"{self.player_1.mention} and {self.player_2.mention}",
            embed=sembed,
            view=self,
        )

    @discord.ui.button(emoji="🤝", label="Split", style=nu.get_button_colour("green"))
    async def split_button(
        self, interaction: discord.Interaction[Red], button: discord.ui.Button
    ):
        if interaction.user == self.player_1:
            if self.choices["player_1"]:
                return await interaction.response.send_message(
                    content=f"You have already chosen **{self.choices['player_1']:}**.",
                    ephemeral=True,
                )
            self.choices["player_1"] = "split"
        if interaction.user == self.player_2:
            if self.choices["player_2"]:
                return await interaction.response.send_message(
                    content=f"You have already chosen **{self.choices['player_2']:}**.",
                    ephemeral=True,
                )
            self.choices["player_2"] = "split"
        await self.update_embed()
        await interaction.response.send_message(
            content="You have chosen 🤝 Split.", ephemeral=True
        )

    @discord.ui.button(emoji="⚔️", label="Steal", style=nu.get_button_colour("red"))
    async def steal_button(
        self, interaction: discord.Interaction[Red], button: discord.ui.Button
    ):
        if interaction.user == self.player_1:
            if self.choices["player_1"]:
                return await interaction.response.send_message(
                    content=f"You have already chosen **{self.choices['player_1']:}**.",
                    ephemeral=True,
                )
            self.choices["player_1"] = "steal"
        if interaction.user == self.player_2:
            if self.choices["player_2"]:
                return await interaction.response.send_message(
                    content=f"You have already chosen **{self.choices['player_2']}**.",
                    ephemeral=True,
                )
            self.choices["player_2"] = "steal"
        await self.update_embed()
        await interaction.response.send_message(
            content="You have chosen ⚔️ Steal.", ephemeral=True
        )

    async def interaction_check(self, interaction: discord.Interaction[Red]) -> bool:
        if interaction.user.id in [self.player_1.id, self.player_2.id]:
            return True
        await interaction.response.send_message(
            content="You are not a player in this SplitOrSteal game.", ephemeral=True
        )
        return False

    async def on_timeout(self) -> None:
        if self.context.channel.id in self.cog.active_cache[str(self.context.guild.id)]:
            self.cog.active_cache[str(self.context.guild.id)].remove(
                self.context.channel.id
            )
        self.stop()
        await self.message.edit(
            content="This SplitOrSteal game has timed out.", view=None, embed=None
        )


class DuelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30.0)
        self.message: discord.Message = None
        self.member: discord.Member = None
        self.value: bool = None

    async def start(self, context: commands.Context, member: discord.Member):
        msg = await context.channel.send(
            content=f"{member.mention}, **{context.author}** has challenged you to a SplitOrStealDuel! "
            "Do you wish to accept?",
            view=self,
        )
        self.message = msg
        self.member = member

    @discord.ui.button(label="Yes", style=nu.get_button_colour("green"))
    async def yes_duel(
        self, interaction: discord.Interaction[Red], button: discord.ui.Button
    ):
        self.value = True
        for x in self.children:
            x.disabled = True
        await interaction.response.edit_message(
            content=f"{self.member.mention} has said yes!", view=self
        )
        self.stop()

    @discord.ui.button(label="No", style=nu.get_button_colour("red"))
    async def no_duel(
        self, interaction: discord.Interaction[Red], button: discord.ui.Button
    ):
        self.value = False
        for x in self.children:
            x.disabled = True
        await interaction.response.edit_message(
            content=f"{self.member.mention} has said no!", view=self
        )
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction[Red]) -> bool:
        if interaction.user == self.member:
            return True
        await interaction.response.send_message(
            content=f"You are not {self.member.mention}.", ephemeral=True
        )
        return False

    async def on_timeout(self) -> None:
        for x in self.children:
            x.disabled = True
        await self.message.edit(
            content=f"It seems {self.member.mention} did not respond.", view=self
        )
