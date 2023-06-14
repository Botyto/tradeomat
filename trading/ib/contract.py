import typing

from ibapi.contract import Contract, ComboLeg

def __make_contract(
    con_id: int = 0,
    symbol: str = "",
    sec_type: str = "",
    last_traded_date_or_contract_month: str = "",
    strike: float = 0.0,
    right: str = "",
    multiplier: str = "",
    exchange: str = "",
    primary_exchange: str = "",
    currency: str = "",
    local_symbol: str = "",
    trading_class: str = "",
    include_expired: bool = False,
    sec_id_type: str = "",	  # CUSIP;SEDOL;ISIN;RIC
    sec_id: str = "",
    description: str = "",
    issuer_id: str = "",
    combo_legs_description: str = "",
    combo_legs: typing.List[ComboLeg]|None = None,
    delta_neutral_contract = None,
):
    contract = Contract()
    contract.conId = con_id
    contract.symbol = symbol
    contract.secType = sec_type
    contract.lastTradeDateOrContractMonth = last_traded_date_or_contract_month
    contract.strike = strike
    contract.right = right
    contract.multiplier = multiplier
    contract.exchange = exchange
    assert primary_exchange != "SMART", "Primary exchange cannot be 'SMART'"
    contract.primaryExchange = primary_exchange
    contract.currency = currency
    contract.localSymbol = local_symbol
    contract.tradingClass = trading_class
    contract.includeExpired = include_expired
    contract.secIdType = sec_id_type
    contract.secId = sec_id
    contract.description = description
    contract.issuerId = issuer_id
    contract.comboLegsDescrip = combo_legs_description
    contract.comboLegs = combo_legs
    contract.deltaNeutralContract = delta_neutral_contract
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
