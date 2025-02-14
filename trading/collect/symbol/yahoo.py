from datetime import timedelta
import typing

from collect.engine import BaseCollector
from collect.web import HttpClient


class YahooSymbolCollector(BaseCollector):
    client: HttpClient

    def __init__(self, env, client: HttpClient|None = None):
        super().__init__(env, timedelta(days=30))
        self.client = client or HttpClient()

    def _next(self, symbol: str, leaf: bool, max_depth: int = 3):
        leaf = leaf or len(symbol) == max_depth
        if not leaf:
            return symbol + "a"
        if all(c == "z" for c in symbol):
            return
        past_z = chr(ord("z") + 1)
        symbol = symbol[:-1] + chr(ord(symbol[-1]) + 1)
        idx = len(symbol) - 1
        while idx >= 0 and symbol[idx] == past_z:
            symbol = symbol[:idx] + "a" + symbol[idx + 1 :]
            symbol = symbol[:idx - 1] + chr(ord(symbol[idx - 1]) + 1) + symbol[idx:]
            idx -= 1
        return symbol

    def _dfs(self) -> typing.List[str]:
        result = []
        symbol = "a"
        while symbol:
            url = f"https://query1.finance.yahoo.com/v1/finance/search?q={symbol}&quotesCount=100&newsCount=0&listsCount=0"
            response = self.client.get(url)
            response.raise_for_status()
            data = response.json()
            print(symbol, len(data["quotes"]))
            for quote in data["quotes"]:
                result.append(quote["symbol"])
            symbol = self._next(symbol, len(data["quotes"]) == 0)
        return result

    def run_once(self):
        symbols = self._dfs()
        print(symbols)
