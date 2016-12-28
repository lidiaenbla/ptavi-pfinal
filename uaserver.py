#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Clase (y programa principal) para un servidor de eco en UDP simple
"""

import socketserver
import sys
import os

try:
    CONFIG = sys.argv[1]
except IndexError:
    sys.exit("Usage: python3 uaserver.py config")


class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    """
    Echo server class
    """
    def handle(self):
        """
        Manejador
        """
        line = self.rfile.read()
        print(line.decode('utf-8'))
        linea = line.decode('utf-8').split()
        if linea[0] == "INVITE":
            if '@' in linea[1]:
                self.wfile.write(b"SIP/2.0 100 Trying\r\n\r\n SIP/2.0 180 Ring\r\n\r\n SIP/2.0 200 OK\r\n\r\n ")
            else:
                self.wfile.write(b"SIP/2.0 400 Bad Request\r\n\r\n")
        elif linea[0] == "BYE":
            self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
        # elif linea[0] == "ACK":
            # cancion = './mp32rtp -i 127.0.0.1 -p 23032 < ' + FILE
            # print("vamos a ejecutar", cancion)
            # os.system(cancion)
            # print("hemos enviado la cancion")
        else:
            self.wfile.write(b"SIP/2.0 405 Method Not Allowed\r\n\r\n")

if __name__ == "__main__":

    serv = socketserver.UDPServer((('', 5060)), SIPRegisterHandler)
    print("Listening...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Finalizado servidor")
