# -*- coding: utf-8 -*-

"""
Configuración del agente de órdenes de cámara.

Se lee de C:\\ProgramData\\MeteoCam\\agente.json y, si un campo no está
allí, de publisher.json (el diseño de la API dice que la clave va en
publisher.json; se admiten los dos sitios). Ejemplo de agente.json:

    {
      "agente": "el IdentificadorAgente de las cámaras (columna camara.ide_agente)",
      "clave_agente": "la de METEOARCHIDONA_CLAVE_AGENTE_METEOCAM del VPS",
      "api_url": "https://meteoarchidona.com/api"
    }

Opcionales: canal_ptz (1), canales ({"ide_vista o id de cámara": canal}),
segundos_llegada (5), camera_http_port (80), camera_https (false).

Sin "agente" o sin "clave_agente" el agente no arranca y la publicación
del directo sigue igual que siempre.
"""

from __future__ import annotations

import json
import os

from dataclasses import dataclass, field
from pathlib import Path


API_URL_POR_DEFECTO = "https://meteoarchidona.com/api"
NOMBRE_FICHERO = "agente.json"


class ConfiguracionIncompleta(ValueError):
    """Faltan datos para arrancar el agente."""


@dataclass
class ConfiguracionAgente:
    agente: str
    clave_agente: str
    api_url: str = API_URL_POR_DEFECTO
    camera_host: str = ""
    camera_username: str = ""
    camera_password: str = field(default="", repr=False)
    camera_http_port: int | None = None
    camera_https: bool = False
    canal_ptz: int = 1
    canales: dict[str, int] = field(default_factory=dict)
    segundos_llegada: float = 5.0
    intervalo_consulta: float = 5.0

    def canal_para(self, camara: dict) -> int:
        """Canal Reolink de una cámara lógica de la API."""

        for clave in (
            camara.get("identificador_vista"),
            str(camara.get("camara_id")),
        ):
            if clave and clave in self.canales:
                return int(self.canales[clave])
        return self.canal_ptz


def carpeta_programdata() -> Path:
    return Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData")) / "MeteoCam"


def _leer_json(ruta: Path) -> dict:
    if not ruta.exists():
        return {}
    with ruta.open("r", encoding="utf-8-sig") as fichero:
        datos = json.load(fichero)
    if not isinstance(datos, dict):
        raise ConfiguracionIncompleta(f"{ruta.name} no contiene un objeto JSON.")
    return datos


def construir(publisher: dict, agente: dict) -> ConfiguracionAgente:
    """Mezcla agente.json (prioridad) con publisher.json."""

    def valor(nombre, defecto=None):
        if nombre in agente and agente[nombre] not in (None, ""):
            return agente[nombre]
        if nombre in publisher and publisher[nombre] not in (None, ""):
            return publisher[nombre]
        return defecto

    faltan = [
        nombre
        for nombre in ("agente", "clave_agente", "camera_host", "camera_username", "camera_password")
        if not isinstance(valor(nombre), str) or not valor(nombre).strip()
    ]
    if faltan:
        raise ConfiguracionIncompleta("Falta configuración del agente: " + ", ".join(faltan))

    canales = valor("canales", {}) or {}
    if not isinstance(canales, dict):
        raise ConfiguracionIncompleta("«canales» debe ser un objeto {vista: canal}.")

    puerto = valor("camera_http_port")

    return ConfiguracionAgente(
        agente=valor("agente").strip(),
        clave_agente=valor("clave_agente").strip(),
        api_url=str(valor("api_url", API_URL_POR_DEFECTO)).strip(),
        camera_host=valor("camera_host").strip(),
        camera_username=valor("camera_username"),
        camera_password=valor("camera_password"),
        camera_http_port=int(puerto) if puerto not in (None, "") else None,
        camera_https=bool(valor("camera_https", False)),
        canal_ptz=int(valor("canal_ptz", 1)),
        canales={str(k): int(v) for k, v in canales.items()},
        segundos_llegada=float(valor("segundos_llegada", 5.0)),
    )


def cargar(publisher: dict, carpeta: Path | None = None) -> ConfiguracionAgente:
    carpeta = carpeta or carpeta_programdata()
    return construir(publisher, _leer_json(carpeta / NOMBRE_FICHERO))


# Fin archivo: src/meteocam/agente/configuracion.py
