import csv
import datetime
import logging
import os

from binance.spot import Spot as Client

from utils import getquantity, sendorder


def getbalance(apikey, apisecret):
    coinsbalance = []
    spot_client = Client(apikey, apisecret)
    params = {'recvWindow': 60000}
    try:
        response = spot_client.account(**params)
        spotbalance = response['balances']
        validspotbalance = [x
                            for x in spotbalance
                            if (float(x['free']) > 0 or float(x['locked']) > 0) and not x['asset'] == 'USDT'
                            ]
        return validspotbalance
    except Exception as e:
        errorStack = str(e)
        print("Something went wrong when retrive the client balance " + errorStack)
        logging.error("Something went wrong when retrive the client balance " + errorStack)


def readarchive(archivename, type, coins):
    file_exists = os.path.exists(archivename)
    coins = coins
    try:
        if file_exists:
            with open(archivename) as file:
                csv_reader = csv.reader(file, delimiter=',')
                line_count = 0
                for row in csv_reader:
                    if line_count > 0:
                        coins = definelist(type, row, coins)
                    else:
                        line_count += 1
        return coins
    except Exception as e:
        errorStack = str(e)
        print("Something went wrong when create order archive " + errorStack)
        logging.error("Something went wrong when create order archive  " + errorStack)


def definelist(type, row, coins):
    coin = {}
    if type > 1:
        if coins:
            if row[0] in coins.keys():
                existentcoin = coins[row[0]]
                existentcoin[row[1]] = {'orderId': row[1], 'orderListId': row[2], 'listClientOrderId': row[3],
                                        'origQty': row[4]}

            else:
                coin[row[0]] = {}
                coin[row[0]][row[1]] = {'orderId': row[1], 'orderListId': row[2], 'listClientOrderId': row[3],
                                        'origQty': row[4]}
                coins.update(coin)
        else:
            coin[row[0]] = {}
            coin[row[0]][row[1]] = {'orderId': row[1], 'orderListId': row[2], 'listClientOrderId': row[3],
                                    'origQty': row[4]}
            coins = coin
    else:
        coin[row[0]] = {'orderId': row[1], 'clientOrderId': row[3], 'executedQty': row[4]}
        coins.update(coin)
    return coins


def findleftcoins(apikey, apisecret, member):
    print('Verifying remaining orders and ocos for ' + member)
    memberscoin = getbalance(apikey, apisecret)
    previousdate = datetime.datetime.today() - datetime.timedelta(days=1)
    currentydate = datetime.datetime.today()
    buyarchivename = 'BUY/' + member + 'diario' + previousdate.strftime('%d-%m-%Y') + 'BUY.csv'
    ocoarchivename = 'OCO/' + member + 'diario' + previousdate.strftime('%d-%m-%Y') + 'OCO.csv'
    ocoarchivenametoday = member + 'diario' + currentydate.strftime('%d-%m-%Y') + 'OCO.csv'
    coin = {}
    boughtcoins = readarchive(buyarchivename, 1, coin)
    coin = {}
    ococoins = readarchive(ocoarchivename, 2, coin)
    ococoins = readarchive(ocoarchivenametoday, 2, ococoins)
    if boughtcoins:
        for boughtcoin in boughtcoins:
            purecoin = boughtcoin.replace('USDT', '')
            asset = [x
             for x in memberscoin
             if (x['asset'] == purecoin)
             ]
            if asset:
                boughtquantity = float(getquantity(boughtcoins[boughtcoin]['orderId'], boughtcoin, apikey, apisecret))
                if boughtquantity > 0:
                    if boughtcoin in ococoins.keys():
                        orderId = extractkeyvalue(ococoins[boughtcoin].keys(), 1)
                        orderquantitys = definequantity(apikey, apisecret, ococoins[boughtcoin].keys(), boughtcoin)
                        totalquantity = orderquantitys[orderId]['quantity'] + \
                                        orderquantitys[extractkeyvalue(ococoins[boughtcoin].keys(), 2)]['quantity']
                        if totalquantity == 0:
                            canceloco(apikey, apisecret, boughtcoin, ococoins[boughtcoin][orderId]['orderListId'],
                                      ococoins[boughtcoin][orderId]['listClientOrderId'], member)
                            orderId = extractkeyvalue(ococoins[boughtcoin].keys(), 2)
                            canceloco(apikey, apisecret, boughtcoin, ococoins[boughtcoin][orderId]['orderListId'],
                                      ococoins[boughtcoin][orderId]['listClientOrderId'], member)
                        elif totalquantity > 0:
                            if orderquantitys[orderId]['quantity'] == 0:
                                canceloco(apikey, apisecret, boughtcoin, ococoins[boughtcoin][orderId]['orderListId'],
                                          ococoins[boughtcoin][orderId]['listClientOrderId'], member)
                            orderId = extractkeyvalue(ococoins[boughtcoin].keys(), 2)
                            if orderquantitys[orderId]['quantity'] == 0:
                                canceloco(apikey, apisecret, boughtcoin, ococoins[boughtcoin][orderId]['orderListId'],
                                          ococoins[boughtcoin][orderId]['listClientOrderId'], member)
                        prepareordertosend(apikey, apisecret, boughtcoin, totalquantity, member)
                    else:
                        prepareordertosend(apikey, apisecret, boughtcoin, boughtquantity, member)
                else:
                    cancelOrder(apikey, apisecret, boughtcoin, boughtcoins[boughtcoin]['orderId'],
                                boughtcoins[boughtcoin]['clientOrderId'], member)
            else:
                cancelOrder(apikey, apisecret, boughtcoin, boughtcoins[boughtcoin]['orderId'],
                            boughtcoins[boughtcoin]['clientOrderId'], member)


