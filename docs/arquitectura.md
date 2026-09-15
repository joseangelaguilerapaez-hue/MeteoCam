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

MeteoCam se concibe desde el principio no solamente como visor local de una
cámara, sino como el **agente local encargado de ejecutar sobre las cámaras
físicas las operaciones autorizadas por la infraestructura de
MeteoArchidona**.

En fases posteriores podrá comunicarse con la API central de MeteoArchidona,
sin exponer directamente las cámaras ni sus credenciales a Internet.

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

A largo plazo MeteoCam actuará también como puente seguro entre la
infraestructura central de MeteoArchidona y las cámaras instaladas en cada
estación.

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
- sincronización operativa con PostgreSQL;
- integración completa con la API central de MeteoArchidona;
- automatismos meteorológicos;
- publicación pública del vídeo;
- control PTZ remoto desde la web;
- movimientos automáticos basados en radar.

Estas funciones quedan previstas arquitectónicamente, pero no deben complicar
la primera implementación.

La arquitectura y los identificadores utilizados desde el comienzo deberán
permitir que una cámara configurada localmente pueda relacionarse en el futuro
con su correspondiente entidad persistida en la API y PostgreSQL de
MeteoArchidona.

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

Además de la identificación local, una cámara podrá disponer posteriormente de
un identificador central que la relacione con la entidad correspondiente
persistida en PostgreSQL a través de la API MeteoArchidona.

---

## 8. Configuración local

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

### Configuración privada local

Información necesaria para que MeteoCam controle físicamente la cámara:

- dirección IP de la LAN;
- usuario;
- contraseña;
- puertos;
- URLs o parámetros internos;
- capacidades descubiertas;
- configuración específica del hardware.

### Catálogo central

Información funcional que MeteoArchidona necesita conocer:

- identificador de cámara;
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
- diagnósticos;
- futuras consultas a la API MeteoArchidona;
- futuras consultas de órdenes persistidas.

La interfaz debe permanecer operativa incluso cuando una cámara o un servicio
remoto no responda.

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

## 14. Identidad visual y temas

MeteoCam utilizará una estética de aplicación de escritorio clásica y técnica.

No se pretende reproducir el estilo visual de una aplicación web moderna.

La interfaz utilizará **Qt Widgets** y hojas de estilo **QSS** para conservar
un aspecto de cliente pesado tradicional:

- paneles grises o metálicos;
- botones con relieve;
- bordes biselados;
- marcos hundidos;
- pestañas clásicas;
- controles claramente delimitados;
- jerarquía visual propia de aplicaciones técnicas de escritorio.

Se definen inicialmente dos temas oficiales:

### MeteoCam Classic Claro

Tema clásico claro basado principalmente en:

- grises claros;
- plata;
- paneles con relieve;
- controles tridimensionales;
- marcos técnicos;
- contraste elevado.

### MeteoCam Classic Oscuro

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

## 15. Diagnóstico

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

## 16. Códigos de error

Los errores tendrán códigos internos estructurados por subsistema.

Familias inicialmente reservadas:

- `CAM-NET-xxx`
- `CAM-DISCOVERY-xxx`
- `CAM-AUTH-xxx`
- `CAM-RTSP-xxx`
- `CAM-STREAM-xxx`
- `CAM-ONVIF-xxx`
- `CAM-PTZ-xxx`
- `CAM-API-xxx`
- `CAM-JOB-xxx`

Ejemplo:

    CAM-RTSP-002

Cada código deberá permitir asociar:

- subsistema;
- descripción;
- etapa;
- información técnica;
- causas probables;
- posibles comprobaciones.

PTZ, API y ejecución de trabajos dispondrán de sus espacios de códigos aunque
no se implementen en la primera fase.

---

## 17. Logging

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

## 18. Informe de diagnóstico

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

## 19. Reconexión

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

## 20. Catálogo central de cámaras

Las cámaras de MeteoArchidona deberán estar representadas posteriormente en la
base de datos PostgreSQL central.

La API será la única interfaz utilizada por la web para consultar y administrar
este catálogo.

Conceptualmente existirá una relación:

    ESTACIÓN
        |
        | 1:N
        v
    CÁMARAS

Una entidad de cámara central podrá contener, entre otros campos que se
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

