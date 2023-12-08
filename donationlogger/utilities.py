import discord
import noobutils as nu

from redbot.core.bot import commands
from redbot.core.utils import mod

from typing import Dict, List, Union, TYPE_CHECKING

from .converters import AmountConverter, DLEmojiConverter
from .exceptions import (
    AmountConversionFailure,
    MoreThanThreeRoles,
)

if TYPE_CHECKING:
    from . import DonationLogger


async def verify_bank(context: commands.Context, bank_name: str) -> bool:
    cog: "DonationLogger" = context.bot.get_cog("DonationLogger")
    banks = await cog.config.guild(context.guild).banks()
    try:
        banks[bank_name.lower()]
        return True
    except KeyError:
        return False


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
            role = await nu.NoobFuzzyRole().convert(context, r)
            if role not in roles:
                roles.append(role)
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
                amount = await AmountConverter().convert(context, ar[0].strip())
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


def is_setup_done():
    async def check_if_setup_done(context: commands.Context):
        cog: "DonationLogger" = context.bot.get_cog("DonationLogger")
        return await cog.config.guild(context.guild).setup() if context.guild else False

    return commands.check(check_if_setup_done)


def is_a_dono_manager_or_higher():
    async def check_if_is_a_dono_manager_or_higher(context: commands.Context):
        if not context.guild:
            return False

        cog: "DonationLogger" = context.bot.get_cog("DonationLogger")
        managers = await cog.config.guild(context.guild).managers()
        return (
            await context.bot.is_owner(context.author)
            or context.author.guild_permissions.manage_guild
            or await mod.is_mod_or_superior(context.bot, context.author)
            or any(role_id in context.author._roles for role_id in managers)
            or False
        )

    return commands.check(check_if_is_a_dono_manager_or_higher)
