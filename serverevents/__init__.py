from .serverevents import ServerEvents

def setup(bot):
    n = ServerEvents(bot)
    bot.add_cog(n)