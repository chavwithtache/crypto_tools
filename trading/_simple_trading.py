from crypto_tools import Config
import collections
import gdax
import logging
import logging.handlers
import os
import math
import requests
import time
import arrow
import numpy as np

logger = logging.getLogger('crypto_toddlerTrading')
log_file = 'C:\\Users\\Ben\\dev\\python\\crypo-check\\logs\\crypto_toddler_trading.log'
should_roll_over = os.path.isfile(log_file)
hdlr = logging.handlers.RotatingFileHandler(log_file, mode='w', backupCount=5, maxBytes=1000000)
if should_roll_over:  # log already exists, roll over!
    hdlr.doRollover()
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)
# logging.basicConfig()
# logger = logging.getLogger()
# logger.setLevel(logging.INFO)


def round_up_nearest(f, nearest):
    return round(math.ceil(f / nearest) * nearest,10)


def round_nearest(f, nearest):
    return round(round(f / nearest,0) * nearest,10)


class SimpleTrading(object):
    def __init__(self, cfg: Config):
        api_config = cfg.api_config()

        self.gdax_config = api_config['gdax_write']
        self.reconnect_client()
        self.reload_orders()
        self.products = {product['id']: {'size_tick': float(product['base_min_size']),
                                         'price_tick': float(product['quote_increment'])} for product in
                         self.gdax_auth_client.get_products()}

        self.Market = collections.namedtuple('Market', 'id size gap_seconds_per_candle accumulate_asset')

        self.markets = []
        self.error_markets = {}
        self.counter = 0
        self.sentiment_or = {}
        self.spread_or = {}
        logger.info('started')

    def reconnect_client(self):
        self.gdax_auth_client = gdax.AuthenticatedClient(self.gdax_config['api_key'], self.gdax_config['api_secret'],
                                                         self.gdax_config['passphrase'])

    def reload_orders(self):
        self.orders = self.gdax_auth_client.get_orders()

    def add_market(self, market_id, size, spread_or=-1.0, sentiment_or=-1.0, accumulate_asset=False,
                   gap_seconds_per_candle=3600):
        self.markets.append(self.Market(id=market_id, size=size, gap_seconds_per_candle=gap_seconds_per_candle,
                                        accumulate_asset=accumulate_asset))
        self.error_markets[market_id] = False
        self.sentiment_or[market_id] = sentiment_or
        self.spread_or[market_id] = spread_or

    def check_products(self):
        try:
            self.reload_orders()
            for market in self.markets:
                self.check_product(market)
        except:
            print('some error...')
            logger.exception('some error...')

    def do_trades(self, market, mid_price):
        market_id = market.id
        sentiment = self.calc_sentiment(market_id) if self.sentiment_or[market_id] == -1.0 else self.sentiment_or[
            market_id]
        spread = self.calc_spread(market_id, market.gap_seconds_per_candle) if self.spread_or[market_id] == -1.0 else \
        self.spread_or[
            market_id]

        sell_price = round_nearest(mid_price + spread * sentiment, self.products[market_id]['price_tick'])
        sell_size = (
                            sell_price - spread) * market.size / sell_price if market.accumulate_asset else market.size
        sell_size = round_up_nearest(sell_size, self.products[market_id]['size_tick'])
        trade1_id = self.do_trade(market_id, 'sell', sell_price, sell_size)

        if trade1_id is not None:
            # first trade succeeded. Do second trade
            buy_price = round_nearest(mid_price - spread * (1 - sentiment), self.products[market_id]['price_tick'])
            trade2_id = self.do_trade(market_id, 'buy', buy_price, market.size)

            if trade2_id is not None:
                # Both trades executed successfully. Happy days
                pass
            else:
                # Trade1 succeeded but trade 2 failed. Need to cancel trade 1
                self.error_markets[market_id] = True
                logger.info(
                    'Second trade failed. Cancelling Trade1 id:{}. Trade_pair {} disabled'.format(trade1_id, market_id))
                logger.info(self.gdax_auth_client.cancel_order(trade1_id))
        else:
            self.error_markets[market_id] = True
            logger.info('First trade failed. Trade_pair {} disabled'.format(market_id))

    def do_trade(self, market, side, price, size):

        print('{} {} {} @ {}'.format(side, size, market, price))
        if side == 'sell':
            result = self.gdax_auth_client.sell(product_id=market, type='limit', size=size, price=price, post_only=True)
        else:
            result = self.gdax_auth_client.buy(product_id=market, type='limit', size=size, price=price, post_only=True)

        logger.info(result)

        # the success is if result is a dictionary with an id key AND 'status' != 'rejected'
        try:
            new_trade_id = result['id']
            if result['status'] == 'rejected':
                new_trade_id = None
            else:
                with open('C:\\Users\\Ben\\dev\\python\\crypo-check\\data\\toddler_trading\\{}\\{}'.format(market,
                                                                                                           new_trade_id),
                          'w'):
                    pass
        except Exception:
            new_trade_id = None

        return new_trade_id

    def check_product(self, market):
        market_id = market.id
        if self.error_markets[market_id]:
            print('{} temporarily suspended due to error'.format(market_id))
        else:
            active_ids = [order['id'] for order in self.orders[0]]
            orders_left = 0
            for active_id in os.listdir(
                    'C:\\Users\\Ben\\dev\\python\\crypo-check\\data\\toddler_trading\\' + market_id):
                try:
                    active_ids.index(active_id)
                    # order still open.
                    orders_left += 1
                except ValueError:
                    # not in the list so delete the file. this means that has traded since last run
                    os.remove(
                        'C:\\Users\\Ben\\dev\\python\\crypo-check\\data\\toddler_trading\\{}\\{}'.format(market_id,
                                                                                                         active_id))

            if orders_left == 0:
                print('{}: orders all hit - do another pair'.format(market_id))
                url = 'https://api.gdax.com/products/' + market_id + '/book?level=1'
                orderbook = requests.get(url).json()  # json.loads(urllib.request.urlopen(url).read())
                mid = (float(orderbook['bids'][0][0]) + float(orderbook['asks'][0][0])) / 2

                self.do_trades(market, mid)

            else:
                self.counter += 1
                print('{} {}: waiting for orders to hit. {} order(s) outstanding'.format(self.counter, market_id,
                                                                                         orders_left))
                time.sleep(5)

    @staticmethod
    def calc_sentiment(market_id):
        # sentiment is the ratio of the spread that is applied to the sell order
        # eg if 0.8 is specified then the orders will be:
        # sell_price =  mid + 0.8 * spread
        # buy_price =  mid - 0.2 * spread
        # eg. 0.2 is bearish, 0.5 neutral, 0.8 bullish

        granularity = 60  # number of seconds for the candle
        lookback_periods = 15  # number of candles to go back
        max_move = 0.01  # highest move in a single candle
        min_move = -0.01  # lowest move in a single candle
        max_sentiment = 0.8  # max sentiment that maps to max_move
        min_sentiment = 0.2  # min sentiment that maps to min_move

        xp = np.array([min_move, max_move])
        fp = np.array([min_sentiment, max_sentiment])

        public_client = gdax.PublicClient()

        to_time = arrow.get(public_client.get_time()['iso']).shift(seconds=-5)
        from_time = to_time.shift(minutes=-lookback_periods)

        # if the market is vs EUR or GBP, check the USD market as it is much more liquid
        liq_market = market_id[0:4] + 'USD' if market_id[4:7] in ['EUR', 'GBP'] else market_id

        result = public_client.get_product_historic_rates(product_id=liq_market, start=from_time.isoformat()[:19],
                                                          end=to_time.isoformat()[:19], granularity=granularity)

        x = np.array([candle[0] for candle in result])
        _close = np.array([candle[4] for candle in result])

        future = x[0] + granularity
        p = np.poly1d(np.polyfit(x, _close, 2))

        _last = _close[0]
        _next = p(future)
        pc_move = (_next - _last) / _last
        sentiment = round(np.interp(pc_move, xp, fp), 2)
        # future close
        logger.info(
            'market {} (used {}), last {}, next {}. Going {} by {:5.4f}% Calculated sentiment:{}'.format(market_id,
                                                                                                         liq_market,
                                                                                                         _last, _next,
                                                                                                         'up' if _next > _last else 'down',
                                                                                                         100 * pc_move,
                                                                                                         sentiment))
        return sentiment

    @staticmethod
    def calc_spread(market_id, spread_seconds_per_candle):
        # returns the average candle size (low - high) for last 50 candles

        # gap_seconds_per_candle must be one of [60, 300, 900, 3600, 21600, 86400]

        if spread_seconds_per_candle not in [60, 300, 900, 3600, 21600, 86400]:
            raise ValueError('gap_seconds_per_candle must be one of [60, 300, 900, 3600, 21600, 86400]')
        # calc gap:

        public_client = gdax.PublicClient()

        lookback_periods = 50  # number of candles to go back
        to_time = arrow.get(public_client.get_time()['iso']).shift(seconds=-5)
        from_time = to_time.shift(minutes=-lookback_periods * spread_seconds_per_candle / 60)

        spread_result = public_client.get_product_historic_rates(product_id=market_id, start=from_time.isoformat()[:19],
                                                                 end=to_time.isoformat()[:19],
                                                                 granularity=spread_seconds_per_candle)

        spread = np.average([candle[2] - candle[1] for candle in spread_result])
        logger.info('market {}  Average of last {} - {} second Candle Size:{}'.format(market_id, lookback_periods,
                                                                                      spread_seconds_per_candle,
                                                                                      spread))
        return spread
