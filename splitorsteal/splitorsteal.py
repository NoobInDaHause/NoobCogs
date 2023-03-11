import discord
import logging
import asyncio
import datetime

from redbot.core import commands
from redbot.core.bot import Red

log = logging.getLogger("red.winterscogs.splitorsteal")

class SplitOrSteal(commands.Cog):
    """
    A fun split or steal game.
    """
    
    def __init__(self, bot: Red) -> None:
        self.bot = bot
        
    __version__ = "1.0.0"
    __author__ = ["Noobindahause#2808"]
    
    def format_help_for_context(self, ctx: commands.Context) -> str:
        """
        Thanks Sinbad and sravan!
        """
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\n\nCog Version: {self.__version__}\nCog Author: {', '.join(self.__author__)}"
    
    async def red_delete_data_for_user(self, **kwargs):
        return
    
    @commands.command(name="splitorsteal", aliases=["sot"], usage="<player_1> <player_2> <prize>")
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.bot_has_permissions(embed_links=True)
    async def splitorsteal(self, ctx, player_1: discord.Member = None, player_2: discord.Member = None, *, prize = None):
        """
        Start a split or steal game event.
        """
        
        if player_1 == None:
            return await ctx.send("This game requires 2 users to play.")
        if player_2 == None:
            return await ctx.send("This game requires 2 users to play.")
        if prize == None:
            return await ctx.send("The game won't start without a prize.")
        
        author = ctx.author
        user1 = player_1
        user2 = player_2
        
        setupembed = discord.Embed(
            description = "Setting up game please wait..."
        )
        setup = await ctx.send(embed=setupembed)
        await asyncio.sleep(5)
        
        setupdoneembed = discord.Embed(
            description = "Set up done. Starting game now."
        )
        await setup.edit(embed=setupdoneembed)
        await asyncio.sleep(3)
        await setup.delete()
        
        sotembed = discord.Embed(
            title = "Split or Steal game",
            description = "The split or steal game has begun!\nPlayers now have 1 minute to discuss if they want to either split 🤝 or steal ⚔️.",
            colour = await ctx.embed_colour()
        )
        sotembed.add_field(name="Prize:", value=prize, inline=False)
        sotembed.set_footer(text="Be warned trust no one in this game. ;)", icon_url="https://static.vecteezy.com/system/resources/previews/012/042/301/original/warning-sign-icon-transparent-background-free-png.png")
        sotembed.set_author(name=f"Hosted by: {author}", icon_url=author.avatar_url)
        sotam = discord.AllowedMentions(roles=False, users=True, everyone=False)
        await ctx.send(content=f"{user1.mention} and {user2.mention}", embed=sotembed, allowed_mentions=sotam)
        await asyncio.sleep(5)
        
        await ctx.send("Time is up! I will now DM the players if they choose to split 🤝 or steal ⚔️.")
        
        await user2.send(
            f"Waiting for {user1}'s answer. Please wait."
        )
        
        try:
            def check(m):
                return m.author == user1 and m.channel == user1.dm_channel
            
            dm1embed = discord.Embed(
                colour = await ctx.embed_colour(),
                description = "You may now choose. Do you want to `split` 🤝 or `steal` ⚔️?\nYou have 30 seconds to answer."
            )
            
            await user1.send(embed=dm1embed)
            
            confirm = await ctx.bot.wait_for("message", check=check, timeout=30)
            
            if confirm.content.lower() in ("split"):
                await user1.send(
                    "You have chosen split 🤝."
                )
                answer1 = "split"
                
            elif confirm.content.lower() in ("steal"):
                await user1.send(
                    "You have chosen steal ⚔️."
                )
                answer1 = "steal"
            
            else:
                if confirm.content.lower() not in ("split", "steal"):
                    await user1.send(
                        "That is not a valid answer, answer `split` or `steal` or you will forfeit the game."
                    )
                    
                    confirm = await ctx.bot.wait_for("message", check=check, timeout=30)
                    
                    if confirm.content.lower() in ("split"):
                        await user1.send(
                            "You have chosen split 🤝."
                        )
                        answer1 = "split"
                        
                    if confirm.content.lower() in ("steal"):
                        await user1.send(
                            "You have chosen steal ⚔️."
                        )
                        answer1 = "steal"
                        
                    if confirm.content.lower() not in ("split", "steal"):
                        await user1.send(
                            "You have failed to answer 2 times therefor you ferfeit the game."
                        )
                        await ctx.send(
                            f"{user1.mention} failed to answer `split` or `steal`, therefor they forfeit game."
                        )
                        await ctx.send(
                            f"{user2.mention} has won the **{prize}**."
                        )
                        return
        except asyncio.TimeoutError:
            await user1.send(
                "You took too long to respond."
            )
            await ctx.send(
                f"{user1.mention} took too long to respond, therefor they forfeit the game."
            )
            await ctx.send(
                f"{user2.mention} has won the {prize}."
            )
            return
        
        try:
            def check(m):
                return m.author == user2 and m.channel == user2.dm_channel
            
            dm2embed = discord.Embed(
                description = "You may now choose. Do you want to `split` 🤝 or `steal` ⚔️?\nYou have 30 seconds to answer.",
                colour = await ctx.embed_colour()
            )
            
            await user2.send(embed=dm2embed)
            
            confirm = await ctx.bot.wait_for("message", check=check, timeout=30)
            
            if confirm.content.lower() in ("split"):
                await user2.send(
                    "You have chosen split 🤝."
                )
                answer2 = "split"
            
            elif confirm.content.lower() in ("steal"):
                await user2.send(
                    "You have chosen steal ⚔️."
                )
                answer2 = "steal"
            
            else:
                if confirm.content.lower() not in ("split", "steal"):
                    await user2.send(
                        "That is not a valid answer, answer `split` or `steal` or you will forfeit the game."
                    )
                    
                    confirm = await ctx.bot.wait_for("message", check=check, timeout=30)
                    
                    if confirm.content.lower() in ("split"):
                        await user2.send(
                            "You have chosen split 🤝."
                        )
                        answer2 = "split"
                        
                    if confirm.content.lower() in ("steal"):
                        await user2.send(
                            "You have chosen steal ⚔️."
                        )
                        answer2 = "steal"
                        
                    if confirm.content.lower() not in ("split", "steal"):
                        await user2.send(
                            "You have failed to answer 2 times therefor you ferfeit the game."
                        )
                        await ctx.send(
                            f"{user2.mention} failed to answer `split` or `steal`, therefor they forfeit game."
                        )
                        await ctx.send(
                            f"{user1.mention} has won the **{prize}**."
                        )
                        return
        except asyncio.TimeoutError:
            await user2.send(
                "You took too long to respond."
            )
            await ctx.send(
                f"{user2.mention} took too long to respond, therefor they forfeit game."
            )
            await ctx.send(
                f"{user1.mention} has won the {prize}."
            )
            return
        
        if answer1 and answer2 == "split":
            result = f"Both players chose split 🤝! They can now split the **{prize}** prize."
            col = 0x00FF00
            
        if answer1 and answer2 == "steal":
            result = f"Both players chose steal ⚔️! They both did not win the **{prize}** prize."
            col = 0x2F3136
            
        if answer1 == "split" and answer2 == "steal":
            result = f"{user2.mention} steals the **{prize}** prize from {user1.mention} ⚔️! "
            col = 0xFF0000
            
        if answer1 == "steal" and answer2 == "split":
            result = f"{user1.mention} steals the **{prize}** prize from {user2.mention} ⚔️!"
            col = 0xFF0000
        
        gameoverembed = discord.Embed(
            colour = col,
            timestamp = datetime.datetime.utcnow(),
            title = "Game over",
            description = f"This Split or Steal game has ended.\n{user1.mention} chose {answer1.capitalize()}!\n{user2.mention} chose {answer2.capitalize()}!"
        )
        gameoverembed.add_field(name="Results:", value=result, inline=False)
        gameoverembed.set_footer(text="Thanks for playing!")
        
        await ctx.send(content=author.mention, embed=gameoverembed)