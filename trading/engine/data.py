import asyncio
import typing

import engine.feed


class EventAggregator:
    loop: asyncio.AbstractEventLoop
    feeds: typing.List[engine.feed.EventFeed]
    buffer: typing.Dict[engine.feed.EventFeed, engine.feed.Event|None]
    all_live: bool = False

    def __init__(self, loop: asyncio.AbstractEventLoop|None = None):
        self.loop = loop or asyncio.get_event_loop()
        self.feeds = []
        self.buffer = {}

    def start(self):
        for feed in self.feeds:
            feed.start()
        self.buffer = {feed: None for feed in self.feeds}

    async def next(self) -> engine.feed.Event:
        if not self.all_live:
            historical = [feed for feed in self.buffer if not feed.live]
            if historical:
                for feed in historical:
                    if self.buffer[feed] is not None:
                        continue
                    event = await feed.next()
                    self.buffer[feed] = event
                earliest: engine.feed.Event|None = None
                for feed in historical:
                    buffered_event = self.buffer[feed]
                    if buffered_event is None:
                        continue
                    if earliest is None or buffered_event.timestamp < earliest.timestamp:
                        earliest = buffered_event
                if earliest:
                    del self.buffer[earliest.feed]
                    self.buffer[earliest.feed] = None
                    return earliest
                else:
                    self.all_live = True
            else:
                self.all_live = True
        if self.all_live:
            raise NotImplementedError()

    def stop(self):
        for feed in self.feeds:
            feed.stop()
