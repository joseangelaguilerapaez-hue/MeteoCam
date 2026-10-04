"""Pruebas del servidor HTTP local para sesiones HLS."""

from __future__ import annotations

from email.message import Message
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from meteocam.cameras.hls_server import HlsServer


@pytest.fixture
def hls_directory(tmp_path: Path) -> Path:
    """Crear una carpeta HLS mínima para las pruebas."""
    playlist = tmp_path / "index.m3u8"
    segment = tmp_path / "segment_000000001.ts"

    playlist.write_text(
        "\n".join(
            (
                "#EXTM3U",
                "#EXT-X-VERSION:3",
                "#EXT-X-TARGETDURATION:2",
                "#EXTINF:2.0,",
                segment.name,
                "",
            )
        ),
        encoding="utf-8",
    )

    segment.write_bytes(b"meteocam-test-segment")

    return tmp_path


def _read_url(
    url: str,
) -> tuple[int, Message, bytes]:
    """Leer una URL conservando las cabeceras HTTP originales."""
    with urlopen(url, timeout=3) as response:
        return (
            response.status,
            response.headers,
            response.read(),
        )


def test_serves_playlist_and_segment(
    hls_directory: Path,
) -> None:
    """Servir correctamente la lista y sus segmentos."""
    server = HlsServer(hls_directory)

    try:
        server.start()

        assert server.is_running
        assert server.port > 0

        status, headers, body = _read_url(server.playlist_url)

        assert status == 200
        assert body.startswith(b"#EXTM3U")
        assert (
            headers["Content-Type"]
            == "application/vnd.apple.mpegurl"
        )
        assert headers["Cache-Control"] == (
            "no-store, no-cache, must-revalidate"
        )
        assert headers["X-Content-Type-Options"] == "nosniff"

        segment_url = (
            f"http://127.0.0.1:{server.port}/"
            "segment_000000001.ts"
        )

        status, headers, body = _read_url(segment_url)

        assert status == 200
        assert body == b"meteocam-test-segment"
        assert headers["Content-Type"] == "video/mp2t"

    finally:
        server.stop()

    assert not server.is_running


def test_root_serves_playlist(
    hls_directory: Path,
) -> None:
    """Permitir usar la raíz como acceso directo a index.m3u8."""
    server = HlsServer(hls_directory)

    try:
        server.start()

        root_url = f"http://127.0.0.1:{server.port}/"
        status, _, body = _read_url(root_url)

        assert status == 200
        assert body.startswith(b"#EXTM3U")

    finally:
        server.stop()


def test_rejects_unrelated_files(
    hls_directory: Path,
) -> None:
    """No convertir la carpeta HLS en un servidor general de archivos."""
    secret_file = hls_directory / "private.txt"
    secret_file.write_text(
        "este archivo no debe publicarse",
        encoding="utf-8",
    )

    server = HlsServer(hls_directory)

    try:
        server.start()

        url = f"http://127.0.0.1:{server.port}/private.txt"

        with pytest.raises(HTTPError) as error:
            urlopen(url, timeout=3)

        assert error.value.code == 404

    finally:
        server.stop()


def test_rejects_nested_paths(
    hls_directory: Path,
) -> None:
    """Rechazar segmentos fuera del nivel raíz de la sesión."""
    nested_directory = hls_directory / "nested"
    nested_directory.mkdir()

    nested_segment = nested_directory / "segment_000000002.ts"
    nested_segment.write_bytes(b"nested")

    server = HlsServer(hls_directory)

    try:
        server.start()

        url = (
            f"http://127.0.0.1:{server.port}/"
            "nested/segment_000000002.ts"
        )

        with pytest.raises(HTTPError) as error:
            urlopen(url, timeout=3)

        assert error.value.code == 404

    finally:
        server.stop()


def test_rejects_path_traversal(
    hls_directory: Path,
    tmp_path: Path,
) -> None:
    """Impedir acceder a archivos situados fuera de la carpeta HLS."""
    outside_file = tmp_path.parent / "outside-meteocam.txt"
    outside_file.write_text(
        "no publicar",
        encoding="utf-8",
    )

    server = HlsServer(hls_directory)

    try:
        server.start()

        url = (
            f"http://127.0.0.1:{server.port}/"
            "%2e%2e/outside-meteocam.txt"
        )

        with pytest.raises(HTTPError) as error:
            urlopen(url, timeout=3)

        assert error.value.code == 404

    finally:
        server.stop()


def test_head_request(
    hls_directory: Path,
) -> None:
    """Responder HEAD sin enviar el cuerpo del recurso."""
    server = HlsServer(hls_directory)

    try:
        server.start()

        request = Request(
            server.playlist_url,
            method="HEAD",
        )

        with urlopen(request, timeout=3) as response:
            assert response.status == 200
            assert (
                response.headers["Content-Type"]
                == "application/vnd.apple.mpegurl"
            )
            assert response.read() == b""

    finally:
        server.stop()


def test_start_twice_is_rejected(
    hls_directory: Path,
) -> None:
    """Evitar iniciar dos veces una misma instancia."""
    server = HlsServer(hls_directory)

    try:
        server.start()

        with pytest.raises(RuntimeError, match="ya está iniciado"):
            server.start()

    finally:
        server.stop()


def test_stop_before_start_is_safe(
    hls_directory: Path,
) -> None:
    """Permitir detener una instancia que todavía no se inició."""
    server = HlsServer(hls_directory)

    server.stop()

    assert not server.is_running


def test_missing_directory_is_rejected(
    tmp_path: Path,
) -> None:
    """Rechazar una carpeta HLS inexistente."""
    missing = tmp_path / "does-not-exist"

    with pytest.raises(
        ValueError,
        match="no existe",
    ):
        HlsServer(missing)


# Fin de fichero
# Fin archivo: tests/test_hls_server.py