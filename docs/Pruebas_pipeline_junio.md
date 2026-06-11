# Pruebas del pipeline — Junio 2026

> Guía completa para probar el flujo Plaud → Drive → Pipeline → Supabase
> → Dashboard con grabaciones reales y dejar el proyecto finalizado.
>
> **Para quién es este documento**: para el usuario que hace las pruebas
> de campo Y para cualquier LLM/agente (Claude Code, Codex u otro) que
> le ayude a diagnosticar y corregir los errores que aparezcan. Contiene
> todo el contexto necesario: qué probar, qué dictar, qué `.txt` debe
> salir, qué debe pasar en cada paso y cómo reportar un fallo.

---

## 1. Contexto del sistema (leer antes de ayudar)

**Flujo completo**:

```
Grabación de voz en Plaud (plantilla + vocabulario cerrado)
    → Plaud genera .txt estructurado CLAVE: valor
    → el usuario sube el .txt a Drive, carpeta 01_entrada
    → App "BirdLog Pipeline" (Streamlit, puerto 8502): botón "Procesar"
    → parsea → valida → resuelve catálogos → inserta en Supabase
    → backup CSV en backups/backup_YYYY-MM-DD/ (15 tablas, retención 30)
    → mueve el .txt a 02_procesados (OK) o 03_errores (fallo)
    → consulta en "BirdLog Dashboard" (Streamlit, puerto 8999)
```

**Dónde está cada cosa** (para el agente que diagnostique):

