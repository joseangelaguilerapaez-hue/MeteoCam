# -*- coding: utf-8 -*-

"""
Pruebas del agente de órdenes de cámara con una cámara Reolink falsa y una
API falsa (servidores HTTP locales). Solo biblioteca estándar y pytest.
"""

from __future__ import annotations

import json
import threading
import time

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import pytest

from meteocam.agente.api import ClienteApiAgente, ConflictoComando
from meteocam.agente.configuracion import ConfiguracionAgente, ConfiguracionIncompleta, construir, cargar
from meteocam.agente.ejecutor import AgenteCamaras
from meteocam.agente.reolink import ClienteReolink, ErrorReolink


# ----------------------------------------------------------------------
# Servidores falsos
# ----------------------------------------------------------------------


class Servidor:
    def __init__(self, manejador):
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), manejador)
        self.httpd.estado = self
        self.puerto = self.httpd.server_address[1]
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def cerrar(self):
        self.httpd.shutdown()
        self.httpd.server_close()


class CamaraFalsa(Servidor):
    def __init__(self):
        self.tokens = 0
        self.caducar_proxima = False
        self.ordenes: list[dict] = []
        self.presets = {
            1: [
                {"id": 0, "name": "Sierra", "enable": 1},
                {"id": 3, "name": "Pueblo", "enable": 1},
                {"id": 4, "name": "", "enable": 0},
            ]
        }
        super().__init__(_ManejadorCamara)

    def movimientos(self):
        return [o["param"]["id"] for o in self.ordenes if o["cmd"] == "PtzCtrl" and o["param"]["op"] == "ToPos"]


