import csv
import json
import logging
import sys
from binance.spot import Spot as Client
from utils import configlog


configlog()
validatekeys = []


def getpermissions(apikey, apisecret):
    spot_client = Client(apikey, apisecret, show_header=True)
    try:
        response = spot_client.api_key_permissions()
        keypermissresponse = response['data']
        return keypermissresponse
    except Exception as e:
        print("Something went wrong:" + e)
        logging.error(e)
        sys.exit()


def validatepermissions(apikey, apisecret):
    permissions = getpermissions(apikey, apisecret)
    if (permissions['enableSpotAndMarginTrading']) and (not permissions['enableWithdrawals']):
        return True
    else:
        return False

def getbalance(apikey, apisecret):
    coinslocked = ''
    usdtfree = ''
    spot_client = Client(apikey, apisecret)
    try:
        response = spot_client.account()
        spotbalance = response['balances']
        usdtinfo = [x
                            for x in spotbalance
                            if float(x['free']) > 0 and x['asset'] == 'USDT'
                            ]
        for usdt in usdtinfo:
            usdtfree = usdt['free']
        lockbalance = [x
                       for x in spotbalance
                       if float(x['free']) > 0 or float(x['locked']) > 0
                       ]
        for coin in lockbalance:
            coinslocked = coinslocked + coin['asset']+';'
        coinslocked= coinslocked[:-1]


        return usdtfree+';'+coinslocked
    except Exception as e:
        print("Something went wrong:" + e)
        logging.error(e)
        sys.exit()

def retrievevalidkeys():
    keyarchive = 'keys.csv'
    with open(keyarchive, 'rt') as archive:
        try:
            reader = csv.reader(archive, delimiter=';')
            for linha in reader:
                print("user's apiKeys validation")
                if validatepermissions(linha[0], linha[1]):
                    coinsbalance = getbalance(linha[0], linha[1])
                    clientskeys = linha[0] + ";" + linha[1]
                    validatekeys.append(clientskeys+';'+coinsbalance)

            return validatekeys
        except Exception as e:
            print("Something went wrong with the list :" + e)
            logging.error(e)
            sys.exit()
