import csv
import math

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
        min_price = exchange_info['symbols'][0]['filters'][0]['minPrice']
        max_price = exchange_info['symbols'][0]['filters'][0]['maxPrice']
        return float(min_price) <= float(investimentbalance) <= float(max_price)
    except Exception as e:
        print("Something went wrong when validate coin's min investiment " + e)
        logging.error("Something went wrong when validate coin's min investiment " + e)
        sys.exit()


def getquantity(quantity, symbol):
    try:
        exchange_info = exchangeinfo(apikey, apisecret, symbol)
        lot_size = exchange_info['symbols'][0]['filters'][2]['minQty']
        precision = (str(lot_size).split('.')[1]).find('1') + 1
        return math.floor(float(quantity) * 10 ** precision) / 10 ** precision
    except Exception as e:
        print("Something went wrong when validate coin's quantity " + e)
        logging.error("Something went wrong when validate coin's quantity " + e)
        sys.exit()

def validateminnotional(quantity, price, symbol):
    try:
        exchange_info = exchangeinfo(apikey, apisecret, symbol)
        min_notional = exchange_info['symbols'][0]['filters'][3]['minNotional']
        return (float(quantity)*float(price))>=float(min_notional)
    except Exception as e:
        print("Something went wrong when validate coin's quantity " + e)
        logging.error("Something went wrong when validate coin's quantity " + e)
        sys.exit()
def formatpriceoco(price, symbol):
    try:
        exchange_info = exchangeinfo(apikey, apisecret, symbol)
        lot_size = exchange_info['symbols'][0]['filters'][0]['minPrice']
        precision = (str(lot_size).split('.')[1]).find('1') + 1
        return math.floor(float(price) * 10 ** precision) / 10 ** precision

    except Exception as e:
        print("Something went wrong when validate coin's quantity " + e)
        logging.error("Something went wrong when validate coin's quantity " + e)
        sys.exit()


def reorganizequantity(params, moeda, quantity):
    quantityplustax = quantity * 0.999
    params[moeda]['firstTarget']["quantity"] = getquantity(quantityplustax / 2, moeda)
    params[moeda]['secondTarget']["quantity"] = getquantity(quantityplustax / 2, moeda)
    params[moeda]['canCreateOco'] = 1


def createbuyorder(params, coin, investimentbalance):
    if 'BUY' in params:
        buy = params['BUY']
        moeda = coin['Moeda']
        buy[moeda] = {
            "symbol": coin['Moeda'],
            "side": "BUY",
            "type": gettype(coin),
        }
    else:
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
        params['BUY'][coin['Moeda']]["price"] = float(coin['ValorCompra'])
        params['BUY'][coin['Moeda']]["quantity"] = getquantity(float(
            investimentbalance / float(params['BUY'][coin['Moeda']]['price'])), coin['Moeda'])
    elif gettype(coin) == 'LIMIT':
        params['BUY'][coin['Moeda']]["timeInForce"] = "GTC"
        params['BUY'][coin['Moeda']]["price"] = float(coin['ValorCompra'])
        params['BUY'][coin['Moeda']]["quantity"] = getquantity(float(
            investimentbalance / float(params['BUY'][coin['Moeda']]['price'])), coin['Moeda'])


