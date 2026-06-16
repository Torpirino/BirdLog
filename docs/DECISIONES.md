# Decisiones técnicas

> Cada decisión importante se registra aquí en el momento de tomarse.
> No se borra ni reescribe: si cambia, se añade una entrada nueva que
> la sustituye y se marca la anterior como "Reemplazada por #N".

---

## #1 — Base de datos: Supabase
**Fecha**: 2026-04-27
**Decisión**: Supabase (PostgreSQL, tier gratis) como BD principal.
**Razón**: Sheets no respeta relaciones. SQLite vive en una sola
máquina. Supabase da BD relacional real accesible desde cualquier
sitio con interfaz web tipo hoja de cálculo.

---

## #2 — Dos entornos Supabase: dev y prod
**Fecha**: 2026-04-28
**Decisión**: Proyectos Supabase separados para desarrollo y producción.
**Razón**: El desarrollo implica meter, borrar y resetear datos.
Hacerlo contra los datos reales del observador es peligroso.
**Implicaciones**: variable `ENTORNO` en `.env` controla cuál se usa.

---

## #3 — Fotos: en Drive, URL en Supabase
**Fecha**: 2026-04-28
**Decisión**: Fotos en Google Drive. Tabla `fotos` en Supabase
guarda los enlaces asociados a visitas o registros concretos.
**Razón**: Supabase Storage tier gratis (1 GB) insuficiente. Drive
da 15 GB gratis y los usuarios ya lo conocen.

---

## #7 — AGENTS.md y CLAUDE.md como espejos
**Fecha**: 2026-04-28
**Decisión**: `AGENTS.md` fuente de verdad. `CLAUDE.md` copia
idéntica. Actualizar con `cp AGENTS.md CLAUDE.md`.

---

