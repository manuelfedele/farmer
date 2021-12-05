from alpaca_trade_api import Stream, REST

from src.abstractions import Strategy
from src.settings import SYMBOL, logger, q, CRYPTO_SYMBOLS, QUANTITY


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
        if self.strategy.symbol in self.crypto_symbols:
            # self.stream.subscribe_crypto_trades(
            #     self.strategy.trade_callback, self.strategy.ticker.symbol
            # )
            self.stream.subscribe_crypto_bars(
                self.strategy.bar_callback,
                self.strategy.symbol,
                self.strategy.bar_size,
            )
            # self.stream.subscribe_crypto_quotes(
            #     self.strategy.quote_callback, self.strategy.ticker.symbol
            # )
        else:
            self.stream.subscribe_trades(
                self.strategy.trade_callback, self.strategy.symbol
            )

            self.stream.subscribe_bars(
                self.strategy.bar_callback,
                self.strategy.symbol,
                self.strategy.bar_size,
            )
            self.stream.subscribe_quotes(
                self.strategy.quote_callback, self.strategy.symbol
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

    def place_order(self, side: str = "buy", qty: int = QUANTITY, price: float = 0.0):
        try:
            self.api.submit_order(
                symbol=SYMBOL,
                side=side,
                type='market',
                qty=qty,
                time_in_force='day',
            )
        except Exception as e:
            logger.error(f"Error while placing order: {e}")

    def listen(self):
        while True:
            message = self.queue.get()
            logger.debug(f"Received message {message}")
            self.place_order(**message)
            self.queue.task_done()
