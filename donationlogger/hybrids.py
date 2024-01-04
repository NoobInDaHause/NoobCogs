import asyncio
import discord
import noobutils as nu
import random

from redbot.core.bot import commands, Red
from redbot.core.utils import chat_formatting as cf, mod

from typing import Literal, TYPE_CHECKING, Union

from .utilities import (
    check_if_is_a_dono_manager_or_higher,
    check_if_setup_done,
    has_dono_permissions,
)
from .views import DonationLoggerSetupView, TotalDonoView

if TYPE_CHECKING:
    from . import DonationLogger


class HYBRIDS:
    @staticmethod
    async def hybrid_send(
        obj: Union[commands.Context, discord.Interaction[Red]], **payload
    ) -> discord.Message:
        if isinstance(obj, commands.Context):
            return await obj.send(
                content=payload.get("content"),
                embed=payload.get("embed"),
                allowed_mentions=payload.get("allowed_mentions"),
            )
        elif obj.response.is_done():
            return await obj.followup.send(
                content=payload.get("content"),
                embed=payload.get("embed"),
                allowed_mentions=payload.get("allowed_mentions"),
                ephemeral=payload.get("ephemeral"),
            )
        else:
            return await obj.response.send_message(
                content=payload.get("content"),
                embed=payload.get("embed"),
                allowed_mentions=payload.get("allowed_mentions"),
                ephemeral=payload.get("ephemeral"),
            )

    @classmethod
    async def hybrid_setup(
        cls,
        cog: "DonationLogger",
        obj: Union[commands.Context, discord.Interaction[Red]],
    ):
        if isinstance(obj, discord.Interaction):
            if not obj.channel.permissions_for(obj.guild.me).embed_links:
                return await cls.hybrid_send(
                    obj,
                    content='I require the "Embed Links" permission to run this command.',
                    ephemeral=True,
                )
            if not has_dono_permissions(
                obj, manage_guild=True
            ) and not await mod.is_mod_or_superior(obj.client, obj.user):
                return await cls.hybrid_send(
                    obj,
                    content="You need to be a guild admin or a guild manager + to run this command.",
                    ephemeral=True,
                )
        if await cog.config.guild(obj.guild).setup():
            content = (
                "It appears this guild is already set up, "
                "you can run this command again when you reset this guild."
            )
            return await cls.hybrid_send(obj, content=content, ephemeral=True)
        conf = (
            "You are about to set up DonationLogger system in your server.\n"
            "Click Yes to continue or No to abort."
        )
        act = "Alright sending set up interactions, please wait..."
        view = nu.NoobConfirmation()
        await view.start(obj, act, content=conf)
        await view.wait()
        await asyncio.sleep(3)
        if view.value:
            await view.message.delete()
            if obj.guild.id in cog.setupcache:
                return await cls.hybrid_send(
                    obj, content="Only one setup interaction per guild."
                )
            cog.setupcache.append(obj.guild.id)
            ctx = (
                obj
                if isinstance(obj, commands.Context)
                else await obj.client.get_context(obj)
            )
            await DonationLoggerSetupView(cog).start(ctx)

    @classmethod
    async def hybrid_resetmember(
        cls,
        cog: "DonationLogger",
        obj: Union[commands.Context, discord.Interaction[Red]],
        member: discord.Member,
        bank_name: str = None,
    ):
        if isinstance(obj, discord.Interaction):
            if not obj.channel.permissions_for(obj.guild.me).embed_links:
                return await cls.hybrid_send(
                    obj,
                    content='I require the "Embed Links" permission to run this command.',
                    ephemeral=True,
                )
            if not check_if_setup_done(obj):
                return await cls.hybrid_send(
                    obj,
                    content="DonationLogger has not been setup in this guild yet.",
                    ephemeral=True,
                )
            if not await check_if_is_a_dono_manager_or_higher(obj):
                return await cls.hybrid_send(
                    obj,
                    content="You need to be a donationlogger manager or higher to run this command.",
                    ephemeral=True,
                )
        if not bank_name:
            act = f"Successfully cleared all bank donations from **{member.name}**."
            conf = f"Are you sure you want to erase all bank donations from **{member.name}**?"
            view = nu.NoobConfirmation()
            await view.start(obj, act, content=conf)
            await view.wait()
            if view.value:
                async with cog.config.guild(obj.guild).banks() as banks:
                    for bank in banks.values():
                        bank["donators"].setdefault(str(member.id), 0)
                        bank["donators"][str(member.id)] = 0
            return
        act = f"Successfully cleared **{bank_name.title()}** donations from **{member.name}**."
        conf = f"Are you sure you want to clear **{bank_name.title()}** donations from **{member.name}**"
        view = nu.NoobConfirmation()
        await view.start(obj, act, content=conf)
        await view.wait()
        if view.value:
            async with cog.config.guild(obj.guild).banks() as banks:
                donations = banks[bank_name.lower()]["donators"].setdefault(
                    str(member.id), 0
                )
                if donations == 0:
                    return await cls.hybrid_send(
                        obj, content="This member has 0 donation balance for this bank."
                    )
                banks[bank_name.lower()]["donators"][str(member.id)] = 0

    @classmethod
    async def hybrid_balance(
        cls,
        cog: "DonationLogger",
        obj: Union[commands.Context, discord.Interaction[Red]],
        member: discord.Member,
        bank_name: str = None,
    ):
        if (
            isinstance(obj, discord.Interaction)
            and not obj.channel.permissions_for(obj.guild.me).embed_links
        ):
            return await cls.hybrid_send(
                obj,
                content='I require the "Embed Links" permission to run this command.',
                ephemeral=True,
            )
        if bank_name:
            async with cog.config.guild(obj.guild).banks() as banks:
                bank = banks[bank_name.lower()]
                donations = bank["donators"].setdefault(str(member.id), 0)
                if bank["hidden"]:
                    return await cls.hybrid_send(obj, content="This bank is hidden")
                embed = discord.Embed(
                    title=f"{member.name} ({member.id})",
                    description=(
                        f"Bank: {bank_name.title()}\n"
                        f"Total amount donated: {bank['emoji']} {cf.humanize_number(donations)}"
                    ),
                    timestamp=discord.utils.utcnow(),
                    colour=member.colour,
                )
                embed.set_thumbnail(url=nu.is_have_avatar(member))
                embed.set_footer(
                    text=f"{obj.guild.name} admires your donations!",
                    icon_url=nu.is_have_avatar(obj.guild),
                )
                return await cls.hybrid_send(obj, embed=embed)
        embed = await cog.get_all_bank_member_dono(obj.guild, member)
        await cls.hybrid_send(obj, embed=embed)

    @classmethod
    async def hybrid_donationcheck(
        cls,
        cog: "DonationLogger",
        obj: Union[commands.Context, discord.Interaction[Red]],
        bank_name: str,
        mla: Literal["more", "less", "all"],
        amount: int = None,
    ):
        if (
            isinstance(obj, discord.Interaction)
            and not obj.channel.permissions_for(obj.guild.me).embed_links
        ):
            return await cls.hybrid_send(
                obj,
                content='I require the "Embed Links" permission to run this command.',
                ephemeral=True,
            )
        if isinstance(obj, commands.Context):
            ctx: commands.Context = obj
        else:
            ctx: commands.Context = await obj.client.get_context(obj)
        if mla == "all":
            embeds = await cog.get_dc_from_bank(ctx, bank_name)
            if not embeds:
                return await cls.hybrid_send(obj, content="This bank is hidden.")
            await nu.NoobPaginator(embeds).start(obj)
            return

        if not amount:
            return await ctx.send_help()

        banks_config = await cog.config.guild(obj.guild).banks()
        bank_data = banks_config.get(bank_name.lower(), {})
        if bank_data.get("hidden"):
            return await cls.hybrid_send(obj, content="This bank is hidden.")

        donators = bank_data.get("donators", {})
        filtered_donators = {
            k: v
            for k, v in donators.items()
            if (mla == "more" and v >= amount) or (mla == "less" and v < amount)
        }

        sorted_donators = sorted(
            filtered_donators.items(), key=lambda u: u[1], reverse=(mla == "more")
        )

        output_list = []
        for index, (donator_id, donation_amount) in enumerate(sorted_donators, 1):
            member = obj.guild.get_member(int(donator_id))
            mention = (
                f"{member.mention} (`{member.id}`)"
                if member
                else f"Member not found in server. (`{donator_id}`)"
            )
            e = (
                "➡️ "
                if member and member.id == (getattr(obj, "author", obj.user)).id
                else ""
            )
            output_list.append(
                f"{e}{index}. {mention}: **{cf.humanize_number(donation_amount)}**"
            )

        output_text = "\n".join(
            output_list
            or [f"No one has donated {mla} than **{cf.humanize_number(amount)}** yet."]
        )

        paginated_output = await nu.pagify_this(
            output_text,
            "\n",
            "Page ({index}/{pages})",
            embed_title=f"All members who have donated {mla} than {cf.humanize_number(amount)} "
            f"for [{bank_name.title()}]",
            embed_colour=await ctx.embed_colour(),
        )

        await nu.NoobPaginator(paginated_output).start(obj)

    @classmethod
    async def hybrid_leaderboard(
        cls,
        cog: "DonationLogger",
        obj: Union[commands.Context, discord.Interaction[Red]],
        bank_name: str,
        top: int,
    ):
        if (
            isinstance(obj, discord.Interaction)
            and not obj.channel.permissions_for(obj.guild.me).embed_links
        ):
            return await cls.hybrid_send(
                obj,
                content='I require the "Embed Links" permission to run this command.',
                ephemeral=True,
            )
        banks = await cog.config.guild(obj.guild).banks()
        if banks[bank_name.lower()]["hidden"]:
            return await cls.hybrid_send(obj, content="This bank is hidden.")
        donors = banks[bank_name.lower()]["donators"]
        emoji = banks[bank_name.lower()]["emoji"]
        sorted_donors = dict(sorted(donors.items(), key=lambda m: m[1], reverse=True))
        embed = discord.Embed(
            title=f"Top {top} donators for [{bank_name.title()}]",
            colour=random.randint(0, 0xFFFFFF),
            timestamp=discord.utils.utcnow(),
        )
        embed.set_footer(text=obj.guild.name)
        embed.set_thumbnail(url=nu.is_have_avatar(obj.guild))
        if not sorted_donors:
            embed.description = "It seems no one has donated from this bank yet."
        for index, (k, v) in enumerate(sorted_donors.items(), 1):
            if index > top:
                break
            member = obj.guild.get_member(int(k))
            mem = f"{member.name}" if member else f"[Member not found in guild] ({k})"
            embed.add_field(
                name=f"{index}. {mem}",
                value=f"{emoji} {cf.humanize_number(v)}",
                inline=False,
            )
        await cls.hybrid_send(obj, embed=embed)

    @classmethod
    async def hybrid_add(
        cls,
        cog: "DonationLogger",
        obj: Union[commands.Context, discord.Interaction[Red]],
        bank_name: str,
        amount: int,
        member: discord.Member,
    ):
        if isinstance(obj, discord.Interaction):
            if not obj.channel.permissions_for(obj.guild.me).embed_links:
                return await cls.hybrid_send(
                    obj,
                    content='I require the "Embed Links" permission to run this command.',
                    ephemeral=True,
                )
            if not check_if_setup_done(obj):
                return await cls.hybrid_send(
                    obj,
                    content="DonationLogger has not been setup in this guild yet.",
                    ephemeral=True,
                )
            if not await check_if_is_a_dono_manager_or_higher(obj):
                return await cls.hybrid_send(
                    obj,
                    content="You need to be a donationlogger manager or higher to run this command.",
                    ephemeral=True,
                )
        if isinstance(obj, commands.Context):
            ctx: commands.Context = obj
        else:
            ctx: commands.Context = await obj.client.get_context(obj)
        async with cog.config.guild(obj.guild).banks() as banks:
            bank = banks[bank_name.lower()]
            emoji = bank["emoji"]
            if bank["hidden"]:
                return await cls.hybrid_send(obj, content="This bank is hidden.")
            bank["donators"].setdefault(str(member.id), 0)
            bank["donators"][str(member.id)] += amount
            updated = bank["donators"][str(member.id)]
            previous = updated - amount
            donated = cf.humanize_number(amount)
            total = cf.humanize_number(updated)
            roles = await cog.update_dono_roles(
                ctx, "add", updated, member, bank["roles"]
            )
            humanized_roles = f"{cf.humanize_list([role.mention for role in roles])}"
            rep = (
                f"Successfully added {emoji} **{donated}** to "
                f"**{member.name}**'s **__{bank_name.title()}__** donation balance.\n"
                f"Their total donation balance is now **{emoji} {total}** on **__{bank_name.title()}__**."
            )
            await TotalDonoView(cog).start(ctx, rep, member)
            await cog.send_to_log_channel(
                ctx,
                "add",
                bank_name,
                emoji,
                amount,
                previous,
                updated,
                member,
                humanized_roles,
            )

    @classmethod
    async def hybrid_remove(
        cls,
        cog: "DonationLogger",
        obj: Union[commands.Context, discord.Interaction[Red]],
        bank_name: str,
        amount: int,
        member: discord.Member,
    ):
        if isinstance(obj, discord.Interaction):
            if not obj.channel.permissions_for(obj.guild.me).embed_links:
                return await cls.hybrid_send(
                    obj,
                    content='I require the "Embed Links" permission to run this command.',
                    ephemeral=True,
                )
            if not check_if_setup_done(obj):
                return await cls.hybrid_send(
                    obj,
                    content="DonationLogger has not been setup in this guild yet.",
                    ephemeral=True,
                )
            if not await check_if_is_a_dono_manager_or_higher(obj):
                return await cls.hybrid_send(
                    obj,
                    content="You need to be a donationlogger manager or higher to run this command.",
                    ephemeral=True,
                )
        if isinstance(obj, commands.Context):
            ctx: commands.Context = obj
        else:
            ctx: commands.Context = await obj.client.get_context(obj)
        async with cog.config.guild(obj.guild).banks() as banks:
            bank = banks[bank_name.lower()]
            donators = bank["donators"]
            emoji = bank["emoji"]
            member_id = str(member.id)
            if bank["hidden"]:
                return await cls.hybrid_send(obj, content="This bank is hidden.")
            donators.setdefault(member_id, 0)
            if donators[member_id] == 0:
                return await cls.hybrid_send(
                    obj, content="This member has 0 donation balance for this bank."
                )
            donators[member_id] -= amount
            updated1 = donators[member_id]
            if updated1 < 0:
                donators[member_id] = 0
            updated2 = donators[member_id]
            previous = updated1 + amount
            donated = cf.humanize_number(amount)
            total = cf.humanize_number(updated2)
            roles = await cog.update_dono_roles(
                ctx, "remove", updated2, member, bank["roles"]
            )
            humanized_roles = f"{cf.humanize_list([role.mention for role in roles])}"
            rep = (
                f"Successfully removed {emoji} **{donated}** from "
                f"**{member.name}**'s **__{bank_name.title()}__** donation balance.\n"
                "Their total donation balance is now "
                f"**{emoji} {total}** on **__{bank_name.title()}__**."
            )
            await TotalDonoView(cog).start(ctx, rep, member)
            await cog.send_to_log_channel(
                ctx,
                "remove",
                bank_name,
                emoji,
                amount,
                previous,
                updated2,
                member,
                humanized_roles,
            )

    @classmethod
    async def hybrid_set(
        cls,
        cog: "DonationLogger",
        obj: Union[commands.Context, discord.Interaction[Red]],
        bank_name: str,
        amount: int,
        member: discord.Member,
    ):
        if isinstance(obj, discord.Interaction):
            if not obj.channel.permissions_for(obj.guild.me).embed_links:
                return await cls.hybrid_send(
                    obj,
                    content='I require the "Embed Links" permission to run this command.',
                    ephemeral=True,
                )
            if not check_if_setup_done(obj):
                return await cls.hybrid_send(
                    obj,
                    content="DonationLogger has not been setup in this guild yet.",
                    ephemeral=True,
                )
            if not await check_if_is_a_dono_manager_or_higher(obj):
                return await cls.hybrid_send(
                    obj,
                    content="You need to be a donationlogger manager or higher to run this command.",
                    ephemeral=True,
                )
        if isinstance(obj, commands.Context):
            ctx: commands.Context = obj
        else:
            ctx: commands.Context = await obj.client.get_context(obj)
        async with cog.config.guild(obj.guild).banks() as banks:
            bank = banks[bank_name.lower()]
            donators = bank["donators"]
            emoji = bank["emoji"]
            if bank["hidden"]:
                return await cls.hybrid_send(obj, content="This bank is hidden.")
            donators.setdefault(str(member.id), 0)
            previous = donators[str(member.id)]
            donators[str(member.id)] = amount
            aroles = await cog.update_dono_roles(
                ctx, "add", amount, member, bank["roles"]
            )
            rrole = await cog.update_dono_roles(
                ctx, "remove", amount, member, bank["roles"]
            )
            roles = aroles + rrole
            humanized_roles = f"{cf.humanize_list([role.mention for role in roles])}"
            rep = (
                f"Successfully set {emoji} **{cf.humanize_number(amount)}** as "
                f"**{member.name}**'s **__{bank_name.title()}__** donation balance."
            )
            await TotalDonoView(cog).start(ctx, rep, member)
            await cog.send_to_log_channel(
                ctx,
                "set",
                bank_name,
                emoji,
                amount,
                previous,
                amount,
                member,
                humanized_roles,
            )
