import json
import socket

TCP_IP = 'production'#'10.0.102.124'
TCP_PORT = 25000
BUFFER_SIZE = 1024

ID = 0

# Create TCP socket object s
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Skip optional step to bind s (socket will choose outgoing port for you)

# Connect s to IP/port defined above
s.connect((TCP_IP, TCP_PORT))

s.send(json.dumps({"type": "hello", "team": "THETARTANS"}))
s.send("\n")
#mrlazynickell


def readlines(sock, recv_buffer=1024, delim='\n'):
    print "Reading line"
    buffer = ''
    data = True
    while data:
        data = sock.recv(recv_buffer)
        buffer += data

        while buffer.find(delim) != -1:
            line, buffer = buffer.split('\n', 1)
            yield line
    return


class Stock:
    def __init__(self, sym, best_buy, best_sell):
        self.sym = sym
        self.size = 0
        self.best_buy = best_buy
        self.best_sell = best_sell
        self.spread = best_sell - best_buy
        self.mid = (best_buy + best_sell) / 2
        self.last_buy = None
        self.last_sell = None
        self.orders = []
    
    def update_spread(self):
        self.spread = best_sell - best_buy
        self.mid = (best_buy + best_sell) / 2
    
    def buy_size(self):
        return 6
        if self.size <= -70:
            return 4 + abs(self.size)//5
        elif self.size >= 70:
            return 3
        else:
            return 5
    
    def sell_size(self):
        return 6
        if self.size >= 10:
            return 4 + self.size//5 
        elif self.size <= 10:
            return 3
        else:
            return 5

    def highest_buy(self):
        largest = 0
        for order in self.orders:
            if order["price"] > largest and order["dir"] == "BUY":
                largest = order["price"]
        return largest

    def smallest_sell(self):
        smallest = Ellipsis
        for order in self.orders:
            if order["price"] < smallest and order["dir"] == "SELL":
                smallest = order["price"]
        return smallest

    def remove_order(self, order_id):
        order_index = None
        for i in xrange(len(self.orders)):
            if self.orders[i]["order_id"] == order_id:
                order_index = i
        if (order_index != None): 
            self.orders.pop(i)

    def clean_orders(self):
        best_buy = self.highest_buy()
        best_sell = self.smallest_sell()
        
        new_orders = []
        for i in xrange(len(self.orders)):
            if (self.orders[i]["dir"] == "BUY" and self.orders[i]["price"] != best_buy or
                self.orders[i]["dir"] == "SELL" and self.orders[i]["price"] != best_sell):
                send_cancel(self.orders[i]["order_id"])
            else:
                new_orders.append(self.orders[i])
        
        self.orders = new_orders

stocks = dict()

def hedgeXLF(size, way):
     #buy 3 bond
     #send_offer(way, "BOND", 1000, size//3)
     #buy 2 GS
     send_offer(way, "GS", stocks["GS"].mid, size//2)
     #buy 3 MS
     send_offer(way, "MS", stocks["MS"].mid, size//3)
     #buy 2 WFC
     send_offer(way, "WFC", stocks["WFC"].mid, size//2)

def send_cancel(order_id):
    s.send(json.dumps({"type":"cancel", "order_id": order_id}))
    s.send("\n")

def send_offer(way, sym, price, size):
    global ID
    offer = {"type": "add",
             "order_id": ID, 
             "symbol": sym, 
             "dir": way, 
             "price": price, 
             "size": size}
   # print offer, "this is in send offer"
    stocks[sym].orders.append(offer)
    s.send(json.dumps(offer))
    s.send("\n")
            
    ID += 1

for line in readlines(s):
    line = json.loads(line)

    if line["type"] == "error":
        print line["error"]
    
    if line["type"] == "fill":
        numbercompleted = line["size"]
        if line["dir"] == "BUY":
            stocks[line["symbol"]].size += numbercompleted
        elif line["dir"]  == "SELL":
            stocks[line["symbol"]].size -= numbercompleted
        stocks[line["symbol"]].remove_order(line["order_id"])
        
    if line["type"] == "book":
        sym = line["symbol"]
        
        
        # Best buy and sell prices
        if len(line["buy"]) == 0 or len(line["sell"]) == 0: 
            continue
        best_buy = line["buy"][0][0]
        best_sell = line["sell"][0][0]
        
        if sym in stocks.keys():
            if (best_buy == stocks[sym].best_buy 
                and best_sell == stocks[sym].best_sell):
                continue
            else:
                stocks[sym].best_buy = best_buy
                stocks[sym].best_sell = best_sell
                stocks[sym].update_spread()
        else:
            stocks[sym] = Stock(sym, best_buy, best_sell)
    
        if sym == "VALE":
            if "VALBZ" in stocks.keys():
                fair_value = stocks["VALBZ"].mid
                if fair_value > stocks["VALE"].mid and stocks["VALBZ"].highest_buy() < best_buy:
                    buy_price = stocks["VALE"].best_buy + 1
                    send_offer("BUY", "VALE", buy_price, 1)
                    #hedge Vale
                    send_offer("SELL", "VALBZ", stocks["VALBZ"].mid, 1)
                elif fair_value < stocks["VALE"].mid and stocks["VALBZ"].smallest_sell() > best_sell:
                    sell_price = stocks["VALE"].best_sell - 1
                    send_offer("SELL", "VALE", sell_price, 1)
                    #hedge Vale
                    send_offer("BUY", "VALBZ", stocks["VALBZ"].mid, 1)
           
        elif  sym == "XLF":
            # Calculate fair value from other bids
            if ("GS" in stocks.keys() and 
               "MS" in stocks.keys() and 
               "WFC" in stocks.keys()):
                fair_value = (3000 + 
                             2 * stocks["GS"].mid + 
                             3 * stocks["MS"].mid +
                             2 * stocks["WFC"].mid) / 10
                # print "fair_value:", fair_value, "mid:", stocks["XLF"].mid, "highest:", stocks["XLF"].highest_buy(), "best:",best_buy
                if fair_value > stocks["XLF"].mid and stocks["XLF"].highest_buy() < best_buy:
                    buy_price = stocks[sym].best_buy + 1
                    size = stocks[sym].buy_size()
                    send_offer("BUY", sym, buy_price, size)
                    hedgeXLF(size, "SELL")
                if fair_value < stocks["XLF"].mid and stocks["XLF"].smallest_sell() > best_sell:
                 #   print "we sellin"
                    size = stocks[sym].sell_size()
                    sell_price = stocks[sym].best_sell - 1
                    send_offer("SELL", sym, sell_price, size)
                    hedgeXLF(size, "BUY")
            
        elif sym == "BOND":
            # If best buy is less than 999, offer 1 penny greater
            if stocks[sym].best_buy < 999: 
                buy_price = stocks[sym].best_buy + 1
                send_offer("BUY", sym, buy_price, 10)
            # If best sell is greater than 1001, offer 1 penny less
            if stocks[sym].best_sell > 1001: 
                sell_price = stocks[sym].best_sell - 1
                send_offer("SELL", sym, sell_price, 10)     
        
        stocks[sym].clean_orders()
