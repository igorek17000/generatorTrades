import logging
import sys

import scheduleOco
from keys import retrievevalidclientsinfos
from order import makeorder
from previousorders import findleftcoins

from utils import configlog, createdatafile

configlog()


def havemissingocos(keyslist):
    count = 0
    for data in keyslist:
        buyOrders = keyslist[data]['strategies']['diario']['orders']['BUY']
        filteredorders = dict(filter(lambda elem: elem[1]['type'] != 'MARKET', buyOrders.items()))
        if len(filteredorders) == 0:
            buyOrders.clear()
        else:
            buyOrders.clear()
            buyOrders.update(filteredorders)
            count += 1
    return count


print("retriving datas from sheets...")
keyslist = retrievevalidclientsinfos()
"""{"fernando_ipiranga": {"membro": "fernando_ipiranga", "api_key": "Kdf7yfQ96HQ35Hb2728k0mjjVv2Xsy3TPUMlplfwtcHewszAS108T16pg0SbgWTM", "api_secret": "La24FklTvAJjObxuLUH27ezTFbIio9OAv4HEx8esBEP1MTRd8CDY77pCIL3oeDBS", "strategies": {"diario": {"strategy": "diario", "capital_disponivel": "126.65", "coins": [{"Moeda": "ETCUSDT", "FlagCompraValida": "S", "TipoCompra": "acima", "ValorCompra": "28.3000", "Aporte%": "23.50", "Aporte($)": "29.76", "PrimeiroAlvo": "30.7500", "SegundoAlvo": "32.6500", "Stop": "26.2000"}, {"Moeda": "AVAXUSDT", "FlagCompraValida": "S", "TipoCompra": "acima", "ValorCompra": "78.5000", "Aporte%": "23.50", "Aporte($)": "29.76", "PrimeiroAlvo": "85.4500", "SegundoAlvo": "90.3000", "Stop": "74.4000"}, {"Moeda": "SOLUSDT", "FlagCompraValida": "S", "TipoCompra": "acima", "ValorCompra": "91.2000", "Aporte%": "23.50", "Aporte($)": "29.76", "PrimeiroAlvo": "94.1000", "SegundoAlvo": "99.1000", "Stop": "84.9000"}, {"Moeda": "ADAUSDT", "FlagCompraValida": "S", "TipoCompra": "market", "ValorCompra": "-", "Aporte%": "23.50", "Aporte($)": "29.76", "PrimeiroAlvo": "0.9640", "SegundoAlvo": "1.0150", "Stop": "0.8400"}], "orders": {"BUY": {"ETCUSDT": {"symbol": "ETCUSDT", "side": "BUY", "type": "STOP_LOSS_LIMIT", "timeInForce": "GTC", "stopPrice": 28.3, "price": 28.3, "quantity": 1.05}, "AVAXUSDT": {"symbol": "AVAXUSDT", "side": "BUY", "type": "STOP_LOSS_LIMIT", "recvWindow": 60000, "timeInForce": "GTC", "stopPrice": 78.5, "price": 78.5, "quantity": 0.37, "orderId": 1316385961, "executed": 0}, "SOLUSDT": {"symbol": "SOLUSDT", "side": "BUY", "type": "STOP_LOSS_LIMIT", "recvWindow": 60000, "timeInForce": "GTC", "stopPrice": 91.2, "price": 91.2, "quantity": 0.32, "orderId": 2224482361, "executed": 0}, "ADAUSDT": {"symbol": "ADAUSDT", "side": "BUY", "type": "MARKET", "recvWindow": 60000, "quoteOrderQty": 29.76, "executed": 1}}, "SELLOCO": {"ETCUSDT": {"symbol": "ETCUSDT", "side": "SELL", "stopLimitTimeInForce": "GTC", "canCreateOco": 0, "recvWindow": 60000, "firstTarget": {"quantity": 0, "price": 30.75}, "secondTarget": {"quantity": 0, "price": 32.65}, "stopPrice": 26.06, "stopLimitPrice": 25.92}, "AVAXUSDT": {"symbol": "AVAXUSDT", "side": "SELL", "stopLimitTimeInForce": "GTC", "canCreateOco": 0, "recvWindow": 60000, "firstTarget": {"quantity": 0, "price": 85.45}, "secondTarget": {"quantity": 0, "price": 90.3}, "stopPrice": 74.02, "stopLimitPrice": 73.64}, "SOLUSDT": {"symbol": "SOLUSDT", "side": "SELL", "stopLimitTimeInForce": "GTC", "canCreateOco": 0, "recvWindow": 60000, "firstTarget": {"quantity": 0, "price": 94.1}, "secondTarget": {"quantity": 0, "price": 99.1}, "stopPrice": 84.47, "stopLimitPrice": 84.04}, "ADAUSDT": {"symbol": "ADAUSDT", "side": "SELL", "stopLimitTimeInForce": "GTC", "canCreateOco": 1, "recvWindow": 60000, "firstTarget": {"quantity": 19.6, "price": 0.964}, "secondTarget": {"quantity": 19.6, "price": 1.014}, "stopPrice": 0.835, "stopLimitPrice": 0.83}}}}}}, "caroline_dourado": {"membro": "caroline_dourado", "api_key": "ECUBSAWveDXTDYYY4rt2ZnVW7OifUQnR0xLgYEnJENU8YVq4ougBGV3OiSNZDeZ7", "api_secret": "GClfeo1d7ALRh3CGk7pLpdphgcpj2NqyCGff963y1xJgodmF2kumLveEcaYRmlsE", "strategies": {"diario": {"strategy": "diario", "capital_disponivel": "133.28", "coins": [{"Moeda": "ETCUSDT", "FlagCompraValida": "S", "TipoCompra": "acima", "ValorCompra": "28.3000", "Aporte%": "23.50", "Aporte($)": "31.32", "PrimeiroAlvo": "30.7500", "SegundoAlvo": "32.6500", "Stop": "26.2000"}, {"Moeda": "AVAXUSDT", "FlagCompraValida": "S", "TipoCompra": "acima", "ValorCompra": "78.5000", "Aporte%": "23.50", "Aporte($)": "31.32", "PrimeiroAlvo": "85.4500", "SegundoAlvo": "90.3000", "Stop": "74.4000"}, {"Moeda": "SOLUSDT", "FlagCompraValida": "S", "TipoCompra": "acima", "ValorCompra": "91.2000", "Aporte%": "23.50", "Aporte($)": "31.32", "PrimeiroAlvo": "94.1000", "SegundoAlvo": "99.1000", "Stop": "84.9000"}, {"Moeda": "ADAUSDT", "FlagCompraValida": "S", "TipoCompra": "market", "ValorCompra": "-", "Aporte%": "23.50", "Aporte($)": "31.32", "PrimeiroAlvo": "0.9640", "SegundoAlvo": "1.0150", "Stop": "0.8400"}]}}}}"""

print("Choose what you want to do:")
print("1- just cancel orders from day before")
print("2- do all process")
try:
    value = int(input("input the option: "))
except Exception as e:
    print('error')
    sys.exit()
if value > 1:
    for data in keyslist:
        findleftcoins(keyslist[data]['api_key'], keyslist[data]['api_secret'], keyslist[data]['membro'])
        dataclient = makeorder(keyslist[data])
        keyslist[data].update(dataclient)
    createdatafile(keyslist)
    if havemissingocos(keyslist) > 0:
        print("starting searching for limit and stop loss limit buy orders ")
        scheduleOco.inicializevariables(keyslist)
else:
    for data in keyslist:
        findleftcoins(keyslist[data]['api_key'], keyslist[data]['api_secret'], keyslist[data]['membro'])