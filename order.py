
import math
import logging
import sys
import time

from utils import configlog, sendorder, sendoco, createorderlogfilebuy, createorderlogfileoco, reorganizequantity, \
    exchangeinfo, getquantitycoin, validateminnotional

configlog()

def makeorder(dataclient):
    apikey = dataclient['api_key']
    apisecret = dataclient['api_secret']
    strategies = dataclient['strategies']

    for data in strategies:
        print("sending buy orders from client: " + dataclient['membro'] + "indice:" + data)
        sendingorder(data['orders'], dataclient['membro'], data, apikey, apisecret)
        filteredsellorders = dict(filter(lambda elem: elem[1]['canCreateOco'] > 0, data['orders']['SELLOCO'].items()))
        sendingoco(filteredsellorders, dataclient['membro'], data, apikey, apisecret)
    return dataclient


def sendingorder(params, membro, strategy, apikey, apisecret):
    for param in params['BUY']:
        orderdata = params['BUY'][param]
        try:
            response = sendorder(apikey, apisecret, orderdata)
            if params['BUY'][param]['type'] == 'MARKET':
                createorderlogfilebuy(membro, strategy, response, params['BUY'][param]['quoteOrderQty'])
            else:
                createorderlogfilebuy(membro, strategy, response, 0)
            if params['BUY'][param]['type'] == 'MARKET' and response['status'] == 'FILLED':
                quantity = response['executedQty']
                reorganizequantity(params['SELLOCO'], params['BUY'][param]['symbol'], float(quantity), 1)
                params['BUY'][param]['executed'] = 1
            else:
                params['BUY'][param]['orderId'] = response['orderId']
                params['BUY'][param]['executed'] = 0
            time.sleep(0.075)
        except Exception as e:
            pass
            errorStack = str(e)
            print("Something went wrong when buy orders, for details look to error.log")
            logging.error("Something went wrong when buy coins for member: " + membro + " and coin: " + orderdata[
                'symbol'] + ' error: ' + errorStack)


def sendingoco(params, membro, strategy, apikey, apisecret):
    print("sending oco orders from client: " + membro + "indice:" + strategy)
    responseoco = {}
    try:
        for param in params:

            if validateminnotional(params[param]['firstTarget']['quantity'], params[param]['firstTarget']['price'],
                                   params[param]['symbol']):
                if params[param]['canCreateOco'] and params[param]['secondTarget'] and params[param]['firstTarget']:
                    paramfirst = {'symbol': params[param]['symbol'], 'side': params[param]['side'],
                                  'quantity': params[param]['firstTarget']['quantity'],
                                  'price': params[param]['firstTarget']['price'],
                                  'stopPrice': params[param]['stopPrice'],
                                  'stopLimitPrice': params[param]['stopLimitPrice'],
                                  'stopLimitTimeInForce': params[param]['stopLimitTimeInForce'], }

                    responseoco['firstTarget'] = sendoco(apikey, apisecret, paramfirst)
                    paramsecond = {'symbol': params[param]['symbol'], 'side': params[param]['side'],
                                   'quantity': params[param]['secondTarget']['quantity'],
                                   'price': params[param]['secondTarget']['price'],
                                   'stopPrice': params[param]['stopPrice'],
                                   'stopLimitPrice': params[param]['stopLimitPrice'],
                                   'stopLimitTimeInForce': params[param]['stopLimitTimeInForce'], }
                    responseoco['secondTarget'] = sendoco(apikey, apisecret, paramsecond)
                elif params[param]['canCreateOco']:
                    paramfirst = {'symbol': params[param]['symbol'], 'side': params[param]['side'],
                                  'quantity': params[param]['firstTarget']['quantity'],
                                  'price': params[param]['firstTarget']['price'],
                                  'stopPrice': params[param]['stopPrice'],
                                  'stopLimitPrice': params[param]['stopLimitPrice'],
                                  'stopLimitTimeInForce': params[param]['stopLimitTimeInForce'], }
                    responseoco['firstTarget'] = sendoco(apikey, apisecret, paramfirst)
                params[param]['executed'] = 1
            else:
                logging.error("Something went wrong when send oco for member: " + membro + " and coin:" + params[param][
                    'symbol'] + "the quantityXprice is lower than min_notional")
            for response in responseoco:
                createorderlogfileoco(membro, strategy, responseoco[response])

    except Exception as e:
        errorStack = str(e)
        print("Something went wrong when send sell orders " + errorStack)
        logging.error("Something went wrong when send sell orders  " + errorStack)
