import datetime
import logging
from typing import Union

import pandas as pd

from alpaca.clients import AlpacaAPI
from alpaca.entities import Order, Bar, Position
from src.settings import SYMBOL, ALLOWED_CRYPTO_EXCHANGES, APCA_API_KEY_ID, APCA_API_SECRET_KEY

logger = logging.getLogger("farmer")


def get_historical_data(
        api: AlpacaAPI,
        symbol: str = SYMBOL,
        timeframe="1Min",
        exchanges: list = ALLOWED_CRYPTO_EXCHANGES,
        df: bool = False
) -> Union[list[Bar], pd.DataFrame]:
    """
    Retrieves historical data from the API
    Args:
        api: The API to use
        symbol: The symbol to retrieve data for
        timeframe: The timeframe to retrieve data for
        exchanges: The exchanges to retrieve data for
        df: Whether to return a pandas dataframe

    Returns:
        The retrieved data

    """

    bars = api.get_crypto_bars(
        symbol=symbol,
        timeframe=timeframe,
        exchanges=exchanges,
    )
    if not df:
        return bars
    else:
        return Bar.to_df(bars)


def place_order(
        api: AlpacaAPI,
        symbol: str = SYMBOL,
        **kwargs
) -> Union[Order, None]:
    """
    Places an order on the API
    Args:
        api: The API to use
        symbol: The symbol to place the order for

    Returns:
        The order ID

    """
    try:
        logger.info(f"Placing {kwargs.get('type')} order {kwargs.get('side')} {kwargs.get('qty')} on {symbol}")
        return api.place_order(
            symbol=symbol,
            **kwargs
        )
    except Exception as e:
        logger.error(f"Error while placing order: {e}")


def get_position(
        api: AlpacaAPI,
        symbol: str = SYMBOL
) -> Union[Position, None]:
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


if __name__ == '__main__':
    if __name__ == '__main__':
        c = AlpacaAPI(key_id=APCA_API_KEY_ID, secret_key=APCA_API_SECRET_KEY)
        df = get_historical_data(c, SYMBOL, timeframe="1Min", exchanges=ALLOWED_CRYPTO_EXCHANGES, df=True)
        df['sma15'] = df['close'].rolling(window=15).mean()
        df['sma50'] = df['close'].rolling(window=60).mean()
        df['sma200'] = df['close'].rolling(window=200).mean()
        signal = (df['sma15'] > df['sma50']).iloc[-1]
        print(signal)
