# Servidor de la simulacion, armado sobre el tc2008B_server.py del profe.
# Unity manda un POST y recibe el estado del tablero despues de una ronda.
# Se corre asi:  python server.py 8585
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import os
import sys

# el modelo vive en la carpeta de al lado, hay que decirle a python donde buscar
carpeta = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(carpeta, "..", "SimulacionAvanzada"))

from modelo import FlashPointModel
from serialiador import estado_json

AVANCES_POR_RONDA = 6
ESTRATEGIA = "mejorada"
TABLERO = os.path.join(carpeta, "..", "tableros", "tablero_final.txt")


def nueva_partida():
    return FlashPointModel(ESTRATEGIA, AVANCES_POR_RONDA, 7, 4, 24, 3, TABLERO)


model = nueva_partida()


class Server(BaseHTTPRequestHandler):

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        # un GET reinicia la partida, sirve para volver a empezar desde Unity
        global model
        model = nueva_partida()
        self._set_response()
        self.wfile.write(estado_json(model).encode('utf-8'))

    def do_POST(self):
        global model
        largo = int(self.headers.get('Content-Length', 0))
        if largo > 0:
            self.rfile.read(largo)          # se lee lo que manda Unity y se ignora

        if not model.termino():
            model.step()

        self._set_response()
        self.wfile.write(estado_json(model).encode('utf-8'))


def run(server_class=HTTPServer, handler_class=Server, port=8585):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info("Starting httpd...\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info("Stopping httpd...\n")


if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
