MeteoCam — Arquitectura y hoja de ruta

1. Identificación del proyecto

Nombre del repositorio: MeteoCam
Nombre provisional de la aplicación: MeteoArchidona Camera Agent
Nombre corto: MeteoCam
Proyecto: MeteoArchidona
Lenguaje principal: Python
Interfaz gráfica prevista: PySide6 / Qt

MeteoCam es el software de escritorio encargado de gestionar, monitorizar,
diagnosticar y controlar las cámaras IP instaladas en las estaciones
meteorológicas de MeteoArchidona.

La aplicación se ejecutará inicialmente en un mini-PC situado en la estación
meteorológica y conectado a la misma red local que las cámaras.

La primera instalación piloto se realizará en la estación Los Llanos,
situada en Villanueva del Trabuco.

La cámara candidata preferente para la primera instalación es actualmente una
Reolink OMVI 3i PoE.

La Reolink TrackMix PoE, inicialmente seleccionada, se mantiene como
alternativa técnicamente válida y como referencia útil para garantizar que la
arquitectura de MeteoCam no quede acoplada a un único modelo de cámara.

La selección definitiva del hardware se realizará antes de la instalación
física y deberá confirmarse mediante pruebas reales de las capacidades
necesarias para MeteoCam.

MeteoCam se concibe desde el principio no solamente como visor local de una
cámara, sino como el agente local encargado de ejecutar sobre los dispositivos
físicos las operaciones autorizadas por la infraestructura de
MeteoArchidona.

En fases posteriores podrá comunicarse con la API central de MeteoArchidona,
sin exponer directamente las cámaras ni sus credenciales a Internet.

Una decisión arquitectónica fundamental es que MeteoCam no asumirá:

«Una cámara física equivale necesariamente a una única vista de vídeo.»

Determinados dispositivos, como la Reolink OMVI 3i PoE, incorporan varios
subsistemas ópticos dentro del mismo dispositivo físico.

Por ello MeteoCam distinguirá conceptualmente entre:

- estación;
- dispositivo físico de cámara;
- vista o canal lógico;
- stream de vídeo.

Esta separación permitirá trabajar tanto con cámaras convencionales de una
única vista como con dispositivos multicanal actuales o futuros.

---

2. Objetivo general

El objetivo inicial de MeteoCam es conseguir una experiencia de uso lo más
próxima posible a:

«Enchufar la cámara, abrir MeteoCam, encontrarla, configurarla y verla.»

La aplicación deberá automatizar todo aquello que pueda descubrir o configurar
automáticamente.

Cuando sea necesaria intervención del usuario, deberá solicitar únicamente la
información imprescindible.

Cuando algo falle, la aplicación deberá intentar explicar:

- qué ha fallado;
- en qué etapa ha fallado;
- qué código interno de error corresponde;
- qué información técnica se ha obtenido;
- cuáles son las causas probables;
- qué comprobaciones puede realizar el usuario.

El diagnóstico y la trazabilidad son requisitos fundamentales desde las
primeras versiones.

A largo plazo MeteoCam actuará también como puente seguro entre la
infraestructura central de MeteoArchidona y las cámaras instaladas en cada
estación.

---

3. Alcance de la primera fase

La primera fase debe proporcionar una aplicación de escritorio funcional y una
arquitectura preparada para trabajar posteriormente con la cámara real.

Debe incluir progresivamente:

- aplicación de escritorio;
- interfaz PySide6;
- abstracción de dispositivos de cámara;
- abstracción de vistas/canales;
- cámara simulada;
- gestión de estaciones y dispositivos;
- configuración local;
- descubrimiento automático desacoplado;
- configuración manual alternativa;
- sistema de estados;
- prueba de conexión;
- diagnóstico detallado;
- logging persistente;
- gestión segura de errores;
- operaciones de red sin bloquear la interfaz;
- preparación del visor de vídeo;
- conexión posterior con hardware Reolink real;
- reproducción estable del vídeo en directo;
- capacidad arquitectónica para más de una vista simultánea;
- reconexión controlada.

La primera fase NO debe incluir todavía:

- grabación de vídeo;
- almacenamiento de fotografías;
- timelapses;
- episodios meteorológicos;
- sincronización operativa con PostgreSQL;
- integración completa con la API central de MeteoArchidona;
- automatismos meteorológicos;
- publicación pública del vídeo;
- control PTZ remoto desde la web;
- movimientos automáticos basados en radar.

Estas funciones quedan previstas arquitectónicamente, pero no deben complicar
la primera implementación.

La arquitectura y los identificadores utilizados desde el comienzo deberán
permitir que un dispositivo configurado localmente pueda relacionarse en el
futuro con su correspondiente entidad persistida en la API y PostgreSQL de
MeteoArchidona.

Asimismo, sus vistas o canales podrán relacionarse posteriormente con las
vistas funcionales publicadas por la infraestructura central.

---

4. Primera instalación física

4.1 Estación piloto

Estación: Los Llanos
Localidad: Villanueva del Trabuco
Proyecto: MeteoArchidona

La primera instalación se realizará en Los Llanos.

El Silo será una instalación posterior si el piloto funciona correctamente.

4.2 Cámara candidata preferente

La cámara candidata preferente es:

Reolink OMVI 3i PoE

La OMVI 3i PoE constituye conceptualmente un único dispositivo físico que
integra dos subsistemas visuales principales.

Cámara superior panorámica

Características oficiales relevantes:

- doble lente que forma una panorámica;
- resolución máxima: 5120 × 1920;
- resolución aproximada: 10 MP;
- campo de visión horizontal: 180 grados;
- campo de visión vertical: 65 grados;
- posición fija;
- H.264/H.265;
- stream principal;
- stream secundario.

Su función meteorológica prevista será proporcionar una visión general y
permanente del cielo visible desde la estación.

Cámara inferior PT

Características oficiales relevantes:

- resolución máxima: 3840 × 2160;
- resolución aproximada: 8 MP;
- campo de visión aproximado: 55 grados horizontal y 30 grados vertical;
- movimiento horizontal máximo aproximado: 350 grados;
- movimiento vertical máximo aproximado: 50 grados;
- movimiento PT controlable;
- zoom digital;
- H.264/H.265;
- stream principal;
- stream secundario.

Su función meteorológica prevista será permitir observación dirigida hacia
sectores concretos del horizonte mediante posiciones autorizadas.

Capacidades adicionales conocidas

La documentación oficial de la OMVI 3i PoE indica actualmente, entre otras
capacidades:

- hasta 64 posiciones preestablecidas;
- una posición de guardia;
- una ruta de patrulla;
- hasta cuatro puntos por ruta de patrulla;
- SyncTrack;
- Pinpoint mediante software compatible;
- encuadre automático;
- RTSP;
- RTMP;
- HTTP/HTTPS;
- DHCP;
- UPnP;
- FTP;
- P2P;
- hasta 12 transmisiones simultáneas;
- 2 transmisiones principales;
- hasta 10 transmisiones secundarias;
- tarjeta microSD de hasta 512 GB;
- protección IP66.

La existencia de una función en el software oficial de Reolink no implica
automáticamente que dicha función pueda ser controlada desde MeteoCam.

Cada capacidad deberá clasificarse posteriormente como:

- disponible físicamente;
- disponible mediante software Reolink;
- disponible mediante RTSP;
- disponible mediante ONVIF;
- disponible mediante CGI/API;
- no accesible desde terceros;
- pendiente de comprobar.

MeteoCam nunca deberá asumir capacidades únicamente a partir del nombre del
modelo.

La detección real de capacidades deberá formar parte de la integración con el
hardware.

4.3 Alimentación y red de la OMVI 3i PoE

La OMVI 3i PoE utiliza:

- PoE activo;
- IEEE 802.3at;
- 48 V;
- puerto Ethernet RJ45 10/100 Mbps.

También admite alimentación DC 12 V / 2 A, con consumo inferior a 24 W, pero
la instalación prevista utilizará PoE.

El switch de Los Llanos deberá verificarse antes de su compra para garantizar
compatibilidad real con IEEE 802.3at y potencia suficiente por puerto.

No deberá seleccionarse un switch únicamente porque se anuncie genéricamente
como "PoE".

4.4 Alternativa TrackMix

La Reolink TrackMix PoE permanece como alternativa válida.

La arquitectura no deberá requerir una OMVI para funcionar.

Una cámara convencional o de arquitectura diferente deberá poder representarse
mediante el mismo modelo general:

DISPOSITIVO
    |
    +---- una o varias vistas/canales
             |
             +---- uno o varios streams

Esto permitirá que MeteoCam pueda trabajar en el futuro con:

- OMVI;
- TrackMix;
- otras cámaras Reolink;
- otros fabricantes;
- cámaras de una sola lente;
- dispositivos multicanal.

4.5 Red física

La instalación prevista es:

ROUTER
   |
   | Ethernet existente
   |
   v
  BAR
   |
   v
SWITCH PoE+ GIGABIT
   |
   +----> Televisión / otros dispositivos
   |
   +----> Cat6 exterior con PoE
              |
              v
           TEJADO
              |
              v
      REOLINK OMVI 3i PoE

En este proyecto, el bar es el nombre utilizado para la zona techada con
porche de Los Llanos donde llega actualmente un cable Ethernet directo desde
el router y existen enchufes eléctricos.

El switch previsto será aproximadamente de 4/5 puertos, Gigabit y PoE activo.

Para la OMVI deberá soportar específicamente IEEE 802.3at y potencia suficiente
por puerto.

No habrá inicialmente:

- NVR;
- grabador dedicado;
- SAI/UPS.

El mini-PC será el elemento inteligente de gestión y procesamiento.

---

5. Arquitectura de red básica

La OMVI, TrackMix y cámaras equivalentes no son webcams USB.

Son dispositivos IP conectados a la LAN.

La comunicación local será aproximadamente:

Dispositivo Reolink
      |
      | Ethernet / PoE
      |
  Switch PoE+
      |
      | LAN
      |
    Router
      |
      |
   Mini-PC
      |
      v
   MeteoCam

La cámara obtendrá inicialmente su dirección mediante DHCP, salvo que
posteriormente se configure una reserva DHCP o dirección estable.

MeteoCam deberá soportar:

- IP descubierta automáticamente;
- IP introducida manualmente;
- fabricante;
- modelo;
- usuario;
- contraseña;
- identificación de vistas/canales;
- stream principal por vista;
- stream secundario por vista;
- capacidades descubiertas;
- parámetros adicionales descubiertos durante las pruebas reales.