No se considera necesario almacenar centralmente las credenciales privadas de
la cámara para que el visor público pueda funcionar.

La información privada necesaria para controlar físicamente la cámara
permanecerá en MeteoCam.

El catálogo central permitirá que la web consulte dinámicamente qué cámaras
existen y cuáles deben aparecer en el selector.

No deberán codificarse manualmente las cámaras disponibles dentro del
JavaScript del visor.

Ejemplo conceptual:

    API
     |
     +---- Los Llanos
     |       |
     |       +---- TrackMix principal
     |
     +---- El Silo
             |
             +---- Cámara principal

Añadir o retirar una cámara pública deberá poder reflejarse en el visor sin
necesidad de modificar manualmente su código fuente.

---

## 21. Vistas y presets persistidos

Las vistas públicas autorizadas de cada cámara deberán persistirse también en
la infraestructura central.

No deberán estar codificadas directamente en el visor web.

Conceptualmente:

    CÁMARA
      |
      | 1:N
      v
    VISTAS AUTORIZADAS

Una entidad de vista podrá incluir posteriormente:

    id
    camara_id
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

La web consultará la API para conocer qué vistas debe mostrar para la cámara
seleccionada.

Ejemplo:

    Los Llanos — TrackMix principal

    [ OESTE ]
    [ SUROESTE ]
    [ SUR ]
    [ SURESTE ]
    [ ESTE ]
    [ PANORÁMICA ]

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

## 22. PTZ administrativo futuro

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

## 23. Presets y vistas públicas

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
habilitada para su tipo de acceso, **vistas previamente configuradas,
verificadas y autorizadas por MeteoArchidona**.

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

## 24. Acceso público y usuarios registrados

La visualización en directo de las cámaras marcadas como públicas no requerirá
registro en MeteoArchidona.

Principio funcional:

> Las cámaras públicas podrán visualizarse en directo sin necesidad de iniciar
> sesión.

El hecho de que una cámara sea pública no implica que todas sus funcionalidades
de control sean públicas.

Determinadas funciones adicionales podrán reservarse posteriormente a usuarios
registrados.

La política concreta se diseñará cuando se implemente el visor y el subsistema
de control.

No se decide todavía si determinadas acciones, como adquirir temporalmente el
selector de vistas, estarán disponibles:

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

### Visitante

Podrá visualizar las cámaras públicas sin registrarse.

Las funcionalidades adicionales dependerán de la política que se establezca.

### Usuario registrado

Podrá visualizar igualmente las cámaras públicas y podrá disponer de
funcionalidades adicionales que se definan posteriormente.

### Administrador

Dispondrá de las funciones de administración, mantenimiento y control
autorizadas, incluyendo aquellas que nunca deben estar disponibles
públicamente.

---

## 25. Referencia lógica de orientación

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

## 26. Panorámica meteorológica autorizada

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

## 27. Reserva futura del selector público

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

La administración dispondrá de prioridad sobre cualquier reserva pública.

---

## 28. Bloqueo administrativo de posición

Un administrador autorizado podrá fijar una cámara en una posición determinada
e impedir temporalmente cualquier modificación procedente de usuarios
públicos o registrados.

Esta función está especialmente prevista para situaciones meteorológicas en
las que interese mantener permanentemente un encuadre.

Ejemplo:

    Cámara: Los Llanos — TrackMix principal
    Vista: OESTE

    BLOQUEO ADMINISTRATIVO ACTIVO

    Motivo:
    Seguimiento de tormenta

Mientras exista un bloqueo administrativo:

- el vídeo continuará siendo visible;
- los usuarios podrán continuar accediendo al directo;
- los controles públicos de cambio de vista quedarán deshabilitados;
- las solicitudes públicas de movimiento serán rechazadas por la API;
- la cámara permanecerá en la vista determinada por Administración.

El bloqueo administrativo tendrá prioridad absoluta sobre las reservas
temporales de usuarios.

Jerarquía conceptual:

    1. BLOQUEO ADMINISTRATIVO
             |
             v
    2. RESERVA TEMPORAL DE USUARIO
             |
             v
    3. CÁMARA LIBRE

El bloqueo no deberá depender exclusivamente del navegador que lo creó.

