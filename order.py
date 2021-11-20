import json

from binance.spot import Spot as Client
import logging
import sys
from utils import configlog

def organizeparams(coins,freebalance):
    params = {}
    for coin in coins:
        params [coin['Moeda']]= {
            "symbol": coin['Moeda'],
            "side": "BUY" if coin['FlagCompraValida'] == 'S' else 'STOPLIMIT',
            "type": "MARKET",
            "quoteOrderQty": str("{0:.2f}".format(float(freebalance)/(float(coin['Aporte%'])/100 )))
        }
    return params


def adjustparam(dataclient):

    strategies = dataclient['strategies']
    for data in strategies:
        params = organizeparams(strategies[data]['coins'], strategies[data]['capital_disponivel'])
        makeorder(dataclient, params)

def makeorder(dataclient,params):
    client = Client(dataclient['api_key'], dataclient['api_secret'])
    try:
        for param in params:
            orderdata = params[param]
            response = client.new_order_test(**orderdata)
            logging.info(response)
    except Exception as e:
        print("Something went wrong when make order" + e)
        logging.error(e)
        sys.exit()
