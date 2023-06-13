import asyncio
from datetime import datetime, timedelta
import threading
import typing

import ibapi
import ibapi.client
import ibapi.common
import ibapi.contract
import ibapi.wrapper

import ib.types
import ib.wrapper


class Request:
    _client: "IBClient"
    id: int = None

    def __init__(self, client: "IBClient"):
        self._client = client

    def __enter__(self):
        self.id = self._client.prep_request()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            return
        awaited_future = self.future
        if self.timeout:
            awaited_future = asyncio.wait_for(awaited_future, timeout=self.timeout.total_seconds())
        asyncio.get_event_loop().run_until_complete(awaited_future)

    @property
    def timeout(self):
        return self._client.timeout

    @property
    def future(self):
        return self._client.futures[self.id]

    @property
    def result(self):
        return self.future.result()


class IBClient:
    _loop: asyncio.BaseEventLoop
    _next_request_id: int
    futures: typing.Dict[int, asyncio.Future]
    _wrapper: ibapi.wrapper.EWrapper
    _eclient: ibapi.client.EClient
    timeout: timedelta|None = None

    def __init__(self):
        self._loop = asyncio.get_event_loop()
        self._next_request_id = 0
        self.futures = {}
        self._wrapper = ib.wrapper.IBWrapper(self.futures, self._loop)
        self._eclient = ibapi.client.EClient(self._wrapper)

    def auto_connnect(self, host: str, client_id: int):
        self._eclient.connect(host, 7497, client_id)

    def connect(self, host: str, port: int, client_id: int):
        return self._eclient.connect(host, port, client_id)
    
    def prep_request(self):
        future = asyncio.Future(loop=asyncio.get_event_loop())
        request_id = self._next_request_id
        self._next_request_id += 1
        self.futures[request_id] = future
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
        with Request(self) as request:
            self._eclient.reqContractDetails(request.id, contract)
        return request.result

    def serach_symbols(self, pattern: str) -> typing.List[ibapi.contract.ContractDescription]:
        with Request(self) as request:
            self._eclient.reqMatchingSymbols(request.id, pattern)
        return request.result

    def run(self):
        return self._eclient.run()
    
    def run_in_thread(self):
        thread = threading.Thread(
            target=self.run,
            name="IBClient",
        )
        thread.start()
        return thread
