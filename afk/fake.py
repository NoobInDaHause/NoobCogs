class FakeMessage:
    def __init__(self, guild_id: int, afk_user_id: int, pinger_id: int) -> None:
        self.guild_id = guild_id
        self.pinger_id = pinger_id
        self.afk_user_id = afk_user_id
