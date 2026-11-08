# -*- coding: utf-8 -*-

"""
Agente de órdenes de cámara: consulta la API y mueve las cámaras PTZ.

Diseño: docs/patrullas.md, secciones 4, 5, 7 y 11, de api-meteoarchidona.
Resumen en docs/agente.md de este repositorio.

- Un hilo de consulta pregunta a la API cada pocos segundos (5 por
  defecto; lo marca la propia API) qué debe hacer cada cámara.
- Un hilo por cámara ejecuta, paso a paso y de forma síncrona:

    1. Timelapse en curso  -> la cámara no se mueve (solo va al preset del
                              timelapse si lo tiene) y la patrulla se pausa.
    2. Orden pendiente     -> se reclama, se ejecuta y se informa del
                              resultado (POSICIONAR_PRESET,
                              EJECUTAR_VUELTA_PATRULLA, SINCRONIZAR_PRESETS).
    3. Patrulla activa     -> vuelta tras vuelta mientras siga activa.
                              Al desactivarse, la cámara vuelve a su preset
                              inicial y se queda quieta.

- Una vuelta: ir al preset inicial -> pasos en orden -> volver al inicial.
- Las esperas se cortan en cuanto cambia algo que obliga a parar.
- Tras un reinicio no se recuerda nada: se pregunta y se ajusta a la API.

Solo usa la biblioteca estándar (se prueba en el CI sin PySide6).
"""

from __future__ import annotations

import json
import logging
import threading
import time

from collections import deque
from typing import Callable

from meteocam.agente.api import ClienteApiAgente, ConflictoComando, ErrorApi
from meteocam.agente.configuracion import ConfiguracionAgente
from meteocam.agente.reolink import ClienteReolink, ErrorReolink


logger = logging.getLogger("meteocam.agente")


MOVER_A_PRESET = "MOVER_A_PRESET"
ESPERAR = "ESPERAR"
ZOOM = "ZOOM"

POSICIONAR_PRESET = "POSICIONAR_PRESET"
EJECUTAR_VUELTA_PATRULLA = "EJECUTAR_VUELTA_PATRULLA"
SINCRONIZAR_PRESETS = "SINCRONIZAR_PRESETS"

MODO_ACTIVA = "activa"
MODO_ORDEN = "orden"

SEGUNDOS_TRAS_ERROR_CAMARA = 30.0
INTENTOS_INFORMAR = 5
SEGUNDOS_ENTRE_INTENTOS_INFORMAR = 5.0


class Interrumpida(Exception):
    """Algo obliga a dejar lo que se estaba haciendo."""

    def __init__(self, motivo: str):
        super().__init__(motivo)
        self.motivo = motivo


def _firma(patrulla: dict | None) -> str | None:
    """Identifica una patrulla con sus pasos: si cambia algo, cambia la firma."""

    if not patrulla:
        return None
    return json.dumps(patrulla, sort_keys=True, default=str)


# ----------------------------------------------------------------------
# Una cámara
# ----------------------------------------------------------------------


