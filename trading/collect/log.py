from enum import Enum


class LogLevel(Enum):
    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3


class CollectLogger:
    module: str
    name: str
    level: LogLevel

    def __init__(self, owner: type, level: LogLevel = LogLevel.INFO):
        self.module = owner.__module__.split(".")[-1]
        self.name = owner.__name__
        self.level = level

    def log(self, level: LogLevel, *args):
        if level.value < self.level.value:
            return
        msg = " ".join(str(arg) for arg in args)
        final_msg = f"{level} [{self.module}.{self.name}] {msg}"
        print(final_msg)
        return final_msg

    def print(self, *args):
        return self.log(LogLevel.INFO, *args)

    def debug(self, *args):
        return self.log(LogLevel.DEBUG, *args)

    def info(self, *args):
        return self.log(LogLevel.INFO, *args)

    def warn(self, *args):
        return self.log(LogLevel.WARN, *args)

    def error(self, *args):
        return self.log(LogLevel.ERROR, *args)
    
    def raise_issue(self, *args):
        msg = self.error(*args)
        # TODO store issue somewhere
        return msg
