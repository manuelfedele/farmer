import logging
import queue
from pathlib import Path

from decouple import config

# Generic configuration
APP_NAME = config("APP_NAME", default="Farmer")
BASE_DIR = config("BASE_DIR", default=Path(__file__).resolve().parent.parent)

# Alpaca configuration
APCA_API_KEY_ID = config("APCA_API_KEY_ID")
APCA_API_SECRET_KEY = config("APCA_API_SECRET_KEY")
APCA_API_BASE_URL = config(
    "APCA_API_BASE_URL", default="https://paper-api.alpaca.markets"
)
DATA_FEED = config(
    "DATA_FEED", default="iex"
)  # <- replace to SIP if you have PRO subscription

# App configuration
SYMBOL = config("SYMBOL", default="BTCUSD")
BAR_SIZE = config("BAR_SIZE", default="minute")

CRYPTO = config("CRYPTO", default=False, cast=bool)
ALLOWED_CRYPTO_EXCHANGES = config(
    "ALLOWED_CRYPTO_EXCHANGES", default="CBSE", cast=lambda x: x.split(",")
)
CRYPTO_SYMBOLS = config(
    "CRYPTO_SYMBOLS",
    default="BTCUSD, BCHUSD, ETHUSD, LTCUSD",
    cast=lambda x: x.split(","),
)

# Logging configuration
logger = logging.getLogger(APP_NAME)
handler = logging.StreamHandler()
formatter = logging.Formatter(
    "{asctime} - {threadName} - {thread:^6d} - {name} - [{filename:>15s}:{lineno:>5d}] - {levelname:^8s} - {message}",
    style="{",
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(config("LOG_LEVEL", default="INFO").upper())

# Queue
q = queue.Queue()
