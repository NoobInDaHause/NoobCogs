import discord
import noobutils as nu
import re

from typing import List, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from . import DonationLogger


class AmountConverter(nu.commands.Converter, nu.app_commands.Transformer):
    async def convert(self, ctx: nu.commands.Context, argument: str) -> int:
        amount_dict = {
            "k": 1000,
            "m": 1000000,
            "b": 1000000000,
            "t": 1000000000000,
        }

        try:
            argument = argument.strip().replace(",", "")
            if argument[-1].lower() in amount_dict:
                amt, unit = float(argument[:-1]), argument[-1].lower()
                amount = round(amt * amount_dict[unit])
            else:
                amount = round(float(argument))
        except (ValueError, KeyError) as e:
            if re.search("<@(.*)>", argument):
                raise nu.commands.BadArgument(
                    "The amount comes first then the member."
                ) from e
            raise nu.commands.BadArgument(
                f'Failed to convert "{argument}" into a proper amount.'
            ) from e
        else:
            if amount > 999999999999999 or amount < 0:
                raise nu.commands.BadArgument("Invalid amount provided.")
            return amount

    async def transform(
        self, interaction: discord.Interaction[nu.Red], value: int | float | str
    ) -> str:
        context = await interaction.client.get_context(interaction)
        return await self.convert(context, value)


class DLEmojiConverter(nu.NoobEmojiConverter):
    async def convert(self, ctx: nu.commands.Context, argument: str):
        argument = argument.strip()
        return argument if argument == "⏣" else await super().convert(ctx, argument)


class MemberOrUserConverter(nu.commands.Converter, nu.app_commands.Transformer):
    async def convert(
        self, ctx: nu.commands.Context, argument: str
    ) -> Union[discord.Member, discord.User]:
        try:
            return await nu.commands.MemberConverter().convert(ctx, argument)
        except nu.commands.MemberNotFound:
            return await nu.commands.UserConverter().convert(ctx, argument)

    async def transform(
        self, interaction: discord.Interaction[nu.Red], value: str
    ) -> Union[discord.Member, discord.User]:
        ctx = await interaction.client.get_context(interaction)
        return await self.convert(ctx, value)


class BankConverter(nu.commands.Converter, nu.app_commands.Transformer):
    async def convert(self, ctx: nu.commands.Context, argument: str) -> str:
        BankConversionFailure = nu.commands.BadArgument
        cog: "DonationLogger" = ctx.bot.get_cog("DonationLogger")
        banks: dict = await cog.config.guild(ctx.guild).banks()
        if not banks.get(argument.strip().lower()):
            raise BankConversionFailure(f'Bank "{argument}" does not exist.')
        return argument.strip().lower()

    async def transform(
        self, interaction: discord.Interaction[nu.Red], value: str
    ) -> str:
        context = await interaction.client.get_context(interaction)
        return await self.convert(context, value)

    async def autocomplete(
        self, interaction: discord.Interaction[nu.Red], value: int | float | str
    ) -> List[nu.app_commands.Choice[str | int | float]]:
        cog: "DonationLogger" = interaction.client.get_cog("DonationLogger")
        banks: dict = await cog.config.guild(interaction.guild).banks()
        bank_list: List[str] = [
            bank for bank, bank_info in banks.items() if not bank_info["hidden"]
        ]
        return [
            nu.app_commands.Choice(name=choice.title(), value=choice)
            for choice in bank_list
            if value.lower() in choice.lower()
        ]
