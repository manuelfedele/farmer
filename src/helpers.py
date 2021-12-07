import datetime
import logging

import msgpack
from alpaca_trade_api import REST, TimeFrame, TimeFrameUnit

from src.mappings import mappings
from src.settings import SYMBOL, ALLOWED_CRYPTO_EXCHANGES, QUANTITY

logger = logging.getLogger("farmer")


def map_entity(
        symbol: str,
        data: dict,
        type: str
) -> dict:
    """
    Maps the received entity to the corresponding mapping
    Args:
        symbol: the symbol of the entity
        data: The entity to be mapped
        type: The type of entity

    Returns:
        The mapped entity

    """
    data['S'] = symbol
    mapping = mappings[type]
    _mapped_dict = {}
    for key, value in data.items():
        try:
            _key = mapping[key]

            if isinstance(value, msgpack.ext.Timestamp):
                value = value.to_datetime()

            elif isinstance(value, str) and 'time' in _key.lower():
                try:
                    value = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
                except ValueError:
                    pass
            _mapped_dict[mapping[key]] = value
        except KeyError:
            logger.debug(f"Key {key} not found in mapping.")
    return _mapped_dict


def get_historical_data(
        api: REST,
        symbol: str = SYMBOL,
        timeframe=TimeFrame(1, TimeFrameUnit.Minute),
        exchanges: list = ALLOWED_CRYPTO_EXCHANGES,
) -> list:
    """
    Retrieves historical data from the API
    Args:
        api: The API to use
        symbol: The symbol to retrieve data for
        timeframe: The timeframe to retrieve data for
        exchanges: The exchanges to retrieve data for

    Returns:
        The retrieved data

    """

    bars = api.get_crypto_bars_iter(
        symbol=symbol,
        timeframe=timeframe,
        exchanges=exchanges,
    )
    bars = [map_entity(symbol, bar, "bar") for bar in bars]

    return bars


def place_order(
        api: REST,
        symbol: str = SYMBOL,
        **kwargs
) -> int:
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
        return api.submit_order(
            symbol=symbol,
            **kwargs
        )
    except Exception as e:
        logger.error(f"Error while placing order: {e}")


def replace_order(
        api: REST,
        order_id: str,
        **kwargs
):
    try:
        logger.info(f"Replacing order {order_id} with {kwargs.get('qty')}")
        return api.replace_order(
            order_id=order_id,
            **kwargs
        )
    except Exception as e:
        logger.error(f"Error while replacing order: {e}")


def get_position(
        api: REST,
        symbol: str = SYMBOL
) -> dict:
    """
    Retrieves the current position of the symbol
    Args:
        api: The API to use
        symbol: The symbol to retrieve the position for

    Returns:
        The retrieved position
    """
    try:
        return api.get_position(symbol)
    except Exception as e:
        logger.debug(e)
        return None


def get_order(api: REST):
    try:
        return api.list_orders()[0]
    except Exception as e:
        logger.debug(e)
        return None


def get_target_position(
        api: REST,
        last_price: float,
):
    cash = float(api.get_account()["cash"])

    target_position_size = cash / last_price * 0.8
    return round(target_position_size, 2)
