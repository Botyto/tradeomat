import datetime

from engine.feed import Event


class BarEvent(Event):
    open: float
    high: float
    low: float
    close: float
    volume: float

    def __init__(self, timestamp: datetime.datetime, open: float, high: float, low: float, close: float, volume: float):
        super().__init__(timestamp)
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