def extractkeyvalue(currency_dict, val):
    listkeys = list(currency_dict)
    return listkeys[val]


def definequantity(apikey, apisecret, ordersid, coin):
    quantity = {}
    i = 1
    while i < 3:
        orderid = extractkeyvalue(ordersid, i)
        quantity[orderid] = {'quantity': float(getquantity(orderid, coin, apikey, apisecret))}
        i += 1
    return quantity


def cancelOrder(apikey, apisecret, coin, orderId, origClientOrderId, member):
    params = {
        "symbol": coin,
        "orderId": orderId,
        "origClientOrderId": origClientOrderId,
        "recvWindow": 1000,
    }
    client = Client(apikey, apisecret)
    try:
        response = client.cancel_order(**params)
    except Exception as e:
        pass
        errorStack = str(e)
        print('Something went wrong when cancel remaining buy order for ' + member + ' coin: ' + coin + ' error: ' + errorStack)
        logging.error('Something went wrong when cancel remaining buy order for ' + member + ' coin: ' + coin + ' error: ' + errorStack)

def canceloco(apikey, apisecret, coin, orderListId, listClientOrderId, member):
    params = {
        "symbol": coin,
        "orderListId": orderListId,
        "listClientOrderId": listClientOrderId
    }
    client = Client(apikey, apisecret)
    try:
        response = client.cancel_oco_order(**params)
    except Exception as e:
        pass
        errorStack = str(e)
        print("Something went wrong when cancel remaining buy order for " + member  + ' coin: ' + coin + ' error: ' + errorStack)
        logging.error("Something went wrong when cancel remaining buy order for " + member + ' coin: ' + coin + ' error: ' + errorStack)


def prepareordertosend(apikey, apisecret, boughtcoin, totalquantity, member):
    params = {
        "symbol": boughtcoin,
        "side": "SELL",
        "type": "MARKET",
        "quantity": totalquantity,
    }
    try:
        sendorder(apikey, apisecret, params)
    except Exception as e:
        pass
        errorStack = str(e)
        print('Something went wrong when sell remaining ' + boughtcoin + ' for ' + member + ' error: ' + errorStack)
        logging.error('Something went wrong when sell remaining ' + boughtcoin + ' for ' + member + ' error: ' + errorStack)
