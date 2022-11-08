import asyncio

import discord

import datetime
from redbot.core import checks, commands
from redbot.core.bot import Red

class GiveawayDonation(commands.Cog):
    """
    Donate bot virtual currencies to server giveaways.
    
    Version: **1.0.0**
    Author: **Richard Winters#2808**
    """
    
    __version__ = "1.0.0"
    __author__ = ("Richard Winters#2808")
    
    def __init__(self, bot: Red):
        self.bot = bot
        
    async def red_delete_data_for_user(self, **kwargs):
        return
    
    @checks.bot_has_permissions(embed_links=True, mention_everyone=True)
    @commands.command(aliases=["gdonate"])
    async def giveawaydonate(self, ctx: commands.Context, bot_type: str, duration: str, winners: str, requirements: str, prize: str, message: str = None):
        """
        Donate to server giveaways.
        
        This will ping the Giveaway Managers and sends an embed version of your message.
        """
        pingrole = "<@&996041779369492540>"
        embed = discord.Embed(description=f"**Bot:** {bot_type}\n**Time:** {duration}\n**Winners:** {winners}\n**Requirements:** {requirements}\n**Prize:** {prize}\n**Message:** {message}", color='16760576', timestamp=datetime.datetime.utcnow())
        embed.set_author(name=f"{ctx.author} would like to donate for a giveaway!", icon_url=f"{ctx.author.avatar_url}")
        embed.set_footer(text=f"{ctx.guild}", icon_url=f"{ctx.guild.icon_url}")
        await ctx.send(embed=embed, content=pingrole, allowed_mentions=discord.AllowedMentions(roles=True))
        await ctx.message.delete()
