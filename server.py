# server.py

from socket import *
import sys
import re

serverPort = 0

# Read the port number from the command line argument
if(len(sys.argv) != 2):
	print("You must specify the port!")
	sys.exit()
else:
	serverPort = int(sys.argv[1])

serverName = "localhost"

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(("", serverPort))
serverSocket.listen(1)

print("Server has been setup.")

# Methods and classes
class RequestException(Exception):
	pass

class HttpResponse:
	def reason(self, resnum):
		reasons = {}
		reasons[200] = "OK"
		reasons[201] = "Created"
		reasons[202] = "Accepted"
		reasons[203] = "Non-Authoritative Information"
		reasons[204] = "No Content"
		reasons[205] = "Reset Content"
		reasons[400] = "Bad Request"
		reasons[401] = "Unauthorized"
		reasons[403] = "Forbidden"
		reasons[404] = "Not Found"
		reasons[408] = "Request Timeout"
		reasons[500] = "Internal Server Error"
		reasons[501] = "Not Implemented"
		reasons[502] = "Bad Gateway"
		reasons[505] = "HTTP Version Not Supported"

		if resnum in reasons:
			return reasons[resnum]
		else:
			return ""

	def sendError(self, errnum):
		message =  "HTTP/1.1 {0} {1}\r\nContent-Length: 0\r\n\r\n".format(errnum, self.reason(errnum))
		raise RequestException(message)

class Http:
	requestLine = []
	headers = {}
	httpResponse = HttpResponse()

	def parseRequestLine(self, line):
		print(line)
		sections = line.split(' ')

		if(len(sections) != 3):
			self.httpResponse.sendError(400)

		# Parse the HEAD
		validHeads = re.compile("(GET|HEAD|POST|PUT|DELETE|TRACE|CONNECT|OPTIONS)$")
		head = sections[0]

		if(not validHeads.match(head)):
			self.httpResponse.sendError(400)

		if(head != "GET"):
			self.httpResponse.sendError(501)

		# Parse the URL
		# Parse the version
		version = sections[2]
		if(version != "HTTP/1.1"):
			self.httpResponse.sendError(505)

		return sections

	def parseHttp(self, request):
		lines = request.split('\r\n')

		if(len(lines) == 0):
			self.httpResponse.sendError(400)

		requestLine = self.parseRequestLine(lines[0])

		return request

# Listening loop
httpObj = Http()

while(1):
	connectionSocket, addr = serverSocket.accept()

	data = connectionSocket.recv(8192)

	request = data.decode()

	# Helpful debug information
	# print(addr)
	# print("Message Recieved:")
	# print(request)

	try:
		response = httpObj.parseHttp(request)
	except RequestException as e:
		response = str(e)

	print("Reponse: " + response)

	connectionSocket.send(response.encode())
	connectionSocket.close()
