"""Envío de un stream RTSP H.264 hacia un servidor SRT."""

from __future__ import annotations

from fractions import Fraction
from urllib.parse import quote

import av
from PySide6.QtCore import QThread, Signal

from meteocam.cameras.diagnostics import Credentials


class SrtPublisher(QThread):
    """Enviar una vista RTSP al VPS mediante SRT.

    La cámara se abre mediante RTSP sobre TCP.

    El vídeo H.264 se remultiplexa como MPEG-TS y se envía mediante
    SRT al servidor remoto sin decodificar ni recodificar.

    La conexión SRT se inicia siempre desde MeteoCam hacia el VPS.
    """

    DEFAULT_FRAME_RATE = Fraction(20, 1)
    DEFAULT_TIME_BASE = Fraction(1, 90000)

    status_changed = Signal(str)
    publication_started = Signal(str)
    publication_stopped = Signal()
    publication_error = Signal(str)

    def __init__(
        self,
        target: str,
        path: str,
        credentials: Credentials,
        srt_host: str,
        srt_port: int,
        rtsp_port: int = 554,
        srt_latency_us: int = 2_000_000,
        parent=None,
    ) -> None:
        """Preparar una sesión RTSP -> SRT."""
        super().__init__(parent)

        self._target = target
        self._path = path
        self._credentials = credentials
        self._rtsp_port = rtsp_port

        self._srt_host = srt_host
        self._srt_port = srt_port
        self._srt_latency_us = srt_latency_us

        self._stop_requested = False

        self._time_base = self.DEFAULT_TIME_BASE
        self._frame_rate = self.DEFAULT_FRAME_RATE
        self._frame_duration = 4500

        self._next_dts = 0
        self._last_dts: int | None = None

    @property
    def destination(self) -> str:
        """Descripción pública del destino sin información sensible."""
        return (
            f"{self._srt_host}:"
            f"{self._srt_port}"
        )

    def stop(self) -> None:
        """Solicitar la detención del envío."""
        self._stop_requested = True
        self.requestInterruption()

    def run(self) -> None:
        """Recibir H.264 por RTSP y enviarlo al VPS mediante SRT."""
        input_container = None
        output_container = None

        self._stop_requested = False
        self._last_dts = None
        self._next_dts = 0

        try:
            self.status_changed.emit(
                "CONECTANDO CÁMARA"
            )

            rtsp_url = self._build_rtsp_url()

            input_container = av.open(
                rtsp_url,
                mode="r",
                options={
                    "rtsp_transport": "tcp",
                    "stimeout": "5000000",
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

            if video_stream.codec_context.name != "h264":
                raise RuntimeError(
                    "La publicación SRT requiere "
                    "un stream RTSP H.264."
                )

            self._preparar_temporizacion(
                video_stream
            )

            self.status_changed.emit(
                "CONECTANDO VPS"
            )

            srt_url = self._build_srt_url()

            output_container = av.open(
                srt_url,
                mode="w",
                format="mpegts",
            )

            output_stream = (
                output_container.add_stream_from_template(
                    video_stream
                )
            )

            self.status_changed.emit(
                "ESPERANDO VÍDEO"
            )

            started_emitted = False
            waiting_for_keyframe = True

            for packet in input_container.demux(
                video_stream
            ):
                if (
                    self._stop_requested
                    or self.isInterruptionRequested()
                ):
                    break

                if packet.size == 0:
                    continue

                if packet.is_corrupt:
                    continue

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
                output_packet.stream = output_stream

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
                        "No se pudo enviar "
                        "el stream al VPS."
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
                        "la publicación SRT."
                    )

                self.status_changed.emit(
                    "ERROR"
                )
                self.publication_error.emit(
                    message
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

            self.publication_stopped.emit()

    def _preparar_temporizacion(
        self,
        video_stream: av.video.stream.VideoStream,
    ) -> None:
        """Obtener temporización utilizable para la remultiplexación."""
        stream_time_base = video_stream.time_base

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
        """Completar las marcas temporales que falten en RTSP."""
        packet_time_base = packet.time_base

        if packet_time_base is None:
            time_base = self._time_base
        else:
            time_base = Fraction(
                packet_time_base.numerator,
                packet_time_base.denominator,
            )

        duration = packet.duration

        if duration is None or duration <= 0:
            if time_base == self._time_base:
                duration = self._frame_duration
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
                    round(duration_fraction),
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
        """Construir la URL RTSP sin mostrar las credenciales."""
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

    def _build_srt_url(self) -> str:
        """Construir el destino SRT en modo caller."""
        return (
            f"srt://{self._srt_host}:"
            f"{self._srt_port}"
            "?mode=caller"
            f"&latency={self._srt_latency_us}"
        )


# Fin de fichero
# Fin archivo: src/meteocam/cameras/srt_publisher.py