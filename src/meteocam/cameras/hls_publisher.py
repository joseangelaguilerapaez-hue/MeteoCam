"""Publicación HLS de vídeo H.264 sin decodificar ni recodificar."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path
from tempfile import TemporaryDirectory

import av


class HlsPublisher:
    """Empaquetar en HLS los paquetes H.264 de una conexión existente.

    Debe crearse, utilizarse y cerrarse desde el mismo hilo receptor.

    No conecta con la cámara ni recibe sus credenciales. Los archivos
    pertenecen únicamente a esta sesión y se eliminan al cerrarla.

    Algunos streams RTSP de cámaras IP no proporcionan PTS, DTS o
    time_base en todos los paquetes. En esos casos MeteoCam completa
    las marcas temporales necesarias para poder remultiplexar H.264
    como HLS sin decodificar ni recodificar el vídeo.
    """

    DEFAULT_FRAME_RATE = Fraction(20, 1)
    DEFAULT_TIME_BASE = Fraction(1, 90000)

    def __init__(
        self,
        source_stream: av.video.stream.VideoStream,
    ) -> None:
        """Preparar una salida HLS a partir del stream de entrada."""
        if source_stream.codec_context.name != "h264":
            raise ValueError(
                "La publicación web requiere un stream H.264."
            )

        self._source_stream = source_stream

        self._temporary_directory = TemporaryDirectory(
            prefix="meteocam-hls-"
        )
        self._directory = Path(self._temporary_directory.name)

        self._output = None
        self._output_stream = None

        self._started = False
        self._closed = False

        self._time_base = self._obtener_time_base(source_stream)
        self._frame_rate = self._obtener_frame_rate(source_stream)
        self._frame_duration = self._calcular_duracion_fotograma()

        self._next_dts = 0
        self._last_dts: int | None = None
        self._last_pts: int | None = None

        try:
            self._output = av.open(
                str(self.playlist_path),
                mode="w",
                format="hls",
                options={
                    "hls_time": "2",
                    "hls_list_size": "5",
                    "hls_delete_threshold": "2",
                    "hls_flags": "delete_segments+temp_file",
                    "hls_segment_filename": str(
                        self._directory / "segment_%09d.ts"
                    ),
                },
            )

            self._output_stream = (
                self._output.add_stream_from_template(source_stream)
            )

        except Exception:
            try:
                self.close()
            except (av.FFmpegError, OSError):
                pass
            raise

    @property
    def directory(self) -> Path:
        """Carpeta privada de esta sesión HLS."""
        return self._directory

    @property
    def playlist_path(self) -> Path:
        """Ruta de la lista HLS."""
        return self._directory / "index.m3u8"

    @staticmethod
    def _obtener_time_base(
        source_stream: av.video.stream.VideoStream,
    ) -> Fraction:
        """Obtener una base temporal válida para el stream."""
        time_base = source_stream.time_base

        if time_base is not None:
            return Fraction(
                time_base.numerator,
                time_base.denominator,
            )

        codec_time_base = source_stream.codec_context.time_base

        if codec_time_base is not None:
            return Fraction(
                codec_time_base.numerator,
                codec_time_base.denominator,
            )

        return HlsPublisher.DEFAULT_TIME_BASE

    @staticmethod
    def _obtener_frame_rate(
        source_stream: av.video.stream.VideoStream,
    ) -> Fraction:
        """Obtener la frecuencia de imagen anunciada por la cámara."""
        candidates = (
            source_stream.average_rate,
            source_stream.base_rate,
            source_stream.guessed_rate,
        )

        for candidate in candidates:
            if candidate is None:
                continue

            rate = Fraction(
                candidate.numerator,
                candidate.denominator,
            )

            if rate > 0:
                return rate

        return HlsPublisher.DEFAULT_FRAME_RATE

    def _calcular_duracion_fotograma(self) -> int:
        """Calcular la duración de un fotograma en unidades del time_base."""
        duration = Fraction(1, 1) / (
            self._frame_rate * self._time_base
        )

        return max(1, round(duration))

    def _resolver_marcas_temporales(
        self,
        packet: av.Packet,
    ) -> tuple[int, int, int, Fraction]:
        """Completar PTS, DTS, duración y time_base cuando falten."""
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
                duration_fraction = Fraction(1, 1) / (
                    self._frame_rate * time_base
                )
                duration = max(1, round(duration_fraction))

        dts = packet.dts
        pts = packet.pts

        if dts is None:
            if pts is not None:
                dts = pts
            elif self._last_dts is not None:
                dts = self._last_dts + duration
            else:
                dts = self._next_dts

        if pts is None:
            pts = dts

        if self._last_dts is not None and dts <= self._last_dts:
            dts = self._last_dts + duration

            if pts < dts:
                pts = dts

        self._last_dts = dts
        self._last_pts = pts
        self._next_dts = dts + duration

        return pts, dts, duration, time_base

    def write_packet(self, packet: av.Packet) -> bool:
        """Añadir un paquete H.264 al HLS sin recodificar.

        Devuelve True si el paquete se entrega al empaquetador.
        Devuelve False para paquetes vacíos o mientras se espera
        el primer fotograma clave.
        """
        if self._closed:
            raise RuntimeError(
                "El publicador HLS ya está cerrado."
            )

        if packet.size == 0:
            return False

        if packet.is_corrupt:
            raise ValueError(
                "Se ha recibido un paquete de vídeo dañado."
            )

        if not self._started and not packet.is_keyframe:
            return False

        pts, dts, duration, time_base = (
            self._resolver_marcas_temporales(packet)
        )

        output_packet = av.Packet(bytes(packet))

        output_packet.pts = pts
        output_packet.dts = dts
        output_packet.duration = duration
        output_packet.time_base = time_base
        output_packet.is_keyframe = packet.is_keyframe
        output_packet.stream = self._output_stream

        self._output.mux(output_packet)

        self._started = True

        return True

    def close(self) -> None:
        """Cerrar la salida y eliminar los archivos temporales."""
        if self._closed:
            return

        self._closed = True

        output = self._output

        self._output = None
        self._output_stream = None

        try:
            if output is not None:
                output.close()
        finally:
            self._temporary_directory.cleanup()


# Fin de fichero
# Fin archivo: src/meteocam/cameras/hls_publisher.py