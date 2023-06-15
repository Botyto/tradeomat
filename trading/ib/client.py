import asyncio
from datetime import datetime, timedelta
from enum import Enum
import inspect
import threading
import typing

import ibapi
import ibapi.client
import ibapi.common
import ibapi.contract
import ibapi.wrapper

import ib.stream
import ib.types
import ib.wrapper


class RequestType(Enum):
    EMPTY = 0
    WITH_FUTURE = 1
    WITH_STREAM = 2


class Request:
    _client: "IBClient"
    _type: RequestType
    id: int = None

    def __init__(self, client: "IBClient", type: RequestType):
        self._client = client
        self._type = type

    def __enter__(self):
        if self._type == RequestType.WITH_FUTURE:
            self.id = self._client._new_request_with_future()
        elif self._type == RequestType.WITH_STREAM:
            self.id = self._client._new_request_with_stream()
        else:
            self.id = self._client._new_request()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            return
        awaitable = self.result
        if not inspect.isawaitable(awaitable):
            return
        if self.timeout:
            awaitable = asyncio.wait_for(awaitable, timeout=self.timeout.total_seconds())
        asyncio.get_event_loop().run_until_complete(awaitable)

    @property
    def timeout(self):
        return self._client.timeout

    @property
    def result(self):
        return self._client.results[self.id]


class IBClient:
    loop: asyncio.BaseEventLoop
    results: typing.Dict[int, typing.Any]
    _next_request_id: int
    _wrapper: ib.wrapper.IBWrapper
    _eclient: ibapi.client.EClient
    timeout: timedelta|None = None

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.results = {}
        self._next_request_id = 0
        self._wrapper = ib.wrapper.IBWrapper(self.results, self.loop)
        self._eclient = ibapi.client.EClient(self._wrapper)

    def auto_connnect(self, host: str, client_id: int):
        self._eclient.connect(host, 7497, client_id)

    def connect(self, host: str, port: int, client_id: int):
        self._eclient.connect(host, port, client_id)
        return self._eclient.isConnected()
    
    def autoconnect(self, host: str, client_id: int):
        LIVE_PORTS = [7496, 4002]
        PAPER_PORTS = [7497, 4001]
        for port in LIVE_PORTS + PAPER_PORTS:
            if self.connect(host, port, client_id):
                return True
    
    def _new_request(self):
        request_id = self._next_request_id
        self._next_request_id += 1
        return request_id

    def _new_request_with_future(self):
        request_id = self._new_request()
        future = asyncio.Future(loop=asyncio.get_event_loop())
        self.results[request_id] = future
        return request_id
    
    def _new_request_with_stream(self):
        request_id = self._new_request()
        stream = ib.stream.AsyncStream()
        self.results[request_id] = stream
        return request_id

    def get_historical_data(
        self,
        contract: ibapi.contract.Contract,
        end_datetime: datetime|None,
        duration: ib.types.Duration,
        bar_size: ib.types.BarSize,
        data_type: ib.types.HistoricalDataType,
        trading_hours: ib.types.TradingHours,
        date_format: ib.types.DateFormat,
        keep_up_to_date: bool
    ) -> typing.List[ibapi.common.BarData]:
        with Request(self) as request:
            self._eclient.reqHistoricalData(
                reqId=request.id,
                contract=contract,
                endDateTime=end_datetime.strftime("%Y%m%d-%H:%M:%S") if end_datetime else "",
                durationStr=str(duration),
                barSizeSetting=bar_size.value,
                whatToShow=data_type.value,
                useRTH=trading_hours.value,
                formatDate=date_format.value,
                keepUpToDate=keep_up_to_date,
                chartOptions=ibapi.client.TagValueList())
        return request.result
    
    def get_contract_details(self, contract: ibapi.contract.Contract) -> ibapi.contract.ContractDetails:
        with Request(self, RequestType.WITH_FUTURE) as request:
            self._eclient.reqContractDetails(request.id, contract)
        return request.result

    def serach_symbols(self, pattern: str) -> typing.List[ibapi.contract.ContractDescription]:
        with Request(self, RequestType.WITH_FUTURE) as request:
            self._eclient.reqMatchingSymbols(request.id, pattern)
        return request.result

    def market_data_subscribe(self, contract: ibapi.contract.Contract, generic_ticks: typing.Iterable[ib.types.GenericTickType]|None = None) -> ib.stream.BarStream:
        with Request(self, RequestType.WITH_STREAM) as request:
            generic_ticks_str = ",".join(gtick.value for gtick in generic_ticks) if generic_ticks else ""
            self._eclient.reqMktData(request.id, contract, generic_ticks_str, False, False, ibapi.common.TagValueList())
        return ib.stream.BarStream(request.id, request.result)

    def market_data_unsubscribe(self, stream_id: int):
        stream: ib.stream.AsyncStream = self.results[stream_id]
        self.loop.call_soon_threadsafe(stream.end)
        del self.results[stream_id]
        self._wrapper.tick_subscription_cancelled(stream_id)

    def run(self):
        return self._eclient.run()
    
    def run_in_thread(self):
        thread = threading.Thread(
            target=self.run,
            name="IBClient",
        )
        thread.start()
        return thread
