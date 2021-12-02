import os

from alpaca_trade_api import Stream, REST

from src.services import AlgoBot, TickerData
from src.settings import APCA_API_KEY_ID, APCA_API_SECRET_KEY, APCA_API_BASE_URL, DATA_FEED

# import logging
# logging.basicConfig(format='%(asctime)s %(message)s', level=logging.WARNING)


# We inject the API key and secret into the environment variables because alpaca_trade_api library will look for them
os.environ.setdefault('APCA_API_KEY_ID', APCA_API_KEY_ID)
os.environ.setdefault('APCA_API_SECRET_KEY', APCA_API_SECRET_KEY)
os.environ.setdefault('APCA_API_BASE_URL', APCA_API_BASE_URL)

if __name__ == '__main__':
    stream = Stream(data_feed=DATA_FEED)
    api = REST()
    ticker_data = TickerData()
    bot = AlgoBot(stream=stream, api=api, ticker_data=ticker_data)
    bot.subscribe()
    bot.run()
