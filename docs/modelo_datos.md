# Modelo de datos — diseño definitivo

Diseño cerrado tras revisión con el observador y revisión del Excel
del cliente v03 (decisiones #40–#43). 14 tablas.
El SQL de creación está en `sql/003_esquema_v3.sql`.

Nota de migración: las tablas que reciben el histórico Lindus 2025
(`especies`, `lugares`, `visitas`, `meteorologia`, `lindus`) llevan
una columna opcional `codigo_origen` con el id del Excel del cliente
(`SP001`, `LUG01`, `V0001`, `M0001`, `L000001`) para trazabilidad.

---

## Estructura general

```
CATÁLOGOS          → VISITAS (hub central) → TABLAS ESPECÍFICAS
especies                    ↑
observadores        meteorologia (1→N)
lugares
```

Toda observación de campo pasa por una **visita**. La visita sabe
cuándo fue, a dónde, quién fue y qué tipo de trabajo se hizo.
Las tablas específicas guardan los datos propios de cada estudio.

---

## CATÁLOGOS

### especies
Lista única de todas las especies del sistema.

| Campo | Tipo | Obligatorio |
|---|---|---|
| id_especie | Entero PK | Sí |
| nombre_cientifico | Texto | Sí |
| nombre_comun | Texto | No |
| grupo | CHECK constraint | No |

Valores de `grupo`: `RAPAZ`, `PASERIFORME`, `ACUATICA`,
`INVERTEBRADO`, `MAMIFERO`, `OTRO`.

Nota: para aves e invertebrados se usa nombre científico. Para
mamíferos se usa nombre común (Visón, Castor, Nutria...).

---

### observadores
Personas que recogen datos en campo.

| Campo | Tipo | Obligatorio |
|---|---|---|
| id_observador | Entero PK | Sí |
| nombre_observador | Texto | Sí |

---

### lugares
Todos los puntos físicos del sistema: puntos de conteo migratorio,
cajas nido, cebos de avispón, nidos de rapaz y puentes. El nombre
lo define el observador y es estable aunque el elemento físico
se renueve (especialmente las cajas nido).

| Campo | Tipo | Obligatorio |
|---|---|---|
| id_lugar | Entero PK | Sí |
| nombre_lugar | Texto | Sí |
| tipo_lugar | CHECK constraint | Sí |
| municipio | Texto | No |
| utm_x | Decimal | Sí |
| utm_y | Decimal | Sí |

Valores de `tipo_lugar`: `CONTEO_MIGRATORIO`, `CAJA_NIDO`,
`CEBO_AVISPON`, `NIDO_RAPAZ`, `PUENTE`, `FOTOTRAMPEO`,
`ESTUDIO_CAMPO`, `OTRO`.

Nota: el nombre de la caja nido identifica la ubicación, no la
caja física. Si la caja desaparece y se repone en el mismo sitio,
mantiene el mismo nombre para preservar el histórico.

---

## HUB CENTRAL

### visitas
Cada vez que el observador va a un lugar a hacer un trabajo de campo.
Una visita = un lugar + una fecha. Si en la misma jornada va a
tres sitios distintos, son tres visitas.

| Campo | Tipo | Obligatorio |
|---|---|---|
| id_visita | Entero PK | Sí |
| id_lugar | FK → lugares | Sí |
| id_observador | FK → observadores | Sí |
| tipo_visita | CHECK constraint | Sí |
| fecha | Fecha | Sí |
| hora_inicio | Hora | Sí |
| hora_fin | Hora | No |
| observaciones | Texto | No |

Valores de `tipo_visita`: `LINDUS`, `CAJA_NIDO`, `CEBO_AVISPON`,
`NIDO_RAPAZ`, `MAMIFEROS_PUENTES`, `IMPACTO_AMBIENTAL`,
`FOTOTRAMPEO`, `CUADERNO_CAMPO`, `CASTOR_RASTROS`.

Nota: en Lindus, `hora_fin` queda vacía mientras la visita larga está
abierta y se rellena al procesar `Fin_visita_Lindus`.

---

### meteorologia
Datos meteorológicos asociados a una visita. En Lindus y Trona
se registra una fila por hora. En el resto de estudios, una sola
fila por visita.

| Campo | Tipo | Obligatorio |
|---|---|---|
| id_meteo | Entero PK | Sí |
| id_visita | FK → visitas | Sí |
| hora | Hora | Sí |
| temperatura | Decimal | No |
| nubosidad | Entero (0-8) | No |
| viento_direccion | Texto | No |
| viento_intensidad | Texto | No |
| precipitacion | Texto | No |
| visibilidad | Texto | No |
| presentes | Entero | No |
| observando | Entero | No |
| visitantes | Entero | No |
| observaciones | Texto | No |

Los campos meteorológicos los dicta el observador al Plaud.
No se usa la API de AEMET por ser poco fiable.
`presentes`/`observando`/`visitantes` son conteos de personas en el
punto de observación (vienen del protocolo Lindus).

**Campos históricos (solo importación del Excel 2025, el Plaud no
los dicta):** `humedad_relativa`, `presion_atm`, `precipitacion_tipo`,
`mar_nubes_cobertura`, `mar_nubes_altura`, `nubes_n1_cobertura`,
`nubes_n1_altura`, `nubes_n1_tipo`, `nubes_n2_cobertura`,
`nubes_n2_tipo`. Todos opcionales. El campo `total_nubes_suma` del
Excel se mapea a `nubosidad`.

---

## TABLAS ESPECÍFICAS

### lindus
Conteos migratorios en Lindus y Trona. Cada fila es un avistamiento
de una especie con un comportamiento concreto.

| Campo | Tipo | Obligatorio |
|---|---|---|
| id_lindus | Entero PK | Sí |
| id_visita | FK → visitas | Sí |
| id_especie | FK → especies | Sí |
| hora | Hora | Sí |
| numero | Entero | Sí |
| comportamiento | CHECK constraint | Sí |
| edad | Texto | No |
| sexo | Texto | No |
| plumaje | Texto | No |
| observaciones | Texto | No |
| especie_texto | Texto | No |

Valores de `comportamiento`: `MIGRADOR` (dirección sur),
`NORTE` (retromigración), `LOCAL`.

Nota: cada avistamiento lleva un solo comportamiento. Si el
observador ve 5 milanos migrando y 2 locales en el mismo momento,
son dos filas distintas. El `total` del Excel histórico no se
almacena: es la suma y se calcula en el dashboard.

`especie_texto` guarda el nombre tal como se transcribió
originalmente (traza de auditoría; `id_especie` es el dato bueno).

---

### cajas_nido
Una fila por revisión de caja nido.

**Campos habituales:**

| Campo | Tipo | Obligatorio |
|---|---|---|
| id_cajanido | Entero PK | Sí |
| id_visita | FK → visitas | Sí |
| id_lugar | FK → lugares | Sí |
| id_especie | FK → especies | No |
| ecosistema | CHECK constraint | Sí |
| especie_arbol | Texto | Sí |
| estado_nido | CHECK constraint | Sí |
| ocupada | Booleano | Sí |
| numero_huevos | Entero | No |
| numero_pollos | Entero | No |
| observaciones | Texto | No |

Valores de `ecosistema`: `ZONA_SALVAJE`, `ZONA_URBANA`,
`PARQUE_CON_RIO`, `PARQUE_URBANO` *(quinto valor pendiente
de confirmar con el observador)*.

Valores de `estado_nido`: `POCAS_HIERBAS`, `MUCHAS_HIERBAS`,
`CASI_TERMINADO`, `TERMINADO`.

**Campos proyecto IB+ (todos opcionales):**
`orientacion_caja` (CHECK: N/NE/E/SE/S/SW/W/NW),
`huevos_caliente_frio`, `peso_pollos`, `longitud_tarso`,
`numero_anilla`, `distancia_rio`, `distancia_peatonal`,
`distancia_carretera`, `cobertura_vegetal`, `cobertura_arboles`,
`cobertura_matorral`, `cobertura_pastizal`.

---

### nidos_rapaces
Una fila por revisión de nido. El texto se guarda literal,
tal como lo anota el observador en campo.

| Campo | Tipo | Obligatorio |
|---|---|---|
| id_nido_rapaz | Entero PK | Sí |
| id_visita | FK → visitas | Sí |
| id_lugar | FK → lugares | Sí |
| id_especie | FK → especies | No |
| texto_revision | Texto | Sí |
| comunicacion_personal | Texto | No |
| descripcion_nido | Texto | No |
| incuba | Booleano | No |
| numero_pollos | Entero | No |
| pollos_volados | Entero | No |

---

### cebos_avispones
Una fila por revisión de cebo. El acumulado de crabro se calcula
en el dashboard sumando las revisiones por periodo — no se guarda
como campo.

| Campo | Tipo | Obligatorio |
|---|---|---|
| id_cebo | Entero PK | Sí |
| id_visita | FK → visitas | Sí |
| id_lugar | FK → lugares | Sí |
| vv | Entero | Sí |
| crabro | Entero | No |
| avispa_europea | Entero | No |
| polilla | Entero | No |
| mariposa | Entero | No |
| otros | Entero | No |
| observaciones | Texto | No |
| numero_trampa | Texto | No |
| fecha_colocacion | Fecha | No |
| utm_x_nido | Decimal | No |
| utm_y_nido | Decimal | No |

Nota: la UTM de la trampa vive en `lugares` (el cebo es el lugar).
`utm_x_nido`/`utm_y_nido` localizan el nido de avispón si se
encuentra durante la revisión.

---

### mamiferos_puentes
Una fila por combinación puente + especie detectada.

| Campo | Tipo | Obligatorio |
|---|---|---|
| id_mamifero | Entero PK | Sí |
| id_visita | FK → visitas | Sí |
| id_lugar | FK → lugares | Sí |
| id_especie | FK → especies | Sí |
| presencia | CHECK constraint | Sí |
| tipo_evidencia | CHECK constraint | No |
| observaciones | Texto | No |

Valores de `presencia`: `PRESENTE`, `AUSENTE`, `POSIBLE`.
Valores de `tipo_evidencia`: `HUELLA`, `EXCREMENTO`,
`MADRIGUERA`, `AVISTAMIENTO`.

---

### fototrampeo *(nueva en v3)*
Evento de colocación/revisión de una cámara de fototrampeo.
Las imágenes y vídeos van en la tabla `fotos` con
`tabla_origen = 'fototrampeo'` e `id_origen = id_fototrampeo`;
aquí solo se guarda el evento y su resumen.

| Campo | Tipo | Obligatorio |
|---|---|---|
| id_fototrampeo | Entero PK | Sí |
| id_visita | FK → visitas | Sí |
| id_lugar | FK → lugares | Sí |
| id_especie | FK → especies | No |
| especie_texto | Texto | No |
| fecha_colocacion | Fecha | No |
| fecha_revision | Fecha | No |
| fecha_imagen | Fecha | No |
| tipo_media | Texto | No |
| numero_imagenes | Entero | No |
| observaciones | Texto | No |

Vocabulario de `tipo_media` pendiente de cerrar con el cliente.

---

### cuaderno_campo *(nueva en v3)*
Observaciones sueltas tipo cuaderno de campo. `id_lugar` es opcional
porque pueden ocurrir fuera de los puntos del catálogo; en ese caso
el sitio se describe en `observaciones`.

| Campo | Tipo | Obligatorio |
|---|---|---|
| id_cuaderno | Entero PK | Sí |
| id_visita | FK → visitas | Sí |
| id_lugar | FK → lugares | No |
| id_especie | FK → especies | No |
| especie_texto | Texto | No |
| numero | Entero | No |
| observaciones | Texto | No |

---

### estudio_campo *(nueva en v3)*
Detecciones de estudios de impacto ambiental. La sesión de muestreo
(punto de observación, hora inicio/fin, meteorología) se registra
como visita de tipo `IMPACTO_AMBIENTAL` + fila en `meteorologia`;
esta tabla guarda solo el detalle por detección.

| Campo | Tipo | Obligatorio |
|---|---|---|
| id_estudio | Entero PK | Sí |
| id_visita | FK → visitas | Sí |
| id_especie | FK → especies | No |
| especie_texto | Texto | No |
| numero | Entero | No |
| deteccion | Texto | No |
| hora_observacion | Hora | No |
| distancia_inicial / lado_inicial | Decimal / Texto | No |
| distancia_minima / lado_minima | Decimal / Texto | No |
| distancia_final / lado_final | Decimal / Texto | No |
| vuelo_sobre | Booleano | No |
| direccion_vuelo | Texto | No |
| migracion | Texto | No |
| altura | Texto | No |
| observaciones | Texto | No |

Vocabularios de `deteccion`, `migracion` y `altura` pendientes de
cerrar con el cliente.

---

### castor_rastros *(nueva en v3)*
Rastros de castor en transectos de río. Las fotos van en la tabla
`fotos` con `tabla_origen = 'castor_rastros'`.

| Campo | Tipo | Obligatorio |
|---|---|---|
| id_castor_rastro | Entero PK | Sí |
| id_visita | FK → visitas | Sí |
| id_lugar | FK → lugares | Sí |
| id_especie | FK → especies | No |
| tipo_rastro | Texto | Sí |
| intensidad_rastro | Texto | No |
| reciente_antiguo | Texto | No |
| aplicacion | Texto | No |
| observaciones | Texto | No |

Vocabularios de `tipo_rastro`, `intensidad_rastro` y
`reciente_antiguo` pendientes de cerrar con el cliente.

---

### fotos (fase futura)
URLs de Drive asociadas a visitas o registros concretos.

| Campo | Tipo | Obligatorio |
|---|---|---|
| id_foto | Entero PK | Sí |
| id_visita | FK → visitas | No |
| tabla_origen | Texto | No |
| id_origen | Entero | No |
| url_drive | Texto | Sí |
| descripcion | Texto | No |
| fecha_subida | Fecha | No |

---

## Cambios respecto al diseño original

| Qué cambió | Por qué |
|---|---|
| `sesiones` → `visitas` | Nombre más natural para el observador |
| `06_observaciones` genérica → `lindus` específica | El observador piensa por tipos de trabajo |
| 3 columnas migrador/norte/local → campo `comportamiento` | Cada avistamiento tiene un solo comportamiento |
| Meteo de 20 campos → 9 campos | El observador confirmó que usa solo 5 variables |
| Añadido `tipo_visita` en visitas | Permite análisis de distribución de trabajo |
| Añadido `tipo_lugar` en lugares | Permite filtrar por tipo de punto |
| Añadido `municipio` en lugares | Lo pidió el observador para cajas nido |
| Añadido `ocupada` en cajas_nido | Lo pidió el observador |
| Añadido `tipo_evidencia` en mamiferos_puentes | Dato de gran valor analítico |
| Añadidos `avispa_europea`, `polilla`, `mariposa` en cebos | Lo pidió el observador |
| Añadido `comunicacion_personal` en nidos_rapaces | Separa info propia de info de terceros |
| `temporada` eliminado de mamiferos_puentes | Se deduce de la fecha de la visita |
| `numero` eliminado de lugares | Redundante con el nombre del lugar |

---

## Cambios v3 (revisión del Excel del cliente v03)

| Qué cambió | Por qué |
|---|---|
| 4 tablas nuevas: `fototrampeo`, `cuaderno_campo`, `estudio_campo`, `castor_rastros` | Nuevos tipos de registro del cliente |
| `estudio_campo` solo guarda detecciones | La sesión va a `visitas` + `meteorologia`; evita duplicar la meteo |
| `fototrampeo` y `castor_rastros` enlazan imágenes vía `fotos` | `fotos` ya está diseñada para eso (`tabla_origen`/`id_origen`) |
| `meteorologia`: conteos de personas + observaciones + históricos nullable | Captura Plaud sigue en 9 campos; el histórico 2025 no pierde datos |
| `nidos_rapaces`: `descripcion_nido`, `incuba`, `numero_pollos`, `pollos_volados` | Datos que el observador ya recoge |
| `cebos_avispones`: `numero_trampa`, `fecha_colocacion`, UTM del nido | Ídem; la UTM de la trampa sigue en `lugares` |
| `codigo_origen` en tablas con histórico | Trazabilidad de la migración desde el Excel |
| `lindus.especie_texto` | Traza de la transcripción original |
| CHECKs ampliados en `tipo_visita` y `tipo_lugar` | Cubrir los nuevos tipos de registro |
| Se mantienen `id_observador`, `tipo_visita`, `visitas.id_lugar`, lugares normalizados e IDs enteros | Decisión #40: la estructura del Excel los perdía |