Las credenciales nunca estarán escritas directamente en el código fuente.

---

6. Arquitectura lógica

La interfaz gráfica no debe depender directamente de Reolink, RTSP, ONVIF ni
ningún fabricante concreto.

La arquitectura conceptual inicial será:

            +----------------------+
            |         GUI          |
            |       PySide6        |
            +----------+-----------+
                       |
                       v
            +----------------------+
            | Application services |
            +----------+-----------+
                       |
                       v
            +----------------------+
            | Camera abstraction   |
            +----------+-----------+
                       |
          +------------+------------+
          |                         |
          v                         v
+--------------------+   +--------------------+
| SimulatedCamera    |   |   ReolinkCamera    |
+--------------------+   +---------+----------+
                                   |
                                   v
                            Dispositivo físico
                                   |
                     +-------------+-------------+
                     |                           |
                     v                           v
                Vista/canal A               Vista/canal B
                     |                           |
                     v                           v
                   Streams                     Streams

La aplicación deberá poder desarrollarse y probarse inicialmente utilizando
"SimulatedCamera".

Cuando llegue la cámara física se incorporará "ReolinkCamera" sin obligar a
reescribir la interfaz gráfica.

La abstracción deberá admitir que un dispositivo exponga una o varias vistas.

La GUI no deberá asumir que existe exactamente un stream principal y un stream
secundario para todo el dispositivo.

Conceptualmente:

CameraDevice
    |
    +---- CameraView
    |        |
    |        +---- main stream
    |        +---- sub stream
    |
    +---- CameraView
             |
             +---- main stream
             +---- sub stream

Los nombres definitivos de las clases se decidirán durante la implementación.

La comunicación futura con MeteoArchidona tampoco deberá quedar acoplada
directamente a la GUI.

Conceptualmente existirá una capa equivalente a:

GUI
 |
 +---- Camera abstraction
 |
 +---- servicios de aplicación
 |
 +---- MeteoArchidonaApiClient
             |
             | HTTPS
             v
      API MeteoArchidona

El nombre definitivo y la estructura del cliente de API se decidirán cuando se
implemente esa fase.

---

7. Entidades estación, dispositivo, vista y stream

MeteoCam debe estar preparada desde el principio para múltiples estaciones,
múltiples dispositivos y múltiples vistas por dispositivo.

No se debe identificar un dispositivo únicamente por su IP.

7.1 Estación

Ejemplo:

Nombre: Los Llanos
Localidad: Villanueva del Trabuco

7.2 Dispositivo físico de cámara

Ejemplo:

Nombre: OMVI principal
Estación: Los Llanos
Fabricante: Reolink
Modelo: OMVI 3i PoE
IP: 192.168.x.x
Usuario: ...
Contraseña: ...

Un dispositivo representa el hardware físico conectado a la red.

Una estación podrá disponer de uno o varios dispositivos físicos.

7.3 Vista o canal

Una vista representa un subsistema visual que puede proporcionar imágenes o
vídeo de manera diferenciada.

Ejemplo para OMVI:

Dispositivo: OMVI principal

Vista 1:
    Nombre: Panorámica
    Tipo: PANORAMICA
    Móvil: no

Vista 2:
    Nombre: PT
    Tipo: PT
    Móvil: sí

Una cámara convencional podrá disponer simplemente de:

Vista 1:
    Nombre: Principal
    Tipo: FIJA

El modelo no impondrá que todos los dispositivos tengan dos vistas.

7.4 Stream

Cada vista podrá proporcionar uno o varios streams.

Ejemplo conceptual:

OMVI principal
    |
    +---- PANORÁMICA
    |        |
    |        +---- MAIN
    |        +---- SUB
    |
    +---- PT
             |
             +---- MAIN
             +---- SUB

No se codificarán anticipadamente números de canal o rutas RTSP específicas
hasta comprobar el hardware real.

El adaptador Reolink será responsable de traducir los identificadores lógicos
de MeteoCam a los identificadores físicos utilizados por la cámara.

7.5 Identificación central futura

Además de la identificación local, un dispositivo y sus vistas podrán disponer
posteriormente de identificadores centrales que los relacionen con las
entidades correspondientes persistidas en PostgreSQL a través de la API
MeteoArchidona.

---

8. Configuración local

En la primera fase no se utilizará PostgreSQL para almacenar la configuración
privada de MeteoCam.

Se utilizará inicialmente una solución local sencilla detrás de una capa de
abstracción.

La aplicación no deberá depender directamente del formato físico utilizado
para persistir la configuración.

Esto permitirá migrar posteriormente a SQLite u otra solución sin modificar la
lógica principal ni la interfaz.

Las contraseñas deberán almacenarse de manera razonablemente segura.

Nunca deberán aparecer contraseñas en:

- logs;
- diagnósticos;
- informes;
- mensajes de excepción mostrados al usuario;
- URLs RTSP registradas sin enmascarar.

Debe distinguirse claramente entre:

Configuración privada local

Información necesaria para que MeteoCam controle físicamente el dispositivo:

- dirección IP de la LAN;
- usuario;
- contraseña;
- puertos;
- URLs o parámetros internos;
- canales físicos;
- capacidades descubiertas;
- configuración específica del hardware.

Catálogo central

Información funcional que MeteoArchidona necesita conocer:

- identificador de dispositivo/cámara;
- estación;
- código;
- nombre;
- fabricante;
- modelo;
- estado;
- si está activa;
- si es pública;
- orden de presentación;
- vistas publicables;
- información necesaria para el visor y la administración.

Los secretos locales de la cámara no deberán publicarse ni entregarse al
navegador.

---

9. Primer arranque

Si no existe ninguna cámara configurada, MeteoCam deberá ofrecer una
experiencia aproximadamente equivalente a:

No hay cámaras configuradas.

[ Buscar cámaras automáticamente ]
[ Añadir cámara manualmente ]

El procedimiento ideal cuando llegue el hardware será:

1. conectar la cámara al switch PoE;
2. esperar su arranque;
3. abrir MeteoCam;
4. seleccionar "Buscar cámaras";
5. detectar el dispositivo;
6. mostrar la información descubierta;
7. seleccionar la cámara;
8. solicitar únicamente los datos que falten;
9. probar los servicios disponibles;
10. detectar las vistas/canales disponibles;
11. detectar los streams disponibles;
12. guardar la configuración;
13. mostrar vídeo en directo.

Para una OMVI, el objetivo ideal será detectar de manera independiente:

- vista panorámica;
- vista PT;
- stream principal panorámico;
- stream secundario panorámico;
- stream principal PT;
- stream secundario PT.

La correspondencia física concreta se comprobará con hardware real.

La detección automática nunca será requisito obligatorio.

Siempre existirá la alternativa de configuración manual.

---

10. Descubrimiento automático

El descubrimiento será un subsistema independiente.

Conceptualmente:

CameraDiscovery
      |
      +---- ONVIF / WS-Discovery
      |
      +---- mecanismos Reolink
      |
      +---- detección de servicios
      |
      +---- otros proveedores futuros

No se asumirá antes de disponer del hardware qué mecanismo será el definitivo.

Si ONVIF o cualquier otro mecanismo falla, la cámara deberá poder utilizarse
mediante configuración manual.

El fallo del descubrimiento nunca debe impedir el funcionamiento del resto de
MeteoCam.

El descubrimiento deberá distinguir cuando sea posible entre:

- descubrimiento del dispositivo;
- identificación del fabricante/modelo;
- descubrimiento de servicios;
- descubrimiento de vistas/canales;
- descubrimiento de streams;
- descubrimiento de capacidades PTZ;
- descubrimiento de capacidades específicas del fabricante.

---

11. Sistema de estados

Los dispositivos tendrán estados explícitos.

Como mínimo se prevén:

- DESCONECTADA;
- CONECTANDO;
- CONECTADA;
- SIN_VIDEO;
- ERROR_AUTENTICACION;
- REINTENTANDO;
- ERROR.

Cuando sea necesario, las vistas y streams podrán disponer también de estados
propios.

Ejemplo:

Dispositivo OMVI........ CONECTADO
Panorámica.............. CONECTADA
Stream panorámico....... OK
PT...................... CONECTADA
Stream PT............... ERROR

Esto permitirá evitar que el fallo de una vista convierta necesariamente todo
el dispositivo en "desconectado".

Los estados deberán poder ampliarse posteriormente sin depender de textos
mostrados directamente en la GUI.

La interfaz representará estos estados de manera comprensible para el usuario.

---

12. Operaciones asíncronas

Ninguna operación potencialmente lenta debe bloquear el hilo principal de Qt.

Esto incluye:

- descubrimiento de dispositivos;
- detección de vistas/canales;
- conexión de red;
- comprobaciones HTTP/HTTPS;
- ONVIF;
- RTSP;
- apertura de streams;
- reconexión;
- diagnósticos;
- futuras consultas a la API MeteoArchidona;
- futuras consultas de órdenes persistidas.

La interfaz debe permanecer operativa incluso cuando una cámara, una vista o un
servicio remoto no responda.

---

13. Vídeo en directo

La primera versión con hardware real únicamente reproducirá vídeo.

No grabará nada.

Cadena conceptual:

Dispositivo
   |
   +---- Vista/canal
            |
            | RTSP
            v
         MeteoCam
            |
            v
     Visor de escritorio

No se implementará manualmente ningún decodificador.

Se evaluarán con el hardware real:

- libVLC / VLC;
- FFmpeg;
- Qt Multimedia;
- otras soluciones justificadas técnicamente.

Los criterios principales serán:

1. estabilidad;
2. compatibilidad;
3. H.264/H.265;
4. reconexión;
5. diagnóstico;
6. consumo de recursos;
7. facilidad de distribución;
8. capacidad para manejar varios streams simultáneamente.

Cuando sea conveniente, el visor permanente podrá utilizar streams de menor
resolución y reservar los streams principales de máxima calidad para futuras
funciones de captura o grabación.

13.1 Dispositivos multivista

La arquitectura del visor deberá permitir que un dispositivo exponga varias
vistas simultáneamente.

No es obligatorio reproducir dos vídeos simultáneos en la primera versión.

Sin embargo, la estructura no deberá impedir posteriormente una disposición
equivalente a:

