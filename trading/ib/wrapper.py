import asyncio
from decimal import Decimal
import typing

import ibapi.common
import ibapi.contract
import ibapi.wrapper

from ib.stream import Snapshot
from ib.types import ShortableThresholds, TickHaltedType
from ib.types import TickPriceType, TickSizeType, TickGenericType


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
        self._loop.call_soon_threadsafe(self._futures[request_id].set_result, result)

    def __instant_set_error(self, request_id: int, error: Exception):
        future = self._futures.get(request_id)
        if future:
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

    def __get_shortable_threshold(value: float):
        if value > 2.5:
            return ShortableThresholds.AT_LEAST_10000_SHARES
        if value > 1.5:
            return ShortableThresholds.AVAILABLE
        return ShortableThresholds.NOT_AVAILABLE

    def __temp_snapshot_assign(self, snapshot: Snapshot, attr: str, value: typing.Any):
        if getattr(snapshot, attr) is not None:
            # TODO push snapshot
            return
        setattr(snapshot, attr, value)

    def tickPrice(self, request_id: int, tick_type: int, price: float, attrib: ibapi.common.TickAttrib):
        super().tickPrice(request_id, tick_type, price, attrib)
        snapshot: Snapshot = self._temp.get(request_id)
        if snapshot is None:
            snapshot = Snapshot()
            self._temp[request_id] = snapshot
        match TickPriceType(tick_type):
            case TickPriceType.BID_PRICE:
                self.__temp_snapshot_assign(snapshot, "bid_price", Decimal(price))
            case TickPriceType.ASK_PRICE:
                self.__temp_snapshot_assign(snapshot, "ask_price", Decimal(price))

    def tickSize(self, request_id: int, tick_type: int, size: Decimal):
        super().tickSize(request_id, tick_type, size)
        snapshot: Snapshot = self._temp.get(request_id)
        if snapshot is None:
            snapshot = Snapshot()
            self._temp[request_id] = snapshot
        match TickSizeType(tick_type):
            case TickSizeType.LAST_SIZE:
                self.__temp_snapshot_assign(snapshot, "volume", size)
    
    def tickGeneric(self, request_id: int, tick_type: int, value: float):
        super().tickGeneric(request_id, tick_type, value)
        match TickGenericType(tick_type):
            case TickGenericType.SHORTABLE:
                # requires GenericTickType.SHORTABLE
                shortable_level = self.__get_shortable_threshold(value)
            case TickGenericType.HALTED:
                halted = TickHaltedType(int(value))
    
    def tickEFP(self, request_id: int, tick_type: int, basisPoints: float, formatted_basis_points: str, total_dividends: float, hold_days: int, future_last_trade_date: str, dividend_impact: float, dividends_to_last_trade_date: float):
        super().tickEFP(request_id, tick_type, basisPoints, formatted_basis_points, total_dividends, hold_days, future_last_trade_date, dividend_impact, dividends_to_last_trade_date)
    
    def tickOptionComputation(self, request_id: int, tick_type: int, tick_attrib: int, implied_volume: float, delta: float, opt_price: float, pv_dividend: float, gamma: float, vega: float, theta: float, und_price: float):
        super().tickOptionComputation(request_id, tick_type, tick_attrib, implied_volume, delta, opt_price, pv_dividend, gamma, vega, theta, und_price)
    
    def tickString(self, request_id: int, tick_type: int, value: str):
        super().tickString(request_id, tick_type, value)
