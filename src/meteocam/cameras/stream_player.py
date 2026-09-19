"""Recepción y decodificación de vídeo RTSP para MeteoCam."""

from __future__ import annotations

from threading import Event
from urllib.parse import quote

import av
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

from meteocam.cameras.diagnostics import CameraTarget, Credentials


class StreamPlayer(QThread):
    """Decodificar un stream RTSP en segundo plano.

    Las credenciales solo se mantienen en memoria mientras la reproducción
    está activa. No se incluyen en mensajes, trazas ni excepciones mostradas.
    """

    frame_received = Signal(QImage)
    status_changed = Signal(str, str)

    def __init__(
        self,
        target: CameraTarget,
        path: str,
        credentials: Credentials,
        parent=None,
    ) -> None:
        """Preparar el reproductor sin iniciar aún la conexión."""
        super().__init__(parent)

        self._target = target
        self._path = path
        self._credentials = credentials
        self._stop_requested = Event()

    def stop(self) -> None:
        """Solicitar la detención del reproductor."""
        self._stop_requested.set()

    def run(self) -> None:
        """Abrir RTSP, decodificar vídeo y emitir fotogramas Qt."""
        container = None
        received_first_frame = False

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

            for frame in container.decode(stream):
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

            if container is not None:
                try:
                    container.close()
                except av.FFmpegError:
                    pass

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


# Fin archivo: src/meteocam/cameras/stream_player.py