import asyncio
import typing

import ibapi.common
import ibapi.contract
import ibapi.wrapper


class IBError(Exception):
    code: int
    advanced_order_reject_json: str

    def __init__(self, code: int, message: str, advanced_order_reject_json: str):
        super().__init__(message)
        self.code = code
        self.advanced_order_reject_json = advanced_order_reject_json


class IBWrapper(ibapi.wrapper.EWrapper):
    _loop: asyncio.BaseEventLoop
    _temp: typing.Dict[int, typing.Any]

    def __init__(self, futures: typing.Dict[int, asyncio.Future], loop: asyncio.BaseEventLoop):
        self._loop = loop
        self._futures = futures
        self._temp = {}

    def __temp_list_append(self, request_id: int, item: typing.Any):
        temp_list = self._temp.get(request_id)
        if temp_list is None:
            self._temp[request_id] = [item]
        else:
            temp_list.append(item)

    def __temp_set_result(self, request_id: int):
        self.__instant_set_result(request_id, self._temp[request_id])
        del self._temp[request_id]

    def __instant_set_result(self, request_id: int, result: typing.Any):
        self._loop.call_soon_threadsafe(self._futures[request_id].set_result, result)

    def __instant_set_error(self, request_id: int, error: Exception):
        self._loop.call_soon_threadsafe(self._futures[request_id].set_exception, error)

    def error(self, request_id: int, code: int, message: str, advanced_order_reject_json: str = ""):
        super().error(request_id, code, message, advanced_order_reject_json)
        if request_id != -1 and request_id in self._futures:
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

    def bondContractDetails(self, reqId: int, contractDetails: ibapi.contract.ContractDetails):
        super().bondContractDetails(reqId, contractDetails)
        self.__instant_set_result(reqId, contractDetails)

    def symbolSamples(self, reqId: int, contractDescriptions: typing.List[ibapi.contract.ContractDescription]):
        super().symbolSamples(reqId, contractDescriptions)
        self.__instant_set_result(reqId, contractDescriptions)