class _ManejadorCamara(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _responder(self, datos):
        cuerpo = json.dumps([datos]).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_POST(self):
        estado: CamaraFalsa = self.server.estado
        consulta = parse_qs(urlparse(self.path).query)
        cmd = consulta["cmd"][0]
        cuerpo = json.loads(self.rfile.read(int(self.headers["Content-Length"])))[0]

        if cmd == "Login":
            usuario = cuerpo["param"]["User"]
            if usuario["userName"] != "admin" or usuario["password"] != "s3creta":
                return self._responder({"cmd": cmd, "code": 1, "error": {"rspCode": -7, "detail": "login failed"}})
            estado.tokens += 1
            return self._responder({"cmd": cmd, "code": 0, "value": {"Token": {"name": f"t{estado.tokens}", "leaseTime": 3600}}})

        token = consulta.get("token", [""])[0]
        if token != f"t{estado.tokens}" or estado.caducar_proxima:
            estado.caducar_proxima = False
            return self._responder({"cmd": cmd, "code": 1, "error": {"rspCode": -6, "detail": "please login first"}})

        if cmd == "GetDevInfo":
            return self._responder({"cmd": cmd, "code": 0, "value": {"DevInfo": {"model": "OMVI", "firmVer": "v3", "channelNum": 2}}})
        if cmd == "GetPtzPreset":
            canal = cuerpo["param"]["channel"]
            if canal not in estado.presets:
                return self._responder({"cmd": cmd, "code": 1, "error": {"rspCode": -9, "detail": "not support"}})
            return self._responder({"cmd": cmd, "code": 0, "value": {"PtzPreset": estado.presets[canal]}})
        if cmd == "PtzCtrl":
            estado.ordenes.append(cuerpo)
            return self._responder({"cmd": cmd, "code": 0, "value": {"rspCode": 200}})
        return self._responder({"cmd": cmd, "code": 1, "error": {"rspCode": -9, "detail": "not support"}})


class ApiFalsa(Servidor):
    CLAVE = "clave-de-prueba"

    def __init__(self):
        self.camara = {
            "camara_id": 7,
            "identificador_dispositivo": "omvi",
            "identificador_vista": "ptz",
            "tipo_vista": "PTZ",
            "timelapse_en_curso": False,
            "preset_timelapse": None,
            "patrulla_activa": None,
            "comando": None,
        }
        self.reclamados: list[int] = []
        self.resultados: dict[int, dict] = {}
        self.cerrojo = threading.Lock()
        super().__init__(_ManejadorApi)

    def poner_comando(self, comando):
        with self.cerrojo:
            self.camara["comando"] = comando


class _ManejadorApi(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _responder(self, codigo, datos):
        cuerpo = json.dumps(datos).encode()
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def _autorizado(self):
        estado: ApiFalsa = self.server.estado
        if self.headers.get("X-Clave-Agente") != estado.CLAVE:
            self._responder(401, {"detail": "Clave de agente ausente o incorrecta."})
            return False
        return True

    def do_GET(self):
        if not self._autorizado():
            return
        estado: ApiFalsa = self.server.estado
        agente = parse_qs(urlparse(self.path).query)["agente"][0]
        with estado.cerrojo:
            camaras = [dict(estado.camara)] if agente == "los-llanos" else []
        self._responder(200, {
            "agente": agente,
            "fecha_servidor": "2026-11-07T10:00:00+01:00",
            "intervalo_consulta_segundos": 0.1,
            "camaras": camaras,
        })

    def do_POST(self):
        if not self._autorizado():
            return
        estado: ApiFalsa = self.server.estado
        ruta = urlparse(self.path).path
        partes = ruta.strip("/").split("/")
        comando_id = int(partes[-2])
        longitud = int(self.headers.get("Content-Length") or 0)
        cuerpo = json.loads(self.rfile.read(longitud)) if longitud else None

        with estado.cerrojo:
            if partes[-1] == "reclamar":
                if comando_id in estado.reclamados:
                    return self._responder(409, {"detail": "ya reclamada"})
                estado.reclamados.append(comando_id)
                if (estado.camara.get("comando") or {}).get("id") == comando_id:
                    estado.camara["comando"] = None
            else:
                estado.resultados[comando_id] = cuerpo
        self._responder(200, {"id": comando_id, "estado": "EN_PROCESO", "intentos": 1,
                              "fecha_reclamacion": None, "fecha_final": None})


# ----------------------------------------------------------------------
# Utilidades
# ----------------------------------------------------------------------


@pytest.fixture
def camara():
    servidor = CamaraFalsa()
    yield servidor
    servidor.cerrar()


@pytest.fixture
def api():
    servidor = ApiFalsa()
    yield servidor
    servidor.cerrar()


def _cliente_camara(camara: CamaraFalsa) -> ClienteReolink:
    return ClienteReolink("127.0.0.1", "admin", "s3creta", puerto=camara.puerto, tiempo_espera=3)


def _agente(camara: CamaraFalsa, api: ApiFalsa) -> AgenteCamaras:
    config = ConfiguracionAgente(
        agente="los-llanos",
        clave_agente=ApiFalsa.CLAVE,
        api_url=f"http://127.0.0.1:{api.puerto}",
        camera_host="127.0.0.1",
        camera_username="admin",
        camera_password="s3creta",
        camera_http_port=camara.puerto,
        segundos_llegada=0.05,
        intervalo_consulta=0.1,
    )
    return AgenteCamaras(config, camara=_cliente_camara(camara))


def _esperar(condicion, segundos=5.0):
    fin = time.monotonic() + segundos
    while time.monotonic() < fin:
        if condicion():
            return True
        time.sleep(0.02)
    return False


PATRULLA = {
    "id": 1,
    "codigo": "GENERAL",
    "nombre": "General",
    "preset_inicial": "0",
    "velocidad_defecto": 20,
    "pasos": [
        {"posicion": 2, "tipo": "ESPERAR", "segundos": 0, "preset": None, "velocidad": None, "nivel_zoom": None},
        {"posicion": 1, "tipo": "MOVER_A_PRESET", "preset": "3", "velocidad": 40, "segundos": None, "nivel_zoom": None},
        {"posicion": 3, "tipo": "ZOOM", "nivel_zoom": 5, "preset": None, "velocidad": None, "segundos": None},
    ],
}


# ----------------------------------------------------------------------
# Cliente Reolink
# ----------------------------------------------------------------------


def test_reolink_presets_solo_activos(camara):
    presets = _cliente_camara(camara).presets(1)
    assert [(p.identificador, p.nombre) for p in presets] == [("0", "Sierra"), ("3", "Pueblo")]


def test_reolink_renueva_sesion_caducada(camara):
    cliente = _cliente_camara(camara)
    cliente.ir_a_preset(1, "3", 99)
    camara.caducar_proxima = True
    cliente.ir_a_preset(1, 0)
    assert camara.tokens == 2
    assert camara.movimientos() == [3, 0]
    # La velocidad se limita a 1-64 y por defecto es 32.
    assert [o["param"]["speed"] for o in camara.ordenes] == [64, 32]


def test_reolink_error_explicado_sin_contrasena(camara):
    cliente = ClienteReolink("127.0.0.1", "admin", "mala", puerto=camara.puerto)
    with pytest.raises(ErrorReolink) as error:
        cliente.presets(1)
    assert "login failed" in str(error.value)
    assert "mala" not in str(error.value)


# ----------------------------------------------------------------------
# Cliente de la API y configuración
# ----------------------------------------------------------------------


def test_api_conflicto_409(api):
    cliente = ClienteApiAgente(f"http://127.0.0.1:{api.puerto}", ApiFalsa.CLAVE, "los-llanos")
    cliente.reclamar(5)
    with pytest.raises(ConflictoComando):
        cliente.reclamar(5)


def test_configuracion_mezcla_y_exige_clave(tmp_path):
    publisher = {"camera_host": "192.168.1.250", "camera_username": "admin", "camera_password": "x", "vps_host": "v"}
    with pytest.raises(ConfiguracionIncompleta):
        cargar(publisher, tmp_path)

    (tmp_path / "agente.json").write_text(
        json.dumps({"agente": "los-llanos", "clave_agente": "k", "canales": {"ptz": 2}}), encoding="utf-8"
    )
    config = cargar(publisher, tmp_path)
    assert config.api_url == "https://meteoarchidona.com/api"
    assert config.canal_para({"identificador_vista": "ptz"}) == 2
    assert config.canal_para({"identificador_vista": "otra", "camara_id": 9}) == 1
    assert "x" not in repr(config)

    # La clave también puede ir en publisher.json.
    assert construir({**publisher, "agente": "a", "clave_agente": "k"}, {}).agente == "a"


# ----------------------------------------------------------------------
# Ejecutor
# ----------------------------------------------------------------------


def test_sincronizar_presets(camara, api):
    api.poner_comando({"id": 11, "tipo": "SINCRONIZAR_PRESETS", "preset": None, "velocidad": None,
                       "patrulla": None, "parametros": None,
                       "fecha_creacion": "2026-11-07T10:00:00+01:00", "fecha_caducidad": None})
    agente = _agente(camara, api)
    agente.iniciar()
    try:
        assert _esperar(lambda: 11 in api.resultados)
    finally:
        agente.detener()

    resultado = api.resultados[11]
    assert resultado["correcto"] is True
    assert resultado["presets"] == [
        {"identificador": "0", "nombre": "Sierra"},
        {"identificador": "3", "nombre": "Pueblo"},
    ]
    assert resultado["resultado"]["dispositivo"]["model"] == "OMVI"


def test_vuelta_de_patrulla_por_orden(camara, api):
    api.poner_comando({"id": 12, "tipo": "EJECUTAR_VUELTA_PATRULLA", "preset": None, "velocidad": None,
                       "patrulla": PATRULLA, "parametros": None,
                       "fecha_creacion": "2026-11-07T10:00:00+01:00", "fecha_caducidad": None})
    agente = _agente(camara, api)
    agente.iniciar()
    try:
        assert _esperar(lambda: 12 in api.resultados)
    finally:
        agente.detener()

    # Inicial -> paso 1 (preset 3) -> vuelta al inicial; ZOOM se anota y no se envía.
    assert camara.movimientos() == [0, 3, 0]
    assert [o["param"]["speed"] for o in camara.ordenes] == [20, 40, 20]
    assert api.resultados[12]["correcto"] is True
    assert "ZOOM" in api.resultados[12]["resultado"]["avisos"][0]


def test_orden_no_admitida_se_informa_como_error(camara, api):
    api.poner_comando({"id": 13, "tipo": "CAPTURA_PUNTUAL", "preset": None, "velocidad": None,
                       "patrulla": None, "parametros": None,
                       "fecha_creacion": "2026-11-07T10:00:00+01:00", "fecha_caducidad": None})
    agente = _agente(camara, api)
    agente.iniciar()
    try:
        assert _esperar(lambda: 13 in api.resultados)
    finally:
        agente.detener()
    assert api.resultados[13]["correcto"] is False
    assert camara.movimientos() == []


def test_patrulla_activa_en_bucle_y_vuelta_al_inicial_al_desactivar(camara, api):
    with api.cerrojo:
        api.camara["patrulla_activa"] = PATRULLA
    agente = _agente(camara, api)
    agente.iniciar()
    try:
        # Al menos dos vueltas completas.
        assert _esperar(lambda: camara.movimientos()[:6] == [0, 3, 0, 0, 3, 0])

        with api.cerrojo:
            api.camara["patrulla_activa"] = None
        assert _esperar(lambda: not agente.ejecutores[7]._ultima_patrulla)
        hechos = len(camara.movimientos())
        time.sleep(0.5)
        # Quieta y en el preset inicial.
        assert len(camara.movimientos()) == hechos
        assert camara.movimientos()[-1] == 0
    finally:
        agente.detener()


def test_timelapse_pausa_la_patrulla(camara, api):
    with api.cerrojo:
        api.camara["patrulla_activa"] = PATRULLA
    agente = _agente(camara, api)
    agente.iniciar()
    try:
        assert _esperar(lambda: len(camara.movimientos()) >= 3)
        with api.cerrojo:
            api.camara["timelapse_en_curso"] = True
            api.camara["preset_timelapse"] = "3"
        assert _esperar(lambda: camara.movimientos()[-1] == 3)
        time.sleep(0.3)
        hechos = len(camara.movimientos())
        time.sleep(0.5)
        assert len(camara.movimientos()) == hechos

        # Al acabar el timelapse, la patrulla se reanuda desde el inicial.
        with api.cerrojo:
            api.camara["timelapse_en_curso"] = False
        assert _esperar(lambda: len(camara.movimientos()) > hechos + 1)
        assert camara.movimientos()[hechos] == 0
    finally:
        agente.detener()


def test_orden_interrumpe_la_patrulla_activa(camara, api):
    patrulla_lenta = {**PATRULLA, "pasos": [
        {"posicion": 1, "tipo": "ESPERAR", "segundos": 30, "preset": None, "velocidad": None, "nivel_zoom": None},
    ]}
    with api.cerrojo:
        api.camara["patrulla_activa"] = patrulla_lenta
    agente = _agente(camara, api)
    agente.iniciar()
    try:
        assert _esperar(lambda: camara.movimientos() == [0])
        api.poner_comando({"id": 14, "tipo": "POSICIONAR_PRESET", "preset": "3", "velocidad": 10,
                           "patrulla": None, "parametros": None,
                           "fecha_creacion": "2026-11-07T10:00:00+01:00", "fecha_caducidad": None})
        # No espera los 30 s: la orden entra enseguida.
        assert _esperar(lambda: 14 in api.resultados, segundos=3)
        assert api.resultados[14]["correcto"] is True
        assert camara.movimientos()[:2] == [0, 3]
        # Y la patrulla se reanuda desde su preset inicial.
        assert _esperar(lambda: camara.movimientos()[2:3] == [0])
    finally:
        agente.detener()


def test_sin_camaras_asignadas_no_falla(camara, api):
    agente = _agente(camara, api)
    agente._config.agente = "otro"
    agente._api = ClienteApiAgente(f"http://127.0.0.1:{api.puerto}", ApiFalsa.CLAVE, "otro")
    assert agente.consultar_una_vez() == pytest.approx(0.1)
    assert agente.ejecutores == {}


def test_api_caida_no_falla(camara):
    config = ConfiguracionAgente(
        agente="los-llanos", clave_agente="k", api_url="http://127.0.0.1:9",
        camera_host="127.0.0.1", camera_username="admin", camera_password="s3creta",
        camera_http_port=camara.puerto, intervalo_consulta=5,
    )
    agente = AgenteCamaras(config)
    assert agente.consultar_una_vez() == 15


# Fin archivo: tests/test_agente.py