def createocoorder(params, coin, investimentbalance):
    if 'SELLOCO' in params:
        selloco = params['SELLOCO']
        moeda = coin['Moeda']
        selloco[moeda] = {
            "symbol": coin['Moeda'],
            "side": "SELL",
            "stopLimitTimeInForce": "GTC",
            "canCreateOco": 0
        }
    else:
        params['SELLOCO'] = {}
        params['SELLOCO'][coin['Moeda']] = {}

        params['SELLOCO'][coin['Moeda']] = {
            "symbol": coin['Moeda'],
            "side": "SELL",
            "stopLimitTimeInForce": "GTC",
            "canCreateOco": 0
        }
    params['SELLOCO'][coin['Moeda']]['firstTarget'] = {}
    if coin['PrimeiroAlvo'] and coin['SegundoAlvo']:
        params['SELLOCO'][coin['Moeda']]['secondTarget'] = {}
        params['SELLOCO'][coin['Moeda']]['firstTarget']["quantity"] = 0
        params['SELLOCO'][coin['Moeda']]['secondTarget']["quantity"] = 0
        params['SELLOCO'][coin['Moeda']]['firstTarget']["price"] = formatpriceoco(
            float(coin['PrimeiroAlvo']), coin['Moeda'])
        params['SELLOCO'][coin['Moeda']]['secondTarget']["price"] = formatpriceoco(
            float(coin['SegundoAlvo']) , coin['Moeda'])
    else:
        params['SELLOCO'][coin['Moeda']]['firstTarget']["quantity"] = getquantity(apikey, apisecret, float(
            investimentbalance / float(params['SELLOCO'][coin['Moeda']]['price']) / 2), coin['Moeda'])
        params['SELLOCO'][coin['Moeda']]['firstTarget']["price"] = formatpriceoco(
            float(coin['PrimeiroAlvo']) - (float(coin['PrimeiroAlvo']) * 0.005), coin['Moeda'])
    params['SELLOCO'][coin['Moeda']]["stopPrice"] = formatpriceoco(float(coin['Stop']) - (float(coin['Stop']) * 0.005),
                                                                   coin['Moeda'])

    params['SELLOCO'][coin['Moeda']]["stopLimitPrice"] = formatpriceoco(
        float(params['SELLOCO'][coin['Moeda']]["stopPrice"]) - float(
            float(params['SELLOCO'][coin['Moeda']]["stopPrice"]) * 0.005), coin['Moeda'])


def organizeordersparams(coins, freebalance):
    params = {}

    for coin in coins:
        investimentbalance = float("{0:.2f}".format(float(freebalance) * (float(coin['Aporte%']) / 100)))
        if investimentbalancegreaterthanlimit(investimentbalance, coin['Moeda']):
            createbuyorder(params, coin, investimentbalance)
            createocoorder(params, coin, investimentbalance)
    return params


def createorderlogfilebuy(membro, estrategia, orderresponse,quotOrderQty):
    date = datetime.today().strftime('%d-%m-%Y')
    archivename = membro + estrategia + date + "BUY.csv"
    if quotOrderQty > 0:
        logdata = [orderresponse['symbol'], orderresponse['orderId'], orderresponse['price'], quotOrderQty, orderresponse['executedQty'],
                   orderresponse['status'], orderresponse['type'], orderresponse['side']]
    else:
        logdata = [orderresponse['symbol'], orderresponse['orderId'], 0, 0,
                   0,
                   0, 0, 0]
    if quotOrderQty > 0 and orderresponse['status'] == 'FILLED':
        logdata.append(orderresponse['fills'][0]['commission'])
        logdata.append(orderresponse['fills'][0]['commissionAsset'])
    header = ['symbol', 'orderId', 'price', 'quotOrderQty', 'executedQty', 'status', 'type', 'side', 'commission', 'commissionAsset']
    createarchive(archivename, header, logdata)

def createorderlogfileoco(membro, estrategia, orderresponse):
    header = ['symbol', 'orderId', 'price', 'origQty', 'status', 'type', 'side', 'stopPrice']
    date = datetime.today().strftime('%d-%m-%Y')
    archivename = membro + estrategia + date + "oco.csv"
    reports = orderresponse['orderReports']
    logdata = []
    for report in reports:
        logdata.append(report['symbol'])
        logdata.append(report['orderId'])
        logdata.append(report['price'])
        logdata.append(report['origQty'])
        logdata.append(report['status'])
        logdata.append(report['type'])
        logdata.append(report['side'])
        if report['type'] == 'STOP_LOSS_LIMIT':
            logdata.append(report['stopPrice'])
        createarchive(archivename, header, logdata)
        logdata.clear()
