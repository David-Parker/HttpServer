# client.py

from socket import *
serverName = 'localhost'
serverPort = 24559

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

message = "GET /index.html HTTP/1.1\r\nHost: www.google.com\r\nConnection: close\r\nContent-Type: html\r\n\r\n"
clientSocket.send(message.encode())

recievedMessage = clientSocket.recv(8192).decode()
print(recievedMessage)
clientSocket.close()