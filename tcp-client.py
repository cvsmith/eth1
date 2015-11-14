import socket
import sys

TCP_IP = '127.0.0.1'
TCP_PORT = 25000
BUFFER_SIZE = 1024


#Create a TCP socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Connect our socket to the port where the server is listening at
server_address = (TCP_IP, TCP_PORT)
s.connect(server_address)

#Try to send a message
MESSAGE = "Hello, World!"
try:
	s.send(MESSAGE)
	data = s.recv(BUFFER_SIZE)
	s.close()

print "received data:", data