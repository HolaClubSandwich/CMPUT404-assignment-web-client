#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it



# citation: https://en.wikipedia.org/wiki/List_of_HTTP_header_fields

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    
    def get_host_port(self,url):
        # netloc is empty string if not present
        if urllib.parse.urlparse(url).netloc != "":
            host = urllib.parse.urlparse(url).netloc.split(":")[0]
        else:
            host = "http://127.0.0.1"
        # port is None of not present
        if urllib.parse.urlparse(url).port:
            port = urllib.parse.urlparse(url).port
        else:
            port = 80
        # path is empty string if not present
        if urllib.parse.urlparse(url).path != "":
            path = urllib.parse.urlparse(url).path
        else:
            path = '/'
        
        return host, port, path

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        code = data.split(' ')[1]
        return int(code)

    def get_headers(self,data):
        header = data.split('\r\n\r\n')[0]
        return header

    def get_body(self, data):
        body = data.split('\r\n\r\n')[1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        # code = 500
        # body = ""

        host, port, path = self.get_host_port(url)
        response_method = "GET {} HTTP/1.1\r\n".format(path)
        response_host = "Host: {}\r\n".format(host)
        response_accept = "Accept: */*\r\n"
        response_connection = "Connection: close\r\n\r\n"
        header = response_method + response_host + response_accept + response_connection

        self.connect(host, port)
        self.sendall(header)
        content = self.recvall(self.socket)
        code = self.get_code(content)
        body = self.get_body(content)
        self.close()

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        host, port, path = self.get_host_port(url)

        if args != None:
            args = urllib.parse.urlencode(args)
        else:
            args = urllib.parse.urlencode("")

        response_method = "POST {} HTTP/1.1\r\n".format(path)
        response_host = "Host: {}\r\n".format(host)
        response_content_type = "Content-Type: application/x-www-form-urlencoded\r\n"
        response_content_length = "Content-Length: {}\r\n".format(len(args))
        response_connection = "Connection: close\r\n\r\n"

        header = response_method + response_host + response_content_type + response_content_length + response_connection + args

        self.connect(host, port)
        self.sendall(header)
        content = self.recvall(self.socket)
        code = self.get_code(content)
        body = self.get_body(content)
        # try:
        #     self.connect(host, port)
        #     self.sendall(header)
        #     content = self.recvall(self.socket)
        #     code = self.get_code(content)
        #     body = self.get_body(content)
        # except:
        #     code = 404
        #     body = None
        
        self.close()

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
