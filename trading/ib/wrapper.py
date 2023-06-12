import asyncio
import typing

from ibapi.common import BarData
import ibapi.wrapper


class IBWrapper(ibapi.wrapper.EWrapper):
    _temp: typing.Dict[int, typing.Any]

    def __init__(self, futures: typing.Dict[int, asyncio.Future]):
        self._futures = futures
        self._temp = {}

    def historicalData(self, request_id: int, bar: BarData):
        if request_id not in self._temp:
            self._temp[request_id] = []
        self._temp[request_id].append(bar)
    
    def historicalDataEnd(self, request_id: int, start: str, end: str):
        self._futures[request_id].set_result(self._temp[request_id])
        del self._temp[request_id]

    def logAnswer(self, fnName, fnParams):
        if 'self' in fnParams:
            prms = dict(fnParams)
            del prms['self']
        else:
            prms = fnParams
        print("ANSWER %s %s" % (fnName, prms))