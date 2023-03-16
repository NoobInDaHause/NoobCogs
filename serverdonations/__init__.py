from .serverdonations import ServerDonations

def setup(bot):
    n = ServerDonations(bot)
    bot.add_cog(n)