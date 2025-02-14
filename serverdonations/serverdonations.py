import contextlib
import discord
import noobutils as nu
import TagScriptEngine as tse

from redbot.core.bot import app_commands, commands, Red

from typing import List, Literal, Optional, Tuple

from .converters import GiveawayConverter, EventConverter, HeistConverter, format_amount
from .views import DonationsView


GMSG = """
{role}
{embed(title):Someone would like to donate for a giveaway!}
{embed(colour):{donor(colour)}}
{embed(thumbnail):{donor(avatar)}}
{embed(footer):{guild(name)}|{guild(icon)}}
{embed(description):**Donor:** {donor(mention)}
**Currency Type:** {currency_type}
**Duration:** {duration}
**Winner(s):** {winners}
**Requirements:** {requirements}
**Prize:** {prize}
**Message:** {message}}
"""

EMSG = """
{role}
{embed(title):Someone would like to donate for an event!}
{embed(colour):{donor(colour)}}
{embed(thumbnail):{donor(avatar)}}
{embed(footer):{guild(name)}|{guild(icon)}}
{embed(description):**Donor:** {donor(mention)}
**Currency Type:** {currency_type}
**Event Name:** {eveny_name}
**Requirements:** {requirements}
**Prize:** {prize}
**Message:** {message}}
"""

HMSG = """
{role}
{embed(title):Someone would like to donate for a heist!}
{embed(colour):{donor(colour)}}
{embed(thumbnail):{donor(avatar)}}
{embed(footer):{guild(name)}|{guild(icon)}}
{embed(description):**Donor:** {donor(mention)}
**Currency Type:** {currency_type}
**Amount:** {amount}
**Requirements:** {requirements}
**Message:** {message}}
"""
DEFAULT_GUILD = {
    "auto_delete": False,
    "dl_support": True,
    "channels": {"gchan": None, "echan": None, "hchan": None},
    "managers": {"gmans": [], "emans": [], "hmans": []},
    "messages": {"gmsg": GMSG, "emsg": EMSG, "hmsg": HMSG},
}


