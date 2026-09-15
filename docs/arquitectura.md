# MeteoCam — Arquitectura y hoja de ruta

## 1. Identificación del proyecto

**Nombre del repositorio:** MeteoCam  
**Nombre provisional de la aplicación:** MeteoArchidona Camera Agent  
**Nombre corto:** MeteoCam  
**Proyecto:** MeteoArchidona  
**Lenguaje principal:** Python  
**Interfaz gráfica prevista:** PySide6 / Qt  

MeteoCam es el software de escritorio encargado de gestionar, monitorizar,
diagnosticar y controlar las cámaras IP instaladas en las estaciones
meteorológicas de MeteoArchidona.

La aplicación se ejecutará inicialmente en un mini-PC situado en la estación
meteorológica y conectado a la misma red local que las cámaras.

La primera instalación piloto se realizará en la estación **Los Llanos**,
situada en Villanueva del Trabuco.

La primera cámara prevista es una **Reolink TrackMix PoE**.

---

## 2. Objetivo general

El objetivo inicial de MeteoCam es conseguir una experiencia de uso lo más
próxima posible a:

> Enchufar la cámara, abrir MeteoCam, encontrarla, configurarla y verla.

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

---

## 3. Alcance de la primera fase

La primera fase debe proporcionar una aplicación de escritorio funcional y una
arquitectura preparada para trabajar posteriormente con la cámara real.

Debe incluir progresivamente:

- aplicación de escritorio;
- interfaz PySide6;
- abstracción de cámaras;
- cámara simulada;
- gestión de estaciones y cámaras;
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
- conexión posterior con Reolink TrackMix PoE;
- reproducción estable del vídeo en directo;
- reconexión controlada.

La primera fase NO debe incluir todavía:

- grabación de vídeo;
- almacenamiento de fotografías;
- timelapses;
- episodios meteorológicos;
- sincronización con PostgreSQL;
- integración completa con la API central de MeteoArchidona;
- automatismos meteorológicos;
- publicación pública del vídeo;
- control PTZ remoto desde la web;
- movimientos automáticos basados en radar.

Estas funciones quedan previstas arquitectónicamente, pero no deben complicar
la primera implementación.

---

## 4. Primera instalación física

### 4.1 Estación piloto

**Estación:** Los Llanos  
**Localidad:** Villanueva del Trabuco  
**Proyecto:** MeteoArchidona  

La primera instalación se realizará en Los Llanos.

El Silo será una instalación posterior si el piloto funciona correctamente.

### 4.2 Cámara

Primera cámara prevista:

**Reolink TrackMix PoE**

Características relevantes para el proyecto:

- cámara IP;
- alimentación PoE;
- doble objetivo;
- resolución máxima aproximada 4K / 8 MP;
- PTZ;
- aproximadamente 355 grados de movimiento horizontal;
- aproximadamente 90 grados de movimiento vertical;
- zoom híbrido;
- streams de diferente calidad;
- RTSP;
- protocolos de integración de red;
- presets PTZ.

Las capacidades concretas utilizadas por MeteoCam deberán comprobarse con el
hardware y firmware reales antes de considerarlas definitivas.

### 4.3 Red física

La instalación prevista es:

    ROUTER
       |
       | Ethernet existente
       |
       v
      BAR
       |
       v
    SWITCH PoE GIGABIT
       |
       +----> Televisión / otros dispositivos
       |
       +----> Cat6 exterior con PoE
                  |
                  v
               TEJADO
                  |
                  v
          REOLINK TRACKMIX PoE

En este proyecto, **el bar** es el nombre utilizado para la zona techada con
porche de Los Llanos donde llega actualmente un cable Ethernet directo desde
el router y existen enchufes eléctricos.

El switch previsto será aproximadamente de 4/5 puertos, Gigabit y PoE activo
IEEE 802.3af/at.

No habrá inicialmente:

- NVR;
- grabador dedicado;
- SAI/UPS.

El mini-PC será el elemento inteligente de gestión y procesamiento.

---

## 5. Arquitectura de red básica

La TrackMix no es una webcam USB.

Es una cámara IP conectada a la LAN.

