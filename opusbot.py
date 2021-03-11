import hashlib
import hmac
import json
import requests

from time import sleep
import sys
from datetime import datetime

import settings


# API info
API_HOST = 'https://api.miraiex.com'
API_SECRET = b(settings.API_SECRET)
API_CLIENT_ID = settings.API_CLIENT_ID

def json_encode(data):
        return json.dumps(data, separators=(',', ':'), sort_keys=True)

def sign(data):
        j = json_encode(data)
        #print('Signing payload: ' + j)
        h = hmac.new(API_SECRET, msg=j.encode(), digestmod=hashlib.sha256)
        return h.hexdigest()


def timestamp_string():
    return "["+datetime.now().strftime("%I:%M:%S %p")+"]"

class ExchangeInterface:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.USD_DECIMAL_PLACES = 2

    def authenticate(self, login, password):
        if not self.dry_run:
          # self.mtgox.authenticate(login, password)
          print("MiraiEX trading bot")
    def cancel_all_orders(self):
        if self.dry_run:
            return

        #trade_data = self.mtgox.open_orders(); sleep(1)
	# check server time
        response = requests.get(API_HOST + '/time')
        a = response.json()
        #print(a['time'])
        ts = str(a['time'])
        # check balances
        data = {
        'timestamp': (ts),
        'validity': '2000'
	}

        signature = sign(data)

        header = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'miraiex-user-clientid': API_CLIENT_ID,
                'miraiex-user-signature': signature,
        }

        response = requests.get(API_HOST + '/v2/orders/BTCNOK?timestamp='+str(ts)+'&validity=2000', headers=header, data=json_encode(data))
        #print('Cancel_All_Orders: ' + response.text)
        trade_data=response.json()

        #orders = trade_data['orders']
        orders = response.json()
        for order in orders:
            typestring = "sell" if order['type'] == 'ask' else "buy"
            print(timestamp_string(), "Cancelling:", typestring, order['amount'], "@", order['price'])
            #while True:
            #    try:
            #        self.mtgox.cancel(order['oid'], order['type']); sleep(1)
            #    except URLError as e:
            #        print(e.reason)
            #        sleep(10)
            #    except ValueError as e:
            #        print(e)
            #        sleep(10)
            #    else:
            #        break
                # check server time
        response = requests.get(API_HOST + '/time')
        a = response.json()
        #print(a['time'])
        ts = str(a['time'])
        # check balances
        data = {
        'timestamp': (ts),
        'validity': '2000'
        }

        signature = sign(data)

        header = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'miraiex-user-clientid': API_CLIENT_ID,
                'miraiex-user-signature': signature,
        }

        response = requests.delete(API_HOST + '/v2/orders/BTCNOK?timestamp='+str(ts)+'&validity=2000', headers=header, data=json_encode(data))
        #print('DELETEOrders: ' + response.text)
        trade_data=response.text

    def get_ticker(self):
        #ticker = self.mtgox.ticker_data()["ticker"]
	#get last
        response = requests.get(API_HOST + '/v2/markets/BTCNOK')
        a = response.json()

	#get buy/sell
        response = requests.get(API_HOST + '/v2/markets/BTCNOK/ticker')
        b = response.json()

        return {"last": float(a["last"]), "buy": float(b["bid"]), "sell": float(b["ask"])}

    def get_trade_data(self):
        if self.dry_run:
            btc = float(settings.DRY_BTC)
            usd = float(settings.DRY_USD)
            orders = []
        else:
            while True:
                try:

                    # check server time
                    response = requests.get(API_HOST + '/time')
                    a = response.json()
                    ts = str(a['time'])

                    data = {
                            'timestamp': str(ts),
                            'validity': '2000'
                           }

                    signature = sign(data)

                    header = {
                               'Accept': 'application/json',
                               'Content-Type': 'application/json',
                               'miraiex-user-clientid': API_CLIENT_ID,
                               'miraiex-user-signature': signature,
                             }


                    #print('Payload with signature: ' + json_encode(data))
                    response = requests.get(API_HOST + '/v2/balances?timestamp='+str(ts)+'&validity=2000', headers=header, data=json_encode(data))
                    #print(header, json_encode(data))
                    #print('Balances: ' + response.text)
                    trade_data=response.json()
                    sleep(1)
                    #trade_data = self.mtgox.open_orders(); sleep(1)
                except URLError as e:
                    print(e.reason)
                    sleep(10)
                except ValueError as e:
                    print(e)
                    sleep(10)
                else:
                    break
            jsonObj = response.json()
            #print(jsonObj[0]["currency"])
            length = len(jsonObj)
            #print(length)
            for x in range(length):
              #print(x)
              if jsonObj[x]["currency"] == "BTC":
                 coins=jsonObj[x]["balance"]
                 #print(coins) 
                 break
            for x in range(length):
              if jsonObj[x]["currency"] == "NOK":
                 cash=jsonObj[x]["balance"]
                 #print(cash)
                 break

            btc = float(coins)
            usd = float(cash)
            orders = []
            # check server time
            response = requests.get(API_HOST + '/time')
            a = response.json()
            #print(a['time'])
            ts = str(a['time'])
            # check balances
            data = {
            'timestamp': (ts),
            'validity': '2000'
            }

            signature = sign(data)

            header = {
                      'Accept': 'application/json',
                      'Content-Type': 'application/json',
                      'miraiex-user-clientid': API_CLIENT_ID,
                      'miraiex-user-signature': signature,
             }

            response = requests.get(API_HOST + '/v2/orders/BTCNOK?timestamp='+str(ts)+'&validity=2000', headers=header, data=json_encode(data))
            #print('Balance Orders: ' + response.text)
            #trade_data=response.json()

            #orders = trade_data['orders']
            orders = response.json()
            #orders = json.loads(response.text)
            #orders = response.text
            #print(orders)
            orders2=[]            

            if orders:
               #print(len(orders))
               for x in range(len(orders)):
                    #print(x)
                    order = {"id": orders[x]["id"], "price": float(orders[x]["price"]), "amount": float(orders[x]["amount"])}
                    order["type"] = "sell" if orders[x]["type"] == 'ask'  else "buy"
                    orders2.append(order)
            #print(orders)

               #for o in orders:
               #    order = {"id": o["id"], "price": float(o["price"]), "amount": float(o["amount"])}
               #    order["type"] = "sell" if o["type"] == 'ask'  else "buy"
               #    orders.append(order)
        return {"btc": btc, "usd": usd, "orders": orders2}

    def place_order(self, price, amount, order_type):
        if settings.DRY_RUN:
            print(timestamp_string(), order_type.capitalize() + ":", amount, "@", price)
            return None

        if order_type == "buy":
            #order_id = self.mtgox.buy(amount, price)["oid"]
            #print("buying")
            # check server time
            response = requests.get(API_HOST + '/time')

            a = response.json()
            #print(a['time'])

            ts = int(a['time'])
            # place buy
            data = {
                    'timestamp': str(ts),
                    'validity': '2000',
                    'market': 'BTCNOK',
                    'type': 'bid',
                    'price': str(price),
                    'amount': str(amount)

            }

            signature = sign(data)

            header = {
                      'Accept': 'application/json',
                      'Content-Type': 'application/json',
                      'miraiex-user-clientid': API_CLIENT_ID,
                      'miraiex-user-signature': signature,
            }



            response = requests.post(API_HOST + '/v2/orders?timestamp='+str(ts)+'&validity=2000', headers=header, data=json_encode(data))
            #print(header, json_encode(data))
            print('order ID: ' + response.text)
            
            tmp=response.json()
            order_id = (tmp['id'])
        elif order_type == "sell":
            #order_id = self.mtgox.sell(amount, price)["oid"]
            #print("selling")
            # check server time
            response = requests.get(API_HOST + '/time')

            a = response.json()
            #print(a['time'])

            ts = int(a['time'])
            # place buy
            data = {
                    'timestamp': str(ts),
                    'validity': '2000',
                    'market': 'BTCNOK',
                    'type': 'ask',
                    'price': str(price),
                    'amount': str(amount)

            }

            signature = sign(data)

            header = {
                      'Accept': 'application/json',
                      'Content-Type': 'application/json',
                      'miraiex-user-clientid': API_CLIENT_ID,
                      'miraiex-user-signature': signature,
            }



            response = requests.post(API_HOST + '/v2/orders?timestamp='+str(ts)+'&validity=2000', headers=header, data=json_encode(data))
            #print(header, json_encode(data))
            print('order ID: ' + response.text)

            tmp2=response.json()
            order_id = (tmp2['id'])


        else:
            print("Invalid order type")
            exit()

        print(timestamp_string(), order_type.capitalize() + ":", amount, "@", price, "id:", order_id)

        return order_id

