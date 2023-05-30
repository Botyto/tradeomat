from enum import Enum

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
    symbol: str
    name: str
    type: SymbolType


class SymbolReader(BaseReader):
    pass


class SymbolWriter(BaseWriter):
    pass
