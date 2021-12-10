from __future__ import annotations

import datetime
import json
import logging
from dataclasses import dataclass

import msgpack
import pandas as pd

from src.settings import APP_NAME

logger = logging.getLogger(APP_NAME)


class BaseEntity:
    def __str__(self):
        return json.dumps(self.__dict__, indent=4, sort_keys=True, default=str)

    def to_dict(self):
        return self.__dict__

    @classmethod
    def to_df(cls, data: list[Bar, Trade, Quote]):
        return pd.DataFrame([entry.to_dict() for entry in data])


@dataclass
class Account:
    account_blocked: bool
    account_number: str
    buying_power: float
    cash: float
    created_at: str
    currency: str
    daytrade_count: int
    daytrading_buying_power: float
    equity: float
    id: str
    initial_margin: float
    last_equity: float
    last_maintenance_margin: float
    long_market_value: float
    maintenance_margin: float
    multiplier: str
    pattern_day_trader: bool
    portfolio_value: float
    regt_buying_power: float
    short_market_value: float
    shorting_enabled: bool
    sma: float
    status: str
    trade_suspended_by_user: bool
    trading_blocked: bool
    transfers_blocked: bool
    crypto_status: str
    non_marginable_buying_power: float
    accrued_fees: float
    pending_transfer_in: float


@dataclass
class Order:
    id: str
    client_order_id: str
    created_at: str
    updated_at: str
    submitted_at: str
    filled_at: str
    expired_at: str
    canceled_at: str
    failed_at: str
    replaced_at: str
    replaced_by: str
    replaces: str
    asset_id: str
    symbol: str
    asset_class: str
    notional: float
    qty: float
    filled_qty: float
    filled_avg_price: float
    order_class: str
    order_type: str
    type: str
    side: str
    time_in_force: str
    limit_price: float
    stop_price: float
    status: str
    extended_hours: bool
    legs: str
    trail_percent: float
    trail_price: float
    hwm: float


@dataclass
class Position:
    asset_id: str
    symbol: str
    exchange: str
    asset_class: str
    avg_entry_price: float
    qty: float
    side: str
    market_value: float
    cost_basis: float
    unrealized_pl: float
    unrealized_plpc: float
    unrealized_intraday_pl: float
    unrealized_intraday_plpc: float
    current_price: float
    lastday_price: float
    change_today: float
    asset_marginable: bool = False


class Bar(BaseEntity):
    """
    Bar class for storing OHLCV data.

    Attributes:
        symbol (str): Symbol of the asset.
        timestamp (str): Timestamp of the bar.
        open (float): Open price.
        high (float): High price.
        low (float): Low price.
        close (float): Close price.
        volume (float): Volume.
        num_trades (int): Number of trades.
        vwap (float): Volume Weighted Average Price.

    """

    def __init__(
        self,
        symbol: str,
        t: str,
        o: float,
        h: float,
        l: float,
        c: float,
        v: int,
        n: int,
        vw: float,
        x: str = "",
    ):
        self.type = "bar"
        self.symbol = symbol
        self.timestamp = t
        self.open = o
        self.high = h
        self.low = l
        self.close = c
        self.volume = v
        self.num_trades = n
        self.vwap = vw
        self.exchange = x

        super().__init__()


class Trade(BaseEntity):
    """
    Trade class for storing trade data.

    Attributes:
        symbol (str): Symbol of the asset.
        timestamp (str): Timestamp in RFC-3339 format with nanosecond precision.
        exchange (str): Exchange where the trade happened.
        price (float): Price of the trade.
        size (int): Size of the trade.
        conditions (list): Conditions of the trade.
        id (str): Trade ID.
        tape (str): Trade tape.

    """

    def __init__(
        self, symbol: str, t: str, x: str, p: float, s: int, c: list, i: int, z: str
    ):
        self.type = "trade"
        self.symbol = symbol
        self.timestamp = t
        self.exchange = x
        self.price = p
        self.size = s
        self.conditions = c
        self.id = i
        self.tape = z
        self.exchange = x

        super().__init__()


class Quote(BaseEntity):
    """
    Quote class for storing quote data.

    Attributes:
        symbol (str): Symbol of the asset.
        timestamp (str): Timestamp in RFC-3339 format with nanosecond precision.
        ask_exchange (str): Exchange where the ask happened.
        ask_price (float): Ask price.
        ask_size (int): Ask size.
        bid_exchange (str): Exchange where the bid happened.
        bid_price (float): Bid price.
        bid_size (int): Bid size.
        conditions (list): Conditions of the quote.
        exchange (str): Exchange where the quote happened.

    """

    def __init__(
        self,
        symbol: str,
        t: str,
        ap: float,
        as_: int,
        bp: float,
        bs: int,
        z: str = "",
        bx: str = "",
        ax: str = "",
        x: str = "",
        c: list = None,
    ):
        self.type = "quote"
        self.symbol = symbol
        self.timestamp = t
        self.ask_exchange = ax
        self.ask_price = ap
        self.ask_size = as_
        self.bid_exchange = bx
        self.bid_price = bp
        self.bid_size = bs
        self.conditions = c
        self.tape = z
        self.exchange = x

        super().__init__()


class EntityFactory:
    def __init__(self, entity: dict):
        self.data = self.cast_attributes(entity)
        self.casters = {
            "bars": Bar,
            "trades": Trade,
            "quotes": Quote,
            "orders": Order,
            "positions": Position,
        }

    @property
    def datetime_formats(self):
        return "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f%z"

    def create_entity(self, type: str):
        if type in self.casters:
            try:
                return self.casters[type](**self.data)
            except TypeError:
                logger.warning(self.data)
                return None
        else:
            raise ValueError(f"Entity type {type} not supported")

    def cast_attributes(self, data):
        for key, value in data.items():
            if isinstance(value, str) and ("time" in key or "at" in key):
                for _format in self.datetime_formats:
                    try:
                        data[key] = datetime.datetime.strptime(value, _format)
                        break
                    except ValueError:
                        pass
            if isinstance(value, pd.Timestamp):
                data[key] = value.to_pydatetime()
            if isinstance(value, msgpack.ext.Timestamp):
                data[key] = value.to_datetime()
        return data
