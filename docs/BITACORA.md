# Bitácora del proyecto

> Este archivo es la memoria viva del proyecto. Codex y Claude Code lo
> leen al iniciar cada sesión y lo actualizan cuando el usuario dice
> "rutina de cierre".

---

## Estado actual

- **Fase activa**: Fase 6 — Dashboard Streamlit completada
- **Última sesión**: 2026-05-02
- **Próxima tarea**: Revisión manual del dashboard con el observador y
  preparar uso real. La incidencia de IDs autogenerados queda resuelta en
  Supabase dev y en `sql/002_esquema_v2.sql`.

---

## Tareas en curso

- [ ] (sin tareas en curso)

---

## Tareas pendientes

### Fase 2: Plantilla Plaud
- [ ] Hacer grabaciones reales de prueba (Lindus, cebos avispón, cajas nido)
- [ ] Confirmar con el observador el quinto ecosistema de cajas_nido

### Fase 3: Parser
- [ ] Recoger 5-6 .txt de ejemplo de tipos distintos de visita

### Pendiente general
- [ ] Limpiar visitas de prueba duplicadas en Supabase dev
      (borrar `id_visita` 3, 4, 5, 6 y sus cebos asociados)

### Fase 6: Dashboard
- [x] Implementar `dashboard/app.py`
- [x] Implementar 8 páginas en `dashboard/paginas/`
- [x] Implementar `dashboard/lib/` (`consultas`, `graficos`, `mapas`,
      `edicion`, `filtros`)
- [x] Crear `.streamlit/config.toml` con tema verde naturaleza
- [x] Instalar librerías: `streamlit`, `streamlit-folium`, `folium`,
      `pandas`, `altair`, `pyproj`
- [x] Verificar arranque sin errores
- [x] Fase 6.5 — Implementar edición, altas y borrado seguro
- [x] Fase 6.6 — Pulido final, revisión visual, documentación y pruebas
      de uso

---

## Tareas completadas

### Incidencia: IDs autogenerados en Supabase (resuelta 2026-05-02)
- [x] Diagnóstico de las 11 PKs `id_*` mediante `information_schema` en
      Supabase dev: 7 ya tenían `IDENTITY ALWAYS` (corregidas manualmente
      en sesiones previas), 4 seguían como `INTEGER PRIMARY KEY` simple
      (`especies`, `observadores`, `lugares`, `fotos`).
- [x] Corrección manual en Supabase dev de las 4 PKs pendientes con
      `ALTER TABLE ... ADD GENERATED ALWAYS AS IDENTITY` y `setval` al
      MAX existente para no chocar con catálogos cargados.
- [x] Verificación de que el dashboard nunca insertaba IDs manuales: la
      lógica de `dashboard/lib/edicion.py` ya elimina la columna ID del
      payload antes de enviar a Supabase.
- [x] Prueba real de alta + edición + borrado de la especie
      `TEST_DASHBOARD_NO_USAR` ejecutando las funciones reales de
      `dashboard/lib/edicion.py` contra Supabase dev: `id_especie=158`
      autogenerado, edición aplicada, borrado limpio. Backup CSV y traza
      generados en cada paso.
- [x] Actualización de `sql/002_esquema_v2.sql` para que las 11 PKs queden
      como `INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY` y la próxima
      aplicación a un entorno limpio salga correcta desde el principio.
- [x] Commit creado: `70544ff fix(sql): autogenerar las 11 PKs id_* con
      GENERATED ALWAYS AS IDENTITY`.
- [x] Comprobaciones realizadas: `pytest` (54 tests), `py_compile` del
      dashboard, imports de las 8 páginas, verificación con `grep` de las
      11 PKs en el SQL editado, revisión de secretos en diff.

### Fase 6.6: Pulido final, documentación y pruebas de uso (completado)
- [x] Dashboard Fase 6 completado para uso local.
- [x] Documentación de uso creada en `docs/USO_DASHBOARD.md`.
- [x] Pulido menor aplicado en Edición / Catálogos: claves de widgets más
      específicas, tablas con anchura actualizada y mensajes de error más
      claros para operaciones rechazadas por Supabase.
- [x] Prueba controlada de alta/edición/borrado intentada con
      `TEST_DASHBOARD_NO_USAR`.
