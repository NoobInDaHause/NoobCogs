from redbot.core.bot import commands

from .exceptions import TimeConversionFailure


class TimeConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str) -> int:
        argument = argument.strip()
        try:
            time = int(argument[:-1])
        except ValueError as e:
            raise TimeConversionFailure(f'"{argument}" is not a valid time.') from e
        unit = argument[-1]
        if unit.lower() in ["s", "m", "h", "d"]:
            time_multiplier = {"s": 1, "m": 60, "h": 3600, "d": 86400}
            return time * time_multiplier[unit]
        raise TimeConversionFailure(f'"{argument}" is not a valid time.')
