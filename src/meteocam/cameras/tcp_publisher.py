"""Publicación resiliente de vídeo RTSP hacia el VPS mediante TCP."""

from __future__ import annotations

import time
from fractions import Fraction
from urllib.parse import quote

import av
from PySide6.QtCore import QThread, Signal

from meteocam.cameras.diagnostics import Credentials


class TcpPublisher(QThread):
    """Enviar continuamente una vista RTSP al VPS mediante TCP.

    La cámara se recibe mediante RTSP sobre TCP.

    El vídeo H.264 se remultiplexa como MPEG-TS y se envía al VPS
    mediante una conexión TCP saliente, sin decodificar ni recodificar.

    Si desaparece la entrada RTSP, se interrumpe la salida TCP o se
    supera el tiempo máximo sin actividad de red, la sesión completa
    se cierra y se intenta reconstruir automáticamente.
    """

    DEFAULT_FRAME_RATE = Fraction(20, 1)
    DEFAULT_TIME_BASE = Fraction(1, 90000)

    IO_TIMEOUT_SECONDS = 15
    IO_TIMEOUT_US = IO_TIMEOUT_SECONDS * 1_000_000

    RECONNECT_DELAY_SECONDS = 5

    status_changed = Signal(str)
    publication_started = Signal(str)
    publication_stopped = Signal()
    publication_error = Signal(str)
    reconnecting = Signal(str)

    def __init__(
        self,
        target: str,
        path: str,
        credentials: Credentials,
        tcp_host: str,
        tcp_port: int,
        rtsp_port: int = 554,
        parent=None,
    ) -> None:
        """Preparar una publicación RTSP -> MPEG-TS -> TCP."""
        super().__init__(parent)

        self._target = target
        self._path = path
        self._credentials = credentials
        self._rtsp_port = rtsp_port

        self._tcp_host = tcp_host
        self._tcp_port = tcp_port

        self._stop_requested = False

        self._time_base = self.DEFAULT_TIME_BASE
        self._frame_rate = self.DEFAULT_FRAME_RATE
        self._frame_duration = 4500

        self._next_dts = 0
        self._last_dts: int | None = None

    @property
    def destination(self) -> str:
        """Descripción pública del destino remoto."""
        return (
            f"{self._tcp_host}:"
            f"{self._tcp_port}"
        )

    def stop(self) -> None:
        """Solicitar la detención definitiva del publicador."""
        self._stop_requested = True
        self.requestInterruption()

    def run(self) -> None:
        """Mantener la publicación activa con reconexión automática."""
        try:
            while not self._debe_detenerse():
                error_message = ""

                try:
                    self._ejecutar_sesion()

                    if self._debe_detenerse():
                        break

                    error_message = (
                        "La sesión de publicación "
                        "ha finalizado inesperadamente."
                    )

                except (
                    av.FFmpegError,
                    OSError,
                    RuntimeError,
                    ValueError,
                    StopIteration,
                ) as exc:
                    if self._debe_detenerse():
                        break

                    error_message = str(exc).strip()

                    if not error_message:
                        error_message = (
                            "Se ha interrumpido "
                            "la publicación TCP."
                        )

                except Exception as exc:
                    if self._debe_detenerse():
                        break

                    error_message = str(exc).strip()

                    if not error_message:
                        error_message = (
                            "Error inesperado durante "
                            "la publicación TCP."
                        )

                if self._debe_detenerse():
                    break

                self.status_changed.emit(
                    "REINTENTANDO"
                )

                self.publication_error.emit(
                    error_message
                )

                self.reconnecting.emit(
                    (
                        "Reintentando conexión "
                        f"en {self.RECONNECT_DELAY_SECONDS} s"
                    )
                )

                if not self._esperar_reconexion():
                    break

        finally:
            self.publication_stopped.emit()

    def _ejecutar_sesion(self) -> None:
        """Ejecutar una sesión completa desde la cámara hasta el VPS."""
        input_container = None
        output_container = None

        self._last_dts = None
        self._next_dts = 0

        try:
            if self._debe_detenerse():
                return

            self.status_changed.emit(
                "CONECTANDO CÁMARA"
            )

            rtsp_url = self._build_rtsp_url()

            input_container = av.open(
                rtsp_url,
                mode="r",
                options={
                    "rtsp_transport": "tcp",
                    "timeout": str(
                        self.IO_TIMEOUT_US
                    ),
                    "rw_timeout": str(
                        self.IO_TIMEOUT_US
                    ),
                },
            )

            video_stream = next(
                (
                    stream
                    for stream in input_container.streams
                    if stream.type == "video"
                ),
                None,
            )

            if video_stream is None:
                raise RuntimeError(
                    "La conexión RTSP no contiene vídeo."
                )

            if (
                video_stream.codec_context.name
                != "h264"
            ):
                raise RuntimeError(
                    "La publicación TCP requiere "
                    "un stream RTSP H.264."
                )

            self._preparar_temporizacion(
                video_stream
            )

            if self._debe_detenerse():
                return

            self.status_changed.emit(
                "CONECTANDO VPS"
            )

            output_container = av.open(
                self._build_tcp_url(),
                mode="w",
                format="mpegts",
                options={
                    "flush_packets": "1",
                    "rw_timeout": str(
                        self.IO_TIMEOUT_US
                    ),
                },
            )

            output_stream = (
                output_container.add_stream_from_template(
                    video_stream
                )
            )

            self.status_changed.emit(
                "ESPERANDO VÍDEO"
            )

            waiting_for_keyframe = True
            started_emitted = False

            last_activity = time.monotonic()

            for packet in input_container.demux(
                video_stream
            ):
                if self._debe_detenerse():
                    break

                now = time.monotonic()

                if (
                    now - last_activity
                    > self.IO_TIMEOUT_SECONDS
                ):
                    raise RuntimeError(
                        "No se reciben datos de vídeo "
                        "desde la cámara."
                    )

                if packet.size == 0:
                    continue

                if packet.is_corrupt:
                    continue

                last_activity = now

                if (
                    waiting_for_keyframe
                    and not packet.is_keyframe
                ):
                    continue

                waiting_for_keyframe = False

                (
                    pts,
                    dts,
                    duration,
                    time_base,
                ) = self._resolver_marcas_temporales(
                    packet
                )

                output_packet = av.Packet(
                    bytes(packet)
                )

                output_packet.pts = pts
                output_packet.dts = dts
                output_packet.duration = duration
                output_packet.time_base = time_base
                output_packet.is_keyframe = (
                    packet.is_keyframe
                )
                output_packet.stream = (
                    output_stream
                )

                output_container.mux(
                    output_packet
                )

                if not started_emitted:
                    started_emitted = True

                    self.status_changed.emit(
                        "PUBLICANDO"
                    )

                    self.publication_started.emit(
                        self.destination
                    )

            if not self._debe_detenerse():
                raise RuntimeError(
                    "La recepción RTSP "
                    "ha finalizado."
                )

        finally:
            if output_container is not None:
                try:
                    output_container.close()
                except (
                    av.FFmpegError,
                    OSError,
                ):
                    pass

            if input_container is not None:
                try:
                    input_container.close()
                except (
                    av.FFmpegError,
                    OSError,
                ):
                    pass

    def _esperar_reconexion(self) -> bool:
        """Esperar antes del siguiente intento sin impedir detener el hilo."""
        steps = (
            self.RECONNECT_DELAY_SECONDS
            * 10
        )

        for _ in range(steps):
            if self._debe_detenerse():
                return False

            time.sleep(0.1)

        return not self._debe_detenerse()

    def _debe_detenerse(self) -> bool:
        """Indicar si el publicador debe finalizar."""
        return (
            self._stop_requested
            or self.isInterruptionRequested()
        )

    def _preparar_temporizacion(
        self,
        video_stream: av.video.stream.VideoStream,
    ) -> None:
        """Obtener temporización utilizable para la remultiplexación."""
        stream_time_base = (
            video_stream.time_base
        )

        if stream_time_base is not None:
            self._time_base = Fraction(
                stream_time_base.numerator,
                stream_time_base.denominator,
            )

        else:
            codec_time_base = (
                video_stream.codec_context.time_base
            )

            if codec_time_base is not None:
                self._time_base = Fraction(
                    codec_time_base.numerator,
                    codec_time_base.denominator,
                )

            else:
                self._time_base = (
                    self.DEFAULT_TIME_BASE
                )

        candidates = (
            video_stream.average_rate,
            video_stream.base_rate,
            video_stream.guessed_rate,
        )

        self._frame_rate = (
            self.DEFAULT_FRAME_RATE
        )

        for candidate in candidates:
            if candidate is None:
                continue

            rate = Fraction(
                candidate.numerator,
                candidate.denominator,
            )

            if rate > 0:
                self._frame_rate = rate
                break

        duration = Fraction(1, 1) / (
            self._frame_rate
            * self._time_base
        )

        self._frame_duration = max(
            1,
            round(duration),
        )

    def _resolver_marcas_temporales(
        self,
        packet: av.Packet,
    ) -> tuple[int, int, int, Fraction]:
        """Completar PTS, DTS, duración y time_base cuando falten."""
        packet_time_base = (
            packet.time_base
        )

        if packet_time_base is None:
            time_base = self._time_base

        else:
            time_base = Fraction(
                packet_time_base.numerator,
                packet_time_base.denominator,
            )

        duration = packet.duration

        if (
            duration is None
            or duration <= 0
        ):
            if (
                time_base
                == self._time_base
            ):
                duration = (
                    self._frame_duration
                )

            else:
                duration_fraction = (
                    Fraction(1, 1)
                    / (
                        self._frame_rate
                        * time_base
                    )
                )

                duration = max(
                    1,
                    round(
                        duration_fraction
                    ),
                )

        dts = packet.dts
        pts = packet.pts

        if dts is None:
            if pts is not None:
                dts = pts

            elif self._last_dts is not None:
                dts = (
                    self._last_dts
                    + duration
                )

            else:
                dts = self._next_dts

        if pts is None:
            pts = dts

        if (
            self._last_dts is not None
            and dts <= self._last_dts
        ):
            dts = (
                self._last_dts
                + duration
            )

            if pts < dts:
                pts = dts

        self._last_dts = dts
        self._next_dts = (
            dts + duration
        )

        return (
            pts,
            dts,
            duration,
            time_base,
        )

    def _build_rtsp_url(self) -> str:
        """Construir la URL RTSP sin mostrar credenciales."""
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

    def _build_tcp_url(self) -> str:
        """Construir el destino TCP hacia el VPS."""
        return (
            f"tcp://{self._tcp_host}:"
            f"{self._tcp_port}"
        )


# Fin de fichero
# Fin archivo: src/meteocam/cameras/tcp_publisher.py