+--------------------------------------------------+
|            PANORÁMICA 180°                      |
|                                                  |
+--------------------------+-----------------------+
|        VISTA PT          |    INFORMACIÓN        |
|                          |                       |
|                          | Estado                |
|                          | Vista                 |
|                          | Diagnóstico           |
+--------------------------+-----------------------+

Para la OMVI esto permitiría mantener permanentemente visible la panorámica
mientras la cámara PT observa un sector específico.

---

14. Identidad visual y temas

MeteoCam utilizará una estética de aplicación de escritorio clásica y técnica.

No se pretende reproducir el estilo visual de una aplicación web moderna.

La interfaz utilizará Qt Widgets y hojas de estilo QSS para conservar
un aspecto de cliente pesado tradicional:

- paneles grises o metálicos;
- botones con relieve;
- bordes biselados;
- marcos hundidos;
- pestañas clásicas;
- controles claramente delimitados;
- jerarquía visual propia de aplicaciones técnicas de escritorio.

Se definen inicialmente dos temas oficiales:

MeteoCam Classic Claro

Tema clásico claro basado principalmente en:

- grises claros;
- plata;
- paneles con relieve;
- controles tridimensionales;
- marcos técnicos;
- contraste elevado.

MeteoCam Classic Oscuro

Versión oscura de la misma identidad visual.

No deberá convertirse en una interfaz plana moderna de color negro.

Mantendrá:

- relieve;
- biseles;
- separación visual de paneles;
- apariencia de aplicación técnica;
- controles tridimensionales.

Ambos temas utilizarán la misma estructura de widgets y la misma lógica.

No se crearán dos interfaces independientes.

La diferencia visual deberá resolverse mediante temas QSS separados.

El usuario podrá cambiar el tema en ejecución sin reiniciar MeteoCam.

Conceptualmente:

Configuración
    |
    +---- Apariencia
             |
             +---- MeteoCam Classic Claro
             |
             +---- MeteoCam Classic Oscuro

La preferencia elegida se persistirá localmente y se restaurará en el siguiente
arranque.

El color se utilizará con moderación.

Los colores semánticos podrán utilizarse para estados como:

- verde: conectado / correcto;
- amarillo: conectando / reintentando / advertencia;
- rojo: error / desconexión problemática.

La identidad visual no deberá introducir dependencias gráficas adicionales
innecesarias.

---

15. Diagnóstico

El diagnóstico es un requisito fundamental del proyecto.

La aplicación no deberá limitarse a mostrar mensajes genéricos como:

«No se pudo conectar.»

Una prueba de conexión deberá ejecutar comprobaciones progresivas.

Ejemplo conceptual:

Iniciando diagnóstico: Los Llanos
Dispositivo: OMVI principal
IP configurada: 192.168.1.50

Comprobando accesibilidad de red...
OK

Comprobando servicios...
OK

Identificando dispositivo...
Reolink OMVI 3i PoE

Detectando vistas/canales...
2 vistas detectadas

Vista panorámica...
OK

Vista PT...
OK

Comprobando RTSP...
OK

Comprobando autenticación...
OK

Solicitando stream panorámico principal...
OK

Códec detectado: H.265
Resolución detectada: 5120 x 1920

Solicitando stream PT principal...
OK

Códec detectado: H.265
Resolución detectada: 3840 x 2160

RESULTADO:
DISPOSITIVO OPERATIVO

Si una etapa falla, las etapas dependientes podrán aparecer como no probadas.

El diagnóstico deberá evitar considerar el dispositivo completo inutilizable
si únicamente falla una de sus vistas o streams.

---

16. Códigos de error

Los errores tendrán códigos internos estructurados por subsistema.

Familias inicialmente reservadas:

- "CAM-NET-xxx"
- "CAM-DISCOVERY-xxx"
- "CAM-AUTH-xxx"
- "CAM-RTSP-xxx"
- "CAM-STREAM-xxx"
- "CAM-CHANNEL-xxx"
- "CAM-ONVIF-xxx"
- "CAM-PTZ-xxx"
- "CAM-API-xxx"
- "CAM-JOB-xxx"

Ejemplo:

CAM-RTSP-002

Cada código deberá permitir asociar:

- subsistema;
- descripción;
- etapa;
- dispositivo;
- vista/canal cuando corresponda;
- información técnica;
- causas probables;
- posibles comprobaciones.

PTZ, API y ejecución de trabajos dispondrán de sus espacios de códigos aunque
no se implementen en la primera fase.

---

17. Logging

MeteoCam tendrá logging persistente desde sus primeras versiones.

Estructura conceptual:

logs/
    meteoarchidona-camera.log
    meteoarchidona-camera.log.1
    meteoarchidona-camera.log.2

Se utilizará rotación para evitar crecimiento ilimitado.

Los logs deberán registrar, cuando corresponda:

- inicio de aplicación;
- cierre;
- versión;
- búsqueda de cámaras;
- dispositivos encontrados;
- vistas/canales detectados;
- streams detectados;
- capacidades detectadas;
- cambios de estado;
- intentos de conexión;
- conexiones;
- desconexiones;
- reconexiones;
- errores RTSP;
- errores de autenticación;
- errores del motor de vídeo;
- excepciones;
- resultados de diagnóstico;
- futuras comunicaciones con la API;
- futuras órdenes recibidas;
- inicio, finalización, cancelación y error de trabajos.

Nunca se registrarán:

- contraseñas;
- secretos;
- credenciales completas;
- URLs que incorporen credenciales sin enmascarar.

---

18. Informe de diagnóstico

MeteoCam deberá poder generar posteriormente un informe técnico fácilmente
compartible.

Ejemplo:

MeteoArchidona Camera Agent
Diagnóstico

Estación: Los Llanos
Dispositivo: OMVI principal
Modelo: Reolink OMVI 3i PoE
Versión MeteoCam: 0.1.0

Red.................... OK
IP..................... 192.168.1.50
Conectividad........... OK
HTTP/HTTPS............. OK

Vistas detectadas...... 2

Panorámica:
    RTSP............... OK
    Stream principal... OK
    Resolución......... 5120 x 1920

PT:
    RTSP............... ERROR
    Stream principal... NO PROBADO

Motor de vídeo......... OK

Último error:
CAM-RTSP-002

El informe nunca incluirá contraseñas ni secretos.

Su finalidad será permitir reproducir y localizar rápidamente problemas cuando
se trabaje con hardware real.

---

19. Reconexión

MeteoCam deberá asumir que una cámara IP puede:

- reiniciarse;
- desaparecer temporalmente;
- perder conectividad;
- perder RTSP;
- perder únicamente uno de sus streams;
- tardar en arrancar;
- recuperar posteriormente la conexión.

La reconexión deberá ser controlada.

No se realizarán bucles agresivos de reconexión.

La interfaz deberá reflejar claramente qué está ocurriendo.

Ejemplo:

CONECTADA
    |
    v
SIN VIDEO
    |
    v
REINTENTANDO
    |
    +----> CONECTADA
    |
    +----> DESCONECTADA

En dispositivos multivista podrá existir reconexión independiente de streams
cuando técnicamente resulte apropiado.

La política exacta de tiempos y reintentos se determinará durante la
implementación y las pruebas reales.

---

20. Catálogo central de cámaras y dispositivos

Las cámaras de MeteoArchidona deberán estar representadas posteriormente en la
base de datos PostgreSQL central.

La API será la única interfaz utilizada por la web para consultar y administrar
este catálogo.

Conceptualmente existirá una relación:

ESTACIÓN
    |
    | 1:N
    v
DISPOSITIVOS
    |
    | 1:N
    v
VISTAS / CANALES

Una entidad central de dispositivo podrá contener, entre otros campos que se
determinarán durante el diseño de la API:

id
estacion_id
codigo
nombre
fabricante
modelo
activa
publica
orden
estado

Una entidad de vista física/lógica podrá contener posteriormente:

id
dispositivo_id
codigo
nombre
tipo
movil
activa
publica
orden

No se considera necesario almacenar centralmente las credenciales privadas de
la cámara para que el visor público pueda funcionar.

La información privada necesaria para controlar físicamente la cámara
permanecerá en MeteoCam.

El catálogo central permitirá que la web consulte dinámicamente qué dispositivos
y vistas existen y cuáles deben aparecer en el selector.

No deberán codificarse manualmente las cámaras disponibles dentro del
JavaScript del visor.

Ejemplo conceptual:

API
 |
 +---- Los Llanos
 |       |
 |       +---- OMVI principal
 |               |
 |               +---- Panorámica
 |               |
 |               +---- PT
 |
 +---- El Silo
         |
         +---- Dispositivo principal
                 |
                 +---- Vista(s)

Añadir o retirar una cámara pública deberá poder reflejarse en el visor sin
necesidad de modificar manualmente su código fuente.

---

21. Vistas físicas y vistas autorizadas

Debe distinguirse entre dos conceptos relacionados pero diferentes.

21.1 Vista física o canal

Representa una fuente visual real proporcionada por el dispositivo.

Ejemplo OMVI:

PANORÁMICA
PT

21.2 Vista meteorológica autorizada

Representa un encuadre funcional autorizado por MeteoArchidona.

Ejemplo sobre la vista PT:

OESTE
SUROESTE
SUR
SURESTE
ESTE
SIERRA

Por tanto:

DISPOSITIVO
   |
   +---- VISTA FÍSICA PANORÁMICA
   |
   +---- VISTA FÍSICA PT
              |
              +---- OESTE
              +---- SUROESTE
              +---- SUR
              +---- SURESTE
              +---- ESTE

Las vistas públicas autorizadas deberán persistirse en la infraestructura
central.

No deberán estar codificadas directamente en el visor web.

Conceptualmente una entidad de vista autorizada podrá incluir posteriormente:

id
vista_fisica_id
codigo
nombre
descripcion
orden
tipo
activa
publica
predeterminada
referencia_interna

La estructura física definitiva se diseñará al implementar este subsistema.

La web consultará la API para conocer qué vistas debe mostrar.

Si Administración:

- añade una vista;
- elimina una vista;
- cambia su nombre;
- cambia su orden;
- la desactiva;
- deja de publicarla;

el visor deberá reflejar el cambio a partir de la información proporcionada
por la API, sin requerir un nuevo despliegue de la web.

Debe distinguirse entre:

- vista existente;
- vista activa;
- vista pública.

Una vista podrá existir y ser utilizada administrativamente sin estar
disponible para visitantes.