La comunicación local será aproximadamente:

    TrackMix PoE
          |
          | Ethernet
          |
      Switch PoE
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
- stream principal;
- stream secundario;
- parámetros adicionales descubiertos durante las pruebas reales.

Las credenciales nunca estarán escritas directamente en el código fuente.

---

## 6. Arquitectura lógica

La interfaz gráfica no debe depender directamente de Reolink, RTSP, ONVIF ni
ningún fabricante concreto.

La arquitectura conceptual inicial será:

                +-------------------+
                |        GUI        |
                |      PySide6      |
                +---------+---------+
                          |
                          v
                +-------------------+
                | Camera abstraction|
                +---------+---------+
                          |
              +-----------+-----------+
              |                       |
              v                       v
    +-------------------+   +-------------------+
    | SimulatedCamera   |   |  ReolinkCamera    |
    +-------------------+   +---------+---------+
                                      |
                                      v
                              TrackMix / red local

La aplicación deberá poder desarrollarse y probarse inicialmente utilizando
`SimulatedCamera`.

Cuando llegue la cámara física se incorporará `ReolinkCamera` sin obligar a
reescribir la interfaz gráfica.

---

## 7. Entidad estación y entidad cámara

MeteoCam debe estar preparada desde el principio para múltiples estaciones y
múltiples cámaras.

No se debe identificar una cámara únicamente por su IP.

Conceptualmente existirán al menos:

### Estación

Ejemplo:

    Nombre: Los Llanos
    Localidad: Villanueva del Trabuco

### Cámara

Ejemplo:

    Nombre: TrackMix principal
    Estación: Los Llanos
    Fabricante: Reolink
    Modelo: TrackMix PoE
    IP: 192.168.x.x
    Usuario: ...
    Contraseña: ...
    Stream preferido: secundario

Una estación podrá disponer en el futuro de más de una cámara.

---

## 8. Configuración local

En la primera fase no se utilizará PostgreSQL para almacenar la configuración
de MeteoCam.

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

---

## 9. Primer arranque

Si no existe ninguna cámara configurada, MeteoCam deberá ofrecer una
experiencia aproximadamente equivalente a:

    No hay cámaras configuradas.

    [ Buscar cámaras automáticamente ]
    [ Añadir cámara manualmente ]

El procedimiento ideal cuando llegue la TrackMix será:

1. conectar la TrackMix al switch PoE;
2. esperar su arranque;
3. abrir MeteoCam;
4. seleccionar "Buscar cámaras";
5. detectar la Reolink;
6. mostrar la información descubierta;
7. seleccionar la cámara;
8. solicitar únicamente los datos que falten;
9. probar los servicios disponibles;
10. guardar la configuración;
11. mostrar vídeo en directo.

La detección automática nunca será requisito obligatorio.

Siempre existirá la alternativa de configuración manual.

---

## 10. Descubrimiento automático

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

---

## 11. Sistema de estados

Las cámaras tendrán estados explícitos.

Como mínimo se prevén:

- DESCONECTADA;
- CONECTANDO;
- CONECTADA;
- SIN_VIDEO;
- ERROR_AUTENTICACION;
- REINTENTANDO;
- ERROR.

Los estados deberán poder ampliarse posteriormente sin depender de textos
mostrados directamente en la GUI.

La interfaz representará estos estados de manera comprensible para el usuario.

---

## 12. Operaciones asíncronas

Ninguna operación potencialmente lenta debe bloquear el hilo principal de Qt.

Esto incluye:

- descubrimiento de dispositivos;
- conexión de red;
- comprobaciones HTTP/HTTPS;
- ONVIF;
- RTSP;
- apertura del stream;
- reconexión;
- diagnósticos.

La interfaz debe permanecer operativa incluso cuando una cámara no responda.

---

## 13. Vídeo en directo

La primera versión con hardware real únicamente reproducirá vídeo.

No grabará nada.

Cadena conceptual:

    TrackMix
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
7. facilidad de distribución.

Cuando sea conveniente, el visor permanente podrá utilizar un stream de menor
resolución y reservar el stream principal de máxima calidad para futuras
funciones de captura o grabación.

---

## 14. Diagnóstico

El diagnóstico es un requisito fundamental del proyecto.

La aplicación no deberá limitarse a mostrar mensajes genéricos como:

> No se pudo conectar.

Una prueba de conexión deberá ejecutar comprobaciones progresivas.

Ejemplo conceptual:

    Iniciando diagnóstico: Los Llanos
    IP configurada: 192.168.1.50

    Comprobando accesibilidad de red...
    OK

    Comprobando servicios...
    OK

    Comprobando RTSP...
    OK

    Comprobando autenticación...
    OK

    Solicitando stream principal...
    OK

    Códec detectado: H.265
    Resolución detectada: 3840 x 2160

    RESULTADO:
    CÁMARA OPERATIVA

Si una etapa falla, las etapas dependientes podrán aparecer como no probadas.

---

## 15. Códigos de error

Los errores tendrán códigos internos estructurados por subsistema.

Familias inicialmente reservadas:

- `CAM-NET-xxx`
- `CAM-DISCOVERY-xxx`
- `CAM-AUTH-xxx`
- `CAM-RTSP-xxx`
- `CAM-STREAM-xxx`
- `CAM-ONVIF-xxx`
- `CAM-PTZ-xxx`

Ejemplo:

    CAM-RTSP-002

Cada código deberá permitir asociar:

- subsistema;
- descripción;
- etapa;
- información técnica;
- causas probables;
- posibles comprobaciones.

PTZ dispondrá de su espacio de códigos aunque no se implemente en la primera
fase.

---

## 16. Logging

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
- cambios de estado;
- intentos de conexión;
- conexiones;
- desconexiones;
- reconexiones;
- errores RTSP;
- errores de autenticación;
- errores del motor de vídeo;
- excepciones;
- resultados de diagnóstico.

Nunca se registrarán:

- contraseñas;
- secretos;
- credenciales completas;
- URLs que incorporen credenciales sin enmascarar.

---

## 17. Informe de diagnóstico

MeteoCam deberá poder generar posteriormente un informe técnico fácilmente
compartible.

Ejemplo:

    MeteoArchidona Camera Agent
    Diagnóstico

    Estación: Los Llanos
    Cámara: TrackMix principal
    Versión: 0.1.0

    Red.................... OK
    IP..................... 192.168.1.50
    Conectividad........... OK
    HTTP/HTTPS............. OK
    RTSP................... ERROR
    Autenticación.......... NO PROBADA
    Stream principal....... NO PROBADO
    Motor de vídeo......... OK

    Último error:
    CAM-RTSP-002

El informe nunca incluirá contraseñas ni secretos.

Su finalidad será permitir reproducir y localizar rápidamente problemas cuando
se trabaje con hardware real.

---

## 18. Reconexión

MeteoCam deberá asumir que una cámara IP puede:

- reiniciarse;
- desaparecer temporalmente;
- perder conectividad;
- perder RTSP;
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

La política exacta de tiempos y reintentos se determinará durante la
implementación y las pruebas reales.

---

## 19. PTZ administrativo futuro

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
- selección de presets.

Este control libre será exclusivamente administrativo o de mantenimiento.

Nunca se expondrá el control PTZ libre a usuarios públicos.

---

## 20. Presets y vistas públicas

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

El usuario público únicamente podrá seleccionar **vistas previamente
configuradas, verificadas y autorizadas por MeteoArchidona**.

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

---

## 21. Referencia lógica de orientación

Para MeteoCam se podrá utilizar el **Sur como referencia lógica**.

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

No se debe asumir que corresponden a las coordenadas internas de Reolink.

Durante la instalación real se orientará la cámara y se crearán presets
visualmente comprobados.

MeteoCam trabajará con nombres semánticos y no necesitará exponer al usuario
las coordenadas internas de la cámara.

---

## 22. Panorámica meteorológica autorizada

Se prevé un recorrido panorámico específicamente diseñado para observación
meteorológica.

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

La TrackMix dispone aproximadamente de 355 grados de recorrido horizontal, por
lo que mecánicamente existe margen suficiente, sujeto a comprobación con la
instalación real.

La panorámica no será un movimiento elegido libremente por el visitante.

Será una secuencia completamente definida y autorizada por MeteoArchidona.

Podrá implementarse mediante:

