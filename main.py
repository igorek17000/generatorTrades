import csv, sys
import json
import logging
from binance.spot import Spot as Client
from binance.lib.utils import config_logging

logging.basicConfig(filename='error.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logging.warning('This message will get logged on to a file')

def callapi(apikey, apisecret):
    spot_client = Client(apikey, apisecret, show_header=True)
    try:
        response = spot_client.api_key_permissions()
        keypermissresponse = response['data']
        return keypermissresponse
    except Exception as e:
        print("Something went wrong:")
        logging.error(e)
        sys.exit()


def validatePermissions(apikey, apisecret):
    permissions = callapi(apikey, apisecret)
    if (permissions['enableSpotAndMarginTrading']) and (not permissions['enableWithdrawals']):
        return True
    else:
        return False


KeyArchive = 'keys.csv'
with open(KeyArchive, 'rt') as archive:
    try:
        reader = csv.reader(archive, delimiter=';')
        for linha in reader:
            print("user's apiKeys validation")
            if validatePermissions(linha[0], linha[1]):
                print("acesso ok")
    except Exception as e:
        print("Something went wrong with key's archive:")
        logging.error(e)
        sys.exit()
