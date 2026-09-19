"""Diagnóstico RTSP independiente de la interfaz y del fabricante."""

from __future__ import annotations

import hashlib
import ipaddress
import re
import secrets
import socket
import time
from dataclasses import dataclass, field
from typing import Callable
from urllib.request import parse_http_list, parse_keqv_list


@dataclass(frozen=True)
class CameraTarget:
    """Dirección de una cámara y rutas candidatas, sin credenciales."""

    host: str
    port: int = 554
    paths: tuple[str, ...] = ("/11", "/1", "/12")
    timeout: float = 3.0


@dataclass(frozen=True)
class Credentials:
    """Credenciales temporales en memoria, sin mostrarlas en representaciones."""

    username: str = field(repr=False)
    password: str = field(repr=False)


@dataclass(frozen=True)
class DiagnosticEvent:
    """Una traza segura para mostrar al usuario."""

    code: str
    message: str


@dataclass(frozen=True)
class DiagnosticResult:
    """Resultado del diagnóstico, sin credenciales ni URL de conexión."""

    status: str
    validated_path: str | None = field(default=None, repr=False)
    events: tuple[DiagnosticEvent, ...] = ()


@dataclass(frozen=True)
class _Response:
    """Respuesta RTSP interna."""

    status: int
    headers: dict[str, str]
    body: bytes = field(repr=False)


class _ProtocolError(Exception):
    """La respuesta RTSP no se puede interpretar con seguridad."""


class _UnsupportedAuth(Exception):
    """La variante de autenticación no está soportada."""


def _validate_target(target: CameraTarget) -> str:
    """Validar IP, puerto y rutas antes de abrir una conexión."""

    address = ipaddress.ip_address(target.host)

    if not 1 <= target.port <= 65535:
        raise ValueError("Puerto no válido")

    if not 0.1 <= target.timeout <= 15:
        raise ValueError("Tiempo de espera no válido")

    if not 1 <= len(target.paths) <= 16:
        raise ValueError("Número de rutas no válido")

    for path in target.paths:
        if (
            not path.startswith("/")
            or path.startswith("//")
            or len(path) > 1024
            or any(ord(character) < 33 or ord(character) > 126 for character in path)
            or any(character in path for character in ("@", "#", "\\"))
        ):
            raise ValueError("Ruta no válida")

    host = f"[{address}]" if address.version == 6 else str(address)
    return f"rtsp://{host}:{target.port}"


def _describe(
    connection: socket.socket,
    uri: str,
    sequence: int,
    timeout: float,
    authorization: str | None = None,
) -> _Response:
    """Enviar DESCRIBE y leer una respuesta RTSP completa."""

    lines = [
        f"DESCRIBE {uri} RTSP/1.0",
        f"CSeq: {sequence}",
        "Accept: application/sdp",
        "User-Agent: MeteoCam",
    ]

    if authorization is not None:
        lines.append(f"Authorization: {authorization}")

    deadline = time.monotonic() + timeout
    connection.settimeout(timeout)
    connection.sendall(("\r\n".join(lines) + "\r\n\r\n").encode("utf-8"))

    data = bytearray()

    def receive() -> bytes:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError

        connection.settimeout(remaining)
        chunk = connection.recv(4096)

        if not chunk:
            raise _ProtocolError

        return chunk

    while b"\r\n\r\n" not in data:
        data.extend(receive())

        if len(data) > 65536:
            raise _ProtocolError

    head, body = bytes(data).split(b"\r\n\r\n", 1)
    lines = head.decode("iso-8859-1").split("\r\n")

    match = re.fullmatch(r"RTSP/1\.0 (\d{3})(?: .*)?", lines[0])
    if match is None:
        raise _ProtocolError

    headers: dict[str, str] = {}

    for line in lines[1:]:
        key, separator, value = line.partition(":")

        if not separator:
            raise _ProtocolError

        key = key.strip().lower()

        if key in headers:
            raise _ProtocolError

        headers[key] = value.strip()

    if headers.get("cseq") != str(sequence):
        raise _ProtocolError

    try:
        content_length = int(headers.get("content-length", "0"))
    except ValueError:
        raise _ProtocolError from None

    if not 0 <= content_length <= 262144:
        raise _ProtocolError

    while len(body) < content_length:
        body += receive()

    return _Response(
        status=int(match.group(1)),
        headers=headers,
        body=body[:content_length],
    )


