import csv

import os

from datetime import datetime
from binance.spot import Spot as Client
import logging
import sys
from utils import configlog

configlog()
apikey = ''
apisecret = ''


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


def investimentbalancegreaterthanlimit(investimentbalance, symbol):
    try:
        exchange_info = exchangeinfo(apikey, apisecret, symbol)
        min_notional = exchange_info['symbols'][0]['filters'][3]['minNotional']
        return float(investimentbalance) > float(min_notional)
    except Exception as e:
        print("Something went wrong when validate coin's min investiment " + e)
        logging.error("Something went wrong when validate coin's min investiment " + e)
        sys.exit()


def getquantity(quantity, symbol):
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


def reorganizequantity(params,moeda,quantity):
    params[moeda]['firstTarget']["quantity"] = getquantity(quantity/2, moeda)
    params[moeda]['secondTarget']["quantity"] = getquantity(quantity/2, moeda)
    params[moeda]['canCreateOco'] = 1


def createbuyorder(params, coin, investimentbalance):
    params['BUY'] = {}
    params['BUY'][coin['Moeda']] = {
        "symbol": coin['Moeda'],
        "side": "BUY",
        "type": gettype(coin),
    }
    if gettype(coin) == 'MARKET':
        params['BUY'][coin['Moeda']]["quoteOrderQty"] = investimentbalance
    elif gettype(coin) == 'STOP_LOSS_LIMIT':
        params['BUY'][coin['Moeda']]["timeInForce"] = "GTC"
        params['BUY'][coin['Moeda']]["stopPrice"] = float(coin['ValorCompra'])
        params['BUY'][coin['Moeda']]["price"] = float(coin['ValorCompra']) + (
                float(coin['ValorCompra']) * 0.005)
        params['BUY'][coin['Moeda']]["quantity"] = getquantity(float(
            investimentbalance / float(params['BUY'][coin['Moeda']]['price'])), coin['Moeda'])
    elif gettype(coin) == 'LIMIT':
        params['BUY'][coin['Moeda']]["timeInForce"] = "GTC"
        params['BUY'][coin['Moeda']]["price"] = float(coin['ValorCompra'])
        params['BUY'][coin['Moeda']]["quantity"] = getquantity(float(
            investimentbalance / float(params['BUY'][coin['Moeda']]['price'])), coin['Moeda'])


def createocoorder(params, coin, investimentbalance):
    params['SELLOCO'] = {}
    params['SELLOCO'][coin['Moeda']] = {}

    params['SELLOCO'][coin['Moeda']] = {
        "symbol": coin['Moeda'],
        "side": "SELL",
        "stopLimitTimeInForce": "GTC",
        "canCreateOco" :0
    }
    params['SELLOCO'][coin['Moeda']]['firstTarget'] = {}
    if coin['PrimeiroAlvo'] and coin['PrimeiroAlvo']:
        params['SELLOCO'][coin['Moeda']]['secondTarget'] = {}
        params['SELLOCO'][coin['Moeda']]['firstTarget']["quantity"] = getquantity(float(
            investimentbalance / float(params['BUY'][coin['Moeda']]['price']) / 2), coin['Moeda'])
        params['SELLOCO'][coin['Moeda']]['secondTarget']["quantity"] = getquantity(float(
            investimentbalance / float(params['BUY'][coin['Moeda']]['price']) / 2), coin['Moeda'])
        params['SELLOCO'][coin['Moeda']]['firstTarget']["price"] = float(coin['PrimeiroAlvo']) - (
                float(coin['PrimeiroAlvo']) * 0.005)
        params['SELLOCO'][coin['Moeda']]['secondTarget']["price"] = float(coin['SegundoAlvo']) - (
                float(coin['SegundoAlvo']) * 0.005)
        params['SELLOCO'][coin['Moeda']]["stopPrice"] = float(coin['Stop']) - (float(coin['Stop']) * 0.005)
        params['SELLOCO'][coin['Moeda']]["stopLimitPrice"] = params['SELLOCO'][coin['Moeda']]["stopPrice"] - (
                params['SELLOCO'][coin['Moeda']]["stopPrice"] * 0.005)
    else:
        params['SELLOCO'][coin['Moeda']]['firstTarget']["quantity"] = getquantity(apikey, apisecret, float(
            investimentbalance / float(params['SELLOCO'][coin['Moeda']]['price']) / 2), coin['Moeda'])

        params['SELLOCO'][coin['Moeda']]['firstTarget']["price"] = float(coin['PrimeiroAlvo']) - (
                float(coin['PrimeiroAlvo']) * 0.005)

        params['SELLOCO'][coin['Moeda']]["stopPrice"] = float(coin['Stop']) - (float(coin['Stop']) * 0.005)
        params['SELLOCO'][coin['Moeda']]["stopLimitPrice"] = params['SELLOCO'][coin['Moeda']]["stopPrice"] - (
                params['SELLOCO'][coin['Moeda']]["stopPrice"] * 0.005)


