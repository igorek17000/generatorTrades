import logging

def configlog():
    logging.basicConfig(filename='error.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
    logging.warning('This message will get logged on to a file')




