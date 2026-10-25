# Catálogo de comandos de cámara (Reolink)

Documento de trabajo para el control de la cámara de Los Llanos desde MeteoCam.

Reúne **todos los comandos que expone la API HTTP de Reolink** y, para cada uno, si
interesa a MeteoArchidona, qué riesgo tiene y si se ha comprobado en la cámara real.
Es la base para decidir qué órdenes nuevas se añaden a la tabla `comando_camara` de
`api-meteoarchidona` y qué tiene que implementar el adaptador `ReolinkCamera` (Sprint 7.7
de `docs/arquitectura.md`).

> **Nada de este catálogo está comprobado todavía en la OMVI 3i salvo lo marcado ✅.**
> La lista de comandos viene de la guía oficial *Reolink Camera HTTP API User Guide*
> (versiones 7 y 8) y de librerías que la implementan. Que un comando exista en la guía
> no garantiza que este modelo lo admita: eso lo dirá `GetAbility` y el script
> `scripts/investigar-reolink.ps1` (ver al final).

## 1. Lo que ya sabemos de la cámara (comprobado el 2026-10-25)

| Dato | Valor | Estado |
| --- | --- | --- |
| Modelo | Reolink OMVI 3i PoE (panorámica + PT) | ✅ |
| Web de la cámara | `http://192.168.1.250`, interfaz «Reolink 2.5.2», con *Channels* 1 y 2 y *Stitch Settings* | ✅ |
| IP | **Fija** 192.168.1.250, máscara 255.255.255.0, puerta de enlace y DNS 192.168.1.1 (antes DHCP: cambió de .100 a .102) | ✅ |
| Conexión | Cable al gateway PoE → router 4G | ✅ |
| RTSP panorámica | `rtsp://…:554/Preview_01_sub` | ✅ en producción |
| RTSP vista específica (PT) | `rtsp://…:554/Preview_02_sub` | ✅ en producción |
| Aplicación Reolink | Accede por UID (P2P), no depende de la IP. **No** permite poner IP fija en este modelo: hay que usar la web | ✅ |
| Saturación | Con la web y la app abiertas a la vez que las dos publicaciones, el RTSP dio errores «Invalid data». Las Reolink admiten pocos espectadores simultáneos | ⚠️ observado, por confirmar |
| Presets PT | Salinas, Jibalto, Trabuco, Rosario (según `camara_preset` de la API) | por confirmar ids |

## 2. Cómo se habla con la API de Reolink

- **Dirección:** `http://<ip>/cgi-bin/api.cgi?cmd=<Comando>&token=<token>`. Algunos firmwares
  responden también en `/api.cgi`.
- **Método:** `POST` con un **array JSON** de órdenes: `[{"cmd": "...", "action": 0, "param": {...}}]`.
  `action: 1` en los `Get…` devuelve además los rangos y valores iniciales (útil para investigar).
- **Sesión:** `Login` con `{"User": {"Version": "0", "userName": "...", "password": "..."}}`
  devuelve `Token.name` válido `leaseTime` segundos (3600). Se cierra con `Logout`.
  Alternativa sin sesión: `&user=…&password=…` en cada petición (no recomendable: la
  contraseña viaja en la URL).
- **Respuesta:** `code: 0` correcto; si no, `error.rspCode` y `error.detail`.
  Ejemplos habituales: `-6` sin permiso/login, `-9` no admitido, `-4` parámetro erróneo.
- **Canales:** numerados desde 0. **Por confirmar** qué canal es la panorámica y cuál la PT
  (lo más probable: 0 = panorámica, 1 = PT, coherente con `Preview_01`/`Preview_02`).
- **Capacidades:** `GetAbility` devuelve, por canal (`abilityChn`), qué funciones existen.
  `ver = 0` → no admitida. `permit` indica lectura/escritura. **Es la fuente de verdad para
  activar o no cada función en MeteoCam** (principio de `docs/arquitectura.md`: nunca
  suponer capacidades por el nombre del modelo).
