from datetime import datetime
import logging

def configlog():
    date = datetime.today().strftime('%d-%m-%Y')
    filename = "error"+date+".log"
    logging.basicConfig(filename=filename, format='%(name)s - %(levelname)s - %(message)s')





