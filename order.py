import json
from math import floor

from binance.spot import Spot as Client
import logging
import sys
from utils import configlog

def gettype(coin):
    if coin['TipoCompra'].lower().find('acima') > -1 or coin['TipoCompra'].lower().find('tocando') > -1:
       return 'STOP_LOSS_LIMIT'
    elif coin['TipoCompra'].lower().find('market') > -1:
       return  'MARKET'

def getquantity(apikey, apisecret,quantity,symbol):

    try:
        client = Client(apikey, apisecret)
        exchange_info = client.exchange_info(symbol=symbol)
        lot_size = float(exchange_info['symbols'][0]['filters'][2]['minQty'])
        precision = str(len(str(lot_size).split('.')[1]))
        formatpattern = "{0:."+precision+"f}"
        return float(formatpattern.format(quantity))

    except Exception as e:
        print("Something went wrong when validate coin's quantity " + e)
        logging.error("Something went wrong when validate coin's quantity " + e)
        sys.exit()


def organizeparams(apikey, apisecret, coins, freebalance):
    params = {}
    for coin in coins:
        params[coin['Moeda']] = {
            "symbol": coin['Moeda'],
            "side": "BUY",
            "type": gettype(coin),
        }
        if gettype(coin) == 'MARKET':
            params[coin['Moeda']]["quoteOrderQty"] = str("{0:.2f}".format(float(freebalance) *(float(coin['Aporte%']) /100)))
        elif gettype(coin) == 'STOP_LOSS_LIMIT':
            params[coin['Moeda']]["timeInForce"]="GTC"
            params[coin['Moeda']]["stopPrice"] = float(coin['ValorCompra'])
            params[coin['Moeda']]["price"] = float(coin['ValorCompra']) + (float(coin['ValorCompra'])*0.005)
            investimentbalance = float("{0:.2f}".format(float(freebalance) * (float(coin['Aporte%']) / 100)))
            params[coin['Moeda']]["quantity"] = getquantity(apikey, apisecret, float(investimentbalance / float(params[coin['Moeda']]['price'])), coin['Moeda'] )
    return params


def makeorder(dataclient):
    strategies = dataclient['strategies']
    for data in strategies:
        params = organizeparams(dataclient['api_key'], dataclient['api_secret'], strategies[data]['coins'], strategies[data]['capital_disponivel'])
        sendorder(dataclient['api_key'], dataclient['api_secret'], params)


def sendorder(apikey, apisecret, params):
    client = Client(apikey, apisecret)
    try:
        for param in params:
            orderdata = params[param]
            response = client.new_order_test(**orderdata)
            logging.info(response)
    except Exception as e:
        print("Something went wrong when make order " + e)
        logging.error("Something went wrong when make order " + e)
        sys.exit()
