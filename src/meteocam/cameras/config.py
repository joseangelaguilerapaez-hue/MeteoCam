"""Configuración de cámaras y vistas conocidas por MeteoCam."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CameraConfig:
    """Configuración de una cámara o vista disponible en MeteoCam.

    Una misma cámara física puede proporcionar varias vistas seleccionables.
    En ese caso, cada vista tiene su propio código y ruta RTSP, pero comparte
    el mismo ``device_code`` con las demás vistas del dispositivo.
    """

    code: str
    device_code: str
    name: str
    station: str
    manufacturer: str
    model: str
    host: str
    rtsp_path: str
    rtsp_port: int = 554


CAMERAS: tuple[CameraConfig, ...] = (
    CameraConfig(
        code="sv3c-pg207-pruebas",
        device_code="sv3c-pg207-pruebas",
        name="SV3C PG207",
        station="Pruebas",
        manufacturer="SV3C",
        model="PG207",
        host="192.168.178.61",
        rtsp_path="/11",
        rtsp_port=554,
    ),
    CameraConfig(
        code="reolink-omvi3i-los-llanos-panoramica",
        device_code="reolink-omvi3i-los-llanos",
        name="MeteoCam Los Llanos — Panorámica",
        station="Los Llanos",
        manufacturer="Reolink",
        model="OMVI 3i PoE",
        host="192.168.1.100",
        rtsp_path="/Preview_01_sub",
        rtsp_port=554,
    ),
    CameraConfig(
        code="reolink-omvi3i-los-llanos-ptz",
        device_code="reolink-omvi3i-los-llanos",
        name="MeteoCam Los Llanos — PTZ",
        station="Los Llanos",
        manufacturer="Reolink",
        model="OMVI 3i PoE",
        host="192.168.1.100",
        rtsp_path="/Preview_02_sub",
        rtsp_port=554,
    ),
)


def get_camera(code: str) -> CameraConfig | None:
    """Obtener una cámara o vista conocida mediante su código."""

    for camera in CAMERAS:
        if camera.code == code:
            return camera

    return None


def get_device_cameras(device_code: str) -> tuple[CameraConfig, ...]:
    """Obtener todas las vistas pertenecientes a un dispositivo físico."""

    return tuple(
        camera
        for camera in CAMERAS
        if camera.device_code == device_code
    )


# Fin de fichero
# Fin archivo: src/meteocam/cameras/config.py