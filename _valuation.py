import json

class Valuation(object):

    def __init__(self, display_ccy: str):
        self.balances = {}
        self.prices = {}
        self.values = {}
        self.missing_coins = []
        self.display_ccy = display_ccy
        self.iconomi_value = 0.0

    def add_from_dict(self, valuation_dict: dict):
        self.balances = valuation_dict['balances']
        self.prices = valuation_dict['prices']
        self.values = valuation_dict['values']
        self.missing_coins = valuation_dict['missing_coins']
        self.iconomi_value = valuation_dict['iconomi_value']

    def add_result(self, coin: str, balance: float, price: float):
        self.balances[coin] = balance
        self.prices[coin] = price
        self.values[coin] = price * balance

    def add_missing_coin(self, coin: str):
        self.missing_coins.append(coin)

    def get_price(self, coin: str):
        return self.prices[coin]

    def total_value(self):
        return sum([self.values[x] for x in self.values])

    def set_display_ccy(self, display_ccy: str):
        self.display_ccy = display_ccy

    def set_iconomi_value(self, iconomi_value: float):
        self.iconomi_value = iconomi_value

    def merge(self, valuation_objects):
        if not isinstance(valuation_objects, list):
            valuation_objects = [valuation_objects]
        for val in valuation_objects:
            self.balances = {**self.balances, **val.balances}
            self.prices = {**self.prices, **val.prices}
            self.values = {**self.values, **val.values}
            self.missing_coins = self.missing_coins + val.missing_coins
            self.iconomi_value += val.iconomi_value

    def valuation(self):
        return {'balances': self.balances,
                'prices': self.prices,
                'values': self.values,
                'total_value': '{:0,.2f}'.format(self.total_value()),
                'display_ccy': self.display_ccy,
                'iconomi_value': self.iconomi_value,
                'missing_coins': self.missing_coins}


def create_val_from_list(display_ccy: str, valuation_list: list) -> Valuation:
    val = Valuation(display_ccy)
    val.merge(valuation_list)
    return val


def create_val_from_file(valuation_path: str) -> Valuation:
    val_dict = json.loads(open(valuation_path).read())['data']
    val = Valuation(val_dict['display_ccy'])
    val.add_from_dict(val_dict)
    return val
