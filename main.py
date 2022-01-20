import logging

import scheduleOco
from keys import retrievevalidclientsinfos
from order import makeorder

from utils import configlog

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
try:
    print("retriving datas from sheets...")
    keyslist = retrievevalidclientsinfos()
    for data in keyslist:
     dataclient = makeorder(keyslist[data])
     keyslist[data].update(dataclient)


    if havemissingocos(keyslist) > 0:
        print("starting searching for limit and stop loss limit buy orders ")
        scheduleOco.inicializevariables(keyslist)

except Exception as e:
    logging.error(e)



