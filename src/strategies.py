import logging
from typing import Union

import numpy as np
from alpaca_trade_api import REST

from src.helpers import get_historical_data, get_position, get_target_position
from src.settings import ALLOWED_CRYPTO_EXCHANGES, SHORT_MA, LONG_MA

logger = logging.getLogger("farmer")


def cross_moving_average_crypto(
        api: REST,
        bar: dict,
        allowed_crypto_exchanges: list = ALLOWED_CRYPTO_EXCHANGES
) -> Union[dict, None]:
    """
    Moving average strategy.
    Args:
        api: The api object.
        bar: The bar quote received.
        allowed_crypto_exchanges: The list of allowed crypto exchanges.
    Returns:

    """
    if bar["exchange"] not in allowed_crypto_exchanges:
        return

    position = get_position(api)

    historical_data = get_historical_data(api)
    short_ma = round(np.mean([b['close'] for b in historical_data[-SHORT_MA:]]), 2)
    long_ma = round(np.mean([b['close'] for b in historical_data[-LONG_MA:]]), 2)

    if not position:
        # We have to buy if condition is met
        if short_ma > long_ma:
            target_position_size = get_target_position(api, float(bar["high"]))

            logger.info(f"Target position size: {target_position_size}")

            logger.info(f"Last price is higher than the moving average sma:{short_ma} > lma:{long_ma}")
            return {"side": "buy", "qty": target_position_size}
        else:
            logger.info(
                f"Last price is lower than the moving average "
                f"sma:{short_ma} < lma:{long_ma} and we have no positions. Doing Nothing")
    else:
        # We have to sell if condition is met
        if short_ma <= long_ma:
            logger.info(f"Last price is lower than the moving average sma:{short_ma} < lma:{long_ma}")
            return {"side": "sell", "qty": position["qty"]}
        else:
            logger.info(
                f"Last price is above the moving average "
                f"sma:{short_ma} > lma:{long_ma} but a position already exists. Doing Nothing")
