"""Ventana de diagnóstico de cámaras IP."""

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from meteocam.cameras.diagnostics import (
    CameraTarget,
    Credentials,
    DiagnosticEvent,
    DiagnosticResult,
    diagnose,
)


class DiagnosticWorker(QThread):
    """Ejecutar operaciones de red fuera del hilo de la interfaz."""

    event_received = Signal(object)
    result_received = Signal(object)

    def __init__(
        self,
        target: CameraTarget,
        credentials: Credentials | None,
        parent: QWidget,
    ) -> None:
        """Preparar el diagnóstico."""
        super().__init__(parent)

        self._target = target
        self._credentials = credentials

    def run(self) -> None:
        """Ejecutar el diagnóstico sin bloquear la ventana."""
        try:
            result = diagnose(
                self._target,
                self._credentials,
                on_event=self.event_received.emit,
            )
            self.result_received.emit(result)
        except Exception:
            self.event_received.emit(
                DiagnosticEvent(
                    "CAM-RTSP-500",
                    "No se pudo completar el diagnóstico por un error interno.",
                )
            )
        finally:
            self._credentials = None


class DiagnosticsDialog(QDialog):
    """Configuración temporal y trazas del diagnóstico RTSP."""

    stream_ready = Signal(object, str, object)

    def __init__(self, parent: QWidget | None = None) -> None:
        """Crear el diálogo de diagnóstico."""
        super().__init__(parent)

        self.setWindowTitle("MeteoCam — Diagnóstico de cámara")
        self.resize(720, 520)
        self.setMinimumSize(560, 420)

        self._worker: DiagnosticWorker | None = None
        self._validated_target: CameraTarget | None = None
        self._validated_path: str | None = None
        self._validated_credentials: Credentials | None = None

        layout = QVBoxLayout(self)

        explanation = QLabel(
            "Comprueba la conexión y las rutas de vídeo de la cámara.\n"
            "Las credenciales se utilizan solo durante esta prueba."
        )
        explanation.setWordWrap(True)
        layout.addWidget(explanation)

        self._fields = QWidget(self)
        form = QFormLayout(self._fields)

        self._host = QLineEdit("192.168.178.61")

        self._port = QSpinBox()
        self._port.setRange(1, 65535)
        self._port.setValue(554)

        self._paths = QLineEdit("/11, /1, /12")
        self._paths.setToolTip(
            "Rutas candidatas separadas por comas. "
            "No introduzcas URLs completas ni credenciales."
        )

        self._username = QLineEdit("admin")

        self._password = QLineEdit()
        self._password.setEchoMode(QLineEdit.EchoMode.Password)
        self._password.setPlaceholderText(
            "Vacío para comprobar sin autenticarse"
        )

        form.addRow("Dirección IP:", self._host)
        form.addRow("Puerto RTSP:", self._port)
        form.addRow("Rutas candidatas:", self._paths)
        form.addRow("Usuario:", self._username)
        form.addRow("Contraseña:", self._password)

        layout.addWidget(self._fields)

        self._log = QPlainTextEdit()
        self._log.setReadOnly(True)
        self._log.setMaximumBlockCount(300)
        layout.addWidget(self._log, stretch=1)

        self._status = QLabel("Preparado para comprobar la cámara.")
        self._status.setWordWrap(True)
        layout.addWidget(self._status)

        buttons = QHBoxLayout()

        self._start_button = QPushButton("Iniciar diagnóstico")
        self._open_video_button = QPushButton("Abrir vídeo en MeteoCam")
        self._close_button = QPushButton("Cerrar")

        self._open_video_button.setEnabled(False)

        self._start_button.clicked.connect(self._start)
        self._open_video_button.clicked.connect(self._open_video)
        self._close_button.clicked.connect(self.reject)

        buttons.addWidget(self._start_button)
        buttons.addWidget(self._open_video_button)
        buttons.addStretch()
        buttons.addWidget(self._close_button)

        layout.addLayout(buttons)

    def _start(self) -> None:
        """Iniciar una prueba nueva con las credenciales introducidas."""
        if self._worker is not None:
            return

        paths = tuple(
            path.strip()
            for path in self._paths.text().split(",")
            if path.strip()
        )

        target = CameraTarget(
            host=self._host.text().strip(),
            port=self._port.value(),
            paths=paths,
        )

        credentials = None

        if self._password.text():
            credentials = Credentials(
                username=self._username.text(),
                password=self._password.text(),
            )

        self._clear_validated_stream()
        self._password.clear()
        self._log.clear()
        self._status.setText("Comprobando la cámara…")
        self._fields.setEnabled(False)
        self._start_button.setEnabled(False)
        self._open_video_button.setEnabled(False)
        self._close_button.setEnabled(False)

        worker = DiagnosticWorker(target, credentials, self)
        worker.event_received.connect(self._show_event)
        worker.result_received.connect(
            lambda result: self._show_result(
                result,
                target,
                credentials,
            )
        )
        worker.finished.connect(self._finished)

        self._worker = worker
        worker.start()

    def _show_event(self, event: DiagnosticEvent) -> None:
        """Añadir una traza segura a la vista."""
        self._log.appendPlainText(f"{event.code}  {event.message}")
        self._status.setText(event.message)

    def _show_result(
        self,
        result: DiagnosticResult,
        target: CameraTarget,
        credentials: Credentials | None,
    ) -> None:
        """Actualizar el diálogo al finalizar el diagnóstico."""
        if result.status == "stream_validated":
            if credentials is None or result.validated_path is None:
                self._status.setText(
                    "La cámara respondió, pero faltan credenciales "
                    "para abrir el vídeo."
                )
                return

            self._validated_target = target
            self._validated_path = result.validated_path
            self._validated_credentials = credentials

            self._open_video_button.setEnabled(True)
            self._status.setText(
                "Vídeo validado. Pulsa «Abrir vídeo en MeteoCam»."
            )

        elif result.status == "credentials_required":
            self._status.setText(
                "La cámara solicita autenticación Digest. "
                "Introduce su contraseña y repite el diagnóstico."
            )

    def _finished(self) -> None:
        """Restaurar los controles al terminar el hilo."""
        worker = self._worker
        self._worker = None

        if worker is not None:
            worker.deleteLater()

        self._fields.setEnabled(True)
        self._start_button.setEnabled(True)
        self._close_button.setEnabled(True)

    def _open_video(self) -> None:
        """Entregar la conexión validada a la ventana principal."""
        if (
            self._validated_target is None
            or self._validated_path is None
            or self._validated_credentials is None
        ):
            return

        self.stream_ready.emit(
            self._validated_target,
            self._validated_path,
            self._validated_credentials,
        )

        self._clear_validated_stream()
        self.accept()

    def _clear_validated_stream(self) -> None:
        """Eliminar las credenciales temporales del diálogo."""
        self._validated_target = None
        self._validated_path = None
        self._validated_credentials = None

    def reject(self) -> None:
        """Cerrar sin mantener datos sensibles."""
        if self._worker is not None:
            return

        self._password.clear()
        self._clear_validated_stream()
        super().reject()

    def closeEvent(self, event) -> None:
        """Evitar destruir el hilo mientras trabaja."""
        if self._worker is not None:
            event.ignore()
            return

        self._password.clear()
        self._clear_validated_stream()
        super().closeEvent(event)


# Fin archivo: src/meteocam/diagnostics_dialog.py