- [x] Resultado de la prueba controlada: la inserción fue rechazada por
      Supabase porque `id_especie` no se autogeneró. No se forzó ningún ID
      manual, no se completó alta/edición/borrado real y quedó creado backup
      CSV local + traza mínima previa al intento.
- [x] Commit creado:
      `bb8e3b4 chore(dashboard): pulir dashboard y documentar uso`.
- [x] Comprobaciones realizadas: `py_compile`, imports de las 8 páginas,
      `pytest` (54 tests), `streamlit run dashboard/app.py`, HTTP local 200,
      revisión de secretos en diff/traza, verificación de que no se modificó
      SQL ni `.env`, y comprobación local de que el borrado exige `BORRAR`.

### Fase 6.5: Edición, altas y borrado seguro (completado)
- [x] Página `dashboard/paginas/08_edicion.py` implementada.
- [x] Tablas editables incluidas: `especies`, `observadores`, `lugares`,
      `visitas`, `meteorologia`, `lindus`, `cajas_nido`,
      `nidos_rapaces`, `cebos_avispones`, `mamiferos_puentes` y `fotos`.
- [x] Alta de registros implementada con validación de campos
      obligatorios, valores cerrados y selectores legibles para FKs.
- [x] Edición de registros implementada con formulario precargado,
      validación y confirmación antes de guardar.
- [x] Borrado seguro implementado con resumen del registro, aviso visible,
      confirmación escrita exacta `BORRAR`, comprobación de dependencias
      cargadas, backup CSV local previo y traza mínima local.
- [x] Commit creado:
      `9bfdb6a feat(dashboard): añadir edición altas y borrado seguro`.
- [x] Comprobaciones realizadas: `py_compile`, imports de las 8 páginas,
      `pytest` (54 tests), render mínimo de Edición, `streamlit run
      dashboard/app.py`, HTTP local 200, revisión de secretos en diff y
      verificación de que no se modificó SQL.

### Fase 6.4: Páginas de consulta biológica (completado)
- [x] Lindus implementado con filtros, métricas, gráficos, tabla, detalle,
      meteorología asociada y fotos Drive cuando existan.
- [x] Cajas nido implementado con métricas de ocupación, filtros, gráficos,
      mapa, tabla, detalle y fotos asociadas.
- [x] Nidos rapaces implementado con histórico, filtros, ficha de revisión,
      texto cómodo, comunicación personal, mapa y fotos asociadas.
- [x] Cebos avispones implementado con totales, composición, ranking,
      evolución, acumulado calculado en dashboard, mapa, tabla y detalle.
- [x] Mamíferos puentes implementado con filtros, resumen por presencia,
      evidencias, diversidad por puente, mapa, tabla, detalle y fotos.
- [x] Commit creado:
      `eca458f feat(dashboard): añadir páginas de consulta por tipo de visita`.
- [x] Comprobaciones realizadas: `py_compile`, imports de las 8 páginas,
      `pytest` (54 tests), renders con datos vacíos y sintéticos,
      `streamlit run dashboard/app.py`, HTTP local 200, revisión de secretos
      en diff y verificación de que no se modificó SQL.

### Fase 5: Gestión de fotos (completado)
- [x] Fase 5 completa: `src/fotos/sincronizar.py`, 54 tests pasando.
- [x] Decidir convención de carpetas en Drive para fotos:
      `Fotos/YYYY-MM-DD_Lugar/`.
- [x] Definir que la vinculación de fotos a visitas es un proceso separado
      del pipeline principal.
- [x] Añadir `DRIVE_FOTOS_ID` a `.env.example`.
- [x] Carpeta `Fotos/` creada en Drive y compartida con service account.
- [x] `DRIVE_FOTOS_ID` configurado en `.env`.
- [x] Implementar `src/fotos/sincronizar.py` para escanear Drive, buscar
      visitas por fecha y lugar, evitar duplicados y registrar URLs en
      `fotos`.
- [x] Tests de sincronización de fotos con mocks pasando.

### Fase 4: Inserción y backup (completado)
- [x] `src/config.py`, `src/conexion.py` creados y funcionando.
- [x] `src/insercion/catalogos.py` y `src/insercion/escritura.py`
      funcionando.
