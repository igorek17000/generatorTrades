import logging

import scheduleOco
from keys import retrievevalidclientsinfos
from order import makeorder
from previousorders import findleftcoins

from utils import configlog, createdatafile

configlog()


def havemissingocos(keylist):
    count = 0
    for data in keyslist:
        buyOrders = keylist[data]['strategies']['diario']['orders']['BUY']
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

for data in keyslist:
    findleftcoins(keyslist[data]['api_key'], keyslist[data]['api_secret'], keyslist[data]['membro'])
    dataclient = makeorder(keyslist[data])
    createdatafile(keyslist)
    keyslist[data].update(dataclient)

if havemissingocos(keyslist) > 0:
    print("starting searching for limit and stop loss limit buy orders ")
    scheduleOco.inicializevariables(keyslist)
