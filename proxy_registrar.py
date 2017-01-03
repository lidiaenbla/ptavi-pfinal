import socket
import sys
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import socketserver
import time
import json
import hashlib

dicc_cliente = {}
clientes = []


def crearFichero(nombre):
    fich = open(nombre, 'a+' )
    fich.close()

def rellenarFichero(nombre, evento):
    nameFich = nombre + ".log"
    crearFichero(nameFich)
    fichLog = open(nameFich, 'a+')
    horaActual = time.strftime('%Y%m%d%H%M%S', time.gmtime(time.time()))
    event = evento.split("\r\n")
    EVNT = ""
    for i in event:
        EVNT = EVNT + str(i)
    fichLog.write(str(horaActual) + " " + EVNT + "\r\n")

def hash(nonce, username):
    ficheros = ['ua1.xml', 'ua2.xml']
    for i in ficheros:
        fich = open(i,'r')
        for line in fich:
            if username in line:
                line = line.split("=")
                line = line[2].split('"')
                contraseña = line[1]
                # print("Contraseña: ", contraseña)
    contraseñaHash1 = hashlib.sha1()
    LINE1 = contraseña + nonce
    contraseñaHash1.update(bytes(LINE1, 'utf-8'))
    fichPasswords = open('passwords', 'r')
    for linea in fichPasswords:
        print("linea:",linea)
        print("username:",username)
        if username in linea:
            linea = linea.split("=")
            contraseñaFicheroHash = linea[1]
    contraseñaHash2 = hashlib.sha1()
    LINE2 = contraseñaFicheroHash + nonce
    contraseñaHash2.update(bytes(LINE2, 'utf-8'))
    if contraseñaHash1.digest() == contraseñaHash2.digest():
        return "coinciden"
    else:
        return "noCoinciden"


class leerFicheroXml(ContentHandler):
    def __init__(self):
        self.server = ""
        self.database = ""
        self.log = ""
        self.misdatos = []

    def startElement(self, etiqueta, attrs):

        if etiqueta == 'server':
            server = {'server': ({'name': attrs.get('name', ""),
                                    'ip': attrs.get('ip', ""),
                                    'puerto': attrs.get('puerto', "")})}
            self.misdatos.append(server)
        elif etiqueta == 'database':
            database = {'database': ({'path': attrs.get('path', ""),
                                      'passwdpath': attrs.get('passwdpath', "")})}
            self.misdatos.append(database)
        elif etiqueta == 'log':
            log = {'log': ({'path': attrs.get('path', "")})}
            self.misdatos.append(log)

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
            print("Creando fichero")
            fich = open('registered.json', 'w')
            fich.close()
            pass

    def comprobarExistencia(self,sip):
        existe = 0
        with open('registered.json','r') as reader:
            for line in reader:
                if sip in line:
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
        self.json2registered()
        self.comprobarExpires()
        dicc_cliente[sip] = [ip, expires]
        existencia = self.comprobarExistencia(sip)
        if existencia == 0:
            self.json2registered()
            self.register2json()
        else:
            print("cliente ya registrado: " + sip  + "\n")

    def handle(self):
        """
        Manejador
        """
        autorizacion = 0
        nonce = '"89898989898989898989"'
        line = self.rfile.read()
        IP = str(self.client_address[0])
        Port = str(self.client_address[1])
        evento = "Recieved from " + IP+":"+Port+": " +line.decode('utf-8') 
        rellenarFichero(name, evento)
        print("Recibimos: ",line.decode('utf-8'))
        linea = line.decode('utf-8').split()
        if ((linea[0] == "INVITE") or (linea[0] == "BYE") or (linea[0] == "ACK")):
            frase = line.decode('utf-8').split(':')
            # Sacamos puerto servidor
            puertoServidor = frase[2].split(" ")[0]
            if linea[0] == "ACK" or linea[0] == "BYE":
                LINE = line.decode('utf-8')
                self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
                    evento = "Sent to " + IP+": " + puertoServidor + line.decode('utf-8')
                    rellenarFichero(name, evento)
                    my_socket.connect(('127.0.0.1', int(puertoServidor)))
                    my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
            else:
                linea = str(linea[1])
                sip = linea.split(":")[-2]
                existencia = self.comprobarExistencia(sip)
                if existencia == 0:
                    self.wfile.write(b"SIP/2.0 404 User Not Found\r\n\r\n")
                else:
                    LINE = line.decode('utf-8')
                    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
                        evento = "Sent to " + IP+": " + puertoServidor + line.decode('utf-8')
                        rellenarFichero(name, evento)
                        my_socket.connect(('127.0.0.1', int(puertoServidor)))
                        my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
                        data = my_socket.recv(1024)
                        print("Recibimos: ",data.decode('utf-8'))
                        evento = "Recieved from " + IP+":"+Port+": " +line.decode('utf-8') 
                        rellenarFichero(name, evento)
                        data = data.decode('utf-8').split()
                        if data[1] == "100" and data[4] == "180" and data[7] == "200":
                            evento = "Sent to " + IP+": puerto SIP/2.0 100 Trying\r\n\r\n SIP/2.0 180 Ring\r\n\r\n SIP/2.0 200 OK\r\n\r\n"
                            rellenarFichero(name, evento)
                            self.wfile.write(b"SIP/2.0 100 Trying\r\n\r\n SIP/2.0 180 Ring\r\n\r\n SIP/2.0 200 OK\r\n\r\n ")
        elif linea[0] == "REGISTER":
            linea = line.decode('utf-8').split(':')
            sip = linea[1]
            resumenHash = hash(nonce, sip)
            print("resumenHash:", resumenHash)
            if resumenHash == "coinciden":
                print("Registrando...")
                line = linea[3].split("\r\n")
                for i in line:
                    if i == "Authorization":
                        autorizacion = 1
                exp = linea[3].split('\r\n')
                expires = exp[0].split(" ")
                if autorizacion == 1:
                    expires = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time() + float(expires[1])))
                    self.Register(IP, sip, expires)
                    evento = "Sent to " + IP+":"+Port + " SIP/2.0 200 OK\r\n\r\n"
                    rellenarFichero(name, evento)
                    self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                else:
                    evento = "Sent to " + IP+":"+Port + " SIP/2.0 401 Unauthorized\r\nWWW Authenticate: Digest nonce=" + nonce
                    rellenarFichero(name, evento)
                    self.wfile.write(b"SIP/2.0 401 Unauthorized\r\nWWW Authenticate: Digest nonce=89898989898989898989\r\n\r\n")
            else:
                print("Contraseña errónea...")
                self.wfile.write(b"SIP/2.0 401 Unauthorized\r\nWWW Authenticate: Digest nonce=89898989898989898989\r\n\r\n")
        else:
            evento = "Sent to " + IP+":"+Port + " SIP/2.0 405 Method Not Allowed\r\n\r\n"
            rellenarFichero(name, evento)
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

    evento = "Starting..."
    rellenarFichero(name, evento)
    serv = socketserver.UDPServer(('', 5062), diccionarioRegistrar)
    print("Listening...")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        evento = "Finishing."
        rellenarFichero(name, evento)
        print("Finalizado proxy")
           