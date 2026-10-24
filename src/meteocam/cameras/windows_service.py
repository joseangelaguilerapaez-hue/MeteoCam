
# -*- coding: utf-8 -*-

"""Servicio de Windows para la publicación permanente de MeteoCam.

Envuelve publisher_runtime.ejecutar_publicacion mediante pywin32 para que
las dos transmisiones RTSP -> TCP -> VPS puedan ejecutarse como un servicio
de Windows, sin sesión de usuario ni interfaz gráfica.

En el mini PC se instala con MeteoCam-Setup.exe (ver docs/instalador.md),
que empaqueta este módulo como MeteoCamPublisher.exe.

Instalación manual desde el código (consola con permisos de administrador):

    python -m meteocam.cameras.windows_service install
    python -m meteocam.cameras.windows_service start
    python -m meteocam.cameras.windows_service stop
    python -m meteocam.cameras.windows_service remove

La configuración privada se carga desde:
C:/ProgramData/MeteoCam/publisher.json
"""

from __future__ import annotations

import logging
import logging.handlers
import os
import sys
import traceback

from pathlib import Path
from threading import Event

import servicemanager
import win32service
import win32serviceutil

from meteocam.cameras.publisher_runtime import ejecutar_publicacion


def _configurar_logging() -> None:
    """Registrar en fichero con rotación, sin volcar a consola."""

    carpeta = Path(
        os.environ.get(
            "PROGRAMDATA",
            r"C:\ProgramData",
        )
    ) / "MeteoCam" / "logs"

    carpeta.mkdir(
        parents=True,
        exist_ok=True,
    )

    handler = logging.handlers.RotatingFileHandler(
        carpeta / "publisher.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )

    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s: %(message)s"
        )
    )

    root_logger = logging.getLogger("meteocam")
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)


class MeteoCamPublisherService(win32serviceutil.ServiceFramework):
    """Servicio de Windows que mantiene activas las publicaciones RTSP."""

    _svc_name_ = "MeteoCamPublisher"
    _svc_display_name_ = "MeteoCam Publisher"
    _svc_description_ = (
        "Publica de forma continua las vistas de cámara de MeteoCam "
        "hacia el VPS mediante RTSP -> TCP."
    )

    def __init__(self, args) -> None:
        """Preparar el evento de parada del servicio."""
        super().__init__(args)
        self._stop_event = Event()

    def SvcStop(self) -> None:
        """Pedir la detención ordenada de las publicaciones."""
        # Cada publicador puede tardar hasta 30 s en cerrarse.
        self.ReportServiceStatus(
            win32service.SERVICE_STOP_PENDING,
            waitHint=90000,
        )
        self._stop_event.set()

    def SvcDoRun(self) -> None:
        """Arrancar el motor de publicación y bloquear hasta su parada."""
        _configurar_logging()

        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, ""),
        )

        try:
            codigo = ejecutar_publicacion(self._stop_event)

        except Exception:
            logging.getLogger("meteocam").exception(
                "Fallo al ejecutar el servicio."
            )
            servicemanager.LogErrorMsg(
                "MeteoCamPublisher: fallo al ejecutar el servicio.\n"
                f"{traceback.format_exc()}"
            )
            # Salida con error para que Windows aplique el reinicio.
            os._exit(1)

        if codigo != 0 and not self._stop_event.is_set():
            logging.getLogger("meteocam").error(
                "Publicación caída (código %s). "
                "Se fuerza la salida para que Windows reinicie el servicio.",
                codigo,
            )
            servicemanager.LogErrorMsg(
                "MeteoCamPublisher: publicación caída; "
                "se fuerza el reinicio del servicio."
            )
            os._exit(1)

        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STOPPED,
            (self._svc_name_, ""),
        )


def main() -> None:
    """Procesar la línea de comandos del servicio (install/start/stop/...).

    Empaquetado con PyInstaller (MeteoCamPublisher.exe), Windows lanza el
    ejecutable sin argumentos: en ese caso se entrega el control al
    administrador de servicios. Con argumentos (install, start, stop,
    remove...) se comporta como la línea de comandos habitual de pywin32.
    """
    if getattr(sys, "frozen", False) and len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(
            MeteoCamPublisherService
        )
        servicemanager.StartServiceCtrlDispatcher()
        return

    win32serviceutil.HandleCommandLine(
        MeteoCamPublisherService
    )


if __name__ == "__main__":
    main()


# Fin de fichero
