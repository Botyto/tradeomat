from ibapi.contract import Contract

def __make_contract(**kwargs):
    contract = Contract()
    for k, v in kwargs.items():
        setattr(contract, k, v)
    return contract

def forex(symbol: str, currency: str, exchange: str = "IDEALPRO", **kwargs) -> Contract:
    return __make_contract(
        symbol=symbol,
        sec_type="CASH",
        currency=currency,
        exchange=exchange,
        **kwargs,
    )

def crypto(symbol: str, currency: str, exchange: str, **kwargs) -> Contract:
    return __make_contract(
        symbol=symbol,
        sec_type="CRYPTO",
        currency=currency,
        exchange=exchange,
        **kwargs,
    )

def stock(symbol: str, currency: str, primary_exchange: str = "", **kwargs) -> Contract:
    return __make_contract(
        symbol=symbol,
        sec_type="STK",
        currency=currency,
        exchange="SMART",
        primary_exchange=primary_exchange,
        **kwargs,
    )

def index(symbol: str, currency: str) -> Contract:
    return __make_contract(
        symbol=symbol,
        sec_type="IND",
        currency=currency,
        exchange="EUREX",
    )

def cdf(symbol: str, currency: str, exchange: str, **kwargs) -> Contract:
    return __make_contract(
        symbol=symbol,
        sec_type="CFD",
        currency=currency,
        exchange=exchange,
        **kwargs,
    )

def commodity(symbol: str, currency: str, exchange: str, **kwargs) -> Contract:
    return __make_contract(
        symbol=symbol,
        sec_type="CMDTY",
        currency=currency,
        exchange=exchange,
        **kwargs,
    )
