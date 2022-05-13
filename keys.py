import logging
import sys

import gspread
from binance.spot import Spot as Client
from oauth2client.service_account import ServiceAccountCredentials

from utils import configlog

configlog()
clientsdata = {}


def getpermissions(apikey, apisecret):
    spot_client = Client(apikey, apisecret, show_header=True)
    params = {'recvWindow': 60000}
    try:
        response = spot_client.api_key_permissions(**params)
        keypermissresponse = response['data']
        return keypermissresponse
    except Exception as e:
        errorStack = str(e)
        print("Something went wrong:" + errorStack)
        logging.error(errorStack)
        sys.exit()


def validatepermissions(apikey, apisecret):
    permissions = getpermissions(apikey, apisecret)
    if (permissions['enableSpotAndMarginTrading']) and (not permissions['enableWithdrawals']):
        return True
    else:
        return False


def organizedata(balance, operations):
    strategy = {}
    coins = []
    strategy = {'strategy': balance['Estrategia'],
                'capital_disponivel': balance['capital_disponivel'].replace('$', '').replace('.', '').replace(',', '.')}
    for operation in operations:
        coin = {'Moeda': operation['Moeda'],
                'FlagCompraValida': operation['FlagCompraValida'],
                'TipoCompra': operation['TipoCompra'],
                'ValorCompra': "-" if operation['ValorCompra'] == '-' else operation['ValorCompra'].replace('$',
                                                                                                            '').replace(
                    '.', '').replace(',', '.'),
                'Aporte%': operation['Aporte%'].replace('%', '').replace(',', '.'),
                'Aporte($)': operation['Aporte($)'].replace('$', '').replace('.', '').replace(',', '.'),
                'PrimeiroAlvo': operation['PrimeiroAlvo'].replace('$', '').replace('.', '').replace(',', '.'),
                'SegundoAlvo': operation['SegundoAlvo'].replace('$', '').replace('.', '').replace(',', '.'),
                'Stop': operation['Stop'].replace('$', '').replace('.', '').replace(',', '.')}
        coins.append(coin)

    if balance['Membro'] in clientsdata:
        clientdata = clientsdata.get(balance['Membro'])
        strategy['coins'] = coins
        clientdata['strategies'][balance['Estrategia']] = strategy
        clientsdata[balance['Membro']].update(clientdata)
    else:
        clientdata = {'membro': balance['Membro'], 'api_key': balance['api_key'], 'api_secret': balance['api_secret']}
        clientdata['strategies'] = {}
        strategy['coins'] = coins
        clientdata['strategies'][balance['Estrategia']] = strategy
        clientsdata[balance['Membro']] = clientdata


def retrievevalidclientsinfos():
    try:
        balances = retrivesheets("Contato_Bot_Messias", 0)
        balances = [x
                    for x in balances
                    if x['api_key'] and x['api_secret'] and validatepermissions(x['api_key'], x['api_secret'])
                    ]

        operations = retrivesheets("Contato_Bot_Messias", 1)
        operations = [x
                      for x in operations
                      if x['Moeda'] and x['FlagCompraValida']
                      and x['TipoCompra'] and x['ValorCompra']
                      and x['Aporte($)'] and x['PrimeiroAlvo']
                      and x['SegundoAlvo'] and x['Stop']
                      ]

        for data in balances:
            operation = [x
                         for x in operations
                         if (x['Membro'] == data['Membro']) and (x['Estrategia'] == data['Estrategia'])
                         ]
            organizedata(data, operation)
        return clientsdata

    except Exception as e:
        errorStack = str(e)
        print("Something went wrong when retriving client's credentials " + errorStack)
        logging.error("Something went wrong when retriving client's credentials " + errorStack)
        sys.exit()

def retrivesheets(sheet, guide):
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)

    sheet = client.open(sheet).get_worksheet(guide)

    return sheet.get_all_records()