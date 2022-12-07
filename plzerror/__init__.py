from .plzerror import PlzError

def setup(bot):
    bot.add_cog(PlzError(bot))