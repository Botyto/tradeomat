import asyncio
import datetime

import engine.data
import engine.feed


class Engine:
    loop: asyncio.AbstractEventLoop
    start_timestamp: datetime.datetime|None = None
    end_timestamp: datetime.datetime|None = None
    aggregator: engine.data.EventAggregator

    def __init__(self, loop: asyncio.AbstractEventLoop|None = None):
        self.loop = loop or asyncio.get_event_loop()

    def run(self):
        self.aggregator.start()
        self._loop()
        self.aggregator.stop()

    def _loop(self):
        if self.start_timestamp is not None:
            pending_event: engine.feed.Event|None = None
            while True:
                future = self.aggregator.next()
                event = self.loop.run_until_complete(future)
                if event is None:
                    break
                if event.timestamp < self.start_timestamp:
                    continue
                pending_event = event
                break
            if pending_event:
                if self.end_timestamp is None or pending_event.timestamp >= self.end_timestamp:
                    return
                self.process(pending_event)
        while True:
            future = self.aggregator.next()
            event = self.loop.run_until_complete(future)
            if event is None:
                break
            if self.end_timestamp is not None and event.timestamp >= self.end_timestamp:
                break
            self.process(event)

    def process(self, event: engine.feed.Event):
        print(event.timestamp, type(event.feed).__name__, type(event).__name__)
