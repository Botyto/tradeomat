import asyncio
from datetime import datetime, timedelta

from engine.bar.event import BarEvent

ZERO_TIMEDELTA = timedelta()


class BarLiveFeed:
    LEEWAY = timedelta(seconds=3)

    ticker: str
    interval: timedelta
    last_poll: datetime|None = None

    def __init__(self, ticker: str, interval: timedelta):
        self.ticker = ticker
        self.interval = interval

    def start(self):
        """
        Starts the live feed.
        Called once before the first call to next().
        """

    async def next(self) -> BarEvent|None:
        start = self.last_poll or datetime.utcnow()
        until_end = self.interval - ((start - datetime.min) % self.interval)
        target = start + until_end - self.interval
        delay = target + self.interval - datetime.utcnow()
        if delay > ZERO_TIMEDELTA:
            await asyncio.sleep((delay + self.LEEWAY).total_seconds())
        self.last_poll = datetime.utcnow()
        return await self._fetch(target)

    def stop(self):
        """
        Stops the live feed.
        Called once after the last call to next().
        Note that stop() will be called, even if start() was not.
        """

    async def _fetch(self, target: datetime) -> BarEvent|None:
        raise NotImplementedError()
