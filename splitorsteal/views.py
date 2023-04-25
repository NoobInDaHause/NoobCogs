from __future__ import annotations
from typing import Dict, Optional, Union, List, Any, TYPE_CHECKING

import discord
from discord.ext import commands

from redbot.core.utils.chat_formatting import humanize_list

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
        
class SosManagerAdd(discord.ui.Modal):
    def __init__(self, *, title: str = "Please provide a role ID to add.", timeout: float = 30.0) -> None:
        super().__init__(title=title, timeout=timeout)
        
    role_ids = discord.ui.TextInput(
        style=discord.TextStyle.long,
        label="Add Role ID's.",
        required=True,
        placeholder="Provide a role ID, Split them with `,` if you want to add multiple roles.",
        max_length=500
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="Successfully submitted.", ephemeral=True)
        
class SosManagerRemove(discord.ui.Modal):
    def __init__(self, *, title: str = "Please provide a role ID to remove.", timeout: float = 30.0) -> None:
        super().__init__(title=title, timeout=timeout)
    
    role_ids = discord.ui.TextInput(
        style=discord.TextStyle.long,
        label="Remove Role ID's.",
        required=True,
        placeholder="Provide a role ID, Split them with `,` if you want to remove multiple roles.",
        max_length=500
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="Successfully submitted.", ephemeral=True)

class SosManager(discord.ui.View):
    def __init__(
        self,
        bot,
        context,
        author: discord.Member,
        config,
        timeout: int,
    ):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.context = context
        self.author = author
        self.config = config
        
    @discord.ui.select(
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Add", emoji="➕", description="Add managers."),
            discord.SelectOption(label="Remove", emoji="➖", description="Remove managers.")
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        # sourcery skip: low-code-quality
        select.disabled = True

        if select.values[0] == "Add":
            addview = SosManagerAdd()
            await self.message.edit(view=self)
            await interaction.response.send_modal(addview)

            await addview.wait()
            
            if role_ids := addview.role_ids.value.split(","):
                added_roles = []
                failed_roles = []
                for i in role_ids:
                    try:
                        sosman = await self.config.guild(interaction.guild).sosmanager_ids()
                        interaction.guild.get_role(int(i))
                        if int(i) in sosman:
                            failed_roles.append(i)
                            continue
                        async with self.config.guild(interaction.guild).sosmanager_ids() as sosmanids:
                            sosmanids.append(int(i))
                        added_roles.append(i)
                    except Exception:
                        failed_roles.append(i)

                embed = discord.Embed(
                    description=f"{humanize_list([f'<@&{role}>' for role in added_roles]) or '`None`'} were added to the manager list.",
                    color=await self.context.embed_colour()
                )
                await self.message.edit(embed=embed)

                if not failed_roles:
                    return
                
                embed = discord.Embed(
                    title="Some roles have failed to add.",
                    description=f"Most likely that the role doesn't exist or ValueError or role is already a manager.\n**Failed Roles:**\n{humanize_list([f'<@&{role}>' for role in failed_roles])}",
                    colour=await self.context.embed_colour()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)

        if select.values[0] == "Remove":
            removeview = SosManagerRemove()
            await self.message.edit(view=self)
            await interaction.response.send_modal(removeview)
            
            await removeview.wait()
            
            if role_ids := removeview.role_ids.value.split(","):
                removed_roles = []
                failed_roles = []
                for i in role_ids:
                    try:
                        sosman = await self.config.guild(interaction.guild).sosmanager_ids()
                        interaction.guild.get_role(int(i))
                        if int(i) not in sosman:
                            failed_roles.append(i)
                            continue
                        async with self.config.guild(interaction.guild).sosmanager_ids() as sosmanids:
                            index = sosmanids.index(int(i))
                            sosmanids.pop(index)
                        removed_roles.append(i)
                    except Exception:
                        failed_roles.append(i)
                        
                embed = discord.Embed(
                    description=f"{humanize_list([f'<@&{role}>' for role in removed_roles]) or '`None`'} were removed from the manager list.",
                    color=await self.context.embed_colour()
                )
                await self.message.edit(embed=embed)
                
                if not failed_roles:
                    return

                embed = discord.Embed(
                    title="Some roles have failed to remove.",
                    description=f"Most likely that the role doesn't exist or ValueError or role is not a manager.\n**Failed Roles:**\n{humanize_list([f'<@&{role}>' for role in failed_roles])}",
                    colour=await self.context.embed_colour()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
            
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
        
class SosButton(discord.ui.View):
    def __init__(self, author: discord.Member):
        super().__init__(timeout=30.0)
        self.author = author
        self.value = None
        
    @discord.ui.button(label="Split", emoji="🤝", style=discord.ButtonStyle.success)
    async def split(self, interaction: discord.Interaction, button: discord.ui.Button):
        for x in self.children:
            x.disabled = True
        self.value = "split"
        self.stop()
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(content=f"You have chosen {self.value.title()} 🤝.")
        
    @discord.ui.button(label="Steal", emoji="⚔️", style=discord.ButtonStyle.danger)
    async def steal(self, interaction: discord.Interaction, button: discord.ui.Button):
        for x in self.children:
            x.disabled = True
        self.value = "steal"
        self.stop()
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(content=f"You have chosen {self.value.title()} ⚔️.")
        
    @discord.ui.button(label="Forfeit", emoji="❌", style=discord.ButtonStyle.grey)
    async def forfeit(self, interaction: discord.Interaction, button: discord.ui.Button):
        for x in self.children:
            x.disabled = True
        self.value = "forfeit"
        self.stop()
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(content=f"You have chosen {self.value.title()} ❌.")
        
    async def on_timeout(self):
        for x in self.children:
            x.disabled = True
        self.value = "forfeit"
        self.stop()
        await self.message.edit(view=self)
        await self.author.send(content="You took too long to respond! Therefor you automatically choose forfeit.")