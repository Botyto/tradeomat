from datetime import datetime
from enum import Enum
import os
import typing

from collect.engine import BaseReader, BaseWriter
from collect.bar.data import Bar


class BarFrequency(Enum):
    MIN_1 = "MIN_1"
    DAY_1 = "DAY_1"


class BarReader(BaseReader):
    symbol: str

    def __init__(self, namespace: str, symbol: str):
        super().__init__(namespace)
        self.symbol = symbol

    def _get_years(self, freq: BarFrequency) -> typing.List[int]:
        dir = self._bars_dir(freq)
        if not os.path.isdir(dir):
            return []
        return [int(name[:-4]) for name in os.listdir(dir)]

    def _bars_dir(self, freq: BarFrequency, year: int) -> str:
        return os.path.join("data", "bars", self.namespace, self.symbol, freq.value)

    def _bars_path(self, freq: BarFrequency, year: int) -> str:
        return os.path.join("data", "bars", self.namespace, self.symbol, freq.value, f"{year}.bar")

    def date_range(self, freq: BarFrequency) -> typing.Tuple[datetime, datetime]:
        years = self._get_years(freq)
        first_year = min(years)
        last_year = max(years)
        path = self._bars_path(freq, first_year)
        with open(path, "rb") as fh:
            fh.seek(4, os.SEEK_SET)
            first_bar = Bar.read(fh)
        path = self._bars_path(freq, last_year)
        with open(path, "rb") as fh:
            fh.seek(-Bar.BINARY_SIZE, os.SEEK_END)
            last_bar = Bar.read(fh)
        return (first_bar.date, last_bar.date)

    def count(self, freq: BarFrequency):
        count = 0
        years = self._get_years(freq)
        for year in years:
            path = self._bars_path(freq, year)
            count += (os.path.getsize(path) - 4) // Bar.BINARY_SIZE
        return count

    def read_all(self, freq: BarFrequency):
        result = []
        years = self._get_years(freq)
        for year in years:
            path = self._bars_path(freq, year)
            count = (os.path.getsize(path) - 4) // Bar.BINARY_SIZE
            with open(path, "rb") as fh:
                fh.seek(4, os.SEEK_SET)
                result.extend(Bar.read(fh) for _ in range(count))
        return result

    def read_since(self, freq: BarFrequency, start: datetime):
        years = self._get_years(freq)
        years = [year for year in years if year >= start.year]
        result = []
        for year in years:
            path = self._bars_path(freq, year)
            count = (os.path.getsize(path) - 4) // Bar.BINARY_SIZE
            with open(path, "rb") as fh:
                fh.seek(4, os.SEEK_SET)
                bars = [Bar.read(fh) for _ in range(count)]
                bars = [bar for bar in bars if bar.date >= start]
                result.extend(bars)
        return result


class BarWriter(BaseWriter):
    symbol: str

    def __init__(self, collector, namespace, symbol: str):
        super().__init__(collector, namespace)
        self.symbol = symbol

    def store(self, freq: BarFrequency, bars: typing.List[Bar]):
        if not bars:
            return
        path = self.get_ns_data_path(self.symbol, freq.value + ".bar")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        exists = os.path.isfile(path)
        with open(path, "ab") as fh:
            if not exists:
                fh.write(Bar.MARKER.encode("ascii"))
            else:
                existing_marker = fh.read(4).decode("ascii")
                if existing_marker != Bar.MARKER:
                    raise Exception(f"Existing marker {existing_marker} does not match {Bar.MARKER}")
                fh.seek(0, os.SEEK_END)
            for bar in bars:
                bar.write(fh)
