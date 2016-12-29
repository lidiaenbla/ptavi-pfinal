import socket
import sys
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import socketserver
import time
import json

dicc_cliente = {}
clientes = []

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
    dicc_client = {}

    def register2json(self):
        """
        Actualizar fichero json con los datos del dicc
        """
        # con a+ empezamos a escribir sin borrar lo anterior
        fichJson = open('registered.json', 'a+')
        fichJson.write('\n')
        json.dump(dicc_cliente, fichJson)
        fichJson.close()

    def json2registered(self):
        """
        comprobar si existe el fichero .json
        """
        try:
            open('registered.json', 'r')
        except:
            print("NO existe el fichero")
            pass

    def comprobarExistencia(self,sip):
        valor = 0
        with open('registered.json','r') as reader:
            for line in reader:
                registro = line.capitalize()
                valor = registro.find(str(sip))
                if valor < 0:
                    existe = 0
                else:
                    existe = 1
        return existe

    def comprobarExpires(self):
        """
        Comprobar si ha expirado un cliente
        """
        deleteList = []
        horaActual = time.gmtime(time.time())
        for cliente in dicc_cliente:
            if time.strptime(dicc_cliente[cliente][1], '%Y-%m-%d %H:%M:%S') <= horaActual:
                deleteList.append(cliente)
        for i in deleteList:
            del dicc_cliente[i]

    def Register(self, ip, sip, expires):
        """
        Registrar a clientes en el diccionario
        """
        self.comprobarExpires()
        dicc_cliente[sip] = [ip, expires]
        print("SIP:",sip)
        existencia = self.comprobarExistencia(sip)
        if valor == 0:
            self.json2registered()
            self.register2json()
        else:
            print("cliente ya registrado")

    def handle(self):
        """
        Manejador
        """
        autorizacion = 0
        line = self.rfile.read()
        IP = str(self.client_address[0])
        Port = str(self.client_address[1])
        print(line.decode('utf-8'))
        linea = line.decode('utf-8').split()
        if linea[0] == "INVITE" or linea[0] == "BYE" or linea[0] == "ACK":
            LINE = str(linea)
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
                my_socket.connect(('127.0.0.1', 5060))
                my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
        elif linea[0] == "REGISTER":
            linea = line.decode('utf-8').split(':')
            sip = linea[1]
            line = linea[3].split("\r\n")
            for i in line:
                if i == "Authorization":
                    autorizacion = 1
            exp = linea[3].split('\r\n')
            expires = exp[0].split(" ")
            if autorizacion == 1:
                expires = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time() + float(expires[1])))
                self.Register(IP, sip, expires)
                self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
            else:
                self.wfile.write(b"SIP/2.0 401 Unauthorized\r\nWWW Authenticate: Digest nonce=89898989898989898989")
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

    serv = socketserver.UDPServer(('', 5062), diccionarioRegistrar)
    print("Listening...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        print("Finalizado proxy")
           