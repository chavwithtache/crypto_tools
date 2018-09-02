from .. import Config, Valuation
import requests


def get_iconomi_fund_values(cfg: Config, iconomi_balances: dict, usdrate):
    iconomi_config = cfg.api_config()['iconomi_blx']
    display_ccy = cfg.display_ccy()

    iconomi_value = 0.0
    val = Valuation(display_ccy)

    for coin, balance in iconomi_balances.items():
        print(iconomi_config['url'] + coin + '-chart')
        data = requests.get(iconomi_config['url'] + coin + '-chart').json()['chartData'].pop()['y'][
            'tokenPrice']
        print(data)
        price_usd = float(data)
        iconomi_value += balance * price_usd * usdrate
        val.add_result(coin, balance, price_usd * usdrate)
    val.set_iconomi_value(iconomi_value)
    return val
