import asyncio
import datetime
import discord
import logging
import random

from redbot.core import commands, Config
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_list
try:
    from slashtags import menu
except ModuleNotFoundError:
    from redbot.core.utils.menus import menu
from redbot.core.utils.menus import DEFAULT_CONTROLS
from redbot.core.utils.predicates import MessagePredicate

class SplitOrSteal(commands.Cog):
    """
    A fun split or steal game.

    This game can shatter friendships.
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
        self.log = logging.getLogger("red.WintersCogs.splitorsteal")
        
    __version__ = "2.1.9"
    __author__ = ["Noobindahause#2808"]
    
    def format_help_for_context(self, ctx: commands.Context) -> str:
        """
        Thanks Sinbad and sravan!
        """
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\n\nCog Version: {self.__version__}\nCog Author: {humanize_list([f'{auth}' for auth in self.__author__])}"
    
    async def red_delete_data_for_user(self, *, requester, user_id):
        # This cog does not store any end user data whatsoever.
        return
    
    @commands.group(name="splitorstealset", aliases=["sorsset"])
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    @commands.admin_or_permissions(administrator=True)
    async def splitorstealset(self, ctx):
        """
        Settings for split or steal.
        """
    
    @splitorstealset.command(name="clearactive")
    @commands.guild_only()
    async def splitorstealset_clearactives(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel
    ):
        """
        Clear an active game on a channel.
        
        If you can not start a game on a channel even if there is no game running use this command.
        """
        active = await self.config.guild(ctx.guild).activechan()
        
        if channel not in active:
            return await ctx.send("No active games found in that channel.")
        
        async with self.config.guild(ctx.guild).activechan() as achan:
            index = achan.index(channel.id)
            achan.pop(index)
        await ctx.send(f"Successfully removed the active game in {channel.mention}")
    
    @splitorstealset.command(name="reset")
    @commands.guild_only()
    async def splitorstealset_reset(self, ctx):
        """
        Reset the guild settings to default.
        """
        await ctx.send("Are you sure you want to reset the splitorsteal guild settings? (`yes`/`no`)")

        pred = MessagePredicate.yes_or_no(ctx)
        try:
            await ctx.bot.wait_for("message", check=pred, timeout=30)
        except asyncio.TimeoutError:
            return await ctx.send("You took too long to respond. Cancelling.")

        if pred.result:
            await self.config.guild(ctx.guild).clear()
            return await ctx.send(f"Successfully resetted the guild's settings.")
        else:
            await ctx.send("Alright not doing that then.")
    
    @splitorstealset.command(name="manageronly")
    @commands.guild_only()
    async def splitorstealset_manageronly(
        self,
        ctx: commands.Context,
        true_or_false: bool
    ):
        """
        Toggle whether to restrict the `[p]splitorsteal` command to the set manager roles.
        """
        await self.config.guild(ctx.guild).manager_only.set(true_or_false)
        
        if true_or_false == True:
            yep = f"Restricted the `{ctx.prefix}splitorsteal` command to set manager roles."
        else:
            yep = f"`{ctx.prefix}splitorsteal` command is now public."
            
        await ctx.send(yep)
    
    @splitorstealset.command(name="showsetting", aliases=["ss", "showset", "showsettings"])
    @commands.guild_only()
    async def splitorstealset_showsettings(self, ctx):
        """
        See the settings of SplitOrSteal.
        """
        settings1 = await self.config.guild(ctx.guild).sosmanager_ids()
        settings2 = await self.config.guild(ctx.guild).manager_only()
        manrole = "No manager role set." if not settings1 else humanize_list([f'<@&{role}>' for role in settings1])
        
        emb = discord.Embed(
            title=f"Settings for {ctx.guild}",
            colour=await ctx.embed_colour()
        )
        emb.add_field(name="Sors Manager roles:", value=manrole, inline=False)
        emb.add_field(name="Sors manager only:", value=settings2, inline=False)
        
        await ctx.send(embed=emb)
    
    @splitorstealset.group(name="manager", aliases=["managers"])
    @commands.guild_only()
    async def splitorstealset_manager(self, ctx):
        """
        Add or remove the manager role.
        """
    
    @splitorstealset_manager.command(name="add")
    async def splitorstealset_manager_set(
        self,
        ctx: commands.Context,
        role: discord.Role
    ):
        """
        Add a manager role.
        """
        settings = await self.config.guild(ctx.guild).sosmanager_ids()
        
        if role.id in settings:
            return await ctx.send(f"It appears that role is already in the set manager roles.")
        
        async with self.config.guild(ctx.guild).sosmanager_ids() as sosman:
            sosman.append(role.id)
        await ctx.send(f"Successfully added `@{role.name}` in the manager roles.")
        
    @splitorstealset_manager.command(name="remove")
    async def splitorstealset_manager_remove(
        self,
        ctx: commands.Context,
        role: discord.Role
    ):
        """
        Remove a set manager role.
        """
        settings = await self.config.guild(ctx.guild).sosmanager_ids()
        
        if not settings:
            return await ctx.send("You do not have a manager role set.")
        
        if role.id not in settings:
            return await ctx.send("It appears that role is not in the set manager roles.")
        
        async with self.config.guild(ctx.guild).sosmanager_ids() as sosman:
            index = sosman.index(role.id)
            sosman.pop(index)
        await ctx.send(f"Successfully removed `@{role.name}` from the set manager roles.")
    
    @commands.command(name="sorsrules")
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def sorsrules(self, ctx):
        """
        Some useful information about split or steal.

        Know how to play or what the rules of split or steal game is.
        """
        em1desc = """
        The game involves a segment called `Split or Steal` in which two participants or players make the decision to either `split` or `steal` and to determine how the prize is divided or stolen.
        
        The game also determines the ones who are good or evil.
        
        The game requires 2 participants or players to play.
        
        A very fun game to play.
        
        :warning: This game can shatter friendships! Play at your own risk!
        
        Happy playing! :)
        """

        em2desc = """
        The rules are pretty simple, you have two choices `split` or `steal`.
        ` - ` If both participants or players chose `split` then they both split the prize and everyone is a winner.
        ` - ` If one player chooses `split` and the other player chooses `steal` the bad person who chose steal gets all the prize!
        ` - ` If both players or participants chose `steal` nobody wins the prize cause they are both bad. :joy:
        :warning: Be warned trust no one in this game. ;)
        """

        em3desc = f"""
        The game works by running `{ctx.prefix}splitorsteal <player_1> <player_2> <prize>`.
        You will need 2 players and a prize to start the game.
        You can not play the game with discord bots. Noob.

        Once the command is ran the bot now sets up the game.
        The bot will now tell both the participants to think very carefully and to discuss whether they want to `split` or `steal`.

        Once the minute is up the bot now sends the players a DM's and letting them choose `split` or `steal`.
        Players must have their DM's open! Otherwise the game gets cancelled.

        If one of the players did not respond to the bots DM's they will automatically forfeit the game.
        If one of the players fail to answer `split` or `steal` they will automatically forfeit the game. It's 2 simple choices how did you still mess up??
        The bot also accepts emojis but it only accepts 🤝 for `split` or ⚔️ for `steal` please don't say anything else besides that.

        Then when everything is set we will now see who the bad or the good person is.
        It may be both good or both bad or one good and one bad.
        """

        em1 = discord.Embed(
            title = "***__What is Split or Steal__***",
            description = em1desc,
            colour = await ctx.embed_colour()
        )
        em1.set_footer(text=f"Command executed by: {ctx.author} | Page 1/3", icon_url=ctx.author.avatar_url)

        em2 = discord.Embed(
            title = "***__Rules of Split or Seal__***",
            description = em2desc,
            colour = await ctx.embed_colour()
        )
        em2.set_footer(text=f"Command executed by: {ctx.author} | Page 2/3", icon_url=ctx.author.avatar_url)

        em3 = discord.Embed(
            title = "***__How Split or Steal works__***",
            description = em3desc,
            colour = await ctx.embed_colour()
        )
        em3.set_footer(text=f"Command executed by: {ctx.author} | Page 3/3", icon_url=ctx.author.avatar_url)
        
        emeds = [em1, em2, em3]
        await menu(ctx, emeds, controls=DEFAULT_CONTROLS, timeout=60)
    
    @commands.command(name="splitorsteal", usage="<player_1> <player_2> <prize>", aliases=["sors"])
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.bot_has_permissions(embed_links=True)
    async def splitorsteal(
        self, ctx, player_1: discord.Member = None,
        player_2: discord.Member = None,
        *,
        prize = None
    ):
        """
        Start a split or steal game event.

        Fun game to play.
        """
        manroles = await self.config.guild(ctx.guild).sosmanager_ids()
        manonly = await self.config.guild(ctx.guild).manager_only()
        active = await self.config.guild(ctx.guild).activechan()
        
        if ctx.channel.id in active:
            return await ctx.send(f"A game of SplitOrSteal is already running from this channel. Wait for that one to finish.\nIf you think this is a mistake ask an admin to run `{ctx.prefix}sosset clearactive <channel>` on this channel.")
        
        if manonly == True:
            if any(role.id in manroles for role in ctx.author.roles):
                await ctx.tick()
            else:
                return await ctx.send(f"You do not have permissions to start a split or steal game.")
        
        if not player_1 and not player_2:
            return await ctx.send("This game requires 2 users to play.")
        if player_1.id == player_2.id or player_2.id == player_1.id:
            return await ctx.send("This game requires 2 users to play.")
        if player_1.bot or player_2.bot:
            return await ctx.send("Erm! You cannot play the game with a bot! 🙄 ||Message brought to you by: Cool aid man#3600||")
        if not prize:
            return await ctx.send("The game won't start without a prize.")
        
        host = ctx.author
        user1 = player_1
        user2 = player_2
        splitans = ["split", "🤝"]
        stealans = ["steal", "⚔️"]
        bothans = ["split", "🤝", "steal", "⚔️"]
        
        async with self.config.guild(ctx.guild).activechan() as achan:
            achan.append(ctx.channel.id)
        
        setupembed = discord.Embed(
            description = "Setting up game please wait."
        )
        setup = await ctx.send(embed=setupembed)
        await asyncio.sleep(5)
        
        setupdoneembed = discord.Embed(
            description = "Setup done. Starting split or steal game now."
        )
        await setup.edit(embed=setupdoneembed)
        await asyncio.sleep(3)
        await setup.delete()
        
        sotdesc = "The split or steal game has begun!\nPlayers now have 1 minute to discuss if they want to either split 🤝 or steal ⚔️.\nThink very carefully and make your decisions precise!"
        
        sotembed = discord.Embed(
            title = "Split or Steal Game",
            description = sotdesc,
            colour = await ctx.embed_colour()
        )
        sotembed.add_field(name="Prize:", value=prize, inline=False)
        sotembed.set_footer(text="Remember trust no one in this game. ;)", icon_url="https://cdn.vectorstock.com/i/preview-1x/13/61/mafia-character-abstract-silhouette-vector-45291361.jpg")
        sotembed.set_author(name=f"Hosted by: {host}", icon_url=host.avatar_url)
        sotam = discord.AllowedMentions(roles=False, users=True, everyone=False)
        await ctx.send(content=f"{user1.mention} and {user2.mention}", embed=sotembed, allowed_mentions=sotam)
        await asyncio.sleep(60)
        
        await ctx.send(
            f"Time is up! I will now DM the players if they choose to split 🤝 or steal ⚔️.\n> {user1.mention} and {user2.mention} make sure you have your DM's open for me to send message."
        )
        await asyncio.sleep(3)
        
        try:
            await user2.send(
                f"Waiting for {user1}'s response. Please wait."
            )
        except Exception:
            async with self.config.guild(ctx.guild).activechan() as achan:
                index = achan.index(ctx.channel.id)
                achan.pop(index)
            return await ctx.send(
                f"It seems {user2.mention} had their DM's closed! Cancelling game."
            )

        
        try:
            def check(m):
                return m.author == user1 and m.channel == user1.dm_channel
            
            dm1embed = discord.Embed(
                title = "Split or Steal",
                colour = await ctx.embed_colour(),
                description = "You may now choose. Do you want to `split` 🤝 or `steal` ⚔️?"
            )
            dm1embed.set_footer(text="You have 30 seconds to answer.")
            
            try:
                await user1.send(embed=dm1embed)
            except Exception:
                async with self.config.guild(ctx.guild).activechan() as achan:
                    index = achan.index(ctx.channel.id)
                    achan.pop(index)
                return await ctx.send(
                    f"It seems {user1.mention} had their DM's closed! Cancelling game."
                )
            
            confirm = await ctx.bot.wait_for("message", check=check, timeout=30)
            
            if confirm.content.lower() in splitans:
                await user1.send(
                    "You have chosen split 🤝."
                )
                answer1 = "split"
                
            elif confirm.content.lower() in stealans:
                await user1.send(
                    "You have chosen steal ⚔️."
                )
                answer1 = "steal"
            
            else:
                if confirm.content.lower() not in bothans:
                    await user1.send(
                        "That is not a valid answer, answer either `split` 🤝 or `steal` ⚔️ or you will forfeit the game."
                    )
                    
                    confirm = await ctx.bot.wait_for("message", check=check, timeout=30)
                    
                    if confirm.content.lower() in splitans:
                        await user1.send(
                            "You have chosen split 🤝."
                        )
                        answer1 = "split"
                        
                    if confirm.content.lower() in stealans:
                        await user1.send(
                            "You have chosen steal ⚔️."
                        )
                        answer1 = "steal"
                        
                    if confirm.content.lower() not in bothans:
                        await user1.send(
                            "You have failed to answer 2 times therefor you ferfeit the game."
                        )

                        failar = f"{user2.mention} has won the **{prize}** prize since {user1.mention} forfeited for failing to answer."
                        failimg = "https://cdn.discordapp.com/attachments/996044937730732062/1084848840017985546/boy-look_1.gif"

                        failembed = discord.Embed(
                            colour = 0x00FF00,
                            title = "Game over",
                            timestamp = datetime.datetime.utcnow(),
                            description = f"Split or Steal game has ended.\n{user1.mention} failed to answer `split` or `steal`!\n{user2.mention} chose nothing!"
                        )
                        failembed.add_field(name="Result:", value=failar, inline=False)
                        failembed.set_footer(text=f"Thanks for playing! | Hosted by: {host}", icon_url=host.avatar_url)
                        failembed.set_image(url=failimg)

                        async with self.config.guild(ctx.guild).activechan() as achan:
                            index = achan.index(ctx.channel.id)
                            achan.pop(index)
                        return await ctx.send(content=host.mention, embed=failembed)
        except asyncio.TimeoutError:
            await user1.send(
                "You took too long to respond."
            )

            failar = f"{user2.mention} has won the **{prize}** prize since {user1.mention} forfeited for taking too long to answer."
            failimg = "https://cdn.discordapp.com/attachments/996044937730732062/1084848840017985546/boy-look_1.gif"

            failembed = discord.Embed(
                colour = 0x00FF00,
                title = "Game over",
                timestamp = datetime.datetime.utcnow(),
                description = f"Split or Steal game has ended.\n{user1.mention} took too long to answer!\n{user2.mention} chose nothing!"
            )
            failembed.add_field(name="Result:", value=failar, inline=False)
            failembed.set_footer(text=f"Thanks for playing! | Hosted by: {host}", icon_url=host.avatar_url)
            failembed.set_image(url=failimg)

            async with self.config.guild(ctx.guild).activechan() as achan:
                index = achan.index(ctx.channel.id)
                achan.pop(index)
            return await ctx.send(content=host.mention, embed=failembed)
        
        try:
            def check(m):
                return m.author == user2 and m.channel == user2.dm_channel
            
            dm2embed = discord.Embed(
                title = "Split or Steal",
                description = "You may now choose. Do you want to `split` 🤝 or `steal` ⚔️?",
                colour = await ctx.embed_colour()
            )
            dm2embed.set_footer(text="You have 30 seconds to answer.")
            
            try:
                await user2.send(embed=dm2embed)
            except Exception:
                async with self.config.guild(ctx.guild).activechan() as achan:
                    index = achan.index(ctx.channel.id)
                    achan.pop(index)
                return await ctx.send(
                    f"It seems {user2.mention} had their DM's closed! Cancelling game."
                )
            
            confirm = await ctx.bot.wait_for("message", check=check, timeout=30)
            
            if confirm.content.lower() in splitans:
                await user2.send(
                    "You have chosen split 🤝."
                )
                answer2 = "split"
            
            elif confirm.content.lower() in stealans:
                await user2.send(
                    "You have chosen steal ⚔️."
                )
                answer2 = "steal"
            
            else:
                if confirm.content.lower() not in bothans:
                    await user2.send(
                        "That is not a valid answer, answer either `split` 🤝 or `steal` ⚔️ or you will forfeit the game."
                    )
                    
                    confirm = await ctx.bot.wait_for("message", check=check, timeout=30)
                    
                    if confirm.content.lower() in splitans:
                        await user2.send(
                            "You have chosen split 🤝."
                        )
                        answer2 = "split"
                        
                    if confirm.content.lower() in stealans:
                        await user2.send(
                            "You have chosen steal ⚔️."
                        )
                        answer2 = "steal"
                        
                    if confirm.content.lower() not in bothans:
                        await user2.send(
                            "You have failed to answer 2 times therefor you ferfeit the game."
                        )

                        failar = f"{user1.mention} has won the **{prize}** prize since {user2.mention} forfeited for failing to answer."
                        failimg = "https://cdn.discordapp.com/attachments/996044937730732062/1084848840017985546/boy-look_1.gif"
                        
                        failembed = discord.Embed(
                            colour = 0x00FF00,
                            title = "Game over",
                            timestamp = datetime.datetime.utcnow(),
                            description = f"Split or Steal game has ended.\n{user1.mention} chose {answer1.capitalize()}!\n{user2.mention} failed to answer `split` or `steal`!"
                        )
                        failembed.add_field(name="Result:", value=failar, inline=False)
                        failembed.set_footer(text=f"Thanks for playing! | Hosted by: {host}", icon_url=host.avatar_url)
                        failembed.set_image(url=failimg)

                        async with self.config.guild(ctx.guild).activechan() as achan:
                            index = achan.index(ctx.channel.id)
                            achan.pop(index)
                        return await ctx.send(content=host.mention, embed=failembed)
        except asyncio.TimeoutError:
            await user2.send(
                "You took too long to respond."
            )

            failar = f"{user1.mention} has won the **{prize}** prize since {user2.mention} forfeited for taking too long to answer."
            failimg = "https://cdn.discordapp.com/attachments/996044937730732062/1084848840017985546/boy-look_1.gif"
            
            failembed = discord.Embed(
                colour = 0x00FF00,
                title = "Game over",
                timestamp = datetime.datetime.utcnow(),
                description = f"Split or Steal game has ended.\n{user1.mention} chose {answer1.capitalize()}!\n{user2.mention} took too long to answer!"
            )
            failembed.add_field(name="Result:", value=failar, inline=False)
            failembed.set_footer(text=f"Thanks for playing! | Hosted by: {host}", icon_url=host.avatar_url)
            failembed.set_image(url=failimg)
                        
            async with self.config.guild(ctx.guild).activechan() as achan:
                index = achan.index(ctx.channel.id)
                achan.pop(index)
            await ctx.send(content=host.mention, embed=failembed)
        
        w1 = "https://cdn.discordapp.com/attachments/1084833694285582466/1084840480489099304/tom-jerry-playing-clg846ldrq2w0l6b.gif"
        w2 = "https://cdn.discordapp.com/attachments/1084833694285582466/1084841885803237427/high-five-amy-santiago.gif"
        w3 = "https://cdn.discordapp.com/attachments/1084833694285582466/1084842629520425160/385b1w_1.gif"
        w4 = "https://cdn.discordapp.com/attachments/1084833694285582466/1084844274367082566/high-five_1.gif"
        w5 = "https://cdn.discordapp.com/attachments/1084833694285582466/1084844732766748772/wedding-crasher-hro_1.gif"
        wimg = [w1, w2, w3, w4, w5]
        wingif = random.choice(wimg)
        
        b1 = "https://cdn.discordapp.com/attachments/1005509686302359562/1084805789677531226/tf2-spy.gif"
        b2 = "https://cdn.discordapp.com/attachments/1005509686302359562/1084819894505324674/Sheperd_Betrayal.gif"
        b3 = "https://cdn.discordapp.com/attachments/1005509686302359562/1084835711355719790/icegif-634.gif"
        b4 = "https://cdn.discordapp.com/attachments/1005509686302359562/1084837146822717480/laughing-kangaroo.gif"
        b5 = "https://cdn.discordapp.com/attachments/1005509686302359562/1084838240923693116/AdolescentUnlawfulDungenesscrab-max-1mb_1.gif"
        bimg = [b1, b2, b3, b4, b5]
        betraygif = random.choice(bimg)

        l1 = "https://cdn.discordapp.com/attachments/1005509422749065286/1084826566841872425/clothesline_collision.gif"
        l2 = "https://cdn.discordapp.com/attachments/1005509422749065286/1084827437411602503/17wM.gif"
        l3 = "https://cdn.discordapp.com/attachments/1005509422749065286/1084829936407281664/1.gif"
        l4 = "https://cdn.discordapp.com/attachments/1005509422749065286/1084834072548888687/collision-knights_1.gif"
        l5 = "https://cdn.discordapp.com/attachments/1005509422749065286/1084845839157039104/gta-grand-theft-auto_1.gif"
        limg = [l1, l2, l3, l4, l5]
        losergif = random.choice(limg)
        
        if answer1 and answer2 == "split":
            result = f"Both players chose Split! They can now split the **{prize}** prize 🤝!"
            col = 0x00FF00
            img = wingif
            
        if answer1 == "steal" and answer2 == "split":
            result = f"Player {user1.mention} steals the **{prize}** prize for themselves ⚔️!"
            col = 0xFF0000
            img = betraygif
        
        if answer1 == "split" and answer2 == "steal":
            result = f"Player {user2.mention} steals the **{prize}** prize for themselves ⚔️! "
            col = 0xFF0000
            img = betraygif
        
        if answer1 and answer2 == "steal":
            result = f"Both players chose Steal! Nobody has won the **{prize}** prize 🚫!"
            col = 0x2F3136
            img = losergif
        
        gameoverdesc = f"Split or Steal game has ended.\n[Player 1] {user1.mention} chose {answer1.capitalize()}!\n[Player 2] {user2.mention} chose {answer2.capitalize()}!"
        
        gameoverembed = discord.Embed(
            colour = col,
            timestamp = datetime.datetime.utcnow(),
            title = "Game over",
            description = gameoverdesc,
        )
        gameoverembed.add_field(name="Result:", value=result, inline=False)
        gameoverembed.set_footer(text=f"Thanks for playing! | Hosted by: {host}", icon_url=host.avatar_url)
        gameoverembed.set_image(url=img)
        
        async with self.config.guild(ctx.guild).activechan() as achan:
            index = achan.index(ctx.channel.id)
            achan.pop(index)
        await ctx.send(content=host.mention, embed=gameoverembed)
