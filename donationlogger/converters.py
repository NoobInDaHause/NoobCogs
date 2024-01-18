import discord
import re

from redbot.core.bot import app_commands, commands, Red

from noobutils import NoobEmojiConverter
from typing import List, TYPE_CHECKING

from .checks import check_if_is_a_dono_manager_or_higher, check_if_setup_done
from .exceptions import BankConversionFailure, AmountConversionFailure

if TYPE_CHECKING:
    from . import DonationLogger


class AmountConverter(app_commands.Transformer):
    @classmethod
    async def convert(cls, ctx: commands.Context, argument: str) -> int:
        try:
            argument = argument.strip().replace(",", "")
            amount_dict = {
                "k": 1000,
                "m": 1000000,
                "b": 1000000000,
                "t": 1000000000000,
            }
            if argument[-1].lower() in amount_dict:
                amt, unit = float(argument[:-1]), argument[-1].lower()
                amount = int(amt * amount_dict[unit])
            else:
                amount = int(float(argument))
            if amount > 999999999999999 or amount < 1:
                raise AmountConversionFailure("Invalid amount provided.")
            return amount
        except (ValueError, KeyError) as e:
            if re.search("<@(.*)>", argument):
                raise AmountConversionFailure(
                    "The amount comes first then the member."
                ) from e
            raise AmountConversionFailure(
                f'Failed to convert "{argument}" into a proper amount.'
            ) from e

    @classmethod
    async def transform(
        cls, interaction: discord.Interaction[Red], value: int | float | str
    ) -> str:
        if not await check_if_setup_done(interaction):
            return ["DonationLogger has not been setup in this guild yet.", True]
        if interaction.command.qualified_name not in [
            "donationlogger balance",
            "donationlogger leaderboard",
            "donationlogger donationcheck",
        ] and not await check_if_is_a_dono_manager_or_higher(interaction):
            return [
                "You need to be a donationlogger manager or higher to run this command.",
                True,
            ]
        context = interaction.client.get_context(interaction)
        try:
            return await cls.convert(context, value)
        except AmountConversionFailure as e:
            return [str(e), False]


class DLEmojiConverter(NoobEmojiConverter):
    async def convert(self, ctx: commands.Context, argument: str):
        argument = argument.strip()
        return argument if argument == "⏣" else await super().convert(ctx, argument)


class BankConverter(app_commands.Transformer):
    @classmethod
    async def convert(cls, ctx: commands.Context, argument: str) -> str:
        cog: "DonationLogger" = ctx.bot.get_cog("DonationLogger")
        banks = await cog.config.guild(ctx.guild).banks()
        if not banks.get(argument.strip().lower()):
            raise BankConversionFailure(f'Bank "{argument}" does not exist.')
        return argument.strip().lower()

    @classmethod
    async def transform(cls, interaction: discord.Interaction[Red], value: str) -> str:
        if not await check_if_setup_done(interaction):
            return ["DonationLogger has not been setup in this guild yet.", True]
        if interaction.command.qualified_name not in [
            "donationlogger balance",
            "donationlogger leaderboard",
            "donationlogger donationcheck",
        ] and not await check_if_is_a_dono_manager_or_higher(interaction):
            return [
                "You need to be a donationlogger manager or higher to run this command.",
                True,
            ]

        context = await interaction.client.get_context(interaction)
        try:
            return await cls.convert(context, value)
        except BankConversionFailure as e:
            return [str(e), False]

    async def autocomplete(
        self, interaction: discord.Interaction[Red], value: int | float | str
    ) -> List[app_commands.Choice[str | int | float]]:
        cog: "DonationLogger" = interaction.client.get_cog("DonationLogger")
        banks = await cog.config.guild(interaction.guild).banks()
        bank_list: List[str] = [
            bank for bank, bank_info in banks.items() if not bank_info["hidden"]
        ]
        return [
            app_commands.Choice(name=choice.title(), value=choice)
            for choice in bank_list
            if value.lower() in choice.lower()
        ]
