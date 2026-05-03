# Plan de la app local de pipeline (Plaud → Supabase)

> Documento de diseño — fase 8. **No implementa código todavía.**
> Actualizar este archivo si el diseño cambia durante la implementación.
> Fecha de creación: 2026-05-03.

---

## 1. Objetivo

Construir una app local con interfaz gráfica sencilla para que el
observador (usuario no técnico) gestione él mismo el pipeline
Plaud → Supabase sin tocar consola ni scripts ad hoc.

La app sustituye al enfoque eliminado de `demo.py` (decisión #30) y
es independiente del dashboard actual (`dashboard/app.py`), que
queda dedicado exclusivamente a consulta y edición de datos.

La app debe permitir:

1. Procesar con un clic todas las grabaciones nuevas que el Plaud
   ha sincronizado en la carpeta Drive `01_entrada`.
2. Ver de un vistazo qué archivos se han procesado, cuáles han
   fallado y por qué.
3. Saltar al dashboard Streamlit ya existente.
4. Saltar a Claude.ai (asistencia conversacional para el observador).

---

## 2. Pipeline actual — diagnóstico

Resumen del código existente (no se modifica en esta fase). Sirve
como base para diseñar la capa de UI sin tocar lógica.

### 2.1 Entrada y orquestación

- **`src/pipeline.py`**
  - `procesar_drive() -> list[dict]`: lista los `.txt` de la carpeta
    Drive `DRIVE_ENTRADA_ID`, los descarga uno a uno a directorio
    temporal y los pasa a `procesar_txt_local`. Tras procesar,
    mueve el archivo a `DRIVE_PROCESADOS_ID` (éxito) o
    `DRIVE_ERRORES_ID` (excepción).
  - `procesar_txt_local(ruta, cliente, ...) -> dict`: parsea →
    valida → normaliza → resuelve FKs → inserta → backup CSV local.
    Si la validación falla, lanza `ValueError` con mensaje claro y
    el `.txt` se mueve a errores en Drive desde `procesar_drive`.

### 2.2 Movimiento de archivos en Drive

- **Carpetas Drive (IDs en `.env`)**:
  - `DRIVE_ENTRADA_ID` → `01_entrada` — Plaud deja los `.txt` aquí.
  - `DRIVE_PROCESADOS_ID` → `02_procesados` — destino de los `.txt`
    insertados correctamente.
  - `DRIVE_ERRORES_ID` → `03_errores` — destino de los `.txt` con
    error de validación o inserción.
  - `DRIVE_BACKUPS_ID` → `Backups` — históricamente para backups
    (decisión #25: backups ya **no** se suben a Drive; la variable
    sigue requerida por compatibilidad de `Config`).
  - `DRIVE_FOTOS_ID` → `Fotos` — usado por `src/fotos/sincronizar.py`,
    independiente del pipeline Plaud.
- **`src/drive/operaciones.py`**: `listar_txt`, `descargar_archivo`,
  `mover_archivo`, `subir_archivo`, `subir_carpeta_csv`.
- **`src/drive/cliente.py`**: `get_drive()` con service account.

### 2.3 Parser, validación y resolución de FKs

- **`src/parser/plaud.py`**: detecta `TIPO_REGISTRO`, parsea la
  cabecera y los bloques (`OBSERVACION_LINDUS`, `METEOROLOGIA`,
  `CAJA_NIDO`, `CEBO_AVISPON`, `NIDO_RAPAZ`, `MAMIFERO_PUENTE`).
- **`src/parser/validacion.py`** y **`src/parser/normalizacion.py`**:
  validación de campos mínimos, valores cerrados y normalización
  conservadora (capitalización, booleanos…).
- **`src/insercion/catalogos.py`**: `resolver_lugar`,
  `resolver_observador`, `resolver_especie`. Si un nombre no existe
  en el catálogo, lanza `ValueError` con mensaje accionable
  ("Da de alta en Supabase y añade el nombre al vocabulario del
  Plaud").
- **`src/insercion/escritura.py`**: inserta en `visitas`,
  `meteorologia` y la tabla específica del tipo de registro,
  resolviendo todas las FKs antes de tocar la BD (decisión #23).

### 2.4 Backup

- **`src/backup/exportar.py`**: `hacer_backup(cliente)` exporta las
  11 tablas a CSV en `backups/backup_YYYY-MM-DD/`. Solo local
  (decisión #25). Se ejecuta tras cada inserción exitosa desde
  `procesar_txt_local`.

### 2.5 Configuración

- **`src/config.py`**: carga `.env`, valida presencia de las 11
  variables y bloquea `ENTORNO=prod` (decisión #23).
- Variables `.env` necesarias para el pipeline:
  - `ENTORNO` (debe ser `dev`)
  - `SUPABASE_DEV_URL`, `SUPABASE_DEV_KEY`
  - `SUPABASE_PROD_URL`, `SUPABASE_PROD_KEY` (presentes pero
    bloqueadas por código)
  - `GOOGLE_CREDENTIALS_PATH`
  - `DRIVE_ENTRADA_ID`, `DRIVE_PROCESADOS_ID`, `DRIVE_ERRORES_ID`,
    `DRIVE_BACKUPS_ID`, `DRIVE_FOTOS_ID`

### 2.6 Reporte de errores actual

Hoy el reporte se hace por consola: cada `procesar_txt_local`
lanza `ValueError` con mensaje legible o devuelve un dict con
`{archivo, estado, resumen|mensaje}`. Falta capa visual.

---

## 3. Arquitectura propuesta de la app

### 3.1 Carpeta y archivos

```
app_pipeline/
├── __init__.py
├── app.py                  # Entrada Streamlit, layout y navegación
├── lib/
│   ├── __init__.py
│   ├── orquestador.py      # Wrapper sobre src.pipeline con estados
│   ├── estados.py          # Constantes y modelo de resultado
│   ├── ui.py               # Componentes visuales (tarjetas, badges)
│   └── enlaces.py          # URLs de dashboard local y Claude.ai
└── README.md               # (opcional) instrucciones de arranque
```

- **`app.py`**: una sola página Streamlit. No reusa el sistema de
  páginas del dashboard. Layout simple en bloques verticales.
- **`lib/orquestador.py`**: única dependencia funcional. Llama a
  `src.pipeline.procesar_drive()` y traduce cada resultado a un
  objeto `ResultadoArchivo` con estado de color, etapa alcanzada
  y mensaje humano. **No reimplementa pipeline**, solo lo envuelve.
- **`lib/estados.py`**: enum/constantes de estado
  (`OK`, `ERROR`, `INCOMPLETO`, `PENDIENTE`) y dataclass
  `ResultadoArchivo` con campos:
  `nombre`, `estado`, `etapa`, `mensaje`,
  `txt_movido_a` (`procesados`/`errores`/`-`),
  `insertado_supabase` (bool), `backup_creado` (bool|str).
- **`lib/ui.py`**: tarjeta visual por archivo, badges de color,
  bloques de cabecera, botones grandes.
- **`lib/enlaces.py`**: helpers para abrir el dashboard local
  (`http://localhost:8501`) y Claude.ai (`https://claude.ai`) en
  pestaña nueva.

### 3.2 Relación con `src/pipeline.py`

- La app **no duplica lógica**. Llama a `src.pipeline.procesar_drive()`.
- `lib/orquestador.py` añade:
  - Captura de `RuntimeError` por Supabase pausado (mensaje
    `"El proyecto Supabase está pausado..."`) y lo traduce a un
    estado global "Supabase pausado".
  - Captura de errores de Drive (credenciales, carpeta inexistente)
    y los traduce a estado "Drive no disponible".
  - Detección por sub-cadena en el mensaje para clasificar:
    - "Lugar no encontrado" / "Observador no encontrado" /
      "Especie no encontrada" → estado `INCOMPLETO` (catálogo).
    - "no es válido" → estado `ERROR` (validación).
    - Otros → estado `ERROR` genérico.
- Si más adelante se quiere granularidad fina (saber por archivo si
  se llegó a backup, por ejemplo), se puede ampliar el dict que
  devuelve `procesar_drive` sin cambiar la firma. Pendiente para
  fase 2 de la app.

### 3.3 Funciones principales (firmas tentativas)

```python
# app_pipeline/lib/estados.py
@dataclass(frozen=True)
class ResultadoArchivo:
    nombre: str
    estado: Literal["OK", "ERROR", "INCOMPLETO", "PENDIENTE"]
    etapa: str          # "Descarga", "Parser", "Validación",
                        # "Catálogos", "Inserción", "Backup"
    mensaje: str
    txt_movido_a: Literal["procesados", "errores", "-"]
    insertado_supabase: bool
    backup_creado: bool

# app_pipeline/lib/orquestador.py
def procesar_lote() -> list[ResultadoArchivo]: ...
def comprobar_entorno() -> EstadoEntorno: ...   # dev/prod, .env, drive

# app_pipeline/lib/ui.py
def render_cabecera(): ...
def render_botones_principales(): ...
def render_resultados(resultados: list[ResultadoArchivo]): ...
def tarjeta_resultado(resultado: ResultadoArchivo): ...
```

---

## 4. Diseño de interfaz (usuario no técnico)

### 4.1 Pantalla única

Layout vertical en tres bloques:

#### Bloque 1 — Cabecera

- Título grande: **"BirdLog — Pipeline Plaud"**.
- Indicador de estado del entorno:
  - Verde: `dev` operativo, `.env` cargado, Drive accesible,
    Supabase responde.
  - Amarillo: `dev` operativo pero Drive sin acceso o Supabase lento.
  - Rojo: falta `.env`, Supabase pausado o credenciales inválidas.
- Texto pequeño con: entorno activo (`dev`), carpeta Drive de
  entrada y fecha/hora del último procesado.

#### Bloque 2 — Acciones principales

Tres botones grandes en fila:

1. **"Procesar grabaciones de Plaud"** (primario, verde).
   - Lanza `procesar_lote()`. Muestra spinner mientras corre.
   - Si el entorno no está OK, deshabilitado con tooltip claro.
2. **"Abrir dashboard"**.
   - Abre `http://localhost:8501` en pestaña nueva.
   - Texto secundario: "Asegúrate de tener el dashboard
     arrancado: `streamlit run dashboard/app.py`".
3. **"Abrir Claude.ai"**.
   - Abre `https://claude.ai` en pestaña nueva.

#### Bloque 3 — Resultados del último procesado

- Si no hay aún ejecución: mensaje neutro
  "Aún no has procesado ninguna grabación en esta sesión".
- Si hay ejecución: una tabla resumen + tarjetas detalladas.

**Tabla resumen** (5 columnas):

| Archivo | Estado | Etapa | Movido a | Mensaje corto |
|---------|--------|-------|----------|----------------|

**Tarjetas detalladas** (una por archivo):

```
┌─────────────────────────────────────────────────────────┐
│ 🟢  visita_lindus_2026-05-03.txt                        │
│ Estado: Procesado correctamente                          │
│ Etapa final: Backup                                      │
│ ✅ Insertado en Supabase   ✅ Backup creado              │
│ 📁 .txt movido a 02_procesados                           │
│ Resumen: visita id=42, 3 observaciones Lindus            │
└─────────────────────────────────────────────────────────┘
```

```
┌─────────────────────────────────────────────────────────┐
│ 🟡  visita_caja_AREATZEA1.txt                           │
│ Estado: Catálogo no encontrado                           │
│ Etapa: Resolución de FKs                                 │
│ ❌ No insertado            ❌ Sin backup                 │
│ 📁 .txt movido a 03_errores                              │
│ Mensaje: Especie no encontrada: 'milano negro'.          │
│   Da de alta en Supabase (tabla especies) y añade el     │
│   nombre al vocabulario del Plaud.                       │
└─────────────────────────────────────────────────────────┘
```

```
┌─────────────────────────────────────────────────────────┐
│ 🔴  visita_cebo.txt                                      │
│ Estado: Error de validación                              │
│ Etapa: Validación                                        │
│ ❌ No insertado            ❌ Sin backup                 │
│ 📁 .txt movido a 03_errores                              │
│ Mensaje: El archivo visita_cebo.txt no es válido:        │
│   - Falta campo obligatorio 'fecha'                      │
└─────────────────────────────────────────────────────────┘
```

### 4.2 Reglas de UX

- Botones grandes, etiquetas en español natural.
- Sin jerga técnica visible (no aparecen palabras como "FK",
  "JSON", "stack trace") salvo el nombre exacto de los catálogos
  (`especies`, `lugares`, `observadores`) para que el observador
  sepa dónde dar el alta.
- Cualquier error crítico se muestra como bloque rojo en la
  cabecera, no como excepción Python.
- Mensajes de Supabase pausado y de credenciales inválidas usan
  los mismos textos que el dashboard
  (`dashboard/lib/conexion.py`) para consistencia.

---

## 5. Estados de resultado (colores y significado)

| Color    | Estado            | Significado                                                                                          | `.txt` movido a       | Inserción | Backup |
|----------|-------------------|------------------------------------------------------------------------------------------------------|-----------------------|-----------|--------|
| 🟢 Verde | `OK`              | Procesado correctamente: parseado, validado, FKs resueltas, insertado y backup creado.               | `02_procesados`        | Sí        | Sí     |
| 🟡 Amarillo | `INCOMPLETO`   | Falta dato de catálogo (lugar, observador o especie). El observador tiene que dar de alta y reintentar. | `03_errores`           | No        | No     |
| 🔴 Rojo  | `ERROR`           | Archivo malformado, validación fallida, o error inesperado de Supabase/Drive durante este archivo.   | `03_errores`           | No        | No     |
| ⚪ Gris   | `PENDIENTE`       | Reservado: aún no procesado en esta sesión, o lote vacío.                                            | `-`                    | No        | No     |

### 5.1 Casos especiales (no por archivo, sino globales)

- **Supabase pausado**: la app no llega a procesar archivos. Bloque
  rojo en cabecera con el texto fijo
  *"El proyecto Supabase está pausado. Reactívalo en supabase.com
  y vuelve a intentarlo."* (decisión #12). Botón "Procesar"
  deshabilitado.
- **Drive no disponible** (credenciales inválidas, carpeta
  inaccesible): bloque rojo con mensaje
  *"No se pudo acceder a Google Drive. Revisa el archivo de
  credenciales y los IDs de carpeta en `.env`."*
- **Lote vacío**: si `01_entrada` no tiene `.txt`, bloque amarillo
  informativo *"No hay grabaciones nuevas en Drive"*. No es error.

### 5.2 Flujo decisión por archivo

```
descarga OK?
├── no → ERROR (rojo). El archivo permanece en 01_entrada.
└── sí → parser OK?
        ├── no → ERROR (rojo). Mover a 03_errores.
        └── sí → validación OK?
                ├── no → ERROR (rojo). Mover a 03_errores.
                └── sí → catálogos OK?
                        ├── no → INCOMPLETO (amarillo). Mover a 03_errores.
                        └── sí → inserción OK?
                                ├── no → ERROR (rojo). Mover a 03_errores.
                                └── sí → backup OK?
                                        ├── no → OK con aviso. Mover a 02_procesados.
                                        └── sí → OK (verde). Mover a 02_procesados.
```

---

## 6. Carpetas Drive implicadas

| Variable `.env`         | Carpeta Drive  | Uso en la app                                  |
|-------------------------|----------------|------------------------------------------------|
| `DRIVE_ENTRADA_ID`      | `01_entrada`   | Lectura: lista los `.txt` a procesar.          |
| `DRIVE_PROCESADOS_ID`   | `02_procesados`| Escritura: destino de éxitos.                  |
| `DRIVE_ERRORES_ID`      | `03_errores`   | Escritura: destino de errores e incompletos.   |
| `DRIVE_BACKUPS_ID`      | `Backups`      | No se usa (decisión #25). Variable conservada. |
| `DRIVE_FOTOS_ID`        | `Fotos`        | No se usa en el pipeline Plaud.                |

---

## 7. Variables `.env` necesarias

La app **no introduce variables nuevas**. Reusa exactamente las del
pipeline existente (sección 2.5). Si falta alguna, `cargar_config()`
ya lanza un `RuntimeError` con la lista que falta; la app debe
mostrarlo como bloque rojo.

---

## 8. Decisión de herramienta

### 8.1 Opciones consideradas

**A. Streamlit (mismo stack que el dashboard).**
- Pros:
  - Stack ya instalado y en uso (decisión #5).
  - El observador ya conoce el patrón visual del dashboard.
  - Componentes nativos suficientes (`st.button`, `st.dataframe`,
    `st.status`, `st.empty`, `st.expander`).
  - Reutilizamos `dashboard/lib/ui.py` y `.streamlit/config.toml`
    para consistencia visual.
  - Coste de implementación bajo. Tests visuales mínimos.
- Contras:
  - Requiere arrancar un segundo proceso (`streamlit run
    app_pipeline/app.py`). Mitigación: script de arranque o alias
    documentado.
  - Streamlit es reactivo; abrir Claude.ai/dashboard en pestaña
    nueva requiere `st.link_button` o JS pequeño, no `webbrowser.open`.

**B. Tkinter / PySimpleGUI / Toga (app de escritorio nativa).**
- Pros: app de escritorio "real", arranca con doble clic.
- Contras:
  - Stack nuevo, dependencia adicional, hay que justificar
    (sección 3 de AGENTS.md).
  - El observador ya está en el navegador (Plaud, Drive, Claude.ai,
    dashboard). Una segunda ventana de escritorio rompe el flujo.
  - Sin precedente en el repo. Mantener dos UIs distintas
    (Streamlit + escritorio) duplica trabajo.

**C. Integrar el procesado en el dashboard actual** (página nueva
en `dashboard/paginas/`).
- Pros: una sola app, una sola URL.
- Contras:
  - Mezcla responsabilidades: el dashboard es para consulta
    (decisión #6, #27). Añadir acciones de pipeline acopla la
    visualización con la operación de datos.
  - Mayor riesgo: un error en el pipeline puede tirar el
    dashboard. Quien quiera consultar datos deja de poder hacerlo.
  - Permisos y backups distintos según contexto.

**D. CLI Python con `rich`/`textual`.**
- Pros: simple, sin servidor.
- Contras: el observador no es técnico (principio #2). La consola
  no es opción.

### 8.2 Recomendación

**Streamlit, en app separada (`app_pipeline/app.py`).**

Justificación:
- Mantiene la separación de responsabilidades: dashboard = consulta,
  app pipeline = operación.
- Reusa stack ya validado (decisión #5) y estilo visual ya pulido
  (`.streamlit/config.toml`).
- Coste bajo de implementación y mantenimiento.
- El observador puede tener dos pestañas abiertas (pipeline y
  dashboard) o cerrar la del pipeline cuando termine.

### 8.3 Decisiones derivadas (a registrar en `DECISIONES.md`)

- App de pipeline **separada** del dashboard.
  `dashboard/app.py` sigue siendo solo dashboard.
- Herramienta elegida: **Streamlit**, mismo stack que el dashboard.
- La app es el **único punto de control** para procesar Plaud
  desde Drive (queda obsoleto cualquier script ad hoc).

---

## 9. Riesgos y mitigaciones

| Riesgo                                                                     | Impacto | Mitigación                                                                                                                |
|----------------------------------------------------------------------------|---------|----------------------------------------------------------------------------------------------------------------------------|
| Confusión sobre cuándo usar app pipeline vs dashboard.                     | Medio   | Cabecera explícita en cada app. Botones cruzados ("Abrir dashboard" en la pipeline).                                      |
| Procesar accidentalmente en `prod`.                                        | Alto    | `src/config.py` ya bloquea `ENTORNO=prod`. La app muestra el entorno en cabecera.                                          |
| Supabase pausado o lento durante el procesado.                             | Medio   | Comprobación previa al procesar lote. Mensaje fijo de pausa (decisión #12). Botón "Reintentar".                            |
| Error parcial: visita insertada pero meteorología no.                      | Medio   | Hoy `escritura.py` no tiene transacción. Riesgo conocido. Mitigación a futuro: agrupar inserciones (fuera del alcance de esta fase). |
| El observador no entiende un error técnico de Supabase.                    | Alto    | Capa `_traducir_error` ya existente para conexión. Para errores por fila se muestra el mensaje literal del backend dentro de la tarjeta y se sugiere "Hablar con Claude.ai" mediante el botón. |
| Backup falla pero la inserción sí se hizo.                                 | Medio   | Marcar tarjeta verde con badge "Backup pendiente"; la app **no** repite la inserción. Documentado.                         |
| Lote grande de archivos: spinner sin progreso visible.                     | Bajo    | Usar `st.status` con líneas por archivo conforme se procesan.                                                              |
| Servidor Streamlit pipeline (8502) y dashboard (8501) chocan.              | Bajo    | Documentar puertos. La app pipeline arranca por defecto en 8502.                                                           |
| Variables `.env` cambiadas a mano y la app cachea config en memoria.       | Bajo    | `cargar_config()` lee `.env` cada vez. Sin caché global. Verificado.                                                       |
| Service account Drive pierde permisos sobre alguna carpeta.                | Medio   | Mensaje claro y accionable: "Comparte la carpeta `01_entrada` con la cuenta de servicio".                                  |

---

## 10. Plan de implementación por fases

### Fase A — Esqueleto y pantalla "lectura"

**Entregables**:
- Crear `app_pipeline/` con `__init__.py`, `app.py`, `lib/`.
- `app.py`: render de cabecera, indicador de entorno
  (`comprobar_entorno()`), botones grandes deshabilitados
  excepto "Abrir dashboard" y "Abrir Claude.ai".
- `lib/enlaces.py`: constantes de URLs y helpers.
- `lib/ui.py`: estilos base reusando `.streamlit/config.toml`.
- `lib/orquestador.py`: solo `comprobar_entorno()`. Detecta:
  - `.env` cargado y completo.
  - `ENTORNO=dev`.
  - Drive autenticable (`get_drive()`).
  - Supabase responde (`probar_conexion` adaptado).

**Tests** (`tests/test_app_pipeline_orquestador.py`):
- `test_comprobar_entorno_falta_env_devuelve_estado_rojo`
- `test_comprobar_entorno_drive_inaccesible_devuelve_amarillo`
- `test_comprobar_entorno_supabase_pausado_devuelve_rojo`
- Mocks de `get_drive`, `get_cliente`.

**Verificación manual**:
- `streamlit run app_pipeline/app.py --server.port 8502`.
- Comprobar que sin `.env` la cabecera es roja.

### Fase B — Procesamiento de lote y resultados

**Entregables**:
- `lib/estados.py`: dataclass `ResultadoArchivo` y constantes.
- `lib/orquestador.py`: `procesar_lote() -> list[ResultadoArchivo]`.
  - Llama a `src.pipeline.procesar_drive()`.
  - Mapea `{archivo, estado: "procesado"|"error", resumen|mensaje}`
    a `ResultadoArchivo` con clasificación de estado por
    sub-cadena del mensaje.
- `lib/ui.py`: `render_resultados`, `tarjeta_resultado`,
  `tabla_resumen`.
- `app.py`: cableado del botón "Procesar grabaciones de Plaud".
  Estado guardado en `st.session_state["resultados"]`.

**Tests** (`tests/test_app_pipeline_orquestador.py`):
- `test_procesar_lote_traduce_resumen_a_resultado_ok`
- `test_procesar_lote_clasifica_especie_no_encontrada_como_incompleto`
- `test_procesar_lote_clasifica_validacion_como_error`
- `test_procesar_lote_supabase_pausado_devuelve_error_global`
- Todos con `monkeypatch` sobre `src.pipeline.procesar_drive`.

**Verificación manual**:
- Subir un `.txt` de prueba a `01_entrada` (manual o copia desde
  `tests/ejemplos_plaud/`).
- Comprobar que la tarjeta refleja correctamente el caso.

### Fase C — Pulido y documentación

**Entregables**:
- Botón "Reintentar último procesado" si la app detecta archivos
  aún en `01_entrada`.
- Mensaje vacío claro si `01_entrada` no tiene archivos.
- Texto de ayuda en pie de página: "Si algo va mal, contacta con
  Javi o pregunta a Claude.ai".
- `docs/USO_APP_PIPELINE.md`: guía corta para el observador
  (cómo arrancar, qué significa cada color, qué hacer cuando un
  catálogo no se encuentra).
- Sección en `README.md` con el comando de arranque y el puerto
  recomendado (8502).

**Tests**:
- `tests/test_app_pipeline_render.py`: smoke tests con
  `streamlit.testing.v1.AppTest`. Mínimo:
  `test_app_arranca_sin_excepciones_con_env_completo` (mock).

**Verificación manual**:
- Arrancar app + dashboard a la vez.
- Procesar un lote real con 1-2 `.txt` sintéticos en
  Supabase dev. Confirmar movimiento de archivos en Drive.

### Fase D — (Opcional) Granularidad de etapas

Solo si la fase B muestra que las tarjetas se quedan cortas:
- Modificar (en una sesión nueva, con cuidado) `src/pipeline.py`
  para que `procesar_txt_local` devuelva un dict con
  `etapas: {parser: ok, validacion: ok, catalogos: ok,
  insercion: ok, backup: ok}`.
- Adaptar `lib/orquestador.py` y tarjetas.
- Esta fase **no se acomete** en la implementación inicial.

### 10.1 Reglas de implementación

- Cada fase termina con commit propio (`feat(app_pipeline): ...`).
- No tocar `src/pipeline.py`, `src/insercion/`, `src/parser/`,
  `src/drive/` ni `src/backup/` salvo en la fase D opcional.
- No tocar SQL ni `.env`.
- Cada PR/commit pasa: `pytest`, `git diff --check`, revisión de
  secretos.
- La app pipeline no inserta IDs manuales ni llama directamente a
  Supabase: todo pasa por las funciones existentes de
  `src.pipeline`.

---

## 11. Resumen visual

```
┌──────────────────────────────────────────────────────────────┐
│  BirdLog — Pipeline Plaud           [🟢 dev · Drive · Supabase] │
│  Carpeta entrada: 01_entrada · Último procesado: 03/05 19:42 │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  [▶ Procesar grabaciones de Plaud]                            │
│                                                              │
│  [📊 Abrir dashboard]    [💬 Abrir Claude.ai]                 │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│  Resultados                                                  │
│                                                              │
│  ┌──────┬─────────────────┬───────────┬──────────────┬────┐ │
│  │ 🟢   │ visita_lindus..│ Backup    │ procesados   │ OK │ │
│  │ 🟡   │ caja_AREATZEA1.│ Catálogos │ errores      │ +  │ │
│  │ 🔴   │ visita_cebo.tx │ Validación│ errores      │ +  │ │
│  └──────┴─────────────────┴───────────┴──────────────┴────┘ │
│                                                              │
│  (tarjetas detalladas debajo)                                │
└──────────────────────────────────────────────────────────────┘
```
