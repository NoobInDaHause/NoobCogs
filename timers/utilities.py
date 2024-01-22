from datetime import datetime, timezone

from typing import Coroutine


class FollowupItem:
    def __init__(self, priority: int, timeout: datetime, coro: Coroutine):
        self.priority: int = priority
        self.timeout: datetime = timeout
        self.coro: Coroutine = coro

    def __lt__(self, other: "FollowupItem"):
        return (self.priority, self.timeout) < (other.priority, other.timeout)

    def is_valid(self):
        return self.timeout > datetime.now(timezone.utc)


class MessageEditItem:
    def __init__(
        self, timer_id: int, priority: int, timeout: datetime, coro: Coroutine
    ):
        self.priority: int = priority
        self.timeout: datetime = timeout
        self.coro: Coroutine = coro
        self.timer_id: int = timer_id

    def __lt__(self, other: "MessageEditItem"):
        return (self.priority, self.timeout) < (other.priority, other.timeout)

    def is_valid(self):
        return self.timeout > datetime.now(timezone.utc)
