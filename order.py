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
    # use creds to create a client to interact with the Google Drive API
    try:
        scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
        client = gspread.authorize(creds)

        sheet = client.open("test_coins").sheet1

        list_of_hashes = sheet.get_all_records()


    except Exception as e:
            print("Something went wrong when retriving coins value" + e)
            logging.error(e)
            sys.exit()





def createorder(data):
    """organizedata(data)
    makeorder()"""
