import asyncio
import datetime
import discord
import logging

from typing import Literal, Optional

from redbot.core.bot import Red
from redbot.core import commands, Config
from redbot.core.utils.chat_formatting import humanize_list

from .converters import EmojiConverter

RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]

class FirstToReact(commands.Cog):
    """
    Play a first to react wins game.
    
    Play a first to react game and whoever reacts first wins.
    """
    
    def __init__(self, bot: Red):
        self.bot = bot
        
        self.config = Config.get_conf(self, identifier=1287312641754617, force_registration=True)
        default_guild = {
            "emoji": "\U0001F680"
        }
        self.config.register_guild(**default_guild)
        self.log = logging.getLogger("red.WintersCogs.FirstToReact")
    
    __version__ = "1.0.0"
    __author__ = ["Noobindahause#2808"]
    
    def format_help_for_context(self, ctx: commands.Context) -> str:
        """
        Thanks Sinbad and sravan!
        """
        pre_processed = super().format_help_for_context(ctx)
        return f"{pre_processed}\n\nCog Version: {self.__version__}\nCog Author: {humanize_list(self.__author__)}"
    
    async def red_delete_data_for_user(
        self, *, requester: RequestType, user_id: int
    ) -> None:
        super().red_delete_data_for_user(requester=requester, user_id=user_id)
    
    @commands.group(name="ftrset")
    @commands.guild_only()
    @commands.bot_has_permissions(add_reactions=True, use_external_emojis=True)
    @commands.admin_or_permissions(manage_guild=True, administrator=True)
    async def ftrset(self, ctx):
        """
        Settings for the FirstToReac cog.
        """
    
    @ftrset.command(name="emoji")
    async def ftrset_emoji(self, ctx: commands.Context, emoji: Optional[EmojiConverter]):
        """
        Change the emoji reaction.
        """
        if not emoji:
            await self.config.guild(ctx.guild).emoji.clear()
            return await ctx.send("Successfully resetted the emoji reaction.")
        
        await self.config.guild(ctx.guild).emoji.set(str(emoji))
        await ctx.message.add_reaction(emoji)
        await ctx.send(f"The new emoji reaction has been set to {emoji}.")
    
    @commands.command(name="firsttoreact", aliases=["ftr"])
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True, add_reactions=True)
    async def firsttoreact(self, ctx):
        """
        Start a first to react game.
        """
        emoji = await self.config.guild(ctx.guild).emoji()
        embed = discord.Embed(
            title="First To React Game",
            description=f"React with {emoji} as soon as you see it!\nHosted by: {ctx.author.mention}",
            color=discord.Color.random(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        message = await ctx.send(embed=embed)
        await asyncio.sleep(5)
        await message.add_reaction(emoji)
        
        def check(reaction, user):
            return str(reaction.emoji) == emoji and user != ctx.bot.user
        
        try:
            reaction, user = await ctx.bot.wait_for("reaction_add", check=check, timeout=30)
        except asyncio.TimeoutError:
            failembed= discord.Embed(
                title="First To React Game",
                description=f"This First To React Game has ended.\nWinner: None\nHosted by: {ctx.author.mention}",
                colour=discord.Embed.Empty,
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            await message.edit(embed=failembed)
            return await ctx.send("It appears nobody wants to play.")
        
        endembed = discord.Embed(
            title="First To React Game",
            description=f"This First To React Game has ended.\nWinner: {user.mention}\nHosted by: {ctx.author.mention}",
            colour=discord.Embed.Empty,
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        await message.edit(embed=endembed)
        await ctx.send(f"Congratulations {user.mention}! You have reacted first and won the game!")