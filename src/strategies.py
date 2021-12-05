import logging

import numpy as np
from alpaca_trade_api import TimeFrame, TimeFrameUnit, REST

from src.abstractions import Strategy
from src.mappings import mapper, bar_mapping
from src.models import Bars
from src.settings import q, ALLOWED_CRYPTO_EXCHANGES, session, SYMBOL, BAR_SIZE, QUANTITY, WINDOW_SIZE

logger = logging.getLogger("farmer")


class MovingAverageCrypto(Strategy):
    """
    Moving average strategy.
    """

    def __init__(self, api: REST, symbol: str = SYMBOL, bar_size: int = BAR_SIZE):
        """
        Constructor
        Args:
            api: REST object that provides the REST API interface
            symbol: The symbol to be used
            bar_size: The bar size to be used
        """
        self.api = api
        self.symbol = symbol
        self.bar_size = bar_size
        self.queue = q

        self.get_historical_data()

    def get_position(self):
        positions = self.api.list_positions()
        if not positions:
            return None
        else:
            return positions[0]

    def get_historical_data(self, start=None, end=None):
        bars = self.api.get_crypto_bars_iter(
            symbol=self.symbol,
            timeframe=TimeFrame(1, TimeFrameUnit.Minute),
            start=start,
            end=end
        )
        for bar in bars:
            bar["S"] = self.symbol
            mapped_bar = mapper(bar, bar_mapping)
            _session = session
            if mapped_bar["exchange"] in ALLOWED_CRYPTO_EXCHANGES:
                _session = Bars.get_or_create(_session, **mapped_bar)

            _session.commit()

    def apply_strategy(self, last: float, mean: float):
        """
        Args:
            last: last received price
            mean: the moving average

        Returns:
            None
        """
        position = self.get_position()
        if last > mean:
            if not position:
                logger.info(f"Last price is higher than the moving average l:{last} > m:{mean}")
                self.queue.put({"side": "buy", "price": last, "qty": QUANTITY})
            else:
                logger.info(
                    f"Last price is higher than the moving average "
                    f"l:{last} > m:{mean} a position already exists. Doing Nothing")
        elif last <= mean:
            if position:
                logger.info(f"Last price is lower than the moving average l:{last} < m:{mean}")
                self.queue.put({"side": "sell", "price": last, "qty": position["qty"]})
            else:
                logger.info(
                    f"Last price is lower than the moving average "
                    f"l:{last} < m:{mean} but no position found. Doing Nothing")

    async def bar_callback(self, bar: dict) -> None:
        """
        Callback for the stream.subscribe_bars method, called when a new bar is received
        Args:
            bar: A BarModel object, containing the latest bar

        Returns:
            None
        """
        bar["S"] = self.symbol
        mapped_bar = mapper(bar, bar_mapping)
        _session = session
        if mapped_bar["exchange"] in ALLOWED_CRYPTO_EXCHANGES:
            _session = Bars.get_or_create(_session, **mapped_bar)
            _session.commit()
            last_bars = Bars.get_last(_session, WINDOW_SIZE)
            mean = round(np.mean([b.close for b in last_bars]), 2)
            self.apply_strategy(last_bars[-1].close, mean)

    async def quote_callback(self, quote: dict) -> None:
        """
        Callback for the stream.subscribe_quotes method, called when a new quote is received
        Args:
            quote: A QuoteModel object, containing the latest quote details

        Returns:
            None

        """

        self.queue.put(quote)

    async def trade_callback(self, trade: dict):
        """
        Callback for the stream.subscribe_trades method, called when a new trade is received
        Args:
            trade: A Trade object, containing the latest trade details

        Returns:
            None

        """
        self.queue.put(trade)
