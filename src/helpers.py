import logging
from typing import Union

import pandas as pd

from alpaca.clients import AlpacaAPI
from alpaca.entities import Order, Bar, Position
from src.settings import SYMBOL, APP_NAME

logger = logging.getLogger(APP_NAME)


def get_historical_data(
    api: AlpacaAPI,
    symbol: str = SYMBOL,
    timeframe="1Min",
    exchanges: list = None,
    df: bool = False,
    crypto: bool = False,
) -> Union[list[Bar], pd.DataFrame]:
    """
    Retrieves historical data from the API
    Args:
        api: The API to use
        symbol: The symbol to retrieve data for
        timeframe: The timeframe to retrieve data for
        exchanges: The exchanges to retrieve data for
        df: Whether to return a pandas dataframe
        crypto: Whether to return crypto data
    Returns:
        The retrieved data

    """

    bars = api.get_bars(
        symbol=symbol, timeframe=timeframe, exchanges=exchanges, crypto=crypto
    )
    if not df:
        return bars
    else:
        return Bar.to_df(bars)


def get_position(api: AlpacaAPI, symbol: str = SYMBOL) -> Union[Position, None]:
    """
    Retrieves the current position of the symbol
    Args:
        api: The API to use
        symbol: The symbol to retrieve the position for

    Returns:
        The retrieved position
    """
    try:
        return api.get_positions(symbol)
    except Exception as e:
        logger.debug(e)
        return None


def get_order(api: AlpacaAPI) -> Union[Order, None]:
    try:
        return api.get_orders()[0]
    except Exception as e:
        logger.debug(e)
        return None


def get_target_position(
    api: AlpacaAPI,
    last_price: float,
) -> float:
    cash = float(api.account.cash)

    target_position_size = cash / last_price * 0.8
    return round(target_position_size, 2)
