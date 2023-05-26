import csv
import os
import requests
import typing


class Ticker:
    names: typing.List[str]
    symbols: typing.List[str]

    def __init__(self, names: typing.List[str], symbols: typing.List[str]):
        self.names = names
        self.symbols = symbols


class SecGovTicker(Ticker):
    cik: str
    exchanges: typing.List[str]

    def __init__(self, cik: str, names: typing.List[str], symbols: typing.List[str], exchanges: typing.List[str] = None):
        super().__init__(names, symbols)
        self.cik = cik
        self.exchanges = exchanges or []


class TickerScraper:
    session: requests.Session
    cache: str|None = None

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        })

    def _fetch_ciks(self) -> typing.List[str]:
        url = "https://www.sec.gov/Archives/edgar/cik-lookup-data.txt"
        response = self.session.get(url)
        response.raise_for_status()
        lookup_data = response.text.split("\n")
        result = []
        for cik_line in lookup_data:
            parts = cik_line.split(":")
            if len(parts) < 2:
                continue
            cik = parts[1]
            try:
                int(cik)
            except ValueError:
                continue
            result.append(cik)
        return result

    def _fetch_ticker(self, cik: str) -> SecGovTicker:
        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        response = self.session.get(url)
        response.raise_for_status()
        data: dict = response.json()
        if not data:
            return
        if data.get("entityType") != "operating":
            return
        names = [
            data["name"],
            *(n["name"] for n in data["formerNames"]),
        ]
        return SecGovTicker(
            cik=cik,
            names=names,
            symbols=data["tickers"],
            exchanges=data["exchanges"],
        )
    
    def _fetch_all(self, callback: typing.Callable[[SecGovTicker], None]):
        ciks = self._fetch_ciks()
        result: typing.List[SecGovTicker] = []
        for cik in ciks:
            try:
                ticker = self._fetch_ticker(cik)
            except:
                pass
            if ticker is None:
                continue
            result.append(ticker)
            if callback:
                callback(ticker)
        return result

    def get_all(self):
        if self.cache:
            os.makedirs(self.cache, exist_ok=True)
            cache_path = os.path.join(self.cache, "all.csv")
            if os.path.isfile(cache_path):
                with open(cache_path, "rt", encoding="utf-8") as fh:
                    return [
                        SecGovTicker(
                            cik=row["cik"],
                            names=row["names"].split("|"),
                            symbols=row["symbols"].split("|"),
                            exchanges=row["exchanges"].split("|"),
                        )
                        for row in csv.DictReader(fh)
                    ]
        if self.cache:
            with open(cache_path, "wt", encoding="utf-8", newline="") as fh:
                writer = csv.DictWriter(fh, fieldnames=["cik", "names", "symbols", "exchanges"])
                writer.writeheader()
                def write_one(ticker: SecGovTicker):
                    writer.writerow({
                        "cik": ticker.cik,
                        "names": "|".join(ticker.names),
                        "symbols": "|".join(ticker.symbols),
                        "exchanges": "|".join(ticker.exchanges),
                    })
                    fh.flush()
                result = self._fetch_all(write_one)
        else:
            result = self._fetch_all(None)
        return result
