from __future__ import annotations
from typing import Dict, Optional, Union, List, Any

import discord
from discord.ext import commands

__all__ = (
    "Paginator",
)

class Paginator(discord.ui.View):
    """
    Paginator originally by PranoyMajumdar
    https://github.com/PranoyMajumdar/dispie/blob/main/dispie/paginator/__init__.py
    
    modified by me
    """
    message: Optional[discord.Message] = None

    def __init__(
        self,
        bot,
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
    ) -> Optional[Union[discord.Message, discord.InteractionMessage, discord.WebhookMessage]]:
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
                self.message = await self.context.send(**kwargs)
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
        bot,
        author: discord.Member,
        timeout: float,
        confirm_action
    ):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.author = author
        self.confirm_action = confirm_action
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
        
class GbanViewReset(discord.ui.View):
    def __init__(
        self,
        bot,
        author: Union[discord.Member, discord.User],
        config,
        timeout: int,
    ):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.author = author
        self.config = config
        
    @discord.ui.select(
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="List", emoji="📰", description="Reset the cogs banlist config."),
            discord.SelectOption(label="Logs", emoji="📜", description="Reset the cogs banlogs config."),
            discord.SelectOption(label="Cog", emoji="⚙️", description="Reset the whole cogs config.")
        ]
    )
    
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        select.disabled = True
        await interaction.response.edit_message(content="Menu no longer available.", view=self)
        
        if select.values[0] == "List":
            confirm_action = "Successfully resetted the globalban banlist."
            confview = Confirmation(bot=self.bot, author=self.author, timeout=30, confirm_action=confirm_action)
            confview.message = await interaction.followup.send("Are you sure you want to reset the globalban banlogs?", view=confview)
            
            await confview.wait()
            
            if confview.value == "yes":
                await self.config.banlist.clear()
        if select.values[0] == "Logs":
            confirm_action = "Successfully resetted the globalban banlogs."
            confview = Confirmation(bot=self.bot, author=self.author, timeout=30, confirm_action=confirm_action)
            confview.message = await interaction.followup.send("Are you sure you want to reset the globalban banlogs?", view=confview)

            await confview.wait()
            
            if confview.value == "yes":
                await self.config.banlogs.clear()
        if select.values[0] == "Cog":
            confirm_action = "Successfully cleared the globalban cogs configuration."
            confview = Confirmation(bot=self.bot, author=self.author, timeout=30, confirm_action=confirm_action)
            confview.message = await interaction.followup.send("This will reset the globalban cogs whole configuration, do you want to continue?", view=confview)

            await confview.wait()
            
            if confview.value == "yes":
                await self.config.clear_all()
            
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        owner = await self.bot.fetch_user(interaction.user.id)
        if await self.bot.is_owner(owner):
            return True
        elif interaction.user.id != self.author.id:
            await interaction.response.send_message(content="You are not the author of this interaction.", ephemeral=True)
            return False
        return True
    
    async def on_timeout(self):
        self.disabled = True
        await self.message.edit(view=self)