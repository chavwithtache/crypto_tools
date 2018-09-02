# pip install binance
# also requires Visual C++ Build Tools.. from here http://landinghub.visualstudio.com/visual-cpp-build-tools
from binance.client import Client as bnbClient
from .. import Config, Balances


def get_binance_balances(cfg: Config):
    print('start binance')
    binance_config = cfg.api_config()['binance']
    bal = Balances(cfg)
    bnb_client = bnbClient(binance_config['api_key'], binance_config['api_secret'])
    recvWindow = 10000  # This may need to be increased if local and server times go out of sync
    bnb_balances = bnb_client.get_account(recvWindow=recvWindow)['balances']  #
    print(bnb_balances)
    nonEmpty = [bnbbal for bnbbal in bnb_balances if float(bnbbal['free']) != 0 or float(bnbbal['locked']) != 0]
    for bnbbal in nonEmpty:
        coin = cfg.resolve_coin(bnbbal['asset'].upper())
        bal.add_balance(coin, float(bnbbal['free']) + float(bnbbal['locked']), 'from Binance')
    print('end binance')
    return bal
