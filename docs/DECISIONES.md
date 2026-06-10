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
**Decisión**: Proyectos Supabase separados: `fauna-dev` y `fauna-prod`.
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

## #4 — Plaud devuelve .txt estructurado: parser sin IA
**Fecha**: 2026-04-28
**Decisión**: El parser es código Python que lee `clave: valor`.
Sin IA en medio.
**Razón**: Plaud ya estructura mediante plantilla. IA encima es
complejidad innecesaria y punto de fallo.
**Implicaciones**: plantilla del Plaud debe ser rigurosa. Valores
que apuntan a catálogos deben coincidir exactamente con la BD.
El vocabulario cerrado del Plaud es la clave del sistema.

---

## #5 — Stack y lenguaje
**Fecha**: 2026-04-28
**Decisión**: Python 3.11+. Librerías: `supabase-py`, `pydantic`,
`streamlit`, `pytest`, `google-api-python-client`.

---

## #6 — Dashboard en páginas separadas
**Fecha**: 2026-04-28
**Decisión**: `dashboard/app.py` como entrada, `dashboard/paginas/`
con un archivo por página, `dashboard/lib/` para lógica común.
**Razón**: Un único `app.py` no escala.

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
**Fecha**: 2026-04-28
**Decisión**: Tras cada inserción significativa: exportar tablas
a CSV, guardar en `backups/backup_YYYY-MM-DD/` local y subir a
Drive en `Backups Sistema Fauna/`. Retención: últimos 30 backups.
**Razón**: Tier gratuito Supabase no incluye backups automáticos.
Coste cero. Datos en tres sitios (Supabase + local + Drive).

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
**Decisión**: Rediseño tabla por tabla tras conversación con el
observador. Cambios principales:
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

## #15 — Meteorología: Plaud, no AEMET
**Fecha**: 2026-04-30
**Decisión**: El observador dicta la meteo al Plaud. No se usa
la API de AEMET.
**Razón**: La API de AEMET no devuelve datos siempre. Un sistema
que depende de una API poco fiable genera registros incompletos
sin que el observador lo sepa. El Plaud es más fiable.
**Implicaciones**: el observador dicta 6 campos de meteo una vez
por hora en Lindus/Trona, y una vez por visita en el resto.

---

## #16 — Notificación de lugar/especie nuevo no encontrado
**Fecha**: 2026-04-30
**Decisión**: Cuando el script encuentre un nombre que no existe
en el catálogo, no inserta nada y muestra un mensaje claro con
los pasos a seguir: dar de alta en Supabase y añadir al
vocabulario del Plaud. El archivo .txt queda en `pendientes/`
para reprocesar.
**Razón**: Insertar una FK rota o inventar un ID corrompe los
datos. Mejor parar y avisar.

---

## #17 — Acumulado de crabro: calculado en dashboard
**Fecha**: 2026-04-30
**Decisión**: No se guarda campo `crabro_acumulado` en la tabla
`cebos_avispones`. El acumulado se calcula en el dashboard
sumando las revisiones del mismo cebo en un periodo dado.
**Razón**: El observador puede pedir ese cálculo para cualquier
periodo sin necesidad de un campo precalculado que complique
el diseño.

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
`Inicio_visita_Lindus` crea la visita sin `hora_fin` y
`Fin_visita_Lindus` la rellena al cerrar la jornada.
**Implicaciones**: el parser y la inserción deben permitir visitas
Lindus abiertas y localizar la visita abierta del día para asociar
observaciones y cierre.

---

## #20 — Plantillas Plaud definitivas v1
**Fecha**: 2026-05-01
**Decisión**: Se definen 7 plantillas Plaud para la fase inicial:
`Inicio_visita_Lindus`, `Observaciones_Lindus`, `Fin_visita_Lindus`,
`Visita_Caja_Nido`, `Visita_Cebo_Avispon`, `Visita_Nido_Rapaz` y
`Visita_Mamiferos_Puente`.
**Razón**: Lindus requiere una visita larga abierta, observaciones
en varias grabaciones y cierre con meteorología horaria. El resto
de tipos se registran como una visita breve con una observación
asociada.
**Implicaciones**:
- `Inicio_visita_Lindus` crea la visita sin `hora_fin`.
- `Observaciones_Lindus` inserta observaciones asociadas a la visita
  Lindus abierta del día.
- `Fin_visita_Lindus` actualiza `hora_fin` y registra meteorología.
- Las plantillas no-Lindus crean visita, observación específica y
  meteorología opcional.

---

## #21 — Sin plantilla Plaud para impacto ambiental en esta fase
**Fecha**: 2026-05-01
**Decisión**: `IMPACTO_AMBIENTAL` queda sin plantilla Plaud en la v1.
**Razón**: La fase actual prioriza los flujos ya definidos con el
observador: Lindus, cajas nido, cebos de avispón, nidos de rapaz y
mamíferos en puentes.
**Implicaciones**: el valor sigue existiendo en `visitas.tipo_visita`,
pero no se implementa parser específico hasta una fase futura.

