import requests
import typing


class Ticker:
    symbols: typing.List[str]
    exchanges: typing.List[str]
    name: str

    def __init__(self, name: str, symbols: typing.List[str], exchanges: typing.List[str] = None):
        self.name = name
        self.symbols = symbols
        self.exchanges = exchanges or []

def scrape_companies():
    result = []
    cik_lookup_data_url = "https://www.sec.gov/Archives/edgar/cik-lookup-data.txt"
    cik_lookup_data = requests.get(cik_lookup_data_url).text.split("\n")
    for cik_line in cik_lookup_data:
        parts = cik_line.split(":")
        if len(parts) < 2:
            continue
        cik = parts[0]
        submission_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        submission_data = requests.get(submission_url).json()
        if not submission_data:
            continue
        if submission_data.get("entityType") != "operating":
            continue
        names = [
            submission_data["name"],
        ]
        names.extend(n["name"] for n in submission_data["formerNames"])
        result.append(Ticker(
            names=names,
            symbols=submission_data["tickers"],
            exchanges=submission_data["exchanges"],
        ))
    return result
