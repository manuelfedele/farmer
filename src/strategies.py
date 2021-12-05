import logging
from typing import Union

import numpy as np
from alpaca_trade_api import REST

from src.helpers import get_historical_data
from src.settings import QUANTITY

logger = logging.getLogger("farmer")


def moving_average_crypto(api: REST, bar: dict) -> Union[dict, None]:
    """
    Moving average strategy.
    Args:
        position: The actual position. At the moment shorting CRYPTO is not supported.
        bar: The bar quote received.
        mean: The moving average.

    Returns:

    """

    positions = api.list_positions()
    if not positions:
        position = None
    else:
        position = positions[0]

    historical_data = get_historical_data(api)
    mean = np.mean([b['close'] for b in historical_data])
    last = bar["close"]

    if not position:
        # We have to buy if condition is met
        if last > mean:
            logger.info(f"Last price is higher than the moving average l:{last} > m:{mean}")
            return {"side": "buy", "price": last, "qty": QUANTITY}
        else:
            logger.debug(
                f"Last price is higher than the moving average "
                f"l:{last} > m:{mean} a position already exists. Doing Nothing")
    else:
        # We have to sell if condition is met
        if last <= mean:
            logger.info(f"Last price is lower than the moving average l:{last} < m:{mean}")
            return {"side": "sell", "price": last, "qty": position["qty"]}
        else:
            logger.debug(
                f"Last price is lower than the moving average "
                f"l:{last} < m:{mean} but no position found. Doing Nothing")
