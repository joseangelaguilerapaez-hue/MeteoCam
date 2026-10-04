"""Servidor HTTP local para una sesión HLS de MeteoCam."""

from __future__ import annotations

import mimetypes
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import unquote, urlsplit


class _HlsRequestHandler(SimpleHTTPRequestHandler):
    """Servir exclusivamente los archivos HLS de una sesión."""

    server_version = "MeteoCamHLS/0.1"

    def __init__(
        self,
        *args,
        hls_directory: Path,
        **kwargs,
    ) -> None:
        """Vincular el manejador a una única carpeta HLS."""
        self._hls_directory = Path(hls_directory).resolve()

        super().__init__(
            *args,
            directory=str(self._hls_directory),
            **kwargs,
        )

    def log_message(
        self,
        format: str,
        *args,
    ) -> None:
        """Evitar que el servidor HTTP escriba peticiones en consola."""
        return

    def do_GET(self) -> None:
        """Atender únicamente recursos pertenecientes a la sesión HLS."""
        requested_path = self._resolve_requested_path()

        if requested_path is None:
            self.send_error(
                HTTPStatus.NOT_FOUND,
                "Recurso HLS no disponible.",
            )
            return

        super().do_GET()

    def do_HEAD(self) -> None:
        """Permitir consultar cabeceras de recursos HLS válidos."""
        requested_path = self._resolve_requested_path()

        if requested_path is None:
            self.send_error(
                HTTPStatus.NOT_FOUND,
                "Recurso HLS no disponible.",
            )
            return

        super().do_HEAD()

    def translate_path(self, path: str) -> str:
        """Traducir una URL únicamente dentro de la carpeta HLS."""
        requested_path = self._resolve_requested_path()

        if requested_path is None:
            return str(self._hls_directory / "__not_found__")

        return str(requested_path)

    def end_headers(self) -> None:
        """Añadir cabeceras apropiadas para reproducción en navegador."""
        self.send_header(
            "Cache-Control",
            "no-store, no-cache, must-revalidate",
        )
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    def guess_type(self, path: str) -> str:
        """Asignar tipos MIME explícitos a listas y segmentos HLS."""
        suffix = Path(path).suffix.lower()

        if suffix == ".m3u8":
            return "application/vnd.apple.mpegurl"

        if suffix == ".ts":
            return "video/mp2t"

        return mimetypes.guess_type(path)[0] or "application/octet-stream"

    def _resolve_requested_path(self) -> Path | None:
        """Resolver una petición sin permitir salir de la carpeta HLS."""
        raw_path = urlsplit(self.path).path
        decoded_path = unquote(raw_path)

        relative_path = decoded_path.lstrip("/")

        if not relative_path:
            relative_path = "index.m3u8"

        candidate = (
            self._hls_directory / relative_path
        ).resolve()

        try:
            candidate.relative_to(self._hls_directory)
        except ValueError:
            return None

        if candidate.name == "index.m3u8":
            return candidate

        if (
            candidate.parent == self._hls_directory
            and candidate.name.startswith("segment_")
            and candidate.suffix.lower() == ".ts"
        ):
            return candidate

        return None


class HlsServer:
    """Servir una carpeta HLS mediante HTTP en segundo plano.

    El servidor no conoce la cámara, las credenciales RTSP ni el origen
    del vídeo. Únicamente publica los archivos generados dentro de una
    carpeta HLS concreta.

    Por defecto escucha solo en localhost. Exponer el servicio a otras
    interfaces debe ser una decisión explícita del código llamante.
    """

    def __init__(
        self,
        directory: Path,
        host: str = "127.0.0.1",
        port: int = 0,
    ) -> None:
        """Preparar el servidor sin iniciarlo todavía."""
        self._directory = Path(directory).resolve()

        if not self._directory.is_dir():
            raise ValueError(
                "La carpeta HLS no existe o no es un directorio."
            )

        self._host = host
        self._requested_port = port

        self._httpd: ThreadingHTTPServer | None = None
        self._thread: Thread | None = None

    @property
    def host(self) -> str:
        """Dirección en la que escucha el servidor."""
        return self._host

    @property
    def port(self) -> int:
        """Puerto real del servidor.

        Si se solicitó el puerto 0, el sistema asignará uno al iniciar.
        """
        if self._httpd is None:
            return self._requested_port

        return int(self._httpd.server_address[1])

    @property
    def playlist_url(self) -> str:
        """URL local de la lista HLS."""
        if self._httpd is None:
            raise RuntimeError(
                "El servidor HLS todavía no está iniciado."
            )

        host = self._format_host_for_url(self.host)

        return f"http://{host}:{self.port}/index.m3u8"

    @property
    def is_running(self) -> bool:
        """Indicar si el servidor HTTP está activo."""
        return (
            self._httpd is not None
            and self._thread is not None
            and self._thread.is_alive()
        )

    def start(self) -> None:
        """Iniciar el servidor HTTP en un hilo dedicado."""
        if self._httpd is not None:
            raise RuntimeError(
                "El servidor HLS ya está iniciado."
            )

        directory = self._directory

        class SessionRequestHandler(_HlsRequestHandler):
            """Handler ligado exclusivamente a esta sesión HLS."""

            def __init__(self, *args, **kwargs) -> None:
                super().__init__(
                    *args,
                    hls_directory=directory,
                    **kwargs,
                )

        httpd = ThreadingHTTPServer(
            (self._host, self._requested_port),
            SessionRequestHandler,
        )

        httpd.daemon_threads = True

        thread = Thread(
            target=httpd.serve_forever,
            name="MeteoCam-HLS-HTTP",
            daemon=True,
        )

        self._httpd = httpd
        self._thread = thread

        try:
            thread.start()
        except Exception:
            self._httpd = None
            self._thread = None
            httpd.server_close()
            raise

    def stop(self) -> None:
        """Detener el servidor y liberar el puerto."""
        httpd = self._httpd
        thread = self._thread

        if httpd is None:
            return

        self._httpd = None
        self._thread = None

        try:
            httpd.shutdown()

            if thread is not None:
                thread.join(timeout=5.0)
        finally:
            httpd.server_close()

    @staticmethod
    def _format_host_for_url(host: str) -> str:
        """Formatear correctamente hosts IPv4, IPv6 y nombres DNS."""
        if ":" in host and not host.startswith("["):
            return f"[{host}]"

        return host


# Fin de fichero
# Fin archivo: src/meteocam/cameras/hls_server.py