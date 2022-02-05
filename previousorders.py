import csv
import datetime
import logging
import os

from binance.spot import Spot as Client


def getbalance(apikey, apisecret):
    coinsbalance= []
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
        print("Something went wrong:")
        logging.error(e)


def  readarchive(archivename, type):
    file_exists = os.path.exists(archivename)
    coins = {}
    try:
        if file_exists:
            with open(archivename) as file:
                csv_reader = csv.reader(file, delimiter=',')
                line_count = 0
                for row in csv_reader:
                    coin = {}
                    if line_count > 0:
                        if type > 1:
                            if row[0] in coins:
                                existentcoin = coins[row[0]]
                                existentcoin[row[1]] ={'orderId': row[1], 'executedQty': row[3]}
                                coins.update(existentcoin)
                            else:
                                coin[row[0]] = {}
                                coin[row[0]][row[1]] = {'orderId': row[1], 'executedQty': row[3]}

                                coins.update(coin)
                        else:
                            coin[row[0]] = {'orderId': row[1], 'executedQty': row[4]}
                            coins.update(coin)
                    else:
                        line_count += 1
            return coins
    except Exception as e:
        print("Something went wrong when create order archive " + e)
        logging.error("Something went wrong when create order archive  " + e)

def findleftcoins(apikey, apisecret, member):
    memberscoin = getbalance(apikey, apisecret)
    previousdate = datetime.datetime.today() - datetime.timedelta(days=1)
    buyarchivename = 'fernando_ipirangadiario20-01-2022BUY.csv'#member + 'diario' + previousdate.strftime('%d-%m-%Y') + 'BUY.csv'
    ocoarchivename = 'fernando_ipirangadiario20-01-2022OCO.csv'  # member + 'diario' + previousdate.strftime('%d-%m-%Y') + 'OCO.csv'
    boughtcoins = readarchive(buyarchivename, 1)
    ococoins = readarchive(ocoarchivename, 2)
    for member in memberscoin:
        if member['asset'] in boughtcoins:
            if boughtcoins[member['asset']]['executedQty'] == member['locked']:
                if member['asset'] in ococoins:
                    ococoins[member['asset']].keys()

findleftcoins('kt5kVIm9wK7364XBDj9l2lVgFPuCiJgRiFrnYB9O2cTPNLXeCj5O7S4WvXGiaXtC','J4dHP27qNLaLzCr4cE6XqOfm9Asaqj7Gbhkd29j7oWE6dHCrLBGhvW9j3yU01t2M','fernando_ipiranga')



#verificar saldo da moedas(lock) e validar se as mesmas estavam nas ordens de ontem
#caso estejam , validar a quantidade que foi comprado olhando as ordens de compra""
