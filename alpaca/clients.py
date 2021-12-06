import datetime

import pytz
import requests

from alpaca.entities import Account, Bar, Trade, Quote
from src.settings import APCA_API_KEY_ID, APCA_API_SECRET_KEY, APCA_API_BASE_URL


class Client:
    def __init__(
            self,
            base_url: str = APCA_API_BASE_URL,
            key_id: str = APCA_API_KEY_ID,
            secret_key: str = APCA_API_SECRET_KEY
    ):
        self.base_url = base_url
        self.data_url = "https://data.alpaca.markets/"
        self.stream_url = f"{self.base_url.replace('http', 'ws')}/stream/"

        self._key_id = key_id
        self._secret_key = secret_key

        self.session = requests.Session()

        self.session.headers.update({
            "APCA-API-KEY-ID": self._key_id,
            "APCA-API-SECRET-KEY": self._secret_key
        })
        self.account = Account(**self.get_account())

        self.tz = pytz.timezone('America/New_York')

        self.casters = {
            "bar": Bar,
            "trade": Trade,
            "quote": Quote
        }

    @property
    def end(self):
        return datetime.datetime.utcnow().astimezone(self.tz)

    @property
    def start(self):
        return self.end - datetime.timedelta(hours=1)

    def _get_data_by_type(self, _type: str, symbol: str, params: dict):
        return self.session.get(
            url=f"{self.data_url}/v2/stocks/{symbol}/{_type}",
            params=params
        ).json()

    def _get_last_data_by_type(self, _type: str, symbol: str):
        return self.session.get(url=f"{self.data_url}/v2/stocks/{symbol}/{_type}/latest").json()

    def get_account(self):
        return self.session.get(url=f"{self.base_url}/v2/account").json()

    def get_order(self, client_order_id: str):
        return self.session.get(
            url=f"{self.base_url}/v2/orders",
            params={"client_order_id": client_order_id}
        ).json()

    def get_orders(self):
        return self.session.get(url=f"{self.base_url}/v2/orders").json()

    def get_positions(self, symbol: str = None):
        if not symbol:
            return self.session.get(url=f"{self.base_url}/v2/positions").json()
        else:
            return self.session.get(url=f"{self.base_url}/v2/positions/{symbol}").json()

    def get_bars(self, symbol: str, timeframe: str = "1Min", start: str = None, end: str = None, limit: int = 1000,
                 adjustment: str = "raw",
                 page_token: str = None):
        tz = pytz.timezone("America/New_York")
        if not end:
            end = datetime.datetime.utcnow().astimezone(tz)
        if not start:
            start = end - datetime.timedelta(hours=1)

        params = {
            "timeframe": timeframe,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "limit": limit,
            "adjustment": adjustment,
            "page_token": page_token
        }
        print(params)
        return self._get_data_by_type("bars", symbol, params).get("bars", [])

    def get_trades(self, symbol: str, start: str = None, end: str = None, limit: int = 1000, page_token: str = None):
        if not end:
            end = self.end
        if not start:
            start = self.start

        params = {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "limit": limit,
            "page_token": page_token
        }
        return self._get_data_by_type("trades", symbol, params).get("trades", [])

    def get_quotes(self, symbol: str, start: str = None, end: str = None, limit: int = 1000, page_token: str = None):
        if not end:
            end = self.end
        if not start:
            start = self.start

        params = {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "limit": limit,
            "page_token": page_token
        }
        print(params)
        return self._get_data_by_type("quotes", symbol, params).get("quotes", [])

    def get_last_bar(self, symbol: str):
        response = self._get_last_data_by_type("bars", symbol)
        return self.casters["bar"](symbol=response["symbol"], **response["bar"])

    def get_last_trade(self, symbol: str):
        response = self._get_last_data_by_type("trades", symbol)
        return self.casters["trade"](symbol=response["symbol"], **response["trade"])

    def get_last_quote(self, symbol: str):
        response = self._get_last_data_by_type("quotes", symbol)
        response["quote"]["as_"] = response["quote"]["as"]
        response["quote"].pop("as")
        return self.casters["quote"](symbol=response["symbol"], **response["quote"])

    def get_snapshot(self, symbol: str):
        return self._get_data_by_type("snapshot", symbol, {})


if __name__ == '__main__':
    c = Client(key_id=APCA_API_KEY_ID, secret_key=APCA_API_SECRET_KEY)
    print(c.get_last_quote("AAPL"))
