import logging
import threading
from typing import Callable

import numpy as np
from alpaca_trade_api import Stream, REST, TimeFrame, TimeFrameUnit

from src.helpers import map_entity
from src.models import Bars, Quotes, Base
from src.settings import Session, BAR_SIZE, CRYPTO_SYMBOLS, q, ALLOWED_CRYPTO_EXCHANGES, WINDOW_SIZE, SYMBOL, QUANTITY

logger = logging.getLogger("farmer")


class SubscriberClient:
    def __init__(self, stream: Stream, api: REST, session: Session, symbol: str = SYMBOL, bar_size: int = BAR_SIZE):
        self.stream = stream
        self.api = api
        self.session = session
        self.symbol = symbol
        self.bar_size = bar_size
        self.queue = q

        self.crypto_symbols = CRYPTO_SYMBOLS

    def start(self):
        """
        Starts the client subscribing to the streams
        Returns:
            None

        """
        logger.info(f"Starting {self.__class__.__name__}")
        if self.symbol in self.crypto_symbols:
            self.stream.subscribe_crypto_trades(
                self.trade_callback, self.symbol
            )
            self.stream.subscribe_crypto_bars(
                self.bar_callback,
                self.symbol,
                self.bar_size,
            )
            self.stream.subscribe_crypto_quotes(
                self.quote_callback, self.symbol
            )
        else:
            self.stream.subscribe_trades(
                self.trade_callback, self.symbol
            )

            self.stream.subscribe_bars(
                self.bar_callback,
                self.symbol,
                self.bar_size,
            )
            self.stream.subscribe_quotes(
                self.quote_callback, self.symbol
            )

        self.stream.run()  # stream.run() is blocking, so stop will be executed after stream.run() returns
        self.stop()

    def stop(self) -> None:
        """
        Stops the client
        Returns:
            None
        """
        logger.info(f"Stopping {self.__class__.__name__}")

    async def bar_callback(self, bar: dict) -> None:
        """
        Callback for the stream.subscribe_bars method, called when a new bar is received
        Args:
            bar: A dict object, containing the latest bar details

        Returns:
            None
        """

        bar = map_entity(self.symbol, bar, "bar")
        logger.debug(f"Received bar: {bar}")
        self.queue.put({**bar, "type": "bar"})

    async def quote_callback(self, quote: dict) -> None:
        """
        Callback for the stream.subscribe_quotes method, called when a new quote is received
        Args:
            quote: A dict object, containing the latest quote details

        Returns:
            None

        """
        quote = map_entity(self.symbol, quote, "quote")
        logger.debug(f"Received quote: {quote}")
        self.queue.put({**quote, "type": "quote"})

    async def trade_callback(self, trade: dict):
        """
        Callback for the stream.subscribe_trades method, called when a new trade is received
        Args:
            trade: A dict object, containing the latest trade details

        Returns:
            None

        """
        # self.queue.put(trade)
        pass


class OrderDispatcher:
    def __init__(self, api: REST, session: Session, strategy: Callable, symbol: str = SYMBOL, bar_size: str = BAR_SIZE):
        self.api = api
        self.session = session
        self.strategy = strategy
        self.symbol = symbol
        self.bar_size = bar_size

        self.queue = q
        self.position = self.get_position()
        self.get_historical_data()

    def start(self):
        logger.info(f"Starting {self.__class__.__name__}")
        threading.Thread(name='Dispatcher', target=self.listen, daemon=True).start()

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
            bar = map_entity(self.symbol, bar, "bar")

            if bar["exchange"] in ALLOWED_CRYPTO_EXCHANGES:
                self.session = Bars.get_or_create(self.session, **bar)

            self.session.commit()

    def place_order(self, side: str = "buy", qty: int = QUANTITY, price: float = 0.0):
        try:
            logger.info(f"Placing order {side} {qty} {price} on {SYMBOL}")
            self.api.submit_order(
                symbol=self.symbol,
                side=side,
                type='market',
                qty=qty,
                time_in_force='day',
            )
        except Exception as e:
            logger.error(f"Error while placing order: {e}")

    def apply_strategy(self, message):
        mean = np.mean([b.close for b in Bars.get_last(self.session, WINDOW_SIZE)])
        result = self.strategy(position=self.position, bar=message, mean=mean)
        if result:
            self.place_order(**result)
            self.position = self.get_position()

    def save(self, message: dict, model: Base):
        message.pop('type')
        if message["exchange"] in ALLOWED_CRYPTO_EXCHANGES:
            model.get_or_create(self.session, **message)
            self.session.commit()

    def process_message(self, message: dict):
        if message["type"] == "bar":
            self.save(message, Bars)
            mean = np.mean([b.close for b in Bars.get_last(self.session, WINDOW_SIZE)])
            logger.info(
                f"Received bar: {message['symbol']}: {message['close']} (mean: {mean})")
            Quotes.delete_old_entries(self.session)
            self.apply_strategy(message)

        else:
            logger.debug(f"Message type {message['type']} not supported.")

    def listen(self):
        while True:
            message = self.queue.get()
            logger.debug(f"Received message {message} [Queue size: {self.queue.qsize()}]")
            self.process_message(message)
            self.queue.task_done()
