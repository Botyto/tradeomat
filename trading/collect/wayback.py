from datetime import datetime, timezone
import typing
import urllib.parse

from collect.web import HttpClient


class WaybackScraper:
    client: HttpClient

    def __init__(self, client: HttpClient|None = None):
        self.client = client or HttpClient()

    def _parse_timestamp(self, timestamp: str):
        return datetime.strptime(timestamp, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)

    def _to_timestamp(self, date: datetime):
        return date.strftime("%Y%m%d%H%M%S")

    def list_snapshopts(self, url, start: datetime|None = None, end: datetime|None = None) -> typing.List[datetime]:
        resume_key = None
        encoded_url = urllib.parse.quote(url)
        base_url = f"http://web.archive.org/cdx/search/cdx?url={encoded_url}&limit=1000&showResumeKey=true&output=json"
        if start:
            base_url += f"&from={self._to_timestamp(start)}"
        if end:
            base_url += f"&to={self._to_timestamp(end)}"
        last_digest = None
        result = []
        while True:
            api_url = f"{base_url}&resumeKey={resume_key}" if resume_key else base_url
            response = self.client.get(api_url)
            data = response.json()
            if len(data) == 1:
                break
            headers = data[0]
            timestamp_idx = headers.index("timestamp")
            statuscode_idx = headers.index("statuscode")
            digest_idx = headers.index("digest")
            for row in data[1:]:
                if not row:
                    break
                if last_digest and row[digest_idx] == last_digest:
                    continue
                if len(row[statuscode_idx]) != 3 or row[statuscode_idx][0] == "3":
                    continue
                timestamp_str = row[timestamp_idx]
                result.append(self._parse_timestamp(timestamp_str))
                last_digest = row[digest_idx]
            if len(data[-2]) > 0:
                break
            resume_key = data[-1][0]
        return result

    def get(self, url: str, timestamp: datetime) -> str:
        timestamp_str = self._to_timestamp(timestamp)
        encoded_url = urllib.parse.quote(url)
        wayback_url = f"http://web.archive.org/web/{timestamp_str}/{encoded_url}"
        response = self.client.get(wayback_url)
        response.raise_for_status()
        return response.text

    def for_each(self, url: str, timestamps: typing.List[datetime], callback: typing.Callable[[str], None], *args, **kwargs):
        result = []
        for timestamp in timestamps:
            html = self.get(url, timestamp)
            result.append(callback(html, *args, **kwargs))
        return result
