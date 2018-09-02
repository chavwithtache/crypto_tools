from . import Config
import json


class Balances(object):

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.coins = {}

    def add_from_dict(self, balances_dict: dict):
        for coin, balances in balances_dict.items():
            for balance in balances['balances']:
                if self.coins.get(coin) is None:
                    self.coins[coin] = {'balances': []}
                self.coins[coin]['balances'].append(balance)

    def add_balance(self, coin: str, balance: float, description: str):
        if self.coins.get(coin) is None:
            self.coins[coin] = {'balances': []}
        self.coins[coin]['balances'].append({'balance': balance, 'description': description})

    def merge(self, bal_objects):
        if not isinstance(bal_objects, list):
            bal_objects = [bal_objects]
        for bal in bal_objects:
            self.add_from_dict(bal.get_all_balances())

    def get_aggregated_balances(self):
        simple_balances = {"crypto": {}, "fiat": {}, "iconomi_fund": {}}
        for coin, balances in self.coins.items():
            simple_balances[self.cfg.coin_type(coin)][coin] = sum(
                [x['balance'] for x in balances['balances']])

        return simple_balances

    def get_all_balances(self):
        return self.coins


def create_bal_from_file(cfg: Config, balances_path: str) -> Balances:
    bal = Balances(cfg)
    bal.add_from_dict(json.loads(open(balances_path).read())['data'])
    return bal


def create_bal_from_list(cfg: Config, balances_list: list) -> Balances:
    bal = Balances(cfg)
    bal.merge(balances_list)
    return bal
