import math
import sys
from datetime import datetime
from binance.spot import Spot as Client
import logging
import csv
import os

def configlog():
    date = datetime.today().strftime('%d-%m-%Y')
    filename = "error" + date + ".log"
    logging.basicConfig(filename=filename, format='%(name)s - %(levelname)s - %(message)s')


def getquantity(orderid, symbol, apikey, apisecret):
    client = Client(apikey, apisecret)
    try:
        response = client.get_order(symbol, orderId=orderid)
        if response['status'] == 'FILLED':
            return response['executedQty']
        elif response['status'] == 'CANCELED':
            return -1
        else:
            return 0
    except Exception as e:
        print("Something went wrong when request order info " + e)
        logging.error("Something went wrong when request order info " + e)


def sendorder(apikey, apisecret, params):
    client = Client(apikey, apisecret)
    return client.new_order(**params)


def sendoco(apikey, apisecret, params):
    client = Client(apikey, apisecret)
    return client.new_oco_order(**params)

def createorderlogfilebuy(membro, estrategia, orderresponse, quotOrderQty):
    date = datetime.today().strftime('%d-%m-%Y')
    archivename = membro + estrategia + date + "BUY.csv"
    if quotOrderQty > 0:
        logdata = [orderresponse['symbol'], orderresponse['orderId'], orderresponse['clientOrderId'],
                   orderresponse['price'], quotOrderQty, orderresponse['executedQty'],
                   orderresponse['status'], orderresponse['type'], orderresponse['side']]
    else:
        logdata = [orderresponse['symbol'], orderresponse['orderId'], orderresponse['clientOrderId'], 0,
                   0,
                   0, '', '', '', 0, 0]
    if quotOrderQty > 0 and orderresponse['status'] == 'FILLED':
        logdata.append(orderresponse['fills'][0]['commission'])
        logdata.append(orderresponse['fills'][0]['commissionAsset'])
    header = ['symbol', 'orderId', 'clientOrderId', 'price', 'quotOrderQty', 'executedQty', 'status', 'type', 'side',
              'commission', 'commissionAsset']
    createarchive(archivename, header, logdata)


def createorderlogfileoco(membro, estrategia, orderresponse):
    header = ['symbol', 'orderId', 'orderListId', 'listClientOrderId', 'origQty', 'price', 'status', 'type', 'side',
              'stopPrice']
    date = datetime.today().strftime('%d-%m-%Y')
    archivename = membro + estrategia + date + "OCO.csv"
    reports = orderresponse['orderReports']
    logdata = []
    for report in reports:
        logdata.append(report['symbol'])
        logdata.append(report['orderId'])
        logdata.append(orderresponse['orderListId'])
        logdata.append(orderresponse['listClientOrderId'])
        logdata.append(report['origQty'])
        logdata.append(report['price'])
        logdata.append(report['status'])
        logdata.append(report['type'])
        logdata.append(report['side'])
        if report['type'] == 'STOP_LOSS_LIMIT':
            logdata.append(report['stopPrice'])
        createarchive(archivename, header, logdata)
        logdata.clear()


def createarchive(archivename, header, logdata):
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


def exchangeinfo(apikey, apisecret, symbol):
    try:
        client = Client(apikey, apisecret)
        exchange_info = client.exchange_info(symbol=symbol)
        return exchange_info
    except Exception as e:
        print("Something went wrong when retrive exchangeinfo " + e)
        logging.error("Something went wrong when retrive exchangeinfo" + e)
        sys.exit()

def getquantitycoin(quantity, symbol):
    apikey = ''
    apisecret = ''
    try:
        exchange_info = exchangeinfo(apikey, apisecret, symbol)
        lot_size = exchange_info['symbols'][0]['filters'][2]['minQty']
        precision = (str(lot_size).split('.')[1]).find('1') + 1
        return math.floor(float(quantity) * 10 ** precision) / 10 ** precision
    except Exception as e:
        print("Something went wrong when validate coin's quantity " + e)
        logging.error("Something went wrong when validate coin's quantity " + e)
        sys.exit()


def reorganizequantity(params, moeda, quantity, type):
    if type == 1:
        quantityplustax = quantity * 0.999
    elif type == 2:
        quantityplustax = quantity
    params[moeda]['firstTarget']["quantity"] = getquantitycoin(quantityplustax / 2, moeda)
    params[moeda]['secondTarget']["quantity"] = getquantitycoin(quantityplustax / 2, moeda)
    params[moeda]['canCreateOco'] = 1
