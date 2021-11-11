import logging
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


def createorder(data):
    organizedata(data)
    makeorder()


