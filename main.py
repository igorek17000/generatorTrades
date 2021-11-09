import logging

from keys import retrievevalidkeys
from utils import configlog

configlog()
try:
    keyslist = retrievevalidkeys()
except Exception as e:
    logging.error(e)
