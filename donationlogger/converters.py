import discord
import re
from redbot.core import commands

from redbot.core.bot import commands

from noobutils import NoobEmojiConverter
from rapidfuzz import process
from unidecode import unidecode

from .exceptions import AmountConversionFailure, FuzzyRoleConversionFailure


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
                        if re.search("<@(.*)>", argument):
                            raise AmountConversionFailure(
                                "The amount comes first then the member."
                            ) from keve
                        raise AmountConversionFailure(
                            f'Failed to convert "{argument}" into a proper amount.'
                        ) from keve
                except KeyError as ke:
                    if re.search("<@(.*)>", argument):
                        raise AmountConversionFailure(
                            "The amount comes first then the member."
                        ) from ke
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


# https://github.com/phenom4n4n/phen-cogs/blob/327fc78c66814ac01f644c6b775dc4d6db6e1e5f/roleutils/converters.py#L36
# original converter from https://github.com/TrustyJAID/Trusty-cogs/blob/master/serverstats/converters.py#L19
class FuzzyRole(commands.RoleConverter):
    """
    This will accept role ID's, mentions, and perform a fuzzy search for
    roles within the guild and return a list of role objects
    matching partial names
    Guidance code on how to do this from:
    https://github.com/Rapptz/discord.py/blob/rewrite/discord/ext/commands/converter.py#L85
    https://github.com/Cog-Creators/Red-DiscordBot/blob/V3/develop/redbot/cogs/mod/mod.py#L24
    """

    def __init__(self, response: bool = True):
        self.response = response
        super().__init__()

    async def convert(self, ctx: commands.Context, argument: str) -> discord.Role:
        try:
            basic_role = await super().convert(ctx, argument)
        except commands.BadArgument:
            pass
        else:
            return basic_role
        result = [
            (r[2], r[1])
            for r in process.extract(
                argument,
                {r: unidecode(r.name) for r in ctx.guild.roles},
                limit=None,
                score_cutoff=75,
            )
        ]
        if not result:
            raise FuzzyRoleConversionFailure(
                f'Role "{argument}" not found.' if self.response else None
            )

        sorted_result = sorted(result, key=lambda r: r[1], reverse=True)
        return sorted_result[0][0]


class DLEmojiConverter(NoobEmojiConverter):
    async def convert(self, ctx, argument):
        argument = argument.strip()
        return argument if argument == "⏣" else await super().convert(ctx, argument)