- [x] `src/backup/exportar.py` funcionando (backup local).
- [x] `src/drive/cliente.py` y `src/drive/operaciones.py` funcionando.
- [x] `src/pipeline.py` funcionando.
- [x] 48 tests pasando.
- [x] Conexión real a Supabase dev verificada.
- [x] Pipeline completo probado de extremo a extremo: descarga `.txt` de
      Drive `01_entrada` → parsea → valida → resuelve FKs → inserta en
      Supabase → backup CSV local → mueve `.txt` a `02_procesados`.
- [x] Backup en Drive descartado: service accounts no tienen cuota de
      almacenamiento (decisión #25).
- [x] Configuración Google Drive completada: service account
      `birdlog-drive` creado, credenciales en
      `~/.config/sistema-fauna/google-credentials.json`, carpetas
      `01_entrada`, `02_procesados`, `03_errores` y `Backups` compartidas
      con el service account.
- [x] Primera inserción real en BD: visita + `cebo_avispon` insertados OK.

### Fase 3: Parser (completado)
- [x] Parser Plaud determinista (`src/parser/plaud.py`).
- [x] Validación de registros (`src/parser/validacion.py`).
- [x] Normalización conservadora (`src/parser/normalizacion.py`).
- [x] Ejemplos sintéticos para las 7 plantillas en `tests/ejemplos_plaud/`.
- [x] Tests de parser, validación y normalización pasando: 39 tests.

### Diseño de la base de datos (completado)
- [x] Diseño inicial de 11 tablas (v1)
- [x] Revisión con el observador mediante conversación grabada
- [x] Rediseño completo tabla por tabla (v2): 10 tablas definitivas
- [x] SQL de creación generado: `sql/002_esquema_v2.sql`
- [x] Diagrama de relaciones generado: `diagrama_relaciones_v2.html`
- [x] Documentos del proyecto actualizados (v3)

### Fase 2: Plantilla Plaud (completado)
- [x] Diseño de plantillas Plaud definitivas v1
- [x] Listar los campos exactos que devolverá el .txt por tipo de visita
- [x] Definir vocabulario cerrado por campo (lugares, especies frecuentes,
      comportamiento, ecosistema, estado_nido, tipo_evidencia...)
- [x] Documentar el formato exacto en `docs/formato_plaud.md`

### Fase 1: Supabase inicial (completado parcialmente)
- [x] Crear proyecto Supabase dev
- [x] Aplicar esquema v1 (ya obsoleto — aplicar v2)
- [x] Importar datos históricos de Lindus 2025 (10.905 observaciones)
- [x] Importar datos meteorológicos de Lindus (1.083 registros)
- [ ] **Pendiente**: aplicar esquema v2 (borrar tablas v1 y crear v2)
- [ ] **Pendiente**: regenerar y reimportar datos con nueva estructura

---

## Bloqueos / dudas

- Quinto ecosistema de cajas_nido pendiente de confirmar con el observador.

---

## Glosario de archivos clave

- `src/config.py`: carga `.env`, expone objeto `Config` con todas las
  variables del proyecto.
- `src/conexion.py`: cliente Supabase, función `get_cliente()`.
- `src/insercion/catalogos.py`: resolución nombre → id con caché.
- `src/insercion/escritura.py`: inserción en Supabase, función
  `insertar_registro()`.
- `src/backup/exportar.py`: exportación de tablas a CSV local.
- `src/drive/cliente.py`: cliente Google Drive con service account.
- `src/drive/operaciones.py`: listar, descargar, mover archivos.
- `src/pipeline.py`: orquestador, funciones `procesar_drive()` y
  `procesar_txt_local()`.
- `src/fotos/sincronizar.py`: sincroniza fotos desde carpetas Drive
  `YYYY-MM-DD_Lugar`, busca la visita correspondiente y registra URLs en
  la tabla `fotos`.
- `dashboard/paginas/03_lindus.py`: consulta Lindus con filtros, gráficos,
  detalle, meteorología y fotos.
- `dashboard/paginas/04_cajas_nido.py`: consulta de cajas nido con métricas,
  gráficos, mapa, tabla, detalle y fotos.
- `dashboard/paginas/05_nidos_rapaces.py`: histórico de nidos rapaces con
  ficha de revisión, mapa y fotos.
- `dashboard/paginas/06_cebos_avispones.py`: seguimiento de cebos con
  acumulados calculados, composición, mapa y detalle.
- `dashboard/paginas/07_mamiferos_puentes.py`: consulta de mamíferos en
  puentes con filtros espaciales, evidencias, diversidad y fotos.
- `dashboard/paginas/08_edicion.py`: edición de catálogos y tablas de
  campo con altas, modificaciones y borrado seguro.
- `dashboard/lib/consultas.py`: carga paginada de tablas Supabase,
  DataFrames legibles y métricas/agregados comunes del dashboard.
- `dashboard/lib/filtros.py`: filtros reutilizables por fecha, especie,
  lugar, tipo y rangos.
- `dashboard/lib/fotos.py`: filtrado de fotos asociadas por visita u origen
  y preparación de enlaces Drive.
- `dashboard/lib/mapas.py`: conversión UTM → lat/lon y mapas Folium por
  lugar/tipo.
- `dashboard/lib/graficos.py`: gráficos Altair reutilizables.
- `dashboard/lib/ui.py`: componentes visuales reutilizables de Streamlit.
- `dashboard/lib/edicion.py`: metadatos de campos editables, validaciones,
  backup previo, traza local y operaciones de alta, edición y borrado.
- `tests/test_catalogos.py`: tests con mocks para resolución de catálogos.
- `tests/test_escritura.py`: tests con mocks para inserción sin BD real.
- `src/parser/plaud.py`: parser determinista de archivos `.txt` de Plaud.
  Detecta `TIPO_REGISTRO`, separa cabecera, meteorología y datos, y
  convierte tipos simples.
- `src/parser/validacion.py`: validaciones de mínimos, formato y valores
  cerrados para los registros Plaud parseados.
- `src/parser/normalizacion.py`: normalización conservadora de códigos de
  cajas, cebos, booleanos y variantes menores de comportamiento.
- `src/parser/`: paquete de parseo, validación y normalización de `.txt`
  Plaud.
- `tests/test_parser_plaud.py`: tests pytest del parser, validación y
  normalización.
- `tests/ejemplos_plaud/`: ejemplos sintéticos `.txt` para las 7 plantillas
  Plaud activas.
- `data/pendientes/.gitkeep`: mantiene versionada la carpeta donde más
  adelante quedarán los `.txt` pendientes de reproceso.
- `sql/002_esquema_v2.sql`: esquema definitivo. Incluye DROP de tablas
  anteriores y CREATE de las 10 tablas nuevas. Aplicar en SQL Editor
  de Supabase.
- `docs/modelo_datos.md`: descripción completa de las 10 tablas con
  todos los campos, tipos y valores cerrados.
- `docs/formato_plaud.md`: plantillas Plaud definitivas v1 y formato
  estructurado esperado para los `.txt`.
- `docs/SEGURIDAD.md`: reglas de seguridad y manejo de credenciales.
- `docs/DECISIONES.md`: historial de decisiones técnicas tomadas.
- `docs/USO_DASHBOARD.md`: guía de uso local del dashboard para el
  observador, incluyendo arranque, páginas, filtros, fotos, edición,
  borrado seguro y errores de Supabase.
- `.env.example`: plantilla de variables de entorno (sin valores reales).
- `diagrama_relaciones_v2.html`: diagrama visual de relaciones entre tablas.

---

## Handoff

Fase 5 queda completada. Las fotos viven en Drive bajo
`Fotos/YYYY-MM-DD_Lugar/`; la sincronización es un proceso separado del
pipeline de `.txt`. `src/fotos/sincronizar.py` escanea carpetas, deduce
fecha y lugar, localiza la visita en Supabase y registra URLs nuevas en
`fotos` evitando duplicados.

Siguiente agente: no tocar prod. Fase 6 queda completada con dashboard
Streamlit local, 8 páginas navegables, consultas, mapas, gráficos, fotos,
edición, altas y borrado seguro. La próxima tarea recomendada es una revisión
manual con el observador; después, corregir incidencias detectadas y preparar
uso real.

Atención: queda una tarea general antes de dar por cerrado el entorno dev:
limpiar visitas de prueba duplicadas (`id_visita` 3, 4, 5, 6 y cebos
asociados). La incidencia de IDs autogenerados queda resuelta tanto en
Supabase dev como en `sql/002_esquema_v2.sql` (commit `70544ff`).
