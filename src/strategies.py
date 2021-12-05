import numpy as np
from alpaca_trade_api import TimeFrame, TimeFrameUnit, REST

from src.abstractions import Strategy
from src.helpers import Ticker
from src.mappings import mapper, bar_mapping
from src.models import Bars
from src.settings import q, ALLOWED_CRYPTO_EXCHANGES, session, logger


class MovingAverage(Strategy):
    """
    Moving average strategy.
    """

    def __init__(self, api: REST, ticker: Ticker):
        """
        Constructor
        Args:
            api: REST object that provides the REST API interface
            ticker: Ticker object that provides the ticker data
        """
        self.api = api
        self.ticker = ticker
        self.queue = q

        self.get_historical_data()

    def get_historical_data(self):
        bars = self.api.get_crypto_bars_iter(
            self.ticker.symbol, TimeFrame(1, TimeFrameUnit.Minute)
        )
        for bar in bars:
            bar["S"] = self.ticker.symbol
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
        if last > mean:
            logger.info(f"Last price {last} is higher than the moving average {mean}")
        else:
            logger.info(f"Last price {last} is lower than the moving average {mean}")
        self.queue.put(last)

    async def bar_callback(self, bar: dict) -> None:
        """
        Callback for the stream.subscribe_bars method, called when a new bar is received
        Args:
            bar: A BarModel object, containing the latest bar

        Returns:
            None
        """
        bar["S"] = self.ticker.symbol
        mapped_bar = mapper(bar, bar_mapping)
        _session = session
        if mapped_bar["exchange"] in ALLOWED_CRYPTO_EXCHANGES:
            _session = Bars.get_or_create(_session, **mapped_bar)

        _session.commit()
        last_bars = Bars.get_last(_session, 50)
        self.apply_strategy(last_bars[-1].close, np.mean([b.close for b in last_bars]))

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
