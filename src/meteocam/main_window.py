"""Ventana principal de MeteoCam."""

from pathlib import Path

from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QMouseEvent, QPixmap
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


class TitleBarWin31(QFrame):
    """Barra de título personalizada inspirada en Windows 3.1."""

    def __init__(self, window: QMainWindow) -> None:
        """Inicializar la barra de título."""
        super().__init__(window)

        self._window = window
        self._drag_position: QPoint | None = None

        self.setObjectName("win31TitleBar")
        self.setFixedHeight(28)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(3, 3, 3, 3)
        layout.setSpacing(3)

        self._system_button = QPushButton()
        self._system_button.setObjectName("win31SystemButton")
        self._system_button.setFixedSize(22, 22)
        self._system_button.setToolTip("Menú de control")
        self._system_button.clicked.connect(self._mostrar_menu_control)

        icon_label = QLabel(self._system_button)
        icon_label.setObjectName("win31ApplicationIcon")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        icon_label.setGeometry(2, 2, 18, 18)

        icon_path = (
            Path(__file__).resolve().parent
            / "themes"
            / "icono-192.png"
        )

        pixmap = QPixmap(str(icon_path))

        if not pixmap.isNull():
            icon_label.setPixmap(
                pixmap.scaled(
                    16,
                    16,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

        self._title_label = QLabel("MeteoCam")
        self._title_label.setObjectName("win31TitleText")
        self._title_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        self._minimize_button = QPushButton("▼")
        self._minimize_button.setObjectName("win31CaptionButton")
        self._minimize_button.setFixedSize(22, 22)
        self._minimize_button.setToolTip("Minimizar")
        self._minimize_button.clicked.connect(self._window.showMinimized)

        self._maximize_button = QPushButton("▲")
        self._maximize_button.setObjectName("win31CaptionButton")
        self._maximize_button.setFixedSize(22, 22)
        self._maximize_button.setToolTip("Maximizar")
        self._maximize_button.clicked.connect(self._alternar_maximizado)

        self._close_button = QPushButton("×")
        self._close_button.setObjectName("win31CaptionButton")
        self._close_button.setFixedSize(22, 22)
        self._close_button.setToolTip("Cerrar")
        self._close_button.clicked.connect(self._window.close)

        layout.addWidget(self._system_button)
        layout.addWidget(self._title_label, stretch=1)
        layout.addWidget(self._minimize_button)
        layout.addWidget(self._maximize_button)
        layout.addWidget(self._close_button)

    def _mostrar_menu_control(self) -> None:
        """Mantener por ahora el botón de sistema como elemento visual."""
        self._window.showNormal()

    def _alternar_maximizado(self) -> None:
        """Alternar entre ventana maximizada y restaurada."""
        if self._window.isMaximized():
            self._window.showNormal()
            self._maximize_button.setText("▲")
            self._maximize_button.setToolTip("Maximizar")
        else:
            self._window.showMaximized()
            self._maximize_button.setText("◆")
            self._maximize_button.setToolTip("Restaurar")

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        """Maximizar o restaurar con doble clic en la barra."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._alternar_maximizado()
            event.accept()
            return

        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Iniciar el arrastre de la ventana."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = (
                event.globalPosition().toPoint()
                - self._window.frameGeometry().topLeft()
            )
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Mover la ventana mientras se arrastra la barra de título."""
        if (
            self._drag_position is not None
            and event.buttons() & Qt.MouseButton.LeftButton
        ):
            if self._window.isMaximized():
                self._window.showNormal()

                relative_x = event.position().x()
                window_width = max(self._window.width(), 1)
                ratio = relative_x / window_width

                new_x = int(
                    event.globalPosition().x()
                    - (self._window.width() * ratio)
                )
                new_y = int(event.globalPosition().y() - 12)

                self._drag_position = QPoint(
                    int(event.globalPosition().x() - new_x),
                    int(event.globalPosition().y() - new_y),
                )

            self._window.move(
                event.globalPosition().toPoint() - self._drag_position
            )
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Finalizar el arrastre de la ventana."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = None
            event.accept()
            return

        super().mouseReleaseEvent(event)


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación MeteoCam."""

    RESIZE_MARGIN = 7

    EDGE_NONE = 0
    EDGE_LEFT = 1
    EDGE_TOP = 2
    EDGE_RIGHT = 4
    EDGE_BOTTOM = 8

    def __init__(self) -> None:
        """Inicializar la ventana principal."""
        super().__init__()

        self.setWindowTitle("MeteoCam")

        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowMinMaxButtonsHint
        )

        self.resize(1100, 760)
        self.setMinimumSize(800, 600)

        self._resize_edges = self.EDGE_NONE
        self._resize_start_position = QPoint()
        self._resize_start_geometry = QRect()

        self.setMouseTracking(True)

        self._crear_interfaz()
        self._crear_barra_estado()

    def _crear_interfaz(self) -> None:
        """Crear la estructura visual principal."""
        central_widget = QWidget(self)
        central_widget.setObjectName("mainWindowSurface")
        central_widget.setMouseTracking(True)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(6)

        main_layout.addWidget(TitleBarWin31(self))
        main_layout.addWidget(self._crear_menu_principal())
        main_layout.addWidget(self._crear_barra_herramientas())
        main_layout.addWidget(self._crear_panel_informacion())
        main_layout.addWidget(self._crear_panel_video(), stretch=1)

        self.setCentralWidget(central_widget)

    def _crear_menu_principal(self) -> QFrame:
        """Crear una barra de menú visual de estilo clásico."""
        frame = QFrame(self)
        frame.setObjectName("win31MenuBar")

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.setSpacing(18)

        for texto in (
            "Archivo",
            "Cámara",
            "Ver",
            "Herramientas",
            "Ayuda",
        ):
            label = QLabel(texto)
            label.setObjectName("win31MenuItem")
            layout.addWidget(label)

        layout.addStretch()

        return frame

    def _crear_barra_herramientas(self) -> QFrame:
        """Crear la barra principal de comandos."""
        frame = QFrame(self)
        frame.setObjectName("win31ToolBar")

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(4, 3, 4, 3)
        layout.setSpacing(5)

        buscar_button = QPushButton("Buscar...")
        conectar_button = QPushButton("Conectar")
        desconectar_button = QPushButton("Desconectar")
        actualizar_button = QPushButton("Actualizar")

        desconectar_button.setEnabled(False)

        configuration_button = QPushButton("Configuración...")
        diagnostics_button = QPushButton("Diagnóstico...")

        for button in (
            buscar_button,
            conectar_button,
            desconectar_button,
            actualizar_button,
            configuration_button,
            diagnostics_button,
        ):
            button.setMinimumHeight(28)

        separator = QFrame(frame)
        separator.setObjectName("win31ToolSeparator")
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)

        layout.addWidget(buscar_button)
        layout.addWidget(conectar_button)
        layout.addWidget(desconectar_button)
        layout.addWidget(actualizar_button)
        layout.addWidget(separator)
        layout.addWidget(configuration_button)
        layout.addWidget(diagnostics_button)

        layout.addStretch()

        version_label = QLabel(f"MeteoCam {__version__}")
        version_label.setObjectName("toolbarVersion")
        layout.addWidget(version_label)

        return frame

    def _crear_panel_informacion(self) -> QGroupBox:
        """Crear el panel con la información de la cámara seleccionada."""
        group = QGroupBox("Cámara seleccionada")

        layout = QHBoxLayout(group)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(24)

        layout.addWidget(
            self._crear_campo("Estación:", "Sin configurar"),
            stretch=1,
        )
        layout.addWidget(
            self._crear_campo("Dispositivo:", "Sin configurar"),
            stretch=1,
        )
        layout.addWidget(
            self._crear_campo("Vista:", "Sin seleccionar"),
            stretch=1,
        )
        layout.addWidget(
            self._crear_campo("Estado:", "DESCONECTADA"),
            stretch=1,
        )

        return group

    def _crear_campo(self, titulo: str, valor: str) -> QWidget:
        """Crear un campo informativo compuesto por título y valor."""
        widget = QWidget(self)

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)

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
        layout.setContentsMargins(10, 8, 10, 10)

        video_frame = QFrame(group)
        video_frame.setObjectName("videoFrame")
        video_frame.setFrameShape(QFrame.Shape.Panel)
        video_frame.setFrameShadow(QFrame.Shadow.Sunken)
        video_frame.setMinimumHeight(360)

        video_layout = QVBoxLayout(video_frame)
        video_layout.setContentsMargins(2, 2, 2, 2)

        video_label = QLabel(
            "SIN SEÑAL DE VÍDEO\n\n"
            "No hay ninguna cámara conectada."
        )
        video_label.setObjectName("videoPlaceholder")
        video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        video_layout.addWidget(video_label)
        layout.addWidget(video_frame)

        return group

    def _crear_barra_estado(self) -> None:
        """Crear la barra de estado inferior."""
        status_bar = QStatusBar(self)
        status_bar.setObjectName("win31StatusBar")
        status_bar.showMessage(" MeteoCam preparado")
        self.setStatusBar(status_bar)

    def _detectar_bordes(self, posicion: QPoint) -> int:
        """Detectar lados o esquinas disponibles para redimensionar."""
        if self.isMaximized():
            return self.EDGE_NONE

        edges = self.EDGE_NONE
        margin = self.RESIZE_MARGIN

        if posicion.x() <= margin:
            edges |= self.EDGE_LEFT
        elif posicion.x() >= self.width() - margin:
            edges |= self.EDGE_RIGHT

        if posicion.y() <= margin:
            edges |= self.EDGE_TOP
        elif posicion.y() >= self.height() - margin:
            edges |= self.EDGE_BOTTOM

        return edges

    def _actualizar_cursor_redimensionado(self, edges: int) -> None:
        """Mostrar el cursor apropiado según el borde señalado."""
        if edges in (
            self.EDGE_LEFT | self.EDGE_TOP,
            self.EDGE_RIGHT | self.EDGE_BOTTOM,
        ):
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            return

        if edges in (
            self.EDGE_RIGHT | self.EDGE_TOP,
            self.EDGE_LEFT | self.EDGE_BOTTOM,
        ):
            self.setCursor(Qt.CursorShape.SizeBDiagCursor)
            return

        if edges in (self.EDGE_LEFT, self.EDGE_RIGHT):
            self.setCursor(Qt.CursorShape.SizeHorCursor)
            return

        if edges in (self.EDGE_TOP, self.EDGE_BOTTOM):
            self.setCursor(Qt.CursorShape.SizeVerCursor)
            return

        self.unsetCursor()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Iniciar manualmente el redimensionado de la ventana."""
        if event.button() == Qt.MouseButton.LeftButton:
            edges = self._detectar_bordes(event.position().toPoint())

            if edges != self.EDGE_NONE:
                self._resize_edges = edges
                self._resize_start_position = event.globalPosition().toPoint()
                self._resize_start_geometry = self.geometry()
                event.accept()
                return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Redimensionar la ventana o actualizar el cursor del borde."""
        if (
            self._resize_edges != self.EDGE_NONE
            and event.buttons() & Qt.MouseButton.LeftButton
        ):
            current_position = event.globalPosition().toPoint()

            delta_x = (
                current_position.x()
                - self._resize_start_position.x()
            )
            delta_y = (
                current_position.y()
                - self._resize_start_position.y()
            )

            geometry = QRect(self._resize_start_geometry)

            minimum_width = self.minimumWidth()
            minimum_height = self.minimumHeight()

            if self._resize_edges & self.EDGE_LEFT:
                new_left = (
                    self._resize_start_geometry.left()
                    + delta_x
                )

                maximum_left = (
                    self._resize_start_geometry.right()
                    - minimum_width
                    + 1
                )

                geometry.setLeft(min(new_left, maximum_left))

            if self._resize_edges & self.EDGE_RIGHT:
                new_right = (
                    self._resize_start_geometry.right()
                    + delta_x
                )

                minimum_right = (
                    self._resize_start_geometry.left()
                    + minimum_width
                    - 1
                )

                geometry.setRight(max(new_right, minimum_right))

            if self._resize_edges & self.EDGE_TOP:
                new_top = (
                    self._resize_start_geometry.top()
                    + delta_y
                )

                maximum_top = (
                    self._resize_start_geometry.bottom()
                    - minimum_height
                    + 1
                )

                geometry.setTop(min(new_top, maximum_top))

            if self._resize_edges & self.EDGE_BOTTOM:
                new_bottom = (
                    self._resize_start_geometry.bottom()
                    + delta_y
                )

                minimum_bottom = (
                    self._resize_start_geometry.top()
                    + minimum_height
                    - 1
                )

                geometry.setBottom(max(new_bottom, minimum_bottom))

            self.setGeometry(geometry)

            event.accept()
            return

        edges = self._detectar_bordes(event.position().toPoint())
        self._actualizar_cursor_redimensionado(edges)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Finalizar el redimensionado manual."""
        if (
            event.button() == Qt.MouseButton.LeftButton
            and self._resize_edges != self.EDGE_NONE
        ):
            self._resize_edges = self.EDGE_NONE

            edges = self._detectar_bordes(event.position().toPoint())
            self._actualizar_cursor_redimensionado(edges)

            event.accept()
            return

        super().mouseReleaseEvent(event)

    def leaveEvent(self, event) -> None:
        """Restaurar el cursor al abandonar la ventana."""
        if self._resize_edges == self.EDGE_NONE:
            self.unsetCursor()

        super().leaveEvent(event)


# Fin de fichero
# Fin archivo: src/meteocam/main_window.py