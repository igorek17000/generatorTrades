import logging
from keys import retrievevalidclientsinfos
from order import makeorder

from utils import configlog

configlog()
try:
    print("retriving datas from sheets...")
    keyslist = retrievevalidclientsinfos()
    for data in keyslist:
        makeorder(keyslist[data])
except Exception as e:
    logging.error(e)
