import logging

from alpaca.clients import AlpacaAPI
from alpaca.entities import Bar
from src.base import Strategy
from src.helpers import get_historical_data, get_position, get_target_position
from src.settings import APP_NAME

logger = logging.getLogger(APP_NAME)


class CrossMovingAverage(Strategy):
    def __init__(
        self,
        api: AlpacaAPI,
        symbol: str,
        short_window: int = 15,
        long_window: int = 50,
        crypto: bool = False,
        allowed_crypto_exchanges: list = None,
    ):
        self.api = api
        self.symbol = symbol
        self.short_window = short_window
        self.long_window = long_window
        self.symbol = symbol
        self.crypto = crypto
        self.allowed_crypto_exchanges = allowed_crypto_exchanges
        self.inhibit_trading = False

    @property
    def historical_data(self):
        df = get_historical_data(
            api=self.api,
            symbol=self.symbol,
            crypto=self.crypto,
            df=True,
            exchanges=self.allowed_crypto_exchanges,
        )
        df["short_ma"] = df["close"].rolling(self.short_window).mean()
        df["long_ma"] = df["close"].rolling(self.long_window).mean()
        return df

    @property
    def position(self):
        return get_position(self.api, self.symbol)

    def target_position(self, actual_price: float):
        return get_target_position(self.api, actual_price)

    def apply(self, bar: Bar):
        if self.crypto and bar.exchange not in self.allowed_crypto_exchanges:
            return

        position = self.position
        historical_df = self.historical_data

        short_sma = round(historical_df.short_ma.iloc[-1], 2)
        long_sma = round(historical_df.long_ma.iloc[-1], 2)

        logger.info(f"Short SMA: {short_sma}")
        logger.info(f"Long SMA: {long_sma}")
        logger.info(f"Trend: {'↑' if short_sma > long_sma else '↓'}")

        if not position:
            # We have to buy if condition is met
            if short_sma > long_sma:
                order = self.api.place_order(
                    bar.symbol,
                    side="buy",
                    type="market",
                    qty=self.target_position(bar.high),
                )
                logger.info(f"Placed order: {order}")
        else:
            # We have to sell if condition is met
            if short_sma <= long_sma:
                order = self.api.place_order(
                    bar.symbol, qty=position.qty, side="sell", type="market"
                )
                logger.info(f"Placed order: {order}")
            else:
                logger.info(f"Actual Position: {position.unrealized_pl}$")
