from .. import Config, Balances
import requests
import time


# Ethplorer.io FreeKey limits
# Requests per second: 0.5 (1 request per 2 seconds)
# Max count of transactions/operations in response: 10
# Max age for timestamp parameter: 30 days
# getAddressInfo method: 1 request per 6 second

def get_ethplorer_balances(cfg: Config):
    print('start ethplorer')
    eth_config = cfg.wallet_config()['ethereum']
    ethplorer_config = cfg.api_config()['ethplorer']
    bal = Balances(cfg)
    counter = 0
    for eth_address in eth_config['addresses']:
        if counter > 0:
            time.sleep(6)
        counter += 1
        print('processing address:{}'.format(eth_address))
        req = requests.get(
            '{}getAddressInfo/{}?apiKey={}'.format(ethplorer_config['url'], eth_address, ethplorer_config['api_key']))
        if req.ok:
            data = req.json()
            bal.add_balance('ETH', data['ETH']['balance'],
                            'from ETH address {}'.format(eth_address))
            for token in data['tokens']:
                token_info = token['tokenInfo']
                add_bal = True
                if token_info['symbol'] != '':
                    coin = cfg.resolve_coin(token_info['symbol'].upper())
                    comment = ''
                elif token_info['name'] != '':
                    coin = cfg.resolve_coin(token_info['name'].upper())
                    comment = ' NO SYMBOL. DODGY.'
                else:
                    add_bal = False

                if add_bal:
                    bal.add_balance(coin, token['balance'] / (10 ** int(token_info['decimals'])),
                                'from ETH address {}.{}'.format(eth_address,comment))
        else:
            print('issue with address:{}'.format(eth_address))
    print('end ethplorer')
    return bal
