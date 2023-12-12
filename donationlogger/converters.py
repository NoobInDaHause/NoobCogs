import re

from redbot.core.bot import commands

from noobutils import NoobEmojiConverter

from .exceptions import AmountConversionFailure


class AmountConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str) -> int:
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
            if amount > 999999999999999 or amount < 0:
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


class DLEmojiConverter(NoobEmojiConverter):
    async def convert(self, ctx: commands.Context, argument: str):
        argument = argument.strip()
        return argument if argument == "⏣" else await super().convert(ctx, argument)
