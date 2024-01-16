from redbot.core.bot import commands


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
            if amount > 999999999999999 or amount < 1:
                raise commands.BadArgument("Invalid amount provided.")
            return amount
        except (ValueError, KeyError) as e:
            raise commands.BadArgument(
                f'Failed to convert "{argument}" into a proper amount.'
            ) from e