---

## #22 — Parser Plaud en tres capas sin dependencias externas
**Fecha**: 2026-05-01
**Decisión**: El mini-pipeline de Fase 3 se separa en parseo
(`src/parser/plaud.py`), validación (`src/parser/validacion.py`) y
normalización (`src/parser/normalizacion.py`), usando solo librería
estándar.
**Razón**: Mantiene el parser determinista y fácil de probar. El parseo
tolera campos desconocidos, la validación informa errores concretos y la
normalización aplica solo variantes menores sin tocar texto libre.
**Implicaciones**: La resolución de FKs y la inserción quedan fuera de
esta capa y se implementarán en fases posteriores.

---

## #23 — Fase 4: resolver FKs antes de insertar
**Fecha**: 2026-05-01
**Decisión**: La inserción resuelve todas las referencias de catálogo
necesarias antes de crear filas en `visitas` o tablas específicas.
**Razón**: Si falta un lugar, observador o especie, no debe quedar una
visita parcial en Supabase. El archivo debe pasar a errores y el usuario
debe recibir pasos claros para corregir el catálogo y el vocabulario
Plaud.
**Implicaciones**: En esta fase `ENTORNO=prod` queda bloqueado desde
configuración; solo se permite dev.

---

## #24 — IDs autogenerados en Supabase dev
**Fecha**: 2026-05-01
**Decisión**: Las columnas `id_*` de las tablas deben autogenerarse con
`GENERATED ALWAYS AS IDENTITY`.
**Razón**: La primera prueba real de inserción en Supabase dev mostró que
los IDs definidos solo como `INTEGER PRIMARY KEY` no se estaban generando
automáticamente, bloqueando las inserciones.
**Implicaciones**: Se corrigió manualmente en Supabase dev con
`ALTER TABLE`. Queda pendiente verificar y actualizar
`sql/002_esquema_v2.sql` para que el esquema aplicable en prod incluya
esta definición correctamente.

---

## #25 — Backup CSV solo local, sin Drive
**Fecha**: 2026-05-02
**Decisión**: El backup CSV se guarda solo en `backups/` local. No se
sube a Drive.
**Razón**: Los service accounts de Google no tienen cuota de
almacenamiento en Drive compartido. Error 403 en prueba real.
**Implicaciones**: Si en el futuro se quiere backup en Drive, habrá que
implementar autenticación OAuth 2.0.

---

## #26 — Fotos: carpetas YYYY-MM-DD_Lugar en Drive
**Fecha**: 2026-05-02
**Decisión**: Las fotos se organizan en Drive en carpetas con formato
`YYYY-MM-DD_Lugar/` dentro de `Fotos/` en `BirdLog/`. La vinculación a
visitas es un proceso separado del pipeline. El script
`sincronizar_fotos()` escanea Drive y registra las URLs en la tabla
`fotos` de Supabase.
**Razón**: El observador puede subir fotos antes o después de procesar
el `.txt`, sin orden fijo. Un proceso separado evita dependencias de
orden.

---

## #27 — Dashboard Streamlit modular y mantenible
**Fecha**: 2026-05-02
**Decisión**: El dashboard Streamlit se construirá de forma modular y
mantenible:
- No se generarán archivos HTML largos.
- No se abusará de `st.markdown(..., unsafe_allow_html=True)`.
- `dashboard/app.py` debe ser solo la entrada principal y navegación.
- Cada página debe vivir en su archivo dentro de `dashboard/paginas/`.
- La lógica común debe vivir en `dashboard/lib/`.
- Los estilos comunes deben centralizarse en `.streamlit/config.toml` y,
  si hace falta, en `dashboard/lib/ui.py`.
- Se evitará CSS duplicado en cada página.
- Se priorizarán componentes nativos de Streamlit.
- Si hace falta HTML/CSS personalizado, debe ser pequeño, reutilizable y
  encapsulado.
**Razón**: El dashboard debe ser bonito desde el principio, pero fácil de
mantener y ampliar durante toda la Fase 6.

---

## #28 — Edición del dashboard con backup local previo y traza
**Fecha**: 2026-05-02
**Decisión**: Las operaciones de alta, edición y borrado desde el
dashboard intentan ejecutar primero el backup CSV local existente
(`src/backup/exportar.py`) y escriben una traza mínima en
`backups/edicion_traza.log`.
**Razón**: La página de edición puede modificar datos reales en Supabase.
Antes de tocar datos conviene dejar una copia local reciente y una pista
de qué acción se intentó, sin crear un sistema nuevo de auditoría.
**Implicaciones**: `backups/` sigue fuera de git. Si el backup falla, la
operación se detiene y el usuario recibe el error en el dashboard.

