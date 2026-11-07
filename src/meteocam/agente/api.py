# -*- coding: utf-8 -*-

"""
Cliente de los endpoints del agente en api-meteoarchidona (/agente/camaras).

Contrato: docs/patrullas.md, sección 11, de api-meteoarchidona.

- GET  /agente/camaras/trabajo?agente=...
- POST /agente/camaras/comandos/{id}/reclamar?agente=...
- POST /agente/camaras/comandos/{id}/resultado?agente=...

Todas llevan la cabecera X-Clave-Agente. La clave no se escribe nunca en
el registro. Solo usa la biblioteca estándar.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request


CABECERA_CLAVE = "X-Clave-Agente"


class ErrorApi(Exception):
    """La API no respondió o devolvió un error."""

    def __init__(self, mensaje: str, estado: int | None = None):
        super().__init__(mensaje)
        self.estado = estado


class ConflictoComando(ErrorApi):
    """409: la orden ya la reclamó otro, ha caducado o se ha cerrado."""


class ClienteApiAgente:
    """Habla con la API de MeteoArchidona en nombre del mini PC."""

    def __init__(
        self,
        url_base: str,
        clave: str,
        agente: str,
        *,
        tiempo_espera: float = 15.0,
    ) -> None:
        self._url_base = url_base.rstrip("/") + "/agente/camaras"
        self._clave = clave
        self._agente = agente
        self._tiempo_espera = tiempo_espera

    @property
    def agente(self) -> str:
        return self._agente

    def _peticion(self, metodo: str, ruta: str, cuerpo: dict | None = None) -> dict:
        consulta = urllib.parse.urlencode({"agente": self._agente})
        url = f"{self._url_base}{ruta}?{consulta}"

        datos = None
        cabeceras = {
            CABECERA_CLAVE: self._clave,
            "Accept": "application/json",
            "User-Agent": "MeteoCam-Agente",
        }
        if cuerpo is not None:
            datos = json.dumps(cuerpo).encode("utf-8")
            cabeceras["Content-Type"] = "application/json"

        peticion = urllib.request.Request(url, data=datos, method=metodo, headers=cabeceras)

        try:
            with urllib.request.urlopen(peticion, timeout=self._tiempo_espera) as respuesta:
                texto = respuesta.read().decode("utf-8")
        except urllib.error.HTTPError as error:
            detalle = ""
            try:
                detalle = json.loads(error.read().decode("utf-8")).get("detail", "")
            except Exception:
                pass
            mensaje = f"HTTP {error.code} en {metodo} {ruta}: {detalle or error.reason}"
            if error.code == 409:
                raise ConflictoComando(mensaje, 409) from error
            raise ErrorApi(mensaje, error.code) from error
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            raise ErrorApi(f"sin conexión con la API ({error})") from error

        try:
            return json.loads(texto) if texto else {}
        except ValueError as error:
            raise ErrorApi(f"respuesta no válida en {metodo} {ruta}") from error

    def trabajo(self) -> dict:
        return self._peticion("GET", "/trabajo")

    def reclamar(self, comando_id: int) -> dict:
        return self._peticion("POST", f"/comandos/{int(comando_id)}/reclamar")

    def resultado(
        self,
        comando_id: int,
        *,
        correcto: bool,
        resultado: dict | None = None,
        mensaje_error: str | None = None,
        presets: list[dict] | None = None,
    ) -> dict:
        cuerpo: dict = {"correcto": correcto}
        if resultado is not None:
            cuerpo["resultado"] = resultado
        if mensaje_error:
            cuerpo["mensaje_error"] = mensaje_error[:1000]
        if presets is not None:
            cuerpo["presets"] = presets
        return self._peticion("POST", f"/comandos/{int(comando_id)}/resultado", cuerpo)


# Fin archivo: src/meteocam/agente/api.py
