import csv
import logging
import sys

from utils import configlog


apikey= ''
apisecret = ''
usdtBalance = ''
ordersprice = 0
coinsLocked = []

def organizedata(data):
    datas = data.split(';')
    apikey = datas[0]
    apisecret = datas[1]
    usdtBalance = datas[2]
    ordersprice = float(usdtBalance)/4
    for x in range(3, len(datas)-1):
        coinsLocked.append(datas[x])
def retrievecoinsvalue():
    keyarchive = 'coins.csv'
    with open(keyarchive, 'rt') as archive:
        try:
            reader = csv.reader(archive, delimiter=';')
            for linha in reader:



            return
        except Exception as e:
            print("Something went wrong with the list :" + e)
            logging.error(e)
            sys.exit()

def createorder(data):
    organizedata(data)
    makeorder()