class EjecutorCamara:
    """Ejecuta, de forma síncrona, el trabajo de una cámara lógica."""

    def __init__(
        self,
        camara_id: int,
        api: ClienteApiAgente,
        camara: ClienteReolink,
        configuracion: ConfiguracionAgente,
        parar: threading.Event,
    ) -> None:
        self.camara_id = camara_id
        self._api = api
        self._camara = camara
        self._config = configuracion
        self._parar = parar

        self._cerrojo = threading.Lock()
        self._estado: dict | None = None
        self._despertar = threading.Event()

        self._hechos: deque[int] = deque(maxlen=500)
        self._posicion: str | None = None
        self._ultima_patrulla: dict | None = None
        self._ultimo_error: str | None = None

        self._hilo = threading.Thread(
            target=self._bucle,
            name=f"meteocam-camara-{camara_id}",
            daemon=True,
        )

    # -- comunicación con el hilo de consulta ---------------------------

    def iniciar(self) -> None:
        self._hilo.start()

    def unir(self, segundos: float) -> None:
        self._hilo.join(segundos)

    @property
    def posicion(self) -> str | None:
        """Último preset al que se mandó la cámara (None si no se sabe)."""

        return self._posicion

    def actualizar(self, estado: dict | None) -> None:
        with self._cerrojo:
            self._estado = estado
        self._despertar.set()

    def _foto(self) -> dict | None:
        with self._cerrojo:
            return self._estado

    # -- utilidades -----------------------------------------------------

    @property
    def _canal(self) -> int:
        estado = self._foto() or {"camara_id": self.camara_id}
        return self._config.canal_para(estado)

    def _orden_nueva(self, estado: dict) -> dict | None:
        comando = estado.get("comando")
        if comando and comando.get("id") not in self._hechos:
            return comando
        return None

    def _comprobar(self, modo: str, firma: str | None) -> None:
        """Lanza Interrumpida si hay que dejar lo que se está haciendo."""

        if self._parar.is_set():
            raise Interrumpida("el servicio se detiene")

        estado = self._foto()
        if estado is None:
            raise Interrumpida("la cámara ya no está asignada a este agente")
        if estado.get("timelapse_en_curso"):
            raise Interrumpida("timelapse en curso")

        if modo == MODO_ACTIVA:
            if self._orden_nueva(estado):
                raise Interrumpida("orden pendiente")
            if _firma(estado.get("patrulla_activa")) != firma:
                raise Interrumpida("la patrulla activa ha cambiado")

    def _esperar(self, segundos: float, modo: str, firma: str | None) -> None:
        """Espera interrumpible: se corta si cambia algo importante."""

        fin = time.monotonic() + max(0.0, float(segundos))
        while True:
            self._comprobar(modo, firma)
            quedan = fin - time.monotonic()
            if quedan <= 0:
                return
            self._despertar.wait(min(quedan, 1.0))
            self._despertar.clear()

    def _ir(self, preset: str, velocidad: int | None, modo: str, firma: str | None) -> None:
        self._comprobar(modo, firma)
        self._camara.ir_a_preset(self._canal, preset, velocidad)
        self._posicion = str(preset)
        # ToPos responde al aceptar la orden; se da tiempo a que llegue.
        self._esperar(self._config.segundos_llegada, modo, firma)

    def _registrar_error(self, mensaje: str) -> None:
        if mensaje != self._ultimo_error:
            logger.warning("Cámara %s: %s", self.camara_id, mensaje)
            self._ultimo_error = mensaje

    # -- vuelta -------------------------------------------------------------

    def _vuelta(self, patrulla: dict, modo: str) -> list[str]:
        """Da una vuelta completa. Devuelve los avisos (pasos ignorados)."""

        firma = _firma(patrulla) if modo == MODO_ACTIVA else None
        defecto = patrulla.get("velocidad_defecto")
        inicial = str(patrulla["preset_inicial"])
        avisos: list[str] = []

        self._ir(inicial, defecto, modo, firma)

        for paso in sorted(patrulla.get("pasos") or [], key=lambda p: p.get("posicion", 0)):
            tipo = paso.get("tipo")

            if tipo == MOVER_A_PRESET and paso.get("preset") is not None:
                self._ir(str(paso["preset"]), paso.get("velocidad") or defecto, modo, firma)

            elif tipo == ESPERAR:
                self._esperar(paso.get("segundos") or 0, modo, firma)

            elif tipo == ZOOM:
                # Pendiente de comprobar que la OMVI admite zoom por la API
                # (docs/patrullas.md, sección 3): se ignora y se anota.
                avisos.append(f"paso {paso.get('posicion')}: ZOOM ignorado (sin comprobar en la cámara)")

            else:
                avisos.append(f"paso {paso.get('posicion')}: tipo {tipo!r} no admitido")

        self._ir(inicial, defecto, modo, firma)
        return avisos

    # -- órdenes ---------------------------------------------------------

    def _informar(self, comando_id: int, **datos) -> None:
        for intento in range(1, INTENTOS_INFORMAR + 1):
            try:
                self._api.resultado(comando_id, **datos)
                return
            except ConflictoComando as error:
                logger.warning("Orden %s: la API no aceptó el resultado (%s).", comando_id, error)
                return
            except ErrorApi as error:
                logger.warning(
                    "Orden %s: no se pudo informar del resultado (intento %s de %s): %s",
                    comando_id, intento, INTENTOS_INFORMAR, error,
                )
                if self._parar.wait(SEGUNDOS_ENTRE_INTENTOS_INFORMAR):
                    return
        # La API la pasará a ERROR («abandonada») pasado su plazo.

    def _ejecutar_orden(self, comando: dict) -> None:
        comando_id = int(comando["id"])
        tipo = comando.get("tipo")
        self._hechos.append(comando_id)

        try:
            self._api.reclamar(comando_id)
        except ConflictoComando as error:
            logger.info("Orden %s (%s) no reclamada: %s", comando_id, tipo, error)
            return
        except ErrorApi as error:
            # Se reintentará en la siguiente consulta si sigue pendiente.
            self._hechos.remove(comando_id)
            self._registrar_error(f"no se pudo reclamar la orden {comando_id}: {error}")
            self._parar.wait(self._config.intervalo_consulta)
            return

        logger.info("Cámara %s: orden %s (%s) en marcha.", self.camara_id, comando_id, tipo)
        canal = self._canal

        try:
            if tipo == POSICIONAR_PRESET:
                if comando.get("preset") is None:
                    raise ValueError("la orden no trae preset")
                self._ir(str(comando["preset"]), comando.get("velocidad"), MODO_ORDEN, None)
                self._informar(
                    comando_id,
                    correcto=True,
                    resultado={"canal": canal, "preset": str(comando["preset"])},
                )

            elif tipo == EJECUTAR_VUELTA_PATRULLA:
                patrulla = comando.get("patrulla")
                if not patrulla:
                    raise ValueError("la orden no trae la patrulla")
                avisos = self._vuelta(patrulla, MODO_ORDEN)
                resultado = {"canal": canal, "patrulla": patrulla.get("codigo")}
                if avisos:
                    resultado["avisos"] = avisos
                self._informar(comando_id, correcto=True, resultado=resultado)

            elif tipo == SINCRONIZAR_PRESETS:
                presets = self._camara.presets(canal)
                resultado = {"canal": canal, "total": len(presets)}
                try:
                    info = self._camara.informacion_dispositivo()
                    resultado["dispositivo"] = {
                        clave: info.get(clave)
                        for clave in ("model", "firmVer", "hardVer", "serial", "channelNum", "name")
                        if clave in info
                    }
                except ErrorReolink as error:
                    resultado["dispositivo_error"] = str(error)
                self._informar(
                    comando_id,
                    correcto=True,
                    resultado=resultado,
                    presets=[
                        {"identificador": p.identificador, "nombre": p.nombre}
                        for p in presets
                    ],
                )

            else:
                self._informar(
                    comando_id,
                    correcto=False,
                    mensaje_error=f"Orden {tipo!r} no admitida por esta versión de MeteoCam.",
                )
                return

            logger.info("Cámara %s: orden %s (%s) completada.", self.camara_id, comando_id, tipo)
            self._ultimo_error = None

        except Interrumpida as motivo:
            logger.info("Cámara %s: orden %s interrumpida: %s.", self.camara_id, comando_id, motivo.motivo)
            self._informar(comando_id, correcto=False, mensaje_error=f"Interrumpida: {motivo.motivo}.")
        except (ErrorReolink, ValueError) as error:
            logger.warning("Cámara %s: orden %s con error: %s", self.camara_id, comando_id, error)
            self._informar(comando_id, correcto=False, mensaje_error=str(error))

    # -- bucle -----------------------------------------------------------

    def _bucle(self) -> None:
        while not self._parar.is_set():
            try:
                self._paso_del_bucle()
            except Interrumpida:
                continue
            except ErrorReolink as error:
                self._registrar_error(str(error))
                self._parar.wait(SEGUNDOS_TRAS_ERROR_CAMARA)
            except Exception:
                logger.exception("Cámara %s: error inesperado; se reintenta.", self.camara_id)
                self._parar.wait(SEGUNDOS_TRAS_ERROR_CAMARA)

    def _paso_del_bucle(self) -> None:
        estado = self._foto()

        if estado is None:
            self._despertar.wait(1.0)
            self._despertar.clear()
            return

        # 1. Timelapse en curso: la cámara queda quieta.
        if estado.get("timelapse_en_curso"):
            if self._ultima_patrulla is not None:
                logger.info("Cámara %s: patrulla en pausa por timelapse.", self.camara_id)
                self._ultima_patrulla = None
            preset = estado.get("preset_timelapse")
            if preset is not None and self._posicion != str(preset):
                logger.info("Cámara %s: al preset %s del timelapse.", self.camara_id, preset)
                self._camara.ir_a_preset(self._canal, preset)
                self._posicion = str(preset)
            self._despertar.wait(1.0)
            self._despertar.clear()
            return

        # 2. Orden pendiente.
        comando = self._orden_nueva(estado)
        if comando:
            self._ejecutar_orden(comando)
            return

        # 3. Patrulla activa en bucle.
        patrulla = estado.get("patrulla_activa")
        if patrulla:
            if _firma(patrulla) != _firma(self._ultima_patrulla):
                logger.info(
                    "Cámara %s: patrulla activa %s en marcha.",
                    self.camara_id, patrulla.get("codigo"),
                )
            self._ultima_patrulla = patrulla
            avisos = self._vuelta(patrulla, MODO_ACTIVA)
            if avisos:
                self._registrar_error("; ".join(avisos))
            else:
                self._ultimo_error = None
            return

        # Sin patrulla: si se acaba de desactivar, vuelve a su preset inicial.
        if self._ultima_patrulla is not None:
            anterior = self._ultima_patrulla
            self._ultima_patrulla = None
            logger.info(
                "Cámara %s: patrulla %s desactivada; vuelve al preset inicial %s.",
                self.camara_id, anterior.get("codigo"), anterior.get("preset_inicial"),
            )
            self._camara.ir_a_preset(
                self._canal, anterior["preset_inicial"], anterior.get("velocidad_defecto")
            )
            self._posicion = str(anterior["preset_inicial"])

        self._despertar.wait(1.0)
        self._despertar.clear()


