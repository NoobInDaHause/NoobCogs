from __future__ import annotations

import discord

from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import box

from typing import Dict, Optional, Union, List, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from discord import Message, InteractionMessage, WebhookMessage

__all__ = (
    "Paginator",
)

class Paginator(discord.ui.View):
    """
    Paginator originally by PranoyMajumdar
    https://github.com/PranoyMajumdar/dispie/blob/main/dispie/paginator/__init__.py
    
    modified by me
    """
    message: Optional[Message] = None

    def __init__(
        self,
        bot: Red,
        author: discord.Member,
        pages: List[Any],
        *,
        timeout: Optional[float] = 60,
        delete_message_after: bool = False,
        per_page: int = 1,
    ):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.author = author
        self.delete_message_after: bool = delete_message_after
        self.current_page: int = 0

        self.context: Optional[commands.Context] = None
        self.interaction: Optional[discord.Interaction] = None
        self.per_page: int = per_page
        self.pages: Any = pages
        total_pages, left_over = divmod(len(self.pages), self.per_page)
        if left_over:
            total_pages += 1

        self.max_pages: int = total_pages
        self.next_page.disabled = self.current_page >= self.max_pages - 1
        self.last_page.disabled = self.current_page >= self.max_pages - 1

    def get_page(self, page_number: int) -> Any:
        if page_number < 0 or page_number >= self.max_pages:
            self.current_page = 0
            return self.pages[self.current_page]

        if self.per_page == 1:
            return self.pages[page_number]
        
        base = page_number * self.per_page
        return self.pages[base: base + self.per_page]

    def format_page(self, page: Any) -> Any:
        return page
    
    async def get_page_kwargs(self, page: Any) -> Dict[str, Any]:
        formatted_page = await discord.utils.maybe_coroutine(self.format_page, page)

        kwargs = {"content": None, "embeds": [], "view": self}
        if isinstance(formatted_page, str):
            kwargs["content"] = formatted_page
        elif isinstance(formatted_page, discord.Embed):
            kwargs["embeds"] = [formatted_page]
        elif isinstance(formatted_page, list):
            if not all(isinstance(embed, discord.Embed) for embed in formatted_page):
                raise TypeError(
                    "All elements in the list must be of type Embed")

            kwargs["embeds"] = formatted_page
        elif isinstance(formatted_page, dict):
            return formatted_page

        return kwargs

    async def update_page(self, interaction: discord.Interaction) -> None:
        if self.message is None:
            self.message = interaction.message

        kwargs = await self.get_page_kwargs(self.get_page(self.current_page))
        self.previous_page.disabled = self.current_page <= 0
        self.first_page.disabled = self.current_page <= 0
        self.next_page.disabled = self.current_page >= self.max_pages - 1
        self.last_page.disabled = self.current_page >= self.max_pages - 1
        await interaction.response.edit_message(**kwargs)

    @discord.ui.button(emoji="\U000023EA", style=discord.ButtonStyle.grey)
    async def first_page(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.current_page = 0
        await self.update_page(interaction)
    
    @discord.ui.button(emoji="\U000025C0", style=discord.ButtonStyle.gray)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.current_page -= 1
        await self.update_page(interaction)

    @discord.ui.button(emoji="\U0000274C", style=discord.ButtonStyle.grey)
    async def stop_page(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        for x in self.children:
            x.disabled = True
        self.stop()
        await interaction.response.edit_message(view=self)
    
    @discord.ui.button(emoji="\U000025B6", style=discord.ButtonStyle.gray)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.current_page += 1
        await self.update_page(interaction)
        
    @discord.ui.button(emoji="\U000023E9", style=discord.ButtonStyle.grey)
    async def last_page(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.current_page = self.max_pages - 1
        await self.update_page(interaction)
    
    async def start(
        self, obj: Union[commands.Context, discord.Interaction]
    ) -> Optional[Union[Message, InteractionMessage, WebhookMessage]]:
        if isinstance(obj, commands.Context):
            self.context = obj
            self.interaction = None
        else:
            self.context = None
            self.interaction = obj

        if self.message is not None and self.interaction is not None:
            await self.update_page(self.interaction)
        else:
            self.first_page.disabled = self.current_page <= 0
            self.previous_page.disabled = self.current_page <= 0
            kwargs = await self.get_page_kwargs(self.get_page(self.current_page))
            if self.context is not None:
                self.message = await self.context.channel.send(**kwargs)
            elif self.interaction is not None:
                if self.interaction.response.is_done():
                    self.message = await self.interaction.followup.send(**kwargs, view=self)
                else:
                    await self.interaction.response.send_message(**kwargs, view=self)
                    self.message = await self.interaction.original_response()
            else:
                raise RuntimeError(
                    "Cannot start a paginator without a context or interaction."
                )
        return self.message
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        owner = await self.bot.fetch_user(interaction.user.id)
        if await self.bot.is_owner(owner):
            return True
        elif interaction.user.id != self.author.id:
            await interaction.response.send_message(content="You are not the author of this interaction.", ephemeral=True)
            return False
        return True
    
    async def on_timeout(self):
        for x in self.children:
            x.disabled = True
        self.stop()
        await self.message.edit(view=self)

class Confirmation(discord.ui.View):
    def __init__(
        self,
        bot: Red,
        author: discord.Member,
        timeout: float,
        confirm_action
    ):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.author = author
        self.confirm_action = confirm_action
        self.message: discord.Message = None
        self.value = None
        
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
        owner = await self.bot.fetch_user(interaction.user.id)
        if await self.bot.is_owner(owner):
            return True
        elif interaction.user.id != self.author.id:
            await interaction.response.send_message(content="You are not the author of this interaction.", ephemeral=True)
            return False
        return True
    
    async def on_timeout(self):
        for x in self.children:
            x.disabled = True
        self.stop()
        await self.message.edit(content="You took too long to respond.", view=self)
        
class Calculator(discord.ui.View):
    def __init__(
        self,
        bot: Red,
        author: discord.Member
    ):
        super().__init__(timeout=180.0)
        self.bot = bot
        self.author = author
        self.message: discord.Message = None
        self.value_list = []
        
    @discord.ui.button(label="1", style=discord.ButtonStyle.grey)
    async def one(self, interaction: discord.Interaction, button: discord.ui.Button):
        """1"""
        await interaction.response.defer()
        self.value_list.append("1")
        merged = "".join(self.value_list)
        await interaction.edit_original_response(content=box(merged, "py"))
        
    @discord.ui.button(label="2", style=discord.ButtonStyle.grey)
    async def two(self, interaction: discord.Interaction, button: discord.ui.Button):
        """2"""
        await interaction.response.defer()
        self.value_list.append("2")
        merged = "".join(self.value_list)
        await interaction.edit_original_response(content=box(merged, "py"))
        
    @discord.ui.button(label="3", style=discord.ButtonStyle.grey)
    async def three(self, interaction: discord.Interaction, button: discord.ui.Button):
        """3"""
        await interaction.response.defer()
        self.value_list.append("3")
        merged = "".join(self.value_list)
        await interaction.edit_original_response(content=box(merged, "py"))
        
    @discord.ui.button(label="+", style=discord.ButtonStyle.blurple)
    async def plus(self, interaction: discord.Interaction, button: discord.ui.Button):
        """+"""
        await interaction.response.defer()
        self.value_list.append("+")
        merged = "".join(self.value_list)
        await interaction.edit_original_response(content=box(merged, "py"))
    
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
        await interaction.response.defer()
        self.value_list.append("4")
        merged = "".join(self.value_list)
        await interaction.edit_original_response(content=box(merged, "py"))
        
    @discord.ui.button(label="5", style=discord.ButtonStyle.grey)
    async def five(self, interaction: discord.Interaction, button: discord.ui.Button):
        """5"""
        await interaction.response.defer()
        self.value_list.append("5")
        merged = "".join(self.value_list)
        await interaction.edit_original_response(content=box(merged, "py"))
        
    @discord.ui.button(label="6", style=discord.ButtonStyle.grey)
    async def six(self, interaction: discord.Interaction, button: discord.ui.Button):
        """6"""
        await interaction.response.defer()
        self.value_list.append("6")
        merged = "".join(self.value_list)
        await interaction.edit_original_response(content=box(merged, "py"))
        
    @discord.ui.button(label="-", style=discord.ButtonStyle.blurple)
    async def minus(self, interaction: discord.Interaction, button: discord.ui.Button):
        """-"""
        await interaction.response.defer()
        self.value_list.append("-")
        merged = "".join(self.value_list)
        await interaction.edit_original_response(content=box(merged, "py"))
    
    @discord.ui.button(label="\u232B", style=discord.ButtonStyle.danger)
    async def erase(self, interaction: discord.Interaction, button: discord.ui.Button):
        """\u232B"""
        await interaction.response.defer()
        if not self.value_list:
            return await interaction.followup.send(content="You can not erase a number anymore, please add more.", ephemeral=True)
        self.value_list.pop()
        merged = "".join(self.value_list)
        await interaction.edit_original_response(content=box(merged, "py")if merged else box("0", "py"))
        
    @discord.ui.button(label="7", style=discord.ButtonStyle.grey)
    async def seven(self, interaction: discord.Interaction, button: discord.ui.Button):
        """7"""
        await interaction.response.defer()
        self.value_list.append("7")
        merged = "".join(self.value_list)
        await interaction.edit_original_response(content=box(merged, "py"))
        
    @discord.ui.button(label="8", style=discord.ButtonStyle.grey)
    async def eight(self, interaction: discord.Interaction, button: discord.ui.Button):
        """8"""
        await interaction.response.defer()
        self.value_list.append("8")
        merged = "".join(self.value_list)
        await interaction.edit_original_response(content=box(merged, "py"))
        
    @discord.ui.button(label="9", style=discord.ButtonStyle.grey)
    async def nine(self, interaction: discord.Interaction, button: discord.ui.Button):
        """9"""
        await interaction.response.defer()
        self.value_list.append("9")
        merged = "".join(self.value_list)
        await interaction.edit_original_response(content=box(merged, "py"))
        
    @discord.ui.button(label="*", style=discord.ButtonStyle.blurple)
    async def times(self, interaction: discord.Interaction, button: discord.ui.Button):
        """*"""
        await interaction.response.defer()
        self.value_list.append("*")
        merged = "".join(self.value_list)
        await interaction.edit_original_response(content=box(merged, "py"))
        
    @discord.ui.button(label="Clear", style=discord.ButtonStyle.danger)
    async def clear(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Clear"""
        await interaction.response.defer()
        self.value_list.clear()
        await interaction.edit_original_response(content=box("0", "py"))
        
    @discord.ui.button(label="00", style=discord.ButtonStyle.grey)
    async def double_zero(self, interaction: discord.Interaction, button: discord.ui.Button):
        """00"""
        await interaction.response.defer()
        self.value_list.append("0")
        self.value_list.append("0")
        merged = "".join(self.value_list)
        await interaction.edit_original_response(content=box(merged, "py"))
        
    @discord.ui.button(label="0", style=discord.ButtonStyle.grey)
    async def zero(self, interaction: discord.Interaction, button: discord.ui.Button):
        """0"""
        await interaction.response.defer()
        self.value_list.append("0")
        merged = "".join(self.value_list)
        await interaction.edit_original_response(content=box(merged, "py"))
        
    @discord.ui.button(label=".", style=discord.ButtonStyle.grey)
    async def dot(self, interaction: discord.Interaction, button: discord.ui.Button):
        """."""
        await interaction.response.defer()
        self.value_list.append(".")
        merged = "".join(self.value_list)
        await interaction.edit_original_response(content=box(merged, "py"))
        
    @discord.ui.button(label="/", style=discord.ButtonStyle.blurple)
    async def divide(self, interaction: discord.Interaction, button: discord.ui.Button):
        """/"""
        await interaction.response.defer()
        self.value_list.append("/")
        merged = "".join(self.value_list)
        await interaction.edit_original_response(content=box(merged, "py"))
        
    @discord.ui.button(label="=", style=discord.ButtonStyle.success)
    async def equals(self, interaction: discord.Interaction, button: discord.ui.Button):
        """="""
        await interaction.response.defer()
        merged = "".join(self.value_list)
        try:
            final = str(eval(merged))
        except Exception as e:
            return await interaction.followup.send(content=f"Error: {e}", ephemeral=True)
        self.value_list.clear()
        self.value_list.append(final)
        await interaction.edit_original_response(content=box(final, "py"))
        
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        owner = await self.bot.fetch_user(interaction.user.id)
        if await self.bot.is_owner(owner):
            return True
        elif interaction.user.id != self.author.id:
            await interaction.response.send_message(content="You are not the author of this interaction.", ephemeral=True)
            return False
        return True
    
    async def on_timeout(self):
        for x in self.children:
            x.disabled = True
        self.stop()
        await self.message.edit(view=self)

class CookieClicker(discord.ui.View):
    def __init__(self, bot: Red, author: discord.Member):
        super().__init__(timeout=30.0)
        self.bot = bot
        self.author = author
        self.message: discord.message = None
        self.clicked = []

    @discord.ui.button(emoji="🍪", label="0", style=discord.ButtonStyle.success)
    async def cookieclicker(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Cookie clicker."""
        await interaction.response.defer()
        self.clicked.append(len(self.clicked) + 1)
        button.label = len(self.clicked)
        await interaction.edit_original_response(content=len(self.clicked), view=self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        owner = await self.bot.fetch_user(interaction.user.id)
        if await self.bot.is_owner(owner):
            return True
        elif interaction.user.id != self.author.id:
            await interaction.response.send_message(content="You are not the author of this interaction.", ephemeral=True)
            return False
        return True
    
    async def on_timeout(self):
        for x in self.children:
            x.disabled = True
        self.stop()
        await self.message.edit(view=self)