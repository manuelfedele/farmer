import datetime
import json

import pytz
import requests

from alpaca.entities import Account, Bar, Trade, EntityFactory
from src.settings import APCA_API_KEY_ID, APCA_API_SECRET_KEY, APCA_API_BASE_URL


class AlpacaAPI:
    EntityFactory = EntityFactory

    def __init__(
        self,
        base_url: str = APCA_API_BASE_URL,
        key_id: str = APCA_API_KEY_ID,
        secret_key: str = APCA_API_SECRET_KEY,
    ):
        self.base_url = base_url
        self.data_url = "https://data.alpaca.markets/"
        self.stream_url = f"{self.base_url.replace('http', 'ws')}/stream/"

        self._key_id = key_id
        self._secret_key = secret_key

        self.session = requests.Session()

        self.session.headers.update(
            {"APCA-API-KEY-ID": self._key_id, "APCA-API-SECRET-KEY": self._secret_key}
        )
        self.account = Account(**self.get_account())

        self.tz = pytz.timezone("America/New_York")

        self.crypto_symbols = ("BTCUSD", "BCHUSD", "ETHUSD", "LTCUSD")

    @property
    def end(self):
        return datetime.datetime.utcnow().astimezone(self.tz)

    @property
    def start(self):
        return self.end - datetime.timedelta(hours=2)

    def _get_data_by_type(
        self,
        _type: str,
        symbol: str,
        params: dict,
        version: str = "v2",
        kind: str = "stocks",
    ):
        response = self.session.get(
            url=f"{self.data_url}/{version}/{kind}/{symbol}/{_type}", params=params
        ).json()
        try:
            return response[_type]
        except KeyError:
            # For snapshots, the response is a single object
            return response

    def _get_last_data_by_type(
        self, _type: str, symbol: str, version: str = "v2", kind: str = "stocks"
    ):
        return self.session.get(
            url=f"{self.data_url}/{version}/{kind}/{symbol}/{_type}/latest"
        ).json()

    def get_account(self, version: str = "v2"):
        return self.session.get(url=f"{self.base_url}/{version}/account").json()

    def get_order(self, order_id: str, version: str = "v2"):
        orders = self.session.get(
            url=f"{self.base_url}/{version}/orders/{order_id}"
        ).json()
        return self.EntityFactory(orders).create_entity("orders")

    def get_orders(self, version: str = "v2"):
        orders = self.session.get(url=f"{self.base_url}/{version}/orders").json()
        return [self.EntityFactory(order).create_entity("orders") for order in orders]

    def get_positions(self, symbol: str = None, version: str = "v2"):
        if not symbol:
            positions = self.session.get(
                url=f"{self.base_url}/{version}/positions"
            ).json()
        else:
            positions = self.session.get(
                url=f"{self.base_url}/{version}/positions/{symbol}"
            ).json()

        if isinstance(positions, list):
            return [
                self.EntityFactory(position).create_entity("positions")
                for position in positions
            ]
        else:
            return self.EntityFactory(positions).create_entity("positions")

    def get_bars(
        self,
        symbol: str,
        timeframe: str = "1Min",
        start: str = None,
        end: str = None,
        limit: int = 1000,
        adjustment: str = "raw",
        page_token: str = None,
        crypto: bool = False,
        exchanges: str = None,
    ) -> list[Bar]:
        if not end:
            end = self.end
        if not start:
            start = self.start

        params = {
            "timeframe": timeframe,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "limit": limit,
            "page_token": page_token,
        }

        if not crypto:
            params["adjustment"] = adjustment
            bars = self._get_data_by_type("bars", symbol, params)
        else:
            params["exchanges"] = exchanges
            bars = self._get_data_by_type(
                "bars", symbol, params, version="v1beta1", kind="crypto"
            )

        for bar in bars:
            bar["symbol"] = symbol
        return [self.EntityFactory(bar).create_entity("bars") for bar in bars]

    def get_trades(
        self,
        symbol: str,
        start: str = None,
        end: str = None,
        limit: int = 1000,
        page_token: str = None,
    ) -> list[Trade]:
        if not end:
            end = self.end
        if not start:
            start = self.start

        params = {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "limit": limit,
            "page_token": page_token,
        }
        trades = self._get_data_by_type("trades", symbol, params)
        for trade in trades:
            trade["symbol"] = symbol

        return [self.EntityFactory(trade).create_entity("trades") for trade in trades]

    def get_quotes(
        self,
        symbol: str,
        start: str = None,
        end: str = None,
        limit: int = 1000,
        page_token: str = None,
    ):
        if not end:
            end = self.end
        if not start:
            start = self.start

        params = {
            "start": start.isoformat(),
            "end": end.isoformat(),
            "limit": limit,
            "page_token": page_token,
        }

        quotes = self._get_data_by_type("quotes", symbol, params)
        for quote in quotes:
            quote["as_"] = quote["as"]
            quote.pop("as")
            quote["symbol"] = symbol

        return [self.EntityFactory(quote).create_entity("quotes") for quote in quotes]

    def get_last_bar(self, symbol: str):
        bar = self._get_last_data_by_type("bars", symbol)["bar"]
        bar["symbol"] = symbol
        return self.EntityFactory(bar).create_entity("bars")

    def get_last_trade(self, symbol: str):
        trade = self._get_last_data_by_type("trades", symbol)["trade"]
        trade["symbol"] = symbol
        return self.EntityFactory(trade).create_entity("trades")

    def get_last_quote(self, symbol: str):
        quote = self._get_last_data_by_type("quotes", symbol)["quote"]
        quote["as_"] = quote["as"]
        quote.pop("as")
        quote["symbol"] = symbol
        return self.EntityFactory(quote).create_entity("quotes")

    def get_snapshot(self, symbol: str):
        return self._get_data_by_type("snapshot", symbol, {})

    def place_order(
        self,
        symbol: str,
        qty: float = None,
        side: str = "buy",
        type: str = "market",
        time_in_force: str = "day",
        limit_price: str = None,
        stop_price: str = None,
        client_order_id: str = None,
        extended_hours: bool = None,
        order_class: str = None,
        take_profit: dict = None,
        stop_loss: dict = None,
        trail_price: str = None,
        trail_percent: str = None,
        notional: float = None,
        version: str = "v2",
    ):
        params = {
            "symbol": symbol,
            "side": side,
            "type": type,
            "time_in_force": time_in_force,
        }
        if qty is not None:
            params["qty"] = qty
        if notional is not None:
            params["notional"] = notional
        if limit_price is not None:
            params["limit_price"] = float(limit_price)
        if stop_price is not None:
            params["stop_price"] = float(stop_price)
        if client_order_id is not None:
            params["client_order_id"] = client_order_id
        if extended_hours is not None:
            params["extended_hours"] = extended_hours
        if order_class is not None:
            params["order_class"] = order_class
        if take_profit is not None:
            if "limit_price" in take_profit:
                take_profit["limit_price"] = float(take_profit["limit_price"])
            params["take_profit"] = take_profit
        if stop_loss is not None:
            if "limit_price" in stop_loss:
                stop_loss["limit_price"] = float(stop_loss["limit_price"])
            if "stop_price" in stop_loss:
                stop_loss["stop_price"] = float(stop_loss["stop_price"])
            params["stop_loss"] = stop_loss
        if trail_price is not None:
            params["trail_price"] = trail_price
        if trail_percent is not None:
            params["trail_percent"] = trail_percent

        order = self.session.post(
            url=f"{self.base_url}/{version}/orders", json=params
        ).json()

        return self.EntityFactory(order).create_entity("orders")


if __name__ == "__main__":
    api = AlpacaAPI(key_id=APCA_API_KEY_ID, secret_key=APCA_API_SECRET_KEY)
    bars = api.get_bars("BTCUSD", "1Min", exchanges=None, crypto=True)
    bars = [bar.to_dict() for bar in bars]
    json.dump(bars, open("../data/bars.json", "w"))

