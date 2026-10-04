"""Panel individual de vídeo para el dashboard de MeteoCam."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class CameraViewPanel(QGroupBox):
    """Representar una vista de cámara dentro del dashboard."""

    publication_changed = Signal(bool)

    def __init__(
        self,
        title: str,
        parent: QWidget | None = None,
    ) -> None:
        """Inicializar el panel de una vista de cámara."""
        super().__init__(title, parent)

        self._last_video_pixmap: QPixmap | None = None

        self._crear_interfaz()

    def _crear_interfaz(self) -> None:
        """Crear los controles visuales del panel."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        self._video_frame = QFrame(self)
        self._video_frame.setObjectName("videoFrame")
        self._video_frame.setFrameShape(
            QFrame.Shape.Panel
        )
        self._video_frame.setFrameShadow(
            QFrame.Shadow.Sunken
        )
        self._video_frame.setMinimumSize(1, 1)

        video_layout = QVBoxLayout(
            self._video_frame
        )
        video_layout.setContentsMargins(
            2,
            2,
            2,
            2,
        )

        self._video_label = QLabel(
            "SIN SEÑAL DE VÍDEO"
        )
        self._video_label.setObjectName(
            "videoPlaceholder"
        )
        self._video_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self._video_label.setMinimumSize(1, 1)

        video_layout.addWidget(
            self._video_label
        )

        layout.addWidget(
            self._video_frame,
            stretch=1,
        )

        information_frame = QFrame(self)
        information_frame.setObjectName(
            "win31ToolBar"
        )

        information_layout = QHBoxLayout(
            information_frame
        )
        information_layout.setContentsMargins(
            6,
            3,
            6,
            3,
        )
        information_layout.setSpacing(8)

        state_title = QLabel("Estado:")
        state_title.setObjectName("fieldTitle")

        self._state_label = QLabel(
            "DESCONECTADA"
        )
        self._state_label.setObjectName(
            "fieldValue"
        )

        information_layout.addWidget(
            state_title
        )
        information_layout.addWidget(
            self._state_label
        )
        information_layout.addStretch()

        self._publication_checkbox = QCheckBox(
            "Publicar"
        )
        self._publication_checkbox.setToolTip(
            "Publicar esta vista de forma independiente."
        )

        self._publication_state_label = QLabel(
            "NO PUBLICANDO"
        )
        self._publication_state_label.setObjectName(
            "fieldValue"
        )

        self._publication_checkbox.toggled.connect(
            self._publication_requested
        )

        information_layout.addWidget(
            self._publication_checkbox
        )
        information_layout.addWidget(
            self._publication_state_label
        )

        layout.addWidget(
            information_frame
        )

    @property
    def state(self) -> str:
        """Obtener el estado mostrado actualmente."""
        return self._state_label.text()

    @property
    def publication_enabled(self) -> bool:
        """Indicar si el usuario ha solicitado publicar la vista."""
        return self._publication_checkbox.isChecked()

    def set_state(self, state: str) -> None:
        """Actualizar el estado visible de la cámara."""
        self._state_label.setText(state)

    def set_publication_enabled(
        self,
        enabled: bool,
    ) -> None:
        """Cambiar el check sin emitir una petición de publicación."""
        self._publication_checkbox.blockSignals(True)

        try:
            self._publication_checkbox.setChecked(
                enabled
            )
        finally:
            self._publication_checkbox.blockSignals(False)

    def set_publication_available(
        self,
        available: bool,
    ) -> None:
        """Habilitar o bloquear el control de publicación."""
        self._publication_checkbox.setEnabled(
            available
        )

    def set_publication_state(
        self,
        state: str,
    ) -> None:
        """Actualizar el estado visible de publicación."""
        self._publication_state_label.setText(
            state
        )

    def set_publication_starting(self) -> None:
        """Mostrar que la publicación está arrancando."""
        self.set_publication_state(
            "INICIANDO..."
        )

    def set_publishing(self) -> None:
        """Mostrar que la vista está siendo publicada."""
        self.set_publication_state(
            "PUBLICANDO"
        )

    def set_not_publishing(self) -> None:
        """Mostrar que la vista no está siendo publicada."""
        self.set_publication_state(
            "NO PUBLICANDO"
        )

    def set_publication_error(self) -> None:
        """Mostrar un error independiente de publicación."""
        self.set_publication_state(
            "ERROR PUBLICACIÓN"
        )

    def _publication_requested(
        self,
        enabled: bool,
    ) -> None:
        """Emitir la intención de publicar o detener la publicación."""
        self.publication_changed.emit(
            enabled
        )

    def set_connecting(self) -> None:
        """Mostrar que se está abriendo la vista."""
        self._last_video_pixmap = None

        self._video_label.clear()
        self._video_label.setText(
            "CONECTANDO CON LA CÁMARA...\n\n"
            "Esperando el primer fotograma."
        )

        self.set_state("CONECTANDO")

    def set_disconnected(
        self,
        message: str = "SIN SEÑAL DE VÍDEO",
    ) -> None:
        """Dejar el panel en estado desconectado."""
        self._last_video_pixmap = None

        self._video_label.clear()
        self._video_label.setText(message)

        self.set_state("DESCONECTADA")

    def set_error(
        self,
        message: str = (
            "NO SE HA PODIDO ABRIR EL VÍDEO"
        ),
    ) -> None:
        """Mostrar un error de recepción de vídeo."""
        self._last_video_pixmap = None

        self._video_label.clear()
        self._video_label.setText(message)

        self.set_state("ERROR")

    def set_frame(self, image) -> None:
        """Mostrar un fotograma recibido por la vista."""
        pixmap = QPixmap.fromImage(image)

        if pixmap.isNull():
            return

        self._last_video_pixmap = pixmap
        self.set_state("VÍDEO ACTIVO")

        self._actualizar_imagen_video()

    def _actualizar_imagen_video(self) -> None:
        """Escalar el último fotograma al espacio disponible."""
        if self._last_video_pixmap is None:
            return

        size = self._video_label.size()

        if size.width() < 1 or size.height() < 1:
            return

        self._video_label.setPixmap(
            self._last_video_pixmap.scaled(
                size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def resizeEvent(self, event) -> None:
        """Reescalar el vídeo cuando cambie el tamaño del panel."""
        self._actualizar_imagen_video()

        super().resizeEvent(event)


# Fin de fichero
# Fin archivo: src/meteocam/camera_view_panel.py