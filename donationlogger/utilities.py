import discord
import noobutils as nu

from redbot.core.bot import commands

from typing import Dict, List, Union

from .converters import AmountConverter, DLEmojiConverter
from .exceptions import (
    AmountConversionFailure,
    MoreThanThreeRoles,
)


async def verify_channel(
    context: commands.Context, argument: str
) -> discord.TextChannel:
    argument = argument.strip()
    try:
        return context.guild.get_channel(int(argument))
    except Exception:
        try:
            return context.guild.get_channel(
                int(argument.replace("<", "").replace(">", "").replace("#", ""))
            )
        except Exception:
            return None


async def verify_emoji(
    context: commands.Context, emoji: str
) -> Union[discord.Emoji, str]:
    emoji = emoji.strip()
    try:
        return await DLEmojiConverter().convert(context, emoji)
    except Exception:
        return None


async def verify_roles(
    context: commands.Context, raw_roles: List[str]
) -> List[discord.Role]:
    roles = []
    for raw in raw_roles:
        try:
            r = raw.strip()
            role = await nu.NoobFuzzyRole.convert(context, r)
            if role._role not in roles:
                roles.append(role._role)
        except Exception:
            continue
    return roles


async def verify_amount_roles(
    context: commands.Context, aroles: List[str]
) -> Dict[str, List[discord.Role]]:
    par = {}
    for araw in aroles:
        ar = araw.strip().split(":")
        if len(ar) >= 2:
            try:
                amount = await AmountConverter.convert(context, ar[0].strip())
                ar.pop(0)
                if len(ar) > 3:
                    raise MoreThanThreeRoles(
                        "You can not assign more than 3 roles per amount."
                    )
                roles = await verify_roles(context, ar)
                if amount and roles and (str(amount) not in par):
                    par[str(amount)] = roles
            except AmountConversionFailure:
                continue
    return dict(sorted(par.items(), key=lambda b: int(b[0])))