La referencia interna utilizada por Reolink no deberá exponerse necesariamente
al navegador.

El navegador trabajará con identificadores públicos controlados por la API.

---

22. PTZ administrativo futuro

El control PTZ no forma parte de la primera fase, pero la arquitectura debe
permitir incorporarlo.

El control administrativo podrá incluir posteriormente:

- izquierda;
- derecha;
- arriba;
- abajo;
- zoom;
- detener movimiento;
- creación de presets;
- edición de presets;
- selección de presets;
- posición de guardia;
- funciones específicas del dispositivo cuando puedan utilizarse de forma
  segura.

Este control libre será exclusivamente administrativo o de mantenimiento.

Nunca se expondrá el control PTZ libre a usuarios públicos.

En dispositivos multivista, las operaciones PTZ se aplicarán únicamente a las
vistas que posean esa capacidad.

En la OMVI, por ejemplo, la panorámica superior es fija y la vista inferior es
la que dispone de movimiento PT.

---

23. Presets y vistas públicas

La web pública de MeteoArchidona NUNCA permitirá al visitante mover libremente
la cámara.

No se permitirán públicamente:

- flechas PTZ;
- arrastrar para mover;
- coordenadas arbitrarias;
- pan arbitrario;
- tilt arbitrario;
- zoom arbitrario;
- selección de presets internos no autorizados.

El usuario público únicamente podrá seleccionar, cuando esa funcionalidad esté
habilitada para su tipo de acceso, vistas previamente configuradas,
verificadas y autorizadas por MeteoArchidona.

Ejemplo:

OESTE
SUROESTE
SUR
SURESTE
ESTE
SIERRA
PANORÁMICA

La API deberá aplicar esta restricción en servidor.

No será suficiente con ocultar controles en la interfaz web.

Una petición manipulada que intente ejecutar una posición no autorizada deberá
ser rechazada.

La existencia de una panorámica fija permite además diferenciar:

Vista pública permanente

Puede mantenerse visible sin necesidad de controlar físicamente la orientación.

Ejemplo:

PANORÁMICA 180°

Vista pública controlable

Puede depender de presets autorizados y políticas de reserva.

Ejemplo:

PT -> OESTE
PT -> SUR
PT -> SIERRA

---

24. Acceso público y usuarios registrados

La visualización en directo de las cámaras marcadas como públicas no requerirá
registro en MeteoArchidona.

Principio funcional:

«Las cámaras públicas podrán visualizarse en directo sin necesidad de iniciar
sesión.»

El hecho de que una cámara sea pública no implica que todas sus funcionalidades
de control sean públicas.

Determinadas funciones adicionales podrán reservarse posteriormente a usuarios
registrados.

La política concreta se diseñará cuando se implemente el visor y el subsistema
de control.

No se decide todavía si determinadas acciones, como adquirir temporalmente el
selector de vistas PT, estarán disponibles:

- para cualquier visitante;
- únicamente para usuarios registrados;
- para diferentes niveles de usuario.

Esta decisión deberá tomarse atendiendo a:

- facilidad de uso;
- prevención de abuso;
- control de concurrencia;
- trazabilidad;
- utilidad meteorológica;
- seguridad.

Conceptualmente existirán al menos tres niveles:

Visitante

Podrá visualizar las cámaras públicas sin registrarse.

Las funcionalidades adicionales dependerán de la política que se establezca.

Usuario registrado

Podrá visualizar igualmente las cámaras públicas y podrá disponer de
funcionalidades adicionales que se definan posteriormente.

Administrador

Dispondrá de las funciones de administración, mantenimiento y control
autorizadas, incluyendo aquellas que nunca deben estar disponibles
públicamente.

---

25. Referencia lógica de orientación

Para las vistas PT de MeteoCam se podrá utilizar el Sur como referencia
lógica.

Conceptualmente:

SUR = 0 grados MeteoCam

A partir de esa referencia:

SO = -45 grados
O  = -90 grados
NO = -135 grados

SE = +45 grados
E  = +90 grados
NE = +135 grados

Estos valores son referencias conceptuales.

No se debe asumir que correspondan a las coordenadas internas de Reolink.

Durante la instalación real se orientará la cámara y se crearán presets
visualmente comprobados.

MeteoCam trabajará con nombres semánticos y no necesitará exponer al usuario
las coordenadas internas de la cámara.

La orientación lógica se aplicará únicamente a vistas capaces de movimiento.

La panorámica fija de una OMVI tendrá su propia orientación física de
instalación, que deberá ajustarse correctamente durante el montaje.

---

26. Panorámica meteorológica

Con la incorporación de dispositivos como la OMVI deben distinguirse dos
conceptos.

26.1 Panorámica óptica permanente

La OMVI 3i PoE proporciona una panorámica superior fija de aproximadamente
180 grados.

Esta vista no necesita mover mecánicamente la cámara.

Su función meteorológica podrá ser:

- mantener una visión general permanente;
- observar simultáneamente una gran parte del cielo;
- servir de referencia mientras la vista PT está orientada a otro sector;
- proporcionar imágenes panorámicas;
- alimentar futuros timelapses panorámicos;
- permanecer disponible mientras otro usuario controla la PT.

Esta característica reduce la necesidad de mover continuamente la cámara para
obtener contexto general.

26.2 Recorrido PT meteorológico

Independientemente de la panorámica fija, se mantiene previsto un recorrido
direccional específicamente diseñado para observación meteorológica.

Recorrido inicial candidato:

NOROESTE
    |
    v
  OESTE
    |
    v
SUROESTE
    |
    v
   SUR
    |
    v
SURESTE
    |
    v
   ESTE
    |
    v
 NORESTE

Expresado de forma abreviada:

NO -> O -> SO -> S -> SE -> E -> NE

El sector Norte queda inicialmente fuera del recorrido habitual.

El recorrido desde NO hasta NE pasando por el Sur cubre aproximadamente
270 grados.

La OMVI dispone de aproximadamente 350 grados de recorrido horizontal en su
vista PT, por lo que mecánicamente existe margen suficiente, sujeto a
comprobación con la instalación real.

Este recorrido no será un movimiento elegido libremente por el visitante.

Será una secuencia completamente definida y autorizada por MeteoArchidona.

Podrá implementarse mediante:

- una secuencia controlada de presets;
- movimiento PT controlado por MeteoCam;
- funciones internas de la cámara si resultan adecuadas.

La OMVI permite una ruta de patrulla de hasta cuatro presets, por lo que esa
función interna no cubre directamente el recorrido candidato completo de siete
orientaciones.

MeteoCam podrá encadenar presets por sí mismo si finalmente se necesita el
recorrido completo.

La solución definitiva se decidirá después de probar el hardware.

---

27. Capacidades avanzadas OMVI previstas para investigación

La OMVI dispone de capacidades específicas que pueden resultar interesantes
para MeteoCam.

Su presencia en este documento no implica compromiso de implementación.

27.1 Posición de guardia

La cámara admite una posición de guardia.

MeteoCam podrá estudiar su utilización como orientación PT de referencia.

Ejemplo conceptual:

POSICIÓN DE GUARDIA:
SUR

La posición real se determinará durante la instalación.

27.2 Presets

La OMVI admite hasta 64 posiciones preestablecidas.

MeteoCam necesitará previsiblemente muchas menos para el uso meteorológico.

Ejemplo:

NO
O
SO
S
SE
E
NE
SIERRA

Los presets internos del fabricante deberán permanecer desacoplados de los
identificadores públicos utilizados por MeteoArchidona.

27.3 Patrulla

La OMVI admite una ruta de patrulla con hasta cuatro puntos.

Se comprobará si resulta útil para alguna operación concreta.

No se dependerá de ella para el recorrido meteorológico completo.

27.4 SyncTrack

La OMVI dispone de seguimiento sincronizado entre la panorámica y la cámara PT.

Su utilidad original está orientada principalmente al seguimiento de objetos.

MeteoCam investigará si alguna parte de esta capacidad resulta útil en un
contexto meteorológico.

No se incorporará automáticamente a la arquitectura operativa.

27.5 Pinpoint

El software compatible de Reolink permite seleccionar una zona de la
panorámica y dirigir la vista PT hacia ella.

Conceptualmente esta función encaja especialmente bien con observación
meteorológica:

PANORÁMICA
    |
    | seleccionar zona
    v
PT orientada hacia esa zona

Sin embargo, antes de diseñar una función MeteoCam basada en Pinpoint deberá
comprobarse si Reolink expone esa operación mediante mecanismos accesibles a
software de terceros.

27.6 Auto Sweep y otras funciones

Las funciones automáticas específicas disponibles en firmware o clientes
Reolink se investigarán cuando exista hardware real.

No se asumirá que una función disponible en Reolink App o Reolink Client esté
necesariamente expuesta mediante ONVIF, CGI u otra API.

---

28. Reserva futura del selector público

Cuando se habilite el selector público de vistas PT, no se permitirá que
múltiples usuarios cambien continuamente la orientación.

Se prevé un sistema de reserva temporal por sesión.

Conceptualmente:

1. un usuario entra en los controles;
2. la API intenta adquirir una reserva temporal de la vista controlable;
3. si está libre, la sesión obtiene temporalmente el selector de vistas;
4. solamente esa sesión puede solicitar presets públicos durante la reserva;
5. otras sesiones pueden continuar viendo el vídeo;
6. la panorámica fija puede continuar disponible independientemente;
7. la reserva se mantiene mediante actividad o heartbeat;
8. si la sesión desaparece, la reserva caduca automáticamente;
9. después de liberar el control puede aplicarse un periodo de estabilización;
10. durante ese periodo se mantiene la última vista elegida;
11. posteriormente la vista PT vuelve a quedar disponible.

La reserva concede únicamente derecho a seleccionar presets autorizados.

Nunca concede PTZ libre.

Se estudiarán parámetros como:

- duración máxima de turno;
- tiempo máximo de inactividad;
- frecuencia de heartbeat;
- tiempo de estabilización posterior;
- límites de frecuencia de cambios.

Los valores definitivos se decidirán mediante experiencia real.

La administración dispondrá de prioridad sobre cualquier reserva pública.

La reserva deberá asociarse a la vista controlable y no necesariamente al
dispositivo físico completo.

Esto permitirá, por ejemplo, que la panorámica de una OMVI continúe siendo
pública y utilizable mientras la PT está reservada.