Su estado deberá persistirse centralmente.

Conceptualmente podrá almacenarse información equivalente a:

    camara_id
    bloqueada
    vista_fijada_id
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

La web pública podrá mostrar, cuando resulte conveniente, que la vista ha sido
fijada por MeteoArchidona y el motivo público correspondiente.

---

## 29. Comunicación con la API MeteoArchidona

MeteoCam deberá estar preparado arquitectónicamente para consumir la API
MeteoArchidona.

La integración no se implementará durante la primera fase, pero será una
capacidad fundamental posterior.

MeteoCam podrá utilizar la API para:

- relacionar su configuración local con cámaras persistidas centralmente;
- consultar información de la estación;
- consultar configuración central autorizada;
- informar de su estado;
- informar del estado de las cámaras;
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
    Reolink TrackMix

Debe evitarse depender de conexiones entrantes directas desde Internet hacia
el mini-PC.

Se priorizarán mecanismos en los que MeteoCam inicie las comunicaciones
salientes hacia la API central.

La autenticación y autorización entre MeteoCam y la API se diseñarán antes de
activar esta comunicación en producción.

---

## 30. Sistema persistente de órdenes

La comunicación remota no se limitará a enviar comandos efímeros desde un
navegador.

Las operaciones que deban sobrevivir al cierre del navegador, a una
desconexión temporal o a un reinicio deberán poder representarse como
**órdenes persistentes**.

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
        CÁMARA

La web solicita la operación.

La API:

1. autentica al usuario;
2. comprueba sus permisos;
3. valida la solicitud;
4. persiste la orden.

MeteoCam consulta periódicamente la API para comprobar si existen órdenes
destinadas a las cámaras que controla.

Cuando encuentra una orden válida:

1. la acepta;
2. actualiza su estado;
3. la ejecuta sobre la cámara;
4. informa del progreso cuando corresponda;
5. informa del resultado;
6. persiste centralmente el estado final mediante la API.

La web no ejecuta físicamente la operación.

La API tampoco deberá convertirse innecesariamente en procesador de vídeo.

**MeteoCam es el ejecutor local de los trabajos relacionados con la cámara.**

---

## 31. Modelo conceptual de órdenes

Se estudiará un sistema general de órdenes en lugar de crear un mecanismo
independiente para cada futura función.

Conceptualmente una orden podrá disponer de información equivalente a:

    id
    camara_id
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

## 32. Timelapses iniciados desde Administración

En una fase futura, un administrador podrá iniciar un timelapse desde el visor
o área administrativa de MeteoArchidona.

La interfaz permitirá seleccionar al menos:

- cámara;
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

Conceptualmente:

    Cámara:       Los Llanos — TrackMix principal
    Inicio:       Ahora
    Finalización: 18:30
    Intervalo:    1 minuto

    [ Iniciar timelapse ]

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

## 33. Cancelación y recuperación de trabajos

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
- recuperación de conectividad.

La política concreta de recuperación se definirá cuando se implemente este
subsistema.

No se asumirá que una orden ha terminado únicamente porque se haya perdido
temporalmente la comunicación con la API.

---

## 34. Auditoría de operaciones remotas

Las operaciones administrativas relacionadas con cámaras deberán integrarse
posteriormente con el subsistema general de auditoría de MeteoArchidona.

Deberá poder conocerse, cuando corresponda:

- qué usuario realizó una acción;
- cuándo;
- sobre qué cámara;
- qué vista seleccionó;
- si fijó una posición;
- cuándo la liberó;
- qué motivo indicó;
- qué timelapse solicitó;
- sus parámetros;
- si solicitó su cancelación;
- cuál fue el resultado.

La auditoría central no sustituye al logging técnico local de MeteoCam.

Ambos sistemas tienen finalidades diferentes:

- **auditoría:** quién hizo qué desde el sistema;
- **logging:** qué ocurrió técnicamente durante la ejecución.

---

## 35. Publicación futura del vídeo

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

La API y el catálogo central permitirán que el visor conozca qué cámaras
públicas existen.

El mecanismo concreto utilizado para transportar el vídeo será una decisión
independiente y se determinará mediante pruebas reales.

---

## 36. Funciones futuras fuera de la primera fase

