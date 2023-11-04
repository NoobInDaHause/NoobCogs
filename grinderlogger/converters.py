from redbot.core.bot import commands

from .exceptions import TimeConversionFailure, AmountConversionFailure


class TimeConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str) -> int:
        argument = argument.strip()
        try:
            amount = int(argument[:-1])
        except ValueError as e:
            raise TimeConversionFailure(
                message=f'"{argument}" is not a valid time.'
            ) from e
        unit = argument[-1]
        if unit.lower() in ["s", "m", "h", "d"]:
            if amount < 10 or amount > (14 * 86400):
                raise TimeConversionFailure(
                    message="The time must be greater than 10 seconds or less than 14 days."
                )

            time_multiplier = {"s": 1, "m": 60, "h": 3600, "d": 86400}
            return amount * time_multiplier[unit]

        raise TimeConversionFailure(message=f'"{argument}" is not a valid time.')


class AmountConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, argument) -> int:
        try:
            amount = int(float(argument))
        except ValueError:
            try:
                amount = int(argument)
            except ValueError:
                argument = argument.strip()
                amount_dict = {
                    "k": 1000,
                    "m": 1000000,
                    "b": 1000000000,
                    "t": 1000000000000,
                }
                try:
                    amt = int(argument[:-1])
                    unit = argument[-1]
                    amount = amt * amount_dict[unit.lower()]
                except ValueError:
                    try:
                        amt = float(argument[:-1])
                        unit = argument[-1]
                        amount = int(amt * float(amount_dict[unit.lower()]))
                    except (KeyError, ValueError) as keve:
                        raise AmountConversionFailure(
                            f'Failed to convert "{argument}" into a proper amount.'
                        ) from keve
                except KeyError as ke:
                    raise AmountConversionFailure(
                        f'Failed to convert "{argument}" into a proper amount.'
                    ) from ke
        if amount >= 999999999999999:
            raise AmountConversionFailure(
                "That is an absurd amount to don't you think? "
                "If you are attempting to break me, Nice Try."
            )
        if amount < 0:
            raise AmountConversionFailure(
                "Adding, removing or setting of negative amount is not allowed."
            )
        return amount
