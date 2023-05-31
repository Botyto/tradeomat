import typing
from typing import Any


class Signal:
    observers: typing.List[typing.Callable]

    def __init__(self):
        self.observers = []

    def subscribe(self, observer: typing.Callable):
        self.observers.append(observer)

    def unsubscribe(self, observer: typing.Callable):
        self.observers.remove(observer)

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        for observer in self.observers:
            observer(*args, **kwds)