- una secuencia controlada de presets;
- movimiento PTZ controlado por MeteoCam;
- una función de patrulla propia de la cámara, si finalmente resulta adecuada.

La solución definitiva se decidirá después de probar el hardware.

---

## 23. Reserva futura del selector público

Cuando se habilite el selector público de vistas, no se permitirá que múltiples
usuarios cambien continuamente la orientación.

Se prevé un sistema de **reserva temporal por sesión**.

Conceptualmente:

1. un usuario entra en los controles;
2. la API intenta adquirir una reserva temporal de la cámara;
3. si está libre, la sesión obtiene temporalmente el selector de vistas;
4. solamente esa sesión puede solicitar presets públicos durante la reserva;
5. otras sesiones pueden continuar viendo el vídeo;
6. la reserva se mantiene mediante actividad o heartbeat;
7. si la sesión desaparece, la reserva caduca automáticamente;
8. después de liberar el control puede aplicarse un periodo de estabilización;
9. durante ese periodo se mantiene la última vista elegida;
10. posteriormente la cámara vuelve a quedar disponible.

La reserva concede únicamente derecho a seleccionar **presets autorizados**.

Nunca concede PTZ libre.

Se estudiarán parámetros como:

- duración máxima de turno;
- tiempo máximo de inactividad;
- frecuencia de heartbeat;
- tiempo de estabilización posterior;
- límites de frecuencia de cambios.

Los valores definitivos se decidirán mediante experiencia real.

La administración podrá disponer de prioridad sobre una reserva pública cuando
sea necesario por mantenimiento, diagnóstico o seguimiento meteorológico.

---

## 24. Comunicación futura con MeteoArchidona

Las credenciales de la cámara nunca deberán llegar al navegador público.

La arquitectura futura será aproximadamente:

    Web MeteoArchidona
            |
            | solicitud autorizada
            v
    API MeteoArchidona
            |
            | orden validada
            v
    MeteoCam - Los Llanos
            |
            | LAN
            v
    Reolink TrackMix

La API central decidirá:

- quién puede solicitar una vista;
- qué vistas están publicadas;
- si existe una reserva activa;
- si la sesión es propietaria de la reserva;
- si existe un periodo de estabilización;
- si la orden está permitida.

MeteoCam será responsable de traducir la orden autorizada a la operación
concreta sobre la cámara.

---

## 25. Publicación futura del vídeo

La publicación del vídeo en la web queda fuera de la primera fase.

La cámara no deberá exponerse directamente al navegador público ni deberán
publicarse sus credenciales.

Se estudiarán las alternativas disponibles cuando dispongamos de la TrackMix y
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
- futuras capturas;
- futuras grabaciones.

---

## 26. Funciones futuras fuera de la primera fase

La arquitectura deberá permitir incorporar posteriormente:

- PTZ;
- presets;
- recorridos panorámicos;
- publicación web;
- capturas fotográficas;
- grabación;
- timelapses;
- almacenamiento local;
- retención automática;
- episodios meteorológicos;
- protección de archivos pertenecientes a episodios;
- comunicación completa con API MeteoArchidona;
- imagen meteorológica actual;
- administración remota;
- automatismos;
- segunda cámara;
- segunda estación;
- múltiples estaciones y cámaras.

Estas capacidades no justifican introducir complejidad prematuramente.

---

## 27. Episodios meteorológicos futuros

En una fase posterior MeteoCam podrá reaccionar a episodios meteorológicos.

Ejemplos:

- aumentar frecuencia de capturas;
- conservar fotografías;
- iniciar grabaciones;
- generar timelapses;
- asociar archivos a `episodio_id`;
- impedir la eliminación automática de archivos protegidos.

No se implementará nada de esto durante la primera fase.

---

## 28. Automatización meteorológica futura

En el futuro podría existir relación entre:

- radar;
- rayos;
- dirección de aproximación de tormentas;
- presets de cámara.

Ejemplo conceptual:

    Tormenta aproximándose desde el oeste
                 |
                 v
    Preset recomendado: OESTE

Inicialmente cualquier movimiento será manual.

No se automatizará el movimiento PTZ utilizando radar hasta disponer de
experiencia suficiente con la cámara real.

---

# 29. Hoja de ruta

