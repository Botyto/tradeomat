import asyncio
from datetime import datetime
from decimal import Decimal
import typing

import ibapi.common
import ibapi.contract
import ibapi.wrapper

from ib.stream import Bar, AsyncStream
from ib.types import TickPriceType, TickSizeType


class IBError(Exception):
    code: int
    advanced_order_reject_json: str

    def __init__(self, code: int, message: str, advanced_order_reject_json: str):
        super().__init__(message)
        self.code = code
        self.advanced_order_reject_json = advanced_order_reject_json


class IBWrapper(ibapi.wrapper.EWrapper):
    _loop: asyncio.BaseEventLoop
    _results: typing.Dict[int, typing.Any]
    _temp: typing.Dict[int, typing.Any]

    def __init__(self, results: typing.Dict[int, typing.Any], loop: asyncio.BaseEventLoop):
        self._loop = loop
        self._results = results
        self._temp = {}

    def __temp_list_append(self, request_id: int, item: typing.Any):
        temp_list: list = self._temp.get(request_id)
        if temp_list is None:
            self._temp[request_id] = [item]
        else:
            assert isinstance(temp_list, list), "Expected a list in _temp"
            temp_list.append(item)

    def __temp_set_result(self, request_id: int):
        self.__instant_set_result(request_id, self._temp[request_id])
        del self._temp[request_id]

    def __instant_set_result(self, request_id: int, result: typing.Any):
        future: asyncio.Future = self._results.get(request_id)
        self._loop.call_soon_threadsafe(future.set_result, result)

    def __instant_set_error(self, request_id: int, error: Exception):
        future: asyncio.Future = self._results.get(request_id)
        if future is None:
            return
        self._loop.call_soon_threadsafe(future.set_exception, error)

    def error(self, request_id: int, code: int, message: str, advanced_order_reject_json: str = ""):
        super().error(request_id, code, message, advanced_order_reject_json)
        if request_id != -1:
            self.__instant_set_error(request_id, IBError(code, message, advanced_order_reject_json))

    def historicalData(self, request_id: int, bar: ibapi.common.BarData):
        super().historicalData(request_id, bar)
        self.__temp_list_append(request_id, bar)
    
    def historicalDataEnd(self, request_id: int, start: str, end: str):
        super().historicalDataEnd(request_id, start, end)
        self.__temp_set_result(request_id)

    def contractDetails(self, request_id: int, contract_details: ibapi.contract.ContractDetails):
        super().contractDetails(request_id, contract_details)
        self.__instant_set_result(request_id, contract_details)

    def bondContractDetails(self, request_id: int, contractDetails: ibapi.contract.ContractDetails):
        super().bondContractDetails(request_id, contractDetails)
        self.__instant_set_result(request_id, contractDetails)

    def symbolSamples(self, request_id: int, contractDescriptions: typing.List[ibapi.contract.ContractDescription]):
        super().symbolSamples(request_id, contractDescriptions)
        self.__instant_set_result(request_id, contractDescriptions)

    def __tick_get_bar(self, request_id: int):
        bar: Bar = self._temp.get(request_id)
        if bar is None:
            bar = Bar()
            self._temp[request_id] = bar
        return bar

    def __tick_push_bar(self, request_id: int):
        bar: Bar = self._temp.get(request_id)
        if bar is None:
            return
        stream: AsyncStream = self._results[request_id]
        self._loop.call_soon_threadsafe(stream.push, bar)
        new_bar = Bar()
        new_bar.open = bar.close
        self._temp[request_id] = new_bar

    def tick_subscription_cancelled(self, request_id: int):
        del self._temp[request_id]

    def tickPrice(self, request_id: int, tick_type: int, price: float, attrib: ibapi.common.TickAttrib):
        super().tickPrice(request_id, tick_type, price, attrib)
        bar = self.__tick_get_bar(request_id)
        current_time = datetime.utcnow().replace(second=0, microsecond=0)
        if current_time > bar.datetime:
            self.__tick_push_bar(request_id)
        print(TickPriceType(tick_type))
        match TickPriceType(tick_type):
            case TickPriceType.LAST_PRICE:
                bar.close = Decimal(price)
                if bar.open is None:
                    bar.open = Decimal(price)
                    bar.high = Decimal(price)
                    bar.low = Decimal(price)
                else:
                    bar.high = max(bar.high, Decimal(price))
                    bar.low = min(bar.low, Decimal(price))

    def tickSize(self, request_id: int, tick_type: int, size: Decimal):
        super().tickSize(request_id, tick_type, size)
        bar = self.__tick_get_bar(request_id)
        match TickSizeType(tick_type):
            case TickSizeType.LAST_SIZE:
                bar.volume += size
