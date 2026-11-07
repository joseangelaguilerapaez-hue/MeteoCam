# -*- coding: utf-8 -*-

"""
Agente de órdenes de cámara de MeteoCam (patrullas, presets, órdenes).

Va dentro del servicio MeteoCamPublisher, junto a la publicación del
directo, pero es independiente de ella: si falla o no está configurado,
el directo sigue igual. Ver docs/agente.md.
"""

from __future__ import annotations

import logging

from pathlib import Path


logger = logging.getLogger("meteocam.agente")


def arrancar_desde_publisher(publisher: dict, carpeta: Path | None = None):
    """Arranca el agente si está configurado. Nunca lanza excepciones."""

    try:
        from meteocam.agente.configuracion import ConfiguracionIncompleta, cargar
        from meteocam.agente.ejecutor import AgenteCamaras

        try:
            configuracion = cargar(publisher, carpeta)
        except ConfiguracionIncompleta as motivo:
            logger.warning("Agente de órdenes de cámara desactivado: %s", motivo)
            return None

        agente = AgenteCamaras(configuracion)
        agente.iniciar()
        return agente

    except Exception:
        logger.exception("No se pudo arrancar el agente de órdenes de cámara.")
        return None


# Fin archivo: src/meteocam/agente/__init__.py
