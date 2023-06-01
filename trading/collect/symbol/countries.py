from datetime import timedelta
import pycountry
import pycountry.db

from collect.engine import BaseCollector
from collect.symbol.engine import SymbolType, Symbol, SymbolWriter


class PyCountryCollector(BaseCollector):
    writer: SymbolWriter

    def __init__(self, env):
        super().__init__(env, timedelta(days=30))
        self.writer = SymbolWriter(self, "pycountry")

    def run_once(self):
        self.writer.store([
            Symbol(SymbolType.CURRENCY, currency.alpha_3, currency.name)
            for currency in pycountry.currencies
        ])
