import discord

from redbot.core import commands
from redbot.core.utils.chat_formatting import box

from expr import evaluate, EvaluatorError
from typing import Optional

from .utils import access_denied

class Calculator(discord.ui.View):
    def __init__(
        self,
        timeout: Optional[float] = 60
    ):
        super().__init__(timeout=timeout)
        self.message: discord.Message = None
        self.context: commands.Context = None
        self.value_list = []

    async def start(self, context: commands.Context):
        msg = await context.send(content=box("0", "py"), view=self)
        self.message = msg
        self.context = context

    @discord.ui.button(label="1", style=discord.ButtonStyle.grey)
    async def one(self, interaction: discord.Interaction, button: discord.ui.Button):
        """1"""
        self.value_list.append("1")
        merged = "".join(self.value_list)
        await interaction.response.edit_message(content=box(merged, "py"))

    @discord.ui.button(label="2", style=discord.ButtonStyle.grey)
    async def two(self, interaction: discord.Interaction, button: discord.ui.Button):
        """2"""
        self.value_list.append("2")
        merged = "".join(self.value_list)
        await interaction.response.edit_message(content=box(merged, "py"))

    @discord.ui.button(label="3", style=discord.ButtonStyle.grey)
    async def three(self, interaction: discord.Interaction, button: discord.ui.Button):
        """3"""
        self.value_list.append("3")
        merged = "".join(self.value_list)
        await interaction.response.edit_message(content=box(merged, "py"))

    @discord.ui.button(label="+", style=discord.ButtonStyle.blurple)
    async def plus(self, interaction: discord.Interaction, button: discord.ui.Button):
        """+"""
        self.value_list.append("+")
        merged = "".join(self.value_list)
        await interaction.response.edit_message(content=box(merged, "py"))

    @discord.ui.button(label="Exit", style=discord.ButtonStyle.danger)
    async def exit(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Exit"""
        for x in self.children:
            x.disabled = True
        self.stop()
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="4", style=discord.ButtonStyle.grey)
    async def four(self, interaction: discord.Interaction, button: discord.ui.Button):
        """4"""
        self.value_list.append("4")
        merged = "".join(self.value_list)
        await interaction.response.edit_message(content=box(merged, "py"))

    @discord.ui.button(label="5", style=discord.ButtonStyle.grey)
    async def five(self, interaction: discord.Interaction, button: discord.ui.Button):
        """5"""
        self.value_list.append("5")
        merged = "".join(self.value_list)
        await interaction.response.edit_message(content=box(merged, "py"))

    @discord.ui.button(label="6", style=discord.ButtonStyle.grey)
    async def six(self, interaction: discord.Interaction, button: discord.ui.Button):
        """6"""
        self.value_list.append("6")
        merged = "".join(self.value_list)
        await interaction.response.edit_message(content=box(merged, "py"))

    @discord.ui.button(label="-", style=discord.ButtonStyle.blurple)
    async def minus(self, interaction: discord.Interaction, button: discord.ui.Button):
        """-"""
        self.value_list.append("-")
        merged = "".join(self.value_list)
        await interaction.response.edit_message(content=box(merged, "py"))

    @discord.ui.button(label="\u232B", style=discord.ButtonStyle.danger)
    async def erase(self, interaction: discord.Interaction, button: discord.ui.Button):
        """\u232B"""
        if not self.value_list:
            return await interaction.followup.send(
                content="You can not erase anymore number, please add more.", ephemeral=True
            )
        self.value_list.pop()
        merged = "".join(self.value_list)
        await interaction.response.edit_message(content=box(merged, "py")if merged else box("0", "py"))

    @discord.ui.button(label="7", style=discord.ButtonStyle.grey)
    async def seven(self, interaction: discord.Interaction, button: discord.ui.Button):
        """7"""
        self.value_list.append("7")
        merged = "".join(self.value_list)
        await interaction.response.edit_message(content=box(merged, "py"))

    @discord.ui.button(label="8", style=discord.ButtonStyle.grey)
    async def eight(self, interaction: discord.Interaction, button: discord.ui.Button):
        """8"""
        self.value_list.append("8")
        merged = "".join(self.value_list)
        await interaction.response.edit_message(content=box(merged, "py"))

    @discord.ui.button(label="9", style=discord.ButtonStyle.grey)
    async def nine(self, interaction: discord.Interaction, button: discord.ui.Button):
        """9"""
        self.value_list.append("9")
        merged = "".join(self.value_list)
        await interaction.response.edit_message(content=box(merged, "py"))

    @discord.ui.button(label="*", style=discord.ButtonStyle.blurple)
    async def times(self, interaction: discord.Interaction, button: discord.ui.Button):
        """*"""
        self.value_list.append("*")
        merged = "".join(self.value_list)
        await interaction.response.edit_message(content=box(merged, "py"))

    @discord.ui.button(label="Clear", style=discord.ButtonStyle.danger)
    async def clear(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Clear"""
        self.value_list.clear()
        await interaction.response.edit_message(content=box("0", "py"))

    @discord.ui.button(label="00", style=discord.ButtonStyle.grey)
    async def double_zero(self, interaction: discord.Interaction, button: discord.ui.Button):
        """00"""
        self.value_list.append("0")
        self.value_list.append("0")
        merged = "".join(self.value_list)
        await interaction.response.edit_message(content=box(merged, "py"))

    @discord.ui.button(label="0", style=discord.ButtonStyle.grey)
    async def zero(self, interaction: discord.Interaction, button: discord.ui.Button):
        """0"""
        self.value_list.append("0")
        merged = "".join(self.value_list)
        await interaction.response.edit_message(content=box(merged, "py"))

    @discord.ui.button(label=".", style=discord.ButtonStyle.grey)
    async def dot(self, interaction: discord.Interaction, button: discord.ui.Button):
        """."""
        self.value_list.append(".")
        merged = "".join(self.value_list)
        await interaction.response.edit_message(content=box(merged, "py"))

    @discord.ui.button(label="/", style=discord.ButtonStyle.blurple)
    async def divide(self, interaction: discord.Interaction, button: discord.ui.Button):
        """/"""
        self.value_list.append("/")
        merged = "".join(self.value_list)
        await interaction.response.edit_message(content=box(merged, "py"))

    @discord.ui.button(label="=", style=discord.ButtonStyle.success)
    async def equals(self, interaction: discord.Interaction, button: discord.ui.Button):
        """="""
        merged = "".join(self.value_list)
        try:
            final = str(evaluate(merged))
        except EvaluatorError as e:
            return await interaction.response.send_message(content=f"Error: {e}", ephemeral=True)
        self.value_list.clear()
        self.value_list.append(final)
        await interaction.response.edit_message(content=box(final, "py"))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if await self.context.bot.fetch_user(interaction.user.id):
            return True
        elif interaction.user.id != self.context.author.id:
            await interaction.response.send_message(content=access_denied(), ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        for x in self.children:
            x.disabled = True
        self.stop()
        await self.message.edit(view=self)

class CookieClicker(discord.ui.View):
    def __init__(
        self,
        emoji: str | discord.Emoji | discord.PartialEmoji,
        timeout: Optional[float] = 60
    ):
        super().__init__(timeout=timeout)
        self.message: discord.Message = None
        self.context: commands.Context = None
        self.cookieclicker.emoji = emoji
        self.clicked = []

    async def start(self, context: commands.Context):
        msg = await context.send(view=self)
        self.message = msg
        self.context = context

    @discord.ui.button(custom_id="cookieclicker", label="0", style=discord.ButtonStyle.success)
    async def cookieclicker(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Cookie clicker."""
        self.clicked.append(len(self.clicked) + 1)
        button.label = len(self.clicked)
        await interaction.response.edit_message(view=self)

    @discord.ui.button(emoji="❎", label="Quit", style=discord.ButtonStyle.danger)
    async def quit(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Quit cookie clicker."""
        for x in self.children:
            x.disabled = True
        self.stop()
        await interaction.response.edit_message(view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if await self.context.bot.fetch_user(interaction.user.id):
            return True
        elif interaction.user != self.context.author:
            await interaction.response.send_message(content=access_denied(), ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        for x in self.children:
            x.disabled = True
        self.stop()
        await self.message.edit(view=self)

class PressFView(discord.ui.View):
    def __init__(
        self,
        emoji: str | discord.Emoji | discord.PartialEmoji,
        timeout: Optional[float] = 180.0
    ):
        super().__init__(timeout=timeout)
        self.context: commands.Context = None
        self.message: discord.Message = None
        self.thing: str = None
        self.f_button.emoji = emoji
        self.paid_users = []

    @discord.ui.button(custom_id="f_button", label="0", style=discord.ButtonStyle.grey)
    async def f_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.paid_users.append(interaction.user.id)
        button.label = len(self.paid_users)
        await self.message.edit(view=self)
        await interaction.response.send_message(
            content=f"**{interaction.user.name}** has paid their respects."
        )

    async def start(self, context: commands.Context, thing: str):
        embed = discord.Embed(
            description=f"Everyone, let's pay our respects to **{thing}**!",
            colour=await context.embed_colour()
        )
        msg = await context.send(embed=embed, view=self)
        self.message = msg
        self.context = context
        self.thing = thing

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id in self.paid_users:
            await interaction.response.send_message(content="You already paid your respects!", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        for x in self.children:
            x.disabled = True
        self.stop()
        await self.message.edit(view=self)
        if len(self.paid_users) == 0:
            return await self.context.channel.send(
                content=f"No one has paid respects to **{self.thing}**.",
                allowed_mentions=discord.AllowedMentions.none()
            )
        plural = "s" if len(self.paid_users) != 1 else ""
        await self.context.channel.send(
            content=f"**{len(self.paid_users)}** user{plural} has paid their respects to **{self.thing}**.",
            allowed_mentions=discord.AllowedMentions.none()
        )
