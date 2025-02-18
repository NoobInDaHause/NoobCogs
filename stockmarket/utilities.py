import noobutils as nu
import random

from redbot.core import bank


def float_generator(start: float, stop: float, step: float):
    value = start
    while value < stop:
        yield round(value, 10)
        value += step


def get_percent_number() -> float:
    return random.choice(list(float_generator(0.01, 0.20, 0.01))) * random.choice(
        [-1, 1]
    )


def is_economy_global():
    async def pred(context: nu.commands.Context):
        if not await bank.is_global():
            if context.interaction:
                if context.interaction.response.is_done():
                    fu = context.interaction.followup.send
                else:
                    fu = context.interaction.response.send_message
                await fu(
                    content="Economy is not set to Global! Please report this to the bot owner!",
                    ephemeral=True,
                )
            return False

        return True

    return nu.commands.check(pred)
