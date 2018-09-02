#pip install gdax
import gdax
from .. import Config, Balances


def get_coinbase_pro_balances(cfg: Config):
    print('start coinbase_pro')
    gdax_config = cfg.api_config()['gdax']
    bal = Balances(cfg)
    gdax_auth_client = gdax.AuthenticatedClient(gdax_config['api_key'], gdax_config['api_secret'],
                                                gdax_config['passphrase'])
    for account in gdax_auth_client.get_accounts():
        print(account)
        coin = cfg.resolve_coin(account['currency'].upper())
        bal.add_balance(coin, float(account['balance']),
                        'from GDAX {addr}'.format(addr=account['id']))
    print('end coinbase_pro')
    return bal
