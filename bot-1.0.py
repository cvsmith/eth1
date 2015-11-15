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

    def clean(self, new_fair):
        for x in xrange(len(self.orders)):
            for order in self.orders:
              #  print type(order)
              #  print order
                if (order["dir"] == "BUY" and 
                    order["price"] >= new_fair):
                    send_cancel(order["order_id"])
                    self.orders.pop(self.orders.index(order))
                elif (order["dir"] == "SELL" and
                    order["price"] <= new_fair):
                    send_cancel(order["order_id"])
                    self.orders.pop(self.order.index(order))

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
        smallest = None
        for order in self.orders:
            if smallest == None or order["price"] < smallest and order["dir"] == "SELL":
                smallest = order["price"]
        return smallest


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
           
        if  sym == "XLF":
            # Calculate fair value from other bids
            if ("GS" in stocks.keys() and 
               "MS" in stocks.keys() and 
               "WFC" in stocks.keys()):
                fair_value = (3000 + 
                             2 * stocks["GS"].mid + 
                             3 * stocks["MS"].mid +
                             2 * stocks["WFC"].mid) / 10
                if fair_value > stocks["XLF"].mid and stocks["XLF"].highest_buy() < best_buy:
                    buy_price = stocks[sym].best_buy + 1
                    size = stocks[sym].buy_size()
                    send_offer("BUY", sym, buy_price, size)
                    hedgeXLF(size, "SELL")
                #print "fair_value:", fair_value, "mid:", stocks["XLF"].mid, "smallest:", stocks["XLF"].smallest_sell(), "best:",best_sell
                if fair_value < stocks["XLF"].mid and stocks["XLF"].smallest_sell() > best_sell:
                 #   print "we sellin"
                    size = stocks[sym].sell_size()
                    sell_price = stocks[sym].best_sell - 1
                    send_offer("SELL", sym, sell_price, size)
                    hedgeXLF(size, "BUY")
                stocks[sym].clean(fair_value)
            
        if sym == "BOND":
            # If best buy is less than 999, offer 1 penny greater
            if stocks[sym].best_buy < 999: 
                buy_price = stocks[sym].best_buy + 1
                send_offer("BUY", sym, buy_price, 10)
            # If best sell is greater than 1001, offer 1 penny less
            if stocks[sym].best_sell > 1001: 
                sell_price = stocks[sym].best_sell - 1
                send_offer("SELL", sym, sell_price, 10)    
     
'''        elif sym == "VALE":
            if "VALBZ" in stocks.keys():
                fair_value = stocks["VALBZ"].mid
                if fair_value > stocks["VALE"].mid:
                    buy_price = stocks["VALE"].best_buy + 1
                    send_offer("BUY", "VALE", buy_price, 1)
                elif fair_value < stocks["VALE"].mid:
                    sell_price = stocks["VALE"].best_sell - 1
                    send_offer("SELL", "VALE", sell_price, 1)
                stocks[sym].clean(fair_value)
        elif sym in ["VALBZ", "MS", "GS", "WFC"]:
            if stocks[sym].spread <= 5:
                continue
            else:
                buy_price = stocks[sym].best_buy + 1
                buy_size = stocks[sym].buy_size()
                sell_price = stocks[sym].best_sell - 1
                sell_size = stocks[sym].sell_size()
                send_offer("BUY", sym, buy_price, buy_size)
                send_offer("SELL", sym, sell_price, sell_size)
                stocks[sym].clean(stocks[sym].mid)
 
        # Stay gold ponyboy
        if stocks[sym].spread <= 3:
            buy_price = stocks[sym].best_buy
            sell_price = stocks[sym].best_sell
            
        #martha stewart
        else:
            buy_price = stocks[sym].best_buy + 1
            sell_price = stocks[sym].best_sell - 1
        
        if (stocks[sym].size <= 20):
            # Buy
            buy_size = 1 + stocks[sym].size // 5
            buy = {"type": "add",
                   "order_id": ID, 
                   "symbol": sym, 
                   "dir": "BUY", 
                   "price": buy_price, 
                   "size": buy_size}
            s.send(json.dumps(buy))
            s.send("\n")
            
            if stocks[sym].last_buy != None:
                cancel = {"type":"cancel", "order_id": stocks[sym].last_buy}
                s.send(json.dumps(cancel))
                s.send("\n")

            stocks[sym].last_buy = ID
            ID += 1
         
        if (stocks[sym].size >= -20):   
            # Sell
            sell_size = 1 + stocks[sym].size // 5
            sell = {"type": "add",
                    "order_id": ID, 
                    "symbol": sym, 
                    "dir": "SELL", 
                    "price": sell_price, 
                    "size": sell_size}
        
            s.send(json.dumps(sell))
            s.send("\n")

            if stocks[sym].last_sell != None:
                cancel = {"type":"cancel", "order_id": stocks[sym].last_sell}
                s.send(json.dumps(cancel))
                s.send("\n")

            stocks[sym].last_sell = ID
            ID += 1
'''

# Strategy 1.0
# For each stock, look at the best (lowest) buy offer and the best (highest) sell offer
# If the spread is 3cents or less, trade outside:
#   Place a buy 1cent below best buy offer
#   Place a sell 1cent above best sell offer
# Otherwise, trade inside:
#   get the average of their two prices, your "fair value"
# Place order to buy 1cent above best buy offer, as long as that is less than the fair value
# Right after, place order to sell 1cent below best sell offer, as long as that is greater than fair value