La hoja de ruta constituye la referencia principal para decidir qué trabajo
debe realizarse a continuación.

Cada hito deberá completarse y probarse antes de introducir complejidad
innecesaria del siguiente.

---

## HITO 0 — Fundación del repositorio

**Estado:** EN CURSO

Objetivo:

Crear una base de desarrollo limpia y reproducible antes de comenzar la
aplicación.

### Sprint 0.1 — Documentación de arquitectura

Objetivos:

- crear `docs/arquitectura.md`;
- documentar alcance;
- documentar decisiones;
- documentar arquitectura;
- establecer hoja de ruta;
- utilizar este documento como referencia de continuidad.

**Estado:** EN CURSO

### Sprint 0.2 — Integración continua

Objetivos:

- crear workflow GitHub Actions;
- ejecutar CI en cada push;
- ejecutar CI en pull requests;
- configurar Python;
- comprobar inicialmente el entorno;
- mantener CI verde desde el comienzo.

Archivo previsto:

    .github/workflows/ci.yml

**Estado:** PENDIENTE

### Sprint 0.3 — Proyecto Python

Objetivos:

- crear `pyproject.toml`;
- definir nombre y versión;
- establecer Python compatible;
- declarar dependencias iniciales;
- preparar instalación editable;
- preparar pytest.

**Estado:** PENDIENTE

### Sprint 0.4 — Primer test

Objetivos:

- incorporar pytest al CI;
- crear primer test mínimo;
- comprobar instalación del paquete;
- garantizar CI verde.

**Estado:** PENDIENTE

---

## HITO 1 — Primera aplicación de escritorio

**Estado:** PENDIENTE

Objetivo:

Conseguir que MeteoCam arranque como aplicación PySide6 real.

### Sprint 1.1 — Paquete MeteoCam

Objetivos:

- crear estructura `src/meteocam`;
- definir versión;
- crear punto de entrada;
- comprobar importación del paquete.

### Sprint 1.2 — Ventana principal

Objetivos:

- iniciar QApplication;
- crear ventana principal;
- título MeteoCam;
- mostrar versión;
- cierre limpio;
- interfaz mínima.

La primera ventana no necesita todavía conectarse a ninguna cámara.

### Sprint 1.3 — Esqueleto visual

Objetivos:

Mostrar inicialmente:

- estación;
- cámara;
- estado;
- zona reservada para vídeo;
- botón Configuración;
- botón Diagnóstico.

No implementar todavía funcionalidad compleja detrás de los botones.

---

## HITO 2 — Dominio de cámaras

**Estado:** PENDIENTE

Objetivo:

Separar completamente la aplicación del fabricante de la cámara.

### Sprint 2.1 — Modelos básicos

Crear modelos para:

- estación;
- cámara;
- configuración;
- identificación;
- stream preferido.

### Sprint 2.2 — Estados

Crear el sistema formal de estados:

- DESCONECTADA;
- CONECTANDO;
- CONECTADA;
- SIN_VIDEO;
- ERROR_AUTENTICACION;
- REINTENTANDO;
- ERROR.

### Sprint 2.3 — Abstracción Camera

Definir la interfaz común que utilizará la aplicación.

Solo se incluirán operaciones necesarias para la fase actual.

No añadir anticipadamente métodos de grabación, episodios o automatización.

### Sprint 2.4 — SimulatedCamera

Implementar una cámara simulada que permita:

- conectar;
- desconectar;
- consultar estado;
- simular éxito;
- simular errores;
- probar la GUI sin hardware.

---

## HITO 3 — Logging y errores

**Estado:** PENDIENTE

Objetivo:

Instrumentar MeteoCam antes de empezar las integraciones reales.

### Sprint 3.1 — Logging persistente

Implementar:

- fichero de log;
- rotación;
- niveles;
- inicio/cierre;
- excepciones;
- cambios de estado.

### Sprint 3.2 — Protección de secretos

Implementar mecanismos para impedir que aparezcan:

- contraseñas;
- credenciales;
- URLs RTSP completas con secretos.

### Sprint 3.3 — Catálogo de errores

Crear las familias:

- CAM-NET;
- CAM-DISCOVERY;
- CAM-AUTH;
- CAM-RTSP;
- CAM-STREAM;
- CAM-ONVIF;
- CAM-PTZ.

