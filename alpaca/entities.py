from dataclasses import dataclass


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
