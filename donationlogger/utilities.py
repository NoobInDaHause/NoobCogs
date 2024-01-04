import discord
import noobutils as nu

from redbot.core.bot import commands, Red
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


async def check_if_setup_done(
    obj: Union[commands.Context, discord.Interaction[Red]]
) -> bool:
    if isinstance(obj, commands.Context):
        cog: "DonationLogger" = obj.bot.get_cog("DonationLogger")
    else:
        cog: "DonationLogger" = obj.client.get_cog("DonationLogger")
    return await cog.config.guild(obj.guild).setup() if obj.guild else False


def is_setup_done():
    return commands.check(check_if_setup_done)


async def check_if_is_a_dono_manager_or_higher(
    obj: Union[commands.Context, discord.Interaction[Red]]
) -> bool:
    if not obj.guild:
        return False

    if isinstance(obj, commands.Context):
        cog: "DonationLogger" = obj.bot.get_cog("DonationLogger")
        author = obj.author
        bot = obj.bot
    else:
        cog: "DonationLogger" = obj.client.get_cog("DonationLogger")
        author = obj.user
        bot = obj.client
    managers = await cog.config.guild(obj.guild).managers()
    return (
        await bot.is_owner(author)
        or author.guild_permissions.manage_guild
        or await mod.is_mod_or_superior(bot, author)
        or any(role_id in author._roles for role_id in managers)
        or False
    )


def is_a_dono_manager_or_higher():
    return commands.check(check_if_is_a_dono_manager_or_higher)


def has_dono_permissions(
    obj: Union[commands.Context, discord.Interaction[Red]], **perms: bool
) -> bool:
    if isinstance(obj, commands.Context):
        permissions = obj.author.guild_permissions
    else:
        permissions = obj.user.guild_permissions

    missing = [
        perm for perm, value in perms.items() if getattr(permissions, perm) != value
    ]

    return not missing
