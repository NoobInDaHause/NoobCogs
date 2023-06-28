import discord

from typing import Union

class Coordinate(dict):
    def __missing__(self, key):
        return key

def is_have_avatar(thing: Union[discord.Member, discord.Guild] = None) -> str:
    if not thing:
        return ""
    if isinstance(thing, discord.Member):
        try:
            return thing.avatar.url
        except AttributeError:
            return thing.display_avatar.url
    if isinstance(thing, discord.Guild):
        try:
            return thing.icon.url
        except AttributeError:
            return ""

def access_denied() -> str:
    return "https://cdn.discordapp.com/attachments/1000751975308197918/1110013262835228814/1.mp4"

def get_button_colour(colour: str) -> discord.ButtonStyle:
    if colour.lower() == "blurple":
        return discord.ButtonStyle.blurple
    elif colour.lower() == "red":
        return discord.ButtonStyle.red
    elif colour.lower() == "green":
        return discord.ButtonStyle.green
    elif colour.lower() == "grey":
        return discord.ButtonStyle.grey
