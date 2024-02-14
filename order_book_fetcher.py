import pandas as pd
import json
import requests

class OrderBookFetcher:
    def __init__(self, fiat='USD', asset='USDT', payment_methods=None, publisher_type=None, trans_amount=0):
        if payment_methods is None:
            payment_methods = ["zinli", "wallytech", "dukascopybank"]
        self._payment_methods = payment_methods
        self._fiat = fiat
        self._asset = asset
        self._publisher_type = publisher_type  # New property
        self._trans_amount = trans_amount  # New property
        self.all_asks = pd.DataFrame()
        self.all_bids = pd.DataFrame()
        self.base_url = 'https://2txjwiew8a.execute-api.us-east-1.amazonaws.com/pre/latest'
        self.params_base = {
            'fiat': self._fiat,
            'asset': self._asset,
            'publisher_type': self._publisher_type,
            'trans_amount': self._trans_amount
        }

    @property
    def payment_methods(self):
        return self._payment_methods

    @payment_methods.setter
    def payment_methods(self, value):
        if not value:
            raise ValueError("Payment methods list cannot be empty.")
        self._payment_methods = value

    @property
    def fiat(self):
        return self._fiat

    @fiat.setter
    def fiat(self, value):
        if not value:
            raise ValueError("Fiat currency cannot be empty.")
        self._fiat = value
        self.params_base['fiat'] = value

    @property
    def asset(self):
        return self._asset

    @asset.setter
    def asset(self, value):
        if not value:
            raise ValueError("Asset cannot be empty.")
        self._asset = value
        self.params_base['asset'] = value

    @property
    def publisher_type(self):
        return self._publisher_type

    @publisher_type.setter
    def publisher_type(self, value):
        if value not in (None, 'none', ''):
            raise ValueError("Publisher type must be None, 'none', or an empty string.")
        self._publisher_type = None if value in ('none', '') else value
        self.params_base['publisher_type'] = self._publisher_type

    @property
    def trans_amount(self):
        return self._trans_amount

    @trans_amount.setter
    def trans_amount(self, value):
        if not isinstance(value, int):
            raise ValueError("Transaction amount must be an integer.")
        self._trans_amount = value
        self.params_base['trans_amount'] = value

    def fetch_order_books(self):
        for method in self.payment_methods:
            self._fetch_for_payment_method(method)

    def _fetch_for_payment_method(self, method):
        params = self.params_base.copy()
        params['payment_methods'] = method

        response = requests.get(f'{self.base_url}/order-book', params=params)

        if response.status_code == 200:
            content_str = response.content.decode('utf-8')
            content_data = json.loads(content_str)

            # Include fiat, asset, trans_amount, and publisher_type in each row
            df_asks = pd.DataFrame(content_data['asks'])
            df_bids = pd.DataFrame(content_data['bids'])
            for df in (df_asks, df_bids):
                df['payment_method'] = method
                df['fiat'] = self._fiat
                df['asset'] = self._asset
                df['trans_amount'] = self._trans_amount
                df['publisher_type'] = self._publisher_type if self._publisher_type else 'None'

            self.all_asks = pd.concat([self.all_asks, df_asks], ignore_index=True)
            self.all_bids = pd.concat([self.all_bids, df_bids], ignore_index=True)
        else:
            print(f"Request failed for payment method {method} with status code: {response.status_code}")

    def fetch_all_payment_methods(self):
        """Fetches all available payment methods from the API."""
        url = f'{self.base_url}/payment-methods/'
        response = requests.get(url)

        if response.status_code == 200:
            payment_methods = response.json()
            return payment_methods
        else:
            print(f"Failed to fetch payment methods with status code: {response.status_code}")
            return []



# Example usage:
# order_book_fetcher = OrderBookFetcher()
# order_book_fetcher.fetch_order_books()

# Access the combined DataFrames
# print(order_book_fetcher.all_asks)
# print(order_book_fetcher.all_bids)
