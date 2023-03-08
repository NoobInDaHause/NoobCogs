import discord
import datetime
import asyncio

from redbot.core import commands
from redbot.core.bot import Red

class FirstToReact(commands.Cog):
    """
    Play a game of first to react wins.
    
    Cog suggested by: Cool aid man#3600
    
    Cog version: 0.1.0
    Cog author: Noobindahause#2808
    """
    
    def __init__(self, bot: Red):
        self.bot = bot
        
    async def red_delete_data_for_user(self, **kwargs):
        return
    
    @commands.command(name="firsttoreact", aliases=["ftr"])
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def firsttoreact(self, ctx):
        """
        Start a first to react game.
        
        This cog speaks for it self, the first one to react wins.
        A very fun cog.
        """
            
        emote = '✅'
        
        em2 = discord.Embed(description="Please wait while I set up the game...")
        msg = await ctx.send(embed=em2)
        await asyncio.sleep(1)
        
        em3 = discord.Embed(description="Setup completed game starting in 10 seconds get ready.")
        await msg.edit(embed=em3)
        await asyncio.sleep(10)
        
        embed = discord.Embed(
            title=":tada: First To React Game Started :tada:",
            description="After the game ends I will send the list of people who reacted.\nAnd to whoever is the first one on that list that means they are the winner and the first one to react.",
            colour=await ctx.embed_colour()
        ).set_footer(text=f"Hosted by: {ctx.author}", icon_url=ctx.author.avatar_url)
        
        await msg.edit(embed=embed)
        await msg.add_reaction(emote)
        await asyncio.sleep(10)
        
        message = await ctx.fetch_message(msg.id)
        
        players = []
        
        for reaction in message.reactions:
            if reaction.emoji == '✅':
                async for user in reaction.users():
                    if user != self.bot.user:
                        players.append(f"{user.mention}")
                        await message.clear_reactions()
        
        if not players:
            await ctx.send("Time is up and it seems no one has entered the game.")
            return await msg.delete()
        
        endem = discord.Embed(
            title=":tada: First To React Game Ended :tada:",
            description="This first react game has ended.\nCongratulations to the first person on the list who reacted first.",
            color=0x2F3136,
            timestamp=datetime.datetime.utcnow()
        ).set_footer(text="Ended at")
        await message.edit(embed=endem)
        
        await ctx.send('\n'.join(players))
