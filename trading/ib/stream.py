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


class BarStream:
    id: int
    queue: asyncio.Queue[Bar]

    def __init__(self, id: int, queue: asyncio.Queue[Bar]):
        self.id = id
        self.queue = queue

    async def __aiter__(self):
        return self

    async def __anext__(self):
        result = await self.queue.get()
        if result is None:
            raise StopAsyncIteration
        return result