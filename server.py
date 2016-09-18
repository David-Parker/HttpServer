# server.py

from socket import *
import sys
import re
from datetime import datetime
import time
import os
# import select

serverPort = 0
dateFormatString = "%a, %d %b %Y %H:%M:%S %Z"

# Read the port number from the command line argument
if(len(sys.argv) != 2):
	print("You must specify the port!")
	sys.exit()
else:
	serverPort = int(sys.argv[1])

serverName = "localhost"

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(("", serverPort))
serverSocket.listen(10)

print("Server has been setup.")

# Methods and classes

# checks a string representing the date against all valid http
# date time/date formats, returns a time struct if the string is
# valid, None otherwise
def getTime(timeString):
	date = None
	try:
		date = time.strptime(timeString, dateFormatString)
	except ValueError:
		try:
			date = time.strptime(timeString)
		except ValueError:
			try:
				date = time.strptime(timeString, "%A, %d-%b-%y %H:%M:%S %Z")
			except ValueError:
				try:
					date = time.strptime(timeString, "%a, %d %b %Y %H:%M:%S")
				except ValueError:
					try:
						date = time.strptime(timeString[:-1], "%a, %d %b %Y %H:%M:%S")
					except ValueError:
						return None
	return date

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
		reasons[304] = "Not Modified"
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
		tnow = time.gmtime()
		tnowstr = time.strftime(dateFormatString, tnow)
		message =  "HTTP/1.1 {0} {1}\r\nContent-Length: 0\r\nDate: {2}\r\nServer: Kappa\r\n".format(errnum, self.reason(errnum), tnowstr)
		raise RequestException(message)

	def createResponse(self, resnum, headers):
		tnow = time.gmtime()
		tnowstr = time.strftime(dateFormatString, tnow)
		message = "HTTP/1.1 {0} {1}\r\nDate: {2}\r\nServer: Kappa\r\n".format(resnum, self.reason(resnum), tnowstr)

		for header in headers:
			message += "{0}: {1}\r\n".format(header, headers[header])

		message += "\r\n"

		return message

class Http:
	requestLine = []
	headers = {}
	httpResponse = HttpResponse()
	body = ""

	def parseRequestLine(self, line):
		sections = line.split(' ')

		if(len(sections) != 3):
			self.httpResponse.sendError(400)

		# Parse the HEAD
		validHeads = re.compile("(GET|HEAD|POST|PUT|DELETE|TRACE|CONNECT|OPTIONS)$")
		head = sections[0]

		if(not validHeads.match(head)):
			self.httpResponse.sendError(501)

		# Parse the URL

		# Parse the version
		version = sections[2]
		if(version != "HTTP/1.1"):
			self.httpResponse.sendError(505)

		return sections

	def parseHeaders(self, lines):
		validHeader = re.compile("(.+): (.+)")
		headers = {}

		for line in lines:
			match = validHeader.match(line)
			if(not match):
				self.httpResponse.sendError(400)
			else:
				header = match.groups()[0]
				value = match.groups()[1]
				headers[header] = value

		if "Host" not in headers or "Connection" not in headers:
			self.httpResponse.sendError(400)

		return headers

	def getContentType(self, filetype):
		if(len(filetype) == 0):
			print("Should not have validated this type!")
			self.httpResponse.sendError(500)

		cleanType = filetype[1:].lower()

		if(cleanType == "jpg" or cleanType == "jpeg" or cleanType == "png" or cleanType == "gif" or cleanType == "bmp"):
			return "image/" + cleanType
		elif(cleanType == "html" or cleanType == "htm"):
			return "text/" + cleanType
		elif(cleanType == "txt"):
			return "text/plain"
		else:
			return "text/plain; charset=us-ascii"


	# Handles the request. Returns a tuple for the response and content body
	def handleRequest(self, requestLine, headers, body):
		response = []

		# Currently only supports the GET head
		if(requestLine[0] == "GET"):
			uri = requestLine[1]

			if(uri == "/"):
				uri = "/index.html"

			# This may be extended to allow absolute paths later
			relativeUri = "." + uri

			try:
				inputFile = open(relativeUri, 'rb')
			except IOError:
				self.httpResponse.sendError(404)

			fileName, fileExtension = os.path.splitext(relativeUri)
			lastModifiedDate = datetime.fromtimestamp(os.path.getmtime(relativeUri))
			lastModifiedDateStr = lastModifiedDate.strftime(dateFormatString)
			print(lastModifiedDateStr)

			if "If-Modified-Since" in headers:
				headerTime = getTime(headers["If-Modified-Since"])
				lastModifiedTime = getTime(lastModifiedDateStr)

				if(not headerTime or not lastModifiedTime):
					self.httpResponse.sendError(400)

				# The server has an older copy, don't update
				if(lastModifiedTime <= headerTime):
					self.httpResponse.sendError(304)


			contents = inputFile.read()
			inputFile.close()

			responseHeaders = {}
			responseHeaders["Content-Length"] = len(contents)
			responseHeaders["Content-Type"] = self.getContentType(fileExtension)
			responseHeaders["Last-Modified"] = lastModifiedDateStr

			response.append(self.httpResponse.createResponse(200, responseHeaders))
			response.append(contents)
			return response
		else:
			self.httpResponse.sendError(501)

		return []



	def parseHttp(self, request):
		lines = request.split('\r\n')

		if(len(lines) < 3):
			self.httpResponse.sendError(400)

		# The last header should have a blank \r\n
		if(lines[len(lines) - 2] != ""):
			self.httpResponse.sendError(400)
		else:
			lines.pop(len(lines) - 2)

		# Grab the content body after the last \r\n
		self.body = lines.pop()

		self.requestLine = self.parseRequestLine(lines.pop(0))
		self.headers = self.parseHeaders(lines)

		content = self.handleRequest(self.requestLine, self.headers, self.body)

		print(self.requestLine)
		print(self.headers)

		return content

# Listening loop
httpObj = Http()

while(1):
	# connectionSocket, addr = serverSocket.accept()

	# connectionSocket.setblocking(0)

	# ready = select.select([connectionSocket], [], [], 10)
	# if ready[0]:
	# 	try:
	# 		data = connectionSocket.recv(8192)
	# 	except Exception as e:
	# 		connectionSocket.close()
	# 		break
	# else:
	# 	continue

	connectionSocket, addr = serverSocket.accept()

	data = connectionSocket.recv(8192)

	request = data.decode()

	print("Request:")
	print(request)

	try:
		response = httpObj.parseHttp(request)
		print(len(response))
		connectionSocket.send(response[0].encode())
		connectionSocket.send(response[1])
		print("Reponse: " + response[0])
	except RequestException as e:
		response = str(e)
		connectionSocket.send(response.encode())
		print("Reponse: " + response)
	# except Exception as e:
	# 	print(str(e))

	connectionSocket.close()
	print("Connection closed")
