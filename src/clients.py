import logging
import threading
from queue import Queue
from typing import Union

from alpaca_trade_api import Stream

from alpaca.clients import AlpacaAPI
from alpaca.entities import Bar, Quote
from src.base import Strategy
from src.settings import q, BAR_SIZE, CRYPTO_SYMBOLS, SYMBOL, ALLOWED_CRYPTO_EXCHANGES

logger = logging.getLogger("farmer")


class PublisherClient:
    """
    PublisherClient is a class that subscribes to the Alpaca stream API and then pushes messages to the queue so that
    the Dispatcher can process them sequentially.
    """

    def __init__(
        self,
        stream: Stream,
        symbol: str = SYMBOL,
        bar_size: str = BAR_SIZE,
        crypto_symbols: list = CRYPTO_SYMBOLS,
        queue: Queue = q,
    ):
        self.stream = stream
        self.symbol = symbol
        self.bar_size = bar_size
        self.crypto_symbols = crypto_symbols

        self.queue = queue

    def start(self):
        """
        Starts the client subscribing to the streams
        Returns:
            None

        """
        logger.info(f"Starting {self.__class__.__name__}")
        if self.symbol in self.crypto_symbols:
            logger.info(
                f"Subscribing data for {self.symbol} ({ALLOWED_CRYPTO_EXCHANGES})"
            )
            self.stream.subscribe_crypto_trades(self.trade_callback, self.symbol)
            self.stream.subscribe_crypto_bars(
                self.bar_callback,
                self.symbol,
                self.bar_size,
            )
            self.stream.subscribe_crypto_quotes(self.quote_callback, self.symbol)
        else:
            self.stream.subscribe_trades(self.trade_callback, self.symbol)

            self.stream.subscribe_bars(
                self.bar_callback,
                self.symbol,
                self.bar_size,
            )
            self.stream.subscribe_quotes(self.quote_callback, self.symbol)

        self.stream.run()  # stream.run() is blocking, so stop will be executed after stream.run() returns
        self.stop()

    def stop(self) -> None:
        """
        Stops the client
        Returns:
            None
        """
        logger.info(f"Stopping {self.__class__.__name__}")

    @staticmethod
    def clean_message(message):
        message.pop("T")
        message["symbol"] = message.pop("S")
        if "as" in message.keys():
            message["as_"] = message.pop("as")
        return message

    async def bar_callback(self, bar: dict) -> None:
        """
        Callback for the stream.subscribe_bars method, called when a new bar is received
        Args:
            bar: A dict object, containing the latest bar details

        Returns:
            None
        """

        logger.debug(f"Received bar: {bar}")
        bar = self.clean_message(bar)

        self.queue.put(Bar(**bar))

    async def quote_callback(self, quote: dict) -> None:
        """
        Callback for the stream.subscribe_quotes method, called when a new quote is received
        Args:
            quote: A dict object, containing the latest quote details

        Returns:
            None

        """
        logger.debug(f"Received quote: {quote}")
        quote = self.clean_message(quote)

        # self.queue.put(Quote(**quote))

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


class SubscriberClient:
    """
    Class that handles the order dispatching in synchronous way
    """

    def __init__(
        self,
        api: AlpacaAPI,
        strategy: Strategy,
        symbol: str = SYMBOL,
        crypto: bool = False,
        queue: Queue = q,
    ):
        self.api = api
        self.strategy = strategy

        self.symbol = symbol
        self.crypto = crypto

        self.queue = queue

    def start(self):
        logger.info(f"Starting {self.__class__.__name__}")
        threading.Thread(name="Dispatcher", target=self.listen, daemon=True).start()

    def process_entity(self, entity: Union[Bar, Quote]):
        if isinstance(entity, Bar):
            self.strategy.apply(entity)
        else:
            logger.debug(f"Message type {type(entity)} not supported.")

    def listen(self):
        while True:
            message = self.queue.get()
            logger.debug(
                f"Received message {message} [Queue size: {self.queue.qsize()}]"
            )
            self.process_entity(message)
            self.queue.task_done()