class OrderManager:
    def __init__(self):
        self.exchange = ExchangeInterface(settings.DRY_RUN)
        self.exchange.authenticate(settings.LOGIN, settings.PASSWORD)
        self.start_time = datetime.now()
        self.reset()

    def reset(self):
        self.exchange.cancel_all_orders()
        self.orders = {}

        ticker = self.exchange.get_ticker()
        self.start_position = ticker["last"]
        trade_data = self.exchange.get_trade_data()
        self.start_btc = trade_data["btc"]
        self.start_usd = trade_data["usd"]
        print(timestamp_string(), "BTC:", self.start_btc, "  NOK:", self.start_usd)

        # Sanity check:
        if self.get_position(-1) >= ticker["sell"] or self.get_position(1) <= ticker["buy"]:
            print(self.start_position)
            print(self.get_position(-1), ticker["sell"], self.get_position(1), ticker["buy"])
            print("Sanity check failed, exchange data is screwy")
            exit()

        for i in range(1, settings.ORDER_PAIRS + 1):
            self.place_order(-i, "buy")
            self.place_order(i, "sell")

        if settings.DRY_RUN:
            exit()

    def get_position(self, index):
        return round(self.start_position * (1+settings.INTERVAL)**index, self.exchange.USD_DECIMAL_PLACES)

    def place_order(self, index, order_type):
        position = self.get_position(index)
        order_id = self.exchange.place_order(position, settings.ORDER_SIZE, order_type)
        self.orders[index] = {"id": order_id, "type": order_type}

    def check_orders(self):
        trade_data = self.exchange.get_trade_data()
        order_ids = [o["id"] for o in trade_data["orders"]]
        old_orders = self.orders.copy()
        print(old_orders)
        print_status = True

        for index, order in old_orders.items():
            if order["id"] not in order_ids:
                print("Order filled, id:", order["id"])
                del self.orders[index]
                if order["type"] == "buy":
                    self.place_order(index + 1, "sell")
                else:
                    self.place_order(index - 1, "buy")
                print_status = True

        num_buys = 0
        num_sells = 0

        for order in self.orders.values():
            if order["type"] == "buy":
                num_buys += 1
            else:
                num_sells += 1

        if num_buys < settings.ORDER_PAIRS:
            low_index = min(self.orders.keys())
            if num_buys == 0:
                # No buy orders left, so leave a gap
                low_index -= 1
            for i in range(1, settings.ORDER_PAIRS - num_buys + 1):
                self.place_order(low_index-i, "buy")

        if num_sells < settings.ORDER_PAIRS:
            high_index = max(self.orders.keys())
            if num_sells == 0:
                # No sell orders left, so leave a gap
                high_index += 1
            for i in range(1, settings.ORDER_PAIRS - num_sells + 1):
                self.place_order(high_index+i, "sell")

        if print_status:
            btc = trade_data["btc"]
            usd = trade_data["usd"]
            print("Profit:", btc - self.start_btc, "BTC,", usd - self.start_usd, "NOK   Run Time:", datetime.now() - self.start_time)


    def run_loop(self):
        while True:
            sleep(60)
            self.check_orders()
            sys.stdout.write(".")
            sys.stdout.flush()



om = OrderManager()
om.run_loop()
