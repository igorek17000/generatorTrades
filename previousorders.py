import csv
import datetime
import logging
import os

from binance.spot import Spot as Client

from utils import getquantity, sendorder


def getbalance(apikey, apisecret):
    coinsbalance = []
    spot_client = Client(apikey, apisecret)
    try:
        response = spot_client.account()
        spotbalance = response['balances']
        validspotbalance = [x
                            for x in spotbalance
                            if float(x['free']) > 0 and not x['asset'] == 'USDT'
                            ]
        return validspotbalance
    except Exception as e:
        print("Something went wrong when retrive the client balance " + e)
        logging.error("Something went wrong when retrive the client balance " + e)


def readarchive(archivename, type):
    file_exists = os.path.exists(archivename)
    coins = {}
    try:
        if file_exists:
            with open(archivename) as file:
                csv_reader = csv.reader(file, delimiter=',')
                line_count = 0
                for row in csv_reader:
                    if line_count > 0:
                        definelist(type, row, coins)
                    else:
                        line_count += 1
            return coins
    except Exception as e:
        print("Something went wrong when create order archive " + e)
        logging.error("Something went wrong when create order archive  " + e)


def definelist(type, row, coins):
    coin = {}
    if type > 1:
        if row[0] in coins:
            existentcoin = coins[row[0]]
            existentcoin[row[1]] = {'orderId': row[1], 'orderListId': row[2], 'listClientOrderId': row[3],
                                    'origQty': row[4]}
            coins.update(existentcoin)
        else:
            coin[row[0]] = {}
            coin[row[0]][row[1]] = {'orderId': row[1], 'orderListId': row[2], 'listClientOrderId': row[3],
                                    'origQty': row[4]}
            coins.update(coin)
    else:
        coin[row[0]] = {'orderId': row[1], 'clientOrderId': row[3], 'executedQty': row[4]}
        coins.update(coin)


def findleftcoins(apikey, apisecret, member):
    memberscoin = getbalance(apikey, apisecret)
    previousdate = datetime.datetime.today() - datetime.timedelta(days=1)
    buyarchivename = 'fernando_ipirangadiario20-01-2022BUY.csv'  # member + 'diario' + previousdate.strftime('%d-%m-%Y') + 'BUY.csv'
    ocoarchivename = 'fernando_ipirangadiario20-01-2022OCO.csv'  # member + 'diario' + previousdate.strftime('%d-%m-%Y') + 'OCO.csv'
    boughtcoins = readarchive(buyarchivename, 1)
    ococoins = readarchive(ocoarchivename, 2)
    for member in memberscoin:
        if member['asset'] in boughtcoins:
            if getquantity(member['asset']['orderid'], member['asset'], apikey, apisecret) < 0:
                orderId = ococoins[member['asset']].keys()[0]
                quantity = definequantity(apikey, apisecret, ococoins[member['asset']].keys(), member['asset'])
                if quantity > 0:
                    canceloco(apikey, apisecret, member['asset'], ococoins[member['asset']][orderId]['orderListId'],
                              ococoins[member['asset']][orderId]['listClientOrderId'])
                    params = {
                        "symbol": member['asset'],
                        "side": "SELL",
                        "type": "MARKET",
                        "quantity": quantity,
                    }
                    sendorder(apikey, apisecret, params)

            else:
                canceloco(apikey, apisecret, member['asset'], member['orderId'], member['clientOrderId'])


findleftcoins('kt5kVIm9wK7364XBDj9l2lVgFPuCiJgRiFrnYB9O2cTPNLXeCj5O7S4WvXGiaXtC',
              'J4dHP27qNLaLzCr4cE6XqOfm9Asaqj7Gbhkd29j7oWE6dHCrLBGhvW9j3yU01t2M', 'fernando_ipiranga')


def definequantity(apikey, apisecret, ordersid, coin):
    quantity = 0
    i = 1
    while i < 3:
        quantity += getquantity(ordersid[i], coin, apikey, apisecret)
        i += 1
    return quantity


def cancelOrder(apikey, apisecret, coin, orderId, origClientOrderId):
    params = {
        "symbol": coin,
        "orderId": orderId,
        "origClientOrderId": origClientOrderId,
        "recvWindow": 1000,
    }
    client = Client(apikey, apisecret)
    response = client.cancel_order(**params)


def canceloco(apikey, apisecret, coin, orderListId, listClientOrderId):
    params = {
        "symbol": "BTCUSDT",
        "orderListId": orderListId,
        "listClientOrderId": listClientOrderId,
        "recvWindow": 1000,
    }
    client = Client(apikey, apisecret)
    response = client.cancel_oco_order(**params)
