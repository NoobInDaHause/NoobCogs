import discord

from redbot.core.bot import commands, Red
from redbot.core.utils import mod

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from . import DonationLogger


async def check_if_setup_done(
    obj: Union[commands.Context, discord.Interaction[Red]]
) -> bool:
    cog: "DonationLogger" = (
        obj.bot.get_cog("DonationLogger")
        if isinstance(obj, commands.Context)
        else obj.client.get_cog("DonationLogger")
    )
    return await cog.config.guild(obj.guild).setup() if obj.guild else False


def is_setup_done():
    return commands.check(check_if_setup_done)


async def check_if_is_a_dono_manager_or_higher(
    obj: Union[commands.Context, discord.Interaction[Red]]
) -> bool:
    if not obj.guild:
        return False

    if isinstance(obj, commands.Context):
        author = obj.author
        bot = obj.bot
    else:
        author = obj.user
        bot = obj.client
    cog: "DonationLogger" = bot.get_cog("DonationLogger")
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
    obj: Union[commands.Context, discord.Interaction[Red]], **perms
) -> bool:
    permissions = (
        obj.author.guild_permissions
        if isinstance(obj, commands.Context)
        else obj.user.guild_permissions
    )

    missing = [
        perm for perm, value in perms.items() if getattr(permissions, perm) != value
    ]

    return not missing
