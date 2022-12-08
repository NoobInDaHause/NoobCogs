from redbot.core import checks, commands
from redbot.core.bot import Red

class PlzError(commands.Cog):
    """
    A very useless cog to test an error.
    
    This cog tests an error.
    """
    
    __version__ = "1.0.0"
    __author__ = ("Richard Winters#2808")
    
    def __init__(self, bot: Red):
        self.bot = bot
        
    async def red_delete_data_for_user(self, **kwargs):
        return
    
    @commands.command()
    @checks.is_owner()
    @checks.bot_has_permissions(embed_links=True)
    async def plzerror(self, ctx):
        """
        This command tests the bots error.
        
        Very useless cog if you ask me unless it's for testing purposes.
        This command contains an AssertionError.
        """
        assert False