def  createarchive(archivename,header,logdata):
    file_exists = os.path.exists(archivename)
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
    apikey = dataclient['api_key']
    apisecret = dataclient['api_secret']
    strategies = dataclient['strategies']

    for data in strategies:
        print("organizing orders from client:" + dataclient['membro'] + " index:" + data)
        params = organizeordersparams(strategies[data]['coins'],
                                      strategies[data]['capital_disponivel'])
        print("sending buy orders from client:" + dataclient['membro'] + "indice:" + data)
        sendorder(params, dataclient['membro'], data, apikey, apisecret)
        print("sending oco orders from client:" + dataclient['membro'] + "indice:" + data)

        filteredsellorders = dict(filter(lambda elem: elem[1]['canCreateOco'] > 0, params['SELLOCO'].items()))

        sendoco(filteredsellorders, dataclient['membro'], data, apikey, apisecret)

        strategies[data]['orders'] = params
    return dataclient




def sendorder(params, membro, strategy, apikey, apisecret):
    client = Client(apikey, apisecret)

    for param in params['BUY']:

        orderdata = params['BUY'][param]
        try:
            response = client.new_order(**orderdata)
            if params['BUY'][param]['type'] == 'MARKET':
                createorderlogfilebuy(membro, strategy, response, params['BUY'][param]['quoteOrderQty'])
            else:
                createorderlogfilebuy(membro, strategy, response, 0)
            if params['BUY'][param]['type'] == 'MARKET' and response['status'] == 'FILLED':
                quantity = response['executedQty']
                reorganizequantity(params['SELLOCO'], params['BUY'][param]['symbol'], float(quantity))
                params['BUY'][param]['executed'] = 1
            else:
                params['BUY'][param]['orderId'] = response['orderId']
                params['BUY'][param]['executed'] = 0
        except Exception as e:
            pass
            print("Something went wrong when buy orders, for details look to error.log")
            logging.error("Something went wrong when buy coins for member:" + membro + " and coin: " + orderdata[
                'symbol'])


def sendoco(params, membro, strategy, apikey, apisecret):
    client = Client(apikey, apisecret)
    responseoco = {}
    try:
        for param in params:

            if validateminnotional( params[param]['firstTarget']['quantity'], params[param]['firstTarget']['price'], params[param]['symbol']):
                if params[param]['canCreateOco'] and params[param]['secondTarget'] and params[param]['firstTarget']:
                    paramfirst = {'symbol': params[param]['symbol'], 'side': params[param]['side'],
                                  'quantity': params[param]['firstTarget']['quantity'],
                                  'price': params[param]['firstTarget']['price'],
                                  'stopPrice': params[param]['stopPrice'],
                                  'stopLimitPrice': params[param]['stopLimitPrice'],
                                  'stopLimitTimeInForce': params[param]['stopLimitTimeInForce'], }

                    responseoco['firstTarget'] = client.new_oco_order(**paramfirst)
                    paramsecond = {'symbol': params[param]['symbol'], 'side': params[param]['side'],
                                   'quantity': params[param]['secondTarget']['quantity'],
                                   'price': params[param]['secondTarget']['price'],
                                   'stopPrice': params[param]['stopPrice'],
                                   'stopLimitPrice': params[param]['stopLimitPrice'],
                                   'stopLimitTimeInForce': params[param]['stopLimitTimeInForce'], }
                    responseoco['secondTarget'] = client.new_oco_order(**paramsecond)
                elif params[param]['canCreateOco']:
                    paramfirst = {'symbol': params[param]['symbol'], 'side': params[param]['side'],
                                  'quantity': params[param]['firstTarget']['quantity'],
                                  'price': params[param]['firstTarget']['price'],
                                  'stopPrice': params[param]['stopPrice'],
                                  'stopLimitPrice': params[param]['stopLimitPrice'],
                                  'stopLimitTimeInForce': params[param]['stopLimitTimeInForce'], }
                    responseoco['firstTarget'] = client.new_oco_order(**paramfirst)
                params[param]['executed'] = 1
            else:
                logging.error("Something went wrong when send oco for member:"+membro+" and coin:" +params[param]['symbol'] + "the quantityXprice is lower than min_notional")
            for response in responseoco:
                createorderlogfileoco(membro, strategy, responseoco[response])

    except Exception as e:
        print("Something went wrong when send sell orders " + e)
        logging.error("Something went wrong when send sell orders  " + e)