- **Seguridad:** la API solo se usa desde MeteoCam dentro de la red local. La cámara no se
  expone a Internet y las credenciales salen de `C:\ProgramData\MeteoCam\publisher.json`.

## 3. Tres niveles de «comando»

```
MeteoArchidona (web/admin)          tabla comando_camara  (orden de alto nivel)
        │                            p. ej. POSICIONAR_PRESET preset=Salinas
        ▼
MeteoCam (mini PC)                   operación del adaptador ReolinkCamera
        │                            p. ej. mover_a_preset(canal=1, id=3)
        ▼
Cámara Reolink                       comando de la API HTTP
                                     PtzCtrl {channel:1, op:"ToPos", id:3, speed:32}
```

La web nunca habla con la cámara: deja la orden en `comando_camara`, MeteoCam la reclama,
la traduce a uno o varios comandos Reolink, la ejecuta y guarda el resultado.

### Órdenes que ya existen en `comando_camara` y su traducción

| Orden MeteoArchidona | Comandos Reolink | Notas |
| --- | --- | --- |
| `POSICIONAR_PRESET` | `PtzCtrl` op `ToPos`, `id` del preset | `id` 0–63 en `PtzCtrl`/`GetPtzPreset`. Por confirmar si el id de la web coincide |
| `CAPTURA_PUNTUAL` | `Snap` (`channel`, `rs` aleatorio) → JPG | Alternativa: fotograma del HLS del VPS, como hace hoy el timelapse |
| `ACTIVAR_PATRULLA` | Secuencia propia de MeteoCam: varios `ToPos` con esperas | La arquitectura descarta la patrulla nativa (`StartPatrol`) para el recorrido meteorológico |
| `DETENER_PATRULLA` | MeteoCam deja de enviar `ToPos`; opcional `PtzCtrl` `Stop` | No usa `StopPatrol` nativo |
| `SINCRONIZAR_PRESETS` | `GetPtzPreset` (canal PT) | Solo marcar ausentes si la lectura fue completa y correcta |

## 4. Catálogo completo

Columnas:
- **Interés**: 🟢 alto (lo usaremos) · 🟡 medio (útil para diagnóstico o más adelante) ·
  ⚪ bajo/ninguno.
- **Riesgo**: L = solo lectura · E = cambia configuración · ⛔ destructivo o puede dejar la
  cámara inaccesible. **Los ⛔ no se implementan sin orden expresa de José.**
- **Estado**: ⏳ pendiente de comprobar en la OMVI · ✅ comprobado · ❌ no admitido.

### 4.1 Sesión y seguridad

| Comando | Qué hace | Interés | Riesgo | Estado |
| --- | --- | --- | --- | --- |
| `Login` / `Logout` | Abre/cierra sesión y obtiene token | 🟢 | L | ⏳ |
| `GetUser` | Lista usuarios | 🟡 (diagnóstico) | L | ⏳ |
| `AddUser` / `ModifyUser` / `DelUser` | Gestión de usuarios | 🟡 crear un usuario solo para MeteoCam | ⛔ | ⏳ |
| `GetOnline` / `Disconnect` | Quién está conectado / expulsar | 🟡 diagnosticar saturación de espectadores | L / E | ⏳ |
| `GetSysCfg` / `SetSysCfg` | Bloqueo de inicio de sesión, etc. | ⚪ | L / E | ⏳ |

### 4.2 Sistema e identificación

