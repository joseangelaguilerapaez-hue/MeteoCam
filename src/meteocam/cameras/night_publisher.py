"""Publicación nocturna de MeteoCam con interfaz mínima.

Archivo temporal exclusivamente local.
NO SUBIR A GIT.
"""

from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from meteocam.cameras.diagnostics import Credentials
from meteocam.cameras.tcp_publisher import TcpPublisher


CAMERA_HOST = "192.168.1.100"
RTSP_PORT = 554

CAMERA_USERNAME = "admin"
CAMERA_PASSWORD = "joseangel13"

VPS_HOST = "187.124.114.42"

PANORAMICA_PATH = "/Preview_01_sub"
PANORAMICA_TCP_PORT = 10080

PTZ_PATH = "/Preview_02_sub"
PTZ_TCP_PORT = 10081


class PublisherRow(QFrame):
    """Mostrar el estado de una publicación."""

    def __init__(
        self,
        name: str,
        parent=None,
    ) -> None:
        """Crear una fila de estado."""
        super().__init__(parent)

        self.setFrameShape(
            QFrame.Shape.StyledPanel
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(
            12,
            10,
            12,
            10,
        )

        self._name_label = QLabel(name)
        self._name_label.setMinimumWidth(130)

        self._indicator_label = QLabel("●")
        self._indicator_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self._indicator_label.setFixedWidth(24)

        self._status_label = QLabel(
            "DETENIDO"
        )
        self._status_label.setStyleSheet(
            "font-weight: bold;"
        )

        layout.addWidget(
            self._name_label
        )
        layout.addWidget(
            self._indicator_label
        )
        layout.addWidget(
            self._status_label,
            stretch=1,
        )

        self.set_status(
            "DETENIDO"
        )

    def set_status(
        self,
        status: str,
    ) -> None:
        """Actualizar el estado visible."""
        self._status_label.setText(
            status
        )

        if status == "PUBLICANDO":
            self._indicator_label.setStyleSheet(
                "color: green;"
                "font-size: 18px;"
            )

        elif status in (
            "REINTENTANDO",
            "CONECTANDO CÁMARA",
            "CONECTANDO VPS",
            "ESPERANDO VÍDEO",
            "ERROR / REINTENTANDO",
        ):
            self._indicator_label.setStyleSheet(
                "color: orange;"
                "font-size: 18px;"
            )

        else:
            self._indicator_label.setStyleSheet(
                "color: red;"
                "font-size: 18px;"
            )


class NightPublisherWindow(QWidget):
    """Ventana mínima para las publicaciones nocturnas."""

    def __init__(self) -> None:
        """Crear la ventana y arrancar ambos publicadores."""
        super().__init__()

        self.setWindowTitle(
            "MeteoCam · Publicación nocturna"
        )

        self.setMinimumWidth(450)
        self.setFixedHeight(245)

        self._closing = False

        credentials = Credentials(
            username=CAMERA_USERNAME,
            password=CAMERA_PASSWORD,
        )

        self._panoramica = TcpPublisher(
            target=CAMERA_HOST,
            path=PANORAMICA_PATH,
            credentials=credentials,
            tcp_host=VPS_HOST,
            tcp_port=PANORAMICA_TCP_PORT,
            rtsp_port=RTSP_PORT,
            parent=self,
        )

        self._ptz = TcpPublisher(
            target=CAMERA_HOST,
            path=PTZ_PATH,
            credentials=credentials,
            tcp_host=VPS_HOST,
            tcp_port=PTZ_TCP_PORT,
            rtsp_port=RTSP_PORT,
            parent=self,
        )

        self._crear_interfaz()
        self._conectar_publicadores()

        self._panoramica.start()
        self._ptz.start()

    def _crear_interfaz(self) -> None:
        """Crear la interfaz mínima."""
        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            16,
            14,
            16,
            14,
        )
        layout.setSpacing(10)

        title = QLabel(
            "MeteoCam · Los Llanos"
        )
        title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        title.setStyleSheet(
            "font-size: 16px;"
            "font-weight: bold;"
        )

        subtitle = QLabel(
            "Visualización local desactivada · "
            "Publicación RTSP → TCP → VPS"
        )
        subtitle.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self._panoramica_row = PublisherRow(
            "Panorámica"
        )

        self._ptz_row = PublisherRow(
            "PTZ"
        )

        destination = QLabel(
            f"VPS {VPS_HOST} · "
            f"{PANORAMICA_TCP_PORT} / "
            f"{PTZ_TCP_PORT}"
        )
        destination.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        close_button = QPushButton(
            "Detener publicaciones y cerrar"
        )
        close_button.clicked.connect(
            self.close
        )

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addWidget(
            self._panoramica_row
        )
        layout.addWidget(
            self._ptz_row
        )
        layout.addWidget(destination)
        layout.addWidget(close_button)

    def _conectar_publicadores(
        self,
    ) -> None:
        """Conectar las señales de ambos publicadores."""

        self._panoramica.status_changed.connect(
            self._panoramica_row.set_status
        )

        self._ptz.status_changed.connect(
            self._ptz_row.set_status
        )

        self._panoramica.publication_started.connect(
            lambda _destination: (
                self._panoramica_row.set_status(
                    "PUBLICANDO"
                )
            )
        )

        self._ptz.publication_started.connect(
            lambda _destination: (
                self._ptz_row.set_status(
                    "PUBLICANDO"
                )
            )
        )

        self._panoramica.publication_error.connect(
            lambda _message: (
                self._panoramica_row.set_status(
                    "ERROR / REINTENTANDO"
                )
            )
        )

        self._ptz.publication_error.connect(
            lambda _message: (
                self._ptz_row.set_status(
                    "ERROR / REINTENTANDO"
                )
            )
        )

        self._panoramica.publication_stopped.connect(
            lambda: (
                self._panoramica_row.set_status(
                    "DETENIDO"
                )
            )
        )

        self._ptz.publication_stopped.connect(
            lambda: (
                self._ptz_row.set_status(
                    "DETENIDO"
                )
            )
        )

    def _detener_publicadores(
        self,
    ) -> None:
        """Detener ambos publicadores de forma ordenada."""
        if self._closing:
            return

        self._closing = True

        self._panoramica_row.set_status(
            "DETENIENDO"
        )

        self._ptz_row.set_status(
            "DETENIENDO"
        )

        publishers = (
            self._panoramica,
            self._ptz,
        )

        for publisher in publishers:
            publisher.stop()

        for publisher in publishers:
            publisher.wait(30000)

    def closeEvent(
        self,
        event: QCloseEvent,
    ) -> None:
        """Cerrar limpiamente ambos publicadores."""
        self._detener_publicadores()
        event.accept()


def main() -> int:
    """Ejecutar la publicación nocturna."""
    app = QApplication(sys.argv)

    window = NightPublisherWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())


# Fin de fichero
# Fin archivo: src/meteocam/night_publisher.py