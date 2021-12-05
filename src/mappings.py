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

mappings = {
    "bar": bar_mapping,
    "quote": quote_mapping,
    "trade": trade_mapping
}
