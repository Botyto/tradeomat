from decimal import Decimal


class Snapshot:
    bid_price: Decimal|None = None
    ask_price: Decimal|None = None
    volume: Decimal|None = None


class MarketDataStream:
    pass
