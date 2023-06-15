import asyncio
from datetime import datetime
from decimal import Decimal


class Bar:
    datetime: datetime
    open: Decimal|None = None
    high: Decimal|None = None
    low: Decimal|None = None
    close: Decimal|None = None
    volume: Decimal

    def __init__(self):
        self.datetime = datetime.utcnow().replace(second=0, microsecond=0)
        self.volume = Decimal(0.0)


class AsyncStream:
    _queue: asyncio.Queue
    ended: bool

    def __init__(self):
        self._queue = asyncio.Queue()
        self.ended = False

    def end(self):
        self.ended = True

    def push(self, item):
        if self.ended:
            raise RuntimeError('Cannot enqueue to an ended stream')
        self._queue.put_nowait(item)

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.ended and self._queue.empty():
            raise StopAsyncIteration
        return await self._queue.get()


class BarStream:
    id: int
    stream: AsyncStream

    def __init__(self, id: int, stream: AsyncStream):
        self.id = id
        self.stream = stream
