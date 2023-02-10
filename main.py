import json
import re

import schedule
import websocket
from binance.spot import Spot


BASE_URL = 'wss://fstream.binance.com/ws'
FUTURE = 'XRPUSDT'
INTERVAL = '1h'

client = Spot()

def get_max_price():
    max_price = str(client.klines(FUTURE, INTERVAL, limit=1)).split(',')[2]
    max_price = re.sub(r'[^0-9.]+', r'', max_price)

    with open("max_priceXRP.txt", "w") as f:
        f.write(max_price)

get_max_price()

def on_open(ws):
    sub_msg = {"method": "SUBSCRIBE","params":[FUTURE.lower() + '@aggTrade']}
    ws.send(json.dumps(sub_msg))
    print('Connection established')

def on_message(ws, message):
    data = json.loads(message)
    if calc(data['p']) > 1:
        print('Цена упала больше чем на 1%')

def calc(price):
    price = float(price)
    with open('max_priceXRP.txt', 'r') as f:
        max_price = float(f.read())
    result = (max_price-price)/price*100
    return result

ws = websocket.WebSocketApp(BASE_URL,
                            on_open=on_open,
                            on_message=on_message)

ws.run_forever()

def timer():
    schedule.every(1).hours.do(get_max_price)
    while True:
        schedule.run_pending()

if __name__ == '__main__':
    timer()