import dataclasses
import json

import plotext as plt
from alpaca_trade_api.entity import Bar
from alpaca_trade_api.rest import REST, APIError
from alpaca_trade_api.stream import Stream
from tenacity import retry

from src.settings import CONFIG_FILE_PATH, TICKER, WINDOW_SIZE, QUANTITY, BAR_SIZE, SAVE_DATA
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

    def determine_action(self) -> tuple[int, bool]:
        if len(self.bars) < self.window_size:
            logger.warning(f"Not enough bars to calculate moving average")
            return 0, False

        if self.side == 'long':
            # Long position and price has just crossed the moving average going down, we have to sell
            if self.last_quote < self.mean:
                return -self.quantity, False
        elif self.side == 'short':
            # Short position and price has just crossed the moving average going up, we have to buy
            if self.last_quote > self.mean:
                return self.quantity, False
        else:
            # No position, so is the starting point
            if self.last_quote < self.mean:
                return -self.quantity, True
            else:
                return self.quantity, True

        return 0, False

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
            plt.plot(self.rolling_mean, label="Moving Average", marker='dot', color='red')

        plt.sleep(0.001)
        plt.clt()
        plt.show()


class AlgoBot:
    def __init__(
            self,
            stream: Stream,
            api: REST,
            ticker_data: TickerData,
            save_data: bool = SAVE_DATA
    ):

        self.stream = stream
        self.api = api
        self.ticker_data = ticker_data
        self.save_data = save_data

        self.load_data()
        self.update_ticker_data()

        logger.info(self.ticker_data)

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
            self.ticker_data.side = None
            logger.info(f"Could not get position for {self.ticker_data.ticker} from Alpaca")
            return None

    def close_position(self, quantity: int):
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
        logger.info(
            f"{side} {quantity}  of {self.ticker_data.ticker} [Open Operation] because last: {self.ticker_data.last_quote} and mean: {self.ticker_data.mean}"
            f"and side: {self.ticker_data.side} while avg_entry_price: {self.ticker_data.avg_entry_price}")
        self._submit_order(side, quantity)

    async def bar_callback(self, bar: Bar):
        self.ticker_data.last_quote = bar.close
        self.ticker_data.bars.append(bar.close)
        self.ticker_data.bars = self.ticker_data.bars[-self.ticker_data.window_size:]
        self.ticker_data.rolling_mean.append(self.ticker_data.mean)
        self.ticker_data.rolling_mean = self.ticker_data.rolling_mean[-self.ticker_data.window_size:]

        self.update_ticker_data()

        logger.debug(self.ticker_data)

        quantity, first_order = self.ticker_data.determine_action()
        if quantity:
            if not first_order:
                # Close the previous position
                side = 'buy' if quantity < 0 else 'sell'
                self.submit_order(side, abs(quantity))
            # Open the position
            side = 'buy' if quantity > 0 else 'sell'
            self.submit_order(side=side, quantity=abs(quantity))
        else:
            logger.info(
                f"No action to take because last: {self.ticker_data.last_quote} and mean: {self.ticker_data.mean}"
                f"and side: {self.ticker_data.side} while avg_entry_price: {self.ticker_data.avg_entry_price}")

    def load_data(self, path: str = CONFIG_FILE_PATH):
        try:
            _data = json.load(open(path))
            logger.info(f"Loaded config from {path}")
            for key in _data.keys():
                setattr(self.ticker_data, key, _data[key])
        except FileNotFoundError:
            logger.warning(f'Config file not found at {path}')

    def subscribe(self):
        self.stream.subscribe_bars(self.bar_callback, self.ticker_data.ticker, self.ticker_data.bar_size)

    def run(self):
        self.stream.run()
        if self.save_data:
            _data = {
                "bars": self.ticker_data.bars,
                "rolling_mean": self.ticker_data.rolling_mean
            }
            logger.info(f"Saving data to {CONFIG_FILE_PATH}")
            json.dump(_data, open(CONFIG_FILE_PATH, 'w'), indent=4)
        logger.warning('Bye!')
