# pip install bitfinex NB the current prod version didn't have the TradeClient class so needed to manually download the bitfinex-develop version and copy bitfinex folder into venv
from bitfinex.client import TradeClient as bfxClient
from .. import Config, Balances


def get_bitfinex_balances(cfg: Config):
    print('start bitfinex')
    bfx_config = cfg.api_config()['bitfinex']
    bal = Balances(cfg)
    bfx_auth_client = bfxClient(bfx_config['api_key'], bfx_config['api_secret'])
    for account in bfx_auth_client.balances():
        coin = cfg.resolve_coin(account['currency'].upper())
        bal.add_balance(coin, float(account['amount']),
                        'from Bitfinex')
    print('end bitfinex')
    return bal
