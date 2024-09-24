import discord
import noobutils as nu

from redbot.core.utils import mod

from typing import Dict, List, TYPE_CHECKING, Union

from .converters import AmountConverter, DLEmojiConverter

if TYPE_CHECKING:
    from . import DonationLogger


async def verify_channel(
    context: nu.commands.Context, argument: str
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
    context: nu.commands.Context, emoji: str
) -> Union[discord.Emoji, str]:
    emoji = emoji.strip()
    try:
        return await DLEmojiConverter().convert(context, emoji)
    except Exception:
        return None


async def verify_roles(
    context: nu.commands.Context, raw_roles: List[str]
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
    context: nu.commands.Context, aroles: List[str]
) -> Dict[str, List[discord.Role]]:
    par = {}
    for araw in aroles:
        ar = araw.strip().split(":")
        if len(ar) >= 2:
            try:
                amount = await AmountConverter().convert(context, ar[0].strip())
                ar.pop(0)
                if len(ar) > 3:
                    raise nu.commands.BadArgument(
                        "You can not assign more than 3 roles per amount."
                    )
                roles = await verify_roles(context, ar)
                if amount and roles and (str(amount) not in par):
                    par[str(amount)] = roles
            except nu.commands.BadArgument:
                continue
    return dict(sorted(par.items(), key=lambda b: int(b[0])))


async def inter_send(
    interaction: discord.Interaction[nu.Red], **kwargs
) -> discord.Message:
    if interaction.response.is_done():
        return await interaction.followup.send(**kwargs)
    await interaction.response.send_message(**kwargs)
    return await interaction.original_response()


async def manager_or_higher(
    bot: nu.Red, author: discord.Member, manager_list: list = None
) -> bool:
    if not manager_list:
        manager_list = []

    return (
        author.guild_permissions.manage_guild
        or await mod.is_mod_or_superior(bot, author)
        or any((role_id in author._roles for role_id in manager_list))
    )


def donationlogger_check(
    setup_check: bool = False,
    owner_only: bool = False,
    check_if_setup_done: bool = False,
    check_if_manager_or_higher: bool = False,
):
    async def check_predicate(ctx: nu.commands.Context) -> bool:
        is_interaction = bool(ctx.interaction)

        if not ctx.guild:
            if is_interaction:
                await inter_send(
                    ctx.interaction,
                    content="This command can only be run in guilds.",
                    ephemeral=True,
                )
            return False

        author = ctx.interaction.user if is_interaction else ctx.author
        is_owner = await ctx.bot.is_owner(author)
        cog: "DonationLogger" = ctx.bot.get_cog("DonationLogger")

        if setup_check and not (
            author.guild_permissions.manage_guild
            or await mod.is_admin_or_superior(ctx.bot, author)
        ):
            if is_interaction:
                await inter_send(
                    ctx.interaction,
                    content='You need to be an admin or have the "Manage Guild" permission to run this '
                    "command.",
                    ephemeral=True,
                )
            return False

        if owner_only and not is_owner:
            if is_interaction:
                await inter_send(
                    ctx.interaction,
                    content="This command is for bot owners only.",
                    ephemeral=True,
                )
            return False

        if check_if_setup_done and not await cog.config.guild(ctx.guild).setup():
            if is_interaction:
                await inter_send(
                    ctx.interaction,
                    content="DonationLogger has not been setup in this guild yet.",
                    ephemeral=True,
                )
            return False

        if check_if_manager_or_higher:
            managers = await cog.config.guild(ctx.guild).managers()
            if not await manager_or_higher(ctx.bot, author, managers):
                if is_interaction:
                    await inter_send(
                        ctx.interaction,
                        content="You must have the set donation manager role or higher to run this command.",
                        ephemeral=True,
                    )
                return False

        return True

    return nu.commands.check(check_predicate)
