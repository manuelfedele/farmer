import json
from dataclasses import dataclass

from src.settings import SYMBOL, BAR_SIZE


@dataclass
class Ticker:
    symbol: str = SYMBOL
    bar_size: str = BAR_SIZE

    def __str__(self):
        return json.dumps(self.__dict__, indent=4)

    def __repr__(self):
        return self.__str__()