---

29. Bloqueo administrativo de posición

Un administrador autorizado podrá fijar una vista PT en una posición
determinada e impedir temporalmente cualquier modificación procedente de
usuarios públicos o registrados.

Esta función está especialmente prevista para situaciones meteorológicas en
las que interese mantener permanentemente un encuadre.

Ejemplo:

Dispositivo: Los Llanos — OMVI principal
Vista física: PT
Vista meteorológica: OESTE

BLOQUEO ADMINISTRATIVO ACTIVO

Motivo:
Seguimiento de tormenta

Mientras exista un bloqueo administrativo:

- el vídeo continuará siendo visible;
- la panorámica podrá continuar funcionando normalmente;
- los usuarios podrán continuar accediendo al directo;
- los controles públicos de cambio de la PT quedarán deshabilitados;
- las solicitudes públicas de movimiento serán rechazadas por la API;
- la PT permanecerá en la vista determinada por Administración.

El bloqueo administrativo tendrá prioridad absoluta sobre las reservas
temporales de usuarios.

Jerarquía conceptual:

1. BLOQUEO ADMINISTRATIVO
         |
         v
2. RESERVA TEMPORAL DE USUARIO
         |
         v
3. VISTA PT LIBRE

El bloqueo no deberá depender exclusivamente del navegador que lo creó.

Su estado deberá persistirse centralmente.

Conceptualmente podrá almacenarse información equivalente a:

vista_fisica_id
bloqueada
vista_autorizada_id
bloqueada_por_usuario_id
bloqueada_desde
motivo

El modelo físico definitivo se decidirá durante la implementación.

Por defecto, un bloqueo administrativo podrá mantenerse hasta que un
administrador autorizado lo libere explícitamente.

No deberá caducar únicamente porque el administrador:

- cierre el navegador;
- cierre sesión;
- pierda conectividad;
- abandone la página.

Otro administrador con permisos suficientes podrá modificar o liberar el
bloqueo.

Todas estas operaciones deberán quedar auditadas posteriormente.

La web pública podrá mostrar, cuando resulte conveniente, que la vista PT ha
sido fijada por MeteoArchidona y el motivo público correspondiente.

---

30. Comunicación con la API MeteoArchidona

MeteoCam deberá estar preparado arquitectónicamente para consumir la API
MeteoArchidona.

La integración no se implementará durante la primera fase, pero será una
capacidad fundamental posterior.

MeteoCam podrá utilizar la API para:

- relacionar su configuración local con dispositivos persistidos centralmente;
- relacionar vistas locales con vistas centrales;
- consultar información de la estación;
- consultar configuración central autorizada;
- informar de su estado;
- informar del estado de dispositivos;
- informar del estado de vistas/streams;
- recibir o consultar órdenes;
- actualizar el progreso de trabajos;
- comunicar errores y resultados;
- participar posteriormente en episodios y automatismos.

Las credenciales de la cámara nunca deberán llegar al navegador público.

La arquitectura será aproximadamente:

Web MeteoArchidona
        |
        | HTTPS
        v
API MeteoArchidona
        |
        v
   PostgreSQL
        ^
        |
        | HTTPS
        |
MeteoCam - Los Llanos
        |
        | LAN
        v
   Dispositivo Reolink
        |
   +----+----+
   |         |
Vista A    Vista B

Debe evitarse depender de conexiones entrantes directas desde Internet hacia
el mini-PC.

Se priorizarán mecanismos en los que MeteoCam inicie las comunicaciones
salientes hacia la API central.

La autenticación y autorización entre MeteoCam y la API se diseñarán antes de
activar esta comunicación en producción.

---

31. Sistema persistente de órdenes

La comunicación remota no se limitará a enviar comandos efímeros desde un
navegador.

Las operaciones que deban sobrevivir al cierre del navegador, a una
desconexión temporal o a un reinicio deberán poder representarse como
órdenes persistentes.

Conceptualmente:

ADMINISTRADOR
      |
      v
WEB METEOARCHIDONA
      |
      v
API METEOARCHIDONA
      |
      v
  POSTGRESQL
      |
      | orden pendiente
      v
   METEOCAM
      |
      v
  DISPOSITIVO
      |
      v
    VISTA

La web solicita la operación.

La API:

1. autentica al usuario;
2. comprueba sus permisos;
3. valida la solicitud;
4. persiste la orden.

MeteoCam consulta periódicamente la API para comprobar si existen órdenes
destinadas a los dispositivos o vistas que controla.

Cuando encuentra una orden válida:

1. la acepta;
2. actualiza su estado;
3. la ejecuta sobre el dispositivo/vista correspondiente;
4. informa del progreso cuando corresponda;
5. informa del resultado;
6. persiste centralmente el estado final mediante la API.

La web no ejecuta físicamente la operación.

La API tampoco deberá convertirse innecesariamente en procesador de vídeo.

MeteoCam es el ejecutor local de los trabajos relacionados con las cámaras.

---

32. Modelo conceptual de órdenes

Se estudiará un sistema general de órdenes en lugar de crear un mecanismo
independiente para cada futura función.

Conceptualmente una orden podrá disponer de información equivalente a:

id
dispositivo_id
vista_id
tipo
estado
parametros
creada_por
creada_en
iniciar_en
finalizar_en
recibida_en
iniciada_en
finalizada_en
resultado
error

"vista_id" podrá ser opcional para operaciones que afecten al dispositivo
completo.

El diseño físico definitivo se realizará cuando se implemente el subsistema.

Los estados podrán incluir inicialmente conceptos como:

PENDIENTE
ACEPTADA
EN_EJECUCION
COMPLETADA
CANCELADA
ERROR

Podrán añadirse otros estados si la implementación real lo necesita.

Entre los tipos futuros de orden podrán existir:

TIMELAPSE
CAPTURAR_IMAGEN
IR_A_VISTA
FIJAR_VISTA
LIBERAR_VISTA
INICIAR_GRABACION
DETENER_GRABACION

Esta enumeración describe capacidades futuras.

No implica que deban implementarse durante la primera fase.

El sistema deberá evitar ejecutar dos veces una misma orden debido a
reintentos, reinicios o problemas de comunicación.

La idempotencia, confirmación de recepción y recuperación después de reinicios
deberán diseñarse antes de activar órdenes reales.

---

33. Timelapses iniciados desde Administración

En una fase futura, un administrador podrá iniciar un timelapse desde el visor
o área administrativa de MeteoArchidona.

La interfaz permitirá seleccionar al menos:

- estación;
- dispositivo;
- vista/canal;
- inicio;
- duración o fecha/hora de finalización;
- intervalo entre capturas.

El intervalo predeterminado será:

1 minuto

El minuto será un valor predeterminado, no necesariamente una limitación
permanente del sistema.

Se podrán estudiar posteriormente otros intervalos según:

- capacidad de la cámara;
- almacenamiento;
- duración;
- finalidad meteorológica;
- carga del mini-PC.

Si el administrador especifica una duración, el sistema podrá calcular la hora
de finalización.

Si especifica directamente la fecha/hora final, se utilizará ese límite.

Ejemplo panorámico:

Dispositivo:   Los Llanos — OMVI principal
Vista:         Panorámica
Inicio:        Ahora
Finalización:  18:30
Intervalo:     1 minuto

[ Iniciar timelapse ]

Ejemplo dirigido:

Dispositivo:   Los Llanos — OMVI principal
Vista:         PT — OESTE
Inicio:        Ahora
Finalización:  18:30
Intervalo:     1 minuto

[ Iniciar timelapse ]

Esto abre la posibilidad futura de mantener simultáneamente:

- un timelapse panorámico general;
- observación PT de un fenómeno concreto.

La concurrencia real y los límites del dispositivo deberán probarse antes de
permitir operaciones simultáneas.

Al confirmar:

1. la web enviará la solicitud a la API;
2. la API validará permisos y parámetros;
3. la API persistirá la orden;
4. el navegador podrá cerrarse sin cancelar el trabajo;
5. MeteoCam detectará la orden;
6. MeteoCam realizará las capturas;
7. MeteoCam controlará el intervalo;
8. MeteoCam controlará la finalización;
9. MeteoCam generará el timelapse según el diseño que se adopte;
10. MeteoCam comunicará el resultado a la API.

La ejecución del timelapse no dependerá de mantener abierta la página web.

---

34. Cancelación y recuperación de trabajos

Un administrador podrá solicitar posteriormente la cancelación de un timelapse
o de otro trabajo cancelable.

La solicitud de cancelación deberá persistirse.

MeteoCam la detectará y realizará una detención ordenada cuando la naturaleza
del trabajo lo permita.

Los trabajos de larga duración deberán diseñarse teniendo en cuenta:

- cierre del navegador;
- caída temporal de Internet;
- caída de la API;
- reinicio de MeteoCam;
- reinicio del mini-PC;
- reinicio de la cámara;
- pérdida de una vista/stream;
- recuperación de conectividad.

La política concreta de recuperación se definirá cuando se implemente este
subsistema.

No se asumirá que una orden ha terminado únicamente porque se haya perdido
temporalmente la comunicación con la API.

---

35. Auditoría de operaciones remotas

Las operaciones administrativas relacionadas con cámaras deberán integrarse
posteriormente con el subsistema general de auditoría de MeteoArchidona.

Deberá poder conocerse, cuando corresponda:

- qué usuario realizó una acción;
- cuándo;
- sobre qué estación;
- sobre qué dispositivo;
- sobre qué vista física;
- qué vista meteorológica seleccionó;
- si fijó una posición;
- cuándo la liberó;
- qué motivo indicó;
- qué timelapse solicitó;
- sus parámetros;
- si solicitó su cancelación;
- cuál fue el resultado.

La auditoría central no sustituye al logging técnico local de MeteoCam.

Ambos sistemas tienen finalidades diferentes:

- auditoría: quién hizo qué desde el sistema;
- logging: qué ocurrió técnicamente durante la ejecución.

---

36. Publicación futura del vídeo

La publicación del vídeo en la web queda fuera de la primera fase.

La cámara no deberá exponerse directamente al navegador público ni deberán
publicarse sus credenciales.

Se estudiarán las alternativas disponibles cuando dispongamos del hardware y
podamos comprobar sus capacidades reales.

Entre las posibilidades estarán:

- servicios proporcionados por Reolink, si resultan adecuados;
- RTSP local hacia MeteoCam;
- HLS;
- WebRTC;
- FFmpeg;
- libVLC;
- servidor de streaming intermedio;
- otras soluciones justificadas técnicamente.

No se tomará una decisión definitiva hasta probar el hardware real.

El diseño debe evitar obligarnos a transcodificar vídeo innecesariamente.

Cuando sea posible, se diferenciará entre:

- stream de visualización;
- stream principal de máxima calidad;
- stream secundario;
- vista panorámica;
- vista PT;
- futuras capturas;
- futuras grabaciones.

La API y el catálogo central permitirán que el visor conozca qué dispositivos y
vistas públicas existen.

El mecanismo concreto utilizado para transportar el vídeo será una decisión
independiente y se determinará mediante pruebas reales.

---

37. Funciones futuras fuera de la primera fase

La arquitectura deberá permitir incorporar posteriormente:

- PTZ;
- presets;
- posición de guardia;
- recorridos panorámicos;
- capacidades multivista;
- catálogo central de dispositivos;
- catálogo central de vistas físicas;
- catálogo central de vistas meteorológicas autorizadas;
- publicación web;
- capturas fotográficas;
- grabación;
- timelapses;
- almacenamiento local;
- retención automática;
- sistema persistente de órdenes;
- bloqueo administrativo;
- episodios meteorológicos;
- protección de archivos pertenecientes a episodios;
- comunicación completa con API MeteoArchidona;
- imagen meteorológica actual;
- administración remota;
- automatismos;
- múltiples dispositivos por estación;
- segunda estación;
- múltiples estaciones y cámaras.

En dispositivos compatibles se podrán investigar además:

- Pinpoint;
- SyncTrack;
- Auto Sweep;
- patrullas;
- otras capacidades específicas del fabricante.

Estas capacidades no justifican introducir complejidad prematuramente.

---

38. Episodios meteorológicos futuros

En una fase posterior MeteoCam podrá reaccionar a episodios meteorológicos.

Ejemplos:

- aumentar frecuencia de capturas;
- conservar fotografías;
- iniciar grabaciones;
- generar timelapses;
- asociar archivos a "episodio_id";
- impedir la eliminación automática de archivos protegidos;
- seleccionar qué vista debe utilizarse.

Un episodio podrá utilizar distintas vistas del mismo dispositivo.

Ejemplo:

Episodio tormentoso
      |
      +---- Panorámica -> contexto general
      |
      +---- PT Oeste -> seguimiento dirigido

Los episodios podrán utilizar en el futuro el mismo mecanismo general de
trabajos u órdenes cuando resulte adecuado.

Esto permitirá que una operación no tenga que proceder necesariamente de una
persona.

Conceptualmente:

Administrador ------+
                    |
Episodio -----------+----> Orden ----> MeteoCam
                    |
Automatización -----+

MeteoCam deberá ejecutar una orden autorizada sin necesitar conocer toda la
lógica meteorológica que originó la decisión.

No se implementará nada de esto durante la primera fase.

---

39. Automatización meteorológica futura

En el futuro podría existir relación entre:

- radar;
- rayos;
- satélite;
- dirección de aproximación de tormentas;
- panorámica;
- presets de la vista PT.

Ejemplo conceptual:

Tormenta aproximándose desde el oeste
             |
             v
Vista PT recomendada: OESTE

La panorámica podría permanecer simultáneamente disponible como contexto
general.

Inicialmente cualquier movimiento será manual.

No se automatizará el movimiento PT utilizando radar hasta disponer de
experiencia suficiente con la cámara real.

El bloqueo administrativo tendrá siempre prioridad sobre automatismos que
pretendan modificar una posición fijada, salvo una acción administrativa
expresamente autorizada para sustituir dicho bloqueo.

---

40. Hoja de ruta

La hoja de ruta constituye la referencia principal para decidir qué trabajo
debe realizarse a continuación.

Cada hito deberá completarse y probarse antes de introducir complejidad
innecesaria del siguiente.

---

HITO 0 — Fundación del repositorio

Estado: EN CURSO

Objetivo:

Crear una base de desarrollo limpia y reproducible antes de comenzar la
aplicación.

Sprint 0.1 — Documentación de arquitectura

Objetivos:

- crear "docs/arquitectura.md";
- documentar alcance;
- documentar decisiones;
- documentar arquitectura;
- establecer hoja de ruta;
- utilizar este documento como referencia de continuidad.

Estado: COMPLETADO

La documentación continuará actualizándose durante todo el proyecto.

Sprint 0.2 — Integración continua

Objetivos:

- crear workflow GitHub Actions;
- ejecutar CI en cada push;
- ejecutar CI en pull requests;
- configurar Python;
- comprobar inicialmente el entorno;
- mantener CI verde desde el comienzo;
- mantener un ciclo de validación rápido compatible con el desarrollo
  incremental archivo a archivo.

Archivo:

.github/workflows/ci.yml

Estado: COMPLETADO

Se comprobó inicialmente la instalación real de las dependencias gráficas.

Posteriormente el workflow principal se optimizó para no descargar e instalar
PySide6 y Qt en cada push.

El CI rápido instala el proyecto sin sus dependencias gráficas pesadas y
realiza las comprobaciones básicas del paquete.

Cuando las pruebas gráficas lo requieran se incorporarán comprobaciones
específicas sin penalizar innecesariamente todos los commits del proyecto.

Sprint 0.3 — Proyecto Python

Objetivos:

- crear "pyproject.toml";
- definir nombre y versión;
- establecer Python compatible;
- declarar dependencias iniciales;
- preparar instalación editable;
- preparar pytest.

Estado: COMPLETADO

La dependencia gráfica inicial es PySide6.

La estructura utiliza el directorio "src".

Sprint 0.4 — Primer test

Objetivos:

- incorporar ejecución real de pytest al CI;
- crear primer test mínimo;
- comprobar instalación del paquete;
- garantizar CI verde;
- mantener el workflow rápido.

Estado: PENDIENTE

---

HITO 1 — Primera aplicación de escritorio

Estado: PENDIENTE

Objetivo:

Conseguir que MeteoCam arranque como aplicación PySide6 real.

Sprint 1.1 — Paquete MeteoCam

Objetivos:

- crear estructura "src/meteocam";
- definir versión;
- crear punto de entrada;
- comprobar importación del paquete.

Estado: EN CURSO

Ya se han completado:

- creación de "src/meteocam";
- creación del paquete;
- definición inicial de versión;
- comprobación de importación desde CI.

Queda pendiente el punto de entrada de la aplicación.

Sprint 1.2 — Ventana principal

Objetivos:

- iniciar QApplication;
- crear ventana principal;
- título MeteoCam;
- mostrar versión;
- cierre limpio;
- interfaz mínima.

La primera ventana no necesita todavía conectarse a ninguna cámara.

Sprint 1.3 — Esqueleto visual

Objetivos:

Mostrar inicialmente:

- estación;
- dispositivo;
- vista seleccionada cuando corresponda;
- estado;
- zona reservada para vídeo;
- botón Configuración;
- botón Diagnóstico.

La estructura visual deberá permitir posteriormente más de una vista
simultánea sin obligar a rediseñar completamente la ventana.

Aplicar progresivamente la identidad visual:

- MeteoCam Classic Claro;
- MeteoCam Classic Oscuro;
- cambio de tema en ejecución;
- persistencia de la preferencia.

No implementar todavía funcionalidad compleja detrás de los botones.

---

HITO 2 — Dominio de cámaras

Estado: PENDIENTE

Objetivo:

Separar completamente la aplicación del fabricante y representar correctamente
dispositivos con una o varias vistas.

Sprint 2.1 — Modelos básicos

Crear modelos para:

- estación;
- dispositivo de cámara;
- vista/canal;
- stream;
- configuración;
- identificación;
- stream preferido;
- capacidades;
- futura referencia a identificadores centrales.

No introducir complejidad innecesaria.

El modelo deberá admitir:

dispositivo de una vista
dispositivo de varias vistas

sin requerir clases específicas en la GUI.

Sprint 2.2 — Estados

Crear el sistema formal de estados:

- DESCONECTADA;
- CONECTANDO;
- CONECTADA;
- SIN_VIDEO;
- ERROR_AUTENTICACION;
- REINTENTANDO;
- ERROR.

Preparar la posibilidad de estados por vista/stream cuando resulte necesario.

Sprint 2.3 — Abstracción Camera

Definir la interfaz común que utilizará la aplicación.

Solo se incluirán operaciones necesarias para la fase actual.

La abstracción deberá permitir consultar las vistas disponibles de un
dispositivo.

No añadir anticipadamente métodos de grabación, episodios o automatización.

Sprint 2.4 — SimulatedCamera

Implementar una cámara simulada que permita:

- conectar;
- desconectar;
- consultar estado;
- exponer una o varias vistas simuladas;
- simular streams;
- simular éxito;
- simular errores;
- probar la GUI sin hardware.

Se deberá poder simular al menos:

- una cámara convencional de una vista;
- un dispositivo tipo OMVI con panorámica + PT.

---

HITO 3 — Logging y errores

Estado: PENDIENTE

Objetivo:

Instrumentar MeteoCam antes de empezar las integraciones reales.

Sprint 3.1 — Logging persistente

Implementar:

- fichero de log;
- rotación;
- niveles;
- inicio/cierre;
- excepciones;
- cambios de estado.

Sprint 3.2 — Protección de secretos

Implementar mecanismos para impedir que aparezcan:

- contraseñas;
- credenciales;
- URLs RTSP completas con secretos.

Sprint 3.3 — Catálogo de errores

Crear las familias:

- CAM-NET;
- CAM-DISCOVERY;
- CAM-AUTH;
- CAM-RTSP;
- CAM-STREAM;
- CAM-CHANNEL;
- CAM-ONVIF;
- CAM-PTZ;
- CAM-API;
- CAM-JOB.

---

HITO 4 — Configuración de cámaras

Estado: PENDIENTE

Objetivo:

Poder administrar dispositivos sin depender todavía de descubrimiento
automático.

Sprint 4.1 — Persistencia local

Implementar repositorio local de configuración.

Sprint 4.2 — Gestión de estaciones

Permitir seleccionar/asociar un dispositivo a una estación.

Primera estación:

Los Llanos

Sprint 4.3 — Añadir cámara manualmente

Campos iniciales:

- estación;
- nombre;
- fabricante;
- modelo;
- IP;
- usuario;
- contraseña.

