import pandas as pd
import typing

from zipline.algorithm import TradingAlgorithm
import zipline.assets


class Asset:
    """Base class for entities that can be owned by a trading algorithm."""
    sid: int
    symbol: str
    asset_name: str
    exchange: str
    exchange_full: str
    exchange_info: zipline.assets.ExchangeInfo
    country_code: str
    start_date: pd.Timestamp
    end_date: pd.Timestamp
    tick_size: float
    auto_close_date: pd.Timestamp

    @classmethod
    def from_dict(cls, data: dict) -> "Asset":
        """Build an Asset instance from a dict."""

    def is_alive_for_session(self, session_label: pd.Timestamp) -> bool:
        """Returns whether the asset is alive at the given dt."""

    def is_exchange_open(self, dt_minute: pd.Timestamp) -> bool:
        """Whether the asset's exchange is open at the given minute."""

    def to_dict(self) -> dict:
        """
        Convert to a python dict containing all attributes of the asset.
        This is often useful for debugging.
        """


FieldType = typing.Literal["price"]|typing.Literal["last_traded"]|typing.Literal["open"]|typing.Literal["high"]|typing.Literal["low"]|typing.Literal["close"]|typing.Literal["volume"]
FrequencyType = typing.Literal["1m"]|typing.Literal["1d"]


class BarData:
    """
    Provides methods for accessing minutely and daily price/volume data from Algorithm API functions.
    Also provides utility methods to determine if an asset is alive, and if it has recent trade data.
    """

    @typing.overload
    def can_trade(self, asset: Asset) -> bool:
        """Bool indicating whether the requested asset(s) can be traded in the current minute."""

    @typing.overload
    def can_trade(self, assets: typing.Iterable[Asset]) -> pd.Series:
        """Series of bools indicating whether the requested asset(s) can be traded in the current minute."""

    @typing.overload
    def current(self, asset: Asset, field: FieldType) -> float|pd.Timestamp:
        """
        Returns the "current" value of the given fields for the given assets at the current simulation time.
        The returned value is a scalar (either a float or a pd.Timestamp depending on the field).
        """

    @typing.overload
    def current(self, asset: Asset, fields: typing.Iterable[FieldType]) -> pd.Series:
        """
        Returns the "current" value of the given fields for the given assets at the current simulation time.
        The returned value is a pd.Series whose indices are the requested fields.
        """

    @typing.overload
    def current(self, assets: typing.Iterable[Asset], field: FieldType) -> pd.Series:
        """
        Returns the "current" value of the given fields for the given assets at the current simulation time.
        The returned value is a pd.Series whose indices are the assets.
        """

    @typing.overload
    def current(self, assets: typing.Iterable[Asset], fields: typing.Iterable[FieldType]) -> pd.DataFrame:
        """
        Returns the "current" value of the given fields for the given assets at the current simulation time.
        The returned value is a pd.DataFrame.
        The columns of the returned frame will be the requested fields, and the index of the frame will be the requested assets.
        """

    @typing.overload
    def history(self,
                asset: Asset,
                field: FieldType,
                bar_count: int,
                frequency: FrequencyType,
                ) -> pd.Series:
        """
        Returns a trailing window of length bar_count with data for the given assets, fields, and frequency, adjusted for splits, dividends, and mergers as of the current simulation time.
        The returned value is a pd.Series of length bar_count whose index is pd.DatetimeIndex.
        """
    
    @typing.overload
    def history(self,
                asset: Asset,
                fields: typing.Iterable[FieldType],
                bar_count: int,
                frequency: FrequencyType,
                ) -> pd.DataFrame:
        """
        Returns a trailing window of length bar_count with data for the given assets, fields, and frequency, adjusted for splits, dividends, and mergers as of the current simulation time.
        The returned value is a pd.DataFrame with shape (bar_count, len(fields)).
        The frame's index will be a pd.DatetimeIndex, and its columns will be fields.
        """

    @typing.overload
    def history(self,
                assets: typing.Iterable[Asset],
                field: FieldType,
                bar_count: int,
                frequency: FrequencyType,
                ) -> pd.DataFrame:
        """
        # Returns a trailing window of length bar_count with data for the given assets, fields, and frequency, adjusted for splits, dividends, and mergers as of the current simulation time.    
        # The returned value is a pd.DataFrame with shape (bar_count, len(assets)).
        # The frame's index will be a pd.DatetimeIndex, and its columns will be assets.
        """
    
    @typing.overload
    def history(self,
                assets: Asset|typing.Iterable[Asset],
                fields: FieldType|typing.Iterable[FieldType],
                bar_count: int,
                frequency: FrequencyType,
                ) -> pd.DataFrame:
        """
        Returns a trailing window of length bar_count with data for the given assets, fields, and frequency, adjusted for splits, dividends, and mergers as of the current simulation time.
        The returned value is a pd.DataFrame with a pd.MultiIndex containing pairs of pd.DatetimeIndex and assets,
        while the columns contain the field(s).
        It has shape `(bar_count * len(assets), len(fields))`. The names of the pd.MultiIndex are:
        - `date` if frequency == "1d" or `date_time` if frequency == "1m"
        - asset
        """
    

    def is_stale(self, asset: Asset) -> bool:
        """
        For the given asset or iterable of assets, returns True if the asset is alive and there is no trade data for the current simulation time.
        If the asset has never traded, returns False.
        If the current simulation time is not a valid market time, we use the current time to check if the asset is alive, but we use the last market minute/day for the trade data check.
        """

    def is_stale(self, assets: typing.Iterable[Asset]) -> pd.Series:
        """
        For the given asset or iterable of assets, returns True if the asset is alive and there is no trade data for the current simulation time.
        If the asset has never traded, returns False.
        If the current simulation time is not a valid market time, we use the current time to check if the asset is alive, but we use the last market minute/day for the trade data check.
        """
