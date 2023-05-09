from __future__ import annotations
from typing import Optional

import datetime
import discord

from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list, box

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
        elif interaction.user.id != self.context.author.id:
            await interaction.response.send_message(content="You are not the author of this interaction.", ephemeral=True)
            return False
        return True
    
    async def on_timeout(self):
        for x in self.children:
            x.disabled = True
        self.stop()
        await self.message.edit(content="You took too long to respond.", view=self)
        
class SosManagerAdd(discord.ui.Modal):
    def __init__(self, *, title: str = "Add manager roles.", timeout: float = 60.0) -> None:
        super().__init__(title=title, timeout=timeout)
        
    role_ids = discord.ui.TextInput(
        style=discord.TextStyle.long,
        label="Please provide a role ID to add.",
        required=True,
        placeholder="Split them with `,` (no spaces) if you want to add multiple roles.",
        max_length=500
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="Successfully submitted.", ephemeral=True)
        
class SosManagerRemove(discord.ui.Modal):
    def __init__(self, *, title: str = "Remove manager roles.", timeout: float = 60.0) -> None:
        super().__init__(title=title, timeout=timeout)
    
    role_ids = discord.ui.TextInput(
        style=discord.TextStyle.long,
        label="Please provide a role ID to remove.",
        required=True,
        placeholder="Split them with `,` (no spaces) if you want to remove multiple roles.",
        max_length=500
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="Successfully submitted.", ephemeral=True)

class SosManager(discord.ui.View):
    def __init__(
        self,
        timeout: Optional[float] = 60.0,
    ):
        super().__init__(timeout=timeout)
        self.context: commands.Context = None
        self.message: discord.Message = None
        self.value = None
        
    async def start(self, context: commands.Context, embed: discord.Embed):
        msg = await context.send(embed=embed, view=self)
        self.message = msg
    
    @discord.ui.select(
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(label="Add", emoji="📥", description="Add managers."),
            discord.SelectOption(label="Remove", emoji="📤", description="Remove managers.")
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        # sourcery skip: low-code-quality
        for x in self.children:
            x.disabled = True

        await self.message.edit(view=self)
        
        if select.values[0] == "Add":
            addview = SosManagerAdd()
            await interaction.response.send_modal(addview)

            await addview.wait()

            if not addview.role_ids.value:
                return

            val = addview.role_ids.value.split(",")
            
            added_roles = []
            failed_roles = []
            for i in val:
                try:
                    sosman = await self.config.guild(interaction.guild).sosmanager_ids()
                    rol = interaction.guild.get_role(int(i))
                    if rol.id in sosman:
                        failed_roles.append(rol.id)
                        continue
                    async with self.config.guild(interaction.guild).sosmanager_ids() as sosmanids:
                        sosmanids.append(rol.id)
                    added_roles.append(rol.id)
                except Exception:
                    failed_roles.append(i)

            embed = discord.Embed(
                description=f"{humanize_list([f'<@&{role}>' for role in added_roles]) or '`None`'} were added to the manager list.",
                color=await self.context.embed_colour()
            )
            await self.message.edit(embed=embed)

            if failed_roles:
                embed = discord.Embed(
                    title="Failed to add some roles.",
                    description="Most likely that the role does not exist or Typo or role is already a manager.",
                    colour=await self.context.embed_colour(),
                    timestamp=datetime.datetime.now(datetime.timezone.utc)
                )
                embed.add_field(name="Raw Input:", value=box(addview.role_ids.value, "py"), inline=False)
                embed.add_field(name="Failed Roles:", value=humanize_list([f'<@&{role}>' for role in failed_roles]), inline=False)
                await interaction.followup.send(embed=embed, ephemeral=True)

        if select.values[0] == "Remove":
            removeview = SosManagerRemove()
            await interaction.response.send_modal(removeview)

            await removeview.wait()

            if not removeview.role_ids.value:
                return

            val = removeview.role_ids.value.split(",")

            removed_roles = []
            failed_roles = []
            for i in val:
                try:
                    sosman = await self.config.guild(interaction.guild).sosmanager_ids()
                    rol = interaction.guild.get_role(int(i))
                    if rol.id not in sosman:
                        failed_roles.append(rol.id)
                        continue
                    async with self.config.guild(interaction.guild).sosmanager_ids() as sosmanids:
                        index = sosmanids.index(rol.id)
                        sosmanids.pop(index)
                    removed_roles.append(rol.id)
                except Exception:
                    failed_roles.append(i)

            embed = discord.Embed(
                description=f"{humanize_list([f'<@&{role}>' for role in removed_roles]) or '`None`'} were removed from the manager list.",
                color=await self.context.embed_colour()
            )
            await self.message.edit(embed=embed)

            if failed_roles:
                embed = discord.Embed(
                    title="Failed to remove some roles.",
                    description="Most likely that the role does not exist or Typo or role is not a manager.",
                    colour=await self.context.embed_colour(),
                    timestamp=datetime.datetime.now(datetime.timezone.utc)
                )
                embed.add_field(name="Raw Input:", value=box(removeview.role_ids.value, "py"), inline=False)
                embed.add_field(name="Failed Roles:", value=humanize_list([f'<@&{role}>' for role in failed_roles]), inline=False)
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
        for x in self.children:
            x.disabled = True
        self.stop()
        await self.message.edit(view=self)
        
class SosButton(discord.ui.View):
    def __init__(self, timeout: Optional[float] = 60.0):
        super().__init__(timeout=timeout)
        self.player: discord.Member = None
        self.message: discord.Message = None
        self.value = None
        
    async def start(self, player: discord.Member, embed: discord.Embed):
        msg = await player.send(embed=embed, view=self)
        self.message = msg
        self.player = player
    
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
        await self.player.send(content="You took too long to respond! Therefor you automatically choose forfeit.")
        await self.message.edit(view=self)