| Componente | Archivo |
|---|---|
| Orquestador del lote Drive | `src/pipeline.py` |
| Parser de `.txt` Plaud | `src/parser/plaud.py` |
| Validación (mínimos, formatos, valores cerrados) | `src/parser/validacion.py` |
| Normalización (fechas, códigos de caja/cebo, comportamiento) | `src/parser/normalizacion.py` |
| Resolución nombre → id de catálogo | `src/insercion/catalogos.py` |
| Inserción en Supabase | `src/insercion/escritura.py` |
| Backup CSV | `src/backup/exportar.py` |
| App pipeline (UI) | `app_pipeline/` (`app.py`, `lib/orquestador.py`, `lib/ui.py`) |
| Formato exacto de las 7 plantillas Plaud | `docs/formato_plaud.md` |
| Guía de uso de la app | `docs/USO_APP_PIPELINE.md` |
| Modelo de datos (15 tablas v3) | `docs/modelo_datos.md` |
| Decisiones técnicas | `docs/DECISIONES.md` (la #47 es la revisión previa a estas pruebas) |

**Estado de la base de datos** (Supabase, proyecto BirdLog
`mbphfgmjryyxzjgcwqxo`):

- Esquema v3 aplicado. Contiene el **histórico real 2025**: 97 visitas,
  1.048 meteo, 10.870 observaciones Lindus. **Los datos son sagrados:
  no borrar ni modificar nada del histórico durante las pruebas.**
- Catálogos actuales: lugares = solo `Lindus` y `Trona`; observadores =
  `Gabi` y `Ander`; especies = 135 (aves e invertebrados del conteo;
  **no hay mamíferos todavía**).
- Toda inserción de prueba debe llevar la frase **«prueba junio»**
  en `OBSERVACIONES_VISITA` para poder identificarla y limpiarla después
  (sección 8).

**Huecos conocidos antes de empezar** (no son fallos de tus pruebas;
si aparecen, son esto):

1. ~~Campos v3 nuevos sin insertar~~ **Resuelto el 2026-06-11**
   (decisión #48): la inserción ya escribe
   `PRESENTES`/`OBSERVANDO`/`VISITANTES` (meteo Lindus),
   `NUMERO_TRAMPA`/`FECHA_COLOCACION`/`UTM_X_NIDO`/`UTM_Y_NIDO` (cebos)
   y `DESCRIPCION_NIDO`/`INCUBA`/`NUMERO_POLLOS`/`POLLOS_VOLADOS` +
   `OBSERVACIONES_NIDO` (nidos rapaces). La prueba P-08 lo confirma
   con datos reales.
2. Si `.env` aún usa la clave **anon** en lugar de `service_role`,
   alguna operación puede fallar por permisos (ver Fase 0).
3. No hay deduplicación: reprocesar un `.txt` ya insertado **duplica
   filas** (decisión #38). Cuidado al mover archivos a mano.

---

## 2. Fase 0 — Preparación (una sola vez)

Marca cada casilla antes de la primera prueba:

- [ ] **Clave `service_role` en `.env`**: Supabase → proyecto BirdLog →
      Settings → API → `service_role`. Sustituir el valor actual (anon)
      de la clave del entorno activo en `.env`. Nunca commitearla.
- [ ] **Arrancar la app**: icono **BirdLog Pipeline** del escritorio
      (o `bash scripts/abrir_app_pipeline.sh`). La cabecera debe quedar
      en verde: Entorno ✓, Drive accesible ✓, Supabase conectado ✓.
- [ ] **Carpeta Drive `01_entrada` vacía** antes de empezar (si hay
      restos de otras pruebas, moverlos fuera).
- [ ] **Altas de catálogo** (dashboard → Edición / Catálogos). Sin
      estas altas, las pruebas P-02 a P-05 caerían en amarillo (eso ya
      lo cubre la P-07); para los caminos felices hay que darlas de
      alta antes:

  **Lugares** (con el nombre real que use el cliente; si aún no se sabe,
  usar estos y renombrar después):

  | nombre_lugar | tipo_lugar | municipio |
  |---|---|---|
  | `BAR01` | CAJA_NIDO | (el real o vacío) |
  | `Cebo avispón 1` | CEBO_AVISPON | (el real o vacío) |
  | `Nido Milano 01` | NIDO_RAPAZ | (el real o vacío) |
  | `Puente de Aranzadi` | PUENTE | (el real o vacío) |

  **Especies de mamíferos** (reales, se quedan en el catálogo):

  | nombre_comun | nombre_cientifico | grupo |
  |---|---|---|
  | `Nutria paleártica` | `Lutra lutra` | MAMIFERO |
  | `Visón europeo` | `Mustela lutreola` | MAMIFERO |
  | `Garduña` | `Martes foina` | MAMIFERO |
  | `Castor europeo` | `Castor fiber` | MAMIFERO |

- [ ] **Vocabulario del Plaud actualizado** con los nombres de arriba
      (los lugares y especies dictados deben coincidir con el catálogo;
      el sistema solo tolera diferencias de mayúsculas/minúsculas).

---

## 3. Mecánica de cada prueba

1. **Dicta** al Plaud el texto de la columna "Dictado" usando la
   plantilla indicada (los prompts exactos están en
   `docs/formato_plaud.md`).
2. **Revisa el `.txt`** que genera Plaud y compáralo con el
   "TXT esperado" de la prueba. Si Plaud genera algo distinto
   (claves inventadas, narrativa, valores fuera de vocabulario), eso ya
   es un resultado: anótalo (el problema está en el prompt de Plaud,
   no en el pipeline).
3. **Sube el `.txt`** a la carpeta `01_entrada` de Drive.
4. En la app pipeline pulsa **"Procesar grabaciones de Plaud"** y
   compara con el "Resultado esperado".
5. **Verifica en el dashboard** (botón "Abrir dashboard") y, si quieres
   ir a la BD, usa las consultas de la sección 7.
6. Apunta el resultado en la tabla de seguimiento (sección 9).

**Colores de la app**: 🟢 insertado y backup hecho · 🟡 falta un dato de
catálogo (dar de alta y reprocesar) · 🔴 error de formato/validación
(corregir plantilla o dictado).

**Reprocesar un archivo fallido**: corrige la causa, mueve el `.txt` de
`03_errores` a `01_entrada` en Drive y vuelve a pulsar Procesar.

---

## 4. Pruebas de camino feliz (P-01 a P-05)

> En todas, usar la fecha real del día de la prueba. Los ejemplos usan
> `2026-06-15` como fecha tipo: sustitúyela. La frase «prueba junio»
> debe aparecer siempre en las observaciones de visita.

### P-01 — Jornada Lindus completa (3 grabaciones)

La prueba más importante: visita larga abierta, observaciones y cierre.
**Sube los 3 `.txt` a la vez y desordenados** (el pipeline debe
ordenarlos solo: inicio → observaciones → fin).

**Grabación 1 — plantilla `Inicio_visita_Lindus`. Dictado:**

> Inicio visita Lindus. Lugar visita: Lindus. Observador: Gabi.
> Observaciones visita: prueba junio del pipeline, amenaza de tormenta.

**TXT esperado:**

```text
TIPO_REGISTRO: INICIO_VISITA_LINDUS
TIPO_VISITA: LINDUS
FECHA: 2026-06-15
HORA_INICIO: 09:00
LUGAR_VISITA: Lindus
OBSERVADOR: Gabi
OBSERVACIONES_VISITA: prueba junio del pipeline, amenaza de tormenta
```

**Grabación 2 — plantilla `Observaciones_Lindus`. Dictado:**

> Observaciones Lindus.
> Observación. Especie: milano negro. Número: cinco. Van hacia el sur.
> Observación. Especie: milano real. Número: dos. Están campeando.
> Observación. Especie: abejero europeo. Número: uno. Va hacia el norte.

**TXT esperado:**

```text
TIPO_REGISTRO: OBSERVACIONES_LINDUS
TIPO_VISITA: LINDUS
FECHA: 2026-06-15

---OBSERVACION_LINDUS---
ESPECIE: milano negro
HORA: 10:15
NUMERO: 5
COMPORTAMIENTO: MIGRADOR

---OBSERVACION_LINDUS---
ESPECIE: milano real
HORA: 10:15
NUMERO: 2
COMPORTAMIENTO: LOCAL

---OBSERVACION_LINDUS---
ESPECIE: abejero europeo
HORA: 10:15
NUMERO: 1
COMPORTAMIENTO: NORTE
```

**Grabación 3 — plantilla `Fin_visita_Lindus`. Dictado:**

> Fin visita Lindus. Hora fin: trece treinta.
> Meteorología de las diez: dieciocho grados, nubosidad tres, viento
> noroeste flojo, sin lluvia, visibilidad buena. Somos tres, dos
> observando, cinco visitantes.
> Observaciones visita: cierre sin incidencias.

**TXT esperado:**

```text
TIPO_REGISTRO: FIN_VISITA_LINDUS
TIPO_VISITA: LINDUS
FECHA: 2026-06-15
HORA_FIN: 13:30
OBSERVACIONES_VISITA: cierre sin incidencias

---METEOROLOGIA---
HORA_METEO: 10:00
TEMPERATURA: 18
NUBOSIDAD: 3
VIENTO_DIRECCION: NW
VIENTO_INTENSIDAD: FLOJO
PRECIPITACION: NULA
VISIBILIDAD: BUENA
PRESENTES: 3
OBSERVANDO: 2
VISITANTES: 5
```

**Resultado esperado**: 3 tarjetas 🟢 procesadas **en orden lógico**
aunque se subieran desordenadas. Una sola visita LINDUS nueva con
`hora_inicio` y `hora_fin`, 3 filas en `lindus`, 1 fila en
`meteorologia`. Las observaciones de visita deben quedar **combinadas**:
`prueba junio del pipeline, amenaza de tormenta | cierre sin incidencias`
(decisión #39 — el cierre no borra las notas del inicio).
**Verificar en dashboard**: páginas Visitas y Lindus muestran la visita
nueva con sus 3 observaciones y su meteo.

> **Hallazgos del primer intento real (2026-06-11)**:
>
> Se grabaron los 3 TXT con Plaud real y se analizaron antes de procesar.
> Se detectaron dos incidencias en los TXT generados:
>
> 1. **Especie en plural**: en el archivo de observaciones,
>    Plaud escribió `ESPECIE: milanos reales` (plural). El catálogo
>    tiene `Milano real` en singular. `resolver_especie` prueba exacto
>    y `.capitalize()`, ambos fallan con `milanos reales`. **Causa**:
>    el prompt de `Observaciones_Lindus` decía "escribe la especie TAL
>    COMO la dice el observador", sin instruir a convertir a singular.
>    **Corrección aplicada en documentación**: sección `NORMALIZACIÓN DE
>    ESPECIE` añadida al prompt de `Observaciones_Lindus` en
>    `docs/formato_plaud.md`, y formas plurales de especies frecuentes
>    añadidas a la lista de vocabulario que debe cargarse en Plaud.
>    **Acción pendiente en Plaud**: actualizar el prompt
>    `Observaciones_Lindus` y el vocabulario con esas nuevas entradas.
>
> 2. **Nombre de archivo incongruente con contenido**: el archivo de
>    observaciones se llamó `06-11_Visita_Inicio_en_Lindus_-_11_de_junio...`
>    pero su `TIPO_REGISTRO` era `OBSERVACIONES_LINDUS`. Ocurrió porque
>    Plaud genera el nombre del archivo a partir de su propio resumen LLM
>    de las primeras palabras del dictado, no del campo `TIPO_REGISTRO`.
>    **Sin impacto en el pipeline** (que lee `TIPO_REGISTRO` del contenido).
>    **Causa probable**: la grabación de observaciones no empezó con la
>    frase exacta "Observaciones Lindus." o Plaud tituló a partir de su
>    resumen interno, no del campo estructurado. **Corrección aplicada**: regla de
>    "Nombre del archivo" añadida a los "Principios generales" de
>    `docs/formato_plaud.md`. **Acción en Plaud**: seguir la convención
>    de título inicial al dictar (ver "Nombre del archivo" en
>    `docs/formato_plaud.md`).
>
> **Repetir P-01 desde Plaud** con el prompt `Observaciones_Lindus`
> actualizado (que incluye `NORMALIZACIÓN DE ESPECIE`). El resto del
> flujo (inicio, fin, meteo, combinación de observaciones) era correcto.

### P-02 — Caja nido (plantilla `Visita_Caja_Nido`)

**Dictado:**

> Visita caja nido. Caja BAR cero uno. Observador: Gabi.
> Hora inicio diez. Hora fin diez y cuarto.
> Parque con río. Árbol: aliso. Nido casi terminado. Ocupada.
> Especie: carbonero común. Cuatro huevos. Orientación sureste.
> Dieciséis grados, nubosidad dos, viento norte flojo, sin lluvia,
> visibilidad buena.
> Observaciones visita: prueba junio del pipeline.

**TXT esperado:**

```text
TIPO_REGISTRO: VISITA_CAJA_NIDO
TIPO_VISITA: CAJA_NIDO
FECHA: 2026-06-15
HORA_INICIO: 10:00
HORA_FIN: 10:15
LUGAR_CAJA: BAR01
OBSERVADOR: Gabi
OBSERVACIONES_VISITA: prueba junio del pipeline

---METEOROLOGIA---
HORA_METEO: 10:00
TEMPERATURA: 16
NUBOSIDAD: 2
VIENTO_DIRECCION: N
VIENTO_INTENSIDAD: FLOJO
PRECIPITACION: NULA
VISIBILIDAD: BUENA

---CAJA_NIDO---
ESPECIE: carbonero común
ECOSISTEMA: PARQUE_CON_RIO
ESPECIE_ARBOL: aliso
ESTADO_NIDO: CASI_TERMINADO
OCUPADA: true
NUMERO_HUEVOS: 4
ORIENTACION_CAJA: SE
```

**Resultado esperado**: 🟢. Visita CAJA_NIDO + 1 fila en `cajas_nido`
(especie resuelta a "Carbonero común" aunque se dictara en minúsculas)
+ 1 meteo. Probar también dictar el lugar como "bar cero uno": el
normalizador debe convertirlo a `BAR01`.

### P-03 — Cebo de avispón (plantilla `Visita_Cebo_Avispon`)

**Dictado:**

> Visita cebo avispón. Cebo avispón uno. Observador: Ander.
> Hora inicio once. Hora fin once y diez.
> Doce velutinas, dos crabro, una avispa europea, tres polillas, cero
> mariposas. Trampa número uno. La coloqué el uno de junio.
> Nido localizado en equis seiscientos doce mil trescientos cuarenta,
> ye cuatro millones setecientos dos mil cien.
> Observaciones cebo: líquido bajo, lo he rellenado.
> Observaciones visita: prueba junio del pipeline.

**TXT esperado:**

```text
TIPO_REGISTRO: VISITA_CEBO_AVISPON
TIPO_VISITA: CEBO_AVISPON
FECHA: 2026-06-15
HORA_INICIO: 11:00
HORA_FIN: 11:10
LUGAR_CEBO: Cebo avispón 1
OBSERVADOR: Ander
OBSERVACIONES_VISITA: prueba junio del pipeline

---CEBO_AVISPON---
VV: 12
CRABRO: 2
AVISPA_EUROPEA: 1
POLILLA: 3
MARIPOSA: 0
NUMERO_TRAMPA: 1
FECHA_COLOCACION: 2026-06-01
UTM_X_NIDO: 612340
UTM_Y_NIDO: 4702100
OBSERVACIONES_CEBO: líquido bajo, lo he rellenado
```

**Resultado esperado**: 🟢. Visita CEBO_AVISPON + 1 fila en
`cebos_avispones` con las capturas, `numero_trampa`,
`fecha_colocacion` y las UTM del nido de velutina (verificar en P-08).

### P-04 — Nido de rapaz (plantilla `Visita_Nido_Rapaz`)

**Dictado:**

> Visita nido rapaz. Lugar nido: Nido Milano cero uno. Observador: Gabi.
> Hora inicio dieciocho. Hora fin dieciocho y veinte.
> Especie: milano real. Texto revisión: adulto echado en el nido,
> está incubando, sin molestias aparentes. Veo dos pollos.
> Según Ander, la semana pasada también incubaba.
> Observaciones visita: prueba junio del pipeline.

**TXT esperado:**

```text
TIPO_REGISTRO: VISITA_NIDO_RAPAZ
TIPO_VISITA: NIDO_RAPAZ
FECHA: 2026-06-15
HORA_INICIO: 18:00
HORA_FIN: 18:20
LUGAR_NIDO: Nido Milano 01
OBSERVADOR: Gabi
OBSERVACIONES_VISITA: prueba junio del pipeline

---NIDO_RAPAZ---
ESPECIE: milano real
TEXTO_REVISION: adulto echado en el nido, está incubando, sin molestias aparentes
INCUBA: true
NUMERO_POLLOS: 2
COMUNICACION_PERSONAL: Ander
```

**Resultado esperado**: 🟢. Visita NIDO_RAPAZ + 1 fila en
`nidos_rapaces` con `texto_revision` literal, `comunicacion_personal`,
`incuba=true` y `numero_pollos=2` (verificar en P-08).

### P-05 — Mamíferos en puente (plantilla `Visita_Mamiferos_Puente`)

**Dictado:**

> Visita mamíferos puente. Puente de Aranzadi. Observador: Gabi.
> Hora inicio ocho. Hora fin ocho y media.
> Nutria paleártica presente, excrementos frescos bajo el arco.
> Visón europeo posible, huellas dudosas en la orilla.
> Observaciones puente: mucho caudal esta semana.
> Observaciones visita: prueba junio del pipeline.

**TXT esperado:**

```text
TIPO_REGISTRO: VISITA_MAMIFEROS_PUENTE
TIPO_VISITA: MAMIFEROS_PUENTES
FECHA: 2026-06-15
HORA_INICIO: 08:00
HORA_FIN: 08:30
LUGAR_PUENTE: Puente de Aranzadi
OBSERVADOR: Gabi
OBSERVACIONES_VISITA: prueba junio del pipeline
OBSERVACIONES_PUENTE: mucho caudal esta semana

---MAMIFERO_PUENTE---
ESPECIE: Nutria paleártica
PRESENCIA: PRESENTE
TIPO_EVIDENCIA: EXCREMENTO
OBSERVACIONES_MAMIFERO: excrementos frescos bajo el arco

---MAMIFERO_PUENTE---
ESPECIE: Visón europeo
PRESENCIA: POSIBLE
TIPO_EVIDENCIA: HUELLA
OBSERVACIONES_MAMIFERO: huellas dudosas en la orilla
```

**Resultado esperado**: 🟢. Visita MAMIFEROS_PUENTES + 2 filas en
`mamiferos_puentes`. Las observaciones de visita deben quedar como
`prueba junio del pipeline | mucho caudal esta semana` (las de puente se combinan,
no se pierden).

---

## 5. Pruebas de error deliberado (P-06, P-07)

Estas pruebas **deben fallar**. Lo que se evalúa es que el mensaje sea
claro y diga qué hacer. Si un mensaje resulta confuso, eso es un
hallazgo: anótalo.

### P-06 — Errores de validación (🔴 esperado)

Crear a mano un `.txt` (no hace falta Plaud) con varios errores a la
vez y subirlo a `01_entrada`:

```text
Revisión del nido de la chopera

TIPO_REGISTRO: VISITA_NIDO_RAPAZ
TIPO_VISITA: NIDO_RAPAZ
FECHA: 15-06-2026
HORA_INICIO: 18:00
LUGAR_NIDO: Nido Milano 01
OBSERVADOR: Gabi
OBSERVACIONES_VISITA: prueba junio error multiple

---METEOROLOGIA---
TEMPERATURA: 18
NUBOSIDAD: 9
VIENTO_DIRECCION: OESTE

---NIDO_RAPAZ---
ESPECIE: milano real
TEXTO_REVISION: prueba de errores
```

**Resultado esperado**: 🔴 una sola tarjeta con TODOS estos diagnósticos
a la vez (no solo el primero), cada uno con campo, valor recibido,
motivo y sugerencia:

- advertencia por el texto narrativo antes de `TIPO_REGISTRO`;
- `FECHA` inválida (`15-06-2026` no es `YYYY-MM-DD` ni `DD/MM/YYYY`);
- `HORA_FIN` ausente (obligatoria en nido rapaz);
- `HORA_METEO` ausente en el bloque de meteorología;
- `NUBOSIDAD` 9 fuera de rango 0–8;
- `VIENTO_DIRECCION` OESTE no válido, con sugerencia "usar W para oeste".

El archivo debe acabar en `03_errores`, sin insertar nada y sin backup.

### P-07 — Error de catálogo (🟡 esperado) y reproceso

Crear un `.txt` correcto pero con una especie que no existe:

```text
TIPO_REGISTRO: VISITA_MAMIFEROS_PUENTE
TIPO_VISITA: MAMIFEROS_PUENTES
FECHA: 2026-06-15
HORA_INICIO: 09:00
HORA_FIN: 09:15
LUGAR_PUENTE: Puente de Aranzadi
OBSERVADOR: Gabi
OBSERVACIONES_VISITA: prueba junio catalogo

---MAMIFERO_PUENTE---
ESPECIE: Tejón europeo
PRESENCIA: PRESENTE
TIPO_EVIDENCIA: HUELLA
```

**Resultado esperado**: 🟡 "Falta un dato de catálogo", indicando
catálogo (`especies`), campo, valor recibido (`Tejón europeo`) y los
pasos: dar de alta en Supabase + añadir al vocabulario del Plaud.
**Nada insertado** (ni siquiera la visita: las FKs se resuelven antes
de escribir, decisión #23). Archivo en `03_errores`.

**Segunda parte — reproceso**: dar de alta `Tejón europeo`
(`Meles meles`, MAMIFERO) en Edición/Catálogos, mover el `.txt` de
`03_errores` a `01_entrada` y reprocesar → ahora 🟢.

**Tercera parte — Lindus tardío**: tras cerrar la jornada de P-01,
subir otro `Observaciones_Lindus` de la misma fecha con 1 observación.
Esperado: 🟢 con aviso "la visita ya tenía hora de fin" y las filas
añadidas a la visita existente (decisión #38), sin crear visita nueva.

---

## 6. Pruebas de infraestructura (P-08 a P-10)

### P-08 — Verificación en BD de los campos v3 nuevos

Tras P-01, P-03 y P-04, comprobar en la BD (sección 7) que llegaron
con su valor (implementado 2026-06-11, decisión #48):

- `meteorologia.presentes/observando/visitantes` y `observaciones`
  de la meteo Lindus;
- `cebos_avispones.numero_trampa/fecha_colocacion/utm_x_nido/utm_y_nido`;
- `nidos_rapaces.descripcion_nido/incuba/numero_pollos/pollos_volados`
  y `observaciones` (de `OBSERVACIONES_NIDO`).

**Resultado esperado**: cada campo dictado aparece con su valor; los
no dictados quedan NULL.

### P-09 — Backup y retención

Tras cualquier prueba 🟢, comprobar en la carpeta del proyecto:

- Existe `backups/backup_<fecha-de-hoy>/` con **15 CSV** (uno por
  tabla, incluidos `fototrampeo`, `cuaderno_campo`, `estudio_campo`
  y `castor_rastros` aunque estén vacíos).
- `lindus.csv` contiene el histórico completo (~10.870 filas + las de
  prueba), no solo lo nuevo.
- Nunca hay más de 30 carpetas `backup_*`.

### P-10 — Estados del entorno (cabecera de la app)

- Pausar manualmente el proyecto en supabase.com (o esperar a una pausa
  natural) y recargar la app → debe decir "El proyecto Supabase está
  pausado. Reactívalo en supabase.com…", no un error genérico.
  Reactivar después.
- Renombrar temporalmente el archivo de credenciales de Google
  (`GOOGLE_CREDENTIALS_PATH`) y recargar → mensaje claro de Drive con
  pasos en el desplegable. Restaurar después.
- Con todo correcto, la cabecera queda verde y el botón Procesar activo.

---

## 7. Consultas de verificación en BD

Para el usuario: pedirle al agente que las ejecute. Para el agente:
usar el MCP de Supabase (proyecto `mbphfgmjryyxzjgcwqxo`) o el cliente
de `src/conexion.py`. **Solo SELECT durante las pruebas.**

```sql
-- Visitas de prueba insertadas
SELECT id_visita, tipo_visita, fecha, hora_inicio, hora_fin, observaciones
FROM visitas WHERE observaciones ILIKE '%prueba junio%' ORDER BY id_visita;

-- Hijos de una visita de prueba (sustituir 999)
SELECT * FROM lindus WHERE id_visita = 999;
SELECT * FROM meteorologia WHERE id_visita = 999;
SELECT * FROM cajas_nido WHERE id_visita = 999;
SELECT * FROM nidos_rapaces WHERE id_visita = 999;
SELECT * FROM cebos_avispones WHERE id_visita = 999;
SELECT * FROM mamiferos_puentes WHERE id_visita = 999;

-- Sanidad del histórico (debe seguir intacto)
SELECT COUNT(*) FROM lindus;          -- 10.870 + filas de prueba
SELECT COUNT(*) FROM visitas;         -- 97 + visitas de prueba
SELECT COUNT(*) FROM meteorologia;    -- 1.048 + meteo de prueba
```

---

## 8. Limpieza final (cuando TODAS las pruebas estén en verde)

Las **especies** dadas de alta (mamíferos) y los **lugares** reales se
quedan: son catálogo útil. Solo se borran las visitas de prueba y sus
hijos.

Opción A (recomendada): dashboard → Edición / Catálogos → borrar cada
registro de prueba con la confirmación `BORRAR` (hace backup previo).

Opción B (agente, SQL — primero los hijos, después las visitas):

```sql
-- Verificar qué se va a borrar ANTES de borrar
SELECT id_visita, tipo_visita, fecha, observaciones FROM visitas
WHERE observaciones ILIKE '%prueba junio%';

DELETE FROM lindus            WHERE id_visita IN (SELECT id_visita FROM visitas WHERE observaciones ILIKE '%prueba junio%');
DELETE FROM meteorologia      WHERE id_visita IN (SELECT id_visita FROM visitas WHERE observaciones ILIKE '%prueba junio%');
DELETE FROM cajas_nido        WHERE id_visita IN (SELECT id_visita FROM visitas WHERE observaciones ILIKE '%prueba junio%');
DELETE FROM nidos_rapaces     WHERE id_visita IN (SELECT id_visita FROM visitas WHERE observaciones ILIKE '%prueba junio%');
DELETE FROM cebos_avispones   WHERE id_visita IN (SELECT id_visita FROM visitas WHERE observaciones ILIKE '%prueba junio%');
DELETE FROM mamiferos_puentes WHERE id_visita IN (SELECT id_visita FROM visitas WHERE observaciones ILIKE '%prueba junio%');
DELETE FROM visitas           WHERE observaciones ILIKE '%prueba junio%';
```

Después: hacer un backup manual (procesar con `01_entrada` vacía no lo
genera; basta con esperar a la próxima inserción real o ejecutar
`hacer_backup` desde el agente) y verificar los contadores de sanidad
de la sección 7.

---

## 9. Tabla de seguimiento

| Prueba | Descripción | Fecha | Resultado | Incidencia / nota |
|---|---|---|---|---|
| P-01 | Jornada Lindus completa (orden + combinación de notas) | | ☐ OK ☐ FALLO | |
| P-02 | Caja nido | | ☐ OK ☐ FALLO | |
| P-03 | Cebo avispón | | ☐ OK ☐ FALLO | |
| P-04 | Nido rapaz | | ☐ OK ☐ FALLO | |
| P-05 | Mamíferos puente (2 especies) | | ☐ OK ☐ FALLO | |
| P-06 | Errores de validación múltiples (🔴 con diagnóstico claro) | | ☐ OK ☐ FALLO | |
| P-07 | Catálogo faltante (🟡) + reproceso + Lindus tardío | | ☐ OK ☐ FALLO | |
| P-08 | Campos v3 nuevos en BD | | ☐ OK ☐ FALLO | |
| P-09 | Backup 15 tablas + retención | | ☐ OK ☐ FALLO | |
| P-10 | Mensajes de entorno (pausa, Drive, credenciales) | | ☐ OK ☐ FALLO | |

---

## 10. Cómo reportar un error a un agente (Claude Code, Codex…)

Copia esta plantilla y rellénala. Con esto el agente tiene todo lo
necesario para reproducir y corregir:

```text
PRUEBA: P-0X (nombre)
QUÉ HICE: (dictado o .txt que subí, pegado completo)
QUÉ ESPERABA: (según esta guía)
QUÉ PASÓ: (color de la tarjeta, mensaje EXACTO de la app, copiado del
  "Registro de procesamiento")
DÓNDE ESTÁ EL ARCHIVO AHORA: (01_entrada / 02_procesados / 03_errores)
¿SE INSERTÓ ALGO EN SUPABASE?: (sí/no/no sé)
```

**Instrucciones para el agente que reciba un reporte:**

1. Lee primero `docs/BITACORA.md`, `docs/DECISIONES.md` y la sección 1
   de este documento.
2. Reproduce el fallo en local **sin tocar Supabase**: guarda el `.txt`
   del reporte en `/tmp/` y pásalo por las capas de
   `src/parser/` y `src/parser/validacion.py`; para inserción usa el
   `ClienteFalso` de `tests/test_escritura.py`. Los 135 tests de
   `pytest` deben pasar antes y después de tu corrección.
3. Clasifica el fallo: prompt de Plaud (corregir `docs/formato_plaud.md`
   y el prompt en el Plaud) · parser/validación/normalización ·
   inserción · catálogo (no es bug: alta pendiente) · UI/mensaje
   confuso (mejorar el diagnóstico en `src/diagnosticos.py` o
   `app_pipeline/lib/ui.py`).
4. Corrige con test que cubra el caso, ejecuta `pytest`, verifica el
   diff sin secretos, commitea con prefijo convencional y registra la
   decisión en `docs/DECISIONES.md` si cambia comportamiento.
5. Marca la incidencia como resuelta en la tabla de la sección 9 y pide
   al usuario repetir la prueba.

---

## 11. Criterio de "proyecto finalizado"

El proyecto queda cerrado cuando:

- [ ] P-01 a P-10 en OK.
- [ ] `.env` con clave `service_role`.
- [ ] Datos de prueba limpiados (sección 8) y sanidad del histórico OK.
- [ ] Catálogo definitivo cargado: lugares reales del cliente (cajas,
      cebos, nidos, puentes con sus UTM) y especies de mamíferos.
- [ ] Pendientes del cliente resueltos (ver `docs/BITACORA.md`):
      observador de las 98 visitas históricas, `id_lugar` de V0001,
      UTM/municipio de Lindus y Trona.
- [ ] Sección de arranque de la app pipeline añadida al `README.md`.
- [ ] Rutina de cierre final en la bitácora.
