#!/usr/bin/env python3
#
# arcticOS
# Copyright (c) 2021 Johnny Stene <jhonnystene@protonmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.
#
# This software contains code from Waveshare, released under the following license:
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# NOTE: using http.server here isn't a huge issue. the phone has no wifi and doesn't expose ports over cellular.
from http.server import BaseHTTPRequestHandler, HTTPServer
import os, sys, time, base64

global hostName, serverPort, driver

hostName = "localhost"
serverPort = 3506

def sendToDevice(data):
    return

def getDataFromDevice():
    return ""

class CellularServer(BaseHTTPRequestHandler):
    def do_GET(self):
        global driver

        if(self.path.startswith("/cellular/")):
            self.send_response(200)
            self.end_headers()
            path = self.path[9:]
            path = base64.b64decode(path)
            path = path.decode("ascii").split("\r")
            print("INFO: CellularService: Request: " + str(path))

            if(path[0] == "INFO"): # Get modem information
                if(path[1] == "GENERAL"): # General
                    sendToDevice("ATI")
                elif(path[1] == "IMEI"): # IMEI
                    sendToDevice("AT+GSN=?")
                elif(path[1] == "IMSI"): # IMSI
                    sendToDevice("AT+CIMI")
                elif(path[1] == "CONNECTION"): # Whether or not we're connected
                    sendToDevice("AT+CREG?")
                elif(path[1] == "QUALITY"): # How well the signal quality is
                    sendToDevice("AT+CSQ")
                elif(path[1] == "TIME"): # Local time
                    sendToDevice("AT+QLTS")
                elif(path[1] == "TECH"): # Cellular network type
                    sendToDevice("AT+QNWINFO")

                self.wfile.write(bytes(str(getDataFromDevice(), "utf-8")))
            elif(path[0] == "AIRPLANE"): # Airplane mode
                if(path[1] == "ON"): # On
                    sendToDevice("AT+CFUN=4,0")
                elif(paht[1] == "OFF"): #Off
                    sendToDevice("AT+CFUN=1,0")
            elif(path[0] == "SMS"): # SMS
                if(path[1] == "READ"): # Read 
                    sendToDevice("AT+CMGR=" + path[2])
                    self.wfile.write(bytes(str(getDataFromDevice(), "utf-8")))
                if(path[1] == "SEND"):
                    sendToDevice("AT+CMGS=" + path[2] + "\r" + path[3] + "^Z")
            elif(path[0] == "CALL"): # Phone call
                if(path[1] == "PLACE"): # Place
                    sendToDevice("ATD" + path[2])
                    self.wfile.write(bytes(str(getDataFromDevice(), "utf-8")))
                elif(path[1] == "ANSWER"):
                    sendToDevice("ATA")
                elif(path[1] == "END"):
                    sendToDevice("AT+CHUP")
            elif(path[0] == "POLL"): # Poll
                if(path[1] == "SMS"): # SMS
                    sendToDevice("AT+CMGL")
                    self.wfile.write(bytes(str(getDataFromDevice(), "utf-8")))
                elif(path[1] == "CALL"): # Phone call
                    sendToDevice("AT+CPAS")
                    if(int(getDataFromDevice()[7:])):
                        self.wfile.write(bytes(str("YES", "utf-8")))
                    else:
                        self.wfile.write(bytes(str("NO", "utf-8")))

        else:
            self.send_response(404)
            self.end_headers()

if(__name__ == "__main__"):
    webserver = HTTPServer((hostName, serverPort), CellularServer)
    print("INFO: CellularService: Started.")

    try:
        webserver.serve_forever()
    except KeyboardInterrupt:
        pass

    webserver.server_close()
    print("INFO: CellularService: Stopped.")