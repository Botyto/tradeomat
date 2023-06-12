import asyncio
from datetime import datetime
import threading
import typing

import ibapi
import ibapi.client
import ibapi.contract
import ibapi.wrapper

import ib.types
import ib.wrapper


class IBClient:
    _request_id: int
    _futures: typing.Dict[int, asyncio.Future]
    _wrapper: ibapi.wrapper.EWrapper
    _eclient: ibapi.client.EClient

    def __init__(self):
        self._request_id = 0
        self._futures = {}
        self._wrapper = ib.wrapper.IBWrapper(self._futures)
        self._eclient = ibapi.client.EClient(self._wrapper)

    def connect(self, host: str, port: int, client_id: int):
        return self._eclient.connect(host, port, client_id)
    
    def _next_request_id(self):
        self._request_id += 1
        return self._request_id
    
    def _next_future(self):
        future = asyncio.Future(loop=asyncio.get_event_loop())
        request_id = self._next_request_id()
        self._futures[request_id] = future
        return request_id, future

    def reqHistoricalData(
        self,
        contract: ibapi.contract.Contract,
        end_datetime: datetime|None,
        duration: ib.types.Duration,
        bar_size: ib.types.BarSize,
        data_type: ib.types.HistoricalDataType,
        trading_hours: ib.types.TradingHours,
        date_format: ib.types.DateFormat,
        keep_up_to_date: bool
    ):
        request_id, future = self._next_future()
        self._eclient.reqHistoricalData(
            reqId=request_id,
            contract=contract,
            endDateTime=end_datetime or "",
            durationStr=str(duration),
            barSizeSetting=str(bar_size.value),
            whatToShow=str(data_type.value),
            useRTH=trading_hours.value,
            formatDate=date_format.value,
            keepUpToDate=keep_up_to_date,
            chartOptions=ibapi.client.TagValueList())
        # future = asyncio.ensure_future(asyncio.wait_for(future))
        result = asyncio.get_event_loop().run_until_complete(future)
        return result
    
    def run(self):
        return self._eclient.run()
    
    def run_in_thread(self):
        thread = threading.Thread(
            target=self.run,
            name="IBClient",
        )
        thread.start()
        return thread
