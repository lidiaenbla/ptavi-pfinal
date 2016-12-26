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

class diccionarioRegistrar(socketserver.DatagramRequestHandler):
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
            if linea[1].split("@"):
                self.wfile.write(b"SIP/2.0 100 Trying\r\n\r\n SIP/2.0 180 Ring\r\n\r\n SIP/2.0 200 OK\r\n\r\n ")
            else:
                self.wfile.write(b"SIP/2.0 400 Bad Request\r\n\r\n")
        elif linea[0] == "BYE":
            self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
        elif linea[0] == "REGISTER":
            self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
        elif linea[0] == "ACK":
            # cancion = './mp32rtp -i 127.0.0.1 -p 23032 < ' + FILE
            # print("vamos a ejecutar", cancion)
            # os.system(cancion)
            # print("hemos enviado la cancion")
        else:
            self.wfile.write(b"SIP/2.0 405 Method Not Allowed\r\n\r\n")

parser = make_parser()
cHandler = leerFicheroXml()
parser.setContentHandler(cHandler)

try:
    CONFIG = sys.argv[1]
except IndexError:
    sys.exit("Usage: python3 proxy_registrar.py config")

parser.parse(open(CONFIG))
misdatos = cHandler.get_tags()
for elementos in misdatos:
    for etiqueta in elementos:
        for atributo, valor in elementos[etiqueta].items():
            if etiqueta == 'server':
                if atributo == 'name':
                    name = valor
                elif atributo == 'ip':
                    ip = valor
                elif atributo == 'puerto':
                    puerto = valor
            elif etiqueta == 'database':
                if atributo =='path':
                    path = valor
                elif atributo == 'passwdpath':
                    passwdpath = valor
            elif etiqueta == 'log':
                if atributo =='path':
                    pathLog = valor

if __name__ == "__main__":

    serv = socketserver.UDPServer((('', 5062)), diccionarioRegistrar)
    print("Listening...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Finalizado proxy")
           