---

## HITO 4 — Configuración de cámaras

**Estado:** PENDIENTE

Objetivo:

Poder administrar cámaras sin depender todavía de descubrimiento automático.

### Sprint 4.1 — Persistencia local

Implementar repositorio local de configuración.

### Sprint 4.2 — Gestión de estaciones

Permitir seleccionar/asociar una cámara a una estación.

Primera estación:

    Los Llanos

### Sprint 4.3 — Añadir cámara manualmente

Campos iniciales:

- estación;
- nombre;
- fabricante;
- modelo;
- IP;
- usuario;
- contraseña;
- stream.

### Sprint 4.4 — Editar y eliminar

Permitir:

- editar cámara;
- eliminar cámara;
- confirmar operaciones destructivas.

---

## HITO 5 — Diagnóstico simulado

**Estado:** PENDIENTE

Objetivo:

Construir el sistema de diagnóstico antes de depender de la TrackMix.

### Sprint 5.1 — Motor de diagnóstico

Definir etapas y resultados.

### Sprint 5.2 — Diagnóstico visual

Mostrar:

- hora;
- etapa;
- estado;
- código de error;
- explicación.

### Sprint 5.3 — Simulación de fallos

Simular:

- red inaccesible;
- autenticación incorrecta;
- RTSP no disponible;
- stream no disponible;
- recuperación.

### Sprint 5.4 — Informe

Generar informe de diagnóstico sin secretos.

---

## HITO 6 — Descubrimiento LAN

**Estado:** PENDIENTE

Objetivo:

Preparar el sistema Plug & Play.

### Sprint 6.1 — Interfaz de descubrimiento

Separar completamente descubrimiento y cámaras.

### Sprint 6.2 — WS-Discovery / ONVIF

Investigar e implementar cuando proceda.

### Sprint 6.3 — Reolink

Comprobar con hardware real qué mecanismos adicionales son útiles.

### Sprint 6.4 — Integración GUI

Implementar:

    Buscar cámaras automáticamente

Mostrar dispositivos encontrados y permitir convertir un descubrimiento en una
configuración persistente.

La entrada manual continuará existiendo siempre.

---

## HITO 7 — Red y TrackMix real

**Estado:** PENDIENTE

Este hito comenzará cuando dispongamos físicamente de la Reolink TrackMix PoE.

### Sprint 7.1 — Primer descubrimiento

Objetivo:

Encontrar la TrackMix conectada en Los Llanos.

### Sprint 7.2 — Identificación

Obtener todo lo posible automáticamente:

- IP;
- fabricante;
- modelo;
- servicios;
- capacidades.

### Sprint 7.3 — Autenticación

Introducir las credenciales de forma segura y comprobar acceso.

### Sprint 7.4 — Servicios

Comprobar:

- conectividad;
- HTTP/HTTPS;
- RTSP;
- ONVIF;
- otros servicios relevantes.

### Sprint 7.5 — ReolinkCamera

Implementar el adaptador real utilizando únicamente capacidades comprobadas.

---

## HITO 8 — Vídeo real

**Estado:** PENDIENTE

Objetivo:

Conseguir el primer directo estable dentro de MeteoCam.

### Sprint 8.1 — Pruebas de streams

Comprobar:

- stream principal;
- stream secundario;
- resolución;
- códec;
- bitrate;
- estabilidad.

### Sprint 8.2 — Selección del motor

Comparar según sea necesario:

- libVLC;
- FFmpeg;
- Qt Multimedia.

Elegir basándonos en pruebas reales.

### Sprint 8.3 — Visor

Integrar vídeo en la ventana PySide6.

### Sprint 8.4 — Reconexión

Probar:

- desconexión de Ethernet;
- reinicio de cámara;
- caída RTSP;
- recuperación;
- credenciales incorrectas.

### Sprint 8.5 — Rendimiento

Medir:

- CPU;
- memoria;
- aceleración de vídeo disponible;
- estabilidad;
- temperatura si resulta relevante;
- diferencia entre stream principal y secundario.

---

## HITO 9 — PTZ local

**Estado:** FUTURO

No comenzar hasta completar satisfactoriamente la fase de vídeo.

