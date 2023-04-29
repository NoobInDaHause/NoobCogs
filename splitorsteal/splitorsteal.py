import asyncio
import datetime
import discord
import logging

from redbot.core import commands, app_commands, Config
from redbot.core.bot import Red
from redbot.core.utils import mod
from redbot.core.utils.chat_formatting import humanize_list

from typing import Literal, Optional

from .constants import SosGifs, SosHelp
from .views import Confirmation, Paginator, SosManager, SosButton

class SplitOrSteal(commands.Cog):
    """
    A fun split or steal game.

    A very fun game to play on an event. This game can shatter friendships!
    [Click here](https://github.com/NoobInDaHause/WintersCogs/blob/red-3.5/splitorsteal/README.md) to see all the available commands for SplitOrSteal.
    """
    def __init__(self, bot: Red) -> None:
        self.bot = bot

        self.config = Config.get_conf(self, identifier=7465487365754648, force_registration=True)
        default_guild_settings = {
            "sosmanager_ids": [],
            "manager_only": False,
            "activechan": []
        }
        self.config.register_guild(**default_guild_settings)
        self.log = logging.getLogger("red.WintersCogs.SplitOrSteal")
        
    __version__ = "1.0.0"
    __author__ = ["Noobindahause#2808"]
    
    def format_help_for_context(self, context: commands.Context) -> str:
        """
        Thanks Sinbad and sravan!
        """
        plural = "s" if len(self.__author__) != 1 else ""
        return f"{super().format_help_for_context(context)}\n\nCog Version: {self.__version__}\nCog Author{plural}: {humanize_list(self.__author__)}"
    
    async def red_delete_data_for_user(
        self, *, requester: Literal["discord_deleted_user", "owner", "user", "user_strict"], user_id: int
    ) -> None:
        # This cog does not store any end user data whatsoever. Also thanks sravan!
        return
    
    async def _start_sos(
        self,
        context: commands.Context,
        host: discord.Member,
        player_1: discord.Member,
        player_2: discord.Member,
        prize
    ):
        """
        Setup the sos game.
        """
        setupembed = discord.Embed(
            description = "Setting up game please wait."
        )
        setup = await context.reply(embed=setupembed, ephemeral=True, mention_author=False)
        await asyncio.sleep(5)
        await setup.delete()
        
        setupdoneembed = discord.Embed(
            description = "Starting split or steal game."
        )
        done = await context.channel.send(embed=setupdoneembed)
        await asyncio.sleep(3)
        await done.delete()
        
        sotembed = discord.Embed(
            title="Split or Steal Game",
            description="The split or steal game has begun!\nPlayers now have 60 seconds to discuss if they want to either split 🤝 or steal ⚔️.\nThink very carefully and make your decisions precise!",
            colour=await context.embed_colour()
        )
        sotembed.add_field(name="Prize:", value=prize, inline=False)
        sotembed.set_footer(text="Remember trust no one in this game. ;)", icon_url="https://cdn.vectorstock.com/i/preview-1x/13/61/mafia-character-abstract-silhouette-vector-45291361.jpg")
        sotembed.set_author(name=f"Hosted by: {host}", icon_url=host.avatar.url)
        sotam = discord.AllowedMentions(roles=False, users=True, everyone=False)
        await context.channel.send(content=f"{player_1.mention} and {player_2.mention}", embed=sotembed, allowed_mentions=sotam)
        await asyncio.sleep(60)
        
        await context.channel.send(
            f"Time is up! I will now DM the players if they want to either split 🤝 or steal ⚔️.\n{player_1.mention} and {player_2.mention} make sure you have your DM's open for me to send message."
        )
        await asyncio.sleep(3)
        
        try:
            await player_2.send(
                f"Waiting for **{player_1}**'s response. Please wait."
            )
        except discord.errors.HTTPException:
            async with self.config.guild(context.guild).activechan() as achan:
                index = achan.index(context.channel.id)
                achan.pop(index)
            return await context.channel.send(
                f"Could not DM {player_2.mention}! Please make sure your DM's are open. Cancelling game."
            )
        
        try:
            answer1 = await self._get_player_answer(player=player_1, prize=prize)
        except discord.errors.HTTPException:
            return await context.channel.send(f"Could not DM {player_1.mention}! Please make sure your DM's are open. Cancelling game.")
        try:
            answer2 = await self._get_player_answer(player=player_2, prize=prize)
        except discord.errors.HTTPException:
            return await context.channel.send(f"Could not DM {player_2.mention}! Please make sure your DM's are open. Cancelling game.")
        
        return await self._end_sos_game(context=context, host=host, player_1=player_1, player_2=player_2, prize=prize, answer1=answer1, answer2=answer2)
    
    async def _get_player_answer(self, player: discord.Member, prize):
        """
        Get the player answer.
        """
        view = SosButton(author=player)
        embed = discord.Embed(
            title="Split or Steal Game.",
            description="You may now choose. Do you want to `split` 🤝 or `steal` ⚔️ or `forfeit` ❌?",
            colour=discord.Colour.default()
        )
        embed.add_field(name="Prize:", value=prize, inline=False)
        embed.set_footer(text="You have 30 seconds to answer or you will automatically forfeit the game.")
        view.message = await player.send(embed=embed, view=view)
        
        await view.wait()
        
        return view.value
    
    async def _end_sos_game(
        self,
        context: commands.Context,
        host: discord.Member,
        player_1: discord.Member,
        player_2: discord.Member,
        prize,
        answer1,
        answer2
    ):  # sourcery skip: low-code-quality
        """
        End the split or steal game.
        """
        async with self.config.guild(context.guild).activechan() as achan:
            index = achan.index(context.channel.id)
            achan.pop(index)
        
        if answer1 and answer2 == "forfeit":
            field_value = f"Both players forfeited! What a shame nobody wins the **{prize}** prize ❌!"
            desc = f"Split or Steal game has ended.\n[Player 1] {player_1.mention} has forfeited!\n[Player 2] {player_2.mention} has forfeited!"
            colour = 0x2F3136
            image = SosGifs.losergif
        
        elif answer1 == "forfeit":
            field_value = f"{player_2.mention} has won the **{prize}** prize since {player_1.mention} has forfeited."
            desc = f"Split or Steal game has ended thanks for playing!\n[Player 1] {player_1.mention} has forfeited!\n[Player 2] {player_2.mention} chose {answer2.title()}!"
            embed = discord.Embed(
                title="Game over",
                colour=0x00FF00,
                description=desc,
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            embed.add_field(name="Result:", value=field_value, inline=False)
            embed.set_footer(text=f"Hosted by: {host}", icon_url=host.avatar.url)
            embed.set_image(url=SosGifs.forfeitgif)
            
            return await context.channel.send(content=host.mention, embed=embed)
        
        elif answer2 == "forfeit":
            field_value = f"{player_1.mention} has won the **{prize}** prize since {player_2.mention} has forfeited."
            desc = f"Split or Steal game has ended thanks for playing!\n[Player 1] {player_1.mention} chose {answer1.title()}!\n[Player 2] {player_2.mention} has forfeited!"
            embed = discord.Embed(
                title="Game over",
                colour=0x00FF00,
                description=desc,
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            embed.add_field(name="Result:", value=field_value, inline=False)
            embed.set_footer(text=f"Hosted by: {host}", icon_url=host.avatar.url)
            embed.set_image(url=SosGifs.forfeitgif)
            
            return await context.channel.send(content=host.mention, embed=embed)
            
        elif answer1 and answer2 == "split":
            field_value = f"Both players chose Split! They can now split the **{prize}** prize 🤝!"
            colour = 0x00FF00
            desc = f"Split or Steal game has ended.\n[Player 1] {player_1.mention} chose {answer1.title()}!\n[Player 2] {player_2.mention} chose {answer2.title()}!"
            image = SosGifs.wingif
            
        elif answer1 == "steal" and answer2 == "split":
            field_value = f"Player {player_1.mention} steals the **{prize}** prize for themselves ⚔️!"
            colour = 0xFF0000
            desc = f"Split or Steal game has ended.\n[Player 1] {player_1.mention} chose {answer1.title()}!\n[Player 2] {player_2.mention} chose {answer2.title()}!"
            image = SosGifs.betraygif
            
        elif answer1 == "split" and answer2 == "steal":
            field_value = f"Player {player_2.mention} steals the **{prize}** prize for themselves ⚔️!"
            colour = 0xFF0000
            desc = f"Split or Steal game has ended.\n[Player 1] {player_1.mention} chose {answer1.title()}!\n[Player 2] {player_2.mention} chose {answer2.title()}!"
            image = SosGifs.betraygif
        
        elif answer1 and answer2 == "steal":
            field_value = f"Both players chose Steal! Nobody has won the **{prize}** prize ❌!"
            colour = 0x2F3136
            desc = f"Split or Steal game has ended thanks for playing!\n[Player 1] {player_1.mention} chose {answer1.title()}!\n[Player 2] {player_2.mention} chose {answer2.title()}!"
            image = SosGifs.losergif
            
        embed = discord.Embed(
            title="Game over",
            description=desc,
            color=colour,
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.add_field(name="Result:", value=field_value, inline=False)
        embed.set_footer(text=f"Hosted by: {host}", icon_url=host.avatar.url)
        embed.set_image(url=image)
        
        return await context.channel.send(content=host.mention, embed=embed)
    
    @commands.hybrid_command(name="splitorsteal", aliases=["sos"])
    @commands.bot_has_permissions(embed_links=True)
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @app_commands.guild_only()
    @app_commands.describe(
        player_1="The first player of the game.",
        player_2="The second player of the game.",
        prize="The prize of the game."
    )
    async def splitorsteal(
        self,
        context: commands.Context,
        player_1: discord.Member,
        player_2: discord.Member,
        *,
        prize: str
    ):
        """
        Start a split or steal game event.

        Fun game to play.
        """
        settings = await self.config.guild(context.guild).all()

        if settings["manager_only"]:
            if context.author.guild_permissions.manage_guild:
                pass
            elif await mod.is_mod_or_superior(context.bot, context.author):
                pass
            elif all(
                role.id not in settings["sosmanager_ids"]
                for role in context.author.roles
            ):
                return await context.reply("You do not have permission to use this command since an admin turned on Manager Only setting.", ephemeral=True, mention_author=False)
        if context.channel.id in settings["activechan"]:
            return await context.reply(content=f"A game of SplitOrSteal is already running from this channel. Wait for that one to finish.\nIf you think this is a mistake ask an admin to run `{context.prefix}splitorstealset clearactive <channel>` on this channel.", ephemeral=True, mention_author=False)
        if player_1.id == player_2.id:
            return await context.reply(content="This game requires 2 users to play.", ephemeral=True, mention_author=False)
        if player_1.bot or player_2.bot:
            return await context.reply(content="The game can not be played with bots.", ephemeral=True, mention_author=False)

        async with self.config.guild(context.guild).activechan() as achan:
            achan.append(context.channel.id)

        await self._start_sos(context=context, host=context.author, player_1=player_1, player_2=player_2, prize=prize)
    
    @commands.hybrid_command(name="splitorstealhelp", aliases=["soshelp"])
    @commands.bot_has_permissions(embed_links=True)
    async def splitorstealhelp(self, context: commands.Context):
        """
        Some useful information about split or steal.

        Know how to play or what the rules of split or steal game is.
        And know some of the commands.
        """
        await context.reply(content="SplitOrSteal help menu sent.", ephemeral=True, mention_author=False)
        
        em1 = discord.Embed(
            title="***__What is Split or Steal__***",
            description=SosHelp.em1desc,
            colour=await context.embed_colour()
        )
        em1.set_footer(text=f"Command executed by: {context.author} | Page 1/3", icon_url=context.author.avatar.url)

        em2 = discord.Embed(
            title="***__Rules of Split or Seal__***",
            description=SosHelp.em2desc,
            colour=await context.embed_colour()
        )
        em2.set_footer(text=f"Command executed by: {context.author} | Page 2/3", icon_url=context.author.avatar.url)

        em3 = discord.Embed(
            title="***__How Split or Steal works__***",
            description=SosHelp.em3desc.replace("[p]", f"{context.prefix}"),
            colour=await context.embed_colour()
        )
        em3.set_footer(text=f"Command executed by: {context.author} | Page 3/3", icon_url=context.author.avatar.url)
        pag = [em1, em2, em3]
        pages = Paginator(bot=self.bot, author=context.author, pages=pag, timeout=60)
        await pages.start(context)
    
    @commands.hybrid_group(name="splitorstealset", invoke_without_command=True, aliases=["sosset"])
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @commands.admin_or_permissions(administrator=True, manage_guild=True)
    async def splitorstealset(self, context: commands.Context):
        """
        Settings for split or steal cog.
        """
        await context.send_help()
        
    @splitorstealset.command(name="clearactive", aliases=["ca"])
    @app_commands.guild_only()
    @app_commands.describe(
        channel="The channel that you want to reset."
    )
    async def splitorstealset_clearactive(self, context: commands.Context, channel: Optional[discord.TextChannel]):
        """
        Clear an active game on a channel if bot thinks there is one in that.
        
        If you can not start a game on a channel even if there is no game running use this command.
        """
        if not context.author.guild_permissions.manage_guild:
            return await context.reply(content="You do not have permission to use this command.", ephemeral=True)
        
        active = await self.config.guild(context.guild).activechan()
        
        if not channel:
            channel = context.channel
        
        if channel.id not in active:
            return await context.send("No active games found in that channel.")
        
        async with self.config.guild(context.guild).activechan() as achan:
            index = achan.index(channel.id)
            achan.pop(index)
            
        await context.send(f"Successfully removed the active game in {channel.mention}.")
    
    @splitorstealset.command(name="manager")
    @app_commands.guild_only()
    async def splitorstealset_manager(self, context: commands.Context):
        """
        Add or remove a manager role.
        """
        if not context.author.guild_permissions.manage_guild:
            return await context.reply(content="You do not have permission to use this command.", ephemeral=True)
        
        embed = discord.Embed(
            description="Choose whether to add or remove splitorsteal manager roles.",
            colour=await context.embed_colour()
        )
        view = SosManager(bot=self.bot, context=context, author=context.author, config=self.config, timeout=30)
        view.message = await context.send(embed=embed, view=view)
        
        await view.wait()
    
    @splitorstealset.command(name="manageronly", aliases=["mo"])
    @app_commands.guild_only()
    @app_commands.describe(
        state="True or False"
    )
    async def splitorstealset_manageronly(self, context: commands.Context, state: bool):
        """
        Toggle whether to restrict the `[p]splitorsteal` command to the set manager roles.
        """
        if not context.author.guild_permissions.manage_guild:
            return await context.reply(content="You do not have permission to use this command.", ephemeral=True)
        
        await self.config.guild(context.guild).manager_only.set(state)
        status = "enabled" if state else "disabled"
        await context.send(f"Manager only setting for splitorsteal has been {status}.")
        
    @splitorstealset.command(name="reset")
    @app_commands.guild_only()
    async def splitorstealset_reset(self, context: commands.Context):
        """
        Reset the guild settings to default.
        """
        if not context.author.guild_permissions.manage_guild:
            return await context.reply(content="You do not have permission to use this command.", ephemeral=True)
        
        confirm_action = "Successfully resetted the SplitOrSteal guild settings."
        view = Confirmation(bot=self.bot, author=context.author, timeout=30, confirm_action=confirm_action)
        view.message = await context.send("Are you sure you want to reset the splitorsteal guild settings?", view=view)
        
        await view.wait()
        
        if view.value == "yes":
            await self.config.guild(context.guild).clear()
        
    @splitorstealset.command(name="resetcog")
    @commands.is_owner()
    async def splitorstealset_resetcog(self, context: commands.Context):
        """
        Reset the splitorsteal cogs configuration. (Bot owners only)
        """
        if not await context.bot.is_owner(context.author):
            return await context.reply(content="You do not have permission to use this command.", ephemeral=True)
        
        confirm_action = "Successfully cleared the splitorsteal cogs configuration."
        view = Confirmation(bot=self.bot, author=context.author, timeout=30, confirm_action=confirm_action)
        view.message = await context.send("This will reset the splitorsteal cogs whole configuration, do you want to continue?", view=view)
        
        await view.wait()
        
        if view.value == "yes":
            await self.config.clear_all()
    
    @splitorstealset.command(name="showsettings", aliases=["ss"])
    @app_commands.guild_only()
    async def splitorstealset_showsetting(self, context: commands.Context):
        """
        See the settings of SplitOrSteal.
        """
        if not context.author.guild_permissions.manage_guild:
            return await context.reply(content="You do not have permission to use this command.", ephemeral=True)
        
        settings = await self.config.guild(context.guild).all()
        
        embed = discord.Embed(
            title=f"Settings for {context.guild}",
            colour=await context.embed_colour()
        )
        embed.add_field(name="Sos Manager roles:", value=humanize_list([f'<@&{role}>' for role in settings["sosmanager_ids"]]) or "None", inline=False)
        embed.add_field(name="Sos manager only:", value=settings["manager_only"], inline=False)
        
        await context.send(embed=embed)
