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
    async def cmd_giveawaydonate(self, ctx: commands.Context, bot, *, time, winners, requirements, prize, message: str = None):
        """
        Donate to server giveaways.
        
        Will automatically delete the command invocation.
        """
        pingrole = "<@&996041779369492540>"
        embed = discord.Embed(description=f"**Bot:** {args1}\n**Time:** {args2}\n**Winners:** {args3}\n**Requirements:** {args4}\n**Prize:** {args5}\n**Message:** {args6}", color=discord.Colour.blurple(), timestamp=datetime.datetime.utcnow())
        embed.set_author(name=f"{ctx.author} would like to donate for a giveaway!", icon_url=f"{ctx.author.avatar_url}")
        embed.set_footer(text='\u200b')
        await ctx.send(embed=embed, content=pingrole, allowed_mentions=discord.AllowedMentions(roles=True))
        await ctx.message.delete()
