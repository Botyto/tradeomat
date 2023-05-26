import asyncio
from datetime import datetime, timedelta

from engine.bar.event import BarEvent

ZERO_TIMEDELTA = timedelta()


class BarLiveFeed:
    LEEWAY = timedelta(seconds=1)

    ticker: str
    interval: timedelta
    last_poll: datetime|None = None

    def __init__(self, ticker: str, interval: timedelta):
        self.ticker = ticker
        self.interval = interval

    def start(self):
        pass

    async def next(self) -> BarEvent|None:
        start = self.last_poll or datetime.utcnow()
        delay = self.interval - ((start - datetime.min) % self.interval)
        target = start + delay - self.interval
        if delay > ZERO_TIMEDELTA:
            await asyncio.sleep((delay + self.LEEWAY).total_seconds())
        self.last_poll = datetime.utcnow()
        return await self._fetch(target)

    def stop(self):
        pass

    async def _fetch(self, target: datetime) -> BarEvent|None:
        raise NotImplementedError()
