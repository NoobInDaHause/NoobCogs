import json

from pathlib import Path
from redbot.core.bot import Red

with open(Path(__file__).parent / "info.json") as fp:
    __red_end_user_data_statement__ = json.load(fp)["end_user_data_statement"]
    
from .firsttoreact import FirstToReact

async def setup(bot: Red):
    cog = FirstToReact(bot)
    bot.add_cog(cog)