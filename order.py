import csv
import logging
import sys
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from utils import configlog

apikey = ''
apisecret = ''
usdtBalance = ''
ordersprice = 0
coinsLocked = []


def organizedata(data):
    datas = data.split(';')
    apikey = datas[0]
    apisecret = datas[1]
    usdtBalance = datas[2]
    ordersprice = float(usdtBalance) / 4
    for x in range(3, len(datas) - 1):
        coinsLocked.append(datas[x])


def retrievecoinsvalue():



def makeorder():
    params = {
        "symbol": "BTCUSDT",
        "side": "BUY",
        "type": "MARKET",
        "quoteOrderQty": "100"
    }

    client = Client(key, secret)

    try:
        response = client.new_order_test(**params)
        logging.info(response)
    except Exception as e:
        print("Something went wrong when make order" + e)
        logging.error(e)
        sys.exit()


retrievecoinsvalue()
def createorder(data):
    """organizedata(data)
    makeorder()"""