---

## #29 — IDs autogenerados con GENERATED ALWAYS AS IDENTITY (cierre de #24)
**Fecha**: 2026-05-02
**Decisión**: Las 11 PKs `id_*` quedan definidas como
`INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY` tanto en Supabase dev
como en `sql/002_esquema_v2.sql`. Sustituye y cierra la decisión #24.
**Razón**: La corrección manual de #24 cubrió 7 de 11 tablas (las que
tocaba el pipeline) pero dejó fuera las de catálogo (`especies`,
`observadores`, `lugares`) y `fotos`. La primera prueba real desde el
dashboard de edición falló al insertar en `especies` porque su PK seguía
sin autogenerarse. Diagnóstico mediante `information_schema.columns` lo
confirmó.
**Implicaciones**:
- En Supabase dev se aplicó `ALTER TABLE ... ADD GENERATED ALWAYS AS
  IDENTITY` sobre las 4 PKs pendientes y `setval` al MAX actual para no
  chocar con los datos de catálogo ya cargados.
- `sql/002_esquema_v2.sql` queda coherente para entornos limpios
  (commit `70544ff`).
- `ALWAYS` impide insertar IDs explícitos: si en el futuro se necesita
  un backfill con IDs concretos habrá que usar `OVERRIDING SYSTEM VALUE`
  o cambiar la columna afectada a `BY DEFAULT` puntualmente.
- El código del dashboard nunca envió IDs manuales: `limpiar_payload`
  ya descartaba la PK vacía antes del `insert`. No requirió cambios.
**Verificación**: alta, edición y borrado de `TEST_DASHBOARD_NO_USAR` en
`especies` ejecutados contra Supabase dev usando las funciones reales de
`dashboard/lib/edicion.py`. `id_especie=158` autogenerado, edición y
borrado correctos, backup CSV y traza local generados en cada paso.

---

## #30 — Pipeline Plaud: sin `demo.py`; gestión mediante app local dedicada
**Fecha**: 2026-05-03
**Decisión**: El script `demo.py` y la carpeta `demo/` han sido eliminados
del repositorio. La prueba y operación del pipeline Plaud → Supabase se
gestionará mediante una app local específica (próxima fase), no mediante
scripts ad hoc de demo.
**Razón**: `demo.py` era un artefacto temporal de preparación para la
demostración con el observador. Una app local dedicada al pipeline aporta
más control, mejor UX y evita "basura" en el repo.
**Implicaciones**:
- Los bugs corregidos durante la preparación de la demo se conservan en
  el código de producción: `src/insercion/catalogos.py` (insensibilidad a
  mayúsculas en especies) y `src/insercion/escritura.py`
  (`observaciones_puente` ya no se descarta silenciosamente).
- Los 3 tests que cubren esos bugs (`test_resolver_especie_tolera_minusculas_*`
  y `test_insertar_mamiferos_puente_no_descarta_observaciones_puente`) se
  mantienen en `tests/`.
- La próxima tarea es diseñar e implementar la app local de pipeline.

---

