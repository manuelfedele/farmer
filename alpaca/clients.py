import requests

from alpaca.entities import Account
from src.settings import APCA_API_KEY_ID, APCA_API_SECRET_KEY, APCA_API_BASE_URL


class Client:
    def __init__(
            self,
            base_url: str = APCA_API_BASE_URL,
            key_id: str = APCA_API_KEY_ID,
            secret_key: str = APCA_API_SECRET_KEY
    ):
        self.base_url = base_url
        self.stream_url = f"{self.base_url.replace('http', 'ws')}/stream/"

        self._key_id = key_id
        self._secret_key = secret_key

        self.session = requests.Session()

        self.session.headers.update({
            "APCA-API-KEY-ID": self._key_id,
            "APCA-API-SECRET-KEY": self._secret_key
        })
        self.account = Account(**self.get_account())

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
