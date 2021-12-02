import dataclasses
import json

import plotext as plt
from alpaca_trade_api.entity import Bar
from alpaca_trade_api.rest import REST, APIError
from alpaca_trade_api.stream import Stream
from tenacity import retry

from src.settings import CONFIG_FILE_PATH, TICKER, WINDOW_SIZE, QUANTITY, BAR_SIZE, SAVE_CONFIG
from src.settings import logger


@dataclasses.dataclass
class TickerData:
    side: str = None
    ticker: str = TICKER
    bar_size: str = BAR_SIZE
    avg_entry_price: float = 0.0
    last_quote: float = 0.0
    window_size: int = WINDOW_SIZE
    quantity: int = QUANTITY
    bars: list = dataclasses.field(default_factory=list)
    rolling_mean: list = dataclasses.field(default_factory=list)

    def __str__(self):
        return json.dumps(self.__dict__, indent=4)

    def __repr__(self):
        return self.__str__()

    @property
    def mean(self):
        try:
            return round(sum(self.bars) / len(self.bars), 2)
        except ZeroDivisionError:
            return 0

    def determine_action(self):
        if len(self.bars) < self.window_size:
            logger.warning(f"Not enough bars to calculate moving average")
            return None, 0, False

        quantity = abs(self.quantity)
        if not self.side:
            if self.mean > self.last_quote:
                return "buy", quantity, True
            elif self.mean < self.last_quote:
                return "sell", quantity, True
        elif self.last_quote <= self.mean and self.side == 'long':
            return "sell", quantity, False
        elif self.last_quote >= self.mean and self.side == 'short':
            return "buy", quantity, False
        else:
            return None, 0, False

    def plot(self):
        plt.clp()
        plt.clc()
        plt.cld()
        plt.xticks([x for x in range(1, len(self.bars))])

        plt.plot(self.bars, xside="lower", yside="right", label="Quotes", marker='dot', color='blue')
        if self.avg_entry_price:
            avg_entry_price = [self.avg_entry_price for _ in range(len(self.bars))]
            plt.plot(avg_entry_price, label="Entry Price", marker='-', color='green')

        if len(self.rolling_mean) >= self.window_size:
            plt.plot(self.rolling_mean, xside="upper", yside="left", label="Moving Average", marker='dot', color='red')

        plt.sleep(0.001)
        plt.clt()
        plt.show()


class AlgoBot:
    def __init__(
            self,
            stream: Stream,
            api: REST,
            ticker_data: TickerData,
            save_config: bool = SAVE_CONFIG
    ):

        self.stream = stream
        self.api = api
        self.ticker_data = ticker_data
        self.save_config = save_config

        self.load_config()
        self.update_ticker_data()

        logger.debug(self.ticker_data)
        self.ticker_data.plot()

    def update_ticker_data(self):
        try:
            logger.info(f"Trying to fetch position from Alpaca for {self.ticker_data.ticker}")
            position = self.api.get_position(self.ticker_data.ticker)
            self.ticker_data.quantity = int(position.qty)
            self.ticker_data.side = position.side
            self.ticker_data.avg_entry_price = float(position.avg_entry_price)
            logger.info("Got position from Alpaca")
            return position
        except APIError:
            logger.warning(f"Could not get position for {self.ticker_data.ticker} from Alpaca")
            return None

    def close_position(self, quantity: int):
        quantity = abs(quantity)
        side = 'buy' if quantity < 0 else 'sell'
        logger.info(f"{side} {quantity} shares of {self.ticker_data.ticker} [Close Operation]")
        self._submit_order(side=side, quantity=quantity)

    @retry
    def _submit_order(self, side: str, quantity: int):
        self.api.submit_order(
            symbol=self.ticker_data.ticker,
            side=side,
            qty=quantity,
            type='market',
            time_in_force='day',
        )

    def submit_order(self, side: str, quantity: int):
        logger.info(f"{side} {quantity}  of {self.ticker_data.ticker} [Open Operation]")
        self._submit_order(side, quantity)

    async def bar_callback(self, bar: Bar):
        self.ticker_data.last_quote = bar.close
        self.ticker_data.bars.append(bar.close)
        self.ticker_data.bars = self.ticker_data.bars[-self.ticker_data.window_size:]
        self.ticker_data.rolling_mean.append(self.ticker_data.mean)
        self.ticker_data.rolling_mean = self.ticker_data.rolling_mean[-self.ticker_data.window_size:]

        self.update_ticker_data()
        self.ticker_data.plot()

        logger.debug(self.ticker_data)

        side, quantity, first_order = self.ticker_data.determine_action()
        if side:
            if not first_order:
                self.close_position(quantity)
            self.submit_order(side=side, quantity=quantity)
        else:
            logger.info("No action to take")

    def load_config(self, path: str = CONFIG_FILE_PATH):
        try:
            config_dict = json.load(open(path))
            logger.info(f"Loaded config from {path}")
            for key in config_dict.keys():
                setattr(self.ticker_data, key, config_dict[key])
        except FileNotFoundError:
            logger.warning(f'Config file not found at {path}')

    def subscribe(self):
        self.stream.subscribe_bars(self.bar_callback, self.ticker_data.ticker, self.ticker_data.bar_size)

    def run(self):
        self.stream.run()
        if self.save_config:
            logger.info(f"Saving config to {CONFIG_FILE_PATH}")
            json.dump(self.ticker_data.__dict__, open(CONFIG_FILE_PATH, 'w'), indent=4)
        logger.warning('Bye!')
