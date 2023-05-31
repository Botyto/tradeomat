from datetime import datetime, timedelta
import json
import os
import zipfile

from collect.engine import BaseCollector
from collect.symbol.engine import SymbolType, Symbol, SymbolWriter
from collect.web import HttpClient

NAMESPACE = "secgov"


class SecGovCollector(BaseCollector):
    BULK_URL = "https://www.sec.gov/Archives/edgar/daily-index/bulkdata/submissions.zip"
    client: HttpClient
    writer: SymbolWriter

    def __init__(self, env, client: HttpClient|None = None):
        super().__init__(env, timedelta(days=30))
        self.client = client or HttpClient()
        self.writer = SymbolWriter(self, NAMESPACE)

    def _download(self):
        temp_fname = self.get_temp_path("secgov.zip")
        os.makedirs(os.path.dirname(temp_fname), exist_ok=True)
        if os.path.isfile(temp_fname):
            mtime = os.path.getmtime(temp_fname)
            if datetime.utcnow() - datetime.utcfromtimestamp(mtime) < self.interval:
                return temp_fname
            os.remove(temp_fname)
        with self.client.get(self.BULK_URL, stream=True) as r:
            r.raise_for_status()
            with open(temp_fname, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    f.write(chunk)
        return temp_fname
    
    def _extract(self, data: dict):
        if not data.get("tickers"):
            return
        return Symbol(SymbolType.STOCK, data["tickers"][0], data["name"])

    def run_once(self):
        result = {}
        zip_path = self._download()
        with zipfile.ZipFile(zip_path, "r") as zip:
            for file in zip.filelist:
                with zip.open(file) as fh:
                    try:
                        data = json.load(fh)
                        symbol = self._extract(data)
                        if not symbol:
                            continue
                        result[symbol.symbol] = symbol
                    except Exception as e:
                        self.log.error(f"Failed to process {file.filename}: {e}")
        self.writer.store(result.values())