## #31 — App de pipeline separada del dashboard
**Fecha**: 2026-05-03
**Decisión**: La app local de pipeline vive en una carpeta nueva
`app_pipeline/`, independiente de `dashboard/`. `dashboard/app.py`
sigue dedicado únicamente a consulta y edición de datos.
**Razón**: El dashboard es para *consultar* (decisiones #6 y #27). La
operación del pipeline (procesar Plaud, mover archivos en Drive, ver
errores) tiene un flujo y un perfil de error distinto. Mezclarlas
acopla responsabilidades: un fallo en el pipeline podría tirar el
dashboard, y la página de procesado tendría que coexistir con
filtros, mapas y tablas que no aplican a la operación.
**Implicaciones**:
- Nueva carpeta `app_pipeline/` con `app.py` + `lib/`
  (`orquestador`, `estados`, `ui`, `enlaces`).
- La app **no duplica lógica del pipeline**: solo envuelve
  `src.pipeline.procesar_drive()` y traduce sus resultados a estados
  visuales (verde/amarillo/rojo/gris).
- Detalle completo en `docs/PLAN_APP_PIPELINE.md`.

---

## #32 — Streamlit como herramienta para la app de pipeline
**Fecha**: 2026-05-03
**Decisión**: La app de pipeline se construye con **Streamlit**, mismo
stack que el dashboard.
**Razón**: Stack ya validado (decisión #5), instalado en el proyecto
y conocido por el observador. Componentes nativos suficientes
(`st.button`, `st.dataframe`, `st.status`, `st.empty`, `st.expander`).
Coste de implementación bajo. Permite reusar `.streamlit/config.toml`
y patrones de `dashboard/lib/ui.py`.
**Alternativas descartadas**:
- Tkinter / app de escritorio: stack nuevo sin justificación; rompe
  el flujo del observador, que ya trabaja en navegador.
- Página dentro del dashboard: acopla operación con consulta
  (ver decisión #31).
- CLI: el observador no es técnico (principio #2).
**Implicaciones**:
- Arranque: `streamlit run app_pipeline/app.py --server.port 8502`
  (puerto distinto al dashboard, 8501, para poder tener ambos
  abiertos a la vez).
- Sin dependencias nuevas. Reusa `streamlit`, `python-dotenv`,
  `supabase-py` y `google-api-python-client` ya presentes.

---

## #33 — App de pipeline como único punto de control para procesar Plaud
**Fecha**: 2026-05-03
**Decisión**: A partir de Fase 8, la app local de pipeline es el
**único punto de control** para procesar archivos Plaud desde Drive.
No habrá scripts ad hoc adicionales (cierra el ciclo abierto por la
decisión #30 al eliminar `demo.py`).
**Razón**: Tener un único entrypoint simplifica el modelo mental del
observador y evita duplicación. Cualquier mejora en el flujo Plaud
→ Supabase se incorpora a la app, no a un script paralelo.
**Implicaciones**:
- `src/pipeline.py` sigue siendo la lógica reutilizable y se mantiene
  testable de forma independiente.
- La app pipeline llama a `procesar_drive()` y traduce los resultados.
- Si en el futuro se necesita ejecución programada (p.ej. cron), se
  añadirá un wrapper que también pase por `src.pipeline`, sin
  duplicar lógica.

---

## #34 — Configuración validada por perfiles de uso
**Fecha**: 2026-05-03
**Decisión**: `src/config.py` valida la configuración por perfiles:
dashboard, Drive, pipeline Plaud y fotos. La app pipeline Plaud no
requiere `DRIVE_FOTOS_ID`; esa variable se valida solo al sincronizar
fotos.
**Razón**: Fotos es un flujo separado del procesado Plaud (decisión #26).
Una variable de fotos no debe bloquear la inserción de grabaciones `.txt`
ni el movimiento de archivos entre `01_entrada`, `02_procesados` y
`03_errores`.
**Implicaciones**:
- Pipeline Plaud requiere `ENTORNO`, Supabase del entorno activo,
  `GOOGLE_CREDENTIALS_PATH`, `DRIVE_ENTRADA_ID`,
  `DRIVE_PROCESADOS_ID` y `DRIVE_ERRORES_ID`.
- Fotos requiere además `DRIVE_FOTOS_ID`.
- Dashboard requiere `ENTORNO` y Supabase del entorno activo.
- `cargar_config()` se conserva como compatibilidad histórica para la
  configuración completa.

---

## #35 — Lanzadores separados para pipeline y dashboard
**Fecha**: 2026-05-03
**Decisión**: BirdLog mantiene dos lanzadores de escritorio separados:
**BirdLog Pipeline** para procesar grabaciones Plaud y **BirdLog Dashboard**
para consultar/editar datos.
**Razón**: Arrancar el dashboard como proceso hijo desde Streamlit añade
fragilidad al ciclo de vida de ambos procesos. Dos lanzadores explícitos
son más estables y más claros para un usuario no técnico.
**Implicaciones**:
- `scripts/abrir_app_pipeline.sh` abre la app pipeline en `8502`.
- `scripts/abrir_dashboard.sh` abre el dashboard en `8999`.
- Ambos scripts intentan abrir el navegador con `xdg-open` y evitan
  arrancar copias repetidas si el servicio ya está activo.

---

## #36 — Fechas Plaud tolerantes y lugares case-insensitive
**Fecha**: 2026-05-03
**Decisión**: El pipeline acepta `FECHA` en `YYYY-MM-DD` y `DD/MM/YYYY`.
Internamente normaliza siempre a `YYYY-MM-DD`. La resolución de lugares
mantiene coincidencia exacta como prioridad y añade una segunda búsqueda
insensible a mayúsculas/minúsculas, fallando si hay ambigüedad.
**Razón**: El primer `.txt` real de Plaud generó `03/05/2026` y un lugar en
minúsculas (`puente de aranzadi`). El sistema debe tolerar esas variaciones
sin relajar valores cerrados ni inventar catálogos.
**Implicaciones**: formatos de fecha fuera de esos dos siguen rechazándose
con mensaje claro. Los nombres de lugares deben seguir viniendo del catálogo.

---

## #37 — Orden lógico de archivos Lindus en lotes Drive
**Fecha**: 2026-05-04
**Decisión**: Antes de insertar un lote de `.txt` desde Drive, el pipeline
descarga los archivos y ordena los registros Lindus de la misma fecha por
tipo lógico: `INICIO_VISITA_LINDUS`, `OBSERVACIONES_LINDUS`,
`FIN_VISITA_LINDUS`. Las observaciones quedan entre inicio y fin y, si hay
varias, se ordenan de forma estable por hora de Drive (`createdTime` o
`modifiedTime`) y nombre.
**Razón**: Drive puede devolver varios `.txt` Lindus en orden no lógico. Si
se procesa primero el cierre, se cierra una visita inexistente o se cierra
antes de insertar observaciones.
**Implicaciones**: `FIN_VISITA_LINDUS` nunca crea una visita nueva. Si no
existe una visita Lindus abierta para esa fecha, el archivo falla con
mensaje claro, se mueve a errores y no crea backup.

---

## #38 — Observaciones Lindus recuperables sobre visita existente
**Fecha**: 2026-05-04
**Decisión**: `OBSERVACIONES_LINDUS` ya no exige que la visita Lindus esté
abierta. Si existe una única visita Lindus para la fecha, las observaciones
se añaden a esa visita aunque ya tenga `hora_fin`. Si hay cero visitas o
varias visitas candidatas, el pipeline falla con mensaje claro.
**Razón**: Permite recuperar archivos de observaciones que fallaron por
catálogo o validación sin borrar y repetir toda la jornada Lindus.
**Implicaciones**:
- No se crea ninguna visita desde `OBSERVACIONES_LINDUS`.
- Si la visita está cerrada, se informa con aviso.
- Si en el futuro el archivo incluye `LUGAR_VISITA` u `OBSERVADOR`, se usan
  para desambiguar.
- No hay deduplicación por especie/hora/número/comportamiento; reprocesar
  el mismo archivo puede duplicar filas. Una deduplicación segura requerirá
  diseño por archivo/hash.

---

## #39 — Cierre Lindus: las observaciones se conservan y se combinan
**Fecha**: 2026-06-10
**Contexto**: Una jornada Lindus escribe dos veces sobre la misma fila
de `visitas`: `INICIO_VISITA_LINDUS` la crea (y puede dejar
observaciones, p.ej. "amenaza de tormenta") y `FIN_VISITA_LINDUS` la
cierra rellenando `hora_fin` (y puede traer sus propias observaciones,
o no traer ninguna).
**Problema detectado**: el cierre siempre incluía `observaciones` en el
UPDATE. Si el archivo de cierre no traía observaciones, enviaba
`observaciones: None` y borraba silenciosamente las dictadas al inicio.
**Decisión**:
- Cierre **sin** observaciones → solo actualiza `hora_fin`; las
  observaciones del inicio se conservan intactas.
- Cierre **con** observaciones → se **combinan** con las existentes
  usando ` | ` como separador (mismo criterio que `observaciones_puente`
  en mamíferos): `"amenaza de tormenta | cierre sin incidencias"`.
  No se pierde texto de ninguna de las dos grabaciones.
**Razón**: Los datos son sagrados (principio #3). El observador puede
dictar notas tanto al abrir como al cerrar la jornada y ambas deben
quedar en la visita.
**Implicaciones**: `_buscar_visita_lindus_abierta` ahora lee también
`observaciones` de la visita abierta para poder combinar antes del
UPDATE. Cubierto con tests (cierre sin observaciones, cierre con
observaciones sin previas, y combinación de ambas).

---

## #40 — Revisión del Excel del cliente v03: se mantiene la estructura v2
**Fecha**: 2026-06-10
**Contexto**: El cliente entregó `docs/BirdLog_tablas_cliente_v03.xlsx`
con un rediseño de la BD: histórico Lindus 2025 cargado (10.903
observaciones, 1.048 meteo, 98 visitas), 4 tablas nuevas (`fototrampeo`,
`cuaderno_campo`, `estudio_campo_tipo`, `castor_rastros`) y cambios
estructurales (IDs de texto `V0001`/`SP001`, sin `observadores` ni
`tipo_visita`, UTM/municipio repetidos en cada tabla, meteo de 25
columnas, comportamiento Lindus como 3 columnas de conteo).
**Decisión**: Se mantiene la estructura base del esquema v2:
- `id_observador` y `tipo_visita` en `visitas`.
- **`visitas.id_lugar` se conserva**: `lindus` y `meteorologia` no
  tienen `id_lugar` propio y solo conocen su lugar vía la visita;
  el pipeline (`LUGAR_VISITA`, decisión #38) y el dashboard dependen
  de él. El `id_lugar` de las tablas específicas es el punto concreto
  (caja, trampa, puente); el de `visitas`, la jornada. No es duplicado.
- UTM y municipio solo en `lugares`; las tablas hijas llevan `id_lugar`.
- IDs `INTEGER GENERATED ALWAYS AS IDENTITY` (decisión #29). Para
  trazar la migración del Excel se podrá usar una columna
  `codigo_origen` temporal.
- Comportamiento Lindus sigue como `comportamiento` + `numero`
  (solo 1 de 10.903 filas históricas mezcla tipos; se partirá en dos
  al migrar). `total` no se almacena: se calcula (criterio #17).
**Razón**: El Excel pierde piezas de las que dependen parser,
inserción y dashboard, y desnormaliza lugares. Lo valioso del Excel
(4 tipos de registro nuevos y campos de detalle: incuba/pollos en
rapaces, fechas y UTM de trampa en cebos, conteos de personas en
meteo) se incorporará sobre la estructura v2.
**Pendiente de concretar**: alcance exacto de las 4 tablas nuevas
(ajustes propuestos: `estudio_campo_tipo` solo detecciones,
`fototrampeo` enlazando imágenes vía `fotos`), tratamiento de la meteo
histórica de 25 columnas, y limpieza de datos (valores meteo fuera de
rango, 33 variantes de dirección de viento, `especies` sin `grupo` ni
`nombre_comun`, 21 especies marcadas `revisar`).
*(Concretado en #41, #42 y #43.)*

---

## #41 — Esquema v3: 4 tablas nuevas con ajustes
**Fecha**: 2026-06-10
**Decisión**: Se crean `fototrampeo`, `cuaderno_campo`,
`estudio_campo` y `castor_rastros` en `sql/003_esquema_v3.sql`, con
estos ajustes respecto al Excel del cliente:
- `estudio_campo` guarda **solo detecciones**. La sesión de muestreo
  (punto, hora inicio/fin, meteo abreviada) del Excel se modela como
  visita de tipo `IMPACTO_AMBIENTAL` + fila en `meteorologia`, sin
  duplicar campos de meteo en la tabla.
- `fototrampeo` y `castor_rastros` **no** llevan `url_drive` ni
  `foto`: las imágenes van a la tabla `fotos` existente con
  `tabla_origen`/`id_origen`.
- `cuaderno_campo` permite `id_lugar` NULL (observaciones fuera de
  los puntos del catálogo; el sitio se describe en `observaciones`).
- CHECKs ampliados: `visitas.tipo_visita` añade `FOTOTRAMPEO`,
  `CUADERNO_CAMPO` y `CASTOR_RASTROS`; `lugares.tipo_lugar` añade
  `FOTOTRAMPEO`, `ESTUDIO_CAMPO` y `OTRO`.
**Razón**: Incorporar los nuevos tipos de registro del cliente sin
romper la normalización del v2 (decisión #40).
**Implicaciones**:
- Vocabularios pendientes de cerrar con el cliente antes de poner
  CHECK: `fototrampeo.tipo_media`, `estudio_campo.deteccion/
  migracion/altura`, `castor_rastros.tipo_rastro/intensidad_rastro/
  reciente_antiguo`. De momento son TEXT libres.
- El esquema v3 **no se ha aplicado** a Supabase dev: dev sigue en
  v2 con datos. Aplicarlo implica DROP+CREATE y reimportar; se hará
  cuando se planifique la migración del histórico.
- Plantillas Plaud, parser e inserción para los 4 tipos nuevos
  quedan para una fase posterior.

---

## #42 — Meteorología: 9 campos de captura + extras nullable
**Fecha**: 2026-06-10
**Decisión**: `meteorologia` mantiene los 9 campos que dicta el
observador al Plaud (decisión #15) y añade:
- Conteos de personas del protocolo Lindus: `presentes`,
  `observando`, `visitantes`, y un campo `observaciones`.
- Campos históricos opcionales que **solo rellena la importación
  del Excel 2025**: `humedad_relativa`, `presion_atm`,
  `precipitacion_tipo`, `mar_nubes_cobertura`, `mar_nubes_altura`,
  `nubes_n1_cobertura`, `nubes_n1_altura`, `nubes_n1_tipo`,
  `nubes_n2_cobertura`, `nubes_n2_tipo`.
- `total_nubes_suma` del Excel se mapea a `nubosidad` (0–8).
- `fecha` e `id_lugar` del Excel de meteo no se importan como
  columnas: se derivan de `id_visita`.
**Razón**: El histórico 2025 trae 25 columnas con datos reales que
no deben perderse (principio #3), pero el flujo de captura Plaud
sigue siendo de 9 campos: nadie dicta dos niveles de nubes por hora.
**Alternativas descartadas**: importar con pérdida (tira datos
reales); tabla `meteo_historica` aparte (dos tablas para el mismo
concepto complican dashboard y consultas; columnas NULL son baratas).

---

## #43 — Limpieza del histórico: corregir en la importación, sin inventar
**Fecha**: 2026-06-10
**Decisión**: La limpieza de datos del Excel del cliente se hará en
el script de importación (pendiente de implementar), con estas
reglas:
- **Valores medidos fuera de rango NO se autocorrigen** (24 filas de
  meteo detectadas: temperaturas 68/95 °C, humedades >100 %,
  presiones de 4–6 dígitos, y el bloque desplazado de V0043,
  M0464–M0478). Se devuelven al cliente para corrección; lista
  concreta en `docs/REVISION_EXCEL_CLIENTE_V03.md`.
- **Direcciones de viento**: se normalizan en la importación a los
  16 rumbos en convención inglesa (N, NNE, NE... igual que
  `cajas_nido.orientacion_caja`), traduciendo la notación española
  (O→W, NNO→NNW...). Valores compuestos tipo "S N" o "SO/NE"
  (cambios de dirección) se dejan NULL y el literal pasa a
  `observaciones`.
- **Comportamiento Lindus**: las 3 columnas de conteo se convierten
  a filas `comportamiento`+`numero`. La única fila mixta de 10.903
  (L002724, 3 MIGRADOR + 1 LOCAL) se parte en dos filas.
- **Especies**: las 21 entradas `revisar=SI` (rangos tipo
  `Accipiter sp`) se importan como entradas válidas del catálogo;
  la columna `revisar` no entra en la BD. `grupo` y `nombre_comun`
  (vacíos en las 135 filas) los debe completar el cliente o se
  rellenan en una pasada posterior.
**Razón**: Los datos son sagrados: el importador puede transformar
formato (notación de rumbos, pivotar columnas) pero no inventar
valores medidos.

---

## #44 — Respuestas del cliente al informe de revisión (Gabi)
**Fecha**: 2026-06-10
**Contexto**: Gabi respondió por escrito (resaltado en amarillo) a
`docs/Informe_revision.docx`, que recogía las cuestiones abiertas del
informe de revisión del Excel. Las respuestas se han aplicado
directamente sobre `docs/BirdLog_tablas_cliente_v03.xlsx` (copia de
seguridad previa `docs/BirdLog_tablas_cliente_v03.bak_<timestamp>.xlsx`).
**Decisiones del cliente y su aplicación al Excel**:
- **2.3 TOTAL**: confirmado que `total = migrador + direccion_norte +
  local`. Sin cambio (la fórmula viva ya estaba aplicada).
- **3.1 Tipo de observación**: el cliente **mantiene las 3 columnas**
  `migrador`/`direccion_norte`/`local`; **no** se unifican en un único
  `tipo_observacion`. Motivo: los datos se descargan de la base general
  Trektellen.nl en ese formato. **Anula la propuesta de pivotar en la
  importación** y matiza la regla de "Comportamiento Lindus" de la
  decisión #43: en BD se conserva `comportamiento`+`numero`, pero la
  fuente mantiene el formato de 3 columnas.
- **3.2 Especies a revisar**: las 21 entradas `revisar=SI` son
  **correctas y se aceptan todas** en el catálogo (nombres genéricos de
  uso recurrente). En el Excel `revisar` pasa de `SI` a `NO` en las 21.
  Confirma el criterio de #43 (entran al catálogo).
- **3.3 Valores meteo fuera de rango**: corregidos los 11 valores con el
  dato real que indicó el cliente (presiones a hPa con decimal, humedades
  reales, y `temperatura` de M0588 sin la nota "+V593"). Ver lista en
  `docs/REVISION_EXCEL_CLIENTE_V03.md`.
- **3.4 Desplazamiento V0043 (M0464–M0478)**: confirmado error
  estructural. Se reordena: el valor de presión mal ubicado en
  `humedad_relativa` se mueve a `presion_atm`; `humedad_relativa` queda
  vacía (dato original no recuperable).
- **3.5 Coordenadas UTM**: sistema de referencia del proyecto =
  **ETRS89, huso 30N** (todos los puntos están en Navarra). Se añaden
  columnas `datum` (ETRS89) y `huso` (30N) a las hojas con UTM
  (`cuaderno_campo`, `castor_rastros`, `cajas_nido`, `cebos_avispones`,
  `nidos_rapaces`, `mamiferos_puentes`).
**Implicaciones para el esquema/importación**:
- Las 24 filas de meteo de #43 que dependían del cliente quedan
  resueltas (11 valores + bloque V0043). Las temperaturas 68/95 °C u
  otras filas no listadas en el informe siguen pendientes si las hubiera.
- La importación ya **no** pivota comportamiento Lindus desde una única
  fuente: el origen mantiene 3 columnas (decisión del cliente).
- Conviene reflejar el sistema de referencia ETRS89/30N en `lugares`
  (o documentarlo) al aplicar el esquema v3 y migrar el histórico.

---

## #45 — Valores deducidos en el Excel (pendientes que no requerían al cliente)
**Fecha**: 2026-06-10
**Contexto**: Tras aplicar las respuestas del cliente (#44) quedaban
huecos en el Excel. Parte eran **deducibles de los propios datos o de
conocimiento taxonómico estándar**; el resto solo los conoce el cliente.
Se resuelven los primeros sin inventar (principio: los datos son
sagrados), y se marcan los segundos como pendientes.
**Deducido y aplicado al Excel** (`BirdLog_tablas_cliente_v03.xlsx`):
- **Temperaturas M1002 (68) y M1039 (95)** → **6.8** y **9.5**. Mismo
  patrón de decimal perdido que el cliente ya confirmó para el resto de
  valores meteo de #44 (p.ej. 786→78.6, 818→81.8). No estaban en el
  informe, pero la regla es la misma; se marcan como deducidos.
- **`visitas.id_lugar`** (98 filas, todas vacías) → derivado de la hoja
  `meteo`, que sí trae `id_lugar` por visita **sin ambigüedad** (cada
  visita mapea a un único lugar). **97 visitas** rellenadas (59 LUG01
  Lindus / 38 LUG02 Trona). **V0001** (2025-07-16) no tiene filas de
  meteo ni `id_lugar` en `Lindus_Trona`: se deja **vacía** y pendiente
  del cliente (no se infiere de visitas vecinas).
- **`especies.grupo`** (135, vacías) → asignado por taxonomía a los
  valores cerrados: RAPAZ (29), PASERIFORME (66), ACUATICA (13),
  INVERTEBRADO (13), OTRO (14). Criterio: orden Passeriformes →
  PASERIFORME (incluye córvidos, hirundínidos, aláudidos); rapaces
  diurnas y nocturnas (Strix) → RAPAZ; aves acuáticas, limícolas,
  láridos y zancudas → ACUATICA; insectos (mariposas, polillas,
  abejorros) → INVERTEBRADO; aves terrestres no paseriformes
  (vencejos, pícidos, palomas, cuco, abejaruco, abubilla) → OTRO.
- **`especies.nombre_comun`** (135, vacías) → nombre común en español
  (nomenclatura SEO/BirdLife) deducido del nombre científico; entradas
  genéricas/rango como "sp." o categorías informales reciben un nombre
  común genérico equivalente.
**Pendiente del cliente (no deducible, NO inventado)**:
- **Observador** de las 98 visitas 2025: no hay dato en el Excel.
- **UTM X/Y y municipio** de Lindus (LUG01) y Trona (LUG02): no se
  inventan coordenadas; la hoja `lugares` no tiene esas columnas.
- **`id_lugar` de V0001**.
- **Vocabularios** de las tablas nuevas (`fototrampeo.tipo_media`,
  `estudio_campo.deteccion/migracion/altura`,
  `castor_rastros.tipo_rastro/intensidad_rastro/reciente_antiguo`).
- **Quinto ecosistema** de `cajas_nido`.
**Aviso**: `grupo` y `nombre_comun` son deducciones; conviene que el
cliente las revise (sobre todo el grupo OTRO y los nombres de las
entradas genéricas) antes de la importación definitiva, pero no
bloquean: son corregibles editando la tabla `especies`.

---

## #46 — Importación del histórico 2025: decisiones de carga
**Fecha**: 2026-06-10
**Decisión**: La importación del histórico 2025 en el proyecto BirdLog
de Supabase (`mbphfgmjryyxzjgcwqxo`) se ejecutó con estas reglas:
- `utm_x`/`utm_y` de `lugares` → **NULL** (coords de Lindus y Trona
  pendientes del cliente). Se eliminó el NOT NULL del esquema v3.
- `id_observador` de las 97 visitas → **Gabi** (placeholder; el cliente
  no entregó el dato para las visitas históricas).
- `tipo_visita` de las 97 visitas → **LINDUS** (Lindus y Trona son
  conteos migratorios).
- **V0001** (sin `id_lugar`) y sus 34 lindus → **omitidos**; pendiente
  del cliente.
- **Fila mixta L002724** (3 MIGRADOR + 1 LOCAL) → dividida en
  L002724_1 y L002724_2 con sus respectivos `comportamiento`/`numero`.
- **Viento compuesto** (12 registros tipo "N/SO", "S N"...) → NULL en
  `viento_direccion`; literal original en `observaciones`.
- **Clave** en `.env`: clave anon del proyecto (JWT `eyJ...`). Permite
  INSERT/UPDATE/DELETE gracias a grants explícitos. Sustituir por
  `service_role` cuando se obtenga del dashboard de Supabase.
**Scripts**: `scripts/insertar_historico.py` (inserta via supabase-py)
y `scripts/importar_historico.py` (genera SQL de auditoría).
**Resultado**: 135 especies, 2 observadores, 2 lugares, 97 visitas,
1.048 meteo, 10.870 lindus.
