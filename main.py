import os
import threading

from alpaca_trade_api import Stream, REST

from src.helpers import Client, OrderDispatcher
from src.settings import APCA_API_KEY_ID, APCA_API_SECRET_KEY, APCA_API_BASE_URL, DATA_FEED, BAR_SIZE, SYMBOL
from src.strategies import MovingAverageCrypto

# import logging
# logging.basicConfig(format='%(asctime)s %(message)s', level=logging.WARNING)


# We inject the API key and secret into the environment variables because alpaca_trade_api library will look for them

os.environ.setdefault('APCA_API_KEY_ID', APCA_API_KEY_ID)
os.environ.setdefault('APCA_API_SECRET_KEY', APCA_API_SECRET_KEY)
os.environ.setdefault('APCA_API_BASE_URL', APCA_API_BASE_URL)

if __name__ == '__main__':
    # These are Alpaca's interfaces for streaming and REST API
    stream = Stream(data_feed=DATA_FEED, raw_data=True)
    api = REST(raw_data=True)

    strategy = MovingAverageCrypto(api=api, symbol=SYMBOL, bar_size=BAR_SIZE)
    client = Client(api=api, stream=stream, strategy=strategy)

    dispatcher = OrderDispatcher(api=api)
    thread = threading.Thread(name='OrderDispatcher', target=dispatcher.listen, daemon=True).start()
    client.start()