| Comando | Qué hace | Interés | Riesgo | Estado |
| --- | --- | --- | --- | --- |
| `GetAbility` | Capacidades por canal | 🟢 detección de capacidades | L | ⏳ |
| `GetDevInfo` | Modelo, firmware, nº serie, canales | 🟢 rellena `camara.Modelo/Firmware/NumeroSerie` | L | ⏳ |
| `GetChannelstatus` | Estado de cada canal | 🟢 en línea / fuera de línea por vista | L | ⏳ |
| `GetDevName` / `SetDevName` | Nombre del dispositivo | 🟡 | L / E | ⏳ |
| `GetTime` / `SetTime` | Fecha, hora, zona, horario de verano | 🟢 la hora va impresa en la imagen | L / E | ⏳ |
| `GetNtp` / `SetNtp` | Servidor de hora | 🟢 verificar que la hora no deriva | L / E | ⏳ |
| `GetHddInfo` | Estado de la microSD | 🟡 | L | ⏳ |
| `GetAutoMaint` / `SetAutoMaint` | Reinicio automático programado | 🟡 | L / E | ⏳ |
| `Reboot` | Reiniciar la cámara | 🟢 recuperación remota (ya se hace a mano desde la app) | ⛔ (corta el directo 1–2 min) | ⏳ |
| `CheckFirmware` / `UpgradeOnline` / `UpgradeStatus` / `UpgradePrepare` / `Upgrade` | Actualización de firmware | 🟡 solo consultar | ⛔ | ⏳ |
| `GetAutoUpgrade` / `SetAutoUpgrade` | Actualización automática | 🟡 conviene desactivada | L / E | ⏳ |
| `Restore` | Restablecer de fábrica | ⚪ | ⛔ | — |
| `Format` | Formatear la microSD | ⚪ | ⛔ | — |

### 4.3 Red

| Comando | Qué hace | Interés | Riesgo | Estado |
| --- | --- | --- | --- | --- |
| `GetLocalLink` | IP, máscara, puerta de enlace, DNS, DHCP/estática | 🟢 vigilar que sigue en IP fija | L | ⏳ |
| `SetLocalLink` | Cambia la configuración de red | ⚪ | ⛔ una IP mal puesta deja la cámara inaccesible | — |
| `GetNetPort` / `SetNetPort` | Puertos HTTP/HTTPS/RTSP/RTMP/ONVIF y si están activos | 🟢 lectura | L / ⛔ | ⏳ |
| `GetRtspUrl` | URLs RTSP oficiales por canal | 🟢 confirmar rutas y canales | L | ⏳ |
| `GetUpnp` / `SetUpnp` | UPnP | 🟡 debe seguir desactivado | L / E | ⏳ |
| `GetP2p` / `SetP2p` | Acceso P2P (UID) para la app | 🟡 | L / ⛔ | ⏳ |
| `GetDdns` / `SetDdns` | DNS dinámico | ⚪ | L / E | ⏳ |
| `GetWifi` / `SetWifi` / `ScanWifi` / `TestWifi` / `GetWifiSignal` | Wi-Fi (la OMVI va por cable) | ⚪ | L / E | ⏳ |
| `GetEmail(V20)` / `SetEmail(V20)` / `TestEmail` | Avisos por correo (hoy activado en la app) | 🟡 | L / E | ⏳ |
| `GetFtp(V20)` / `SetFtp(V20)` / `TestFtp` | Subida por FTP | ⚪ | L / E | ⏳ |
| `GetPush(V20)` / `SetPush(V20)` / `GetPushCfg` / `SetPushCfg` | Notificaciones push | ⚪ | L / E | ⏳ |
| `GetCertificateInfo` / `CertificateClear` | Certificado HTTPS | ⚪ | L / E | ⏳ |

### 4.4 Imagen y vídeo

| Comando | Qué hace | Interés | Riesgo | Estado |
| --- | --- | --- | --- | --- |
| `GetEnc` / `SetEnc` | Resolución, fps, bitrate, códec de los streams principal y secundario | 🟢 calidad del directo y del timelapse | L / E | ⏳ |
| `Snap` | Foto JPG del canal (`channel`, `rs`) | 🟢 `CAPTURA_PUNTUAL`, fotos en alta resolución para timelapse | L | ⏳ |
| `GetIsp` / `SetIsp` | Día/noche (`DayNight`), exposición, antiparpadeo, contraluz, balance de blancos, antiniebla, nitidez | 🟢 cielo nocturno, sol de frente, niebla | L / E | ⏳ |
| `GetImage` / `SetImage` | Brillo, contraste, saturación, tono | 🟡 | L / E | ⏳ |
| `GetOsd` / `SetOsd` | Texto en imagen: nombre («MeteoCam Los Llanos-1»), fecha/hora y posición | 🟡 | L / E | ⏳ |
| `GetMask` / `SetMask` | Máscaras de privacidad | 🟡 tapar casas vecinas | L / E | ⏳ |
| `GetCrop` / `SetCrop` | Recorte | ⚪ | L / E | ⏳ |
| `GetStitch` / `SetStitch` | Unión de las dos lentes de la panorámica (OMVI) | 🟡 se ve una costura con el sol | L / E | ⏳ |