def _quoted(value: str) -> str:
    """Escapar un valor para una cabecera Digest."""

    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise _UnsupportedAuth

    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _digest(
    challenge: str,
    credentials: Credentials,
    uri: str,
) -> str:
    """Construir una cabecera HTTP Digest para una solicitud DESCRIBE."""

    scheme, separator, parameters = challenge.partition(" ")

    if not separator or scheme.lower() != "digest":
        raise _UnsupportedAuth

    values = {
        key.lower(): value
        for key, value in parse_keqv_list(parse_http_list(parameters)).items()
    }

    realm = values.get("realm")
    nonce = values.get("nonce")

    if realm is None or not nonce:
        raise _UnsupportedAuth

    algorithm = values.get("algorithm", "MD5").upper()

    algorithms = {
        "MD5": "md5",
        "MD5-SESS": "md5",
        "SHA-256": "sha256",
        "SHA-256-SESS": "sha256",
    }

    if algorithm not in algorithms:
        raise _UnsupportedAuth

    if values.get("userhash", "false").lower() == "true":
        raise _UnsupportedAuth

    charset = values.get("charset", "").lower()

    if charset not in ("", "utf-8"):
        raise _UnsupportedAuth

    encoding = "utf-8" if charset else "iso-8859-1"

    def digest(text: str) -> str:
        return hashlib.new(
            algorithms[algorithm],
            text.encode(encoding),
        ).hexdigest()

    cnonce = secrets.token_hex(16)

    ha1 = digest(
        f"{credentials.username}:{realm}:{credentials.password}"
    )

    if algorithm.endswith("-SESS"):
        ha1 = digest(f"{ha1}:{nonce}:{cnonce}")

    ha2 = digest(f"DESCRIBE:{uri}")

    qop = values.get("qop")

    if qop is not None:
        qop_options = {item.strip().lower() for item in qop.split(",")}

        if "auth" not in qop_options:
            raise _UnsupportedAuth

        response = digest(f"{ha1}:{nonce}:00000001:{cnonce}:auth:{ha2}")
    else:
        response = digest(f"{ha1}:{nonce}:{ha2}")

    fields = [
        f"username={_quoted(credentials.username)}",
        f"realm={_quoted(realm)}",
        f"nonce={_quoted(nonce)}",
        f"uri={_quoted(uri)}",
        f"response={_quoted(response)}",
        f"algorithm={algorithm}",
    ]

    if "opaque" in values:
        fields.append(f"opaque={_quoted(values['opaque'])}")

    if qop is not None:
        fields.extend(
            [
                "qop=auth",
                "nc=00000001",
                f"cnonce={_quoted(cnonce)}",
            ]
        )
    elif algorithm.endswith("-SESS"):
        fields.append(f"cnonce={_quoted(cnonce)}")

    return "Digest " + ", ".join(fields)


def _has_video(response: _Response) -> bool:
    """Reconocer una descripción SDP con al menos un medio de vídeo.

    En RTSP, el puerto indicado en SDP puede ser 0 porque el transporte se
    negocia en un paso posterior mediante SETUP.
    """

    content_type = response.headers.get("content-type", "")

    if content_type.split(";", 1)[0].strip().lower() != "application/sdp":
        return False

    lines = response.body.decode("utf-8", errors="replace").splitlines()

    if "v=0" not in lines:
        return False

    for line in lines:
        if not line.startswith("m="):
            continue

        fields = line[2:].split()

        if len(fields) < 4 or fields[0].lower() != "video":
            continue

        port_parts = fields[1].split("/")

        if len(port_parts) > 2:
            continue

        try:
            port = int(port_parts[0])
            port_count = int(port_parts[1]) if len(port_parts) == 2 else 1
            payloads = [int(value) for value in fields[3:]]
        except ValueError:
            continue

        if not 0 <= port <= 65535 or port_count < 1:
            continue

        if not fields[2].upper().startswith("RTP/"):
            continue

        if payloads and all(0 <= value <= 127 for value in payloads):
            return True

    return False


