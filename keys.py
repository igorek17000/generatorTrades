import csv
import json
import logging
import sys
from binance.spot import Spot as Client
from utils import configlog


configlog()
validatekeys = []


def callapi(apikey, apisecret):
    spot_client = Client(apikey+"0", apisecret, show_header=True)
    try:
        response = spot_client.api_key_permissions()
        keypermissresponse = response['data']
        return keypermissresponse
    except Exception as e:
        print("Something went wrong:")
        logging.error(e)
        sys.exit()


def validatepermissions(apikey, apisecret):
    permissions = callapi(apikey, apisecret)
    if (permissions['enableSpotAndMarginTrading']) and (not permissions['enableWithdrawals']):
        return True
    else:
        return False


def retrievevalidkeys():
    keyarchive = 'keys.csv'
    with open(keyarchive, 'rt') as archive:
        try:
            reader = csv.reader(archive, delimiter=';')
            for linha in reader:
                print("user's apiKeys validation")
                if validatepermissions(linha[0], linha[1]):
                    clientskeys = linha[0] + ";" + linha[1]
                    validatekeys.append(clientskeys)

            return validatekeys
        except Exception as e:
            print("Something went wrong with key's archive:")
            logging.error(e)
            sys.exit()
