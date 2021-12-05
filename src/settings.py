import logging
import queue
from pathlib import Path

from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import Base

# Generic configuration
BASE_DIR = config("BASE_DIR", default=Path(__file__).resolve().parent.parent)
DATABASE_PATH = config("DATABASE_PATH", default=BASE_DIR / "db.sqlite3")

# Alpaca configuration
APCA_API_KEY_ID = config('APCA_API_KEY_ID')
APCA_API_SECRET_KEY = config('APCA_API_SECRET_KEY')
APCA_API_BASE_URL = config('APCA_API_BASE_URL', default='https://paper-api.alpaca.markets')
DATA_FEED = config('DATA_FEED', default='iex')  # <- replace to SIP if you have PRO subscription

# App configuration
SYMBOL = config("SYMBOL", default="BTCUSD")
BAR_SIZE = config("BAR_SIZE", default="minute")
WINDOW_SIZE = config("WINDOW_SIZE", default=50, cast=int)
QUANTITY = config("QUANTITY", default=1, cast=float)
SAVE_DATA = config("SAVE_DATA", default=False, cast=bool)
ALLOWED_CRYPTO_EXCHANGES = config("ALLOWED_CRYPTO_EXCHANGES", default='CBSE,', cast=lambda x: x.split(','))
CRYPTO_SYMBOLS = config("CRYPTO_SYMBOLS", default='BTCUSD, BCHUSD, ETHUSD, LTCUSD', cast=lambda x: x.split(','))

# Logging configuration
logger = logging.getLogger("farmer")
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '{asctime} - {threadName} - {thread} - {name} - [{filename:>15s}:{lineno:^4d}] - {levelname:^8s} - {message}',
    style='{'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(config('LOG_LEVEL', default='INFO').upper())

# Queue
q = queue.Queue()

# Database
engine = create_engine(f"sqlite:///{DATABASE_PATH}", echo=False, future=True)
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()
Base.metadata.create_all(engine)
