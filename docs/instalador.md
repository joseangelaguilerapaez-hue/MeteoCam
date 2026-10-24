# Instalador del servicio MeteoCam Publisher

`MeteoCam-Setup.exe` instala en el mini PC de la estación el servicio de Windows
**MeteoCamPublisher**, que envía de forma permanente las dos vistas de la cámara al VPS
(RTSP → MPEG-TS → TCP, puertos 10080 y 10081). Sustituye a dejar abierta la ventana del
Night Publisher: arranca solo al encender el equipo, sin iniciar sesión, y Windows lo
relanza si se cae.

## Qué contiene

| Pieza | Qué hace |
| --- | --- |
| `src/meteocam/cameras/publisher_runtime.py` | Motor sin ventana: lee la configuración y mantiene las dos publicaciones (`TcpPublisher`), con reconexión. |
| `src/meteocam/cameras/windows_service.py` | Servicio de Windows (pywin32). Si el motor se cae, sale con error para que Windows lo reinicie. |
| `installer/meteocam_publisher.py` | Punto de entrada para PyInstaller → `MeteoCamPublisher.exe`. |
| `installer/MeteoCam-Setup.iss` | Instalador Inno Setup → `MeteoCam-Setup.exe`. |
| `.github/workflows/instalador.yml` | Construye el instalador en Windows, lo instala y desinstala de prueba y lo publica como artefacto. |

El mini PC **no necesita Python, Git ni VS Code**: todo va dentro del instalador.

## Credenciales

Nunca van en el código, en el repositorio ni en el instalador. Viven solo en
`C:\ProgramData\MeteoCam\publisher.json` de cada equipo:

```json
{
  "camera_host": "IP de la cámara",
  "camera_username": "usuario",
  "camera_password": "contraseña",
  "vps_host": "IP del VPS"
}
```

Campos opcionales con su valor por defecto: `rtsp_port` (554), `panoramica_path`
(`/Preview_01_sub`), `panoramica_tcp_port` (10080), `especifica_path` (`/Preview_02_sub`),
`especifica_tcp_port` (10081).

El instalador obtiene ese archivo así, por orden:

1. Si hay un `publisher.json` **en la misma carpeta que `MeteoCam-Setup.exe`** (por ejemplo,
   copiado del portátil a un pendrive), lo usa tal cual y no pregunta nada.
2. Si no, y el equipo ya lo tenía (reinstalación o actualización), lo conserva.
3. Si no hay ninguno, el asistente pide IP, usuario y contraseña de la cámara y la IP del VPS.

Después lo deja legible solo por SYSTEM y Administradores.

## Descargar el instalador

GitHub → repositorio MeteoCam → pestaña **Actions** → «Instalador Windows» → la ejecución más
reciente en verde → apartado **Artifacts** → `MeteoCam-Setup` (descarga un `.zip` con el `.exe`).
También se puede lanzar a mano con **Run workflow**.

## Instalar en el mini PC

1. Copiar al mismo pendrive `MeteoCam-Setup.exe` y el `publisher.json` del equipo que ya
   funciona (`C:\ProgramData\MeteoCam\publisher.json`; es una carpeta oculta, se abre pegando
   la ruta en la barra del Explorador).
2. **Cerrar el Night Publisher en cualquier otro equipo**: el VPS solo acepta una conexión por
   vista, y dos emisores a la vez se pisan.
3. En el mini PC, doble clic en `MeteoCam-Setup.exe` (pide permisos de administrador) → Instalar.
4. Comprobar (PowerShell):

   ```
   Get-Service MeteoCamPublisher
   Get-Content C:\ProgramData\MeteoCam\logs\publisher.log -Tail 20
   ```

   Debe salir `Running` y, en el registro, `PUBLICANDO hacia …` para las dos vistas.

Actualizar: ejecutar un `MeteoCam-Setup.exe` nuevo encima; para el servicio, cambia los
archivos, conserva `publisher.json` y lo vuelve a arrancar.
Desinstalar: «Agregar o quitar programas» → MeteoCam Publisher (`publisher.json` y los
registros se quedan en `C:\ProgramData\MeteoCam`).

## Ajustes recomendados del mini PC (por confirmar en el equipo)

- Energía: no suspender nunca y no apagar los adaptadores de red.
- BIOS/UEFI: encender al volver la corriente («Restore on AC power loss» → Power On).
