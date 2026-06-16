# Bitácora del proyecto

> Este archivo es la memoria viva del proyecto. Los agentes lo leen al
> iniciar cada sesión y lo actualizan cuando el usuario dice "rutina de cierre".

---

## Estado actual

- **Fase activa**: Primera versión basada en **hojas-guía** — el
  observador rellena plantillas tabulares que el agente valida antes de
  insertar en Supabase.
- **Última sesión**: 2026-06-16
- **Próxima tarea**: (a) revisar las 9 hojas-guía de `docs/Guias/` con el
  cliente y afinar columnas/ejemplos; (b) diseñar el flujo de revisión
  por el agente (hoja-guía/voz Telegram → validación → inserción en
  Supabase con autorización del usuario); (c) recoger del cliente:
  observador de las visitas históricas, coordenadas UTM de los puntos de
  conteo, vocabularios de las tablas nuevas y quinto ecosistema de
  `cajas_nido`.

---

## Tareas en curso

- [ ] (sin tareas en curso)

---

## Tareas pendientes

### Hojas-guía y flujo de validación por el agente
- [ ] Revisar las 9 hojas-guía de `docs/Guias/` con el cliente y confirmar
      columnas, ejemplos y vocabularios cerrados.
- [ ] Diseñar el flujo de revisión por el agente: hoja-guía/voz Telegram
      → validación → inserción en Supabase con autorización del usuario.

### Esquema v3 y pendientes del catálogo
- [ ] Recoger del cliente: observador de las visitas históricas,
      coordenadas UTM de los puntos de conteo (`utm_x`/`utm_y` de los
      lugares), vocabularios de las tablas nuevas
      (`fototrampeo.tipo_media`, `estudio_campo.deteccion/migracion/
      altura`, `castor_rastros.tipo_rastro/intensidad_rastro/
      reciente_antiguo`) y quinto ecosistema de `cajas_nido`.
- [ ] Confirmar el quinto ecosistema de `cajas_nido.ecosistema` con el
      observador.
- [ ] Rellenar `utm_x`/`utm_y` de los lugares cuando el cliente entregue
      las coordenadas (ETRS89 huso 30N).

### Pendiente general
- [ ] Sustituir clave anon en `.env` por `service_role` del proyecto
      Supabase (panel de Supabase → Settings → API → service_role).

---

## Tareas completadas

### Sesión 2026-06-16: Primera versión basada en hojas-guía (completado)
- [x] **`docs/Guias/` creado** con la referencia de formato
      (`formato-guias.md`: campos obligatorios, valores cerrados,
      normalización, validación y resolución de FKs) y **9 plantillas**
      con tablas de columnas reales: `lindus`, `cajas_nido`,
      `nidos_rapaces`, `cebos_avispones`, `mamiferos_puentes`,
      `fototrampeo`, `cuaderno_campo`, `estudio_campo`, `castor_rastros`.
- [x] **`pyproject.toml`** depurado: solo las dependencias del flujo
      actual (`supabase`, `pydantic`, `pandas`, `python-dotenv`,
      `google-api-python-client`).
- [x] **README.md, AGENTS.md y CLAUDE.md** actualizados al nuevo flujo
      (CLAUDE.md sincronizado con `cp`). Reglas de seguridad intactas.
- [x] **No se tocó `.env`** ni se subió nada a GitHub.

### Esquema v3, importación del histórico y base técnica
- [x] **Esquema v3 aplicado** en Supabase: 14 tablas con `utm_x`/`utm_y`
      nullable en `lugares`.
- [x] **Importación del histórico**: 135 especies, 2 observadores,
      2 lugares, 97 visitas, 1.048 meteo, 10.870 observaciones Lindus.
      V0001 omitida (sin `id_lugar`). Fila Lindus mixta dividida en dos.
- [x] **Scripts creados**: `scripts/importar_historico.py` (genera SQL)
      y `scripts/insertar_historico.py` (inserta vía supabase-py, lotes 200).
