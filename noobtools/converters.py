import noobutils as nu

from typing import Union


class ModifiedFuzzyRole(nu.NoobFuzzyRole):
    async def convert(
        self, ctx: nu.commands.Context, argument: str
    ) -> Union[nu.discord.Role, str]:
        arg = argument.lower().strip()
        if arg in {"@here", "here", "@everyone", "everyone"}:
            return arg.replace("@", "")
        return await super().convert(ctx, argument)
