from redbot.core.bot import commands
from redbot.core.utils import chat_formatting as cf

from typing import Self


def format_amount(argument: str):
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
        return None if amount > 999999999999999 or amount < 1 else amount
    except (ValueError, KeyError):
        return None


class GiveawayConverter(commands.Converter):
    def __init__(self, **payload) -> None:
        super().__init__()
        self.currency_type: str = payload.get("currency_type")
        self.duration: str = payload.get("duration")
        self.winners: str = payload.get("winners")
        self.requirements: str = payload.get("requirements")
        self.prize: str = payload.get("prize")
        self.message: str = payload.get("message")

    @classmethod
    async def convert(cls, ctx: commands.Context, argument: str) -> Self:
        arg = argument.strip().split("|")
        if len(arg) > 6:
            raise commands.BadArgument(
                "It appears you added an extra vertical bar `|`, please try again."
            )
        bad_arg = "All arguments are required, put `None` in [requirements] and/or [message] if none."
        if len(arg) < 6:
            raise commands.BadArgument(bad_arg)
        if not all(arg):
            raise commands.BadArgument(bad_arg)
        giveaway_dict = {
            "winners": None,
            "requirements": arg[3].strip(),
            "prize": cf.humanize_number(amt)
            if (amt := format_amount(arg[4].strip()))
            else arg[4].strip(),
            "message": arg[5].strip(),
            "currency_type": arg[0].strip(),
            "duration": cf.humanize_timedelta(timedelta=duration_td)
            if (duration_td := commands.parse_timedelta(arg[1].strip()))
            else arg[1],
        }
        try:
            giveaway_dict["winners"] = int(arg[2].replace("w", "").strip())
        except ValueError as e:
            raise commands.BadArgument("Winners must be a number.") from e
        return cls(**giveaway_dict)


class EventConverter(commands.Converter):
    def __init__(self, **payload) -> None:
        super().__init__()
        self.currency_type: str = payload.get("currency_type")
        self.event_name: str = payload.get("event_name")
        self.requirements: str = payload.get("requirements")
        self.prize: str = payload.get("prize")
        self.message: str = payload.get("message")

    @classmethod
    async def convert(cls, ctx: commands.Context, argument: str) -> Self:
        arg = argument.strip().split("|")
        if len(arg) > 5:
            raise commands.BadArgument(
                "It appears you added an extra vertical bar `|`, please try again."
            )
        bad_arg = "All arguments are required, put `None` in [requirements] and/or [message] if none."
        if len(arg) < 5:
            raise commands.BadArgument(bad_arg)
        if not all(arg):
            raise commands.BadArgument(bad_arg)
        event_dict = {
            "message": arg[4].strip(),
            "currency_type": arg[0].strip(),
            "event_name": arg[1].strip(),
            "requirements": arg[2].strip(),
            "prize": cf.humanize_number(amt)
            if (amt := format_amount(arg[3].strip()))
            else arg[3],
        }
        return cls(**event_dict)


class HeistConverter(commands.Converter):
    def __init__(self, **payload) -> None:
        super().__init__()
        self.currency_type: str = payload.get("currency_type")
        self.requirements: str = payload.get("requirements")
        self.amount: str = payload.get("amount")
        self.message: str = payload.get("message")

    @classmethod
    async def convert(cls, ctx: commands.Context, argument: str) -> Self:
        arg = argument.strip().split("|")
        if len(arg) > 4:
            raise commands.BadArgument(
                "It appears you added an extra vertical bar `|`, please try again."
            )
        bad_arg = "All arguments are required, put `None` in [requirements] and/or [message] if none."
        if len(arg) < 4:
            raise commands.BadArgument(bad_arg)
        if not all(arg):
            raise commands.BadArgument(bad_arg)
        heist_dict = {
            "message": arg[3].strip(),
            "currency_type": arg[0].strip(),
            "requirements": arg[1].strip(),
            "amount": cf.humanize_number(amt)
            if (amt := format_amount(arg[2].strip()))
            else arg[2],
        }
        return cls(**heist_dict)
