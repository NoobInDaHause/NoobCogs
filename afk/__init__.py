import json

from pathlib import Path
from redbot.core.bot import Red

with open(Path(__file__).parent / "info.json") as fp:
    """
    This cog stores data provided by users for the express purpose of notifying users whenever they go AFK and only for that reason. It does not store user data which was not provided through a command. Users may remove their own content without making a data removal request. This cog does not support data requests, but will respect deletion requests.
    
    Thanks aikaterna and some others for this end user data statement.
    """
    __red_end_user_data_statement__ = json.load(fp)["end_user_data_statement"]
    
from .afk import Afk

async def setup(bot: Red):
    cog = Afk(bot)
    bot.add_cog(cog)