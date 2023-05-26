import asyncio
import threading
import typing

import engine.feed


class EventAggregator:
    loop: asyncio.AbstractEventLoop
    feeds: typing.List[engine.feed.EventFeed]
    buffer: typing.List[engine.feed.Event]
    buffer_size: int|None = None
    tasks: typing.List[asyncio.Task[engine.feed.Event]]|None = None
    loop_thread: threading.Thread|None = None

    def __init__(self, loop: asyncio.AbstractEventLoop|None = None):
        self.loop = loop or asyncio.get_event_loop()
        self.feeds = []
        self.buffer = []

    def start(self):
        if self.buffer_size is None:
            self.buffer_size = len(self.feeds)
        for feed in self.feeds:
            feed.start()
        self.tasks = [self._poll(feed) for feed in self.feeds]
        self.loop_thread = threading.Thread(target=self.loop.run_forever, daemon=True)

    def _poll(self, feed: engine.feed.EventFeed) -> asyncio.Future[engine.feed.Event]:
        future = feed.next()
        task = self.loop.create_task(future)
        self.loop.call_soon(task)
        return task

    async def next(self) -> engine.feed.Event:
        if not self.tasks:
            return
        if len(self.buffer) < self.buffer_size:
            new_events = []
            for task in self.tasks:
                if not task.done():
                    continue
                event = task.result()
                if event is None:
                    continue
                new_events.append(event)
                self.tasks.append(self._poll(event.feed))
            if not new_events:
                done, pending = await asyncio.wait(self.tasks, return_when=asyncio.FIRST_COMPLETED)
                new_events = [done.result()]
                self.tasks = list(pending)
                self.tasks.append(self._poll(new_events[0].feed))
            if new_events:
                self.buffer.extend(new_events)
                self.buffer.sort(key=lambda event: event.timestamp, reverse=True)
        if self.buffer:
            return self.buffer.pop()

    def stop(self):
        for feed in self.feeds:
            feed.stop()
        for task in self.tasks:
            task.cancel()
        self.loop.stop()
