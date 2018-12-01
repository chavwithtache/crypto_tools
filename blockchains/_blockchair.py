from .. import Config, Balances
import requests


def get_blockchair_balances(cfg: Config):
    print('start blockchair')
    bch_config = cfg.wallet_config()['bitcoin-cash']
    blockchair_config = cfg.api_config()['blockchair']
    bal = Balances(cfg)
    for address in bch_config['addresses']:
        print('processing address:{}'.format(address))
        bch_url = blockchair_config['url'] + 'bitcoin-cash/dashboards/address/{addr}'.format(addr=address)
        blockchair_result = requests.get(bch_url).json()
        balance = blockchair_result['data'][address]['address']['balance']
        print('balance:{}'.format(balance))
        if balance != 0:
            bal.add_balance('BCH', (int(balance) / blockchair_config['blockchair_units']),
                            'from BCH address {addr}'.format(addr=address))

        print('end blockchair')
    return bal
