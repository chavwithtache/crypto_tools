from .. import Config, Balances
import requests


def get_blockchair_balances(cfg: Config):
    print('start blockchair')
    bch_config = cfg.wallet_config()['bitcoin-cash']
    blockchair_config = cfg.api_config()['blockchair']
    bal = Balances(cfg)
    for address in bch_config['addresses']:
        print('processing address:{}'.format(address))
        bch_url = blockchair_config['url'] + '?q=recipient({addr})'.format(addr=address)
        blockchair_result = requests.get(bch_url).json()
        print('is spent:{}'.format(blockchair_result['data'][0]['is_spent']))
        if blockchair_result['data'][0]['is_spent'] == 0:
            bal.add_balance('BCH', int(blockchair_result['data'][0]['value']) / blockchair_config['blockchair_units'],
                            'from BCH address {addr}'.format(addr=address))
    print('end blockchair')
    return bal
