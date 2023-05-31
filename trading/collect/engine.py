from datetime import datetime, timedelta, timezone
import json
import os
import threading
import time
import typing

from collect.log import CollectLogger
from collect.signal import Signal


class Environment:
    data_path: str
    temp_path: str

    def __init__(self, data_path: str, temp_path: str):
        self.data_path = data_path
        self.temp_path = temp_path

    def get_data_path(self, *args):
        result = os.path.join(self.data_path, *args)
        os.makedirs(os.path.dirname(result), exist_ok=True)
        return result

    def get_temp_path(self, *args):
        result = os.path.join(self.temp_path, *args)
        os.makedirs(os.path.dirname(result), exist_ok=True)
        return result


class BaseCollector:
    env: Environment
    interval: timedelta
    last_run: datetime
    log: CollectLogger
    module: str
    on_run: Signal

    def __init__(self, env: Environment, interval: timedelta):
        self.env = env
        self.interval = interval
        self.log = CollectLogger(self.__class__)
        self.module = type(self).__module__.split(".")[-1]
        self.on_run = Signal()
        self.last_run = datetime.min.replace(tzinfo=timezone.utc)

    def get_data_path(self, *args):
        return self.env.get_data_path(self.module, *args)

    def get_temp_path(self, *args):
        return self.env.get_temp_path(self.module, *args)

    def raise_issue(self, message: str):
        self.log.error(message)

    def run_once(self):
        raise NotImplementedError()

    def run_forever(self):
        while True:
            time_since_last_run = datetime.utcnow().replace(tzinfo=timezone.utc) - self.last_run
            if time_since_last_run < self.interval:
                time.sleep((self.interval - time_since_last_run).total_seconds())
                continue
            self.last_run = datetime.utcnow().replace(tzinfo=timezone.utc)
            self.on_run(self)
            self.run_once()


class BaseStorage:
    collector: BaseCollector
    namespace: str

    def __init__(self, collector: BaseCollector, namespace: str):
        self.collector = collector
        self.namespace = namespace

    def get_data_path(self, *args):
        return self.collector.get_data_path(*args)

    def get_temp_path(self, *args):
        return self.collector.get_temp_path(*args)

    def get_ns_data_path(self, *args):
        return self.get_data_path(self.namespace, *args)
    
    def get_ns_temp_path(self, *args):
        return self.get_temp_path(self.namespace, *args)

    def __find_ns_path(self, template: str):
        start_idx = template.find("<NS>")
        end_ids = start_idx + len("<NS>")
        left = template[:start_idx]
        right = template[end_ids:]
        if right.startswith(os.sep):
            right = right[len(os.sep):]
        for ns in os.listdir(left):
            ns_path = os.path.join(left, ns, right)
            if not os.path.isdir(ns_path):
                continue
            file_path = os.path.join(ns_path, right)
            if os.path.isfile(file_path):
                return file_path

    def find_ns_data_path(self, *args):
        template = self.get_data_path("<NS>", *args)
        return self.__find_ns_path(template)
    
    def find_ns_temp_path(self, *args):
        template = self.get_temp_path("<NS>", *args)
        return self.__find_ns_path(template)


class BaseReader(BaseStorage):
    pass


class BaseWriter(BaseStorage):
    pass


class Executor:
    env: Environment
    collectors: typing.List[BaseCollector]
    threads: typing.Dict[BaseCollector, threading.Thread]
    last_run: typing.Dict[str, datetime]
    last_run_lock: threading.Lock

    def __init__(self, env: Environment):
        self.env = env
        self.collectors = []
        self.threads = {}
        self.last_run_lock = threading.Lock()

        last_run_path = self._last_run_path()
        if os.path.isfile(last_run_path):
            with open(last_run_path, "rt", encoding="utf-8") as fh:
                self.last_run = json.load(fh)
        else:
            self.last_run = {}

    def _last_run_path(self):
        return self.env.get_data_path("last_run")

    def add_collector(self, collector: BaseCollector):
        self.collectors.append(collector)
        collector.on_run.subscribe(self.on_collector_run)
        collector.last_run = self.last_run.get(type(collector).__name__, datetime.min.replace(tzinfo=timezone.utc))

    def on_collector_run(self, collector: BaseCollector):
        with self.last_run_lock:
            self.last_run[type(collector).__name__] = datetime.utcnow().replace(tzinfo=timezone.utc)
            with open(self._last_run_path(), "wt", encoding="utf-8") as fh:
                json.dump(self.last_run, fh, indent=2)

    def run_in_thread(self) -> threading.Thread:
        thread = threading.Thread(target=self.run_forever)
        thread.start()
        return thread

    def run_forever(self):
        for collector in self.collectors:
            thread = threading.Thread(
                target=collector.run_forever,
            )
            thread.start()
            self.threads[collector] = thread
        for collector, thread in self.threads.items():
            thread.join()
