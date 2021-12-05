import logging
from typing import Union

import numpy as np
from alpaca_trade_api import REST

from src.helpers import get_historical_data, get_position
from src.settings import QUANTITY

logger = logging.getLogger("farmer")


def moving_average_crypto(api: REST, bar: dict) -> Union[dict, None]:
    """
    Moving average strategy.
    Args:
        api: The api object.
        bar: The bar quote received.

    Returns:

    """

    position = get_position(api, bar["symbol"])

    historical_data = get_historical_data(api)
    mean = round(np.mean([b['close'] for b in historical_data]), 2)
    last = bar["close"]

    if not position:
        # We have to buy if condition is met
        if last > mean:
            logger.info(f"Last price is higher than the moving average l:{last} > m:{mean}")
            return {"side": "buy", "price": last, "qty": QUANTITY}
        else:
            logger.info(
                f"Last price is lower than the moving average "
                f"l:{last} < m:{mean} and we have no positions. Doing Nothing")
    else:
        # We have to sell if condition is met
        if last <= mean:
            logger.info(f"Last price is lower than the moving average l:{last} < m:{mean}")
            return {"side": "sell", "price": last, "qty": position["qty"]}
        else:
            logger.info(
                f"Last price is above the moving average "
                f"l:{last} > m:{mean} but a position already exists. Doing Nothing")
