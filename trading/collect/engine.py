from datetime import timedelta
import time


class BaseStorage:
    namespace: str

    def __init__(self, namespace: str):
        self.namespace = namespace


class BaseReader(BaseStorage):
    pass


class BaseWriter(BaseStorage):
    pass


class BaseCollector:
    interval: timedelta

    def __init__(self, interval: timedelta):
        self.interval = interval

    def run_once(self):
        raise NotImplementedError()

    def run_forever(self):
        while True:
            self.run_once()
            time.sleep(self.interval.total_seconds())
