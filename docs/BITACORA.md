# Bitácora del proyecto

> Este archivo es la memoria viva del proyecto. Codex y Claude Code lo
> leen al iniciar cada sesión y lo actualizan cuando el usuario dice
> "rutina de cierre".

---

## Estado actual

- **Fase activa**: Fase 6 — Dashboard Streamlit
- **Última sesión**: 2026-05-02
- **Próxima tarea**: Implementar dashboard Streamlit completo
  (8 páginas + tema visual verde naturaleza)

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
- [ ] Verificar que `sql/002_esquema_v2.sql` incluye
      `GENERATED ALWAYS AS IDENTITY` en todas las columnas `id_*`

### Fase 6: Dashboard
- [ ] Implementar `dashboard/app.py`
- [ ] Implementar 8 páginas en `dashboard/paginas/`
- [ ] Implementar `dashboard/lib/` (`consultas`, `graficos`, `mapas`,
      `edicion`, `filtros`)
- [ ] Crear `.streamlit/config.toml` con tema verde naturaleza
- [ ] Instalar librerías: `streamlit`, `streamlit-folium`, `folium`,
      `pandas`, `altair`, `pyproj`
- [ ] Verificar arranque sin errores

---

## Tareas completadas

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
- Las columnas `id_*` de todas las tablas no tenían `GENERATED ALWAYS AS
  IDENTITY`. Se corrigió manualmente en Supabase dev con `ALTER TABLE`.
  Pendiente verificar que `sql/002_esquema_v2.sql` refleja esto
  correctamente para cuando se aplique en prod.

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
- `.env.example`: plantilla de variables de entorno (sin valores reales).
- `diagrama_relaciones_v2.html`: diagrama visual de relaciones entre tablas.

---

## Handoff

Fase 5 queda completada. Las fotos viven en Drive bajo
`Fotos/YYYY-MM-DD_Lugar/`; la sincronización es un proceso separado del
pipeline de `.txt`. `src/fotos/sincronizar.py` escanea carpetas, deduce
fecha y lugar, localiza la visita en Supabase y registra URLs nuevas en
`fotos` evitando duplicados.

Siguiente agente: no tocar prod. La fase activa pasa a Fase 6 —
Dashboard Streamlit. La próxima tarea es implementar el dashboard
completo con 8 páginas y tema visual verde naturaleza.

Atención: quedan dos tareas generales antes de dar por cerrado el entorno
dev: limpiar visitas de prueba duplicadas (`id_visita` 3, 4, 5, 6 y cebos
asociados) y verificar que `sql/002_esquema_v2.sql` incluye
`GENERATED ALWAYS AS IDENTITY` en todas las columnas `id_*`.