La arquitectura deberá permitir incorporar posteriormente:

- PTZ;
- presets;
- recorridos panorámicos;
- catálogo central de cámaras;
- catálogo central de vistas;
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
- segunda cámara;
- segunda estación;
- múltiples estaciones y cámaras.

Estas capacidades no justifican introducir complejidad prematuramente.

---

## 37. Episodios meteorológicos futuros

En una fase posterior MeteoCam podrá reaccionar a episodios meteorológicos.

Ejemplos:

- aumentar frecuencia de capturas;
- conservar fotografías;
- iniciar grabaciones;
- generar timelapses;
- asociar archivos a `episodio_id`;
- impedir la eliminación automática de archivos protegidos.

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

## 38. Automatización meteorológica futura

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

El bloqueo administrativo tendrá siempre prioridad sobre automatismos que
pretendan modificar una posición fijada, salvo una acción administrativa
expresamente autorizada para sustituir dicho bloqueo.

---

# 39. Hoja de ruta

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

**Estado:** COMPLETADO

La documentación continuará actualizándose durante todo el proyecto.

### Sprint 0.2 — Integración continua

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

**Estado:** COMPLETADO

Se comprobó inicialmente la instalación real de las dependencias gráficas.

Posteriormente el workflow principal se optimizó para no descargar e instalar
PySide6 y Qt en cada push.

El CI rápido instala el proyecto sin sus dependencias gráficas pesadas y
realiza las comprobaciones básicas del paquete.

Cuando las pruebas gráficas lo requieran se incorporarán comprobaciones
específicas sin penalizar innecesariamente todos los commits del proyecto.

### Sprint 0.3 — Proyecto Python

Objetivos:

- crear `pyproject.toml`;
- definir nombre y versión;
- establecer Python compatible;
- declarar dependencias iniciales;
- preparar instalación editable;
- preparar pytest.

**Estado:** COMPLETADO

La dependencia gráfica inicial es PySide6.

La estructura utiliza el directorio `src`.

### Sprint 0.4 — Primer test

Objetivos:

- incorporar ejecución real de pytest al CI;
- crear primer test mínimo;
- comprobar instalación del paquete;
- garantizar CI verde;
- mantener el workflow rápido.

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

**Estado:** EN CURSO

Ya se han completado:

- creación de `src/meteocam`;
- creación del paquete;
- definición inicial de versión;
- comprobación de importación desde CI.

Queda pendiente el punto de entrada de la aplicación.

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

Aplicar progresivamente la identidad visual:

- MeteoCam Classic Claro;
- MeteoCam Classic Oscuro;
- cambio de tema en ejecución;
- persistencia de la preferencia.

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
- stream preferido;
- futura referencia a identificador central.

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
- CAM-PTZ;
- CAM-API;
- CAM-JOB.

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

## HITO 9 — Integración con API y catálogo central

**Estado:** FUTURO

Objetivo:

Relacionar MeteoCam con la infraestructura central de MeteoArchidona sin
exponer las cámaras directamente a Internet.

Implementar progresivamente:

- cliente API desacoplado;
- autenticación segura de MeteoCam;
- asociación entre cámara local y cámara central;
- catálogo persistente de cámaras;
- estado online/offline;
- heartbeat cuando resulte necesario;
- comunicación saliente desde MeteoCam;
- recuperación ante pérdida de conexión.

La integración deberá mantener separados:

- catálogo central;
- configuración privada local;
- secretos del hardware.

---

## HITO 10 — PTZ local

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

## HITO 11 — Panorámica meteorológica

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

## HITO 12 — Catálogo central de vistas y control administrativo

**Estado:** FUTURO

Objetivo:

Persistir las vistas autorizadas y permitir su administración central.

Implementar:

- vistas asociadas a cámara;
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

## HITO 13 — Sistema persistente de órdenes

**Estado:** FUTURO

Objetivo:

Permitir que MeteoCam ejecute trabajos solicitados desde la infraestructura
central.

Implementar:

- creación de órdenes;
- persistencia;
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

## HITO 14 — Publicación del directo

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

La visualización de las cámaras públicas no requerirá registro.

---

## HITO 15 — Selector público de vistas

**Estado:** FUTURO

Objetivo:

