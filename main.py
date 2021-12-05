import os

from alpaca_trade_api import Stream, REST

from src.clients import OrderDispatcher, SubscriberClient
from src.settings import APCA_API_KEY_ID, APCA_API_SECRET_KEY, APCA_API_BASE_URL, DATA_FEED
from src.strategies import moving_average_crypto

# We inject the API key and secret into the environment variables because alpaca_trade_api library will look for them

os.environ.setdefault('APCA_API_KEY_ID', APCA_API_KEY_ID)
os.environ.setdefault('APCA_API_SECRET_KEY', APCA_API_SECRET_KEY)
os.environ.setdefault('APCA_API_BASE_URL', APCA_API_BASE_URL)

if __name__ == '__main__':
    # These are Alpaca's interfaces for streaming and REST API
    stream = Stream(data_feed=DATA_FEED, raw_data=True)
    api = REST(raw_data=True)

    subscriber_client = SubscriberClient(api=api, stream=stream)
    order_dispatcher = OrderDispatcher(api=api, strategy=moving_average_crypto)

    order_dispatcher.start()
    subscriber_client.start()
