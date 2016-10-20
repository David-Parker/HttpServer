# This is a very simple script that sends a valid request
#
# usage: python3 Valid.py <servername> <serverport> <filename>
#  ex:   python3 Valid.py localhost 5001 test.html

from socket import *
import sys

serverName = sys.argv[1]
serverPort = int(sys.argv[2])
filename = sys.argv[3]

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName,serverPort))

message = 'GET ' + filename + ' HTTP/1.1' + '\r\n'
message += 'Host: www.google.com\r\n\r\n'  
clientSocket.send(message.encode())
response = clientSocket.recv(8192)
print ('From Server:' + response.decode())
clientSocket.close()