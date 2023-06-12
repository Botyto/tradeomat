import asyncio
import typing

from ibapi.common import BarData
import ibapi.wrapper


class IBWrapper(ibapi.wrapper.EWrapper):
    _loop: asyncio.BaseEventLoop
    _temp: typing.Dict[int, typing.Any]

    def __init__(self, futures: typing.Dict[int, asyncio.Future], loop: asyncio.BaseEventLoop):
        self._loop = loop
        self._futures = futures
        self._temp = {}

    def _temp_list_append(self, request_id: int, item: typing.Any):
        if request_id not in self._temp:
            self._temp[request_id] = []
        self._temp[request_id].append(item)

    def _set_result_from_temp(self, request_id: int):
        self._loop.call_soon_threadsafe(self._futures[request_id].set_result, self._temp[request_id])
        del self._temp[request_id]

    def historicalData(self, request_id: int, bar: BarData):
        self._temp_list_append(request_id, bar)
    
    def historicalDataEnd(self, request_id: int, start: str, end: str):
        self._set_result_from_temp(request_id)

    def logAnswer(self, fnName, fnParams):
        if 'self' in fnParams:
            params = dict(fnParams)
            del params['self']
        else:
            params = fnParams
        print("ANSWER %s %s" % (fnName, params))
