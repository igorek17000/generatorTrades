import logging
import sys

import gspread
from binance.spot import Spot as Client
from oauth2client.service_account import ServiceAccountCredentials

from utils import configlog, gettypeorder, getquantitycoin, formatpriceoco, investimentbalancegreaterthanlimit

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


def createbuyorder(params, coin, investimentbalance):
    if 'BUY' in params:
        buy = params['BUY']
        moeda = coin['Moeda']
        buy[moeda] = {
            "symbol": coin['Moeda'],
            "side": "BUY",
            "type": gettypeorder(coin),
            'recvWindow': 60000,
        }
    else:
        params['BUY'] = {}
        params['BUY'][coin['Moeda']] = {
            "symbol": coin['Moeda'],
            "side": "BUY",
            "type": gettypeorder(coin),
        }
    if gettypeorder(coin) == 'MARKET':
        params['BUY'][coin['Moeda']]["quoteOrderQty"] = investimentbalance
    elif gettypeorder(coin) == 'STOP_LOSS_LIMIT':
        params['BUY'][coin['Moeda']]["timeInForce"] = "GTC"
        params['BUY'][coin['Moeda']]["stopPrice"] = float(coin['ValorCompra'])
        params['BUY'][coin['Moeda']]["price"] = float(coin['ValorCompra'])
        params['BUY'][coin['Moeda']]["quantity"] = getquantitycoin(float(
            investimentbalance / float(params['BUY'][coin['Moeda']]['price'])), coin['Moeda'])
    elif gettypeorder(coin) == 'LIMIT':
        params['BUY'][coin['Moeda']]["timeInForce"] = "GTC"
        params['BUY'][coin['Moeda']]["price"] = float(coin['ValorCompra'])
        params['BUY'][coin['Moeda']]["quantity"] = getquantitycoin(float(
            investimentbalance / float(params['BUY'][coin['Moeda']]['price'])), coin['Moeda'])


def createocoorder(params, coin, investimentbalance):
    if 'SELLOCO' in params:
        selloco = params['SELLOCO']
        moeda = coin['Moeda']
        selloco[moeda] = {
            "symbol": coin['Moeda'],
            "side": "SELL",
            "stopLimitTimeInForce": "GTC",
            "canCreateOco": 0,
            'recvWindow': 60000,
        }
    else:
        params['SELLOCO'] = {}
        params['SELLOCO'][coin['Moeda']] = {}

        params['SELLOCO'][coin['Moeda']] = {
            "symbol": coin['Moeda'],
            "side": "SELL",
            "stopLimitTimeInForce": "GTC",
            "canCreateOco": 0,
            'recvWindow': 60000,
        }
    params['SELLOCO'][coin['Moeda']]['firstTarget'] = {}
    if coin['PrimeiroAlvo'] and coin['SegundoAlvo']:
        params['SELLOCO'][coin['Moeda']]['secondTarget'] = {}
        params['SELLOCO'][coin['Moeda']]['firstTarget']["quantity"] = 0
        params['SELLOCO'][coin['Moeda']]['secondTarget']["quantity"] = 0
        params['SELLOCO'][coin['Moeda']]['firstTarget']["price"] = formatpriceoco(
            float(coin['PrimeiroAlvo']), coin['Moeda'])
        params['SELLOCO'][coin['Moeda']]['secondTarget']["price"] = formatpriceoco(
            float(coin['SegundoAlvo']), coin['Moeda'])
    else:
        params['SELLOCO'][coin['Moeda']]['firstTarget']["quantity"] = getquantitycoin(float(
            investimentbalance / float(params['SELLOCO'][coin['Moeda']]['price']) / 2), coin['Moeda'])
        params['SELLOCO'][coin['Moeda']]['firstTarget']["price"] = formatpriceoco(
            float(coin['PrimeiroAlvo']) - (float(coin['PrimeiroAlvo']) * 0.005), coin['Moeda'])
    params['SELLOCO'][coin['Moeda']]["stopPrice"] = formatpriceoco(float(coin['Stop']) - (float(coin['Stop']) * 0.005),
                                                                   coin['Moeda'])

    params['SELLOCO'][coin['Moeda']]["stopLimitPrice"] = formatpriceoco(
        float(params['SELLOCO'][coin['Moeda']]["stopPrice"]) - float(
            float(params['SELLOCO'][coin['Moeda']]["stopPrice"]) * 0.005), coin['Moeda'])



def organizeordersparams(coins, freebalance):
    params = {}

    for coin in coins:
        investimentbalance = float("{0:.2f}".format(float(freebalance) * (float(coin['Aporte%']) / 100)))
        if investimentbalancegreaterthanlimit(investimentbalance, coin['Moeda']):
            createbuyorder(params, coin, investimentbalance)
            createocoorder(params, coin, investimentbalance)
    return params

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
            if data['Estrategia'] == 'diario':
                clientsdata[data['Membro']]['strategies']['diario']['orders'] = {}
                clientsdata[data['Membro']]['strategies']['diario']['orders'] = organizeordersparams(clientsdata[data['Membro']]['strategies']['diario']['coins'], clientsdata[data['Membro']]['strategies']['diario']['capital_disponivel'])
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