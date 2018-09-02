# pip install coinbase
from coinbase.wallet.client import Client as cbClient
from .. import Config, Balances


def get_coinbase_balances(cfg: Config):
    print('start coinbase')
    coinbase_config = cfg.api_config()['coinbase']
    bal=Balances(cfg)
    client = cbClient(coinbase_config['api_key'], coinbase_config['api_secret'])
    accounts = client.get_accounts()
    for account in accounts.data:
        coin = cfg.resolve_coin(account['currency'].upper())
        bal.add_balance(coin, float(account['balance']['amount']),
                        'from Coinbase {addr}'.format(addr=account['name']))
    print('end coinbase')
    return bal
