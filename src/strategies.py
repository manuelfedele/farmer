import logging
from typing import Union

from alpaca.clients import AlpacaAPI
from alpaca.entities import Bar
from src.helpers import get_historical_data, get_position, get_target_position

logger = logging.getLogger("farmer")


def cross_moving_average(
    api: AlpacaAPI,
    bar: Bar,
    crypto: bool = False,
    allowed_crypto_exchanges: list = None,
) -> Union[dict, None]:
    """
    Moving average strategy.
    Args:
        api: The api object.
        bar: The bar quote received.
        crypto: If the asset is crypto.
        allowed_crypto_exchanges: The list of allowed crypto exchanges.
    Returns:

    """
    if crypto and bar.exchange not in allowed_crypto_exchanges:
        return

    position = get_position(api)
    target_position_size = get_target_position(api, float(bar.high))

    historical_data_df = get_historical_data(api, df=True, crypto=crypto)
    short_sma = round(historical_data_df.close.rolling(window=15).mean().iloc[-1], 2)
    long_sma = round(historical_data_df.close.rolling(window=50).mean().iloc[-1], 2)

    if not position:
        # We have to buy if condition is met
        if short_sma > long_sma:
            logger.info(f"Short sma:{short_sma} > Long sma:{long_sma}")
            order = api.place_order(
                bar.symbol, side="buy", type="market", qty=target_position_size
            )
            logger.info(f"Placed order: {order}")
        else:
            logger.info(f"Short sma:{short_sma} < Long sma:{long_sma}. Doing Nothing")
    else:
        # We have to sell if condition is met
        if short_sma <= long_sma:
            logger.info(f"Short sma:{short_sma} < Long sma:{long_sma}")
            order = api.place_order(
                bar.symbol, qty=position.qty, side="sell", type="market"
            )
            logger.info(f"Placed order: {order}")
        else:
            logger.info(f"Short sma:{short_sma} > Long sma:{long_sma}")
            logger.info(f"Actual Position: {position}")
