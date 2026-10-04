"""Pruebas del publicador HLS con vídeo sintético, sin cámara ni red."""

from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace

import av
import pytest

from meteocam.cameras.hls_publisher import HlsPublisher


@pytest.fixture(scope="module")
def synthetic_video(tmp_path_factory) -> Path:
    """Crear 32 segundos de vídeo pequeño para comprobar el flujo completo.

    La codificación se utiliza únicamente para fabricar el vídeo de prueba.
    El publicador debe reutilizar sus paquetes sin recodificarlos.
    """
    directory = tmp_path_factory.mktemp("synthetic-video")
    path = directory / "source.mp4"

    with av.open(str(path), mode="w") as output:
        stream = output.add_stream("libx264", rate=10)
        stream.width = 160
        stream.height = 96
        stream.pix_fmt = "yuv420p"
        stream.codec_context.gop_size = 10
        stream.codec_context.max_b_frames = 0
        stream.options = {
            "preset": "ultrafast",
            "tune": "zerolatency",
            "sc_threshold": "0",
        }

        for index in range(320):
            frame = av.VideoFrame(160, 96, format="yuv420p")
            frame.pts = index
            frame.time_base = Fraction(1, 10)

            # Imagen gris cuya luminosidad cambia con cada fotograma.
            # Rellenar los planos completos, incluido su posible padding.
            brightness = 32 + index % 180
            frame.planes[0].update(
                bytes([brightness]) * frame.planes[0].buffer_size
            )

            for plane in frame.planes[1:]:
                plane.update(bytes([128]) * plane.buffer_size)

            for packet in stream.encode(frame):
                output.mux(packet)

        for packet in stream.encode():
            output.mux(packet)

    return path


def packet_state(packet) -> tuple:
    """Capturar los datos que el publicador debe dejar intactos."""
    return (
        bytes(packet),
        packet.pts,
        packet.dts,
        packet.duration,
        packet.time_base,
        packet.is_keyframe,
        packet.stream,
    )


def test_hls_is_playable_and_preserves_local_video(
    synthetic_video: Path,
) -> None:
    """Generar HLS y decodificar el original desde los mismos paquetes."""
    with av.open(str(synthetic_video)) as source:
        stream = source.streams.video[0]
        publisher = HlsPublisher(stream)
        directory = publisher.directory
        local_frames = 0
        published_packets = 0

        try:
            for packet in source.demux(stream):
                before = packet_state(packet)

                if publisher.write_packet(packet):
                    published_packets += 1

                assert packet_state(packet) == before

                # El visor local podrá seguir decodificando el original.
                local_frames += len(packet.decode())

            assert local_frames == 320
            assert published_packets > 0
            assert publisher.playlist_path.is_file()

            playlist = publisher.playlist_path.read_text(
                encoding="utf-8"
            )
            assert playlist.startswith("#EXTM3U")

            segment_names = [
                line.strip()
                for line in playlist.splitlines()
                if line.strip() and not line.startswith("#")
            ]

            # La lista debe mantener una ventana de cinco segmentos.
            assert len(segment_names) == 5

            for name in segment_names:
                # La lista debe utilizar nombres relativos a su carpeta.
                assert Path(name).name == name
                segment_path = directory / name
                assert segment_path.is_file()

                # Comprobar el vídeo real, no solo la existencia del archivo.
                with av.open(str(segment_path)) as segment:
                    assert (
                        segment.streams.video[0].codec_context.name
                        == "h264"
                    )

                    decoded_frames = 0

                    for frame in segment.decode(video=0):
                        assert frame.width == 160
                        assert frame.height == 96
                        decoded_frames += 1

                    assert decoded_frames > 0

            # Se conservan algunos segmentos extra para lectores rezagados,
            # pero no todos los generados durante los 32 segundos.
            assert len(list(directory.glob("segment_*.ts"))) < 16

        finally:
            publisher.close()

        assert not directory.exists()

        # Cerrar una segunda vez debe ser inocuo.
        publisher.close()


def test_rejects_unsupported_codec() -> None:
    """Rechazar H.265 antes de crear una sesión de publicación."""
    source_stream = SimpleNamespace(
        codec_context=SimpleNamespace(name="hevc")
    )

    with pytest.raises(ValueError, match="H.264"):
        HlsPublisher(source_stream)


def test_close_without_packets(synthetic_video: Path) -> None:
    """Permitir cancelar la publicación antes del primer paquete."""
    with av.open(str(synthetic_video)) as source:
        publisher = HlsPublisher(source.streams.video[0])
        directory = publisher.directory

        assert directory.is_dir()

        publisher.close()

        assert not directory.exists()

        with pytest.raises(RuntimeError, match="cerrado"):
            publisher.write_packet(av.Packet())


def test_missing_timestamps_are_rejected(
    synthetic_video: Path,
) -> None:
    """Informar si un paquete inicial carece de marcas temporales."""
    with av.open(str(synthetic_video)) as source:
        stream = source.streams.video[0]
        publisher = HlsPublisher(stream)

        try:
            packet = next(
                packet
                for packet in source.demux(stream)
                if packet.size > 0 and packet.is_keyframe
            )
            packet.pts = None

            with pytest.raises(ValueError, match="marcas temporales"):
                publisher.write_packet(packet)

        finally:
            publisher.close()


# Fin archivo: tests/test_hls_publisher.py