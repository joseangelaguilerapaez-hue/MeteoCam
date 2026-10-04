"""Ventana de configuración y selección de cámaras de MeteoCam."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from meteocam.cameras.config import CAMERAS, CameraConfig


class CameraConfigDialog(QDialog):
    """Seleccionar una cámara conocida por MeteoCam."""

    camera_selected = Signal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        """Crear el diálogo de configuración de cámara."""
        super().__init__(parent)

        self.setWindowTitle("MeteoCam — Configuración de cámara")
        self.resize(560, 360)
        self.setMinimumSize(480, 320)

        self._selected_camera: CameraConfig | None = None

        layout = QVBoxLayout(self)

        explanation = QLabel(
            "Selecciona la cámara que utilizará MeteoCam.\n"
            "La configuración contiene únicamente los datos técnicos "
            "del dispositivo; las credenciales no se almacenan aquí."
        )
        explanation.setWordWrap(True)
        layout.addWidget(explanation)

        self._fields = QWidget(self)
        form = QFormLayout(self._fields)

        self._camera_combo = QComboBox()

        for camera in CAMERAS:
            self._camera_combo.addItem(
                f"{camera.name} — {camera.manufacturer} {camera.model}",
                camera.code,
            )

        self._station = QLabel()
        self._manufacturer = QLabel()
        self._model = QLabel()
        self._host = QLabel()
        self._rtsp_port = QLabel()

        form.addRow("Cámara:", self._camera_combo)
        form.addRow("Estación:", self._station)
        form.addRow("Fabricante:", self._manufacturer)
        form.addRow("Modelo:", self._model)
        form.addRow("Dirección IP:", self._host)
        form.addRow("Puerto RTSP:", self._rtsp_port)

        layout.addWidget(self._fields)
        layout.addStretch()

        self._status = QLabel()
        self._status.setWordWrap(True)
        layout.addWidget(self._status)

        buttons = QHBoxLayout()

        self._select_button = QPushButton("Seleccionar")
        self._cancel_button = QPushButton("Cancelar")

        self._select_button.clicked.connect(self._select_camera)
        self._cancel_button.clicked.connect(self.reject)
        self._camera_combo.currentIndexChanged.connect(
            self._update_camera_information
        )

        buttons.addWidget(self._select_button)
        buttons.addStretch()
        buttons.addWidget(self._cancel_button)

        layout.addLayout(buttons)

        if self._camera_combo.count() > 0:
            self._update_camera_information()
        else:
            self._select_button.setEnabled(False)
            self._status.setText(
                "No hay cámaras configuradas en MeteoCam."
            )

    def _current_camera(self) -> CameraConfig | None:
        """Obtener la cámara seleccionada actualmente."""
        index = self._camera_combo.currentIndex()

        if index < 0:
            return None

        code = self._camera_combo.itemData(index)

        for camera in CAMERAS:
            if camera.code == code:
                return camera

        return None

    def _update_camera_information(self) -> None:
        """Mostrar los datos de la cámara seleccionada."""
        camera = self._current_camera()

        if camera is None:
            self._station.clear()
            self._manufacturer.clear()
            self._model.clear()
            self._host.clear()
            self._rtsp_port.clear()
            self._status.setText("No hay ninguna cámara seleccionada.")
            return

        self._station.setText(camera.station)
        self._manufacturer.setText(camera.manufacturer)
        self._model.setText(camera.model)
        self._host.setText(camera.host)
        self._rtsp_port.setText(str(camera.rtsp_port))

        self._status.setText(
            f"Preparada para seleccionar «{camera.name}»."
        )

    def _select_camera(self) -> None:
        """Confirmar la cámara seleccionada."""
        camera = self._current_camera()

        if camera is None:
            self._status.setText(
                "Selecciona una cámara antes de continuar."
            )
            return

        self._selected_camera = camera
        self.camera_selected.emit(camera)
        self.accept()

    @property
    def selected_camera(self) -> CameraConfig | None:
        """Devolver la cámara seleccionada al cerrar el diálogo."""
        return self._selected_camera


# Fin archivo: src/meteocam/camera_config_dialog.py