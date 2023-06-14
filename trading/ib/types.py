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


class TickType(Enum):
    BID_SIZE = 0  # Number of contracts or lots offered at the bid price.
    BID_PRICE = 1  # Highest priced bid for the contract.
    ASK_PRICE = 2  # Lowest price offer on the contract.
    ASK_SIZE = 3  # Number of contracts or lots offered at the ask price.
    LAST_PRICE = 4  # Last price at which the contract traded (does not include some trades in RTVolume).
    LAST_SIZE = 5  # Number of contracts or lots traded at the last price.
    HIGH = 6  # High price for the day.
    LOW = 7  # Low price for the day.
    VOLUME = 8  # Trading volume for the day for the selected contract (US Stocks: multiplier 100).
    CLOSE_PRICE = 9  # The last available closing price for the previous day. For US Equities, we use corporate action processing to get the closing price, so the close price is adjusted to reflect forward and reverse splits and cash and stock dividends. 
    BID_OPTION_COMPUTATION = 10  # Computed Greeks and implied volatility based on the underlying stock price and the option bid price. See Option Greeks
    ASK_OPTION_COMPUTATION = 11  # Computed Greeks and implied volatility based on the underlying stock price and the option ask price. See Option Greeks
    LAST_OPTION_COMPUTATION = 12  # Computed Greeks and implied volatility based on the underlying stock price and the option last traded price. See Option Greeks
    MODEL_OPTION_COMPUTATION = 13  # Computed Greeks and implied volatility based on the underlying stock price and the option model price. Correspond to greeks shown in TWS. See Option Greeks
    OPEN_TICK = 14  # Current session's opening price. Before open will refer to previous day. The official opening price requires a market data subscription to the native exchange of the instrument.
    LOW_13_WEEKS = 15  # Lowest price for the last 13 weeks. For stocks only.
    HIGH_13_WEEKS = 16  # Highest price for the last 13 weeks. For stocks only.
    LOW_26_WEEKS = 17  # Lowest price for the last 26 weeks. For stocks only.
    HIGH_26_WEEKS = 18  # Highest price for the last 26 weeks. For stocks only.
    LOW_52_WEEKS = 19  # Lowest price for the last 52 weeks. For stocks only.
    HIGH_52_WEEKS = 20  # Highest price for the last 52 weeks. For stocks only.
    AVERAGE_VOLUME = 21  # The average daily trading volume over 90 days. Multiplier of 100. For stocks only.
    OPEN_INTEREST = 22  # (Deprecated, not currently in use) Total number of options that are not closed.
    OPTION_HISTORICAL_VOLATILITY = 23  # The 30-day historical volatility (currently for stocks).
    OPTION_IMPLIED_VOLATILITY = 24  # A prediction of how volatile an underlying will be in the future. The IB 30-day volatility is the at-market volatility estimated for a maturity thirty calendar days forward of the current trading day, and is based on option prices from two consecutive expiration months.
    OPTION_BID_EXCHANGE = 25  # Not Used.
    OPTION_ASK_EXCHANGE = 26  # Not Used.
    OPTION_CALL_OPEN_INTEREST = 27  # Call option open interest.
    OPTION_PUT_OPEN_INTEREST = 28  # Put option open interest.
    OPTION_CALL_VOLUME = 29  # Call option volume for the trading day.
    OPTION_PUT_VOLUME = 30  # Put option volume for the trading day.
    INDEX_FUTURE_PREMIUM = 31  # The number of points that the index is over the cash index.
    BID_EXCHANGE = 32  # For stock and options, identifies the exchange(s) posting the bid price. See Component Exchanges
    ASK_EXCHANGE = 33  # For stock and options, identifies the exchange(s) posting the ask price. See Component Exchanges
    AUCTION_VOLUME = 34  # The number of shares that would trade if no new orders were received and the auction were held now.
    AUCTION_PRICE = 35  # The price at which the auction would occur if no new orders were received and the auction were held now- the indicative price for the auction. Typically received after Auction imbalance (tick type 36)
    AUCTION_IMBALANCE = 36  # The number of unmatched shares for the next auction; returns how many more shares are on one side of the auction than the other. Typically received after Auction Volume (tick type 34)
    MARK_PRICE = 37  # The mark price is the current theoretical calculated value of an instrument. Since it is a calculated value, it will typically have many digits of precision.
    BID_EFP_COMPUTATION = 38  # Computed EFP bid price
    ASK_EFP_COMPUTATION = 39  # Computed EFP ask price
    LAST_EFP_COMPUTATION = 40  # Computed EFP last price
    OPEN_EFP_COMPUTATION = 41  # Computed EFP open price
    HIGH_EFP_COMPUTATION = 42  # Computed high EFP traded price for the day
    LOW_EFP_COMPUTATION = 43  # Computed low EFP traded price for the day
    CLOSE_EFP_COMPUTATION = 44  # Computed closing EFP price for previous day
    LAST_TIMESTAMP = 45  # Time of the last trade (in UNIX time).
    SHORTABLE = 46  # Describes the level of difficulty with which the contract can be sold short. See Shortable
    RT_VOLUME_TIME_AND_SALES = 48  # Last trade details (Including both "Last" and "Unreportable Last" trades). See RT Volume
    HALTED = 49  # Indicates if a contract is halted. See Halted
    BID_YIELD = 50  # Implied yield of the bond if it is purchased at the current bid.
    ASK_YIELD = 51  # Implied yield of the bond if it is purchased at the current ask.
    LAST_YIELD = 52  # Implied yield of the bond if it is purchased at the last price.
    CUSTOM_OPTION_COMPUTATION = 53  # Greek values are based off a user customized price.
    TRADE_COUNT = 54  # Trade count for the day.
    TRADE_RATE = 55  # Trade count per minute.
    VOLUME_RATE = 56  # Volume per minute.
    LAST_RTH_TRADE = 57  # Last Regular Trading Hours traded price.
    RT_HISTORICAL_VOLATILITY = 58  # 30-day real time historical volatility.
    IB_DIVIDENDS = 59  # Contract's dividends. See IB Dividends.
    BOND_FACTOR_MULTIPLIER = 60  # The bond factor is a number that indicates the ratio of the current bond principal to the original principal
    REGULATORY_IMBALANCE = 61  # The imbalance that is used to determine which at-the-open or at-the-close orders can be entered following the publishing of the regulatory imbalance.
    NEWS = 62  # Contract's news feed.
    SHORT_TERM_VOLUME_3_MINUTES = 63  # The past three minutes volume. Interpolation may be applied. For stocks only.
    SHORT_TERM_VOLUME_5_MINUTES = 64  # The past five minutes volume. Interpolation may be applied. For stocks only.
    SHORT_TERM_VOLUME_10_MINUTES = 65  # The past ten minutes volume. Interpolation may be applied. For stocks only.
    DELAYED_BID = 66  # Delayed bid price. See Market Data Types.
    DELAYED_ASK = 67  # Delayed ask price. See Market Data Types.
    DELAYED_LAST = 68  # Delayed last traded price. See Market Data Types.
    DELAYED_BID_SIZE = 69  # Delayed bid size. See Market Data Types.
    DELAYED_ASK_SIZE = 70  # Delayed ask size. See Market Data Types.
    DELAYED_LAST_SIZE = 71  # Delayed last size. See Market Data Types.
    DELAYED_HIGH_PRICE = 72  # Delayed highest price of the day. See Market Data Types.
    DELAYED_LOW_PRICE = 73  # Delayed lowest price of the day. See Market Data Types
    DELAYED_VOLUME = 74  # Delayed traded volume of the day. See Market Data Types
    DELAYED_CLOSE = 75  # The prior day's closing price.
    DELAYED_OPEN = 76  # Not currently available
    RT_TRADE_VOLUME = 77  # Last trade details that excludes "Unreportable Trades". See RT Trade Volume
    CREDITMAN_MARK_PRICE = 78  # Not currently available
    CREDITMAN_SLOW_MARK_PRICE = 79  # Slower mark price update used in system calculations
    DELAYED_BID_OPTION = 80  # Computed greeks based on delayed bid price. See Market Data Types and Option Greeks.
    DELAYED_ASK_OPTION = 81  # Computed greeks based on delayed ask price. See Market Data Types and Option Greeks.
    DELAYED_LAST_OPTION = 82  # Computed greeks based on delayed last price. See Market Data Types and Option Greeks.
    DELAYED_MODEL_OPTION = 83  # Computed Greeks and model's implied volatility based on delayed stock and option prices.
    LAST_EXCHANGE = 84  # Exchange of last traded price
    LAST_REGULATORY_TIME = 85  # Timestamp (in Unix ms time) of last trade returned with regulatory snapshot
    FUTURES_OPEN_INTEREST = 86  # Total number of outstanding futures contracts (TWS v965+). *HSI open interest requested with generic tick 101
    AVERAGE_OPTION_VOLUME = 87  # Average volume of the corresponding option contracts(TWS Build 970+ is required)
    DELAYED_LAST_TIMESTAMP = 88  # Delayed time of the last trade (in UNIX time) (TWS Build 970+ is required)
    SHORTABLE_SHARES = 89  # Number of shares available to short (TWS Build 974+ is required)
    ETF_NAV_CLOSE = 92  # Today's closing price of ETF's Net Asset Value (NAV). Calculation is based on prices of ETF's underlying securities.
    ETF_NAV_PRIOR_CLOSE = 93  # Yesterday's closing price of ETF's Net Asset Value (NAV). Calculation is based on prices of ETF's underlying securities.
    ETF_NAV_BID = 94  # The bid price of ETF's Net Asset Value (NAV). Calculation is based on prices of ETF's underlying securities.
    ETF_NAV_ASK = 95  # The ask price of ETF's Net Asset Value (NAV). Calculation is based on prices of ETF's underlying securities.
    ETF_NAV_LAST = 96  # The last price of Net Asset Value (NAV). For ETFs: Calculation is based on prices of ETF's underlying securities. For NextShares: Value is provided by NASDAQ
    ETF_NAV_FROZEN_LAST = 97  # ETF Nav Last for Frozen data
    ETF_NAV_HIGH = 98  # The high price of ETF's Net Asset Value (NAV)
    ETF_NAV_LOW = 99  # The low price of ETF's Net Asset Value (NAV)
    ESTIMATED_IPO_MIDPOINT = 101  # Midpoint is calculated based on IPO price range
    FINAL_IPO_PRICE = 102  # Final price for IPO
