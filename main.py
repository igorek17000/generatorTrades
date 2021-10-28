import csv, sys
import logging
from binance.spot import Spot as Client
from binance.lib.utils import config_logging

def validateAccess(apiKey,apiSecret):
    # url ='https://api.binance.com/sapi/v1/account/apiRestrictions'
    # response = requests.get(url,params={'timestamp':'1635378863304', 'signature':'c8f3a7ebc60dedf250ce898ea67e96e328e25b9841f64bde90f041929b1dbd98'})
    # response.request.headers
    # {'Content-Type':'application/json', 'X-MBX-APIKEY': apiKey}
    # status = response.status_code

    spot_client = Client(apiKey+'0', apiSecret, show_header=True)
    response = spot_client.api_key_permissions()

    logging.info(response)
    print(response)


KeyArchive = 'keys.csv'
with open(KeyArchive, 'rt') as archive:
    print(archive)
    reader = csv.reader(archive, delimiter=';')
    for linha in reader:
        print("user's apiKeys validation")
        validateAccess(linha[0], linha[1])




