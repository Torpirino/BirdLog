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
