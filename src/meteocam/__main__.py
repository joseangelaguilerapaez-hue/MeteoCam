"""Punto de entrada ejecutable de MeteoCam."""

import sys

from PySide6.QtWidgets import QApplication

from meteocam.main_window import MainWindow
from meteocam.themes.classic_light import CLASSIC_LIGHT_STYLESHEET


def main() -> int:
    """Iniciar la aplicación de escritorio MeteoCam."""
    app = QApplication(sys.argv)

    app.setApplicationName("MeteoCam")
    app.setOrganizationName("MeteoArchidona")

    # Aplicar el tema visual clásico de MeteoCam a toda la aplicación.
    app.setStyleSheet(CLASSIC_LIGHT_STYLESHEET)

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())


# Fin de fichero
# Fin archivo: src/meteocam/__main__.py