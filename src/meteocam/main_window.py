"""Ventana principal de MeteoCam."""

from pathlib import Path

from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QMouseEvent, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QInputDialog,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from meteocam import __version__
from meteocam.camera_config_dialog import CameraConfigDialog
from meteocam.camera_view_panel import CameraViewPanel
from meteocam.cameras.config import CAMERAS, CameraConfig
from meteocam.cameras.diagnostics import CameraTarget, Credentials
from meteocam.cameras.stream_player import StreamPlayer
from meteocam.cameras.tcp_publisher import TcpPublisher
from meteocam.diagnostics_dialog import DiagnosticsDialog


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
        self._system_button.clicked.connect(
            self._mostrar_menu_control
        )

        icon_label = QLabel(
            self._system_button
        )
        icon_label.setObjectName(
            "win31ApplicationIcon"
        )
        icon_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        icon_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents
        )
        icon_label.setGeometry(
            2,
            2,
            18,
            18,
        )

        icon_path = (
            Path(__file__).resolve().parent
            / "themes"
            / "icono-192.png"
        )

        pixmap = QPixmap(
            str(icon_path)
        )

        if not pixmap.isNull():
            icon_label.setPixmap(
                pixmap.scaled(
                    16,
                    16,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

        self._title_label = QLabel(
            "MeteoCam"
        )
        self._title_label.setObjectName(
            "win31TitleText"
        )
        self._title_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignVCenter
        )

        self._minimize_button = QPushButton(
            "▼"
        )
        self._minimize_button.setObjectName(
            "win31CaptionButton"
        )
        self._minimize_button.setFixedSize(
            22,
            22,
        )
        self._minimize_button.setToolTip(
            "Minimizar"
        )
        self._minimize_button.clicked.connect(
            self._window.showMinimized
        )

        self._maximize_button = QPushButton(
            "▲"
        )
        self._maximize_button.setObjectName(
            "win31CaptionButton"
        )
        self._maximize_button.setFixedSize(
            22,
            22,
        )
        self._maximize_button.setToolTip(
            "Maximizar"
        )
        self._maximize_button.clicked.connect(
            self._alternar_maximizado
        )

        self._close_button = QPushButton(
            "×"
        )
        self._close_button.setObjectName(
            "win31CaptionButton"
        )
        self._close_button.setFixedSize(
            22,
            22,
        )
        self._close_button.setToolTip(
            "Cerrar"
        )
        self._close_button.clicked.connect(
            self._window.close
        )

        layout.addWidget(
            self._system_button
        )
        layout.addWidget(
            self._title_label,
            stretch=1,
        )
        layout.addWidget(
            self._minimize_button
        )
        layout.addWidget(
            self._maximize_button
        )
        layout.addWidget(
            self._close_button
        )

    def _mostrar_menu_control(self) -> None:
        """Mantener por ahora el botón de sistema como elemento visual."""
        self._window.showNormal()

    def _alternar_maximizado(self) -> None:
        """Alternar entre ventana maximizada y restaurada."""
        if self._window.isMaximized():
            self._window.showNormal()

            self._maximize_button.setText(
                "▲"
            )
            self._maximize_button.setToolTip(
                "Maximizar"
            )

        else:
            self._window.showMaximized()

            self._maximize_button.setText(
                "◆"
            )
            self._maximize_button.setToolTip(
                "Restaurar"
            )

    def mouseDoubleClickEvent(
        self,
        event: QMouseEvent,
    ) -> None:
        """Maximizar o restaurar con doble clic en la barra."""
        if (
            event.button()
            == Qt.MouseButton.LeftButton
        ):
            self._alternar_maximizado()

            event.accept()
            return

        super().mouseDoubleClickEvent(
            event
        )

    def mousePressEvent(
        self,
        event: QMouseEvent,
    ) -> None:
        """Iniciar el arrastre de la ventana."""
        if (
            event.button()
            == Qt.MouseButton.LeftButton
        ):
            self._drag_position = (
                event.globalPosition().toPoint()
                - self._window.frameGeometry().topLeft()
            )

            event.accept()
            return

        super().mousePressEvent(
            event
        )

    def mouseMoveEvent(
        self,
        event: QMouseEvent,
    ) -> None:
        """Mover la ventana mientras se arrastra la barra de título."""
        if (
            self._drag_position is not None
            and event.buttons()
            & Qt.MouseButton.LeftButton
        ):
            if self._window.isMaximized():
                self._window.showNormal()

                relative_x = (
                    event.position().x()
                )

                window_width = max(
                    self._window.width(),
                    1,
                )

                ratio = (
                    relative_x
                    / window_width
                )

                new_x = int(
                    event.globalPosition().x()
                    - (
                        self._window.width()
                        * ratio
                    )
                )

                new_y = int(
                    event.globalPosition().y()
                    - 12
                )

                self._drag_position = QPoint(
                    int(
                        event.globalPosition().x()
                        - new_x
                    ),
                    int(
                        event.globalPosition().y()
                        - new_y
                    ),
                )

            self._window.move(
                event.globalPosition().toPoint()
                - self._drag_position
            )

            event.accept()
            return

        super().mouseMoveEvent(
            event
        )

    def mouseReleaseEvent(
        self,
        event: QMouseEvent,
    ) -> None:
        """Finalizar el arrastre de la ventana."""
        if (
            event.button()
            == Qt.MouseButton.LeftButton
        ):
            self._drag_position = None

            event.accept()
            return

        super().mouseReleaseEvent(
            event
        )


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación MeteoCam."""

    RESIZE_MARGIN = 7

    EDGE_NONE = 0
    EDGE_LEFT = 1
    EDGE_TOP = 2
    EDGE_RIGHT = 4
    EDGE_BOTTOM = 8

    TCP_VPS_HOST = "187.124.114.42"

    PANORAMIC_TCP_PORT = 10080
    PTZ_TCP_PORT = 10081

    def __init__(self) -> None:
        """Inicializar la ventana principal."""
        super().__init__()

        self.setWindowTitle(
            "MeteoCam"
        )

        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowMinMaxButtonsHint
        )

        self.resize(
            1200,
            760,
        )

        self.setMinimumSize(
            900,
            600,
        )

        self._resize_edges = (
            self.EDGE_NONE
        )

        self._resize_start_position = QPoint()
        self._resize_start_geometry = QRect()

        self._panoramic_camera = (
            self._buscar_vista(
                "-panoramica"
            )
        )

        self._ptz_camera = (
            self._buscar_vista(
                "-ptz"
            )
        )

        self._panoramic_player: StreamPlayer | None = (
            None
        )

        self._ptz_player: StreamPlayer | None = (
            None
        )

        self._panoramic_publisher: TcpPublisher | None = (
            None
        )

        self._ptz_publisher: TcpPublisher | None = (
            None
        )

        self._session_username: str | None = (
            None
        )

        self._session_password: str | None = (
            None
        )

        self.setMouseTracking(
            True
        )

        self._crear_interfaz()
        self._crear_barra_estado()
        self._actualizar_disponibilidad()

    @staticmethod
    def _buscar_vista(
        suffix: str,
    ) -> CameraConfig | None:
        """Localizar una vista configurada mediante el sufijo de su código."""
        return next(
            (
                camera
                for camera in CAMERAS
                if camera.code.endswith(
                    suffix
                )
            ),
            None,
        )

    def _crear_interfaz(self) -> None:
        """Crear la estructura visual principal."""
        central_widget = QWidget(
            self
        )

        central_widget.setObjectName(
            "mainWindowSurface"
        )

        central_widget.setMouseTracking(
            True
        )

        main_layout = QVBoxLayout(
            central_widget
        )

        main_layout.setContentsMargins(
            4,
            4,
            4,
            4,
        )

        main_layout.setSpacing(
            6
        )

        main_layout.addWidget(
            TitleBarWin31(
                self
            )
        )

        main_layout.addWidget(
            self._crear_menu_principal()
        )

        main_layout.addWidget(
            self._crear_barra_herramientas()
        )

        main_layout.addWidget(
            self._crear_panel_informacion()
        )

        main_layout.addWidget(
            self._crear_dashboard_video(),
            stretch=1,
        )

        self.setCentralWidget(
            central_widget
        )

    def _crear_menu_principal(
        self,
    ) -> QFrame:
        """Crear una barra de menú visual de estilo clásico."""
        frame = QFrame(
            self
        )

        frame.setObjectName(
            "win31MenuBar"
        )

        layout = QHBoxLayout(
            frame
        )

        layout.setContentsMargins(
            4,
            0,
            4,
            0,
        )

        layout.setSpacing(
            18
        )

        for texto in (
            "Archivo",
            "Cámara",
            "Ver",
            "Herramientas",
            "Ayuda",
        ):
            label = QLabel(
                texto
            )

            label.setObjectName(
                "win31MenuItem"
            )

            layout.addWidget(
                label
            )

        layout.addStretch()

        return frame

    def _crear_barra_herramientas(
        self,
    ) -> QFrame:
        """Crear la barra principal de comandos."""
        frame = QFrame(
            self
        )

        frame.setObjectName(
            "win31ToolBar"
        )

        layout = QHBoxLayout(
            frame
        )

        layout.setContentsMargins(
            4,
            3,
            4,
            3,
        )

        layout.setSpacing(
            5
        )

        buscar_button = QPushButton(
            "Buscar..."
        )

        self._conectar_button = QPushButton(
            "Conectar"
        )

        self._desconectar_button = QPushButton(
            "Desconectar"
        )

        actualizar_button = QPushButton(
            "Actualizar"
        )

        configuration_button = QPushButton(
            "Configuración..."
        )

        diagnostics_button = QPushButton(
            "Diagnóstico..."
        )

        self._desconectar_button.setEnabled(
            False
        )

        self._conectar_button.clicked.connect(
            self._conectar_camaras
        )

        self._desconectar_button.clicked.connect(
            self._desconectar_camaras
        )

        configuration_button.clicked.connect(
            self._abrir_configuracion
        )

        diagnostics_button.clicked.connect(
            self._abrir_diagnostico
        )

        for button in (
            buscar_button,
            self._conectar_button,
            self._desconectar_button,
            actualizar_button,
            configuration_button,
            diagnostics_button,
        ):
            button.setMinimumHeight(
                28
            )

        separator = QFrame(
            frame
        )

        separator.setObjectName(
            "win31ToolSeparator"
        )

        separator.setFrameShape(
            QFrame.Shape.VLine
        )

        separator.setFrameShadow(
            QFrame.Shadow.Sunken
        )

        layout.addWidget(
            buscar_button
        )

        layout.addWidget(
            self._conectar_button
        )

        layout.addWidget(
            self._desconectar_button
        )

        layout.addWidget(
            actualizar_button
        )

        layout.addWidget(
            separator
        )

        layout.addWidget(
            configuration_button
        )

        layout.addWidget(
            diagnostics_button
        )

        layout.addStretch()

        version_label = QLabel(
            f"MeteoCam {__version__}"
        )

        version_label.setObjectName(
            "toolbarVersion"
        )

        layout.addWidget(
            version_label
        )

        return frame

    def _crear_panel_informacion(
        self,
    ) -> QGroupBox:
        """Crear el resumen del dispositivo mostrado en el dashboard."""
        group = QGroupBox(
            "MeteoCam Los Llanos"
        )

        layout = QHBoxLayout(
            group
        )

        layout.setContentsMargins(
            10,
            8,
            10,
            8,
        )

        layout.setSpacing(
            24
        )

        station = (
            self._panoramic_camera
            or self._ptz_camera
        )

        layout.addWidget(
            self._crear_campo(
                "Estación:",
                (
                    station.station
                    if station is not None
                    else "Sin configurar"
                ),
            ),
            stretch=1,
        )

        layout.addWidget(
            self._crear_campo(
                "Dispositivo:",
                (
                    f"{station.manufacturer} "
                    f"{station.model}"
                    if station is not None
                    else "Sin configurar"
                ),
            ),
            stretch=1,
        )

        layout.addWidget(
            self._crear_campo(
                "Vistas:",
                "Panorámica + PTZ",
            ),
            stretch=1,
        )

        self._general_state_value = QLabel(
            "DESCONECTADA"
        )

        self._general_state_value.setObjectName(
            "fieldValue"
        )

        state_widget = QWidget(
            self
        )

        state_layout = QVBoxLayout(
            state_widget
        )

        state_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        state_layout.setSpacing(
            1
        )

        state_title = QLabel(
            "Estado:"
        )

        state_title.setObjectName(
            "fieldTitle"
        )

        state_layout.addWidget(
            state_title
        )

        state_layout.addWidget(
            self._general_state_value
        )

        layout.addWidget(
            state_widget,
            stretch=1,
        )

        return group

    def _crear_campo(
        self,
        titulo: str,
        valor: str,
    ) -> QWidget:
        """Crear un campo informativo compuesto por título y valor."""
        widget = QWidget(
            self
        )

        layout = QVBoxLayout(
            widget
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )

        layout.setSpacing(
            1
        )

        title_label = QLabel(
            titulo
        )

        title_label.setObjectName(
            "fieldTitle"
        )

        value_label = QLabel(
            valor
        )

        value_label.setObjectName(
            "fieldValue"
        )

        layout.addWidget(
            title_label
        )

        layout.addWidget(
            value_label
        )

        return widget

    def _crear_dashboard_video(
        self,
    ) -> QGroupBox:
        """Crear el dashboard con Panorámica y PTZ simultáneas."""
        group = QGroupBox(
            "Vídeo en directo"
        )

        layout = QHBoxLayout(
            group
        )

        layout.setContentsMargins(
            10,
            8,
            10,
            10,
        )

        layout.setSpacing(
            8
        )

        self._panoramic_panel = (
            CameraViewPanel(
                "Panorámica",
                group,
            )
        )

        self._ptz_panel = (
            CameraViewPanel(
                "PTZ",
                group,
            )
        )

        self._panoramic_panel.publication_changed.connect(
            self._cambiar_publicacion_panoramica
        )

        self._ptz_panel.publication_changed.connect(
            self._cambiar_publicacion_ptz
        )

        self._panoramic_panel.set_publication_available(
            False
        )

        self._ptz_panel.set_publication_available(
            False
        )

        self._panoramic_panel.set_disconnected(
            "SIN SEÑAL DE VÍDEO"
        )

        self._ptz_panel.set_disconnected(
            "SIN SEÑAL DE VÍDEO"
        )

        layout.addWidget(
            self._panoramic_panel,
            stretch=1,
        )

        layout.addWidget(
            self._ptz_panel,
            stretch=1,
        )

        return group

    def _actualizar_disponibilidad(
        self,
    ) -> None:
        """Actualizar los controles según las vistas configuradas."""
        available = (
            self._panoramic_camera is not None
            and self._ptz_camera is not None
        )

        self._conectar_button.setEnabled(
            available
        )

        if available:
            self.statusBar().showMessage(
                " MeteoCam preparado: "
                "Panorámica y PTZ disponibles"
            )

            return

        self._general_state_value.setText(
            "CONFIGURACIÓN INCOMPLETA"
        )

        self.statusBar().showMessage(
            " Faltan las vistas Panorámica "
            "o PTZ en la configuración"
        )

    def _conectar_camaras(
        self,
    ) -> None:
        """Conectar simultáneamente Panorámica y PTZ."""
        if (
            self._panoramic_camera is None
            or self._ptz_camera is None
        ):
            self.statusBar().showMessage(
                " No están configuradas las dos "
                "vistas de Los Llanos."
            )

            return

        username, accepted = QInputDialog.getText(
            self,
            "MeteoCam — Credenciales",
            "Usuario de la cámara:",
            QLineEdit.EchoMode.Normal,
            "admin",
        )

        if not accepted:
            return

        username = (
            username.strip()
        )

        if not username:
            self.statusBar().showMessage(
                " Debes indicar el usuario "
                "de la cámara."
            )

            return

        password, accepted = QInputDialog.getText(
            self,
            "MeteoCam — Credenciales",
            "Contraseña de la cámara:",
            QLineEdit.EchoMode.Password,
        )

        if not accepted:
            return

        credentials = Credentials(
            username=username,
            password=password,
        )

        self._detener_todos_los_publicadores()
        self._detener_todos_los_videos()

        self._session_username = (
            username
        )

        self._session_password = (
            password
        )

        self._panoramic_panel.set_publication_enabled(
            False
        )

        self._ptz_panel.set_publication_enabled(
            False
        )

        self._panoramic_panel.set_not_publishing()
        self._ptz_panel.set_not_publishing()

        self._panoramic_panel.set_publication_available(
            True
        )

        self._ptz_panel.set_publication_available(
            True
        )

        self._panoramic_panel.set_connecting()
        self._ptz_panel.set_connecting()

        self._general_state_value.setText(
            "CONECTANDO"
        )

        self._conectar_button.setEnabled(
            False
        )

        self._desconectar_button.setEnabled(
            True
        )

        self._panoramic_player = (
            self._crear_reproductor(
                self._panoramic_camera,
                credentials,
                self._panoramic_panel,
                "Panorámica",
            )
        )

        self._ptz_player = (
            self._crear_reproductor(
                self._ptz_camera,
                credentials,
                self._ptz_panel,
                "PTZ",
            )
        )

        self.statusBar().showMessage(
            " Abriendo Panorámica y PTZ "
            "simultáneamente..."
        )

        self._panoramic_player.start()
        self._ptz_player.start()

    def _crear_reproductor(
        self,
        camera: CameraConfig,
        credentials: Credentials,
        panel: CameraViewPanel,
        view_name: str,
    ) -> StreamPlayer:
        """Crear un reproductor RTSP independiente para una vista."""
        target = CameraTarget(
            host=camera.host,
            port=camera.rtsp_port,
            paths=(
                camera.rtsp_path,
            ),
        )

        player_credentials = Credentials(
            username=credentials.username,
            password=credentials.password,
        )

        player = StreamPlayer(
            target=target,
            path=camera.rtsp_path,
            credentials=player_credentials,
            parent=self,
            publish_hls=False,
            hls_host="127.0.0.1",
            hls_port=0,
        )

        player.frame_received.connect(
            panel.set_frame
        )

        player.status_changed.connect(
            lambda code,
            message,
            p=panel,
            name=view_name: (
                self._mostrar_estado_vista(
                    p,
                    name,
                    code,
                    message,
                )
            )
        )

        player.finished.connect(
            lambda p=player,
            name=view_name: (
                self._video_finalizado(
                    p,
                    name,
                )
            )
        )

        return player

    def _cambiar_publicacion_panoramica(
        self,
        enabled: bool,
    ) -> None:
        """Activar o detener la publicación TCP de la panorámica."""
        self._cambiar_publicacion_tcp(
            enabled=enabled,
            camera=self._panoramic_camera,
            panel=self._panoramic_panel,
            view_name="Panorámica",
            publisher_attribute=(
                "_panoramic_publisher"
            ),
            tcp_port=(
                self.PANORAMIC_TCP_PORT
            ),
        )

    def _cambiar_publicacion_ptz(
        self,
        enabled: bool,
    ) -> None:
        """Activar o detener la publicación TCP de la vista PTZ."""
        self._cambiar_publicacion_tcp(
            enabled=enabled,
            camera=self._ptz_camera,
            panel=self._ptz_panel,
            view_name="PTZ",
            publisher_attribute=(
                "_ptz_publisher"
            ),
            tcp_port=(
                self.PTZ_TCP_PORT
            ),
        )

    def _cambiar_publicacion_tcp(
        self,
        enabled: bool,
        camera: CameraConfig | None,
        panel: CameraViewPanel,
        view_name: str,
        publisher_attribute: str,
        tcp_port: int,
    ) -> None:
        """Gestionar el envío TCP independiente de una vista."""
        publisher = getattr(
            self,
            publisher_attribute,
        )

        if not enabled:
            if publisher is not None:
                publisher.stop()

            panel.set_not_publishing()

            self.statusBar().showMessage(
                f" {view_name}: "
                "envío TCP detenido"
            )

            return

        if camera is None:
            panel.set_publication_enabled(
                False
            )

            panel.set_publication_error()

            self.statusBar().showMessage(
                f" {view_name}: "
                "vista no configurada"
            )

            return

        if (
            self._session_username is None
            or self._session_password is None
        ):
            panel.set_publication_enabled(
                False
            )

            panel.set_publication_error()

            self.statusBar().showMessage(
                f" {view_name}: "
                "conecta primero la cámara"
            )

            return

        if (
            publisher is not None
            and publisher.isRunning()
        ):
            return

        credentials = Credentials(
            username=self._session_username,
            password=self._session_password,
        )

        publisher = TcpPublisher(
            target=camera.host,
            path=camera.rtsp_path,
            credentials=credentials,
            tcp_host=self.TCP_VPS_HOST,
            tcp_port=tcp_port,
            rtsp_port=camera.rtsp_port,
            parent=self,
        )

        setattr(
            self,
            publisher_attribute,
            publisher,
        )

        publisher.publication_started.connect(
            lambda destination,
            pub=publisher,
            p=panel,
            name=view_name,
            attr=publisher_attribute: (
                self._publicacion_tcp_iniciada(
                    pub,
                    p,
                    name,
                    attr,
                    destination,
                )
            )
        )

        publisher.publication_error.connect(
            lambda message,
            pub=publisher,
            p=panel,
            name=view_name,
            attr=publisher_attribute: (
                self._error_publicacion_tcp(
                    pub,
                    p,
                    name,
                    attr,
                    message,
                )
            )
        )

        publisher.finished.connect(
            lambda pub=publisher,
            p=panel,
            name=view_name,
            attr=publisher_attribute: (
                self._publicador_tcp_finalizado(
                    pub,
                    p,
                    name,
                    attr,
                )
            )
        )

        panel.set_publication_starting()

        self.statusBar().showMessage(
            f" {view_name}: "
            "conectando con el VPS por TCP..."
        )

        publisher.start()

    def _publicacion_tcp_iniciada(
        self,
        publisher: TcpPublisher,
        panel: CameraViewPanel,
        view_name: str,
        publisher_attribute: str,
        destination: str,
    ) -> None:
        """Reflejar que una vista se está enviando al VPS."""
        if (
            getattr(
                self,
                publisher_attribute,
            )
            is not publisher
        ):
            return

        panel.set_publishing()

        self.statusBar().showMessage(
            f" {view_name}: "
            f"enviando al VPS · {destination}"
        )

    def _error_publicacion_tcp(
        self,
        publisher: TcpPublisher,
        panel: CameraViewPanel,
        view_name: str,
        publisher_attribute: str,
        message: str,
    ) -> None:
        """Mostrar un error TCP sin afectar a la otra vista."""
        if (
            getattr(
                self,
                publisher_attribute,
            )
            is not publisher
        ):
            return

        panel.set_publication_enabled(
            False
        )

        panel.set_publication_error()

        self.statusBar().showMessage(
            f" {view_name}: "
            "error de publicación TCP · "
            f"{message}"
        )

    def _publicador_tcp_finalizado(
        self,
        publisher: TcpPublisher,
        panel: CameraViewPanel,
        view_name: str,
        publisher_attribute: str,
    ) -> None:
        """Liberar un publicador TCP finalizado."""
        if (
            getattr(
                self,
                publisher_attribute,
            )
            is not publisher
        ):
            publisher.deleteLater()

            return

        setattr(
            self,
            publisher_attribute,
            None,
        )

        publisher.deleteLater()

    def _mostrar_estado_vista(
        self,
        panel: CameraViewPanel,
        view_name: str,
        code: str,
        message: str,
    ) -> None:
        """Actualizar el estado de una vista sin afectar a la otra."""
        self.statusBar().showMessage(
            f" {view_name} · "
            f"{code}  {message}"
        )

        if code == "CAM-STREAM-200":
            panel.set_state(
                "CONECTADA"
            )

        elif code == "CAM-STREAM-201":
            panel.set_state(
                "VÍDEO ACTIVO"
            )

        elif code == "CAM-STREAM-500":
            panel.set_error(
                "NO SE HA PODIDO ABRIR "
                "EL VÍDEO\n\n"
                "Consulta el diagnóstico "
                "de la cámara."
            )

        self._actualizar_estado_general()

    def _actualizar_estado_general(
        self,
    ) -> None:
        """Calcular el estado global a partir de las dos vistas."""
        states = {
            self._panoramic_panel.state,
            self._ptz_panel.state,
        }

        if states == {
            "VÍDEO ACTIVO"
        }:
            state = (
                "VÍDEO ACTIVO"
            )

        elif states == {
            "ERROR"
        }:
            state = (
                "ERROR"
            )

        elif "ERROR" in states:
            state = (
                "ERROR PARCIAL"
            )

        elif "CONECTANDO" in states:
            state = (
                "CONECTANDO"
            )

        elif (
            "CONECTADA" in states
            or "VÍDEO ACTIVO" in states
        ):
            state = (
                "CONECTADA"
            )

        else:
            state = (
                "DESCONECTADA"
            )

        self._general_state_value.setText(
            state
        )

    def _desconectar_camaras(
        self,
    ) -> None:
        """Detener las dos vistas manteniendo el dashboard disponible."""
        self._detener_todos_los_publicadores()
        self._detener_todos_los_videos()

        self._session_username = None
        self._session_password = None

        self._panoramic_panel.set_publication_enabled(
            False
        )

        self._ptz_panel.set_publication_enabled(
            False
        )

        self._panoramic_panel.set_publication_available(
            False
        )

        self._ptz_panel.set_publication_available(
            False
        )

        self._panoramic_panel.set_not_publishing()
        self._ptz_panel.set_not_publishing()

        self._panoramic_panel.set_disconnected(
            "SIN SEÑAL DE VÍDEO\n\n"
            "Pulsa Conectar para abrir esta vista."
        )

        self._ptz_panel.set_disconnected(
            "SIN SEÑAL DE VÍDEO\n\n"
            "Pulsa Conectar para abrir esta vista."
        )

        self._general_state_value.setText(
            "DESCONECTADA"
        )

        self._conectar_button.setEnabled(
            self._panoramic_camera is not None
            and self._ptz_camera is not None
        )

        self._desconectar_button.setEnabled(
            False
        )

        self.statusBar().showMessage(
            " Vídeos desconectados"
        )

    def _detener_todos_los_publicadores(
        self,
    ) -> None:
        """Detener de forma segura las dos publicaciones TCP."""
        publishers = (
            self._panoramic_publisher,
            self._ptz_publisher,
        )

        self._panoramic_publisher = None
        self._ptz_publisher = None

        for publisher in publishers:
            if publisher is not None:
                publisher.stop()

        for publisher in publishers:
            if publisher is None:
                continue

            publisher.wait(
                6000
            )

            publisher.deleteLater()

    def _detener_todos_los_videos(
        self,
    ) -> None:
        """Detener de forma segura los dos reproductores RTSP."""
        players = (
            self._panoramic_player,
            self._ptz_player,
        )

        self._panoramic_player = None
        self._ptz_player = None

        for player in players:
            if player is None:
                continue

            player.stop()

            player.wait(
                3000
            )

            player.deleteLater()

    def _video_finalizado(
        self,
        player: StreamPlayer,
        view_name: str,
    ) -> None:
        """Liberar la referencia de un reproductor finalizado."""
        if (
            self._panoramic_player
            is player
        ):
            self._panoramic_player = (
                None
            )

        elif (
            self._ptz_player
            is player
        ):
            self._ptz_player = (
                None
            )

        player.deleteLater()

        if (
            self._panoramic_player is None
            and self._ptz_player is None
        ):
            self._desconectar_button.setEnabled(
                False
            )

            self._conectar_button.setEnabled(
                self._panoramic_camera is not None
                and self._ptz_camera is not None
            )

        self.statusBar().showMessage(
            f" {view_name}: "
            "recepción RTSP finalizada"
        )

    def _abrir_configuracion(
        self,
    ) -> None:
        """Abrir la configuración de cámaras conocidas por MeteoCam."""
        dialog = CameraConfigDialog(
            self
        )

        try:
            dialog.exec()

        finally:
            dialog.deleteLater()

    def _abrir_diagnostico(
        self,
    ) -> None:
        """Abrir el diagnóstico usando la vista panorámica como referencia."""
        camera = (
            self._panoramic_camera
            or self._ptz_camera
        )

        if camera is None:
            self.statusBar().showMessage(
                " No hay ninguna vista "
                "de Los Llanos configurada."
            )

            return

        dialog = DiagnosticsDialog(
            self,
            camera=camera,
        )

        try:
            dialog.exec()

        finally:
            dialog.deleteLater()

    def _crear_barra_estado(
        self,
    ) -> None:
        """Crear la barra de estado inferior."""
        status_bar = QStatusBar(
            self
        )

        status_bar.setObjectName(
            "win31StatusBar"
        )

        status_bar.showMessage(
            " MeteoCam preparado"
        )

        self.setStatusBar(
            status_bar
        )

    def _detectar_bordes(
        self,
        posicion: QPoint,
    ) -> int:
        """Detectar lados o esquinas disponibles para redimensionar."""
        if self.isMaximized():
            return self.EDGE_NONE

        edges = (
            self.EDGE_NONE
        )

        margin = (
            self.RESIZE_MARGIN
        )

        if posicion.x() <= margin:
            edges |= (
                self.EDGE_LEFT
            )

        elif (
            posicion.x()
            >= self.width() - margin
        ):
            edges |= (
                self.EDGE_RIGHT
            )

        if posicion.y() <= margin:
            edges |= (
                self.EDGE_TOP
            )

        elif (
            posicion.y()
            >= self.height() - margin
        ):
            edges |= (
                self.EDGE_BOTTOM
            )

        return edges

    def _actualizar_cursor_redimensionado(
        self,
        edges: int,
    ) -> None:
        """Mostrar el cursor apropiado según el borde señalado."""
        if edges in (
            self.EDGE_LEFT
            | self.EDGE_TOP,
            self.EDGE_RIGHT
            | self.EDGE_BOTTOM,
        ):
            self.setCursor(
                Qt.CursorShape.SizeFDiagCursor
            )

            return

        if edges in (
            self.EDGE_RIGHT
            | self.EDGE_TOP,
            self.EDGE_LEFT
            | self.EDGE_BOTTOM,
        ):
            self.setCursor(
                Qt.CursorShape.SizeBDiagCursor
            )

            return

        if edges in (
            self.EDGE_LEFT,
            self.EDGE_RIGHT,
        ):
            self.setCursor(
                Qt.CursorShape.SizeHorCursor
            )

            return

        if edges in (
            self.EDGE_TOP,
            self.EDGE_BOTTOM,
        ):
            self.setCursor(
                Qt.CursorShape.SizeVerCursor
            )

            return

        self.unsetCursor()

    def mousePressEvent(
        self,
        event: QMouseEvent,
    ) -> None:
        """Iniciar manualmente el redimensionado de la ventana."""
        if (
            event.button()
            == Qt.MouseButton.LeftButton
        ):
            edges = self._detectar_bordes(
                event.position().toPoint()
            )

            if (
                edges
                != self.EDGE_NONE
            ):
                self._resize_edges = (
                    edges
                )

                self._resize_start_position = (
                    event.globalPosition().toPoint()
                )

                self._resize_start_geometry = (
                    self.geometry()
                )

                event.accept()
                return

        super().mousePressEvent(
            event
        )

    def mouseMoveEvent(
        self,
        event: QMouseEvent,
    ) -> None:
        """Redimensionar la ventana o actualizar el cursor del borde."""
        if (
            self._resize_edges
            != self.EDGE_NONE
            and event.buttons()
            & Qt.MouseButton.LeftButton
        ):
            current_position = (
                event.globalPosition().toPoint()
            )

            delta_x = (
                current_position.x()
                - self._resize_start_position.x()
            )

            delta_y = (
                current_position.y()
                - self._resize_start_position.y()
            )

            geometry = QRect(
                self._resize_start_geometry
            )

            minimum_width = (
                self.minimumWidth()
            )

            minimum_height = (
                self.minimumHeight()
            )

            if (
                self._resize_edges
                & self.EDGE_LEFT
            ):
                new_left = (
                    self._resize_start_geometry.left()
                    + delta_x
                )

                maximum_left = (
                    self._resize_start_geometry.right()
                    - minimum_width
                    + 1
                )

                geometry.setLeft(
                    min(
                        new_left,
                        maximum_left,
                    )
                )

            if (
                self._resize_edges
                & self.EDGE_RIGHT
            ):
                new_right = (
                    self._resize_start_geometry.right()
                    + delta_x
                )

                minimum_right = (
                    self._resize_start_geometry.left()
                    + minimum_width
                    - 1
                )

                geometry.setRight(
                    max(
                        new_right,
                        minimum_right,
                    )
                )

            if (
                self._resize_edges
                & self.EDGE_TOP
            ):
                new_top = (
                    self._resize_start_geometry.top()
                    + delta_y
                )

                maximum_top = (
                    self._resize_start_geometry.bottom()
                    - minimum_height
                    + 1
                )

                geometry.setTop(
                    min(
                        new_top,
                        maximum_top,
                    )
                )

            if (
                self._resize_edges
                & self.EDGE_BOTTOM
            ):
                new_bottom = (
                    self._resize_start_geometry.bottom()
                    + delta_y
                )

                minimum_bottom = (
                    self._resize_start_geometry.top()
                    + minimum_height
                    - 1
                )

                geometry.setBottom(
                    max(
                        new_bottom,
                        minimum_bottom,
                    )
                )

            self.setGeometry(
                geometry
            )

            event.accept()
            return

        edges = self._detectar_bordes(
            event.position().toPoint()
        )

        self._actualizar_cursor_redimensionado(
            edges
        )

        super().mouseMoveEvent(
            event
        )

    def mouseReleaseEvent(
        self,
        event: QMouseEvent,
    ) -> None:
        """Finalizar el redimensionado manual."""
        if (
            event.button()
            == Qt.MouseButton.LeftButton
            and self._resize_edges
            != self.EDGE_NONE
        ):
            self._resize_edges = (
                self.EDGE_NONE
            )

            edges = self._detectar_bordes(
                event.position().toPoint()
            )

            self._actualizar_cursor_redimensionado(
                edges
            )

            event.accept()
            return

        super().mouseReleaseEvent(
            event
        )

    def resizeEvent(
        self,
        event,
    ) -> None:
        """Mantener el dashboard adaptado al tamaño de la ventana."""
        super().resizeEvent(
            event
        )

    def closeEvent(
        self,
        event,
    ) -> None:
        """Cerrar ambos receptores RTSP antes de destruir la ventana."""
        self._detener_todos_los_publicadores()
        self._detener_todos_los_videos()

        self._session_username = None
        self._session_password = None

        super().closeEvent(
            event
        )

    def leaveEvent(
        self,
        event,
    ) -> None:
        """Restaurar el cursor al abandonar la ventana."""
        if (
            self._resize_edges
            == self.EDGE_NONE
        ):
            self.unsetCursor()

        super().leaveEvent(
            event
        )


# Fin de fichero
# Fin archivo: src/meteocam/main_window.py