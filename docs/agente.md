# Agente de órdenes de cámara

Parte de MeteoCam que, desde el mini PC de la estación, **mueve la cámara PTZ** según lo que
diga la API: patrulla activa en bucle, vueltas sueltas o programadas, ir a un preset y leer los
presets de la cámara. El diseño completo está en `docs/patrullas.md` (secciones 4, 5, 7 y 11) de
`api-meteoarchidona`; aquí, cómo lo hace MeteoCam.

Va **dentro del servicio MeteoCamPublisher**, junto al directo, pero es independiente: si no está
configurado, si la API no responde o si la cámara falla, el directo sigue igual.

## Qué hace

```
API (VPS) ◄── cada 5 s: GET /agente/camaras/trabajo ── hilo de consulta
                                                          │ reparte
                                                          ▼
                                        un hilo por cámara (síncrono, paso a paso)
                                                          │ PtzCtrl ToPos / GetPtzPreset
                                                          ▼
                                                  cámara Reolink (red local)
```

Prioridades en cada cámara:

| Prioridad | Qué | Qué hace MeteoCam |
| --- | --- | --- |
| 1 | Timelapse en curso | No mueve la cámara (solo la lleva al preset del timelapse si lo tiene) y pausa la patrulla |
| 2 | Orden pendiente | La reclama, la ejecuta e informa del resultado |
| 3 | Patrulla activa | Vuelta tras vuelta; al desactivarla, vuelve al preset inicial y se queda quieta |

Órdenes que entiende:

| Orden | Qué hace |
| --- | --- |
| `SINCRONIZAR_PRESETS` | Lee los presets activos de la cámara (`GetPtzPreset`) y se los manda a la API, que los guarda en `camara_preset`. Añade modelo y firmware (`GetDevInfo`) al resultado |
| `POSICIONAR_PRESET` | Lleva la cámara a un preset |
| `EJECUTAR_VUELTA_PATRULLA` | Una vuelta: preset inicial → pasos → preset inicial |
| Otras (`CAPTURA_PUNTUAL`…) | Se informan como error «no admitida por esta versión» |

Pasos de una patrulla: `MOVER_A_PRESET` y `ESPERAR`. **`ZOOM` se ignora y se anota** en el
resultado hasta comprobar que la OMVI lo admite por la API.

Detalles:

- `ToPos` responde al aceptar la orden, no al llegar: tras cada movimiento se esperan
  `segundos_llegada` (5 s por defecto).
- Las esperas se cortan en cuanto llega una orden, empieza un timelapse o cambia la patrulla.
  Una orden no espera a que acabe un `ESPERAR` largo.
- Una vuelta mandada como orden no la corta otra orden, solo un timelapse.
- Si la API no responde, se reintenta cada 15 s (con 5 s de intervalo normal) y se anota una sola
  vez en el registro, no cada vez.
- Tras reiniciarse no recuerda nada: pregunta y se ajusta a la API.
- La sesión con la cámara (token) se renueva sola.

## Configuración: `C:\ProgramData\MeteoCam\agente.json`

```json
{
  "agente": "el valor de camara.ide_agente de las cámaras de la estación",
  "clave_agente": "la de METEOARCHIDONA_CLAVE_AGENTE_METEOCAM del servidor",
  "api_url": "https://meteoarchidona.com/api"
}
```

La IP, el usuario y la contraseña de la cámara salen de `publisher.json`. Campos opcionales:

| Campo | Por defecto | Para qué |
| --- | --- | --- |
| `canal_ptz` | `1` | Canal Reolink de la PTZ (0 = panorámica, 1 = específica, **por confirmar** con `comprobar-agente`) |
| `canales` | `{}` | Canal por vista o por id de cámara, si hiciera falta: `{"ptz": 1}` |
| `segundos_llegada` | `5` | Espera tras cada movimiento |
| `camera_http_port` | `80` | Puerto HTTP de la cámara |
| `camera_https` | `false` | Usar HTTPS con la cámara |

También se admiten `agente` y `clave_agente` dentro de `publisher.json`. Sin ellos, el agente no
arranca y el registro dice `Agente de órdenes de cámara desactivado: …`.

El instalador copia `agente.json` si está **junto a `MeteoCam-Setup.exe`** (como
`publisher.json`); si no hay ninguno, el asistente lo pide (se puede dejar vacío) y lo deja legible
solo por SYSTEM y Administradores.

## Comprobar en el mini PC (no mueve la cámara)

En PowerShell como administrador:

```
& "C:\Program Files\MeteoCam\Publisher\MeteoCamPublisher.exe" comprobar-agente
```

Revisa, por orden, la configuración, la sesión con la cámara (modelo y firmware), los presets de
los canales 0 y 1 (para confirmar cuál es la PTZ) y qué cámaras le asigna la API. Acaba con
`RESULTADO: todo correcto` o explicando qué falla.

En el registro del servicio (`C:\ProgramData\MeteoCam\logs\publisher.log`) aparecen
`Agente: conectado con la API; N cámara(s) asignadas…` y cada orden ejecutada.

## Código

| Pieza | Qué hace |
| --- | --- |
| `src/meteocam/agente/reolink.py` | Cliente HTTP de la cámara: Login, GetDevInfo, GetPtzPreset, PtzCtrl |
| `src/meteocam/agente/api.py` | Cliente de `/agente/camaras` con la cabecera `X-Clave-Agente` |
| `src/meteocam/agente/configuracion.py` | Lee `agente.json` y `publisher.json` |
| `src/meteocam/agente/ejecutor.py` | Hilo de consulta y un ejecutor por cámara |
| `src/meteocam/agente/diagnostico.py` | `comprobar-agente` |
| `tests/test_agente.py` | Pruebas con una cámara Reolink falsa y una API falsa |

Todo con biblioteca estándar: se prueba sin PySide6 ni av.

## Pendiente

- Confirmar en la estación el canal de la PTZ y que los números de preset de la cámara coinciden
  con los que guarda la API.
- Zoom de la OMVI por la API (`GetZoomFocus`/`StartZoomFocus`), sin comprobar.
- `CAPTURA_PUNTUAL`, hasta decidir adónde se sube la imagen.
