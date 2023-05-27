import discord

from redbot.core import commands
from redbot.core.utils.chat_formatting import box

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

    async def start(
        self,
        context: commands.Context,
        confirmation_msg: str,
        confirm_action: str,
        *args,
        **kwargs
    ):
        msg = await context.send(content=confirmation_msg, view=self, *args, **kwargs)
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

class FieldsModal(discord.ui.Modal):
    def __init__(self, title: str):
        super().__init__(title=title)

    name = discord.ui.TextInput(
        label="Field Name.",
        style=discord.TextStyle.short,
        max_length=50,
        required=True
    )
    value = discord.ui.TextInput(
        label="Field Value.",
        style=discord.TextStyle.short,
        max_length=50,
        required=True
    )
    inline = discord.ui.TextInput(
        label="Field Inline. (must be true or false only)",
        style=discord.TextStyle.short,
        max_length=50,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="Successfully submitted.", ephemeral=True)

class GiveawayFields(discord.ui.View):
    def __init__(self, timeout: Optional[float] = 60.0):
        super().__init__(timeout=timeout)
        self.context: commands.Context = None
        self.message: discord.Message = None

    async def start(
        self,
        context: commands.Context,
        *args,
        **kwargs
    ):
        msg = await context.send(view=self, *args, **kwargs)
        self.context = context
        self.message = msg

    async def gtype(self, interaction: discord.Interaction):
        modal = FieldsModal(title="Giveaway type field.")
        await interaction.response.send_modal(modal)

        await modal.wait()

        name = modal.name.value
        value = modal.value.value
        inline = modal.inline.value
        guild = interaction.guild

        if not name or not value or not inline:
            return

        if inline.lower() in ["true", "1", "yes"]:
            inline = True
        elif inline.lower() in ["false", "0", "no"]:
            inline = False
        else:
            return await self.message.edit(
                content="Your answer for the inline value should only be `true` or `false`, "
                "redo the command again.",
                embed=None
            )

        await self.context.cog.config.guild(guild).embeds.giveaway.g_fields.g_type.g_tname.set(name)
        await self.context.cog.config.guild(guild).embeds.giveaway.g_fields.g_type.g_tvalue.set(value)
        await self.context.cog.config.guild(guild).embeds.giveaway.g_fields.g_type.g_tinline.set(inline)

        final = f"""
        The giveaway embed type field name has been set to:
        {box(name, 'py')}
        The giveaway embed type field value has been set to:
        {box(value, 'py')}
        The giveaway embed type field inline has been set to:
        {box(inline, 'py')}
        """
        await self.message.edit(content=final, embed=None)

    async def gspon(self, interaction: discord.Interaction):
        modal = FieldsModal(title="Giveaway sponsor field.")
        await interaction.response.send_modal(modal)

        await modal.wait()

        name = modal.name.value
        value = modal.value.value
        inline = modal.inline.value
        guild = interaction.guild

        if not name or not value or not inline:
            return

        if inline.lower() in ["true", "1", "yes"]:
            inline = True
        elif inline.lower() in ["false", "0", "no"]:
            inline = False
        else:
            return await self.message.edit(
                content="Your answer for the inline value should only be `true` or `false`, "
                "redo the command again.",
                embed=None
            )

        await self.context.cog.config.guild(guild).embeds.giveaway.g_fields.g_spon.g_sname.set(name)
        await self.context.cog.config.guild(guild).embeds.giveaway.g_fields.g_spon.g_svalue.set(value)
        await self.context.cog.config.guild(guild).embeds.giveaway.g_fields.g_spon.g_sinline.set(inline)

        final = f"""
        The giveaway embed sponsor field name has been set to:
        {box(name, 'py')}
        The giveaway embed sponsor field value has been set to:
        {box(value, 'py')}
        The giveaway embed sponsor field inline has been set to:
        {box(inline, 'py')}
        """
        await self.message.edit(content=final, embed=None)

    async def gdura(self, interaction: discord.Interaction):
        modal = FieldsModal(title="Giveaway duration field.")
        await interaction.response.send_modal(modal)

        await modal.wait()

        name = modal.name.value
        value = modal.value.value
        inline = modal.inline.value
        guild = interaction.guild

        if not name or not value or not inline:
            return

        if inline.lower() in ["true", "1", "yes"]:
            inline = True
        elif inline.lower() in ["false", "0", "no"]:
            inline = False
        else:
            return await self.message.edit(
                content="Your answer for the inline value should only be `true` or `false`, "
                "redo the command again.",
                embed=None
            )

        await self.context.cog.config.guild(guild).embeds.giveaway.g_fields.g_dura.g_dname.set(name)
        await self.context.cog.config.guild(guild).embeds.giveaway.g_fields.g_dura.g_dvalue.set(value)
        await self.context.cog.config.guild(guild).embeds.giveaway.g_fields.g_dura.g_dinline.set(inline)

        final = f"""
        The giveaway embed duration field name has been set to:
        {box(name, 'py')}
        The giveaway embed duration field value has been set to:
        {box(value, 'py')}
        The giveaway embed duration field inline has been set to:
        {box(inline, 'py')}
        """
        await self.message.edit(content=final, embed=None)

    async def gwinn(self, interaction: discord.Interaction):
        modal = FieldsModal(title="Giveaway winners field.")
        await interaction.response.send_modal(modal)

        await modal.wait()

        name = modal.name.value
        value = modal.value.value
        inline = modal.inline.value
        guild = interaction.guild

        if not name or not value or not inline:
            return

        if inline.lower() in ["true", "1", "yes"]:
            inline = True
        elif inline.lower() in ["false", "0", "no"]:
            inline = False
        else:
            return await self.message.edit(
                content="Your answer for the inline value should only be `true` or `false`, "
                "redo the command again.",
                embed=None
            )

        await self.context.cog.config.guild(guild).embeds.giveaway.g_fields.g_winn.g_wname.set(name)
        await self.context.cog.config.guild(guild).embeds.giveaway.g_fields.g_winn.g_wvalue.set(value)
        await self.context.cog.config.guild(guild).embeds.giveaway.g_fields.g_winn.g_winline.set(inline)

        final = f"""
        The giveaway embed winners field name has been set to:
        {box(name, 'py')}
        The giveaway embed winners field value has been set to:
        {box(value, 'py')}
        The giveaway embed winners field inline has been set to:
        {box(inline, 'py')}
        """
        await self.message.edit(content=final, embed=None)

    async def grequ(self, interaction: discord.Interaction):
        modal = FieldsModal(title="Giveaway requirements field.")
        await interaction.response.send_modal(modal)

        await modal.wait()

        name = modal.name.value
        value = modal.value.value
        inline = modal.inline.value
        guild = interaction.guild

        if not name or not value or not inline:
            return

        if inline.lower() in ["true", "1", "yes"]:
            inline = True
        elif inline.lower() in ["false", "0", "no"]:
            inline = False
        else:
            return await self.message.edit(
                content="Your answer for the inline value should only be `true` or `false`, "
                "redo the command again.",
                embed=None
            )

        await self.context.cog.config.guild(guild).embeds.giveaway.g_fields.g_requ.g_rname.set(name)
        await self.context.cog.config.guild(guild).embeds.giveaway.g_fields.g_requ.g_rvalue.set(value)
        await self.context.cog.config.guild(guild).embeds.giveaway.g_fields.g_requ.g_rinline.set(inline)

        final = f"""
        The giveaway embed requirements field name has been set to:
        {box(name, 'py')}
        The giveaway embed requirements field value has been set to:
        {box(value, 'py')}
        The giveaway embed requirements field inline has been set to:
        {box(inline, 'py')}
        """
        await self.message.edit(content=final, embed=None)

    async def gpriz(self, interaction: discord.Interaction):
        modal = FieldsModal(title="Giveaway prize field.")
        await interaction.response.send_modal(modal)

        await modal.wait()

        name = modal.name.value
        value = modal.value.value
        inline = modal.inline.value
        guild = interaction.guild

        if not name or not value or not inline:
            return

        if inline.lower() in ["true", "1", "yes"]:
            inline = True
        elif inline.lower() in ["false", "0", "no"]:
            inline = False
        else:
            return await self.message.edit(
                content="Your answer for the inline value should only be `true` or `false`, "
                "redo the command again.",
                embed=None
            )

        await self.context.cog.config.guild(guild).embeds.giveaway.g_fields.g_priz.g_pname.set(name)
        await self.context.cog.config.guild(guild).embeds.giveaway.g_fields.g_priz.g_pvalue.set(value)
        await self.context.cog.config.guild(guild).embeds.giveaway.g_fields.g_priz.g_pinline.set(inline)

        final = f"""
        The giveaway embed prize field name has been set to:
        {box(name, 'py')}
        The giveaway embed prize field value has been set to:
        {box(value, 'py')}
        The giveaway embed prize field inline has been set to:
        {box(inline, 'py')}
        """
        await self.message.edit(content=final, embed=None)

    async def gmess(self, interaction: discord.Interaction):
        modal = FieldsModal(title="Giveaway message field.")
        await interaction.response.send_modal(modal)

        await modal.wait()

        name = modal.name.value
        value = modal.value.value
        inline = modal.inline.value
        guild = interaction.guild

        if not name or not value or not inline:
            return

        if inline.lower() in ["true", "1", "yes"]:
            inline = True
        elif inline.lower() in ["false", "0", "no"]:
            inline = False
        else:
            return await self.message.edit(
                content="Your answer for the inline value should only be `true` or `false`, "
                "redo the command again.",
                embed=None
            )

        await self.context.cog.config.guild(guild).embeds.giveaway.g_fields.g_mess.g_mname.set(name)
        await self.context.cog.config.guild(guild).embeds.giveaway.g_fields.g_mess.g_mvalue.set(value)
        await self.context.cog.config.guild(guild).embeds.giveaway.g_fields.g_mess.g_minline.set(inline)

        final = f"""
        The giveaway embed message field name has been set to:
        {box(name, 'py')}
        The giveaway embed message field value has been set to:
        {box(value, 'py')}
        The giveaway embed message field inline has been set to:
        {box(inline, 'py')}
        """
        await self.message.edit(content=final, embed=None)

    @discord.ui.select(
        min_values=1,
        max_values=1,
        placeholder="Choose what giveaways fields to set.",
        options=[
            discord.SelectOption(
                label="Type Field.",
                value="gtype",
                description="Customize the type field.",
                emoji="🏷️"
            ),
            discord.SelectOption(
                label="Sponsor Field.",
                value="gspon",
                description="Customize the sponsor field.",
                emoji="🥳"
            ),
            discord.SelectOption(
                label="Duration Field.",
                value="gdura",
                description="Customize the duration field.",
                emoji="⌛"
            ),
            discord.SelectOption(
                label="Winners Field.",
                value="gwinn",
                description="Customize the winners field.",
                emoji="🎖️"
            ),
            discord.SelectOption(
                label="Requirements Field.",
                value="grequ",
                description="Customize the requirements field.",
                emoji="📜"
            ),
            discord.SelectOption(
                label="Prize Field.",
                value="gpriz",
                description="Customize the prize field.",
                emoji="🏆"
            ),
            discord.SelectOption(
                label="Message Field.",
                value="gmess",
                description="Customize the message field.",
                emoji="💬"
            ),
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        for x in self.children:
            x.disabled = True
        await self.message.edit(view=self)

        if select.values[0] == "gtype":
            return await self.gtype(interaction=interaction)
        if select.values[0] == "gspon":
            return await self.gspon(interaction=interaction)
        if select.values[0] == "gdura":
            return await self.gdura(interaction=interaction)
        if select.values[0] == "gwinn":
            return await self.gwinn(interaction=interaction)
        if select.values[0] == "grequ":
            return await self.grequ(interaction=interaction)
        if select.values[0] == "gpriz":
            return await self.gpriz(interaction=interaction)
        if select.values[0] == "gmess":
            return await self.gmess(interaction=interaction)

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

class EventFields(discord.ui.View):
    def __init__(self, timeout: Optional[float] = 60):
        super().__init__(timeout=timeout)
        self.context: commands.Context = None
        self.message: discord.Message = None

    async def start(
        self,
        context: commands.Context,
        *args,
        **kwargs
    ):
        msg = await context.send(view=self, *args, **kwargs)
        self.context = context
        self.message = msg

    async def espon(self, interaction: discord.Interaction):
        modal = FieldsModal(title="Event sponsor field.")
        await interaction.response.send_modal(modal)

        await modal.wait()

        name = modal.name.value
        value = modal.value.value
        inline = modal.inline.value
        guild = interaction.guild

        if not name or not value or not inline:
            return

        if inline.lower() in ["true", "1", "yes"]:
            inline = True
        elif inline.lower() in ["false", "0", "no"]:
            inline = False
        else:
            return await self.message.edit(
                content="Your answer for the inline value should only be `true` or `false`, "
                "redo the command again.",
                embed=None
            )

        await self.context.cog.config.guild(guild).embeds.event.e_fields.e_spon.e_sname.set(name)
        await self.context.cog.config.guild(guild).embeds.event.e_fields.e_spon.e_svalue.set(value)
        await self.context.cog.config.guild(guild).embeds.event.e_fields.e_spon.e_sinline.set(inline)

        final = f"""
        The event embed sponsor field name has been set to:
        {box(name, 'py')}
        The event embed sponsor field value has been set to:
        {box(value, 'py')}
        The event embed sponsor field inline has been set to:
        {box(inline, 'py')}
        """
        await self.message.edit(content=final, embed=None)

    async def ename(self, interaction: discord.Interaction):
        modal = FieldsModal(title="Event name field.")
        await interaction.response.send_modal(modal)

        await modal.wait()

        name = modal.name.value
        value = modal.value.value
        inline = modal.inline.value
        guild = interaction.guild

        if not name or not value or not inline:
            return

        if inline.lower() in ["true", "1", "yes"]:
            inline = True
        elif inline.lower() in ["false", "0", "no"]:
            inline = False
        else:
            return await self.message.edit(
                content="Your answer for the inline value should only be `true` or `false`, "
                "redo the command again.",
                embed=None
            )

        await self.context.cog.config.guild(guild).embeds.event.e_fields.e_name.e_nname.set(name)
        await self.context.cog.config.guild(guild).embeds.event.e_fields.e_name.e_nvalue.set(value)
        await self.context.cog.config.guild(guild).embeds.event.e_fields.e_name.e_ninline.set(inline)

        final = f"""
        The event embed name field name has been set to:
        {box(name, 'py')}
        The event embed name field value has been set to:
        {box(value, 'py')}
        The event embed name field inline has been set to:
        {box(inline, 'py')}
        """
        await self.message.edit(content=final, embed=None)

    async def erequ(self, interaction: discord.Interaction):
        modal = FieldsModal(title="Event requirements field.")
        await interaction.response.send_modal(modal)

        await modal.wait()

        name = modal.name.value
        value = modal.value.value
        inline = modal.inline.value
        guild = interaction.guild

        if not name or not value or not inline:
            return

        if inline.lower() in ["true", "1", "yes"]:
            inline = True
        elif inline.lower() in ["false", "0", "no"]:
            inline = False
        else:
            return await self.message.edit(
                content="Your answer for the inline value should only be `true` or `false`, "
                "redo the command again.",
                embed=None
            )

        await self.context.cog.config.guild(guild).embeds.event.e_fields.e_requ.e_rname.set(name)
        await self.context.cog.config.guild(guild).embeds.event.e_fields.e_requ.e_rvalue.set(value)
        await self.context.cog.config.guild(guild).embeds.event.e_fields.e_requ.e_rinline.set(inline)

        final = f"""
        The event embed requirements field name has been set to:
        {box(name, 'py')}
        The event embed requirements field value has been set to:
        {box(value, 'py')}
        The event embed requirements field inline has been set to:
        {box(inline, 'py')}
        """
        await self.message.edit(content=final, embed=None)

    async def epriz(self, interaction: discord.Interaction):
        modal = FieldsModal(title="Event prize field.")
        await interaction.response.send_modal(modal)

        await modal.wait()

        name = modal.name.value
        value = modal.value.value
        inline = modal.inline.value
        guild = interaction.guild

        if not name or not value or not inline:
            return

        if inline.lower() in ["true", "1", "yes"]:
            inline = True
        elif inline.lower() in ["false", "0", "no"]:
            inline = False
        else:
            return await self.message.edit(
                content="Your answer for the inline value should only be `true` or `false`, "
                "redo the command again.",
                embed=None
            )

        await self.context.cog.config.guild(guild).embeds.event.e_fields.e_priz.e_pname.set(name)
        await self.context.cog.config.guild(guild).embeds.event.e_fields.e_priz.e_pvalue.set(value)
        await self.context.cog.config.guild(guild).embeds.event.e_fields.e_priz.e_pinline.set(inline)

        final = f"""
        The event embed prize field name has been set to:
        {box(name, 'py')}
        The event embed prize field value has been set to:
        {box(value, 'py')}
        The event embed prize field inline has been set to:
        {box(inline, 'py')}
        """
        await self.message.edit(content=final, embed=None)

    async def emess(self, interaction: discord.Interaction):
        modal = FieldsModal(title="Event message field.")
        await interaction.response.send_modal(modal)

        await modal.wait()

        name = modal.name.value
        value = modal.value.value
        inline = modal.inline.value
        guild = interaction.guild

        if not name or not value or not inline:
            return

        if inline.lower() in ["true", "1", "yes"]:
            inline = True
        elif inline.lower() in ["false", "0", "no"]:
            inline = False
        else:
            return await self.message.edit(
                content="Your answer for the inline value should only be `true` or `false`, "
                "redo the command again.",
                embed=None
            )

        await self.context.cog.config.guild(guild).embeds.event.e_fields.e_mess.e_mname.set(name)
        await self.context.cog.config.guild(guild).embeds.event.e_fields.e_mess.e_mvalue.set(value)
        await self.context.cog.config.guild(guild).embeds.event.e_fields.e_mess.e_minline.set(inline)

        final = f"""
        The event embed message field name has been set to:
        {box(name, 'py')}
        The event embed message field value has been set to:
        {box(value, 'py')}
        The event embed message field inline has been set to:
        {box(inline, 'py')}
        """
        await self.message.edit(content=final, embed=None)

    async def etype(self, interaction: discord.Interaction):
        modal = FieldsModal(title="Events type field.")
        await interaction.response.send_modal(modal)

        await modal.wait()

        name = modal.name.value
        value = modal.value.value
        inline = modal.inline.value
        guild = interaction.guild

        if not name or not value or not inline:
            return

        if inline.lower() in ["true", "1", "yes"]:
            inline = True
        elif inline.lower() in ["false", "0", "no"]:
            inline = False
        else:
            return await self.message.edit(
                content="Your answer for the inline value should only be `true` or `false`, "
                "redo the command again.",
                embed=None
            )

        await self.context.cog.config.guild(guild).embeds.event.e_fields.e_type.e_tname.set(name)
        await self.context.cog.config.guild(guild).embeds.event.e_fields.e_type.e_tvalue.set(value)
        await self.context.cog.config.guild(guild).embeds.event.e_fields.e_type.e_tinline.set(inline)

        final = f"""
        The event embed type field name has been set to:
        {box(name, 'py')}
        The event embed type field value has been set to:
        {box(value, 'py')}
        The event embed type field inline has been set to:
        {box(inline, 'py')}
        """
        await self.message.edit(content=final, embed=None)

    @discord.ui.select(
        max_values=1,
        min_values=1,
        placeholder="Choose what event fields to set.",
        options=[
            discord.SelectOption(
                label="Type Field.",
                value="etype",
                description="Customize the type field.",
                emoji="🏷️"
            ),
            discord.SelectOption(
                label="Sponsor Field.",
                value="espon",
                description="Customize the sponsor field.",
                emoji="🥳"
            ),
            discord.SelectOption(
                label="Name Field.",
                value="ename",
                description="Customize the name field.",
                emoji="🎊"
            ),
            discord.SelectOption(
                label="Requirements Field.",
                value="erequ",
                description="Customize the requirements field.",
                emoji="📜"
            ),
            discord.SelectOption(
                label="Prize Field.",
                value="epriz",
                description="Customize the prize field.",
                emoji="🏆"
            ),
            discord.SelectOption(
                label="Message Field.",
                value="emess",
                description="Customize the message field.",
                emoji="💬"
            ),
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        for x in self.children:
            x.disabled = True
        await self.message.edit(view=self)

        if select.values[0] == "etype":
            return await self.etype(interaction=interaction)
        if select.values[0] == "espon":
            return await self.espon(interaction=interaction)
        if select.values[0] == "ename":
            return await self.ename(interaction=interaction)
        if select.values[0] == "erequ":
            return await self.erequ(interaction=interaction)
        if select.values[0] == "epriz":
            return await self.epriz(interaction=interaction)
        if select.values[0] == "emess":
            return await self.emess(interaction=interaction)

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

class HeistFields(discord.ui.View):
    def __init__(self, timeout: Optional[float] = 60):
        super().__init__(timeout=timeout)
        self.context: commands.Context = None
        self.message: discord.Message = None

    async def start(
        self,
        context: commands.Context,
        *args,
        **kwargs
    ):
        msg = await context.send(view=self, *args, **kwargs)
        self.context = context
        self.message = msg

    async def hspon(self, interaction: discord.Interaction):
        modal = FieldsModal("Heist sponsor field.")
        await interaction.response.send_modal(modal)

        await modal.wait()

        name = modal.name.value
        value = modal.value.value
        inline = modal.inline.value
        guild = interaction.guild

        if not name or not value or not inline:
            return

        if inline.lower() in ["true", "1", "yes"]:
            inline = True
        elif inline.lower() in ["false", "0", "no"]:
            inline = False
        else:
            return await self.message.edit(
                content="Your answer for the inline value should only be `true` or `false`, "
                "redo the command again.",
                embed=None
            )

        await self.context.cog.config.guild(guild).embeds.heist.h_fields.h_spon.h_sname.set(name)
        await self.context.cog.config.guild(guild).embeds.heist.h_fields.h_spon.h_svalue.set(value)
        await self.context.cog.config.guild(guild).embeds.heist.h_fields.h_spon.h_sinline.set(inline)

        final = f"""
        The heist embed sponsor field name has been set to:
        {box(name, 'py')}
        The heist embed sponsor field value has been set to:
        {box(value, 'py')}
        The heist embed sponsor field inline has been set to:
        {box(inline, 'py')}
        """
        await self.message.edit(content=final, embed=None)

    async def hamou(self, interaction: discord.Interaction):
        modal = FieldsModal("Heist amount field.")
        await interaction.response.send_modal(modal)

        await modal.wait()

        name = modal.name.value
        value = modal.value.value
        inline = modal.inline.value
        guild = interaction.guild

        if not name or not value or not inline:
            return

        if inline.lower() in ["true", "1", "yes"]:
            inline = True
        elif inline.lower() in ["false", "0", "no"]:
            inline = False
        else:
            return await self.message.edit(
                content="Your answer for the inline value should only be `true` or `false`, "
                "redo the command again.",
                embed=None
            )

        await self.context.cog.config.guild(guild).embeds.heist.h_fields.h_amou.h_aname.set(name)
        await self.context.cog.config.guild(guild).embeds.heist.h_fields.h_amou.h_avalue.set(value)
        await self.context.cog.config.guild(guild).embeds.heist.h_fields.h_amou.h_ainline.set(inline)

        final = f"""
        The heist embed amount field name has been set to:
        {box(name, 'py')}
        The heist embed amount field value has been set to:
        {box(value, 'py')}
        The heist embed amount field inline has been set to:
        {box(inline, 'py')}
        """
        await self.message.edit(content=final, embed=None)

    async def hrequ(self, interaction: discord.Interaction):
        modal = FieldsModal("Heist requirements field.")
        await interaction.response.send_modal(modal)

        await modal.wait()

        name = modal.name.value
        value = modal.value.value
        inline = modal.inline.value
        guild = interaction.guild

        if not name or not value or not inline:
            return

        if inline.lower() in ["true", "1", "yes"]:
            inline = True
        elif inline.lower() in ["false", "0", "no"]:
            inline = False
        else:
            return await self.message.edit(
                content="Your answer for the inline value should only be `true` or `false`, "
                "redo the command again.",
                embed=None
            )

        await self.context.cog.config.guild(guild).embeds.heist.h_fields.h_requ.h_rname.set(name)
        await self.context.cog.config.guild(guild).embeds.heist.h_fields.h_requ.h_rvalue.set(value)
        await self.context.cog.config.guild(guild).embeds.heist.h_fields.h_requ.h_rinline.set(inline)

        final = f"""
        The heist embed requirements field name has been set to:
        {box(name, 'py')}
        The heist embed requirements field value has been set to:
        {box(value, 'py')}
        The heist embed requirements field inline has been set to:
        {box(inline, 'py')}
        """
        await self.message.edit(content=final, embed=None)

    async def hmess(self, interaction: discord.Interaction):
        modal = FieldsModal("Heist message field.")
        await interaction.response.send_modal(modal)

        await modal.wait()

        name = modal.name.value
        value = modal.value.value
        inline = modal.inline.value
        guild = interaction.guild

        if not name or not value or not inline:
            return

        if inline.lower() in ["true", "1", "yes"]:
            inline = True
        elif inline.lower() in ["false", "0", "no"]:
            inline = False
        else:
            return await self.message.edit(
                content="Your answer for the inline value should only be `true` or `false`, "
                "redo the command again.",
                embed=None
            )

        await self.context.cog.config.guild(guild).embeds.heist.h_fields.h_mess.h_mname.set(name)
        await self.context.cog.config.guild(guild).embeds.heist.h_fields.h_mess.h_mvalue.set(value)
        await self.context.cog.config.guild(guild).embeds.heist.h_fields.h_mess.h_minline.set(inline)

        final = f"""
        The heist embed message field name has been set to:
        {box(name, 'py')}
        The heist embed message field value has been set to:
        {box(value, 'py')}
        The heist embed message field inline has been set to:
        {box(inline, 'py')}
        """
        await self.message.edit(content=final, embed=None)

    async def htype(self, interaction: discord.Interaction):
        modal = FieldsModal("Heist type field.")
        await interaction.response.send_modal(modal)

        await modal.wait()

        name = modal.name.value
        value = modal.value.value
        inline = modal.inline.value
        guild = interaction.guild

        if not name or not value or not inline:
            return

        if inline.lower() in ["true", "1", "yes"]:
            inline = True
        elif inline.lower() in ["false", "0", "no"]:
            inline = False
        else:
            return await self.message.edit(
                content="Your answer for the inline value should only be `true` or `false`, "
                "redo the command again.",
                embed=None
            )

        await self.context.cog.config.guild(guild).embeds.heist.h_fields.h_type.h_tname.set(name)
        await self.context.cog.config.guild(guild).embeds.heist.h_fields.h_type.h_tvalue.set(value)
        await self.context.cog.config.guild(guild).embeds.heist.h_fields.h_type.h_tinline.set(inline)

        final = f"""
        The heist embed type field name has been set to:
        {box(name, 'py')}
        The heist embed type field value has been set to:
        {box(value, 'py')}
        The heist embed type field inline has been set to:
        {box(inline, 'py')}
        """
        await self.message.edit(content=final, embed=None)
    
    @discord.ui.select(
        max_values=1,
        min_values=1,
        placeholder="Choose what heist fields to set.",
        options=[
            discord.SelectOption(
                label="Sponsor Field.",
                value="hspon",
                description="Customize the sponsor field.",
                emoji="🥳"
            ),
            discord.SelectOption(
                label="Type Field.",
                value="htype",
                description="Customize the type field.",
                emoji="🏷️"
            ),
            discord.SelectOption(
                label="Amount Field.",
                value="hamou",
                description="Customize the amount field.",
                emoji="🔢"
            ),
            discord.SelectOption(
                label="Requirements Field.",
                value="hrequ",
                description="Customize the requirements field.",
                emoji="📜"
            ),
            discord.SelectOption(
                label="Message Field.",
                value="hmess",
                description="Customize the message field.",
                emoji="💬"
            ),
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        for x in self.children:
            x.disabled = True
        await self.message.edit(view=self)

        if select.values[0] == "hspon":
            return await self.hspon(interaction=interaction)
        if select.values[0] == "hamou":
            return await self.hamou(interaction=interaction)
        if select.values[0] == "hrequ":
            return await self.hrequ(interaction=interaction)
        if select.values[0] == "hmess":
            return await self.hmess(interaction=interaction)
        if select.values[0] == "htype":
            return await self.htype(interaction=interaction)

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