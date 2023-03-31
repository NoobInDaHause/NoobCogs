import json

from pathlib import Path
from redbot.core.bot import Red

with open(Path(__file__).parent / "info.json") as fp:
    __red_end_user_data_statement__ = json.load(fp)["end_user_data_statement"]

from .globalban import GlobalBan

async def setup(bot: Red):
    cog = GlobalBan(bot)
    await cog.initialize(bot)
    bot.add_cog(cog)