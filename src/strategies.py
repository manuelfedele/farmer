from src.abstractions import Strategy, REST, Stream
from src.helpers import Ticker
from src.settings import logger


class MovingAverage(Strategy):
    def __init__(self, stream: Stream, api: REST, ticker: Ticker):
        self.stream = stream
        self.api = api
        self.ticker = ticker

    def start(self):
        logger.info(f"Starting {self.__class__.__name__} strategy")
        self.stream.subscribe_bars(self.bar_callback, self.ticker.symbol, self.ticker.bar_size)
        self.stream.run()  # stream.run() is blocking, so stop will be executed after stream.run() returns
        self.stop()

    def stop(self):
        logger.info(f"Stopping {self.__class__.__name__} strategy")

    def execute(self):
        logger.info(f"Executing {self.__class__.__name__} strategy")

    async def bar_callback(self, bar):
        logger.info(bar)

    async def quote_callback(self, quote):
        logger.info(quote)