## #8 — Git: rama única main
**Fecha**: 2026-04-28
**Decisión**: Todo en `main`. Sin ramas dev ni feature/*.
**Razón**: Proyecto de una persona. Las ramas añaden fricción.

---

## #9 — Repositorio privado en GitHub
**Fecha**: 2026-04-28
**Decisión**: Repo privado. Los datos reales del observador no
se suben al repo aunque sea privado.

---

## #10 — Bitácora con trigger "rutina de cierre"
**Fecha**: 2026-04-28
**Decisión**: Bitácora se actualiza con trigger manual del usuario.
Los agentes la leen automáticamente al inicio de cada sesión.

---

## #11 — Backups gestionados desde el script Python
**Fecha**: 2026-04-28 (actualizado en #25)
**Decisión**: Tras cada inserción significativa: exportar tablas
a CSV y guardar en `backups/backup_YYYY-MM-DD/` local.
Retención: últimos 30 backups.
**Razón**: Tier gratuito Supabase no incluye backups automáticos.
Coste cero.

---

## #12 — Pausa por inactividad de Supabase: aceptarla
**Fecha**: 2026-04-28
**Decisión**: Aceptar la pausa de 7 días. Reactivar manualmente
es un clic. El sistema muestra mensaje claro al usuario cuando
detecta error de conexión por pausa.

---

## #13 — Seguridad: credenciales nunca en git
**Fecha**: 2026-04-28
**Decisión**: Claves Supabase, credenciales Drive, tokens: nunca
en git. Todo en `.env` (en `.gitignore`). Repo siempre privado.
Ver `docs/SEGURIDAD.md` para detalle operativo.

---

## #14 — Rediseño completo del modelo de datos (v2)
**Fecha**: 2026-04-30
**Decisión**: Rediseño tabla por tabla. Cambios principales:
- `sesiones` → `visitas` (nombre más natural).
- `06_observaciones` genérica → `lindus` específica.
- 3 columnas migrador/norte/local → campo `comportamiento`
  con CHECK constraint (MIGRADOR/NORTE/LOCAL).
- Meteo simplificada de 20 campos a 9.
- `tipo_visita` añadido en visitas (CHECK constraint).
- `tipo_lugar` y `municipio` añadidos en lugares.
- `ocupada` añadido en cajas_nido.
- `tipo_evidencia` añadido en mamiferos_puentes.
- `avispa_europea`, `polilla`, `mariposa` añadidos en cebos.
- `comunicacion_personal` añadido en nidos_rapaces.
- `temporada` eliminado de mamiferos_puentes (se deduce de fecha).
- `numero` eliminado de lugares (redundante con nombre).
**SQL**: `sql/002_esquema_v2.sql`.

---

## #15 — Meteorología: anotada por el observador, no AEMET
**Fecha**: 2026-04-30
**Decisión**: El observador registra la meteo directamente. No se
usa la API de AEMET.
**Razón**: La API de AEMET no devuelve datos siempre. Un sistema
que depende de una API poco fiable genera registros incompletos
sin que el observador lo sepa.
**Implicaciones**: el observador anota los campos de meteo una vez
por hora en conteos migratorios, y una vez por visita en el resto.

---

## #16 — Notificación de lugar/especie nuevo no encontrado
**Fecha**: 2026-04-30
**Decisión**: Cuando el sistema encuentre un nombre que no existe
en el catálogo, no inserta nada y muestra un mensaje claro con
los pasos a seguir: dar de alta en Supabase y añadir al
vocabulario de la hoja-guía. El registro queda pendiente para
reprocesar.
**Razón**: Insertar una FK rota o inventar un ID corrompe los
datos. Mejor parar y avisar.

---

## #17 — Acumulado de crabro: calculado, no almacenado
**Fecha**: 2026-04-30
**Decisión**: No se guarda campo `crabro_acumulado` en la tabla
`cebos_avispones`. El acumulado se calcula sumando las revisiones
del mismo cebo en un periodo dado.
**Razón**: El observador puede pedir ese cálculo para cualquier
periodo sin necesidad de un campo precalculado.

---

## #18 — Cajas nido: nombre identifica la ubicación
**Fecha**: 2026-04-30
**Decisión**: El nombre de una caja nido (`BAR01`, `CAR01`...)
identifica la ubicación, no la caja física. Si la caja
desaparece y se repone en el mismo sitio, mantiene el mismo
nombre. Si se mueve definitivamente, se da de alta con nombre
nuevo y la antigua queda como histórico.
**Razón**: El observador quiere un histórico de lo que ha ocurrido
en cada ubicación, no de cada caja física concreta.

---

## #19 — `visitas.hora_fin` permite NULL
**Fecha**: 2026-05-01
**Decisión**: `visitas.hora_fin` no es obligatorio en base de datos.
**Razón**: Lindus funciona con una visita larga abierta:
el inicio crea la visita sin `hora_fin` y el cierre lo rellena al
terminar la jornada.
**Implicaciones**: el parser y la inserción deben permitir visitas
abiertas y localizar la visita abierta del día para asociar
observaciones y cierre.

---

## #22 — Parser de texto estructurado en tres capas
**Fecha**: 2026-05-01
**Decisión**: El flujo de parseo se separa en parseo
(`src/parser/texto_estructurado.py`), validación (`src/parser/validacion.py`) y
normalización (`src/parser/normalizacion.py`), usando solo librería
estándar.
**Razón**: Mantiene el parser determinista y fácil de probar. El parseo
tolera campos desconocidos, la validación informa errores concretos y la
normalización aplica solo variantes menores sin tocar texto libre.
**Implicaciones**: La resolución de FKs y la inserción quedan fuera de
esta capa.

---

## #23 — Resolver FKs antes de insertar
**Fecha**: 2026-05-01
**Decisión**: La inserción resuelve todas las referencias de catálogo
necesarias antes de crear filas en `visitas` o tablas específicas.
**Razón**: Si falta un lugar, observador o especie, no debe quedar una
visita parcial en Supabase. El registro debe quedar pendiente y el usuario
debe recibir pasos claros para corregir el catálogo.

---

## #25 — Backup CSV solo local
**Fecha**: 2026-05-02
**Decisión**: El backup CSV se guarda solo en `backups/` local.
**Razón**: Los service accounts de Google no tienen cuota de
almacenamiento en Drive compartido. Error 403 en prueba real.
**Implicaciones**: Si en el futuro se quiere backup en Drive, habrá que
implementar autenticación OAuth 2.0.

---

## #26 — Fotos: carpetas YYYY-MM-DD_Lugar en Drive
**Fecha**: 2026-05-02
**Decisión**: Las fotos se organizan en Drive en carpetas con formato
`YYYY-MM-DD_Lugar/` dentro de `Fotos/`. La vinculación a visitas es un
proceso separado. El script `sincronizar_fotos()` escanea Drive y
registra las URLs en la tabla `fotos` de Supabase.
**Razón**: El observador puede subir fotos antes o después de procesar
el registro, sin orden fijo. Un proceso separado evita dependencias de
orden.

---

## #29 — IDs autogenerados con GENERATED ALWAYS AS IDENTITY
**Fecha**: 2026-05-02
**Decisión**: Las 11 PKs `id_*` quedan definidas como
`INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY`.
**Razón**: Prueba real mostró que los IDs definidos solo como
`INTEGER PRIMARY KEY` no se generaban automáticamente.
**Implicaciones**:
- En Supabase se aplica `ALTER TABLE ... ADD GENERATED ALWAYS AS
  IDENTITY` y `setval` al MAX actual para no chocar con datos cargados.
- `sql/002_esquema_v2.sql` queda coherente para entornos limpios.
- `ALWAYS` impide insertar IDs explícitos: backfills con IDs concretos
  requieren `OVERRIDING SYSTEM VALUE`.

---

## #39 — Cierre de jornada: las observaciones se conservan y se combinan
**Fecha**: 2026-06-10
**Contexto**: Una jornada Lindus escribe dos veces sobre la misma fila
de `visitas`: el inicio la crea (y puede dejar observaciones) y el cierre
la cierra rellenando `hora_fin` (y puede traer sus propias observaciones,
o no traer ninguna).
**Problema detectado**: el cierre siempre incluía `observaciones` en el
UPDATE. Si el archivo de cierre no traía observaciones, enviaba
`observaciones: None` y borraba silenciosamente las dictadas al inicio.
**Decisión**:
- Cierre **sin** observaciones → solo actualiza `hora_fin`; las
  observaciones del inicio se conservan intactas.
- Cierre **con** observaciones → se **combinan** con las existentes
  usando ` | ` como separador: `"nota inicio | nota cierre"`.
**Razón**: Los datos son sagrados (principio #3). El observador puede
anotar tanto al abrir como al cerrar la jornada y ambas notas deben
quedar en la visita.

---

## #40 — Revisión del histórico: se mantiene la estructura v2
**Fecha**: 2026-06-10
**Decisión**: Se mantiene la estructura base del esquema v2 frente al
rediseño propuesto en el Excel histórico:
- `id_observador` y `tipo_visita` en `visitas`.
- `visitas.id_lugar` se conserva: las observaciones y meteorología
  no tienen `id_lugar` propio y solo conocen su lugar vía la visita.
- UTM y municipio solo en `lugares`; las tablas hijas llevan `id_lugar`.
- IDs `INTEGER GENERATED ALWAYS AS IDENTITY` (decisión #29).
**Razón**: El Excel históricamente recibido desnormalizaba lugares y
perdía piezas de las que dependen el parser y la inserción.

---

## #41 — Esquema v3: 4 tablas nuevas con ajustes
**Fecha**: 2026-06-10
**Decisión**: Se crean `fototrampeo`, `cuaderno_campo`,
`estudio_campo` y `castor_rastros` en `sql/003_esquema_v3.sql`:
- `estudio_campo` guarda **solo detecciones**. La sesión de muestreo
  se modela como visita `IMPACTO_AMBIENTAL` + `meteorologia`.
- `fototrampeo` y `castor_rastros` no llevan `url_drive`: las imágenes
  van a la tabla `fotos` con `tabla_origen`/`id_origen`.
- `cuaderno_campo` permite `id_lugar` NULL.
- CHECKs ampliados: `visitas.tipo_visita` añade `FOTOTRAMPEO`,
  `CUADERNO_CAMPO` y `CASTOR_RASTROS`; `lugares.tipo_lugar` añade
  `FOTOTRAMPEO`, `ESTUDIO_CAMPO` y `OTRO`.
**Razón**: Incorporar nuevos tipos de registro sin romper la
normalización del v2 (decisión #40).
**Implicaciones**: Vocabularios de `fototrampeo.tipo_media`,
`estudio_campo.deteccion/migracion/altura` y `castor_rastros.*`
pendientes de cerrar con el cliente; de momento texto libre.

---

## #42 — Meteorología: 9 campos de captura + extras nullable
**Fecha**: 2026-06-10
**Decisión**: `meteorologia` mantiene los 9 campos que dicta el
observador y añade:
- Conteos de personas del protocolo Lindus: `presentes`,
  `observando`, `visitantes`, y un campo `observaciones`.
- Campos históricos opcionales que **solo rellena la importación**:
  `humedad_relativa`, `presion_atm`, `precipitacion_tipo`,
  niveles de nubes.
- `total_nubes_suma` del Excel se mapea a `nubosidad` (0–8).
**Razón**: El histórico trae columnas con datos reales que no deben
perderse (principio #3), pero el flujo de captura sigue siendo de
9 campos.

---

## #43 — Limpieza del histórico: corregir en la importación, sin inventar
**Fecha**: 2026-06-10
**Decisión**: La limpieza de datos del histórico se hace en el script de
importación, con estas reglas:
- **Valores medidos fuera de rango NO se autocorrigen**: se devuelven
  al cliente para corrección.
- **Direcciones de viento**: se normalizan a los 16 rumbos en
  convención inglesa (N, NNE, NE... igual que `orientacion_caja`).
  Valores compuestos tipo "S N" o "SO/NE" (cambios de dirección) se
  dejan NULL y el literal pasa a `observaciones`.
- **Comportamiento Lindus**: las 3 columnas de conteo se convierten
  a filas `comportamiento`+`numero`. Las filas mixtas se parten.
- **Especies**: las entradas marcadas para revisión se importan como
  entradas válidas del catálogo.
**Razón**: Los datos son sagrados: el importador puede transformar
formato pero no inventar valores medidos.

---

## #44 — Coordenadas UTM: ETRS89, huso 30N
**Fecha**: 2026-06-10
**Decisión**: El sistema de referencia del proyecto es **ETRS89,
huso 30N** (todos los puntos están en Navarra). Las coordenadas
`utm_x`/`utm_y` de los lugares se dejan nullable hasta que el cliente
entregue los datos; el observador no escribe huso ni datum en las
hojas-guía.

---

## #45 — Valores deducidos en el histórico
**Fecha**: 2026-06-10
**Decisión**: En la preparación del histórico se aplican deducciones
solo para valores derivables de los propios datos sin inventar:
- Temperaturas con decimal perdido → se corrigen por el mismo patrón
  ya confirmado para otros valores similares.
- `visitas.id_lugar` → derivado de la hoja de meteo (sin ambigüedad
  cuando cada visita mapea a un único lugar).
- `especies.grupo` y `nombre_comun` → por taxonomía estándar.
**Pendiente del cliente (no deducible, no inventado)**:
- Observador de las visitas históricas.
- UTM de los puntos de conteo.
- `id_lugar` de visitas sin meteo.
- Vocabularios de las tablas nuevas y quinto ecosistema.

---

## #46 — Importación del histórico: decisiones de carga
**Fecha**: 2026-06-10
**Decisión**: La importación del histórico se ejecutó con estas reglas:
- `utm_x`/`utm_y` de `lugares` → NULL (pendientes del cliente).
- `id_observador` de las visitas históricas → observador del catálogo
  (placeholder; el cliente no entregó el dato).
- `tipo_visita` de las visitas históricas → LINDUS.
- Primera visita sin `id_lugar` → omitida; pendiente del cliente.
- Fila Lindus mixta → dividida en dos filas con su respectivo
  `comportamiento`/`numero`.
- Viento compuesto → NULL en `viento_direccion`; literal en
  `observaciones`.
**Resultado**: 135 especies, 2 observadores, 2 lugares, 97 visitas,
1.048 meteo, 10.870 observaciones Lindus.

---

## #48 — Inserción de los campos v3 y columna observaciones en nidos_rapaces
**Fecha**: 2026-06-11
**Contexto**: Los campos nuevos del esquema v3 (decisiones #41/#42) se
parseaban y validaban pero la inserción los descartaba en silencio:
contra el principio "los datos son sagrados".
**Decisión**: la inserción escribe ya todos los campos v3 dictables:
- `meteorologia`: `presentes`, `observando`, `visitantes` y
  `observaciones` en `_fila_meteo`.
- `cebos_avispones`: `numero_trampa`, `fecha_colocacion`,
  `utm_x_nido`, `utm_y_nido` en `_insertar_cebo`.
- `nidos_rapaces`: `descripcion_nido`, `incuba`, `numero_pollos`,
  `pollos_volados` y `observaciones` en `_insertar_nido`.
**Columna nueva**: `nidos_rapaces.observaciones TEXT` añadida con
migración aditiva (`sql/004_observaciones_nidos_rapaces.sql`).

---

## #50 — Captura por hojas-guía revisadas por el agente
**Fecha**: 2026-06-16
**Decisión**: BirdLog pasa a una **versión basada en hojas-guía**:
1. El observador rellena **hojas-guía tabulares** (`docs/Guias/`, una
   plantilla por tipo de visita/observación). Lindus llega normalmente
   en hoja-guía; el resto puede llegar por hoja-guía o por
   **voz/Telegram**.
2. **El agente valida** los campos contra las reglas de las guías y el
   modelo de datos, avisa de los fallos antes de insertar y solo sube
   a Supabase cuando todo es correcto y el usuario lo autoriza.
3. El backup CSV local se conserva (decisión #25); se mantienen las
   reglas de seguridad y de resolución de FKs.
**Razón**: simplicidad antes que sofisticación (principio #1). Un agente
que revisa antes de insertar protege «los datos son sagrados» (principio
#3) sin infraestructura frágil adicional.
