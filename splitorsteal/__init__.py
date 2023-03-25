from .splitorsteal import SplitOrSteal

def setup(bot):
    n = SplitOrSteal(bot)
    bot.add_cog(n)