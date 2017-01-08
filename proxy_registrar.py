import socket
import sys
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import socketserver
import time
import json
import hashlib

# dicc_cliente = {}


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

def hash(nonce, username, resumenCliente):
    nonce = nonce.split('"')
    fichPasswords = open('passwords', 'r')
    for linea in fichPasswords:
        if username in linea:
            linea = linea.split("=")
            contraseñaFicheroHash = linea[1]
    contraseñaHash2 = hashlib.sha1()
    contraseñaFicheroHash = contraseñaFicheroHash.split("\n")
    LINE2 = contraseñaFicheroHash[0] + nonce[1]
    contraseñaHash2.update(bytes(LINE2, 'utf-8'))
    contraseñaHash2 = str(contraseñaHash2.digest()).split("'")
    print("Resumen fichero passwords: ",contraseñaHash2[1])
    print("Resumen cliente: ", resumenCliente)
    if resumenCliente == contraseñaHash2[1]:
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

    def register2json(self, dicc_cliente):
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
            print("Creando fichero\n")
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

    def comprobarExpires(self,dicc_cliente):
        """
        Comprobar si ha expirado un cliente
        """
        List = []
        deleteList = []
        horaActual = time.gmtime(time.time())
        horaActual = time.strftime('%Y-%m-%d %H:%M:%S', horaActual)
        horaActual = horaActual.split(" ")
        with open('registered.json','r') as reader:
            for line in reader:
                if (line != "\n"):
                    if (line != "{}\n"):
                        if (line != "[]\n"):
                            hora = line.split(",")
                            hora = hora[1].split(" ")
                            hora = hora[2].split('"')
                            List.append(hora[0])
        for i in List:
            if i <= horaActual[1]:
                deleteList.append(i)
        with open('registered.json','r') as reader:
            List = []
            for line in reader:
                List.append(line)
        j=0
        for j in deleteList:
            for elemento in List:
                if j in elemento:
                    print("Eliminamos -->", elemento)
                    List.remove(elemento)
        if List != 0:
            fJson = open('registered.json','w')
            json.dump(List, fJson)
            fJson.close()

    

    def Register(self, ip, sip, expires, dicc_cliente):
        """
        Registrar a clientes en el diccionario
        """
        self.json2registered()
        if dicc_cliente != 0:
            self.comprobarExpires(dicc_cliente)
        dicc_cliente[sip] = [ip, expires]
        existencia = self.comprobarExistencia(sip)
        if existencia == 0:
            self.json2registered()
            self.register2json(dicc_cliente)
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
        ipPuerto = IP + ":" + Port
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
                        print("Recibimos: ",data.decode('utf-8') + "\n")
                        evento = "Recieved from " + IP+":"+Port+": " +line.decode('utf-8') 
                        rellenarFichero(name, evento)
                        data = data.decode('utf-8').split()
                        if data[1] == "100" and data[4] == "180" and data[7] == "200":
                            evento = "Sent to " + IP+": puerto SIP/2.0 100 Trying\r\n\r\n SIP/2.0 180 Ring\r\n\r\n SIP/2.0 200 OK\r\n\r\n"
                            rellenarFichero(name, evento)
                            self.wfile.write(b"SIP/2.0 100 Trying\r\n\r\n SIP/2.0 180 Ring\r\n\r\n SIP/2.0 200 OK\r\n\r\n ")
        elif linea[0] == "REGISTER":
            if linea[4] != "0":
                dicc_cliente = {}
                resumenHash = ""
                linea = line.decode('utf-8').split(':')
                try:
                    resumenCliente = linea[4]
                    resumenCliente = resumenCliente.split('"')
                    sip = linea[1]
                    resumenHash = hash(nonce, sip, resumenCliente[1])
                except:
                    pass
                if resumenHash == "coinciden":
                    print("Registrando...\n")
                    line = linea[3].split("\r\n")
                    for i in line:
                        if i == "Authorization":
                            autorizacion = 1
                    if autorizacion == 1:
                        expires = linea[3].split("\r\n")
                        expires = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time() + int(expires[0])))
                        self.Register(ipPuerto, sip, expires, dicc_cliente)
                        evento = "Sent to " + IP+":"+Port + " SIP/2.0 200 OK\r\n\r\n"
                        rellenarFichero(name, evento)
                        self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                    else:
                        evento = "Sent to " + IP+":"+Port + " SIP/2.0 401 Unauthorized\r\nWWW Authenticate: Digest nonce=" + nonce
                        rellenarFichero(name, evento)
                        self.wfile.write(b"SIP/2.0 401 Unauthorized\r\nWWW Authenticate: Digest nonce=" + nonce + "\r\n\r\n")
                else:
                    print("Contraseña errónea...\n")
                    self.wfile.write(b"SIP/2.0 401 Unauthorized\r\nWWW Authenticate: Digest nonce=89898989898989898989\r\n\r\n")
            else:
                print("Valor de expires incorrecto")
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
    print("Server proxy listening at port 5062...\n")
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        evento = "Finishing."
        rellenarFichero(name, evento)
        print("Finalizado proxy")
           