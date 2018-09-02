from .. import Config, Valuation
import requests


def get_fixerio_values(cfg: Config, fiat_balances: dict):
    print('start fixer.io')
    display_ccy = cfg.display_ccy()
    val = Valuation(display_ccy)
    fixer_config = cfg.api_config()['fixerio']
    api_key = fixer_config['api_key']
    url = fixer_config['url'] + '?symbols={}&access_key={}'.format(
        ','.join(set(list(fiat_balances) + [display_ccy])), api_key)
    print(url)
    fxrates_raw = requests.get(url).json()
    fixer_base_rate = fxrates_raw['rates'][display_ccy]
    fxrates = {key: value / fixer_base_rate for key, value in fxrates_raw['rates'].items()}

    for coin, balance in fiat_balances.items():
        val.add_result(coin, balance, 1 / fxrates[coin])
    print('end fixer.io')
    return val
