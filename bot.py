import websocket, json, pprint, talib, numpy
from decouple import config
from binance.client import Client
from binance.enums import *
import ssl
import time
import certifi





#### This Is Bot
SOCKET = "wss://stream.binance.com:9443/ws/irisusdt@kline_1m"

RSI_PERIOD = 5
RSI_OVERBOUGHT = 30
RSI_OVERSOLD = 100
TRADE_SYMBOL = 'IRISUSDT'
TRADE_QUANTITY = 100

closes = []
in_position = False

API_KEY = config('API_KEY')
API_SECRET = config('API_SECRET')
client = Client(API_KEY, API_SECRET, {"verify": True, "timeout": 60})

fees = client.get_trade_fee(symbol=TRADE_SYMBOL)
print(fees)

# fee = fees[0]['makerCommission'] 

# print(float(fee))

# S_QUANTITY = TRADE_QUANTITY - float(fee)
 
SELL_QUANTITY = TRADE_QUANTITY - 1
def order(side, quantity, symbol,order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return True

def on_message(ws, message):
    print(message)

def on_error(ws, error):
    print(error)
        
def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global closes, in_position
    
    print('received message')
    json_message = json.loads(message)
    pprint.pprint(json_message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']

    if is_candle_closed:
        print("candle closed at {}".format(close))
        closes.append(float(close))
        print("closes")
        print(closes)

        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            print("all rsis calculated so far")
            print(rsi)
            last_rsi = rsi[-1]
            print("the current rsi is {}".format(last_rsi))

            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                    print("Overbought! Sell! Sell! Sell!")
                    # put binance sell logic here
                    order_succeeded = order(SIDE_SELL, SELL_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = False
                else:
                    print("It is overbought, but we don't own any. Nothing to do.")
            
            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    print("It is oversold, but you already own it, nothing to do.")
                else:
                    print("Oversold! Buy! Buy! Buy!")
                    # put binance buy order logic here
                    order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = True


if __name__ == "__main__":
    websocket.enableTrace(True)         
    ws = websocket.WebSocketApp(SOCKET,
                              on_open = on_open,
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})