- [x] **`sql/003_esquema_v3.sql`** con `utm_x`/`utm_y` nullable.
- [x] **Columna `nidos_rapaces.observaciones`** añadida con migración
      aditiva `sql/004_observaciones_nidos_rapaces.sql`.
- [x] **Parser ampliado**: campos v3 en `CAMPOS_ENTEROS`, `incuba` como
      booleano, `fecha_colocacion` normalizada y validada.
- [x] **Inserción de campos v3**: `presentes/observando/visitantes` en
      meteo; `numero_trampa`, `fecha_colocacion` y UTM del nido en cebos;
      campos de cría en nidos rapaces.
- [x] **Backup actualizado al esquema v3**: exporta las 14 tablas con
      retención de 30 backups.
- [x] **142 tests pasan**.

---

## Bloqueos / dudas

- Vocabularios cerrados pendientes con el cliente:
  `fototrampeo.tipo_media`, `estudio_campo.deteccion/migracion/altura`,
  `castor_rastros.tipo_rastro/intensidad_rastro/reciente_antiguo`.
- Quinto ecosistema de `cajas_nido` pendiente de confirmar.
- Coordenadas UTM de los puntos de conteo pendientes del cliente.
- Observador de las visitas históricas pendiente.
- `id_lugar` de la primera visita (sin meteo asociada) pendiente del cliente.

---

## Glosario de archivos clave

- `src/config.py`: carga `.env`, expone objeto `Config` con las variables
  del proyecto.
- `src/conexion.py`: cliente Supabase, función `get_cliente()`.
- `src/insercion/catalogos.py`: resolución nombre → id con caché.
- `src/insercion/escritura.py`: inserción en Supabase, función
  `insertar_registro()`.
- `src/backup/exportar.py`: exportación de tablas a CSV local; retención
  de 30 backups.
- `src/drive/cliente.py`: cliente Google Drive con service account.
- `src/drive/operaciones.py`: listar, descargar, mover archivos.
- `src/fotos/sincronizar.py`: sincroniza fotos desde carpetas Drive
  `YYYY-MM-DD_Lugar` y registra URLs en la tabla `fotos`.
- `src/parser/texto_estructurado.py`: parser determinista de texto estructurado
  `CAMPO: valor`.
- `src/parser/validacion.py`: validaciones de mínimos, formato y valores
  cerrados.
- `src/parser/normalizacion.py`: normalización conservadora de valores.
- `tests/test_catalogos.py`: tests de resolución de catálogos.
- `tests/test_escritura.py`: tests de inserción con mocks.
- `tests/test_parser_texto_estructurado.py`: tests del parser heredado de texto estructurado, validación y
  normalización.
- `tests/test_backup_exportar.py`: tests del backup CSV.
- `docs/Guias/formato-guias.md`: referencia de campos, valores cerrados,
  normalización y validación para las hojas-guía.
- `docs/Guias/`: plantillas de hoja-guía por tipo de
  visita/observación.
- `docs/modelo_datos.md`: descripción completa de las 14 tablas (v3).
- `docs/SEGURIDAD.md`: reglas de seguridad y manejo de credenciales.
- `docs/DECISIONES.md`: historial de decisiones técnicas tomadas.
- `sql/002_esquema_v2.sql`: esquema v2 (referencia histórica).
- `sql/003_esquema_v3.sql`: esquema v3 definitivo (14 tablas), aplicado
  en Supabase.
- `sql/004_observaciones_nidos_rapaces.sql`: migración aditiva que añade
  `observaciones TEXT` a `nidos_rapaces`.
- `scripts/importar_historico.py`: genera SQL INSERT desde el Excel
  histórico.
- `scripts/insertar_historico.py`: inserta el histórico en Supabase por
  lotes de 200.
- `.env.example`: plantilla de variables de entorno (sin valores reales).
