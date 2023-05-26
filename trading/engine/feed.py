import datetime
import typing


class Event:
    feed: "EventFeed"
    timestamp: datetime.datetime

    def __init__(self, timestamp: datetime.datetime):
        self.timestamp = timestamp

T = typing.TypeVar('T', bound=Event)


class EventFeed(typing.Generic[T]):
    live: bool = False

    def start(self):
        pass

    async def next(self) -> T:
        if not self.live:
            result = self._historical_next()
            assert result.feed == self
            if result is not None:
                return result
            self.live = True
        result = await self._live_next()
        assert result.feed == self
        return result
    
    def stop(self):
        pass
    
    def _historical_next(self) -> T|None:
        raise NotImplementedError()
    
    async def _live_next(self) -> T|None:
        raise NotImplementedError()
