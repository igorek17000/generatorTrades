import logging

def configlog():
    logging.basicConfig(filename='error.log', format='%(name)s - %(levelname)s - %(message)s')
    logging.warning('This message will get logged on to a file')




