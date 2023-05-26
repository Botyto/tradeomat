import datetime
import typing


class Event:
    feed: "EventFeed" = None
    timestamp: datetime.datetime

    def __init__(self, timestamp: datetime.datetime):
        self.timestamp = timestamp

T = typing.TypeVar('T', bound=Event)


class EventFeed(typing.Generic[T]):
    live_since: datetime.datetime|None = None

    @property
    def live(self):
        return self.live_since is not None

    def start(self):
        """
        Starts the feed.
        Called once before the first call to next().
        """
        pass

    async def next(self) -> T:
        if not self.live:
            result = self._historical_next()
            if result is not None:
                assert result.feed is None
                result.feed = self
                return result
            self.live_since = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
            self.start_live()
        result = await self._live_next()
        assert result.feed is None
        assert result.timestamp >= self.live_since
        result.feed = self
        return result
    
    def stop(self):
        """
        Stops the feed.
        Called once after the last call to next().
        Called after start_live() (note that start_live() may not be called if backtesting).
        """
        pass
    
    def start_live(self):
        """
        Starts the live feed.
        Called once before the first call to _live_next().
        May not be called if backtesting.
        """
        pass

    def _historical_next(self) -> T|None:
        raise NotImplementedError()
    
    async def _live_next(self) -> T|None:
        raise NotImplementedError()
