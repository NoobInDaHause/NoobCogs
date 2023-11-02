import asyncio
import contextlib
import discord
import noobutils as nu

from redbot.core.bot import commands
from redbot.core.utils import chat_formatting as cf

from typing import Dict, List, TYPE_CHECKING, Union

from .exceptions import MoreThanThreeRoles
from .utilities import verify_amount_roles, verify_channel, verify_emoji, verify_roles

if TYPE_CHECKING:
    from . import DonationLogger


class DonationLoggerSetupView(discord.ui.View):
    def __init__(self, cog: "DonationLogger", timeout: float = 180.0):
        super().__init__(timeout=timeout)
        self.cog = cog
        self.message: discord.Message = None
        self.context: commands.Context = None
        self.autorole = False
        self.log_channel: discord.TextChannel = None
        self.manager_roles: List[discord.Role] = []
        self.bank: Dict[str, Union[discord.Emoji, str]] = {}
        self.amount_roles: Dict[str, List[discord.Role]] = {}

    async def start(self, context: commands.Context):
        self.context = context
        msg_embed = await self.update_embed_setup()
        msg = await context.send(embed=msg_embed, view=self)
        self.message = msg

    async def update_embed_setup(self) -> discord.Embed:
        banks2 = f"{self.bank['emoji']} {self.bank['name']}" if self.bank else "None"
        ar2 = "".join(
            [
                f"` - ` **{cf.humanize_number(int(k))}**: {cf.humanize_list([role.mention for role in v])}\n"
                for k, v in self.amount_roles.items()
            ]
            if self.amount_roles
            else ["None"]
        )
        man_r2 = (
            cf.humanize_list([r.mention for r in self.manager_roles])
            if self.manager_roles
            else "None"
        )
        lchan = self.log_channel.mention if self.log_channel else "None"
        return discord.Embed(
            title=f"DonationLogger setup for [{self.context.guild.name}]",
            description=f"**Manager Roles:** {man_r2}\n"
            f"**Bank:** {banks2}\n"
            f"**Auto Role:** {self.autorole}\n"
            f"**Log Channel:** {lchan}\n"
            f"**Bank Amount-Roles:**\n{ar2}",
            colour=await self.context.embed_colour(),
        )

    @discord.ui.button(
        emoji="👥",
        label="Manager Roles (Required)",
        style=nu.get_button_colour("blurple"),
    )
    async def manager_roles_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()
        msg = await self.message.reply(
            content="You have 30 seconds to input a single role or multiple roles separated by `,`.\n"
            "` - ` Role(s) can be **role Mention/ID/Name** or input **none** to reset this field."
        )
        try:
            m_msg = await self.context.bot.wait_for(
                "message",
                check=lambda x: x.channel.id == self.context.channel.id
                and x.author.id == self.context.author.id,
                timeout=30,
            )
        except asyncio.TimeoutError:
            return await msg.edit(
                content="You took too long to respond.", delete_after=5
            )
        with contextlib.suppress(Exception):
            if m_msg.content.lower() == "none":
                self.manager_roles = []
                await msg.delete()
                await m_msg.delete()
                m_cont = await self.update_embed_setup()
                return await self.message.edit(embed=m_cont, view=self)
            roles = await verify_roles(self.context, m_msg.content.split(","))
            if not roles:
                await m_msg.delete()
                return await msg.edit(
                    content="Those do not seem to be valid roles.", delete_after=5
                )
            await msg.delete()
            await m_msg.delete()
            self.manager_roles = roles
            msg_cont = await self.update_embed_setup()
            await self.message.edit(embed=msg_cont, view=self)

    @discord.ui.button(
        emoji="🏦",
        label="Bank Name and Emoji (Required)",
        style=nu.get_button_colour("blurple"),
    )
    async def bank_name_and_emoji_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()
        msg = await self.message.reply(
            content="You have 30 seconds to input your first bank name and emoji or **none** to reset:"
            "\n` - ` **Note:** Bank name first then emoji and then separate both with `,`.\n"
            "` - ` **Example:** `dank,💰`\n` - ` You can add more banks later after the setup is done."
        )
        try:
            m_bank = await self.context.bot.wait_for(
                "message",
                check=lambda x: x.channel.id == self.context.channel.id
                and x.author.id == self.context.author.id,
                timeout=30,
            )
        except asyncio.TimeoutError:
            return await msg.edit(
                content="You took too long to respond.", delete_after=5
            )
        with contextlib.suppress(Exception):
            if m_bank.content.lower() == "none":
                self.bank = {}
                m_cont = await self.update_embed_setup()
                await m_bank.delete()
                await msg.delete()
                return await self.message.edit(embed=m_cont, view=self)
            _b = m_bank.content.split(",")
            if len(_b) < 2:
                await m_bank.delete()
                return await msg.edit(
                    content="That does not seem to be a valid bank name or emoji.",
                    delete_after=5,
                )
            bank_name = _b[0]
            if " " in bank_name:
                await m_bank.delete()
                return await msg.edit(
                    content="Spaces are not allowed for bank names.", delete_after=5
                )
            if len(bank_name) > 20:
                await m_bank.delete()
                return await msg.edit(
                    content="Keep the bank names under 20 characters.", delete_after=5
                )
            emoji = await verify_emoji(self.context, _b[1])
            if not emoji or not bank_name:
                await m_bank.delete()
                return await msg.edit(
                    content="I don't seem to recognize that emoji or bank name is invalid.",
                    delete_after=5,
                )
            self.bank["name"] = bank_name
            self.bank["emoji"] = emoji
            co = await self.update_embed_setup()
            await m_bank.delete()
            await msg.delete()
            await self.message.edit(embed=co, view=self)

    @discord.ui.button(
        emoji="🔄",
        label="Auto Add or Remove Roles (Optional)",
        style=nu.get_button_colour("blurple"),
    )
    async def auto_role_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        current = self.autorole
        self.autorole = not current
        up = await self.update_embed_setup()
        await interaction.response.edit_message(embed=up, view=self)

    @discord.ui.button(
        emoji="📜", label="Log Channel (Optional)", style=nu.get_button_colour("blurple")
    )
    async def log_channel_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer()
        msg = await self.message.reply(
            content="You have 30 seconds to input the log channel, it can be channel mention or channel id "
            "or **none** to reset: (Threads are not supported)"
        )
        try:
            m_chan = await self.context.bot.wait_for(
                "message",
                check=lambda x: x.channel.id == self.context.channel.id
                and x.author.id == self.context.author.id,
                timeout=30,
            )
        except asyncio.TimeoutError:
            return await msg.edit(
                content="You took too long to respond.", delete_after=5
            )
        with contextlib.suppress(Exception):
            if m_chan.content.lower() == "none":
                self.log_channel = None
                m_cont = await self.update_embed_setup()
                await m_chan.delete()
                await msg.delete()
                return await self.message.edit(embed=m_cont, view=self)
            _m = m_chan.content.strip()
            if c := await verify_channel(self.context, _m):
                self.log_channel = c
                await msg.delete()
                await m_chan.delete()
                msg_cont = await self.update_embed_setup()
                await self.message.edit(embed=msg_cont, view=self)
            else:
                await m_chan.delete()
                await msg.edit(content="That's an invalid channel.", delete_after=5)

    @discord.ui.button(
        emoji="🔢",
        label="Bank Amount Roles (Optional)",
        style=nu.get_button_colour("blurple"),
    )
    async def bank_amount_roles_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if not self.bank:
            return await interaction.response.send_message(
                content="You must set a bank and emoji first before you can add amount roles.",
                ephemeral=True,
            )
        await interaction.response.defer()
        msg = await self.message.reply(
            content="You have 30 seconds to input a **amount first** and then role ID/name/mention separate "
            "them with `:`\n` - ` You can add multiple amount roles make sure to separate them "
            "with `,` input **none** to reset.\n` - ` You can have up to 3 roles max per amount."
            "\n` - ` Example: `10m:@role:@role,10k:(role_id),12.5e6:(role_name)`"
        )
        try:
            m_bank = await self.context.bot.wait_for(
                "message",
                check=lambda x: x.channel.id == self.context.channel.id
                and x.author.id == self.context.author.id,
                timeout=30,
            )
        except asyncio.TimeoutError:
            return await msg.edit(
                content="You took too long to respond.", delete_after=5
            )
        with contextlib.suppress(Exception):
            if m_bank.content.lower() == "none":
                self.amount_roles = {}
                await msg.delete()
                await m_bank.delete()
                cop = await self.update_embed_setup()
                return await self.message.edit(embed=cop, view=self)
            _ar = m_bank.content.strip().split(",")
            try:
                arole = await verify_amount_roles(self.context, _ar)
            except MoreThanThreeRoles:
                await m_bank.delete()
                return await msg.edit(
                    content="The maximum roles you can assign to an amount should be no more than 3.",
                    delete_after=5,
                )
            if not arole:
                await m_bank.delete()
                return await msg.edit(
                    content="Those do not seem to be valid roles or invalid amount.",
                    delete_after=5,
                )
            self.amount_roles.update(arole)
            await msg.delete()
            cp = await self.update_embed_setup()
            await m_bank.delete()
            await self.message.edit(embed=cp, view=self)

    @discord.ui.button(emoji="✔️", style=nu.get_button_colour("green"))
    async def done_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if not self.bank:
            return await interaction.response.send_message(
                content="A bank name and emoji is required before you complete the setup.",
                ephemeral=True,
            )
        if not self.manager_roles:
            return await interaction.response.send_message(
                content="At least one role is required for the manager role.",
                ephemeral=True,
            )
        act = "Well alright."
        conf = "Are you sure these informations are correct?"
        view = nu.NoobConfirmation()
        await view.start(interaction, act, True, content=conf)
        await view.wait()
        if not view.value:
            return
        config = self.cog.config.guild
        async with config(interaction.guild).banks() as banks:
            banks |= {
                self.bank["name"].lower(): {
                    "hidden": False,
                    "emoji": str(self.bank["emoji"]),
                    "roles": {},
                    "donators": {},
                }
            }
        async with config(interaction.guild).managers() as managers:
            managers: list = managers
            for j in self.manager_roles:
                if j.id not in managers:
                    managers.append(j.id)
        await config(interaction.guild).auto_role.set(self.autorole)
        if self.log_channel:
            await config(interaction.guild).log_channel.set(self.log_channel.id)
        if self.amount_roles:
            async with config(interaction.guild).banks() as banks:
                banks[self.bank["name"].lower()]["roles"] |= {
                    k: [r.id for r in v] for k, v in self.amount_roles.items()
                }
        await config(interaction.guild).setup.set(True)
        for x in self.children:
            x.disabled = True
        await self.message.edit(view=self)
        await interaction.followup.send(
            content="Alright setup done, you can now use the DonationLogger system."
        )
        self.cog.setupcache.remove(self.context.guild.id)
        self.stop()

    @discord.ui.button(emoji="✖️", style=nu.get_button_colour("red"))
    async def cancel_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.stop()
        self.cog.setupcache.remove(self.context.guild.id)
        await interaction.message.delete()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if await self.context.bot.is_owner(interaction.user):
            return True
        elif interaction.user != self.context.author:
            await interaction.response.send_message(
                content=nu.access_denied(), ephemeral=True
            )
            return False
        else:
            return True

    async def on_timeout(self):
        for x in self.children:
            x.disabled = True
        self.stop()
        self.cog.setupcache.remove(self.context.guild.id)
        await self.message.edit(view=self)


