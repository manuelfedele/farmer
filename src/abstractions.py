import abc


class Ticker(abc.ABC):
    pass


class Stream(abc.ABC):
    @abc.abstractmethod
    def run(self, *args, **kwargs):
        pass

    @abc.abstractmethod
    def subscribe_bars(self, *args, **kwargs):
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
    def __init__(self, ticker: Ticker, stream: Stream, api: REST, *args, **kwargs):
        pass

    @abc.abstractmethod
    def start(self):
        pass

    @abc.abstractmethod
    def stop(self):
        pass

    @abc.abstractmethod
    def execute(self):
        pass

    @abc.abstractmethod
    async def bar_callback(self, bar):
        pass

    @abc.abstractmethod
    async def quote_callback(self, quote):
        pass
