import logging
from keys import retrievevalidkeys
from order import adjustparam
from utils import configlog

configlog()
try:
    keyslist = retrievevalidkeys()
    for data in keyslist:
        adjustparam(keyslist[data])
except Exception as e:
    logging.error(e)
