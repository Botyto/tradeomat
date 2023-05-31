from datetime import timedelta
import os
import time

from collect.log import CollectLogger


class Environment:
    data_path: str
    temp_path: str

    def __init__(self, data_path: str, temp_path: str):
        self.data_path = data_path
        self.temp_path = temp_path

    def get_data_path(self, *args):
        return os.path.join(self.data_path, *args)

    def get_temp_path(self, *args):
        return os.path.join(self.temp_path, *args)


class BaseCollector:
    env: Environment
    interval: timedelta
    log: CollectLogger
    module: str

    def __init__(self, env: Environment, interval: timedelta):
        self.env = env
        self.interval = interval
        self.log = CollectLogger(self.__class__)
        self.module = type(self).__module__.split(".")[-1]

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
            self.run_once()
            time.sleep(self.interval.total_seconds())


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
