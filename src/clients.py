import logging
import threading
from typing import Callable

from alpaca_trade_api import Stream, REST

from src.helpers import map_entity, place_order
from src.settings import BAR_SIZE, CRYPTO_SYMBOLS, q, SYMBOL

logger = logging.getLogger("farmer")


class SubscriberClient:
    def __init__(self, stream: Stream, api: REST, symbol: str = SYMBOL, bar_size: int = BAR_SIZE):
        self.stream = stream
        self.api = api
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
    def __init__(self, api: REST, strategy: Callable, symbol: str = SYMBOL):
        self.api = api
        self.strategy = strategy
        self.symbol = symbol

        self.queue = q

    def start(self):
        logger.info(f"Starting {self.__class__.__name__}")
        threading.Thread(name='Dispatcher', target=self.listen, daemon=True).start()

    def apply_strategy(self, message):
        result = self.strategy(api=self.api, bar=message)
        if result:
            place_order(self.api, **result)

    def process_message(self, message: dict):
        if message["type"] == "bar":
            self.apply_strategy(message)
        else:
            logger.debug(f"Message type {message['type']} not supported.")

    def listen(self):
        while True:
            message = self.queue.get()
            logger.debug(f"Received message {message} [Queue size: {self.queue.qsize()}]")
            self.process_message(message)
            self.queue.task_done()
