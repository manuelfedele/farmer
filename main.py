import os

from alpaca_trade_api import Stream

from alpaca.clients import AlpacaAPI
from src.clients import PublisherClient, SubscriberClient
from src.settings import (
    APCA_API_KEY_ID,
    APCA_API_SECRET_KEY,
    APCA_API_BASE_URL,
    DATA_FEED,
    CRYPTO,
    SYMBOL,
    ALLOWED_CRYPTO_EXCHANGES,
)
from src.strategies import CrossMovingAverage

os.environ.setdefault("APCA_API_KEY_ID", APCA_API_KEY_ID)
os.environ.setdefault("APCA_API_SECRET_KEY", APCA_API_SECRET_KEY)
os.environ.setdefault("APCA_API_BASE_URL", APCA_API_BASE_URL)

if __name__ == "__main__":
    # These are Alpaca's interfaces for streaming and REST API
    stream = Stream(data_feed=DATA_FEED, raw_data=True)
    api = AlpacaAPI()

    strategy = CrossMovingAverage(
        api=api,
        symbol=SYMBOL,
        crypto=CRYPTO,
        allowed_crypto_exchanges=ALLOWED_CRYPTO_EXCHANGES,
    )

    publisher = PublisherClient(stream=stream)
    subscriber = SubscriberClient(api=api, strategy=strategy, crypto=CRYPTO)

    subscriber.start()
    publisher.start()
