"""Recepción, decodificación y publicación de vídeo RTSP para MeteoCam."""

from __future__ import annotations

from threading import Event
from urllib.parse import quote

import av
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

from meteocam.cameras.diagnostics import CameraTarget, Credentials
from meteocam.cameras.hls_publisher import HlsPublisher
from meteocam.cameras.hls_server import HlsServer


class StreamPlayer(QThread):
    """Recibir y decodificar un stream RTSP en segundo plano.

    El mismo flujo RTSP puede utilizarse simultáneamente para:

    - mostrar vídeo en la interfaz local;
    - publicar vídeo HLS para consumo HTTP.

    La publicación HLS reutiliza los paquetes H.264 originales y no
    recodifica el vídeo.

    Las credenciales solo se mantienen en memoria mientras la reproducción
    está activa. No se incluyen en mensajes, trazas ni excepciones mostradas.
    """

    frame_received = Signal(QImage)
    status_changed = Signal(str, str)

    hls_started = Signal(str)
    hls_stopped = Signal()

    def __init__(
        self,
        target: CameraTarget,
        path: str,
        credentials: Credentials,
        parent=None,
        publish_hls: bool = False,
        hls_host: str = "127.0.0.1",
        hls_port: int = 0,
    ) -> None:
        """Preparar el reproductor sin iniciar aún la conexión."""
        super().__init__(parent)

        self._target = target
        self._path = path
        self._credentials = credentials

        self._publish_hls = publish_hls
        self._hls_host = hls_host
        self._hls_port = hls_port

        self._stop_requested = Event()

        self._hls_publisher: HlsPublisher | None = None
        self._hls_server: HlsServer | None = None

    def stop(self) -> None:
        """Solicitar la detención del reproductor."""
        self._stop_requested.set()

    def run(self) -> None:
        """Abrir RTSP, publicar HLS y decodificar vídeo local."""
        container = None
        received_first_frame = False
        hls_available = False

        try:
            url = self._build_url()

            container = av.open(
                url,
                mode="r",
                options={
                    "rtsp_transport": "tcp",
                    "timeout": "5000000",
                },
            )

            self.status_changed.emit(
                "CAM-STREAM-200",
                "Conexión RTSP abierta; esperando imágenes.",
            )

            stream = next(
                (
                    candidate
                    for candidate in container.streams
                    if candidate.type == "video"
                ),
                None,
            )

            if stream is None:
                self.status_changed.emit(
                    "CAM-STREAM-422",
                    "El stream abierto no contiene vídeo.",
                )
                return

            stream.thread_type = "AUTO"

            if self._publish_hls:
                hls_available = self._prepare_hls(stream)

            for packet in container.demux(stream):
                if self._stop_requested.is_set():
                    return

                if packet.size == 0:
                    continue

                if hls_available:
                    try:
                        self._hls_publisher.write_packet(packet)

                        if (
                            self._hls_server is None
                            and self._hls_publisher.playlist_path.is_file()
                        ):
                            self._start_hls_server()

                    except (
                        av.FFmpegError,
                        OSError,
                        RuntimeError,
                        ValueError,
                    ):
                        self._disable_hls()

                        self.status_changed.emit(
                            "CAM-STREAM-HLS-500",
                            (
                                "La publicación web se ha detenido, "
                                "pero el vídeo local continúa."
                            ),
                        )

                        hls_available = False

                try:
                    frames = packet.decode()
                except av.FFmpegError:
                    continue

                for frame in frames:
                    if self._stop_requested.is_set():
                        return

                    image = self._to_qimage(frame)

                    if image.isNull():
                        continue

                    if not received_first_frame:
                        received_first_frame = True

                        self.status_changed.emit(
                            "CAM-STREAM-201",
                            "Vídeo recibido correctamente.",
                        )

                    self.frame_received.emit(image)

        except (av.FFmpegError, OSError, ValueError):
            self.status_changed.emit(
                "CAM-STREAM-500",
                "No se pudo abrir o decodificar el vídeo RTSP.",
            )

        finally:
            self._credentials = None

            self._disable_hls()

            if container is not None:
                try:
                    container.close()
                except av.FFmpegError:
                    pass

    def _prepare_hls(self, stream) -> bool:
        """Preparar el empaquetador HLS para el stream recibido."""
        try:
            self._hls_publisher = HlsPublisher(stream)

        except (av.FFmpegError, OSError, ValueError):
            self._hls_publisher = None

            self.status_changed.emit(
                "CAM-STREAM-HLS-422",
                (
                    "El stream no puede publicarse por HLS sin "
                    "recodificación; el vídeo local continúa."
                ),
            )

            return False

        self.status_changed.emit(
            "CAM-STREAM-HLS-100",
            "Publicación HLS preparada; esperando el primer segmento.",
        )

        return True

    def _start_hls_server(self) -> None:
        """Iniciar HTTP cuando ya exista una playlist HLS utilizable."""
        if self._hls_publisher is None:
            return

        if self._hls_server is not None:
            return

        server = HlsServer(
            self._hls_publisher.directory,
            host=self._hls_host,
            port=self._hls_port,
        )

        try:
            server.start()

        except (OSError, RuntimeError, ValueError):
            try:
                server.stop()
            except (OSError, RuntimeError):
                pass

            raise

        self._hls_server = server

        self.status_changed.emit(
            "CAM-STREAM-HLS-200",
            "Publicación HLS disponible.",
        )

        self.hls_started.emit(server.playlist_url)

    def _disable_hls(self) -> None:
        """Detener servidor y publicador HLS de forma segura."""
        had_hls = (
            self._hls_server is not None
            or self._hls_publisher is not None
        )

        server = self._hls_server
        publisher = self._hls_publisher

        self._hls_server = None
        self._hls_publisher = None

        if server is not None:
            try:
                server.stop()
            except (OSError, RuntimeError):
                pass

        if publisher is not None:
            try:
                publisher.close()
            except (av.FFmpegError, OSError):
                pass

        if had_hls:
            self.hls_stopped.emit()

    def _build_url(self) -> str:
        """Crear una URL temporal sin exponerla fuera de este objeto."""
        username = quote(self._credentials.username, safe="")
        password = quote(self._credentials.password, safe="")

        if ":" in self._target.host:
            host = f"[{self._target.host}]"
        else:
            host = self._target.host

        return (
            f"rtsp://{username}:{password}@"
            f"{host}:{self._target.port}{self._path}"
        )

    @staticmethod
    def _to_qimage(frame) -> QImage:
        """Convertir un fotograma PyAV a una copia independiente de QImage."""
        rgb_frame = frame.reformat(format="rgb24")
        plane = rgb_frame.planes[0]

        image = QImage(
            bytes(plane),
            rgb_frame.width,
            rgb_frame.height,
            plane.line_size,
            QImage.Format.Format_RGB888,
        )

        return image.copy()


# Fin de fichero
# Fin archivo: src/meteocam/cameras/stream_player.py