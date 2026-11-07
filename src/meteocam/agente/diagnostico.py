# -*- coding: utf-8 -*-

"""
Comprobación del agente desde la consola del mini PC, sin mover la cámara.

    "C:\\Program Files\\MeteoCam\\Publisher\\MeteoCamPublisher.exe" comprobar-agente

Hace, por orden, y explica cada resultado:

1. Lee publisher.json y agente.json.
2. Abre sesión en la cámara y lee modelo y firmware (GetDevInfo).
3. Lee los presets de los canales 0 y 1 (GetPtzPreset), para confirmar
   cuál es el canal de la PTZ.
4. Pregunta a la API qué cámaras tiene asignadas este agente y qué
   trabajo hay (GET /agente/camaras/trabajo).

Nunca escribe la contraseña ni la clave. No mueve la cámara: solo lee.
"""

from __future__ import annotations

import json
import sys

from meteocam.agente.api import ClienteApiAgente, ErrorApi
from meteocam.agente.configuracion import ConfiguracionIncompleta, carpeta_programdata, cargar
from meteocam.agente.reolink import ClienteReolink, ErrorReolink


def _titulo(texto: str) -> None:
    print()
    print(f"== {texto}")


def comprobar(salida=None) -> int:
    """Devuelve 0 si todo va bien y 1 si algo falla."""

    if salida is not None:
        sys.stdout = salida

    fallos = 0
    carpeta = carpeta_programdata()

    _titulo("1. Configuración")
    try:
        with (carpeta / "publisher.json").open("r", encoding="utf-8-sig") as fichero:
            publisher = json.load(fichero)
        configuracion = cargar(publisher, carpeta)
    except FileNotFoundError:
        print(f"MAL: no existe {carpeta / 'publisher.json'}")
        return 1
    except (ConfiguracionIncompleta, ValueError) as error:
        print(f"MAL: {error}")
        print(f"     Revisa {carpeta / 'agente.json'} (docs/agente.md).")
        return 1

    print(f"Bien: agente «{configuracion.agente}», API {configuracion.api_url}")
    print(f"      cámara {configuracion.camera_host}, canal PTZ {configuracion.canal_ptz}")

    camara = ClienteReolink(
        configuracion.camera_host,
        configuracion.camera_username,
        configuracion.camera_password,
        puerto=configuracion.camera_http_port,
        https=configuracion.camera_https,
    )

    _titulo("2. Cámara: sesión y datos del dispositivo")
    try:
        info = camara.informacion_dispositivo()
        for clave in ("model", "name", "firmVer", "hardVer", "channelNum", "serial"):
            if clave in info:
                print(f"      {clave}: {info[clave]}")
        print("Bien: la cámara responde por la API HTTP.")
    except ErrorReolink as error:
        fallos += 1
        print(f"MAL: {error}")
        print("     Comprueba la IP, el usuario y la contraseña de publisher.json.")

    _titulo("3. Cámara: presets por canal")
    for canal in (0, 1):
        try:
            presets = camara.presets(canal)
            marca = "  <- canal PTZ configurado" if canal == configuracion.canal_ptz else ""
            print(f"Canal {canal}: {len(presets)} preset(s){marca}")
            for preset in presets:
                print(f"      {preset.identificador}: {preset.nombre or '(sin nombre)'}")
        except ErrorReolink as error:
            print(f"Canal {canal}: sin presets ({error})")

    _titulo("4. API: cámaras de este agente")
    api = ClienteApiAgente(configuracion.api_url, configuracion.clave_agente, configuracion.agente)
    try:
        trabajo = api.trabajo()
        camaras = trabajo.get("camaras") or []
        if not camaras:
            fallos += 1
            print(f"MAL: la API no asigna ninguna cámara a «{configuracion.agente}».")
            print("     El valor de «agente» debe ser igual a camara.ide_agente.")
        for c in camaras:
            patrulla = (c.get("patrulla_activa") or {}).get("codigo") or "ninguna"
            comando = c.get("comando")
            orden = f"{comando.get('tipo')} n.º {comando.get('id')}" if comando else "ninguna"
            print(
                f"      cámara {c.get('camara_id')} ({c.get('tipo_vista')}, vista {c.get('identificador_vista')}):"
                f" canal {configuracion.canal_para(c)}, patrulla activa {patrulla},"
                f" orden pendiente {orden}, timelapse {'sí' if c.get('timelapse_en_curso') else 'no'}"
            )
        if camaras:
            print("Bien: la API reconoce al agente.")
    except ErrorApi as error:
        fallos += 1
        print(f"MAL: {error}")
        if error.estado == 401:
            print("     La clave_agente no coincide con la del servidor.")
        elif error.estado == 503:
            print("     El servidor no tiene configurada la clave del agente.")

    print()
    print("RESULTADO:", "todo correcto" if not fallos else f"{fallos} problema(s)")
    return 0 if not fallos else 1


# Fin archivo: src/meteocam/agente/diagnostico.py
