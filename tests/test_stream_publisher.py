"""Pruebas del publicador RTSP independiente de MeteoCam."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import meteocam.cameras.stream_publisher as stream_publisher_module
from meteocam.cameras.diagnostics import Credentials
from meteocam.cameras.stream_publisher import StreamPublisher


class FakeCodecContext:
    """Contexto de códec H.264 simulado."""

    name = "h264"


class FakeVideoStream:
    """Stream de vídeo H.264 simulado."""

    type = "video"

    def __init__(self) -> None:
        self.codec_context = FakeCodecContext()


class FakePacket:
    """Paquete de vídeo simulado."""

    def __init__(self, number: int) -> None:
        self.number = number


class FakeContainer:
    """Contenedor RTSP simulado."""

    def __init__(
        self,
        packets: list[FakePacket] | None = None,
        *,
        with_video: bool = True,
    ) -> None:
        self.video_stream = FakeVideoStream()

        if with_video:
            self.streams = [self.video_stream]
        else:
            self.streams = []

        self._packets = packets or []
        self.closed = False

    def demux(self, stream):
        """Entregar los paquetes configurados."""
        assert stream is self.video_stream

        yield from self._packets

    def close(self) -> None:
        """Registrar el cierre del contenedor."""
        self.closed = True


class FakeHlsPublisher:
    """Empaquetador HLS simulado."""

    instances: list["FakeHlsPublisher"] = []

    def __init__(self, source_stream) -> None:
        self.source_stream = source_stream
        self.directory = MagicMock()
        self.closed = False
        self.received_packets: list[FakePacket] = []

        self.__class__.instances.append(self)

    def write_packet(self, packet) -> bool:
        """Aceptar todos los paquetes simulados."""
        self.received_packets.append(packet)
        return True

    def close(self) -> None:
        """Registrar el cierre del publicador."""
        self.closed = True


class FakeHlsServer:
    """Servidor HTTP HLS simulado."""

    instances: list["FakeHlsServer"] = []

    def __init__(
        self,
        directory,
        host: str = "127.0.0.1",
        port: int = 0,
    ) -> None:
        self.directory = directory
        self.host = host
        self.port = port

        self.started = False
        self.stopped = False

        self.playlist_url = (
            "http://127.0.0.1:45678/index.m3u8"
        )

        self.__class__.instances.append(self)

    def start(self) -> None:
        """Registrar el inicio del servidor."""
        self.started = True

    def stop(self) -> None:
        """Registrar la parada del servidor."""
        self.stopped = True


@pytest.fixture(autouse=True)
def reset_fakes():
    """Vaciar las instancias simuladas antes de cada prueba."""
    FakeHlsPublisher.instances.clear()
    FakeHlsServer.instances.clear()

    yield

    FakeHlsPublisher.instances.clear()
    FakeHlsServer.instances.clear()


def create_credentials(
    username: str = "admin",
    password: str = "secret",
) -> Credentials:
    """Crear credenciales para una prueba."""
    return Credentials(
        username=username,
        password=password,
    )


def install_hls_fakes(
    monkeypatch,
) -> None:
    """Sustituir publicador y servidor HLS por dobles de prueba."""
    monkeypatch.setattr(
        stream_publisher_module,
        "HlsPublisher",
        FakeHlsPublisher,
    )
    monkeypatch.setattr(
        stream_publisher_module,
        "HlsServer",
        FakeHlsServer,
    )


def test_build_url_uses_target_port_path_and_credentials():
    """Construir correctamente la URL RTSP de publicación."""
    credentials = create_credentials(
        username="usuario",
        password="clave",
    )

    publisher = StreamPublisher(
        target="192.168.1.100",
        path="/Preview_01_sub",
        credentials=credentials,
        rtsp_port=8554,
    )

    assert publisher._build_url() == (
        "rtsp://usuario:clave"
        "@192.168.1.100:8554"
        "/Preview_01_sub"
    )


def test_build_url_adds_missing_initial_slash():
    """Añadir la barra inicial cuando la ruta no la contiene."""
    credentials = create_credentials()

    publisher = StreamPublisher(
        target="192.168.1.100",
        path="Preview_02_sub",
        credentials=credentials,
    )

    assert publisher._build_url().endswith(
        ":554/Preview_02_sub"
    )


def test_build_url_escapes_special_credentials():
    """Escapar caracteres especiales de usuario y contraseña."""
    credentials = create_credentials(
        username="admin@test",
        password="a:b/c@d",
    )

    publisher = StreamPublisher(
        target="192.168.1.100",
        path="/Preview_01_sub",
        credentials=credentials,
    )

    url = publisher._build_url()

    assert "admin%40test" in url
    assert "a%3Ab%2Fc%40d" in url


def test_run_starts_independent_hls_publication(
    monkeypatch,
):
    """Publicar los paquetes RTSP mediante HLS."""
    install_hls_fakes(monkeypatch)

    container = FakeContainer(
        packets=[
            FakePacket(1),
            FakePacket(2),
        ]
    )

    open_mock = MagicMock(
        return_value=container
    )

    monkeypatch.setattr(
        stream_publisher_module.av,
        "open",
        open_mock,
    )

    credentials = create_credentials()

    publisher = StreamPublisher(
        target="192.168.1.100",
        path="/Preview_01_sub",
        credentials=credentials,
    )

    started_urls: list[str] = []

    publisher.publication_started.connect(
        started_urls.append
    )

    publisher.run()

    open_mock.assert_called_once()

    assert started_urls == [
        "http://127.0.0.1:45678/index.m3u8"
    ]

    assert len(
        FakeHlsPublisher.instances
    ) == 1

    fake_hls_publisher = (
        FakeHlsPublisher.instances[0]
    )

    assert [
        packet.number
        for packet
        in fake_hls_publisher.received_packets
    ] == [1, 2]

    assert fake_hls_publisher.closed is True

    assert len(
        FakeHlsServer.instances
    ) == 1

    fake_server = FakeHlsServer.instances[0]

    assert fake_server.started is True
    assert fake_server.stopped is True
    assert container.closed is True


def test_publication_started_is_emitted_only_once(
    monkeypatch,
):
    """Emitir una sola vez la URL aunque lleguen muchos paquetes."""
    install_hls_fakes(monkeypatch)

    container = FakeContainer(
        packets=[
            FakePacket(1),
            FakePacket(2),
            FakePacket(3),
        ]
    )

    monkeypatch.setattr(
        stream_publisher_module.av,
        "open",
        MagicMock(
            return_value=container
        ),
    )

    publisher = StreamPublisher(
        target="192.168.1.100",
        path="/Preview_01_sub",
        credentials=create_credentials(),
    )

    started_urls: list[str] = []

    publisher.publication_started.connect(
        started_urls.append
    )

    publisher.run()

    assert started_urls == [
        "http://127.0.0.1:45678/index.m3u8"
    ]


def test_run_reports_missing_video_stream(
    monkeypatch,
):
    """Informar del error cuando RTSP no contiene vídeo."""
    install_hls_fakes(monkeypatch)

    container = FakeContainer(
        with_video=False
    )

    monkeypatch.setattr(
        stream_publisher_module.av,
        "open",
        MagicMock(
            return_value=container
        ),
    )

    publisher = StreamPublisher(
        target="192.168.1.100",
        path="/Preview_01_sub",
        credentials=create_credentials(),
    )

    errors: list[str] = []

    publisher.publication_error.connect(
        errors.append
    )

    publisher.run()

    assert errors == [
        "La conexión RTSP no contiene vídeo."
    ]
    assert container.closed is True

    assert not FakeHlsPublisher.instances
    assert not FakeHlsServer.instances


def test_run_rejects_non_h264_video(
    monkeypatch,
):
    """Rechazar un stream que no pueda remultiplexarse como HLS."""
    install_hls_fakes(monkeypatch)

    container = FakeContainer()
    container.video_stream.codec_context.name = (
        "hevc"
    )

    monkeypatch.setattr(
        stream_publisher_module.av,
        "open",
        MagicMock(
            return_value=container
        ),
    )

    publisher = StreamPublisher(
        target="192.168.1.100",
        path="/Preview_01_main",
        credentials=create_credentials(),
    )

    errors: list[str] = []

    publisher.publication_error.connect(
        errors.append
    )

    publisher.run()

    assert errors == [
        "La publicación web requiere "
        "un stream RTSP H.264."
    ]

    assert container.closed is True
    assert not FakeHlsPublisher.instances
    assert not FakeHlsServer.instances


def test_run_reports_rtsp_open_error(
    monkeypatch,
):
    """Informar cuando no puede abrirse la conexión RTSP."""
    install_hls_fakes(monkeypatch)

    monkeypatch.setattr(
        stream_publisher_module.av,
        "open",
        MagicMock(
            side_effect=OSError(
                "RTSP no disponible"
            )
        ),
    )

    publisher = StreamPublisher(
        target="192.168.1.100",
        path="/Preview_01_sub",
        credentials=create_credentials(),
    )

    errors: list[str] = []

    publisher.publication_error.connect(
        errors.append
    )

    publisher.run()

    assert errors == [
        "RTSP no disponible"
    ]

    assert not FakeHlsPublisher.instances
    assert not FakeHlsServer.instances


def test_stop_sets_stop_request():
    """Solicitar una parada sin depender del visor local."""
    publisher = StreamPublisher(
        target="192.168.1.100",
        path="/Preview_01_sub",
        credentials=create_credentials(),
    )

    publisher.stop()

    assert publisher._stop_requested is True


# Fin de fichero
# Fin archivo: tests/test_stream_publisher.py