La configuración de vistas y streams deberá poder ampliarse cuando se conozca
el hardware real.

Sprint 4.4 — Editar y eliminar

Permitir:

- editar dispositivo;
- eliminar dispositivo;
- confirmar operaciones destructivas.

---

HITO 5 — Diagnóstico simulado

Estado: PENDIENTE

Objetivo:

Construir el sistema de diagnóstico antes de depender del hardware real.

Sprint 5.1 — Motor de diagnóstico

Definir etapas y resultados.

Incluir conceptualmente:

- dispositivo;
- servicios;
- vistas/canales;
- streams.

Sprint 5.2 — Diagnóstico visual

Mostrar:

- hora;
- etapa;
- dispositivo;
- vista cuando corresponda;
- estado;
- código de error;
- explicación.

Sprint 5.3 — Simulación de fallos

Simular:

- red inaccesible;
- autenticación incorrecta;
- RTSP no disponible;
- vista no disponible;
- stream no disponible;
- fallo parcial de un dispositivo multivista;
- recuperación.

Sprint 5.4 — Informe

Generar informe de diagnóstico sin secretos.

---

HITO 6 — Descubrimiento LAN

Estado: PENDIENTE

Objetivo:

Preparar el sistema Plug & Play.

Sprint 6.1 — Interfaz de descubrimiento

Separar completamente descubrimiento y dispositivos.

Sprint 6.2 — WS-Discovery / ONVIF

Investigar e implementar cuando proceda.

Sprint 6.3 — Reolink

Comprobar con hardware real qué mecanismos adicionales son útiles.

Investigar especialmente:

- identificación de modelo;
- canales;
- vistas;
- RTSP;
- ONVIF;
- CGI/API;
- capacidades PT;
- presets.

Sprint 6.4 — Integración GUI

Implementar:

Buscar cámaras automáticamente

Mostrar dispositivos encontrados y permitir convertir un descubrimiento en una
configuración persistente.

La entrada manual continuará existiendo siempre.

---

HITO 7 — Hardware Reolink real

Estado: PENDIENTE

Este hito comenzará cuando dispongamos físicamente de la cámara seleccionada
para Los Llanos.

La candidata preferente actual es la Reolink OMVI 3i PoE.

La arquitectura no dependerá de que finalmente se adquiera ese modelo.

Sprint 7.1 — Primer descubrimiento

Objetivo:

Encontrar la cámara conectada en Los Llanos.

Sprint 7.2 — Identificación

Obtener todo lo posible automáticamente:

- IP;
- fabricante;
- modelo;
- firmware;
- servicios;
- vistas/canales;
- capacidades.

Sprint 7.3 — Autenticación

Introducir las credenciales de forma segura y comprobar acceso.

Sprint 7.4 — Servicios

Comprobar:

- conectividad;
- HTTP/HTTPS;
- RTSP;
- ONVIF;
- CGI/API cuando proceda;
- otros servicios relevantes.

Sprint 7.5 — Investigación multicanal OMVI

Si la cámara seleccionada es la OMVI, determinar experimentalmente:

- cómo identifica internamente la panorámica;
- cómo identifica internamente la PT;
- qué canales expone por RTSP;
- qué perfiles expone por ONVIF;
- stream principal panorámico;
- stream secundario panorámico;
- stream principal PT;
- stream secundario PT;
- codecs;
- resoluciones;
- acceso simultáneo;
- límites de conexiones;
- comportamiento ante reinicios.

No se codificará ninguna correspondencia de canales hasta haberla comprobado.

Sprint 7.6 — Capacidades de control

Comprobar qué operaciones pueden realizarse desde software externo:

- PT;
- presets;
- posición de guardia;
- patrulla;
- Pinpoint;
- SyncTrack;
- Auto Sweep;
- otras funciones descubiertas.

Cada función deberá quedar clasificada como:

SOPORTADA
NO SOPORTADA
PARCIAL
PENDIENTE
SOLO SOFTWARE REOLINK

Sprint 7.7 — ReolinkCamera

Implementar el adaptador real utilizando únicamente capacidades comprobadas.

---

HITO 8 — Vídeo real

Estado: PENDIENTE

Objetivo:

Conseguir el primer directo estable dentro de MeteoCam.

Sprint 8.1 — Pruebas de streams

Comprobar para cada vista:

- stream principal;
- stream secundario;
- resolución;
- códec;
- bitrate;
- estabilidad.

Para OMVI se comprobarán independientemente:

PANORÁMICA
    MAIN
    SUB

PT
    MAIN
    SUB

Sprint 8.2 — Selección del motor

Comparar según sea necesario:

- libVLC;
- FFmpeg;
- Qt Multimedia.

Elegir basándonos en pruebas reales.

Sprint 8.3 — Visor

Integrar vídeo en la ventana PySide6.

Comenzar por una vista estable.

Después, si el hardware y el rendimiento lo permiten, probar visualización
simultánea de varias vistas.

Sprint 8.4 — Reconexión

Probar:

- desconexión de Ethernet;
- reinicio de cámara;
- caída RTSP;
- caída de un único stream;
- recuperación;
- credenciales incorrectas.

Sprint 8.5 — Rendimiento

Medir:

- CPU;
- memoria;
- aceleración de vídeo disponible;
- estabilidad;
- temperatura si resulta relevante;
- diferencia entre stream principal y secundario;
- coste de reproducir dos vistas simultáneamente.

---

HITO 9 — Integración con API y catálogo central

Estado: FUTURO

Objetivo:

Relacionar MeteoCam con la infraestructura central de MeteoArchidona sin
exponer las cámaras directamente a Internet.

Implementar progresivamente:

- cliente API desacoplado;
- autenticación segura de MeteoCam;
- asociación entre dispositivo local y dispositivo central;
- asociación de vistas;
- catálogo persistente de cámaras/dispositivos;
- catálogo de vistas;
- estado online/offline;
- heartbeat cuando resulte necesario;
- comunicación saliente desde MeteoCam;
- recuperación ante pérdida de conexión.

La integración deberá mantener separados:

- catálogo central;
- configuración privada local;
- secretos del hardware.

---

HITO 10 — PTZ local

Estado: FUTURO

No comenzar hasta completar satisfactoriamente la fase de vídeo.

Objetivos futuros:

- comprobar capacidades PT reales;
- movimiento administrativo;
- zoom;
- presets;
- creación de vistas autorizadas;
- posición de guardia;
- referencia lógica Sur;
- probar límites seguros.

En dispositivos multivista, las operaciones se dirigirán únicamente a la vista
con capacidad PT.

---

HITO 11 — Observación panorámica meteorológica

Estado: FUTURO

Objetivo:

Aprovechar de manera óptima las capacidades panorámicas y PT disponibles.

Si el dispositivo dispone de panorámica fija

Ejemplo OMVI:

Utilizar la panorámica de 180 grados como vista meteorológica general
permanente.

Comprobar físicamente:

- orientación;
- horizonte cubierto;
- cielo cubierto;
- deformaciones;
- unión de las lentes;
- exposición;
- comportamiento nocturno;
- utilidad meteorológica;
- privacidad.

Vista PT

Crear el recorrido autorizado candidato:

NO -> O -> SO -> S -> SE -> E -> NE

Comprobar físicamente:

- encuadres;
- privacidad;
- límites;
- velocidad;
- suavidad;
- tiempos de permanencia;
- retorno;
- comportamiento mecánico.

Determinar si se implementa mediante:

- presets;
- control MeteoCam;
- funciones internas de la cámara.

La panorámica fija y el recorrido PT son funciones complementarias y no
excluyentes.

---

HITO 12 — Catálogo central de vistas y control administrativo

Estado: FUTURO

Objetivo:

Persistir las vistas autorizadas y permitir su administración central.

Implementar:

- vistas físicas asociadas a dispositivo;
- vistas meteorológicas asociadas a vistas físicas;
- activación/desactivación;
- publicación;
- orden;
- vista predeterminada;
- asociación con presets internos;
- bloqueo administrativo persistente;
- vista fijada;
- motivo del bloqueo;
- liberación administrativa;
- auditoría.

La API será la autoridad que determine qué vistas pueden ofrecerse al visor.

---

HITO 13 — Sistema persistente de órdenes

Estado: FUTURO

Objetivo:

Permitir que MeteoCam ejecute trabajos solicitados desde la infraestructura
central.

Implementar:

- creación de órdenes;
- persistencia;
- identificación de dispositivo;
- identificación de vista cuando corresponda;
- consulta desde MeteoCam;
- aceptación;
- ejecución;
- estados;
- resultados;
- errores;
- cancelación;
- idempotencia;
- recuperación después de reinicios;
- auditoría.

No depender de una conexión entrante directa al mini-PC.

---

HITO 14 — Publicación del directo

Estado: FUTURO

Objetivo:

Mostrar las cámaras en la web pública de MeteoArchidona.

Investigar con hardware real:

- capacidades Reolink;
- publicación independiente de vistas;
- publicación simultánea de panorámica y PT;
- posibilidad de publicación sin transcodificación;
- HLS;
- WebRTC;
- infraestructura necesaria;
- ancho de banda;
- número de espectadores;
- latencia;
- costes.

La visualización de las cámaras públicas no requerirá registro.

---

HITO 15 — Selector público de vistas

Estado: FUTURO

Objetivo:

Permitir que la web construya dinámicamente el selector utilizando los
dispositivos y vistas publicados por la API.

Implementar:

- catálogo de dispositivos publicables;
- catálogo de vistas físicas publicables;
- catálogo de vistas meteorológicas publicables;
- generación dinámica del selector;
- API de selección;
- validación servidor;
- política de acceso para visitantes y usuarios registrados;
- reserva temporal por sesión cuando proceda;
- heartbeat;
- expiración;
- periodo de estabilización;
- prioridad administrativa;
- bloqueo administrativo;
- protección contra abuso.

La panorámica fija podrá permanecer disponible independientemente de la reserva
de la vista PT.

Nunca implementar PTZ público libre.

---

HITO 16 — Capturas, almacenamiento y timelapses

Estado: FUTURO

Objetivos:

- fotografías;
- grabación;
- almacenamiento local;
- retención;
- timelapses;
- selección de vista origen.

Para los timelapses administrativos:

