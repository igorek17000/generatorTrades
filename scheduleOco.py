from apscheduler.schedulers.blocking import BlockingScheduler
import logging
import order
from utils import configlog, getquantity, sendoco, createorderlogfileoco

configlog()

sched = BlockingScheduler()
clientsdata = {}




def sendingoco(params, membro, strategy, apikey, apisecret):
    responseoco = {}
    try:
        if order.validateminnotional(params['firstTarget']['quantity'], params['firstTarget']['price'],
                                     params['symbol']):
            if params['canCreateOco'] and params['secondTarget'] and params['firstTarget']:
                paramfirst = {'symbol': params['symbol'], 'side': params['side'],
                              'quantity': params['firstTarget']['quantity'],
                              'price': params['firstTarget']['price'],
                              'stopPrice': params['stopPrice'],
                              'stopLimitPrice': params['stopLimitPrice'],
                              'stopLimitTimeInForce': params['stopLimitTimeInForce'], }

                responseoco['firstTarget'] = sendoco(apikey, apisecret, **paramfirst)
                paramsecond = {'symbol': params['symbol'], 'side': params['side'],
                               'quantity': params['secondTarget']['quantity'],
                               'price': params['secondTarget']['price'],
                               'stopPrice': params['stopPrice'],
                               'stopLimitPrice': params['stopLimitPrice'],
                               'stopLimitTimeInForce': params['stopLimitTimeInForce'], }
                responseoco['secondTarget'] = sendoco(apikey, apisecret, **paramsecond)
            elif params['canCreateOco']:
                paramfirst = {'symbol': params['symbol'], 'side': params['side'],
                              'quantity': params['firstTarget']['quantity'],
                              'price': params['firstTarget']['price'],
                              'stopPrice': params['stopPrice'],
                              'stopLimitPrice': params['stopLimitPrice'],
                              'stopLimitTimeInForce': params['stopLimitTimeInForce'], }
                responseoco['firstTarget'] = sendoco(apikey, apisecret, **paramfirst)
            params['executed'] = 1
        else:
            logging.error("Something went wrong when send oco for member:" + membro + " and coin:" + params[
                'symbol'] + "the quantityXprice is lower than min_notional")
        for response in responseoco:
            createorderlogfileoco(membro, strategy, responseoco[response])

    except Exception as e:
        print("Something went wrong when send sell orders " + e)
        logging.error("Something went wrong when send sell orders  " + e)


@sched.scheduled_job('interval', minutes=10)
def timed_job():
    for client in clientsdata:
        print("looking for sell orders from client " + client)
        for data in clientsdata[client]['strategies']['diario']['orders']['BUY']:
            clientbuyorder= clientsdata[client]['strategies']['diario']['orders']['BUY'][data]
            quantity = float(getquantity(clientbuyorder['orderId'], data, clientsdata[client]['api_key'], clientsdata[client]['api_secret']))
            if quantity > 0:
                clientsdata[client]['strategies']['diario']['orders']['BUY'][data]['executed'] = 1
                sellorders= clientsdata[client]['strategies']['diario']['orders']['SELLOCO']
                order.reorganizequantity(sellorders,data,quantity)
                sellorder = dict(filter(lambda elem: elem[0] == data, sellorders.items()))
                if len(sellorder) > 0:
                    sendoco(sellorder[data], client, 'diario', clientsdata[client]['api_key'], clientsdata[client]['api_secret'])
        buyOrders = clientsdata[client]['strategies']['diario']['orders']['BUY']
        filteredorders = dict(filter(lambda elem: elem[1]['executed'] < 1, buyOrders.items()))
        buyOrders.clear()
        buyOrders.update(filteredorders)
        #verificar se o cliente está vazio e tirar da lista
        #se lista vazia parar execução

def inicializevariables(data):
    global clientsdata
    clientsdata = data;
    timed_job()
    sched.start()