Permitir que la web construya dinámicamente el selector utilizando las cámaras
y vistas publicadas por la API.

Implementar:

- catálogo de cámaras publicables;
- catálogo de vistas publicables;
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

Nunca implementar PTZ público libre.

---

## HITO 16 — Capturas, almacenamiento y timelapses

**Estado:** FUTURO

Objetivos:

- fotografías;
- grabación;
- almacenamiento local;
- retención;
- timelapses.

Para los timelapses administrativos:

- permitir inicio desde la web;
- persistir la orden;
- aceptar duración o fecha/hora final;
- intervalo predeterminado de 1 minuto;
- ejecutar físicamente en MeteoCam;
- permitir cancelación;
- comunicar progreso y resultado.

No comenzar hasta disponer de una instalación estable.

---

## HITO 17 — Episodios meteorológicos

**Estado:** FUTURO

Objetivos:

- asociación con episodios;
- protección de archivos;
- aumento de frecuencia;
- grabaciones condicionadas;
- timelapses condicionados;
- generación automática de órdenes;
- automatismos meteorológicos.

---

# 40. Estado actual del proyecto

## Completado

- creación del repositorio `MeteoCam`;
- definición del objetivo general;
- elección de Python;
- elección de PySide6/Qt;
- selección de Reolink TrackMix PoE;
- elección de Los Llanos como instalación piloto;
- definición conceptual de arquitectura;
- definición de modo simulado;
- definición conceptual del diagnóstico;
- definición conceptual del logging;
- definición de restricciones de PTZ público;
- definición del recorrido panorámico candidato;
- definición conceptual de reserva pública por sesión;
- creación de `docs/arquitectura.md`;
- creación de `.github/workflows/ci.yml`;
- creación de `pyproject.toml`;
- creación de `src/meteocam/__init__.py`;
- definición inicial de versión del paquete;
- comprobación de importación del paquete en CI;
- comprobación inicial de instalación de PySide6 en CI;
- optimización posterior del CI para evitar instalar dependencias gráficas
  pesadas en cada push;
- definición de los temas MeteoCam Classic Claro y Classic Oscuro;
- decisión de cambio de tema en ejecución y persistencia local;
- definición de integración futura con la API MeteoArchidona;
- separación entre configuración privada local y catálogo central;
- definición conceptual del catálogo persistente de cámaras;
- definición conceptual del catálogo persistente de vistas/presets;
- decisión de construir dinámicamente el selector web desde la API;
- decisión de mantener pública la visualización de cámaras públicas sin exigir
  registro;
- previsión de funcionalidades adicionales para usuarios registrados;
- definición del bloqueo administrativo persistente de posición;
- definición de prioridad administrativa sobre reservas públicas;
- definición conceptual del sistema persistente de órdenes;
- definición de MeteoCam como ejecutor local de trabajos;
- definición conceptual de timelapses iniciados desde Administración;
- intervalo predeterminado de timelapse de 1 minuto;
- previsión de cancelación, recuperación y trazabilidad de trabajos.

## En curso

- HITO 0 — Fundación del repositorio;
- Sprint 1.1 parcialmente iniciado mediante la creación del paquete base.

## Siguiente trabajo

El siguiente paso será:

**Sprint 0.4 — Primer test**

Crear el primer test mínimo del paquete y hacer que el workflow rápido ejecute
realmente pytest.

Objetivos inmediatos:

1. crear el directorio de pruebas;
2. crear el primer test;
3. ejecutar pytest desde GitHub Actions;
4. mantener CI verde y rápido.

Después de completar Sprint 0.4 se cerrará el HITO 0.

A continuación se retomará:

**Sprint 1.1 — Paquete MeteoCam**

El siguiente objetivo será crear el punto de entrada de la aplicación.

Posteriormente:

**Sprint 1.2 — Ventana principal**

Se comenzará la primera aplicación PySide6 ejecutable.

---

# 41. Reglas de desarrollo

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

# 42. Principio rector

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

Una vez establecida esa base, MeteoCam podrá evolucionar desde una aplicación
local de control hacia un agente distribuido de MeteoArchidona capaz de
ejecutar de forma segura, persistente y auditable operaciones sobre las cámaras
de cada estación.

<!-- Fin archivo: docs/arquitectura.md -->