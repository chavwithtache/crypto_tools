import requests
from .. import Config, Valuation


class CoinMarketCap(object):
    def __init__(self, base_url: str, api_key: str, display_ccy: str):
        self._base_url = base_url
        self._display_ccy = display_ccy
        self._api_key = api_key
        self.get_map()

    def _request_get(self, uri):
        full_url = self._base_url + uri
        print('{}'.format(full_url))
        res = requests.get(full_url, headers={'X-CMC_PRO_API_KEY': self._api_key})
        return res

    def get_map(self):
        uri = 'cryptocurrency/map?listing_status=active&start=1'
        listings = self._request_get(uri).json()['data']
        self._coin_lookup = {item['symbol']: item['id'] for item in listings}

    def get_prices(self, coins):
        coin_ids = [self._coin_lookup.get(coin) for coin in coins if self._coin_lookup.get(coin)]
        uri = 'cryptocurrency/quotes/latest?id={}&convert={}'.format(','.join([str(coin_id) for coin_id in coin_ids]),
                                                                     self._display_ccy)
        data = self._request_get(uri).json()['data']
        prices = {item['symbol']: item['quote'][self._display_ccy.upper()]['price'] for _, item in data.items()}
        return prices

    def get_lookup(self):
        return self._coin_lookup


def get_cmc_values(cfg: Config, crypto_balances: dict, environment='pro'):
    print('start cmc')
    display_ccy = cfg.display_ccy()
    val = Valuation(display_ccy)
    cmc_config = cfg.api_config()['coinmarketcap.{}'.format(environment)]
    cmc = CoinMarketCap(cmc_config['url'], cmc_config['api_key'], display_ccy)
    coins = [coin for coin in crypto_balances]
    prices = cmc.get_prices(coins)
    for coin in crypto_balances:
        price = prices.get(coin, None)
        if price:
            val.add_result(coin, crypto_balances[coin], float(price))
        else:
            val.add_missing_coin(coin)
    print('end cmc')
    return val
