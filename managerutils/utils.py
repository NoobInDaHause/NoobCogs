from redbot.core import commands
from redbot.core.utils import mod

# credits go to cray for these custom checks

def is_gman():
    async def predicate(ctx):
        gmans = await ctx.cog.config.guild(ctx.guild).giveaway_manager_ids()
        
        if not ctx.guild:
            return False
        
        elif await mod.is_mod_or_superior(ctx.bot, ctx.author):
            return True
        
        elif ctx.author.guild_permissions.administrator:
            return True
        
        elif not gmans:
            return False
        
        elif gmans:
            if any(role.id in gmans for role in ctx.author.roles):
                return True

    return commands.check(predicate)

def is_eman():
    async def predicate(ctx):
        emans = await ctx.cog.config.guild(ctx.guild).event_manager_ids()
        
        if not ctx.guild:
            return False
        
        elif await mod.is_mod_or_superior(ctx.bot, ctx.author):
            return True
        
        elif ctx.author.guild_permissions.administrator:
            return True
        
        elif not emans:
            return False
        
        elif emans:
            if any(role.id in emans for role in ctx.author.roles):
                return True

    return commands.check(predicate)

def is_hman():
    async def predicate(ctx):
        hmans = await ctx.cog.config.guild(ctx.guild).heist_manager_ids()
        
        if not ctx.guild:
            return False
        
        elif await mod.is_mod_or_superior(ctx.bot, ctx.author):
            return True
        
        elif ctx.author.guild_permissions.administrator:
            return True
        
        elif not hmans:
            return False
        
        elif hmans:
            if any(role.id in hmans for role in ctx.author.roles):
                return True

    return commands.check(predicate)