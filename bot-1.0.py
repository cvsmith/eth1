import json
import socket

TCP_IP = '10.0.102.124'
TCP_PORT = 25000
BUFFER_SIZE = 1024

def readlines(sock, recv_buffer=1024, delim='\n'):
    buffer = ''
    data = True
    while data:
        data = sock.recv(recv_buffer)
        buffer += data

        while buffer.find(delim) != -1:
            line, buffer = buffer.split('\n', 1)
            yield line
    return

# Create TCP socket object s
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Skip optional step to bind s (socket will choose outgoing port for you)

# Connect s to IP/port defined above
s.connect((TCP_IP, TCP_PORT))

class Stock:
    def __init__(self, sym, best_buy, best_sell):
        self.sym = sym
        self.best_buy = best_buy
        self.best_sell = best_sell
        self.spread = best_sell - best_buy
        self.mid = (best_buy + best_sell) / 2

stocks = dict()

for line in readlines(s):
    line = json.loads(line)

    if line.type == "book":
        sym = line.symbol
        # Best buy and sell prices
        best_buy = line.buy[0][0]
        best_sell = line.sell[0][0]
        stocks[sym] = Stock(sym, best_buy, best_sell)

        # Stay gold ponyboy
        if stocks[sym].spread <= 3:
            buy_price = stocks[sym].best_buy - .01
            sell_price = stocks[sym].best_sell + .01
            
        #martha stewart
        else:
            buy_price = stocks[sym].best_buy + .01
            sell_price = stocks[sym].best_sell - .01
        
        buy = dict()
        sell = dict()
        buy_size = 5
        sell_size = 7
        #format is (type (ADD), order_id, symbol, dir (sell or SELL), price, size)
        buy = {"type": "add", "order_id": sym + "B" + buy_price, "symbol": "sym", "dir": "BUY", "price": buy_price, "size": buy_size}
        sell = {"type": "add", "order_id": sym + "S" + sell_price, "symbol": "sym", "dir": "sell", "price": sell_price, "size": sell_size}

        s.send(json.loads(buy))
        s.send(json.loads(sell))

# Strategy 1.0
# For each stock, look at the best (lowest) buy offer and the best (highest) sell offer
# If the spread is 3cents or less, trade outside:
#   Place a buy 1cent below best buy offer
#   Place a sell 1cent above best sell offer
# Otherwise, trade inside:
#   get the average of their two prices, your "fair value"
# Place order to buy 1cent above best buy offer, as long as that is less than the fair value
# Right after, place order to sell 1cent below best sell offer, as long as that is greater than fair value
