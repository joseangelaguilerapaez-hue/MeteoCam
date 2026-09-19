"""Pruebas del diagnóstico de cámaras sin acceso a la red."""

from unittest.mock import MagicMock, patch

from meteocam.cameras.diagnostics import (
    CameraTarget,
    Credentials,
    _Response,
    _digest,
    diagnose,
)


MODULE = "meteocam.cameras.diagnostics"

VIDEO_DESCRIPTION = (
    b"v=0\r\n"
    b"o=- 0 0 IN IP4 192.168.178.61\r\n"
    b"s=Camera\r\n"
    b"t=0 0\r\n"
    b"m=video 5004 RTP/AVP 96\r\n"
    b"a=rtpmap:96 H264/90000\r\n"
)

DIGEST_CHALLENGE = (
    'Digest realm="camera", nonce="test-nonce", qop="auth"'
)


def run_simulated(responses, credentials=None):
    """Sustituir transporte y respuestas sin abrir conexiones."""
    connection = MagicMock()

    with (
        patch(
            f"{MODULE}.socket.create_connection",
            return_value=connection,
        ),
        patch(f"{MODULE}._describe", side_effect=responses) as describe,
    ):
        result = diagnose(
            CameraTarget("192.168.178.61"),
            credentials,
        )

    return result, describe


def test_invalid_ip_does_not_connect():
    """Una IP no válida no debe provocar tráfico de red."""
    with patch(f"{MODULE}.socket.create_connection") as connect:
        result = diagnose(CameraTarget("not-an-ip"))

    assert result.status == "invalid_target"
    connect.assert_not_called()


def test_closed_port_reports_network_failure():
    """Un puerto cerrado debe indicar un fallo de conexión."""
    with patch(
        f"{MODULE}.socket.create_connection",
        side_effect=ConnectionRefusedError,
    ):
        result = diagnose(CameraTarget("192.168.178.61"))

    assert result.status == "connection_failed"
    assert result.events[-1].code == "CAM-NET-503"


def test_401_requires_credentials_and_does_not_validate_path():
    """Una respuesta Digest sin contraseña debe detener el diagnóstico."""
    response = _Response(
        401,
        {
            "server": "Hipcam RealServer/V1.0",
            "www-authenticate": DIGEST_CHALLENGE,
        },
        b"",
    )

    result, describe = run_simulated([response])

    assert result.status == "credentials_required"
    assert result.validated_path is None
    assert describe.call_count == 1
    assert result.events[-1].code == "CAM-AUTH-100"
    assert not any(
        event.code == "CAM-STREAM-001"
        for event in result.events
    )


def test_digest_then_valid_video_description():
    """Una respuesta Digest correcta valida la descripción SDP del vídeo."""
    credentials = Credentials("admin", "secret-for-test")

    responses = [
        _Response(
            401,
            {"www-authenticate": DIGEST_CHALLENGE},
            b"",
        ),
        _Response(
            200,
            {"content-type": "application/sdp"},
            VIDEO_DESCRIPTION,
        ),
    ]

    result, describe = run_simulated(responses, credentials)

    assert result.status == "stream_validated"
    assert result.validated_path == "/11"
    assert describe.call_count == 2

    authorization = describe.call_args_list[1].kwargs["authorization"]

    assert authorization.startswith("Digest ")
    assert credentials.password not in authorization
    assert credentials.password not in repr(credentials)
    assert credentials.password not in repr(result)
    assert "rtsp://" not in repr(result)

    # Validar DESCRIBE no equivale todavía a recibir imágenes.
    assert result.events[-1].code == "CAM-STREAM-100"


def test_rejected_credentials_stop_further_attempts():
    """Las credenciales rechazadas no deben probar otras rutas."""
    response = _Response(
        401,
        {"www-authenticate": DIGEST_CHALLENGE},
        b"",
    )

    result, describe = run_simulated(
        [response, response],
        Credentials("admin", "wrong-password"),
    )

    assert result.status == "auth_rejected"
    assert result.validated_path is None
    assert describe.call_count == 2


def test_missing_path_tries_next_candidate():
    """Una ruta inexistente debe permitir probar la siguiente."""
    responses = [
        _Response(404, {}, b""),
        _Response(
            200,
            {"content-type": "application/sdp"},
            VIDEO_DESCRIPTION,
        ),
    ]

    result, describe = run_simulated(responses)

    assert result.status == "stream_validated"
    assert result.validated_path == "/1"
    assert describe.call_count == 2


def test_200_without_video_does_not_validate_stream():
    """Una respuesta 200 sin SDP de vídeo no valida un stream."""
    response = _Response(
        200,
        {"content-type": "text/html"},
        b"<html>Camera login</html>",
    )

    result, _ = run_simulated([response, response, response])

    assert result.status == "stream_not_found"
    assert result.validated_path is None


def test_rtsp_video_with_zero_port_is_valid():
    """RTSP permite un puerto SDP 0 antes de negociar SETUP."""
    response = _Response(
        200,
        {"content-type": "application/sdp"},
        VIDEO_DESCRIPTION.replace(
            b"m=video 5004",
            b"m=video 0",
        ),
    )

    result, describe = run_simulated([response])

    assert result.status == "stream_validated"
    assert result.validated_path == "/11"
    assert describe.call_count == 1


def test_digest_matches_known_calculation():
    """Comprobar el cálculo Digest sin enviar una solicitud real."""
    import hashlib

    credentials = Credentials("admin", "test-password")
    uri = "rtsp://192.168.178.61:554/11"

    def md5(value):
        return hashlib.md5(value.encode("ascii")).hexdigest()

    ha1 = md5("admin:camera:test-password")
    ha2 = md5(f"DESCRIBE:{uri}")
    expected = md5(
        f"{ha1}:test-nonce:00000001:fixed-cnonce:auth:{ha2}"
    )

    with patch(
        f"{MODULE}.secrets.token_hex",
        return_value="fixed-cnonce",
    ):
        header = _digest(DIGEST_CHALLENGE, credentials, uri)

    assert f'response="{expected}"' in header
    assert "qop=auth" in header
    assert "nc=00000001" in header
    assert "test-password" not in header