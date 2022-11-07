from .giveawaydonation import GiveawayDonation


def setup(bot):
    bot.add_cog(GiveawayDonation(bot))