from enum import Enum


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
