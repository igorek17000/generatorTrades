import csv, sys
import json
import logging
from binance.spot import Spot as Client
from binance.lib.utils import config_logging

def callapi(apikey,apisecret):

    spot_client = Client(apikey+'0', apisecret, show_header=True)
    try:
        response = spot_client.api_key_permissions()
        keypermissresponse = json.loads(response.content)
        return keypermissresponse
    except:
        print("Something went wrong")




def validatePermissions(apikey,apisecret):
    permissions = callapi(apikey,apisecret)
    if (permissions['enableSpotAndMarginTrading']) and (not permissions['enableWithdrawals']):
        return True
    else:
        return False



KeyArchive = 'keys.csv'
with open(KeyArchive, 'rt') as archive:
    print(archive)
    reader = csv.reader(archive, delimiter=';')
    for linha in reader:
        print("user's apiKeys validation")
        if(validatePermissions(linha[0], linha[1])