- permitir seleccionar panorámica o vista PT cuando proceda;
- permitir inicio desde la web;
- persistir la orden;
- aceptar duración o fecha/hora final;
- intervalo predeterminado de 1 minuto;
- ejecutar físicamente en MeteoCam;
- permitir cancelación;
- comunicar progreso y resultado.

No comenzar hasta disponer de una instalación estable.

---

HITO 17 — Episodios meteorológicos

Estado: FUTURO

Objetivos:

- asociación con episodios;
- protección de archivos;
- aumento de frecuencia;
- grabaciones condicionadas;
- timelapses condicionados;
- selección automática o manual de vistas;
- generación automática de órdenes;
- automatismos meteorológicos.

---

41. Estado actual del proyecto

Completado

- creación del repositorio "MeteoCam";
- definición del objetivo general;
- elección de Python;
- elección de PySide6/Qt;
- selección inicial de Reolink TrackMix PoE;
- incorporación de Reolink OMVI 3i PoE como candidata preferente;
- mantenimiento de TrackMix como alternativa compatible;
- elección de Los Llanos como instalación piloto;
- definición conceptual de arquitectura;
- generalización de cámara a dispositivo físico;
- incorporación del concepto de vista/canal;
- incorporación del concepto de streams por vista;
- preparación para dispositivos de una o varias vistas;
- identificación conceptual de panorámica + PT para OMVI;
- definición de modo simulado;
- definición conceptual del diagnóstico;
- ampliación del diagnóstico para dispositivos multivista;
- definición conceptual del logging;
- definición de restricciones de PTZ público;
- definición del recorrido PT meteorológico candidato;
- diferenciación entre panorámica fija y recorrido PT;
- incorporación como futuribles de posición de guardia, presets, patrulla,
  Pinpoint, SyncTrack y otras capacidades específicas;
- definición conceptual de reserva pública por sesión;
- adaptación de la reserva para aplicarse a vistas controlables;
- creación de "docs/arquitectura.md";
- creación de ".github/workflows/ci.yml";
- creación de "pyproject.toml";
- creación de "src/meteocam/__init__.py";
- definición inicial de versión del paquete;
- comprobación de importación del paquete en CI;
- comprobación inicial de instalación de PySide6 en CI;
- optimización posterior del CI para evitar instalar dependencias gráficas
  pesadas en cada push;
- definición de los temas MeteoCam Classic Claro y Classic Oscuro;
- decisión de cambio de tema en ejecución y persistencia local;
- definición de integración futura con la API MeteoArchidona;
- separación entre configuración privada local y catálogo central;
- definición conceptual del catálogo persistente de dispositivos;
- definición conceptual del catálogo persistente de vistas físicas;
- definición conceptual del catálogo persistente de vistas autorizadas;
- decisión de construir dinámicamente el selector web desde la API;
- decisión de mantener pública la visualización de cámaras públicas sin exigir
  registro;
- previsión de funcionalidades adicionales para usuarios registrados;
- definición del bloqueo administrativo persistente de posición;
- adaptación del bloqueo a la vista PT sin afectar necesariamente a la
  panorámica;
- definición de prioridad administrativa sobre reservas públicas;
- definición conceptual del sistema persistente de órdenes;
- adaptación de órdenes para poder dirigirse a dispositivo o vista;
- definición de MeteoCam como ejecutor local de trabajos;
- definición conceptual de timelapses iniciados desde Administración;
- posibilidad futura de seleccionar vista de origen del timelapse;
- intervalo predeterminado de timelapse de 1 minuto;
- previsión de cancelación, recuperación y trazabilidad de trabajos.

En curso

- HITO 0 — Fundación del repositorio;
- Sprint 1.1 parcialmente iniciado mediante la creación del paquete base.

Siguiente trabajo

El siguiente paso continúa siendo:

Sprint 0.4 — Primer test

El cambio de cámara candidata y la generalización multivista no alteran el
siguiente trabajo inmediato.

Crear el primer test mínimo del paquete y hacer que el workflow rápido ejecute
realmente pytest.

Objetivos inmediatos:

1. crear el directorio de pruebas;
2. crear el primer test;
3. ejecutar pytest desde GitHub Actions;
4. mantener CI verde y rápido.

Después de completar Sprint 0.4 se cerrará el HITO 0.

A continuación se retomará:

Sprint 1.1 — Paquete MeteoCam

El siguiente objetivo será crear el punto de entrada de la aplicación.

Posteriormente:

Sprint 1.2 — Ventana principal

Se comenzará la primera aplicación PySide6 ejecutable.

La generalización de dispositivo/vistas deberá respetarse progresivamente
durante el HITO 2, sin introducir anticipadamente complejidad que todavía no
sea necesaria.

---

42. Reglas de desarrollo

El desarrollo se realizará incrementalmente.

Flujo preferido:

1. un archivo por paso cuando sea razonable;
2. indicar siempre la ruta exacta;
3. proporcionar el contenido completo cuando se cree o sustituya un archivo;
4. evitar parches parciales cuando se vaya a sustituir el fichero;
5. proporcionar mensaje de commit separado;
6. commit/push;
7. comprobar CI;
8. continuar con el siguiente paso.

El usuario trabaja frecuentemente desde móvil.

Los bloques deberán facilitar copiar y pegar.

Todos los archivos Python del proyecto deberán terminar con la marca de fin de
fichero establecida para el proyecto.

Además, todos los archivos entregados durante el desarrollo deberán finalizar
con una marca que identifique claramente el final y la ruta completa del
archivo.

Ejemplo para Python:

# Fin archivo: src/meteocam/main.py

Ejemplo para YAML:

# Fin archivo: .github/workflows/ci.yml

Para Markdown se utilizará:

<!-- Fin archivo: docs/arquitectura.md -->

El CI principal deberá mantenerse deliberadamente rápido.

No se instalarán dependencias gráficas pesadas en cada push si la comprobación
que se está realizando no las necesita.

Las comprobaciones gráficas específicas se incorporarán cuando sean necesarias
sin penalizar innecesariamente el ciclo normal de desarrollo archivo a archivo.

---

43. Principio de detección de capacidades

MeteoCam no deberá determinar las capacidades operativas de un dispositivo
únicamente por su fabricante y modelo.

El modelo conocido podrá utilizarse como información orientativa.

La capacidad efectiva deberá obtenerse, cuando sea posible, mediante:

- descubrimiento;
- consulta al dispositivo;
- perfiles ONVIF;
- servicios disponibles;
- pruebas RTSP;
- mecanismos específicos del fabricante;
- configuración persistida después de una comprobación real.

Esto resulta especialmente importante en dispositivos nuevos o cuyo firmware
evoluciona.

Una misma familia de cámara podrá comportarse de manera diferente según:

- revisión de hardware;
- versión de firmware;
- configuración;
- servicios habilitados;
- compatibilidad del protocolo utilizado.

Por ello MeteoCam distinguirá conceptualmente entre:

CAPACIDAD ESPERADA
CAPACIDAD DETECTADA
CAPACIDAD COMPROBADA

Las funciones críticas deberán apoyarse preferentemente en capacidades
comprobadas.

Ejemplo:

Dispositivo: Reolink OMVI 3i PoE

Esperado:
    panorámica........ sí
    PT................ sí
    RTSP.............. sí
    presets........... sí

Detectado:
    vistas............ 2
    RTSP.............. sí

Comprobado:
    panorámica MAIN... OK
    panorámica SUB.... OK
    PT MAIN........... OK
    PT SUB............ OK
    presets........... pendiente

Esta filosofía será especialmente útil durante la primera instalación real.

---

44. Principio multivista

La arquitectura de MeteoCam deberá tratar como conceptos diferentes:

ESTACIÓN
    |
    v
DISPOSITIVO FÍSICO
    |
    v
VISTA / CANAL
    |
    v
STREAM

Ejemplo OMVI:

LOS LLANOS
    |
    v
OMVI PRINCIPAL
    |
    +---- PANORÁMICA
    |        |
    |        +---- MAIN
    |        |
    |        +---- SUB
    |
    +---- PT
             |
             +---- MAIN
             |
             +---- SUB

Ejemplo cámara convencional:

ESTACIÓN
    |
    v
CÁMARA FIJA
    |
    v
PRINCIPAL
    |
    +---- MAIN
    |
    +---- SUB

Por tanto, la arquitectura multivista no obliga a que todas las cámaras tengan
varias vistas.

Simplemente elimina la restricción artificial de asumir una única vista por
dispositivo.

Esta decisión deberá aplicarse con proporcionalidad.

No será necesario crear desde el primer sprint todas las clases, tablas o
interfaces futuras.

Se incorporarán cuando la hoja de ruta llegue al dominio correspondiente.

---

45. Principio rector

MeteoCam debe crecer por necesidades reales y comprobadas.

No se introducirán prematuramente componentes complejos únicamente porque
puedan ser útiles en el futuro.

La prioridad será siempre:

1. funcionamiento;
2. diagnóstico;
3. estabilidad;
4. seguridad;
5. simplicidad;
6. capacidad de evolución.

La primera gran prueba real del proyecto será:

«Conectar la cámara Reolink seleccionada en Los Llanos, abrir MeteoCam,
encontrarla, configurarla, descubrir sus capacidades reales, diagnosticarla
y conseguir vídeo en directo estable.»

Si la cámara seleccionada finalmente es la Reolink OMVI 3i PoE, una segunda
gran validación técnica consistirá en:

«Detectar correctamente sus vistas panorámica y PT, identificar sus streams
de forma independiente y conseguir reproducir ambas fuentes de manera
controlada sin acoplar la aplicación a identificadores internos específicos
del fabricante.»

Todo el diseño de la primera fase debe conducir de forma progresiva y
comprobable hacia esos objetivos.

Una vez establecida esa base, MeteoCam podrá evolucionar desde una aplicación
local de control hacia un agente distribuido de MeteoArchidona capaz de
ejecutar de forma segura, persistente y auditable operaciones sobre los
dispositivos y vistas de cada estación.

La panorámica permanente y la vista PT de dispositivos como la OMVI permiten
además un modelo especialmente apropiado para observación meteorológica:

«mantener siempre el contexto general del cielo mientras una segunda vista
observa de forma dirigida el fenómeno meteorológico de interés.»

Esta posibilidad deberá aprovecharse cuando las pruebas reales demuestren que
puede implementarse de manera estable y segura, sin convertir una capacidad
prometedora del hardware en una dependencia prematura del proyecto.

<!-- Fin archivo: docs/arquitectura.md -->