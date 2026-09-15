"""Ventana principal de MeteoCam."""

from PySide6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget

from meteocam import __version__


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación MeteoCam."""

    def __init__(self) -> None:
        """Inicializar la ventana principal."""
        super().__init__()

        self.setWindowTitle("MeteoCam")
        self.resize(1000, 700)

        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)

        title_label = QLabel("MeteoCam")
        version_label = QLabel(f"Versión {__version__}")

        layout.addWidget(title_label)
        layout.addWidget(version_label)
        layout.addStretch()

        self.setCentralWidget(central_widget)


# Fin de fichero
# Fin archivo: src/meteocam/main_window.py