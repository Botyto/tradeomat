from enum import Enum
import itertools
import pickle
import os
import typing

from collect.engine import BaseReader, BaseWriter


class SymbolType(Enum):
    CURRENCY = "CURRENCY"
    STOCK = "STOCK"
    COMODITY = "COMODITY"
    BOND = "BOND"
    FUTURE = "FUTURE"
    OPTION = "OPTION"
    INDEX = "INDEX"
    ETF = "ETF"
    CDF = "CDF"


class Symbol:
    type: SymbolType
    symbol: str
    name: str

    def __init__(self, type: SymbolType, symbol: str, name: str):
        self.type = type
        self.symbol = symbol
        self.name = name


class SymbolReader(BaseReader):
    pass


class SymbolWriter(BaseWriter):
    def store(self, symbols: typing.List[Symbol]):
        by_type = itertools.groupby(symbols, lambda s: s.type)
        for type, symbols in by_type:
            path = self.get_data_path(type.value + ".json")
            data: typing.List[Symbol] = []
            os.makedirs(os.path.dirname(path), exist_ok=True)
            if os.path.isfile(path):
                with open(path, "rt", encoding="utf-8") as fh:
                    data = pickle.load(fh)
            symbol_map = {symbol.symbol: symbol for symbol in data}
            for symbol in symbols:
                symbol_map[symbol.symbol] = symbol
            data = list(symbol_map.values())
            with open(path, "wt", encoding="utf-8") as fh:
                pickle.dump(data, fh, indent=2, sort_keys=True)
