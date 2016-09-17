# client.py

from socket import *
serverName = 'localhost'
serverPort = 24559

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

message = "GET /index.html HTTP/1.1\r\nContent-Type: html\r\n\r\n"
clientSocket.send(message.encode())

clientSocket.close()