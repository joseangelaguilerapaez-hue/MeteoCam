"""Servidor HTTP mínimo que imita la API de Reolink para probar en CI
scripts/investigar-reolink.ps1 sin cámara real.

Uso: python tests/servidor_reolink_falso.py <puerto>

- Login con la contraseña "clave-secreta" devuelve un token.
- Cualquier otro comando con token correcto responde code 0 y repite el
  comando y los parámetros recibidos.
- GetHddInfo responde con error, para probar ese camino.
- Solo sirve /cgi-bin/api.cgi.
"""

import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

TOKEN = "token-de-prueba"
CLAVE = "clave-secreta"


class Manejador(BaseHTTPRequestHandler):
    def do_POST(self):  # noqa: N802
        url = urlparse(self.path)
        if url.path != "/cgi-bin/api.cgi":
            self.send_error(404)
            return
        consulta = parse_qs(url.query)
        cmd = consulta.get("cmd", [""])[0]
        longitud = int(self.headers.get("Content-Length", 0))
        orden = json.loads(self.rfile.read(longitud))[0]

        if cmd == "Login":
            if orden["param"]["User"]["password"] == CLAVE:
                respuesta = {"cmd": cmd, "code": 0,
                             "value": {"Token": {"leaseTime": 3600, "name": TOKEN}}}
            else:
                respuesta = {"cmd": cmd, "code": 1,
                             "error": {"rspCode": -7, "detail": "login failed"}}
        elif consulta.get("token", [""])[0] != TOKEN:
            respuesta = {"cmd": cmd, "code": 1,
                         "error": {"rspCode": -6, "detail": "please login first"}}
        elif cmd == "GetHddInfo":
            respuesta = {"cmd": cmd, "code": 1,
                         "error": {"rspCode": -9, "detail": "not support"}}
        else:
            # Incluye el token para comprobar que el script lo oculta.
            respuesta = {"cmd": cmd, "code": 0,
                         "value": {"recibido": orden, "eco": f"token={TOKEN}"}}

        cuerpo = json.dumps([respuesta]).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", int(sys.argv[1])), Manejador).serve_forever()

# Fin archivo: tests/servidor_reolink_falso.py
