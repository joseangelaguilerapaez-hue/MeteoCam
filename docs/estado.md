# Estado del proyecto — MeteoCam

Última actualización: 2026-10-23.
Origen: reconstruido a partir del historial de Git, ramas y pull requests. Lo marcado
**(por confirmar)** necesita que José lo ratifique o corrija.

## Cómo se mantiene este documento

Es la fuente de verdad de "por dónde vamos". Al empezar una sesión se lee; al terminar
cada tarea se actualiza **en el mismo PR que el cambio**:

1. Mover lo que corresponda entre *Hecho*, *En construcción* y *Pendiente*.
2. Añadir una línea fechada al *Registro* (una línea, sin detalles de código).
3. Si algo de `docs/arquitectura.md` ya no es cierto, corregirlo allí.

No se marca nada como hecho que no esté en `main`.

## Hecho (en `main`, hasta el 19 sep)

- HITO 0: paquete Python, CI con pytest, arquitectura y hoja de ruta.
- Ventana principal en PySide6 con tema "Classic Claro" (estilo Windows 3.1), identidad visual e icono.
- Diagnóstico RTSP y reproducción de vídeo.

## En construcción

- Rama `feature/streaming-web` (2 commits por delante de `main`, 3 y 4 oct, sin PR): configuración multicámara y multivista, y desarrollo de streaming y publicación. **(por confirmar el estado real y si está lista para PR)**.
- PR #1 · este `CLAUDE.md` y `docs/estado.md`.

## Pendiente

- Instalación piloto en la estación Los Llanos (Villanueva del Trabuco) en un mini-PC dentro de la red de las cámaras.
- Decisión definitiva de hardware: Reolink OMVI 3i PoE (candidata preferente) frente a Reolink TrackMix PoE; debe confirmarse con pruebas reales.
- Comunicación con la API central sin exponer cámaras ni credenciales a Internet (fase posterior, según `docs/arquitectura.md`).
- Contrastar `docs/arquitectura.md` con el código actual: la hoja de ruta se escribió en septiembre **(por confirmar qué hitos siguen vigentes)**.

## Registro

- 2026-10-23 · Creados `CLAUDE.md` y este documento; estado reconstruido desde Git.
