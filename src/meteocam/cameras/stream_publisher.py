"""Publicación independiente de un stream RTSP como HLS."""

from __future__ import annotations

from urllib.parse import quote

import av
from PySide6.QtCore import QThread, Signal

from meteocam.cameras.diagnostics import Credentials
from meteocam.cameras.hls_publisher import HlsPublisher
from meteocam.cameras.hls_server import HlsServer


class StreamPublisher(QThread):
    """Publicar una vista RTSP como HLS sin decodificarla.

    Cada instancia mantiene su propia conexión RTSP, su propio
    empaquetador HLS y su propio servidor HTTP.

    El publicador es completamente independiente del StreamPlayer
    utilizado para mostrar vídeo en la interfaz.
    """

    status_changed = Signal(str)
    publication_started = Signal(str)
    publication_stopped = Signal()
    publication_error = Signal(str)

    def __init__(
        self,
        target: str,
        path: str,
        credentials: Credentials,
        rtsp_port: int = 554,
        hls_host: str = "127.0.0.1",
        hls_port: int = 0,
        parent=None,
    ) -> None:
        """Preparar una sesión independiente de publicación."""
        super().__init__(parent)

        self._target = target
        self._path = path
        self._credentials = credentials
        self._rtsp_port = rtsp_port

        self._hls_host = hls_host
        self._hls_port = hls_port

        self._stop_requested = False

    def stop(self) -> None:
        """Solicitar la detención de la publicación."""
        self._stop_requested = True
        self.requestInterruption()

    def run(self) -> None:
        """Mantener la conexión RTSP y publicar sus paquetes H.264."""
        container = None
        publisher = None
        server = None

        self._stop_requested = False

        try:
            self.status_changed.emit(
                "CONECTANDO"
            )

            url = self._build_url()

            container = av.open(
                url,
                mode="r",
                options={
                    "rtsp_transport": "tcp",
                    "stimeout": "5000000",
                },
            )

            video_stream = next(
                (
                    stream
                    for stream in container.streams
                    if stream.type == "video"
                ),
                None,
            )

            if video_stream is None:
                raise RuntimeError(
                    "La conexión RTSP no contiene vídeo."
                )

            if video_stream.codec_context.name != "h264":
                raise RuntimeError(
                    "La publicación web requiere "
                    "un stream RTSP H.264."
                )

            publisher = HlsPublisher(
                video_stream
            )

            server = HlsServer(
                directory=publisher.directory,
                host=self._hls_host,
                port=self._hls_port,
            )
            server.start()

            self.status_changed.emit(
                "ESPERANDO VÍDEO"
            )

            started_emitted = False

            for packet in container.demux(
                video_stream
            ):
                if (
                    self._stop_requested
                    or self.isInterruptionRequested()
                ):
                    break

                written = publisher.write_packet(
                    packet
                )

                if (
                    written
                    and not started_emitted
                ):
                    started_emitted = True

                    self.status_changed.emit(
                        "PUBLICANDO"
                    )
                    self.publication_started.emit(
                        server.playlist_url
                    )

        except (
            av.FFmpegError,
            OSError,
            RuntimeError,
            ValueError,
            StopIteration,
        ) as exc:
            if not (
                self._stop_requested
                or self.isInterruptionRequested()
            ):
                message = str(exc).strip()

                if not message:
                    message = (
                        "No se pudo publicar "
                        "el stream RTSP."
                    )

                self.status_changed.emit(
                    "ERROR"
                )
                self.publication_error.emit(
                    message
                )

        except Exception as exc:
            if not (
                self._stop_requested
                or self.isInterruptionRequested()
            ):
                message = str(exc).strip()

                if not message:
                    message = (
                        "Error inesperado durante "
                        "la publicación."
                    )

                self.status_changed.emit(
                    "ERROR"
                )
                self.publication_error.emit(
                    message
                )

        finally:
            if server is not None:
                try:
                    server.stop()
                except OSError:
                    pass

            if publisher is not None:
                try:
                    publisher.close()
                except (
                    av.FFmpegError,
                    OSError,
                ):
                    pass

            if container is not None:
                try:
                    container.close()
                except (
                    av.FFmpegError,
                    OSError,
                ):
                    pass

            self.publication_stopped.emit()

    def _build_url(self) -> str:
        """Construir la URL RTSP sin exponer credenciales en logs."""
        username = quote(
            self._credentials.username,
            safe="",
        )
        password = quote(
            self._credentials.password,
            safe="",
        )

        path = self._path

        if not path.startswith("/"):
            path = f"/{path}"

        return (
            f"rtsp://{username}:{password}"
            f"@{self._target}:{self._rtsp_port}"
            f"{path}"
        )


# Fin de fichero
# Fin archivo: src/meteocam/cameras/stream_publisher.py