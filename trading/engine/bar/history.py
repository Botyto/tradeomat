import csv
import io
import typing

from engine.bar.event import BarEvent


class BarHistory:
    def start(self):
        pass

    def next(self) -> BarEvent|None:
        raise NotImplementedError()
    
    def stop(self):
        pass


class CsvColumnMapping:
    column: str
    parse: typing.Callable[[str], typing.Any]
    field: str

    def __init__(self, column: str, parse: typing.Callable[[str], typing.Any], field: str):
        self.column = column
        self.parse = parse
        self.field = field

    def map(self, value: str, obj: BarEvent):
        setattr(obj, self.field, self.parse(value))


class CsvColumnMapper:
    columns: typing.List[CsvColumnMapping]
    col_indices: typing.Dict[str, int]

    def __init__(self, columns: typing.List[CsvColumnMapping], header: typing.List[str]):
        self.columns = columns
        self.col_indices = {col.column: header.index(col.column) for col in columns}

    def map(self, row: typing.List[str]):
        result = BarEvent(None, None, None, None, None, None)
        for col in self.columns:
            value = row[self.col_indices[col.column]]
            if not value or value == "null":
                continue
            col.map(value, result)
        return result
    
    @classmethod
    def try_make(self, columns: typing.List[CsvColumnMapping], header: typing.List[str]):
        if all(col.column in header for col in columns):
            return CsvColumnMapper(columns, header)


class CsvBarHistory(BarHistory):
    fh: io.IOBase
    reader: typing.Iterable[BarEvent]
    columns: typing.List[CsvColumnMapping]|None = None
    mapper: CsvColumnMapper|None = None
    read_header: bool = False

    def __init__(self, path: str, columns: typing.List[CsvColumnMapping]|None = None):
        self.fh = open(path)
        self.reader = csv.reader(self.fh)
        if columns is not None:
            self.set_columns(columns)

    def set_columns(self, columns: typing.List[CsvColumnMapping]):
        self.columns = columns
        self.read_header = True

    def start(self):
        if self.read_header:
            header: typing.List[str] = next(self.reader)
            mapper = CsvColumnMapper.try_make(self.columns, header)
            if mapper is not None:
                self.mapper = mapper

    def transform(self, row: typing.List[float]):
        if self.mapper is not None:
            return self.mapper.map(row)
        raise NotImplementedError()

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
        if self.fh is None:
            return
        self.reader = None
        self.fh.close()
        self.fh = None