### 4.5 PT (movimiento), presets, patrulla, zoom

| Comando | Qué hace | Interés | Riesgo | Estado |
| --- | --- | --- | --- | --- |
| `PtzCtrl` | Mover y parar. Operaciones: `Left`, `Right`, `Up`, `Down`, `LeftUp`, `LeftDown`, `RightUp`, `RightDown`, `Stop`, `ZoomInc`, `ZoomDec`, `FocusInc`, `FocusDec`, `IrisInc`, `IrisDec`, `Auto`, `ToPos` (ir a preset), `StartPatrol`, `StopPatrol`. Velocidad 1–64 (32 media) | 🟢 | E (mueve la cámara) | ⏳ |
| `GetPtzPreset` | Lista de presets (`id` 0–63, `name` ≤ 31 caracteres, `enable`) | 🟢 `SINCRONIZAR_PRESETS` | L | ⏳ |
| `SetPtzPreset` | Crear/renombrar/borrar preset (guarda la posición actual) | 🟡 desde Administración | E | ⏳ |
| `GetPtzPatrol` / `SetPtzPatrol` | Patrulla nativa (OMVI: 1 ruta, 4 puntos) | 🟡 | L / E | ⏳ |
| `GetPtzGuard` / `SetPtzGuard` | Posición de guardia y vuelta automática tras inactividad | 🟢 decidir dónde descansa la PT; puede interferir con nuestras órdenes | L / E | ⏳ |
| `GetZoomFocus` / `StartZoomFocus` | Leer/fijar zoom (`ZoomPos`) y enfoque (`FocusPos`) | 🟡 la PT de la OMVI tiene zoom digital: puede no aplicar | L / E | ⏳ |
| `GetAutoFocus` / `SetAutoFocus` | Autoenfoque | ⚪ probablemente no aplica | L / E | ⏳ |
| `GetPtzCheckState` / `PtzCheck` | Estado de calibración / recalibrar el PT | 🟡 si la PT pierde la referencia | L / E | ⏳ |
| `GetPtzSerial` / `SetPtzSerial`, `GetPtzTattern` / `SetPtzTattern` | Puerto serie PTZ, trazados | ⚪ | L / E | ⏳ |
| *Pinpoint, SyncTrack, encuadre automático* | Funciones de la app Reolink | 🟡 | — | ⏳ no aparecen en la guía HTTP: probablemente solo app |

### 4.6 Luces

| Comando | Qué hace | Interés | Riesgo | Estado |
| --- | --- | --- | --- | --- |
| `GetIrLights` / `SetIrLights` | Infrarrojos `Auto`/`On`/`Off` | 🟢 los IR reflejan en niebla/lluvia y no dejan ver el cielo nocturno | L / E | ⏳ |
| `GetWhiteLed` / `SetWhiteLed` | Foco blanco (si lo tiene; la app muestra «Luz») | 🟡 | L / E | ⏳ |
| `GetPowerLed` / `SetPowerLed` | LED de estado | ⚪ | L / E | ⏳ |

### 4.7 Grabación, alarmas e IA

