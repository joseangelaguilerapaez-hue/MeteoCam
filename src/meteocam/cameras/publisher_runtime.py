
# -*- coding: utf-8 -*-

"""
MeteoCam - Motor de publicación permanente.

Ejecuta las dos transmisiones RTSP -> TCP -> VPS
sin interfaz gráfica.

Preparado para ser utilizado por un servicio Windows.

La configuración privada se carga desde:
C:/ProgramData/MeteoCam/publisher.json
"""

from __future__ import annotations

import json
import logging
import os

from pathlib import Path
from threading import Event
from urllib.parse import quote

from PySide6.QtCore import (
    QCoreApplication,
    QObject,
    QTimer,
)

from meteocam.cameras.diagnostics import Credentials
from meteocam.cameras.tcp_publisher import TcpPublisher


logger = logging.getLogger("meteocam.publisher")


def cargar_configuracion() -> dict:
    """Leer la configuración local protegida."""

    carpeta = Path(
        os.environ.get(
            "PROGRAMDATA",
            r"C:\ProgramData",
        )
    ) / "MeteoCam"

    archivo = carpeta / "publisher.json"

    with archivo.open(
        "r",
        encoding="utf-8-sig",
    ) as fichero:
        config = json.load(fichero)

    if not isinstance(config, dict):
        raise ValueError(
            "Configuración de MeteoCam inválida."
        )

    obligatorios = (
        "camera_host",
        "camera_username",
        "camera_password",
        "vps_host",
    )

    for campo in obligatorios:
        if (
            not isinstance(config.get(campo), str)
            or not config[campo].strip()
        ):
            raise ValueError(
                f"Falta configuración: {campo}"
            )

    return config


class PublisherRuntime(QObject):
    """Controlar ambas transmisiones sin ventanas."""

    def __init__(
        self,
        config: dict,
        stop_event: Event,
    ) -> None:
        super().__init__()

        self._stop_event = stop_event
        self._cerrando = False

        self._password = config[
            "camera_password"
        ]

        credentials = Credentials(
            username=config["camera_username"],
            password=self._password,
        )

        self._panoramica = TcpPublisher(
            target=config["camera_host"],
            path=config.get(
                "panoramica_path",
                "/Preview_01_sub",
            ),
            credentials=credentials,
            tcp_host=config["vps_host"],
            tcp_port=int(
                config.get(
                    "panoramica_tcp_port",
                    10080,
                )
            ),
            rtsp_port=int(
                config.get("rtsp_port", 554)
            ),
            parent=self,
        )

        self._especifica = TcpPublisher(
            target=config["camera_host"],
            path=config.get(
                "especifica_path",
                "/Preview_02_sub",
            ),
            credentials=credentials,
            tcp_host=config["vps_host"],
            tcp_port=int(
                config.get(
                    "especifica_tcp_port",
                    10081,
                )
            ),
            rtsp_port=int(
                config.get("rtsp_port", 554)
            ),
            parent=self,
        )

        self._publicadores = (
            ("Panorámica", self._panoramica),
            ("Vista específica", self._especifica),
        )

        self._timer = QTimer(self)
        self._timer.setInterval(1000)

        self._timer.timeout.connect(
            self._comprobar_estado
        )

        self._conectar_eventos()

    def _limpiar_error(
        self,
        error: str,
    ) -> str:
        """Evitar registrar credenciales."""

        mensaje = str(error)

        for secreto in (
            self._password,
            quote(self._password, safe=""),
        ):
            if secreto:
                mensaje = mensaje.replace(
                    secreto,
                    "[OCULTO]",
                )

        return mensaje

    def _conectar_eventos(self) -> None:
        """Registrar los cambios de estado."""

        for nombre, publicador in self._publicadores:

            publicador.status_changed.connect(
                lambda estado, n=nombre: logger.info(
                    "%s: %s",
                    n,
                    estado,
                )
            )

            publicador.publication_started.connect(
                lambda destino, n=nombre: logger.info(
                    "%s: PUBLICANDO hacia %s",
                    n,
                    destino,
                )
            )

            publicador.publication_error.connect(
                lambda error, n=nombre: logger.warning(
                    "%s: %s",
                    n,
                    self._limpiar_error(error),
                )
            )

    def iniciar(self) -> None:
        """Arrancar las dos publicaciones."""

        logger.info(
            "Iniciando MeteoCam Publisher."
        )

        for nombre, publicador in self._publicadores:
            logger.info(
                "Arrancando vista %s",
                nombre,
            )

            publicador.start()

        self._timer.start()

    def _comprobar_estado(self) -> None:
        """Vigilar parada solicitada o hilos caídos."""

        if self._cerrando:
            return

        if self._stop_event.is_set():
            self.detener()
            return

        for nombre, publicador in self._publicadores:
            if not publicador.isRunning():
                logger.error(
                    "Publicador finalizado: %s",
                    nombre,
                )

                self.detener(codigo=1)
                return

    def detener(
        self,
        codigo: int = 0,
    ) -> None:
        """Detener los dos publicadores."""

        if self._cerrando:
            return

        self._cerrando = True
        self._timer.stop()

        logger.info(
            "Deteniendo publicaciones."
        )

        for _, publicador in self._publicadores:
            publicador.stop()

        for nombre, publicador in self._publicadores:
            if not publicador.wait(30000):
                logger.error(
                    "No se detuvo a tiempo: %s",
                    nombre,
                )
                codigo = 1

        # Un hilo bloqueado no debe destruirse
        # mientras siga ejecutándose.
        if any(
            publicador.isRunning()
            for _, publicador in self._publicadores
        ):
            logger.critical(
                "Quedan hilos activos. "
                "Se requiere recuperación externa."
            )
            os._exit(1)

        logger.info(
            "Publicaciones detenidas."
        )

        QCoreApplication.exit(codigo)


def ejecutar_publicacion(
    stop_event: Event,
) -> int:
    """Ejecutar el motor sin interfaz gráfica."""

    config = cargar_configuracion()

    app = QCoreApplication([])

    app.setApplicationName(
        "MeteoCam Publisher"
    )

    runtime = PublisherRuntime(
        config=config,
        stop_event=stop_event,
    )

    runtime.iniciar()

    return app.exec()


# Fin de fichero
