"""Punto de entrada ejecutable de MeteoCam."""

import sys

from PySide6.QtWidgets import QApplication

from meteocam.main_window import MainWindow


def main() -> int:
    """Iniciar la aplicación de escritorio MeteoCam."""
    app = QApplication(sys.argv)

    app.setApplicationName("MeteoCam")
    app.setOrganizationName("MeteoArchidona")

    window = MainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())


# Fin de fichero
# Fin archivo: src/meteocam/__main__.py