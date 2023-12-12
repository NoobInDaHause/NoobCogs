import discord

from redbot.core.bot import commands

from noobutils import NoobFuzzyRole
from typing import List


class CustomFuzzyRole(NoobFuzzyRole):
    id: int
    mention: str
    members: List[discord.Member]
    name: str
    color: discord.Color
    colour: discord.Colour
    mentionable: bool

    async def convert(self, ctx: commands.Context, argument: str) -> discord.Role:
        if argument.lower().strip().replace("@", "") in {"everyone", "here"}:
            return argument.lower().strip().replace("@", "")
        return await super().convert(ctx, argument)
