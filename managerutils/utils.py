from redbot.core import commands
from redbot.core.utils import mod

def is_gman():
    async def predicate(ctx):
        gman = await ctx.cog.config.guild(ctx.guild).giveaway_manager_id()
        
        if not ctx.guild:
            return False
        
        elif await mod.is_mod_or_superior(ctx.bot, ctx.author):
            return True
        
        elif ctx.author.guild_permissions.administrator:
            return True
        
        elif not gman:
            return False
        
        elif gman:
            role = ctx.guild.get_role(gman)
            if role in ctx.author.roles:
                return True

    return commands.check(predicate)

def is_eman():
    async def predicate(ctx):
        eman = await ctx.cog.config.guild(ctx.guild).event_manager_id()
        
        if not ctx.guild:
            return False
        
        elif await mod.is_mod_or_superior(ctx.bot, ctx.author):
            return True
        
        elif ctx.author.guild_permissions.administrator:
            return True
        
        elif not eman:
            return False
        
        elif eman:
            role = ctx.guild.get_role(eman)
            if role in ctx.author.roles:
                return True

    return commands.check(predicate)

def is_hman():
    async def predicate(ctx):
        hman = await ctx.cog.config.guild(ctx.guild).heist_manager_id()
        
        if not ctx.guild:
            return False
        
        elif await mod.is_mod_or_superior(ctx.bot, ctx.author):
            return True
        
        elif ctx.author.guild_permissions.administrator:
            return True
        
        elif not hman:
            return False
        
        elif hman:
            role = ctx.guild.get_role(hman)
            if role in ctx.author.roles:
                return True

    return commands.check(predicate)