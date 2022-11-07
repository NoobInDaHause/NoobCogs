import asyncio

import discord

import datetime
from redbot.core import checks, commands
from redbot.core.bot import Red

class GiveawayDonation(commands.Cog):
    """
    Donate bot virtual currencies to server giveaways."""
    
    __version__ = "1.0.0"
    
    def __init__(self, bot: Red):
        self.bot = bot
        
    async def red_delete_data_for_user(self, **kwargs):
        return
    
    @checks.bot_has_permissions(embed_links=True, mention_everyone=True)
    @commands.command(name="giveawaydonate")
    async def cmd_giveawaydonate(self, ctx: commands.Context, bot_type: str, duration: str, winners: str, requirements: str = None, prize: str, message=None: str = None):
        """
        Donate to server giveaways.
        
        Will automatically delete the command invocation.
        """
        pingrole = "<@&996041779369492540>"
        embed = discord.Embed(description=f"**Bot:** {bot_type}\n**Time:** {duration}\n**Winners:** {winners}\n**Requirements:** {requirements}\n**Prize:** {prize}\n**Message:** {message}", color=discord.Colour.blurple(), timestamp=datetime.datetime.utcnow())
        embed.set_author(name=f"{ctx.author} would like to donate for a giveaway!", icon_url=f"{ctx.author.avatar_url}")
        embed.set_footer(text=f"{ctx.guild}", icon_url=f"{ctx.guild.icon_url}")
        await ctx.send(embed=embed, content=pingrole, allowed_mentions=discord.AllowedMentions(roles=True))
        await ctx.message.delete()
