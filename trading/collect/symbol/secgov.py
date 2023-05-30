from datetime import timedelta
import json
import os
import requests
import zipfile

from collect.engine import BaseCollector
from collect.symbol.engine import SymbolType, Symbol
from collect.web import HttpClient


class SecGovCollector(BaseCollector):
    client: HttpClient
    BULK_URL = "https://www.sec.gov/Archives/edgar/daily-index/bulkdata/submissions.zip"

    def __init__(self, client: HttpClient|None = None):
        super().__init__(timedelta(days=30))
        self.client = client or HttpClient()

    def _download(self):
        temp_fname = os.path.join("temp", "secgov.zip")
        os.makedirs(os.path.dirname(temp_fname), exist_ok=True)
        if os.path.isfile(temp_fname):
            os.remove(temp_fname)
        with self.client.get(self.BULK_URL, stream=True) as r:
            r.raise_for_status()
            with open(temp_fname, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    f.write(chunk)
        return temp_fname
    
    def _extract(self, data: dict):
        result = Symbol()
        # TODO ...
        return result

    def run_once(self):
        result = {}
        zip_path = self._download()
        with zipfile.ZipFile(zip_path, "r") as zip:
            for file in zip.filelist:
                with zip.open(file) as fh:
                    data = json.load(fh)
                    symbol = self._extract(data)
                    result[symbol.symbol] = symbol
        return list(result.values())
