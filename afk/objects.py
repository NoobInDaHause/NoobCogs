class FakeMessage:
    def __init__(self, guild_id: int, afk_user_id: int, pinger_id: int) -> None:
        self.guild_id = guild_id
        self.pinger_id = pinger_id
        self.afk_user_id = afk_user_id


class PingObject:
    def __init__(self, **payload):
        # dict_log = {
        #     "pinger_id": message.author.id,
        #     "jump_url": message.jump_url,
        #     "channel_id": message.channel.id,
        #     "timestamp": round(nu.discord.utils.utcnow().timestamp()),
        #     "message": message.content,
        # }
        self.pinger_id: int = payload.get("pinger_id")
        self.jump_url: str = payload.get("jump_url")
        self.channel_id: int = payload.get("channel_id")
        self.timestamp: int = payload.get("timestamp")
        self.message: str = payload.get("message")