Objetivos futuros:

- comprobar capacidades PTZ reales;
- movimiento administrativo;
- zoom;
- presets;
- creación de vistas autorizadas;
- referencia lógica Sur;
- probar límites seguros.

---

## HITO 10 — Panorámica meteorológica

**Estado:** FUTURO

Objetivo:

Crear el recorrido autorizado:

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
- patrulla de cámara.

---

## HITO 11 — Comunicación remota

**Estado:** FUTURO

Objetivo:

Permitir comunicación segura entre MeteoCam y la infraestructura central de
MeteoArchidona.

No exponer directamente la cámara a Internet.

Estudiar:

- autenticación;
- autorización;
- conexión saliente desde MeteoCam;
- heartbeat;
- estado online/offline;
- recepción segura de órdenes.

---

## HITO 12 — Publicación del directo

**Estado:** FUTURO

Objetivo:

Mostrar las cámaras en la web pública de MeteoArchidona.

Investigar con hardware real:

- capacidades Reolink;
- posibilidad de publicación sin transcodificación;
- HLS;
- WebRTC;
- infraestructura necesaria;
- ancho de banda;
- número de espectadores;
- latencia;
- costes.

---

## HITO 13 — Selector público de vistas

**Estado:** FUTURO

Objetivo:

Permitir que usuarios de la web seleccionen únicamente vistas autorizadas.

Implementar:

- catálogo de vistas publicables;
- API de selección;
- validación servidor;
- reserva temporal por sesión;
- heartbeat;
- expiración;
- periodo de estabilización;
- prioridad administrativa;
- protección contra abuso.

Nunca implementar PTZ público libre.

---

## HITO 14 — Capturas y almacenamiento

**Estado:** FUTURO

Objetivos:

- fotografías;
- grabación;
- almacenamiento local;
- retención;
- timelapses.

No comenzar hasta disponer de una instalación estable.

---

## HITO 15 — Episodios meteorológicos

**Estado:** FUTURO

Objetivos:

- asociación con episodios;
- protección de archivos;
- aumento de frecuencia;
- grabaciones condicionadas;
- automatismos meteorológicos.

---

# 30. Estado actual del proyecto

A fecha de creación inicial de este documento:

### Completado

- creación del repositorio `MeteoCam`;
- definición del objetivo general;
- elección inicial de Python;
- elección inicial de PySide6/Qt;
- selección de Reolink TrackMix PoE;
- elección de Los Llanos como instalación piloto;
- definición conceptual de arquitectura;
- definición de modo simulado;
- definición conceptual del diagnóstico;
- definición conceptual del logging;
- definición de restricciones de PTZ público;
- definición del recorrido panorámico candidato;
- definición conceptual de reserva pública por sesión.

### En curso

- documentación inicial de arquitectura.

### Siguiente trabajo

Una vez incorporado este documento y comprobado el commit:

**Sprint 0.2 — Integración continua**

Crear:

    .github/workflows/ci.yml

El workflow deberá ejecutarse inicialmente en cada push y pull request y
mantenerse verde desde el primer momento.

Después:

**Sprint 0.3 — Proyecto Python**

Crear:

    pyproject.toml

No avanzar a la aplicación PySide6 hasta disponer de una base Python y CI
reproducibles.

---

# 31. Reglas de desarrollo

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

Todos los archivos Python del proyecto deberán terminar exactamente con una
marca de fin de fichero adecuada.

Además, todos los archivos entregados durante el desarrollo deberán finalizar
con una marca que identifique claramente el final y la ruta completa del
archivo.

Ejemplo para Python:

    # Fin archivo: src/meteocam/main.py

Ejemplo para YAML:

    # Fin archivo: .github/workflows/ci.yml

Para Markdown se utilizará:

    <!-- Fin archivo: docs/arquitectura.md -->

---

# 32. Principio rector

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

> Conectar la Reolink TrackMix PoE en Los Llanos, abrir MeteoCam, encontrarla,
> configurarla, diagnosticarla y conseguir vídeo en directo estable.

Todo el diseño de la primera fase debe conducir de forma progresiva y
comprobable hacia ese objetivo.

<!-- Fin archivo: docs/arquitectura.md -->