class TotalDonoView(discord.ui.View):
    def __init__(self, cog: "DonationLogger", timeout: float = 60.0):
        super().__init__(timeout=timeout)
        self.cog = cog
        self.member: discord.Member = None
        self.message: discord.Message = None

    async def start(self, context: commands.Context, content: str, member: discord.Member):
        msg = await context.reply(content=content, mention_author=False, view=self)
        self.message = msg
        self.member = member

    @discord.ui.button(label="Total donations", style=nu.get_button_colour("green"))
    async def total_dono(self, interaction: discord.Interaction, button: discord.ui.Button):
        final = {}
        final_overall = []
        async with self.cog.config.guild(interaction.guild).banks() as banks:
            for k, v in banks.items():
                if v["hidden"]:
                    continue
                donations = v["donators"].setdefault(str(self.member.id), 0)
                final[k] = f"{v['emoji']} {cf.humanize_number(donations)}"
                final_overall.append(donations)

        overall = sum(final_overall)
        embed = discord.Embed(
            description=f"Overall combined bank donation amount: {cf.humanize_number(overall)}",
            timestamp=discord.utils.utcnow(),
            colour=self.member.colour,
        )
        embed.set_author(
            name=f"{self.member} ({self.member.id})", icon_url=nu.is_have_avatar(self.member)
        )
        embed.set_footer(
            text=f"{interaction.guild.name} admires your donations!",
            icon_url=nu.is_have_avatar(interaction.guild),
        )
        if final:
            for k, v in final.items():
                embed.add_field(name=k.title(), value=v, inline=True)
        else:
            embed.description = (
                "There are no banks registered yet, or banks are hidden."
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def on_timeout(self):
        for x in self.children:
            x.disabled = True

        self.stop()
        await self.message.edit(view=self)