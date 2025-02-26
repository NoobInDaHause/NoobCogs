import datetime
import quickchart as qc
import typing as t

from .utilities import get_percent_number


class StockObject:
    def __init__(self, **payload):
        self.name: str = payload.get("name")
        self.price: int = payload.get("price")
        self._percent: float = payload.get("percent")
        self.bankrupt: bool = payload.get("bankrupt")
        self.emoji: str = payload.get("emoji")
        self.previous_price: int = payload.get("previous_price")
        self.last_updated_timestamp: float = payload.get("last_updated_timestamp")
        self._graph_url = payload.get("graph_url")

        # these things are just temporary
        self.price_history_time = []
        self.price_history = []

    def __str__(self):
        return self.name

    @property
    def graph_url(self) -> str:
        return self._graph_url or (
            "https://cdn.discordapp.com/attachments/1000751975308197918"
            "/1335571235408707584/no_data_found.png"
        )

    @property
    def last_updated(self) -> t.Optional[datetime.datetime]:
        return (
            datetime.datetime.fromtimestamp(
                self.last_updated_timestamp, datetime.timezone.utc
            )
            if self.last_updated_timestamp
            else None
        )

    @property
    def percent(self) -> str:
        return f"+{self._percent:.0%}" if self._percent > 0 else f"{self._percent:.0%}"

    @property
    def status(self) -> str:
        return (
            "📈"
            if self.price > self.previous_price
            else "📉" if self.price < self.previous_price else "🟰"
        )

    def generate_graph_url(self) -> str:
        chart = qc.QuickChart()
        chart.width = 700
        chart.height = 300
        chart.config = {
            "type": "line",
            "data": {
                "labels": self.price_history_time[-24:],
                "datasets": [
                    {
                        "label": (
                            f"{self.name.title()} "
                            f"({self.last_updated.strftime('%A, %B %d, %Y')} UTC)"
                        ),
                        "data": self.price_history[-24:],
                        "fill": False,
                        "borderColor": "black",
                    },
                ],
            },
        }
        self._graph_url = chart.get_url()

    def update_price(self, date_time: datetime.datetime) -> None:
        if not self.bankrupt:
            self.price_history_time.append(date_time.strftime("%H:%M"))
            self.last_updated_timestamp = date_time.timestamp()
            self._percent = get_percent_number()

            self.previous_price = self.price
            new_price = round(self.price * self._percent)
            self.price = round(self.price + new_price)
            self.price_history.append(self.price)

            self.generate_graph_url()
            if self.price < 10:
                self.price = 0
                self.bankrupt = True

    def to_dict(self) -> dict:
        return {
            self.name: {
                "price": self.price,
                "percent": self._percent,
                "bankrupt": self.bankrupt,
                "emoji": self.emoji,
                "previous_price": self.previous_price,
                "last_updated_timestamp": self.last_updated_timestamp,
                "graph_url": self._graph_url,
            }
        }