def organizeordersparams(coins, freebalance):
    params = {}

    for coin in coins:
        investimentbalance = float("{0:.2f}".format(float(freebalance) * (float(coin['Aporte%']) / 100)))
        if investimentbalancegreaterthanlimit(investimentbalance, coin['Moeda']):
            createbuyorder(params, coin, investimentbalance)
            createocoorder(params, coin, investimentbalance)
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
    api_key = dataclient['api_key']
    api_secret = dataclient['api_secret']
    strategies = dataclient['strategies']
    try:
        for data in strategies:
            params = organizeordersparams(strategies[data]['coins'],
                                          strategies[data]['capital_disponivel'])
            sendorder(params, dataclient['membro'], data)
            sendoco(params['SELLOCO'])
    except Exception as e:
        print("Something went wrong when make order " + e)
        logging.error("Something went wrong when make order " + e)
        sys.exit()

def sendorder(params, membro, strategy):
    client = Client(apikey, apisecret)
    try:
        for param in params['BUY']:
            orderdata = params['BUY'][param]
            response = client.new_order_test(**orderdata)
            createorderlogfile(membro, strategy, response)
            if response['status'] == 'FILLED':
                quantity = response['executedQty']
                reorganizequantity(params['SELLOCO'], params['BUY'][param]['symbol'], float(quantity))


    except Exception as e:
        print("Something went wrong when send orders " + e)
        logging.error("Something went wrong when send orders  " + e)
        sys.exit()


def sendoco(params, membro, strategy):
    client = Client(apikey, apisecret)
    responseoco = {}
    try:
        for param in params:
            if params[param]['canCreateOco'] and params[param]['secondTarget'] and params[param]['firstTarget']:
                responseoco['firstTarget'] = client.new_oco_order(params[param]['symbol'], params[param]['side'], params[param]['quantity'],
                                                                  params[param]['firstTarget'], params[param]['stopPrice'],
                                                                  params[param]['stopLimitPrice'],
                                                                  params[param]['stopLimitTimeInForce'], )
                responseoco['secondTarget'] = client.new_oco_order(params[param]['symbol'], params[param]['side'], params[param]['quantity'],
                                                                   params[param]['secondTarget'], params[param]['stopPrice'],
                                                                   params[param]['stopLimitPrice'],
                                                                   params[param]['stopLimitTimeInForce'], )
            elif param['canCreateOco']:
                responseoco['firstTarget'] = client.new_oco_order(param['symbol'], param['side'], param['quantity'],
                                                                  param['firstTarget'],
                                                                  param['stopPrice'], param['stopLimitPrice'],
                                                                  param['stopLimitTimeInForce'], )
            params[param]['executed'] = 1
            for response in responseoco:
                createorderlogfile(membro, strategy, responseoco[response])
    except Exception as e:
        print("Something went wrong when make order " + e)
        logging.error("Something went wrong when make order " + e)
        sys.exit()
