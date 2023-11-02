from redbot.core.commands import BadArgument


class AmountConversionFailure(BadArgument):
    pass


class FuzzyRoleConversionFailure(BadArgument):
    pass


class MoreThanThreeRoles(BadArgument):
    pass
