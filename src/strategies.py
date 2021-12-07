import logging
from typing import Union

from alpaca.clients import AlpacaAPI
from alpaca.entities import Bar
from src.helpers import get_historical_data, get_position, get_target_position
from src.settings import ALLOWED_CRYPTO_EXCHANGES, SHORT_MA, LONG_MA

logger = logging.getLogger("farmer")


def cross_moving_average_crypto(
        api: AlpacaAPI,
        bar: Bar,
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
    if bar.exchange not in allowed_crypto_exchanges:
        return

    position = get_position(api)
    target_position_size = get_target_position(api, float(bar.high))

    # Setting exchanges to None to fetch quotes from all exchanges. This is the only way to have a moving average
    # consistent with TradingView (where the strategy has been tested).
    historical_data_df = get_historical_data(api, exchanges=None, df=True)
    short_sma = round(historical_data_df.close.rolling(window=SHORT_MA).mean().iloc[-1], 2)
    long_sma = round(historical_data_df.close.rolling(window=LONG_MA).mean().iloc[-1], 2)

    logger.info(f"\n{historical_data_df.tail().to_string()}")

    if not position:
        # We have to buy if condition is met
        if short_sma > long_sma:
            logger.info(f"Short sma:{short_sma} > Long sma:{long_sma}")
            return {"type": "market", "side": "buy", "qty": target_position_size}
        else:
            logger.info(f"Short sma:{short_sma} < Long sma:{long_sma}. Doing Nothing")
    else:
        # We have to sell if condition is met
        if short_sma <= long_sma:
            logger.info(f"Short sma:{short_sma} < Long sma:{long_sma}")
            return {"type": "trailing_stop", "side": "sell", "qty": position.qty}
        else:
            logger.info(f"Short sma:{short_sma} > Long sma:{long_sma}. Doing Nothing")