def diagnose(
    target: CameraTarget,
    credentials: Credentials | None = None,
    on_event: Callable[[DiagnosticEvent], None] | None = None,
) -> DiagnosticResult:
    """Comprobar red, RTSP, autenticación y descripción de vídeo.

    Debe ejecutarse fuera del hilo de la interfaz. Nunca publica respuestas
    crudas, cabeceras Digest, contraseñas ni URLs con credenciales.
    """

    events: list[DiagnosticEvent] = []

    def emit(code: str, message: str) -> None:
        event = DiagnosticEvent(code, message)
        events.append(event)

        if on_event is not None:
            on_event(event)

    def finish(
        status: str,
        path: str | None = None,
    ) -> DiagnosticResult:
        return DiagnosticResult(
            status=status,
            validated_path=path,
            events=tuple(events),
        )

    try:
        base_uri = _validate_target(target)
    except (TypeError, ValueError):
        emit("CAM-NET-400", "Revisa la IP, el puerto y las rutas configuradas.")
        return finish("invalid_target")

    emit("CAM-NET-001", "Dirección IP válida; comprobando conexión.")

    connected_once = False

    for index, path in enumerate(target.paths, start=1):
        uri = base_uri + path

        try:
            with socket.create_connection(
                (target.host, target.port),
                timeout=target.timeout,
            ) as connection:
                if not connected_once:
                    connected_once = True
                    emit("CAM-NET-002", "Dispositivo accesible mediante TCP.")
                    emit("CAM-RTSP-001", "Puerto RTSP abierto.")

                response = _describe(
                    connection=connection,
                    uri=uri,
                    sequence=1,
                    timeout=target.timeout,
                )

                server = response.headers.get("server", "")

                if server == "Hipcam RealServer/V1.0":
                    emit(
                        "CAM-RTSP-002",
                        "Servidor identificado: Hipcam RealServer/V1.0.",
                    )
                elif server:
                    emit("CAM-RTSP-002", "Servidor RTSP detectado.")
                else:
                    emit("CAM-RTSP-002", "Servicio RTSP detectado.")

                if response.status == 401:
                    challenge = response.headers.get("www-authenticate", "")
                    scheme = challenge.partition(" ")[0].lower()

                    if scheme != "digest":
                        emit(
                            "CAM-AUTH-405",
                            "Método de autenticación no compatible.",
                        )
                        return finish("unsupported_auth")

                    emit(
                        "CAM-AUTH-001",
                        "El servidor requiere autenticación Digest.",
                    )

                    if credentials is None:
                        emit(
                            "CAM-AUTH-100",
                            "Introduce las credenciales de la cámara.",
                        )
                        return finish("credentials_required")

                    authorization = _digest(
                        challenge=challenge,
                        credentials=credentials,
                        uri=uri,
                    )

                    response = _describe(
                        connection=connection,
                        uri=uri,
                        sequence=2,
                        timeout=target.timeout,
                        authorization=authorization,
                    )

                    if response.status in (401, 403):
                        emit(
                            "CAM-AUTH-401",
                            "Acceso rechazado; revisa las credenciales.",
                        )
                        return finish("auth_rejected")

                    emit("CAM-AUTH-002", "Acceso al stream autorizado.")

                elif response.status == 403:
                    emit(
                        "CAM-AUTH-403",
                        "El servidor no permite acceder al recurso.",
                    )
                    return finish("access_denied")

                if response.status == 200:
                    if not _has_video(response):
                        emit(
                            "CAM-STREAM-422",
                            f"Candidata {index}: descripción de vídeo no válida.",
                        )
                        continue

                    emit(
                        "CAM-STREAM-001",
                        f"Candidata {index}: descripción de vídeo validada.",
                    )
                    emit(
                        "CAM-STREAM-100",
                        "Pendiente abrir el vídeo y comprobar la recepción de imágenes.",
                    )
                    return finish("stream_validated", path)

                if response.status in (400, 404):
                    emit(
                        "CAM-STREAM-404",
                        f"Candidata {index}: ruta rechazada por el servidor.",
                    )
                    continue

                emit(
                    "CAM-RTSP-400",
                    f"El servidor respondió con estado RTSP {response.status}.",
                )
                return finish("rtsp_error")

        except _UnsupportedAuth:
            emit(
                "CAM-AUTH-405",
                "Variante Digest no compatible con esta versión de MeteoCam.",
            )
            return finish("unsupported_auth")

        except UnicodeError:
            emit(
                "CAM-AUTH-405",
                "La respuesta de autenticación contiene caracteres no compatibles.",
            )
            return finish("unsupported_auth")

        except _ProtocolError:
            emit(
                "CAM-RTSP-422",
                "Respuesta RTSP incompleta o no válida.",
            )
            return finish("protocol_error")

        except (TimeoutError, OSError):
            if connected_once:
                emit(
                    "CAM-RTSP-408",
                    "La comunicación RTSP se interrumpió o agotó el tiempo.",
                )
            else:
                emit(
                    "CAM-NET-503",
                    "No se pudo conectar al puerto RTSP de la cámara.",
                )

            return finish("connection_failed")

    emit(
        "CAM-STREAM-404",
        "Ninguna de las rutas candidatas devolvió vídeo válido.",
    )
    return finish("stream_not_found")


# Fin archivo: src/meteocam/cameras/diagnostics.py