| Comando | Qué hace | Interés | Riesgo | Estado |
| --- | --- | --- | --- | --- |
| `GetRec(V20)` / `SetRec(V20)` | Grabación en microSD (hoy «Encendido» en la app) | 🟡 | L / E | ⏳ |
| `Search` / `Download` / `Playback` / `NvrDownload` | Buscar y bajar grabaciones de la microSD | 🟡 recuperar huecos del timelapse | L | ⏳ |
| `GetMdState` / `GetMdAlarm` / `SetMdAlarm` | Detección de movimiento | ⚪ | L / E | ⏳ |
| `GetAiState` / `GetAiCfg` / `SetAiCfg` | Detección de personas/vehículos/animales | ⚪ | L / E | ⏳ |
| `GetAlarm` / `SetAlarm`, `GetAudioAlarm(V20)` / `SetAudioAlarm(V20)`, `GetBuzzerAlarmV20` / `SetBuzzerAlarmV20`, `AudioAlarmPlay` | Alarmas y sirena | ⚪ | L / E | ⏳ |
| `GetAiAlarm` / `SetAiAlarm` / `SetAlarmArea` | Zonas de alarma IA | ⚪ | L / E | ⏳ |

## 5. Órdenes nuevas candidatas para `comando_camara`

**Propuesta, no decidida ni implementada.** Añadir un tipo exige cambiar el `CHECK` de la
tabla en `api-meteoarchidona` (migración) y el adaptador en MeteoCam. José elige cuáles.

| Orden propuesta | Comandos Reolink | Para qué |
| --- | --- | --- |
| `LEER_ESTADO_CAMARA` | `GetDevInfo`, `GetChannelstatus`, `GetLocalLink`, `GetTime`, `GetHddInfo` | Panel de salud en Administración |
| `LEER_CAPACIDADES` | `GetAbility` | Rellenar `CapacidadPTZ`, `CapacidadPreset`… con datos reales |
| `MOVER_PT` | `PtzCtrl` dirección + `Stop` tras N ms | Ajuste fino manual desde Administración |
| `GUARDAR_PRESET` | `SetPtzPreset` | Crear un preset nuevo desde la posición actual |
| `MODO_DIA_NOCHE` | `SetIsp` `DayNight` | Forzar color/blanco y negro |
| `LUZ_INFRARROJA` | `SetIrLights` | Apagar IR para ver el cielo nocturno |
| `REINICIAR_CAMARA` | `Reboot` | Recuperación remota sin la app (⛔: confirmar siempre) |
| `CAPTURA_ALTA_RESOLUCION` | `Snap` del stream principal | Fotos de calidad para episodios meteorológicos |

## 6. Investigación en la cámara real

`scripts/investigar-reolink.ps1` hace **solo lecturas** (`Get…`) y guarda todas las
respuestas en un JSON para rellenar las columnas *Estado* de este documento. No mueve la
cámara ni cambia nada.

- Toma IP, usuario y contraseña de `C:\ProgramData\MeteoCam\publisher.json`, así que no hay
  que escribir credenciales.
- Guarda el resultado en `C:\ProgramData\MeteoCam\investigacion\reolink-<fecha>.json`,
  con la contraseña y el token sustituidos por `[OCULTO]`.
- Ejecución en el mini PC (PowerShell como administrador, porque `publisher.json` solo lo
  leen administradores):

  ```
  $s = "$env:TEMP\investigar-reolink.ps1"
  Invoke-WebRequest https://raw.githubusercontent.com/joseangelaguilerapaez-hue/MeteoCam/main/scripts/investigar-reolink.ps1 -OutFile $s
  powershell -ExecutionPolicy Bypass -File $s
  ```

- Cierra antes la web y la app de la cámara para no saturarla. El script tarda menos de un
  minuto y no interrumpe la publicación del servicio.

## 7. Fuentes

- Reolink, *Camera HTTP API User Guide*, versión 7 (2022-09) y versión 8: índice de comandos,
  `Login`/token y `GetAbility`.
- Librerías que implementan la guía v8: `reolink_api_wrapper` (Go), `reolink-api` (Node),
  `IPCamera::Reolink` (Perl): operaciones de `PtzCtrl`, rangos de presets, zoom y enfoque.
- `docs/arquitectura.md` (secciones 4.2, 27 y Sprints 7.x) y la tabla `comando_camara` de
  `api-meteoarchidona`.