# ----------------------------------------------------------------------
# Agente completo
# ----------------------------------------------------------------------


class AgenteCamaras:
    """Hilo de consulta a la API y un ejecutor por cámara."""

    def __init__(
        self,
        configuracion: ConfiguracionAgente,
        *,
        api: ClienteApiAgente | None = None,
        camara: ClienteReolink | None = None,
        parar: threading.Event | None = None,
        fabrica_ejecutor: Callable[..., EjecutorCamara] = EjecutorCamara,
    ) -> None:
        self._config = configuracion
        self._parar = parar or threading.Event()
        self._api = api or ClienteApiAgente(
            configuracion.api_url,
            configuracion.clave_agente,
            configuracion.agente,
        )
        self._camara = camara or ClienteReolink(
            configuracion.camera_host,
            configuracion.camera_username,
            configuracion.camera_password,
            puerto=configuracion.camera_http_port,
            https=configuracion.camera_https,
        )
        self._fabrica = fabrica_ejecutor
        self._ejecutores: dict[int, EjecutorCamara] = {}
        self._conectado: bool | None = None
        self._hilo = threading.Thread(target=self._bucle, name="meteocam-agente", daemon=True)

    @property
    def ejecutores(self) -> dict[int, EjecutorCamara]:
        return self._ejecutores

    def iniciar(self) -> None:
        logger.info(
            "Agente de órdenes de cámara en marcha (agente %s, API %s).",
            self._config.agente, self._config.api_url,
        )
        self._hilo.start()

    def detener(self, segundos: float = 10.0) -> None:
        self._parar.set()
        self._hilo.join(segundos)
        for ejecutor in self._ejecutores.values():
            ejecutor.unir(segundos)

    def consultar_una_vez(self) -> float:
        """Pide el trabajo y lo reparte. Devuelve los segundos hasta la siguiente."""

        intervalo = self._config.intervalo_consulta
        posiciones = {
            camara_id: ejecutor.posicion
            for camara_id, ejecutor in self._ejecutores.items()
            if getattr(ejecutor, "posicion", None) is not None
        }
        try:
            trabajo = self._api.trabajo(posiciones)
        except ErrorApi as error:
            if self._conectado is not False:
                logger.warning("Agente: sin respuesta de la API: %s", error)
            self._conectado = False
            # Tras un fallo se espera algo más, sin pasar de 30 s.
            return min(30.0, intervalo * 3)

        if self._conectado is not True:
            camaras = trabajo.get("camaras") or []
            logger.info(
                "Agente: conectado con la API; %s cámara(s) asignadas a «%s».",
                len(camaras), self._config.agente,
            )
            if not camaras:
                logger.warning(
                    "Agente: la API no asigna ninguna cámara a «%s». "
                    "Revisa camara.ide_agente y que estén habilitadas.",
                    self._config.agente,
                )
        self._conectado = True

        vistas = set()
        for camara in trabajo.get("camaras") or []:
            camara_id = int(camara["camara_id"])
            vistas.add(camara_id)
            ejecutor = self._ejecutores.get(camara_id)
            if ejecutor is None:
                ejecutor = self._fabrica(camara_id, self._api, self._camara, self._config, self._parar)
                self._ejecutores[camara_id] = ejecutor
                ejecutor.actualizar(camara)
                ejecutor.iniciar()
            else:
                ejecutor.actualizar(camara)

        for camara_id, ejecutor in self._ejecutores.items():
            if camara_id not in vistas:
                ejecutor.actualizar(None)

        segundos = trabajo.get("intervalo_consulta_segundos")
        if isinstance(segundos, (int, float)) and segundos > 0:
            intervalo = float(segundos)
        return intervalo

    def _bucle(self) -> None:
        while not self._parar.is_set():
            try:
                espera = self.consultar_una_vez()
            except Exception:
                logger.exception("Agente: error inesperado en la consulta.")
                espera = 30.0
            self._parar.wait(espera)


# Fin archivo: src/meteocam/agente/ejecutor.py
