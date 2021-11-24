import csv

import os

from datetime import datetime
from binance.spot import Spot as Client
import logging
import sys
from utils import configlog


def gettype(coin):
    if coin['TipoCompra'].lower().find('tocando') > -1:
        return 'LIMIT'
    if coin['TipoCompra'].lower().find('acima') > -1:
        return 'STOP_LOSS_LIMIT'
    elif coin['TipoCompra'].lower().find('market') > -1:
        return 'MARKET'


def exchangeinfo(apikey, apisecret, symbol):
    try:
        client = Client(apikey, apisecret)
        exchange_info = client.exchange_info(symbol=symbol)
        return exchange_info
    except Exception as e:
        print("Something went wrong when retrive exchangeinfo " + e)
        logging.error("Something went wrong when retrive exchangeinfo" + e)
        sys.exit()


def investimentbalancegreaterthanlimit(apikey, apisecret, investimentbalance, symbol):
    try:
        exchange_info = exchangeinfo(apikey, apisecret, symbol)
        min_notional = exchange_info['symbols'][0]['filters'][3]['minNotional']
        return float(investimentbalance) > float(min_notional)
    except Exception as e:
        print("Something went wrong when validate coin's min investiment " + e)
        logging.error("Something went wrong when validate coin's min investiment " + e)
        sys.exit()


def getquantity(apikey, apisecret, quantity, symbol):
    try:
        exchange_info = exchangeinfo(apikey, apisecret, symbol)
        lot_size = exchange_info['symbols'][0]['filters'][2]['minQty']
        min_notional = exchange_info['symbols'][0]['filters'][3]['minNotional']
        precision = (str(lot_size).split('.')[1]).find('1') + 1
        return format(float(quantity), '.' + str(precision) + 'f')

    except Exception as e:
        print("Something went wrong when validate coin's quantity " + e)
        logging.error("Something went wrong when validate coin's quantity " + e)
        sys.exit()


def organizeparams(apikey, apisecret, coins, freebalance):
    params = {}
    for coin in coins:
        investimentbalance = float("{0:.2f}".format(float(freebalance) * (float(coin['Aporte%']) / 100)))
        if investimentbalancegreaterthanlimit(apikey, apisecret, investimentbalance, coin['Moeda']):
            params[coin['Moeda']] = {
                "symbol": coin['Moeda'],
                "side": "BUY",
                "type": gettype(coin),
            }
            if gettype(coin) == 'MARKET':
                params[coin['Moeda']]["quoteOrderQty"] = investimentbalance
            elif gettype(coin) == 'STOP_LOSS_LIMIT':
                params[coin['Moeda']]["timeInForce"] = "GTC"
                params[coin['Moeda']]["stopPrice"] = float(coin['ValorCompra'])
                params[coin['Moeda']]["price"] = float(coin['ValorCompra']) + (float(coin['ValorCompra']) * 0.005)
                params[coin['Moeda']]["quantity"] = getquantity(apikey, apisecret, float(investimentbalance /float(params[coin['Moeda']]['price'])),coin['Moeda'])
            elif gettype(coin) == 'LIMIT':
                params[coin['Moeda']]["timeInForce"] = "GTC"
                params[coin['Moeda']]["price"] = float(coin['ValorCompra'])
                params[coin['Moeda']]["quantity"] = getquantity(apikey, apisecret, float(
                    investimentbalance / float(params[coin['Moeda']]['price'])), coin['Moeda'])

    return params


def createorderlogfile(membro, estrategia, orderresponse):
    date = datetime.today().strftime('%d-%m-%Y')
    archivename = membro + estrategia + date + ".csv"
    file_exists = os.path.exists(archivename)
    logdata = []
    logdata.append(orderresponse['symbol'])
    logdata.append(orderresponse['orderId'])
    logdata.append(orderresponse['price'])
    logdata.append(orderresponse['executedQty'])
    logdata.append(orderresponse['status'])
    logdata.append(orderresponse['type'])
    logdata.append(orderresponse['side'])
    if orderresponse['status'] == 'FILLED':
        logdata.append(orderresponse['fills'][0]['commission'])
        logdata.append(orderresponse['fills'][0]['commissionAsset'])
    header = ['symbol', 'orderId', 'price', 'executedQty', 'status', 'type', 'side', 'commission', 'commissionAsset']
    try:
        with open(archivename, 'a', newline='') as f:
            write = csv.writer(f)
            if not file_exists:
                write.writerow(header)
            write.writerow(logdata)
    except Exception as e:
        print("Something went wrong when create order archive " + e)
        logging.error("Something went wrong when create order archive  " + e)
        sys.exit()


def makeorder(dataclient):
    strategies = dataclient['strategies']
    for data in strategies:
        params = organizeparams(dataclient['api_key'], dataclient['api_secret'], strategies[data]['coins'],
                                strategies[data]['capital_disponivel'])
        orderresponse = sendorder(dataclient['api_key'], dataclient['api_secret'], params)
        if(orderresponse):
            createorderlogfile(dataclient['membro'], data, orderresponse)


def sendorder(apikey, apisecret, params):
    client = Client(apikey, apisecret)
    try:
        for param in params:
            orderdata = params[param]
            response = client.new_order(**orderdata)
            return response
    except Exception as e:
        print("Something went wrong when make order " + e)
        logging.error("Something went wrong when make order " + e)
        sys.exit()
