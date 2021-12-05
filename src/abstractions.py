import abc


class Ticker(abc.ABC):
    @abc.abstractmethod
    def __init__(self, symbol: str, bar_size: str):
        self.symbol = symbol
        self.bar_size = bar_size


class Stream(abc.ABC):
    @abc.abstractmethod
    def run(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def subscribe_bars(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def subscribe_quotes(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def subscribe_trades(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def subscribe_crypto_trades(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def subscribe_crypto_quotes(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def subscribe_crypto_bars(self, *args, **kwargs):
        pass


class REST(abc.ABC):
    @abc.abstractmethod
    def get_bars(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def get_position(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def submit_order(self, *args, **kwargs):
        pass


class Strategy(abc.ABC):
    @abc.abstractmethod
    def __init__(self, ticker: Ticker, stream: Stream, api: REST):
        self.ticker = ticker
        self.stream = stream
        self.api = api

    @abc.abstractmethod
    async def bar_callback(self, bar):
        pass

    @abc.abstractmethod
    async def quote_callback(self, quote):
        pass

    @abc.abstractmethod
    async def trade_callback(self, quote):
        pass
