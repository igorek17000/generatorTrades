import logging
import sys

import scheduleOco
from keys import retrievevalidclientsinfos
from order import makeorder
from previousorders import findleftcoins

from utils import configlog, createdatafile

configlog()


def havemissingocos(keyslist):
    count = 0
    for data in keyslist:
        buyOrders = keyslist[data]['strategies']['diario']['orders']['BUY']
        filteredorders = dict(filter(lambda elem: elem[1]['type'] != 'MARKET', buyOrders.items()))
        if len(filteredorders) == 0:
            buyOrders.clear()
        else:
            buyOrders.clear()
            buyOrders.update(filteredorders)

            count += 1
    return count
print("retriving datas from sheets...")
keyslist = retrievevalidclientsinfos()

print("Choose what you want to do:")
print("1- just cancel orders from day before")
print("2- do all process")
try:
    value = int(input("input the option: "))
except Exception as e:
    print('error')
    sys.exit()
if value > 1:
    for data in keyslist:
        findleftcoins(keyslist[data]['api_key'], keyslist[data]['api_secret'], keyslist[data]['membro'])
        dataclient = makeorder(keyslist[data])
        keyslist[data].update(dataclient)
    createdatafile(keyslist)
    if havemissingocos(keyslist) > 0:
        print("starting searching for limit and stop loss limit buy orders ")
        scheduleOco.inicializevariables(keyslist)
else:
    for data in keyslist:
        findleftcoins(keyslist[data]['api_key'], keyslist[data]['api_secret'], keyslist[data]['membro'])