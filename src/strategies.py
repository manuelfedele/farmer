import logging
from typing import Union

from src.settings import QUANTITY

logger = logging.getLogger("farmer")


def moving_average_crypto(position: dict, quote: dict, mean: float) -> Union[dict, None]:
    """
    Moving average strategy.
    Args:
        position: The actual position. At the moment shorting CRYPTO is not supported.
        quote: The last quote received.
        mean: The moving average.

    Returns:

    """
    if not position:
        # We have to buy if condition is met
        last = quote["ask_price"]
        if last > mean:
            logger.info(f"Last price is higher than the moving average l:{last} > m:{mean}")
            return {"side": "buy", "price": last, "qty": QUANTITY}
        else:
            logger.debug(
                f"Last price is higher than the moving average "
                f"l:{last} > m:{mean} a position already exists. Doing Nothing")
    else:
        # We have to sell if condition is met
        last = quote["bid_price"]
        if last <= mean:
            logger.info(f"Last price is lower than the moving average l:{last} < m:{mean}")
            return {"side": "sell", "price": last, "qty": position["qty"]}
        else:
            logger.debug(
                f"Last price is lower than the moving average "
                f"l:{last} < m:{mean} but no position found. Doing Nothing")
