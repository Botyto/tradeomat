from datetime import datetime
from enum import Enum

import ibapi
import ibapi.client
import ibapi.contract
import ibapi.wrapper
import random


class IBWrapper(ibapi.wrapper.EWrapper):
    def logAnswer(self, fnName, fnParams):
        if 'self' in fnParams:
            prms = dict(fnParams)
            del prms['self']
        else:
            prms = fnParams
        print("ANSWER %s %s" % (fnName, prms))


class DurationUnit(Enum):
    SECOND = "S"
    DAY = "D"
    WEEK = "W"


class Duration:
    amount: int
    unit: DurationUnit

    def __init__(self, amount: int, unit: DurationUnit):
        self.amount = amount
        self.unit = unit

    def __str__(self):
        return f"{self.amount} {self.unit.value}"


class BarSize(Enum):
    SEC_1 = "1 sec"
    SEC_5 = "5 secs"
    SEC_15 = "15 secs"
    SEC_30 = "30 secs"
    MIN_1 = "1 min"
    MIN_2 = "2 mins"
    MIN_3 = "3 mins"
    MIN_5 = "5 mins"
    MIN_15 = "15 mins"
    MIN_30 = "30 mins"
    HOUR_1 = "1 hour"
    DAY_1 = "1 day"


class HistoricalDataType(Enum):
    TRADES = "TRADES"
    MIDPOINT = "MIDPOINT"
    BID = "BID"
    ASK = "ASK"
    BID_ASK = "BID_ASK"
    HISTORICAL_VOLATILITY = "HISTORICAL_VOLATILITY"
    OPTION_IMPLIED_VOLATILITY = "OPTION_IMPLIED_VOLATILITY"
    SCHEDULE = "SCHEDULE"


class TradingHours(Enum):
    ALL = 0
    REGULAR = 1


class DateFormat(Enum):
    STRING = 1
    UNIX_TIMESTAMP = 2


class IBClient:
    _wrapper: ibapi.wrapper.EWrapper
    _eclient: ibapi.client.EClient
    _request_id: int

    def __init__(self):
        self._wrapper = IBWrapper()
        self._eclient = ibapi.client.EClient(self._wrapper)
        self._request_id = 0

    def connect(self, host: str, port: int, client_id: int):
        return self._eclient.connect(host, port, client_id)
    
    def _next_request_id(self):
        self._request_id += 1
        return self._request_id
    
    def reqHistoricalData(
        self,
        contract: ibapi.contract.Contract,
        end_datetime: datetime|None,
        duration: Duration,
        bar_size: BarSize,
        data_type: HistoricalDataType,
        trading_hours: TradingHours,
        date_format: DateFormat,
        keep_up_to_date: bool):
        reqId = self._next_request_id()
        self._eclient.reqHistoricalData(
            reqId=reqId,
            contract=contract,
            endDateTime=end_datetime or "",
            durationStr=str(duration),
            barSizeSetting=str(bar_size.value),
            whatToShow=str(data_type.value),
            useRTH=trading_hours.value,
            formatDate=date_format.value,
            keepUpToDate=keep_up_to_date,
            chartOptions=ibapi.client.TagValueList())
        return reqId
    
    def run(self):
        return self._eclient.run()

def raw():
    client = IBClient()
    client.connect("localhost", 4001, 0)
    contract = ibapi.contract.Contract()
    contract.symbol = "EUR"
    contract.secType = "CASH"
    contract.currency = "GBP"
    contract.exchange = "IDEALPRO"
    client.reqHistoricalData(
        contract=contract,
        end_datetime=None,
        duration=Duration(1, DurationUnit.DAY),
        bar_size=BarSize.MIN_1,
        data_type=HistoricalDataType.MIDPOINT,
        trading_hours=TradingHours.REGULAR,
        date_format=DateFormat.STRING,
        keep_up_to_date=False)
    client.run()

def ibinsync():
    import ib_insync
    ib = ib_insync.IB()
    ib.connect("localhost", 4001)
    contract = ib_insync.Forex("EURUSD")
    bars = ib.reqHistoricalData(contract, "", "3600 S", "1 min", "MIDPOINT", True)
    print(bars)


raw()
# ibinsync()
