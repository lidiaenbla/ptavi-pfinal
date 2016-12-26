#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Programa cliente UDP que abre un socket a un servidor
"""

import socket
import sys
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

class leerFicheroXml(ContentHandler):
    def __init__(self):
        self.account = ""
        self.uaserver = ""
        self.rtpaudio = ""
        self.regproxy = ""
        self.log = ""
        self.audio = ""
        self.misdatos = []

    def startElement(self, etiqueta, attrs):

        if etiqueta == 'account':
            account = {'account': ({'username': attrs.get('username', ""),
                                    'passwd': attrs.get('passwd', "")})}
            self.misdatos.append(account)
        elif etiqueta == 'uaserver':
            uaserver = {'uaserver': ({'ip': attrs.get('ip', ""),
                                      'puerto': attrs.get('puerto', "")})}
            self.misdatos.append(uaserver)
        elif etiqueta == 'rtpaudio':
            rtpaudio = {'rtpaudio': ({'puerto': attrs.get('puerto', "")})}
            self.misdatos.append(rtpaudio)
        elif etiqueta == 'regproxy':
            regproxy = {'regproxy': ({'ip': attrs.get('ip', ""),
                                      'puerto': attrs.get('puerto', "")})}
            self.misdatos.append(regproxy)
        elif etiqueta == 'log':
            log = {'log': ({'path': attrs.get('path', "")})}
            self.misdatos.append(log)
        elif etiqueta == 'audio':
            audio = {'audio': ({'path': attrs.get('path', "")})}
            self.misdatos.append(audio)

    def get_tags(self):
        return self.misdatos


parser = make_parser()
cHandler = leerFicheroXml()
parser.setContentHandler(cHandler)

try:
    CONFIG = sys.argv[1]
    METHOD = sys.argv[2]
    if METHOD == "INVITE" or METHOD == "BYE":
        dirr = sys.argv[3]
    elif METHOD == "REGISTER":
        OPCION = sys.argv[3]
except IndexError:
    sys.exit("Usage: python3 client.py config method opcion")

parser.parse(open(CONFIG))
misdatos = cHandler.get_tags()
for elementos in misdatos:
    for etiqueta in elementos:
        for atributo, valor in elementos[etiqueta].items():
            if etiqueta == 'account':
                if atributo == 'username':
                    username = valor
                elif atributo == 'passwd':
                    passwd = valor
            elif etiqueta == 'uaserver':
                if atributo =='ip':
                    ip = valor
                elif atributo == 'puerto':
                    puerto = valor
            elif etiqueta == 'rtpaudio':
                if atributo == 'puerto':
                    puertoRtp = valor
            elif etiqueta == 'regproxy':
                if atributo == 'ip':
                    ipProxy = valor
                elif atributo == 'puerto':
                    puertoProxy = valor
            elif etiqueta == 'log':
                if atributo == 'path':
                    pathLog = valor
            elif etiqueta == 'audio':
                if atributo == 'path':
                    pathAudio = valor


if METHOD == "INVITE":
    LINE = "INVITE sip:" + dirr + " SIP/2.0 \r\nContent-Type: application/sdp"
    LINE += "\r\n"
    LINE += "v=0\r\no=\r\ns=misesion\r\nt=0\r\nm=" + pathAudio + " " + puertoRtp + " RTP"
elif METHOD == "REGISTER":
    LINE2 = "REGISTER sip:" + username + ":" + puertoProxy + " SIP/2.0 \r\nExpires: 3600"  
elif METHOD == "BYE":
    LINE = "BYE " 

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
    my_socket.connect(('127.0.0.1', int(puerto)))
    my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
    data = my_socket.recv(1024)
    print(data.decode('utf-8'))
    data = data.decode('utf-8').split()
    if data[1] == "100" and data[4] == "180" and data[7] == "200":
        LINE = "ACK " + SIP
        my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket2:
    my_socket2.connect(('127.0.0.1', int(puertoProxy)))
    my_socket2.send(bytes(LINE2, 'utf-8') + b'\r\n')

print("Socket terminado.")
