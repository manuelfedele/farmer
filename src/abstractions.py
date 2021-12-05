import abc
from queue import Queue

from alpaca_trade_api import REST


class Strategy(abc.ABC):
    symbol: str
    bar_size: int
    api: REST
    queue: Queue

    @abc.abstractmethod
    async def bar_callback(self, bar):
        pass

    @abc.abstractmethod
    async def quote_callback(self, quote):
        pass

    @abc.abstractmethod
    async def trade_callback(self, trade):
        pass
