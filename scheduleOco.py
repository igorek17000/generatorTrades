from apscheduler.schedulers.blocking import BlockingScheduler
from binance.spot import Spot as Client

import logging

import order
from utils import configlog

configlog()

sched = BlockingScheduler()
clientsdata = {}


def getquantity(orderid, symbol, apikey, apisecret):
    client = Client(apikey, apisecret)
    try:
        response = client.get_order(symbol, orderId=orderid)
        if response['status'] == 'FILLED':
            return response['executedQty']
        else:
            return 0
    except Exception as e:
        print("Something went wrong when request order info " + e)
        logging.error("Something went wrong when request order info " + e)


def sendoco(params, membro, strategy, apikey, apisecret):
    client = Client(apikey, apisecret)
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

                responseoco['firstTarget'] = client.new_oco_order(**paramfirst)
                paramsecond = {'symbol': params['symbol'], 'side': params['side'],
                               'quantity': params['secondTarget']['quantity'],
                               'price': params['secondTarget']['price'],
                               'stopPrice': params['stopPrice'],
                               'stopLimitPrice': params['stopLimitPrice'],
                               'stopLimitTimeInForce': params['stopLimitTimeInForce'], }
                responseoco['secondTarget'] = client.new_oco_order(**paramsecond)
            elif params['canCreateOco']:
                paramfirst = {'symbol': params['symbol'], 'side': params['side'],
                              'quantity': params['firstTarget']['quantity'],
                              'price': params['firstTarget']['price'],
                              'stopPrice': params['stopPrice'],
                              'stopLimitPrice': params['stopLimitPrice'],
                              'stopLimitTimeInForce': params['stopLimitTimeInForce'], }
                responseoco['firstTarget'] = client.new_oco_order(**paramfirst)
            params['executed'] = 1
        else:
            logging.error("Something went wrong when send oco for member:" + membro + " and coin:" + params[
                'symbol'] + "the quantityXprice is lower than min_notional")
        for response in responseoco:
            order.createorderlogfileoco(membro, strategy, responseoco[response])

    except Exception as e:
        print("Something went wrong when send sell orders " + e)
        logging.error("Something went wrong when send sell orders  " + e)


@sched.scheduled_job('interval', minutes=1)
def timed_job():
    for client in clientsdata:
        print("looking for sell orders from client " + client)
        for data in clientsdata[client]['strategies']['diario']['orders']['BUY']:
            clientbuyorder= clientsdata[client]['strategies']['diario']['orders']['BUY'][data]
            quantity = getquantity(clientbuyorder['orderId'], data, clientsdata[client]['api_key'], clientsdata[client]['api_secret'])
            if quantity > 0:
                order.reorganizequantity()
                clientsdata[client]['strategies']['diario']['orders']['BUY'][data]['executed'] = 1
                sellorders= clientsdata[client]['strategies']['diario']['orders']['SELLOCO']
                order.reorganizequantity(sellorders,data,quantity)
                sellorder = dict(filter(lambda elem: elem[0] == data, sellorders.items()))
                if len(sellorder) > 0:
                    sendoco(sellorder[data], client, 'diario', clientsdata[client]['api_key'], clientsdata[client]['api_secret'])
        buyOrders = clientsdata[client]['strategies']['diario']['orders']['BUY']
        filteredorders = dict(filter(lambda elem: elem[1]['executed'] < 1, buyOrders.items()))
        buyOrders.update(filteredorders)

def inicializevariables(data):
    global clientsdata
    clientsdata = data;
    timed_job()
    sched.start()
