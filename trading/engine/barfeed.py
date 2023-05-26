import csv
import datetime
import io
import typing

import engine.feed


class BarEvent(engine.feed.Event):
    open: float
    high: float
    low: float
    close: float
    volume: float

    def __init__(self, timestamp: datetime.datetime, open: float, high: float, low: float, close: float, volume: float):
        super().__init__(timestamp)
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume


class BarHistory:
    def start(self):
        pass

    def next(self) -> BarEvent|None:
        raise NotImplementedError()
    
    def stop(self):
        pass


class CsvBarHistory(BarHistory):
    fh: io.IOBase
    reader: typing.Iterable[BarEvent]
    columns: typing.List[str]|None = None
    read_header: bool = True

    def __init__(self, path: str):
        self.fh = open(path)
        self.reader = csv.reader(self.fh)

    def start(self):
        if self.read_header:
            self.columns = next(self.reader)
            if not all(col in self.columns for col in ("datetime", "open", "high", "low", "close", "volume")):
                self.columns = None

    def transform(self, row: typing.List[float]):
        if self.columns is None:
            raise NotImplementedError()
        return BarEvent(
            timestamp=datetime.datetime.strptime(row[self.columns.index("datetime")], "%Y-%m-%d %H:%M:%S"),
            open=float(row[self.columns.index("open")]),
            high=float(row[self.columns.index("high")]),
            low=float(row[self.columns.index("low")]),
            close=float(row[self.columns.index("close")]),
            volume=float(row[self.columns.index("volume")]),
        )

    def next(self) -> BarEvent:
        if self.reader is None:
            return
        try:
            row = next(self.reader)
            bar = self.transform(row)
            return bar
        except StopIteration:
            self.stop()

    def stop(self):
        self.reader = None
        self.fh.close()
        self.fh = None


class BarFeed(engine.feed.EventFeed[BarEvent]):
    history: BarHistory|None = None

    def start(self):
        if self.history is not None:
            self.history.start()

    def _historical_next(self) -> BarEvent|None:
        if self.history is not None:
            return self.history.next()
        
    def stop(self):
        if self.history is not None:
            self.history.stop()
