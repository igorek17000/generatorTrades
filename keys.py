import logging
import sys

import gspread
from binance.spot import Spot as Client
from oauth2client.service_account import ServiceAccountCredentials

from utils import configlog

configlog()
validatekeys = []

clientsdata = {}


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
    try:
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
        client = gspread.authorize(creds)

        sheet = client.open("Contato_Bot_Messias").get_worksheet(0)
        balances = sheet.get_all_records()
        sheet = client.open("Contato_Bot_Messias").get_worksheet(1)
        operations = sheet.get_all_records()



    except Exception as e:
        print("Something went wrong when retriving coins value" + e)
        logging.error(e)
        sys.exit()


def organizedata(balance, operations):
    if balance['Membro'] in clientsdata:
        clientdata = clientsdata.get(balance['Membro'])
    else:
        clientdata = {'membro': balance['Membro'], 'api_key': balance['api_key'], 'api_secret': balance['api_secret']}

        strategies = {'strategy': balance['Estrategia'], 'capital_disponivel': balance['capital_disponivel']}
        coins = []

        for operation in operations:
            coin = {'Moeda': operation['Moeda'],
                    'FlagCompraValida': operation['FlagCompraValida'],
                    'TipoCompra': operation['TipoCompra'],
                    'ValorCompra': operation['ValorCompra'],
                    'Aporte%': operation['Aporte%'],
                    'Aporte($)': operation['Aporte($)'],
                    'PrimeiroAlvo': operation['PrimeiroAlvo'],
                    'SegundoAlvo': operation['SegundoAlvo'],
                    'Stop': operation['Stop']}
            coins.append(coin)
        strategies['coins'] = coins
        clientdata['strategies'] = strategies
        clientsdata[balance['Membro']] = clientdata


def retrievevalidkeys():
    try:
        scope = ['https://spreadsheets.google.com/feeds',
                 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
        client = gspread.authorize(creds)

        sheet = client.open("Contato_Bot_Messias").get_worksheet(0)
        balances = sheet.get_all_records()
        balances = [x
                    for x in balances
                    if x['api_key'] and x['api_secret']
                    ]
        sheet = client.open("Contato_Bot_Messias").get_worksheet(1)
        operations = sheet.get_all_records()
        operations = [x
                      for x in operations
                      if x['Moeda'] and x['FlagCompraValida']
                      and x['TipoCompra'] and x['ValorCompra']
                      and x['Aporte($)'] and x['PrimeiroAlvo']
                      and x['SegundoAlvo'] and x['Stop']
                      ]

        for data in balances:
            if validatepermissions(data['api_key'], data['api_secret']):
                operation = [x
                             for x in operations
                             if (x['Membro'] == data['Membro']) and (x['Estrategia'] == data['Estrategia'])
                             ]
                organizedata(data, operation)
                return

    except Exception as e:
        print("Something went wrong when retriving client's credentials " + e)
        logging.error(e)
        sys.exit()