class ServerDonations(nu.Cog):
    """
    Donate bot currencies or any other currencies to servers.

    Donate Nitro, Dank Memer Coins, Bro Coins, Owo Cash, Karuta Tickets and many more.
    """

    def __init__(self, bot: Red, *args, **kwargs):
        super().__init__(
            bot=bot,
            cog_name=self.__class__.__name__,
            version="3.3.2",
            authors=["NoobInDaHause"],
            use_config=True,
            force_registration=True,
            *args,
            **kwargs,
        )
        self.config.register_guild(**DEFAULT_GUILD)

    async def red_delete_data_for_user(
        self,
        *,
        requester: Literal["discord_deleted_user", "owner", "user", "user_strict"],
        user_id: int,
    ) -> None:
        """
        This cog does not store any end user data whatsoever.
        """
        return await super().red_delete_data_for_user(
            requester=requester, user_id=user_id
        )

    async def send_donation(
        self, _type: str, context: commands.Context, **payload
    ) -> None:
        tagengine = tse.AsyncInterpreter(
            blocks=[
                tse.EmbedBlock(),
                tse.LooseVariableGetterBlock(),
                tse.StrictVariableGetterBlock(),
                tse.IfBlock(),
                tse.RandomBlock(),
                tse.FiftyFiftyBlock(),
                tse.AllBlock(),
                tse.AnyBlock(),
                tse.ReplaceBlock(),
                tse.AssignmentBlock(),
                tse.PythonBlock(),
            ]
        )

        def get_manager_roles(
            manager_type: str,
        ) -> Tuple[Optional[discord.TextChannel], List[discord.Role], str, str]:
            channel = context.guild.get_channel(channels[f"{manager_type[0]}chan"])
            message = messages[f"{manager_type[0]}msg"]
            roles = [
                context.guild.get_role(r) for r in managers[f"{manager_type[0]}mans"]
            ]
            role_mention = (
                nu.cf.humanize_list([ro.mention for ro in roles])
                if roles
                else f"`There are no {manager_type} manager roles set.`"
            )
            return channel, roles, role_mention, message

        channels = await self.config.guild(context.guild).channels()
        messages = await self.config.guild(context.guild).messages()
        managers = await self.config.guild(context.guild).managers()

        var = {
            "donor": tse.MemberAdapter(context.author),
            "server": tse.GuildAdapter(context.guild),
            "guild": tse.GuildAdapter(context.guild),
            "currency_type": tse.StringAdapter(payload.get("currency_type")),
            "requirements": tse.StringAdapter(payload.get("requirements")),
            "message": tse.StringAdapter(payload.get("message")),
        }

        if _type != "heist":
            var |= {"prize": tse.StringAdapter(payload.get("prize"))}

        channel, roles, role_mention, message = get_manager_roles(_type)
        var |= {"role": tse.StringAdapter(role_mention)}

        if _type in {"event", "giveaway"}:
            if _type == "event":
                var |= {"event_name": tse.StringAdapter(payload.get("event_name"))}
            elif _type == "giveaway":
                var |= {
                    "duration": tse.StringAdapter(payload.get("duration")),
                    "winners": tse.StringAdapter(payload.get("winners")),
                }
            elif _type == "heist":
                var |= {"amount": tse.StringAdapter(payload.get("amount"))}

        processed = await tagengine.process(message=message, seed_variables=var)

        if roles:
            for rl in roles:
                with contextlib.suppress(Exception):
                    await rl.edit(mentionable=True)
        try:
            view = DonationsView(self, context, channel, _type)
            await view.start(
                processed.body,
                processed.actions.get("embed"),
                discord.AllowedMentions(roles=True, users=True, everyone=False),
            )
        except Exception:
            return (
                "Donation channel not found or I do not have permission to send or embed messages"
                " in the channel."
            )
        finally:
            if roles:
                for rl in roles:
                    with contextlib.suppress(Exception):
                        await rl.edit(mentionable=False)

    async def get_managers(
        self, context: commands.Context, _type: str
    ) -> discord.Embed:
        embed = discord.Embed(
            title=f"List of {_type} manager roles for [{context.guild.name}]",
            colour=context.bot._color,
            timestamp=discord.utils.utcnow(),
        ).set_thumbnail(url=nu.is_have_avatar(context.guild))
        if _type == "event":
            roles = await self.config.guild(context.guild).managers.emans()
        elif _type == "giveaway":
            roles = await self.config.guild(context.guild).managers.gmans()
        else:
            roles = await self.config.guild(context.guild).managers.hmans()
        updated_roles = [
            role.mention for r in roles if (role := context.guild.get_role(r))
        ]
        embed.description = (
            nu.cf.humanize_list(updated_roles)
            if updated_roles
            else f"There are no {_type} manager roles set."
        )
        return embed

    async def add_or_remove_manager_roles(
        self,
        context: commands.Context,
        _type: str,
        action_type: str,
        roles: List[discord.Role],
    ) -> List[str]:
        success = []
        failed = []

        def process_roles(role_list: List[int]) -> None:
            for role in roles:
                if (action_type == "add" and role.id in role_list) or (
                    action_type == "remove" and role.id not in role_list
                ):
                    failed.append(role.mention)
                else:
                    (
                        role_list.append(role.id)
                        if action_type == "add"
                        else role_list.remove(role.id)
                    )
                    success.append(role.mention)

        conf = self.config.guild(context.guild).managers
        config = (
            getattr(conf, "emans")
            if _type == "event"
            else (
                getattr(conf, "gmans")
                if _type == "giveaway"
                else getattr(conf, "hmans")
            )
        )

        async with config() as managers:
            if _type == "event":
                process_roles(managers)
            elif _type == "giveaway":
                process_roles(managers)
            else:
                process_roles(managers)

        return [nu.cf.humanize_list(success), nu.cf.humanize_list(failed)]

    @commands.command(
        name="giveawaydonate",
        usage="<currency_type> | <duration> | <winners> | [requirements] | <prize> | [message]",
    )
    @commands.bot_has_permissions(embed_links=True, manage_roles=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def giveawaydonate(
        self, context: commands.Context, *, giveaway: GiveawayConverter
    ):
        """
        Donate to giveaways.

        Split arguments with a vertical bar `|`.
        Put `none` in any of the optional [arguments] if you do not want anything on there.
        """
        if not await self.config.guild(context.guild).channels.gchan():
            return await context.send(
                content="There is no set giveaway donation channel. Ask an admin to set one."
            )
        gaw = {
            "currency_type": giveaway.currency_type,
            "duration": giveaway.duration,
            "winners": giveaway.winners,
            "requirements": giveaway.requirements,
            "prize": giveaway.prize,
            "message": giveaway.message,
        }
        if await self.config.guild(context.guild).auto_delete():
            await context.message.delete()
        else:
            await context.tick()
        msg = await self.send_donation("giveaway", context, **gaw)
        if msg:
            await context.send(content=msg)

    @commands.command(
        name="eventdonate",
        usage="<currency_type> | <event_name> | [requirements] | <prize> | [message]",
    )
    @commands.bot_has_permissions(embed_links=True, manage_roles=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def eventdonate(self, context: commands.Context, *, event: EventConverter):
        """
        Donate to events.

        Split arguments with a vertical bar `|`.
        Put `none` in any of the optional [arguments] if you do not want anything on there.
        """
        if not await self.config.guild(context.guild).channels.echan():
            return await context.send(
                content="There is no set event donation channel. Ask an admin to set one."
            )
        even = {
            "currency_type": event.currency_type,
            "event_name": event.event_name,
            "requirements": event.requirements,
            "prize": event.prize,
            "message": event.message,
        }
        if await self.config.guild(context.guild).auto_delete():
            await context.message.delete()
        else:
            await context.tick()
        msg = await self.send_donation("event", context, **even)
        if msg:
            await context.send(content=msg)

    @commands.command(
        name="heistdonate",
        usage="<currency_type> | <amount> | [requirements] | [message]",
    )
    @commands.bot_has_permissions(embed_links=True, manage_roles=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.guild_only()
    async def heistdonate(self, context: commands.Context, *, heist: HeistConverter):
        """
        Donate to heists.

        Split arguments with a vertical bar `|`.
        Put `none` in any of the optional [arguments] if you do not want anything on there.
        """
        if not await self.config.guild(context.guild).channels.hchan():
            return await context.send(
                content="There is no set heist donation channel. Ask an admin to set one."
            )
        heis = {
            "currency_type": heist.currency_type,
            "amount": heist.amount,
            "requirements": heist.requirements,
            "message": heist.message,
        }
        if await self.config.guild(context.guild).auto_delete():
            await context.message.delete()
        else:
            await context.tick()
        msg = await self.send_donation("heist", context, **heis)
        if msg:
            await context.send(content=msg)

    @commands.group(name="serverdonationsset", aliases=["sdonateset", "sdonoset"])
    @commands.bot_has_permissions(embed_links=True)
    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    async def serverdonationsset(self, context: commands.Context):
        """
        Serverdonations settings.
        """
        pass

    @serverdonationsset.command(name="channel", aliases=["chan", "channels"])
    async def serverdonationsset_channel(
        self,
        context: commands.Context,
        channel_type: Literal["giveaway", "event", "heist"],
        channel: discord.TextChannel = None,
    ):
        """
        Set or remove the giveaway, event or heist donation channel.

        Leave channel blank to remove the set one if there is one.
        """
        conf = self.config.guild(context.guild).channels
        _type = (
            "gchan"
            if channel_type == "giveaway"
            else "echan" if channel_type == "event" else "hchan"
        )
        config = getattr(conf, _type)
        if not channel:
            await config.clear()
            return await context.send(
                content=f"The {channel_type} donation channel has been cleared."
            )
        channel_id = await config()
        if channel_id:
            if channel_id == channel.id:
                return await context.send(
                    content=f"That channel is already the {channel_type} donation channel."
                )
            else:
                return await context.send(
                    content=f"You already have a set {channel_type} donation channel, remove it first."
                )
        await config.set(channel.id)
        await context.send(
            content=f"{channel.mention} has been set as the {channel_type} donation channel."
        )

    @serverdonationsset.command(name="manager", aliases=["managers"])
    async def serverdonationsset_manager(
        self,
        context: commands.Context,
        manager_type: Literal["event", "giveaway", "heist"],
        action_type: Literal["add", "remove", "list"],
        *roles: nu.NoobFuzzyRole,
    ):
        """
        Set the manager roles.

        Leave `role` blank to reset role.
        """
        if action_type == "list":
            embed = await self.get_managers(context, manager_type)
            return await context.send(embed=embed)
        if not roles:
            return await context.send_help()
        actions = await self.add_or_remove_manager_roles(
            context, manager_type, action_type, roles
        )
        _type2 = "added to" if action_type == "add" else "removed from"
        if actions[0]:
            await context.send(
                f"Roles {actions[0]} was successfully {_type2} the list of {manager_type} managers."
            )
        if actions[1]:
            await context.send(
                f"Roles {action_type} have failed to {actions[1]} from the list of {manager_type} managers."
            )

    @serverdonationsset.command(name="message")
    async def serverdonationsset_message(
        self,
        context: commands.Context,
        message_type: Literal["event", "giveaway", "heist"],
        message: str = None,
    ):
        """
        Set the donation message.

        Make sure you know TagScriptEngine.
        Available Blocks:
        If blocks, Random blocks, Fifty fifty blocks, Any blocks, All blocks, Embed blocks.

        Available variables:
        {donor} - The donor.
        Ex: {donor(mention)}, {donor(name)}
        {server} - The server.
        Ex: {server(name)}, {server(id)}
        {role} - The manage role that gets mentioned.
        ` - ` Events:
        {currency_type} - The type of currency that they want to donate.
        {event_name} - The event name.
        {requirements} - The requirements to join the event.
        {prize} - The prize of the event.
        {message} - The optional donor message.
        ` - ` Giveaways:
        {currency_type} - The type of currency that they want to donate.
        {duration} - The duration of the giveaway.
        {winners} - The amount of winners for the giveaway.
        {requirements} - The requirements to join the giveaway.
        {prize} - The prize of the giveaway.
        {message} - The optional donor message.
        ` - ` Heists:
        {currency_type} - The type of currency that they want to donate.
        {amount} - The amount of the heist.
        {requirements} - The requirements to join the heist.
        {message} - The optional donor message.
        """
        if message_type == "event":
            if not message:
                await self.config.guild(context.guild).messages.emsg.clear()
                return await context.send(
                    content="The TagScript for the event donation message has been cleared."
                )
            await self.config.guild(context.guild).messages.emsg.set(message)
            await context.send(
                content="The TagScript for the event donation message has been set to:\n"
                f"{nu.cf.box(message, 'py')}"
            )
        elif message_type == "giveaway":
            if not message:
                await self.config.guild(context.guild).messages.gmsg.clear()
                return await context.send(
                    content="The TagScript for the giveaway donation message has been cleared."
                )
            await self.config.guild(context.guild).messages.gmsg.set(message)
            await context.send(
                content="The TagScript for the giveaway donation message has been set to:\n"
                f"{nu.cf.box(message, 'py')}"
            )
        elif message_type == "heist":
            if not message:
                await self.config.guild(context.guild).messages.hmsg.clear()
                return await context.send(
                    content="The TagScript for the heist donation message has been cleared."
                )
            await self.config.guild(context.guild).messages.hmsg.set(message)
            await context.send(
                content="The TagScript for the heist donation message has been set to:\n"
                f"{nu.cf.box(message, 'py')}"
            )

    @serverdonationsset.command(name="autodelete", aliases=["autodel"])
    async def serverdonationsset_autodelete(self, context: commands.Context):
        """
        Toggle wheather to automatically delete command invocation.
        """
        current = await self.config.guild(context.guild).auto_delete()
        await self.config.guild(context.guild).auto_delete.set(not current)
        state = "will no longer" if current else "will now"
        await context.send(content=f"I {state} automatically delete commands.")

    @serverdonationsset.command(name="donationloggersupport", aliases=["dlsupport"])
    async def serverdonationsset_donationloggersupport(self, context: commands.Context):
        """
        Set whether to enable donationlogger support or not.
        """
        current = await self.config.guild(context.guild).dl_support()
        await self.config.guild(context.guild).dl_support.set(not current)
        state = "disabled" if current else "enabled"
        await context.send(content=f"DonationLogger support is now {state}.")

    @serverdonationsset.command(name="resetguild")
    async def serverdonationsset_resetguild(self, context: commands.Context):
        """
        Reset your serverdonations guild settings.
        """
        act = "You serverdonations guild settings has been cleared."
        conf = "Are you sure you want to reset your serverdonations guild settings?"

        view = nu.NoobConfirmation(obj=context, confirm_action=act)
        await view.start(content=conf)

        await view.wait()

        if view.value:
            await self.config.guild(context.guild).clear()

    @serverdonationsset.command(name="resetcog")
    @commands.is_owner()
    async def serverdonationsset_resetcog(self, context: commands.Context):
        """
        Reset the whole cog config.
        """
        act = "The cog config has been clear."
        conf = "Are you sure you want to reset the whole cog config?"

        view = nu.NoobConfirmation(obj=context, confirm_action=act)
        await view.start(content=conf)

        await view.wait()

        if view.value:
            await self.config.clear_all_guilds()

    @serverdonationsset.command(name="showsettings", aliases=["ss"])
    async def serverdonationsset_showsettings(self, context: commands.Context):
        """
        See your current serverdonations guild settings.
        """
        guild_data = await self.config.guild(context.guild).all()
        chans = guild_data["channels"]
        mans = guild_data["managers"]
        msgs = guild_data["messages"]
        autodel = guild_data["auto_delete"]
        channels = (
            "Event: "
            f"""{f'<#{chans["echan"]}>' if chans["echan"] else "None"}\n"""
            "Giveaway: "
            f"""{f'<#{chans["gchan"]}>' if chans["gchan"] else "None"}\n"""
            "Heist: "
            f"""{f'<#{chans["hchan"]}>' if chans["hchan"] else "None"}\n"""
        )
        managers = (
            "Event: "
            f"""{nu.cf.humanize_list([f'<@&{r}>' for r in mans["emans"]]) if mans["emans"] else "None"}\n"""
            "Giveaway: "
            f"""{nu.cf.humanize_list([f'<@&{r}>' for r in mans["gmans"]]) if mans["gmans"] else "None"}\n"""
            "Heist: "
            f"""{nu.cf.humanize_list([f'<@&{r}>' for r in mans["hmans"]]) if mans["hmans"] else "None"}"""
        )
        embed = discord.Embed(
            title=f"Serverdonations guild settings for [{context.guild.name}]",
            colour=await context.embed_colour(),
            timestamp=discord.utils.utcnow(),
        )
        embed.add_field(name="Auto Delete:", value=autodel, inline=False)
        embed.add_field(name="Donation Channels:", value=channels, inline=False)
        embed.add_field(name="Donation Managers:", value=managers, inline=False)
        embed.set_footer(text="Page (1/4)")
        msg1 = discord.Embed(
            title=f"Serverdonations guild settings for [{context.guild.name}]",
            colour=await context.embed_colour(),
            timestamp=discord.utils.utcnow(),
            description=f"**Event Message:**\n{nu.cf.box(msgs['emsg'])}",
        ).set_footer(text="Page (2/4)")
        msg2 = discord.Embed(
            title=f"Serverdonations guild settings for [{context.guild.name}]",
            colour=await context.embed_colour(),
            timestamp=discord.utils.utcnow(),
            description=f"**Giveaway Message:**\n{nu.cf.box(msgs['gmsg'])}",
        ).set_footer(text="Page (3/4)")
        msg3 = discord.Embed(
            title=f"Serverdonations guild settings for [{context.guild.name}]",
            colour=await context.embed_colour(),
            timestamp=discord.utils.utcnow(),
            description=f"**Heist Message:**\n{nu.cf.box(msgs['hmsg'])}",
        ).set_footer(text="Page (4/4)")
        lst = [embed, msg1, msg2, msg3]
        await nu.NoobPaginator(obj=context, pages=lst).start()

    # <----------------------------------------- SLASH COMMANDS -------------------------------------------->

    @app_commands.command(name="giveawaydonate", description="Donate to giveaways.")
    @app_commands.guild_only()
    @app_commands.checks.bot_has_permissions(embed_links=True)
    @app_commands.checks.cooldown(1, 10, key=lambda x: (x.guild_id, x.user.id))
    @app_commands.describe(
        currency_type="The type of bot currency or any other currency that you want to donate.",
        duration="The duration of the giveaway.",
        winners="The amount of winners for the giveaway.",
        prize="The prize for the giveaway.",
        requirements="The optional requirements for the giveaway.",
        message="Send an optional message for the giveaway.",
    )
    async def slash_giveawaydonate(
        self,
        interaction: discord.Interaction[Red],
        currency_type: str,
        duration: str,
        winners: int,
        prize: str,
        requirements: str = None,
        message: str = None,
    ):
        """_summary_

        Args:
            interaction (discord.Interaction[Red]): _description_
            currency_type (str): _description_
            duration (str): _description_
            winners (int): _description_
            prize (str): _description_
            requirements (str, optional): _description_. Defaults to None.
            message (str, optional): _description_. Defaults to None.
        """
        if not await self.config.guild(interaction.guild).channels.gchan():
            return await interaction.response.send_message(
                content="There is no set giveaway donation channel. Ask an admin to set one.",
                ephemeral=True,
            )
        if not message:
            message = "None"
        if not requirements:
            requirements = "None"
        gaw = {
            "currency_type": currency_type.strip(),
            "duration": (
                nu.cf.humanize_timedelta(timedelta=duration_td)
                if (duration_td := commands.parse_timedelta(duration.strip()))
                else duration.strip()
            ),
            "winners": winners,
            "requirements": requirements.strip(),
            "prize": amt if (amt := format_amount(prize.strip())) else prize.strip(),
            "message": message.strip(),
        }
        context: commands.Context = await interaction.client.get_context(interaction)
        msg = await self.send_donation("giveaway", context, **gaw)
        if msg:
            await interaction.response.send_message(content=msg, ephemeral=True)
        else:
            await interaction.response.send_message(
                content="You have successfully sent a giveaway donation.",
                ephemeral=True,
            )

    @app_commands.command(name="eventdonate", description="Donate to events.")
    @app_commands.guild_only()
    @app_commands.checks.bot_has_permissions(embed_links=True)
    @app_commands.checks.cooldown(1, 10, key=lambda x: (x.guild_id, x.user.id))
    @app_commands.describe(
        currency_type="The type of bot currency or any other currency that you want to donate.",
        event_name="The name of the event that you want members to play.",
        prize="The prize for the event.",
        requirements="The optional requirements for the event.",
        message="Send an optional message for the event.",
    )
    async def slash_eventdonate(
        self,
        interaction: discord.Interaction[Red],
        currency_type: str,
        event_name: str,
        prize: str,
        requirements: str = None,
        message: str = None,
    ):
        """_summary_

        Args:
            interaction (discord.Interaction[Red]): _description_
            currency_type (str): _description_
            event_name (str): _description_
            prize (str): _description_
            requirements (str, optional): _description_. Defaults to None.
            message (str, optional): _description_. Defaults to None.
        """
        if not await self.config.guild(interaction.guild).channels.echan():
            return await interaction.response.send_message(
                content="There is no set event donation channel. Ask an admin to set one.",
                ephemeral=True,
            )
        if not requirements:
            requirements = "None"
        if not message:
            message = "None"
        even = {
            "currency_type": currency_type.strip(),
            "event_name": event_name.strip(),
            "requirements": requirements.strip(),
            "prize": amt if (amt := format_amount(prize.strip())) else prize.strip(),
            "message": message.strip(),
        }
        context = await interaction.client.get_context(interaction)
        msg = await self.send_donation("event", context, **even)
        if msg:
            await interaction.response.send_message(content=msg, ephemeral=True)
        else:
            await interaction.response.send_message(
                content="You have successfully sent an event donation.", ephemeral=True
            )

    @app_commands.command(name="heistdonate", description="Donate to heists.")
    @app_commands.guild_only()
    @app_commands.checks.bot_has_permissions(embed_links=True)
    @app_commands.checks.cooldown(1, 10, key=lambda x: (x.guild_id, x.user.id))
    @app_commands.describe(
        currency_type="The type of bot currency or any other currency that you want to donate.",
        amount="The total amount of the heist.",
        requirements="The optional requirements for the heist.",
        message="Send an optional message for the heist.",
    )
    async def slash_heistdonate(
        self,
        interaction: discord.Interaction[Red],
        currency_type: str,
        amount: str,
        requirements: str = None,
        message: str = None,
    ):
        """_summary_

        Args:
            interaction (discord.Interaction[Red]): _description_
            currency_type (str): _description_
            amount (str): _description_
            requirements (str, optional): _description_. Defaults to None.
            message (str, optional): _description_. Defaults to None.
        """
        if not await self.config.guild(interaction.guild).channels.hchan():
            return await interaction.response.send_message(
                content="There is no set heist donation channel. Ask an admin to set one.",
                ephemeral=True,
            )
        if not requirements:
            requirements = "None"
        if not message:
            message = "None"
        heis = {
            "currency_type": currency_type.strip(),
            "amount": amt if (amt := format_amount(amount.strip())) else amount.strip(),
            "requirements": requirements.strip(),
            "message": message.strip(),
        }
        context = await interaction.client.get_context(interaction)
        msg = await self.send_donation("heist", context, **heis)
        if msg:
            await interaction.response.send_message(content=msg, ephemeral=True)
        else:
            await interaction.response.send_message(
                content="You have successfully sent a heist donation.", ephemeral=True
            )
