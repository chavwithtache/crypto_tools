import json


class Config(object):

    def __init__(self, path: str):
        self.config = json.loads(open(path).read())
        self.coin_types = self.config['coin_types']

    def starting_balances(self) -> dict:
        return self.config['starting_balances']

    def api_config(self):
        return self.config['api_config']

    def display_ccy(self)->str:
        return self.config['display_ccy']

    def wallet_config(self):
        return self.config['wallets']

    def coin_config(self):
        return self.config['coins']

    def links(self):
        return self.config['links']

    def coin_type(self, coin: str):
        if coin in self.coin_types['fiat']:
            return 'fiat'
        elif coin in self.coin_types['iconomi_fund']:
            return 'iconomi_fund'
        else:
            return 'crypto'

    def resolve_coin(self, coin: str):
        return self.links().get(coin, coin)
