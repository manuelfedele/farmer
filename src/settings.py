import logging
from pathlib import Path

from decouple import config

# Generic configuration
BASE_DIR = config("BASE_DIR", default=Path(__file__).resolve().parent.parent)
CONFIG_FILE_PATH = config("CONFIG_FILE_PATH", default=BASE_DIR / "config.json")

# Alpaca configuration
APCA_API_KEY_ID = config('APCA_API_KEY_ID')
APCA_API_SECRET_KEY = config('APCA_API_SECRET_KEY')
APCA_API_BASE_URL = config('APCA_API_BASE_URL', default='https://paper-api.alpaca.markets')
DATA_FEED = config('DATA_FEED', default='iex')  # <- replace to SIP if you have PRO subscription

# App configuration
SYMBOL = config("SYMBOL", default="AAPL")
BAR_SIZE = config("BAR_SIZE", default="minute")
WINDOW_SIZE = config("WINDOW_SIZE", default=50, cast=int)
QUANTITY = config("QUANTITY", default=100, cast=int)
SAVE_DATA = config("SAVE_DATA", default=False, cast=bool)

# Logging configuration
logger = logging.getLogger("farmer")
handler = logging.StreamHandler()
formatter = logging.Formatter('{asctime} - {name} - {lineno:^4d} - {levelname:^8s} - {message}', style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
