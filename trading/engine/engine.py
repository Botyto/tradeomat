import datetime

import engine.data
import engine.feed


class Engine:
    start_timestamp: datetime.datetime|None = None
    end_timestamp: datetime.datetime|None = None
    aggregator: engine.data.EventAggregator

    async def start(self):
        self.aggregator.start()
        while True:
            event = self.aggregator.next()
            if event is None:
                break
            self.process(event)
        self.aggregator.stop()

    def process(self, event: engine.feed.Event):
        print(event.timestamp, type(event.feed).__name__, type(event).__name__)
