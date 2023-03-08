import discord
import datetime
import asyncio

from redbot.core import commands
from redbot.core.bot import Red

class FirstToReact(commands.Cog):
    """
    Play a game of first to react wins.
    
    Cog suggested by: Cool aid man#3600
    
    Cog version: 0.0.3
    Cog author: Noobindahause#2808
    """
    
    def __init__(self, bot: Red):
        self.bot = bot
        
    async def red_delete_data_for_user(self, **kwargs):
        return
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        user = self.bot.get_user(payload.user_id)
        
        if not user:
            user = await self.bot.fetch_user(payload.user_id)
        
        if user.bot:
            return
        
        if str(payload.emoji) == '⚡':
            await message.clear_reactions()
            await asyncio.sleep(2)
            winner = discord.Embed(
                title="\U0001F389 First To React Game Ended \U0001F389",
                description=f"This first to react game has ended.\nCongratulations to {user.mention}! They are the first one to react!",
                colour=0x2F3136,
                timestamp=datetime.datetime.utcnow()
            ).set_footer(text="Ended at")
            await message.edit(content=user.mention, embed=winner)
            await message.reply(f"{user.mention} has reacted first!")
    
    @commands.command(name="firsttoreact", aliases=["ftr"])
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def firsttoreact(self, ctx):
        """
        Start a first to react game.
        
        This cog speaks for it self, the first one to react wins.
        A very fun cog.
        """
            
        emote = '⚡'
        
        embed = discord.Embed(
            title="\U0001F389 First To React Game \U0001F389",
            description="First one to react with ⚡ wins the game!",
            colour=await ctx.embed_colour()
        ).set_footer(text=f"Hosted by: {ctx.author}", icon_url=ctx.author.avatar_url)
        
        ftrmsg = await ctx.send(embed=embed)
        await ftrmsg.add_reaction(emote)
