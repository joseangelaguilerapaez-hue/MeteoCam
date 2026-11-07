# -*- coding: utf-8 -*-

"""
Cliente mínimo de la API HTTP de las cámaras Reolink (cgi-bin/api.cgi).

Solo lo que necesita el agente de órdenes (docs/agente.md):

- Login (token con caducidad) y renovación automática.
- GetDevInfo: datos del dispositivo (modelo, firmware, número de serie).
- GetPtzPreset: presets de un canal.
- PtzCtrl ToPos / Stop: mover la cámara a un preset o pararla.

Referencia de los comandos: docs/catalogo-comandos-reolink.md (rama main).

Solo usa la biblioteca estándar: se prueba en el CI sin PySide6 ni av.
La contraseña viaja en el cuerpo JSON del Login, nunca en la URL, y no se
escribe nunca en el registro.
"""

from __future__ import annotations

import json
import logging
import ssl
import threading
import time
import urllib.error
import urllib.request

from dataclasses import dataclass


logger = logging.getLogger("meteocam.agente.reolink")


# Códigos de error de Reolink que indican sesión caducada o inválida.
CODIGOS_SESION_INVALIDA = {-6, -5}

VELOCIDAD_MINIMA = 1
VELOCIDAD_MAXIMA = 64
VELOCIDAD_POR_DEFECTO = 32


class ErrorReolink(Exception):
    """La cámara no respondió o rechazó el comando."""

    def __init__(self, comando: str, mensaje: str, codigo: int | None = None):
        super().__init__(f"{comando}: {mensaje}")
        self.comando = comando
        self.codigo = codigo


@dataclass(frozen=True)
class PresetCamara:
    identificador: str
    nombre: str | None


class ClienteReolink:
    """Habla con una cámara Reolink de la red local."""

    def __init__(
        self,
        host: str,
        usuario: str,
        contrasena: str,
        *,
        puerto: int | None = None,
        https: bool = False,
        tiempo_espera: float = 10.0,
    ) -> None:
        esquema = "https" if https else "http"
        destino = host if puerto is None else f"{host}:{puerto}"

        self._url = f"{esquema}://{destino}/cgi-bin/api.cgi"
        self._usuario = usuario
        self._contrasena = contrasena
        self._tiempo_espera = tiempo_espera
        self._token: str | None = None
        self._caduca: float = 0.0
        self._cerrojo = threading.Lock()

        # Las cámaras usan certificados propios: en red local no se
        # comprueba el certificado si se elige HTTPS.
        self._contexto = None
        if https:
            self._contexto = ssl.create_default_context()
            self._contexto.check_hostname = False
            self._contexto.verify_mode = ssl.CERT_NONE

    # ------------------------------------------------------------------
    # Transporte
    # ------------------------------------------------------------------

    def _enviar(self, comando: str, parametros: dict, token: str | None) -> dict:
        url = f"{self._url}?cmd={comando}"
        if token:
            url += f"&token={token}"

        cuerpo = json.dumps(
            [{"cmd": comando, "action": 0, "param": parametros}]
        ).encode("utf-8")

        peticion = urllib.request.Request(
            url,
            data=cuerpo,
            method="POST",
            headers={"Content-Type": "application/json"},
        )

        try:
            with urllib.request.urlopen(
                peticion,
                timeout=self._tiempo_espera,
                context=self._contexto,
            ) as respuesta:
                datos = json.loads(respuesta.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            raise ErrorReolink(comando, f"sin respuesta de la cámara ({error})") from error
        except ValueError as error:
            raise ErrorReolink(comando, "respuesta no válida de la cámara") from error

        if isinstance(datos, list) and datos:
            datos = datos[0]

        if not isinstance(datos, dict):
            raise ErrorReolink(comando, "respuesta no válida de la cámara")

        if datos.get("code") != 0:
            error = datos.get("error") or {}
            codigo = error.get("rspCode")
            detalle = error.get("detail") or "error sin detalle"
            raise ErrorReolink(comando, f"{detalle} (rspCode {codigo})", codigo)

        return datos.get("value") or {}

    def _iniciar_sesion(self) -> str:
        valor = self._enviar(
            "Login",
            {
                "User": {
                    "Version": "0",
                    "userName": self._usuario,
                    "password": self._contrasena,
                }
            },
            token=None,
        )

        token = (valor.get("Token") or {}).get("name")
        if not token:
            raise ErrorReolink("Login", "la cámara no devolvió token")

        duracion = int((valor.get("Token") or {}).get("leaseTime") or 3600)
        self._token = token
        # Margen de un minuto para no usar un token a punto de caducar.
        self._caduca = time.monotonic() + max(60, duracion - 60)
        logger.info("Sesión abierta en la cámara (token válido %s s).", duracion)
        return token

    def comando(self, comando: str, parametros: dict) -> dict:
        """Ejecuta un comando con sesión; la renueva una vez si ha caducado."""

        with self._cerrojo:
            if not self._token or time.monotonic() >= self._caduca:
                self._iniciar_sesion()

            try:
                return self._enviar(comando, parametros, self._token)
            except ErrorReolink as error:
                if error.codigo not in CODIGOS_SESION_INVALIDA:
                    raise
                logger.info("Sesión de la cámara caducada; se abre otra.")
                self._iniciar_sesion()
                return self._enviar(comando, parametros, self._token)

    # ------------------------------------------------------------------
    # Comandos
    # ------------------------------------------------------------------

    def informacion_dispositivo(self) -> dict:
        """GetDevInfo: modelo, firmware, número de serie, canales..."""

        valor = self.comando("GetDevInfo", {})
        return valor.get("DevInfo") or valor

    def presets(self, canal: int) -> list[PresetCamara]:
        """GetPtzPreset: presets activos del canal, por número."""

        valor = self.comando("GetPtzPreset", {"channel": canal})
        lista = valor.get("PtzPreset")
        if not isinstance(lista, list):
            raise ErrorReolink("GetPtzPreset", "la cámara no devolvió la lista de presets")

        resultado = []
        for preset in lista:
            if not isinstance(preset, dict):
                continue
            # Reolink devuelve los 64 huecos; solo cuentan los activos.
            if not preset.get("enable"):
                continue
            nombre = (preset.get("name") or "").strip() or None
            resultado.append(PresetCamara(str(preset.get("id")), nombre))

        return resultado

    def ir_a_preset(self, canal: int, preset: str | int, velocidad: int | None = None) -> dict:
        """PtzCtrl ToPos. La cámara responde al aceptar la orden, no al llegar."""

        velocidad = VELOCIDAD_POR_DEFECTO if velocidad is None else int(velocidad)
        velocidad = max(VELOCIDAD_MINIMA, min(VELOCIDAD_MAXIMA, velocidad))

        return self.comando(
            "PtzCtrl",
            {
                "channel": canal,
                "op": "ToPos",
                "id": int(preset),
                "speed": velocidad,
            },
        )

    def detener(self, canal: int) -> dict:
        """PtzCtrl Stop."""

        return self.comando("PtzCtrl", {"channel": canal, "op": "Stop"})


# Fin archivo: src/meteocam/agente/reolink.py
