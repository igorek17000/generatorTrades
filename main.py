import logging

from keys import retrievevalidkeys
from order import createorder
from utils import configlog

configlog()
try:
    keyslist = retrievevalidkeys()
    for data in keyslist:
        createorder(data)
except Exception as e:
    logging.error(e)
