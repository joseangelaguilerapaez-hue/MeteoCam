# CLAUDE.md — MeteoCam

Agente de escritorio de MeteoArchidona para gestionar, monitorizar, diagnosticar y controlar
las cámaras IP de las estaciones meteorológicas. Se ejecutará en un mini-PC en la propia
estación, dentro de la misma red local que las cámaras. Instalación piloto prevista: estación
Los Llanos (Villanueva del Trabuco).

Forma parte de MeteoArchidona junto con `api-meteoarchidona` y `web-meteoarchidona`. No
pertenece a Horizonte 4K: no mezcles código, configuración ni secretos con ese proyecto.

## Pila

Python ≥ 3.11 · PySide6 (interfaz Qt) · PyAV (`av`) para vídeo · pytest. Paquete en `src/meteocam/`.

## Mapa

- `src/meteocam/__main__.py`: punto de entrada. `main_window.py`: ventana principal.
- `src/meteocam/cameras/`: diagnóstico de cámaras (`diagnostics.py`) y reproducción de streams (`stream_player.py`).
- `src/meteocam/diagnostics_dialog.py`: diálogo de diagnóstico. `themes/`: temas visuales.
- `tests/`: pytest. `docs/arquitectura.md` (≈3.500 líneas): arquitectura y hoja de ruta; lee solo la sección que toque.

## Principios de diseño que no deben romperse

- Se distingue entre **estación**, **dispositivo físico de cámara**, **vista o canal lógico** y **stream de vídeo**. Una cámara física no equivale necesariamente a una sola vista (p. ej. la Reolink OMVI 3i PoE tiene varios subsistemas ópticos).
- No acoplar la arquitectura a un único modelo de cámara.
- Las cámaras y sus credenciales no se exponen a Internet. Las credenciales no van nunca en el código ni en los commits.
- Diagnóstico y trazabilidad son requisitos: cuando algo falla, explicar qué, en qué etapa, con qué código interno, qué información se obtuvo y qué puede comprobar el usuario.

## Cómo trabajar

- Edita los archivos directamente. Varios archivos relacionados van en un mismo commit y un solo push.
- Rama por funcionalidad (`feature/...`, `fix/...`, `docs/...`), PR a `main`. No empujes a `main` sin que se pida.
- Commits en español y descriptivos, como en el historial.
- **El CI instala el paquete sin dependencias gráficas** (`pip install -e . --no-deps`) y ejecuta `python -m pytest`. Por tanto, la lógica que se pruebe no debe importar PySide6 ni `av` a nivel de módulo; mantén lo gráfico aislado de lo que se prueba.
- Si cambias comportamiento documentado en `docs/arquitectura.md`, actualízalo en el mismo PR.
- Algunos archivos acaban con `# Fin archivo: ruta`. Mantén esa línea donde ya exista.
- La interfaz gráfica no se puede probar en el entorno de Claude Code: dilo claramente cuando algo solo se haya verificado con tests y no ejecutándolo.
