import datetime

import msgpack.ext

from src.settings import logger

trade_mapping = {
    "i": "id",
    "S": "symbol",
    "c": "conditions",
    "x": "exchange",
    "p": "price",
    "s": "size",
    "t": "timestamp",
    "z": "tape",  # stocks only
    "tks": "takerside"  # crypto only
}

quote_mapping = {
    "S": "symbol",
    "x": "exchange",  # crypto only
    "ax": "ask_exchange",
    "ap": "ask_price",
    "as": "ask_size",
    "bx": "bid_exchange",
    "bp": "bid_price",
    "bs": "bid_size",
    "c": "conditions",  # stocks only
    "t": "timestamp",
    "z": "tape"  # stocks only
}

bar_mapping = {
    "S": "symbol",
    "x": "exchange",  # crypto only
    "o": "open",
    "h": "high",
    "l": "low",
    "c": "close",
    "v": "volume",
    "t": "timestamp",
    "n": "trade_count",
    "vw": "vwap"
}

status_mapping = {
    "S": "symbol",
    "sc": "status_code",
    "sm": "status_message",
    "rc": "reason_code",
    "rm": "reason_message",
    "t": "timestamp",
    "z": "tape"
}

luld_mapping = {
    "S": "symbol",
    "u": "limit_up_price",
    "d": "limit_down_price",
    "i": "indicator",
    "t": "timestamp",
    "z": "tape"
}


def mapper(data: dict, mapping: dict) -> dict:
    """
    Maps a dict to another dict.
    Args:
        mapping:
        data:

    Returns:
        mapped_data:
    """
    _mapped_dict = {}
    for key, value in data.items():
        try:
            _key = mapping[key]

            if isinstance(value, msgpack.ext.Timestamp):
                value = value.to_datetime()

            elif isinstance(value, str) and 'time' in _key.lower():
                try:
                    value = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
                except ValueError:
                    pass
            _mapped_dict[mapping[key]] = value
        except KeyError:
            logger.warning(f"Key {key} not found in mapping.")
    return _mapped_dict
