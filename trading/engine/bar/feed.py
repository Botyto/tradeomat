from datetime import datetime, timezone

from engine.feed import EventFeed
from engine.bar.event import BarEvent
from engine.bar.history import BarHistory
from engine.bar.live import BarLiveFeed


class BarFeed(EventFeed[BarEvent]):
    history: BarHistory|None = None
    live_feed: BarLiveFeed|None = None

    def start(self):
        if self.history is not None:
            self.history.start()

    def _historical_next(self) -> BarEvent|None:
        if self.history is not None:
            return self.history.next()
        
    async def _live_next(self) -> BarEvent|None:
        if self.live_feed is not None:
            return await self.live_feed.next()

    def _try_stop_history(self):
        if self.history is None:
            return
        self.history.stop()
        self.history = None

    def start_live(self):
        self._try_stop_history()
        if self.live_feed is not None:
            self.live_feed.start()
            self.live_since = self.live_since - ((self.live_since - datetime.min.replace(tzinfo=timezone.utc)) % self.live_feed.interval)

    def stop(self):
        self._try_stop_history()
        if self.live_feed is not None:
            self.live_feed.stop()
