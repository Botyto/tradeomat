from enum import Enum


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


class SymbolReader:
    namespace: str
    
    def __init__(self, namespace: str):
        self.namespace = namespace


class SymbolWriter:
    namespace: str
    
    def __init__(self, namespace: str):
        self.namespace = namespace
