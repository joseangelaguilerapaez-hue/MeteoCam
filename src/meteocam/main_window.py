"""Ventana principal de MeteoCam."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from meteocam import __version__


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación MeteoCam."""

    def __init__(self) -> None:
        """Inicializar la ventana principal."""
        super().__init__()

        self.setWindowTitle("MeteoCam")
        self.resize(1100, 760)
        self.setMinimumSize(800, 600)

        self._crear_interfaz()
        self._crear_barra_estado()

    def _crear_interfaz(self) -> None:
        """Crear la estructura visual principal."""
        central_widget = QWidget(self)
        main_layout = QVBoxLayout(central_widget)

        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        main_layout.addWidget(self._crear_cabecera())
        main_layout.addWidget(self._crear_panel_informacion())
        main_layout.addWidget(self._crear_panel_video(), stretch=1)
        main_layout.addLayout(self._crear_panel_acciones())

        self.setCentralWidget(central_widget)

    def _crear_cabecera(self) -> QFrame:
        """Crear la cabecera de la aplicación."""
        frame = QFrame(self)
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setFrameShadow(QFrame.Shadow.Raised)

        layout = QHBoxLayout(frame)

        title_label = QLabel("MeteoCam")
        title_label.setObjectName("applicationTitle")

        version_label = QLabel(f"Versión {__version__}")
        version_label.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(version_label)

        return frame

    def _crear_panel_informacion(self) -> QGroupBox:
        """Crear el panel con la información de la cámara seleccionada."""
        group = QGroupBox("Cámara")

        layout = QHBoxLayout(group)
        layout.setSpacing(24)

        layout.addWidget(self._crear_campo("Estación", "Sin configurar"))
        layout.addWidget(self._crear_campo("Dispositivo", "Sin configurar"))
        layout.addWidget(self._crear_campo("Vista", "Sin seleccionar"))
        layout.addWidget(self._crear_campo("Estado", "DESCONECTADA"))

        layout.addStretch()

        return group

    def _crear_campo(self, titulo: str, valor: str) -> QWidget:
        """Crear un campo informativo compuesto por título y valor."""
        widget = QWidget(self)
        layout = QVBoxLayout(widget)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        title_label = QLabel(titulo)
        title_label.setObjectName("fieldTitle")

        value_label = QLabel(valor)
        value_label.setObjectName("fieldValue")

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        return widget

    def _crear_panel_video(self) -> QGroupBox:
        """Crear la zona reservada para el futuro visor de vídeo."""
        group = QGroupBox("Vídeo en directo")

        layout = QVBoxLayout(group)

        video_frame = QFrame(group)
        video_frame.setObjectName("videoFrame")
        video_frame.setFrameShape(QFrame.Shape.Panel)
        video_frame.setFrameShadow(QFrame.Shadow.Sunken)
        video_frame.setMinimumHeight(360)

        video_layout = QVBoxLayout(video_frame)

        video_label = QLabel(
            "Sin señal de vídeo\n\n"
            "El visor se conectará a una cámara en una fase posterior."
        )
        video_label.setObjectName("videoPlaceholder")
        video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        video_layout.addWidget(video_label)

        layout.addWidget(video_frame)

        return group

    def _crear_panel_acciones(self) -> QHBoxLayout:
        """Crear los controles principales de la ventana."""
        layout = QHBoxLayout()

        configuration_button = QPushButton("Configuración")
        configuration_button.setMinimumWidth(150)
        configuration_button.setMinimumHeight(36)

        diagnostics_button = QPushButton("Diagnóstico")
        diagnostics_button.setMinimumWidth(150)
        diagnostics_button.setMinimumHeight(36)

        layout.addWidget(configuration_button)
        layout.addWidget(diagnostics_button)
        layout.addStretch()

        return layout

    def _crear_barra_estado(self) -> None:
        """Crear la barra de estado inferior."""
        status_bar = QStatusBar(self)
        status_bar.showMessage("MeteoCam preparado")
        self.setStatusBar(status_bar)


# Fin de fichero
# Fin archivo: src/meteocam/main_window.py