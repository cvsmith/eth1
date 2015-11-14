import socket

TCP_IP = '127.0.0.1'
TCP_PORT = 25000
BUFFER_SIZE = 1024
MESSAGE = "Hello, World!"

# Create TCP socket object s
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Skip optional step to bind s (socket will choose outgoing port for you)

# Connect s to IP/port defined above
s.connect((TCP_IP, TCP_PORT))

# Treat s like a file now, except with send/recv instead of read/write
s.send(MESSAGE)
data = s.recv(BUFFER_SIZE)
s.close()

print "received data:", data