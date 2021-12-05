import json

from src.abstractions import REST, Stream, Strategy
from src.settings import SYMBOL, BAR_SIZE, logger, q, CRYPTO_SYMBOLS


class Ticker:
    def __init__(self, symbol: str = SYMBOL, bar_size: str = BAR_SIZE):
        self.symbol = symbol
        self.bar_size = bar_size

    def __str__(self):
        return json.dumps(self.__dict__, indent=4)

    def __repr__(self):
        return self.__str__()


class Client:
    def __init__(self, stream: Stream, api: REST, strategy: Strategy):
        self.stream = stream
        self.api = api
        self.strategy = strategy

        self.crypto_symbols = CRYPTO_SYMBOLS

    def start(self):
        """
        Starts the client
        Returns:
            None

        """
        logger.info(f"Starting {self.__class__.__name__}")
        if self.strategy.ticker.symbol in self.crypto_symbols:
            # self.stream.subscribe_crypto_trades(
            #     self.strategy.trade_callback, self.strategy.ticker.symbol
            # )
            self.stream.subscribe_crypto_bars(
                self.strategy.bar_callback,
                self.strategy.ticker.symbol,
                self.strategy.ticker.bar_size,
            )
            # self.stream.subscribe_crypto_quotes(
            #     self.strategy.quote_callback, self.strategy.ticker.symbol
            # )
        else:
            self.stream.subscribe_trades(
                self.strategy.trade_callback, self.strategy.ticker.symbol
            )

            self.stream.subscribe_bars(
                self.strategy.bar_callback,
                self.strategy.ticker.symbol,
                self.strategy.ticker.bar_size,
            )
            self.stream.subscribe_quotes(
                self.strategy.quote_callback, self.strategy.ticker.symbol
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


class OrderDispatcher:
    def __init__(self, api: REST):
        self.queue = q
        self.api = api

    @staticmethod
    def place_order(entity):
        pass

    def listen(self):
        while True:
            message = self.queue.get()
            logger.debug(f"Received message {message}")
            self.place_order(message)
            self.queue.task_done()
