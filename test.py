# test.py

from socket import *
import re
serverName = 'localhost'
serverPort = 24559

tests = {
		# "": 408,
		"       ": 400,
		"hey": 400,
		 "GET /index.html HTTP/1.1\r\n\r\n": 400,
		 "GET /index.html HTTP/1.1\r\nHost: www.cs.utexas.edu\r\n": 400,
		 "GET /index.html HTTP/1.1\nHost: www.cs.utexas.edu\r\n\r\n": 400,
		 "GET /index.html HTTP/1.1\r\nHost; www.cs.utexas.edu\r\n\r\n": 400,
		 "sdfsdfsdfsdf\r\ndfasdfasdf\r\n\r\n": 400,
		 "GET HTTP/1.1\r\nHost: www.cs.utexas.edu\r\n\r\n": 400,
		 "GET HTTP/1.1 junk\r\nHost: www.cs.utexas.edu\r\n\r\n": 400,
		 "GET\r\nHost: www.cs.utexas.edu\r\n\r\n": 400,
		 "GET /index.html HTTP/1.1\r\nHost: www.cs.utexas.edu\r\n\r\n": 200,
		 "GET /index.html HTTP/1.1 trash\r\nHost: www.cs.utexas.edu\r\n\r\n": 400,
		 "GET /index.html HTTP/1.0\r\nHost: www.cs.utexas.edu\r\n\r\n": 505,
		 "GET /index.html HTTP/1.2\r\nHost: www.cs.utexas.edu\r\n\r\n": 505,
		 "GET /index.html HTTP/1\r\nHost: www.cs.utexas.edu\r\n\r\n": 400,
		 "GET /index.html HTTP/\r\nHost: www.cs.utexas.edu\r\n\r\n": 400,
		 "HEAD /index.html HTTP/1.1\r\nHost: www.cs.utexas.edu\r\n\r\n": 501,
		 "HEAD /index.html HTTP/1.1\r\nHost: www.cs.utexas.edu\r\n": 400,
		 "GET /test.txt HTTP/1.1\r\nHost: www.cs.utexas.edu\r\n\r\n": 200,
		 "GET /hello.html HTTP/1.1\r\nHost: www.cs.utexas.edu\r\n\r\n": 404,
		 "GET  HTTP/1.1\r\nHost: www.cs.utexas.edu\r\n\r\n": 404,
		 "GET /index.html HTTP/1.1\r\nhOsT: www.cs.utexas.edu\r\n\r\n": 200,
		 "GeT /index.html HTTP/1.1\r\nhOsT: www.cs.utexas.edu\r\n\r\n": 501,
		 "GET /index.html HTTP/1.1\r\nHost: www.cs.utexas.edu\r\nIf-Modified-Since: Mon, 19 Sep 2016 16:17:09 GMT\r\n\r\n": 304,
		 "GET /index.html HTTP/1.1\r\nHost: www.cs.utexas.edu\r\nIf-Modified-Since: Mon, 19 Sep 2016 16:17:10 GMT\r\n\r\n": 304,
		 "GET /index.html HTTP/1.1\r\nHost: www.cs.utexas.edu\r\nIf-Modified-Since: Mon, 19 Sep 2016 16:17:08 GMT\r\n\r\n": 200
		 }

for test in tests:
	clientSocket = socket(AF_INET, SOCK_STREAM)
	clientSocket.connect((serverName, serverPort))
	message = test
	clientSocket.send(message.encode())
	recievedMessage = clientSocket.recv(8192).decode()
	response = recievedMessage.split("\r\n")
	header = response[0]
	regex = re.compile("HTTP\/1.1 ([0-9]{3}) (.*)")

	if(regex.match(header)):
		status = int(regex.match(header).groups()[0])
		if(status == tests[test]):
			print(str(tests[test]) + ": Pass! ")
		else:
			print("Failed test: " + test)
			print("Got: " + str(status))
			print("Expected: " + str(tests[test]))
	else:
		print("Fail! The response header was malformed.")	

	# print(recievedMessage)
	print("****************************")
	clientSocket.close()