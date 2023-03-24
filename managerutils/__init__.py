from .managerutils import ManagerUtils

def setup(bot):
    n = ManagerUtils(bot)
    bot.add_cog(n)