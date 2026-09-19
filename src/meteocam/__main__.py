"""Punto de entrada ejecutable de MeteoCam."""

import ctypes
import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from meteocam.main_window import MainWindow


WINDOWS_APP_ID = "MeteoArchidona.MeteoCam"


def _configurar_identidad_windows() -> None:
    """Asignar a MeteoCam una identidad propia en Windows."""
    if sys.platform != "win32":
        return

    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            WINDOWS_APP_ID
        )
    except (AttributeError, OSError):
        # La aplicación debe poder arrancar aunque Windows no permita
        # establecer explícitamente el identificador.
        pass


def _obtener_ruta_icono() -> Path:
    """Obtener la ruta del icono principal de MeteoCam."""
    return Path(__file__).resolve().parent / "themes" / "icono-192.png"


def main() -> int:
    """Iniciar la aplicación de escritorio MeteoCam."""
    _configurar_identidad_windows()

    app = QApplication(sys.argv)

    app.setApplicationName("MeteoCam")
    app.setApplicationDisplayName("MeteoCam")
    app.setOrganizationName("MeteoArchidona")

    icon_path = _obtener_ruta_icono()

    if icon_path.is_file():
        icon = QIcon(str(icon_path))
        app.setWindowIcon(icon)
    else:
        icon = QIcon()

    window = MainWindow()

    if not icon.isNull():
        window.setWindowIcon(icon)

    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())


# Fin de fichero
# Fin archivo: src/meteocam/__main__.py