# Bitácora del proyecto

> Este archivo es la memoria viva del proyecto. Codex y Claude Code lo
> leen al iniciar cada sesión y lo actualizan cuando el usuario dice
> "rutina de cierre".

---

## Estado actual

- **Fase activa**: Fase 8 — App local de pipeline (código del pipeline
  revisado y robustecido; listo para pruebas reales con Plaud)
- **Última sesión**: 2026-06-11
- **Próxima tarea**: (a) Sustituir clave anon del `.env` por la clave
  `service_role` del proyecto BirdLog (dashboard → Settings → API);
  (b) continuar pruebas reales con Nidos rapaces, Cebos avispones,
  Cajas nido y Lindus vía Plaud; (c) recoger del cliente lo pendiente:
  observador de las 98 visitas, `id_lugar` de V0001, UTM/municipio de
  Lindus y Trona, vocabularios de las tablas nuevas y quinto ecosistema.

---

## Tareas en curso

- [ ] (sin tareas en curso)

---

## Tareas pendientes

### Fase 2: Plantilla Plaud
- [ ] Continuar pruebas reales con Nidos rapaces, Cebos avispones,
      Cajas nido y Lindus.
- [ ] Confirmar con el observador el quinto ecosistema de cajas_nido

### Fase 3: Parser
- [ ] Recoger 5-6 .txt de ejemplo de tipos distintos de visita

### Esquema v3 y migración del histórico
- [x] Recoger respuestas del cliente al informe de revisión
      (`docs/Informe_revision.docx`) y aplicarlas al Excel:
      11 valores de meteo + bloque V0043, especies aceptadas,
      UTM ETRS89/30N (decisión #44).
- [x] Resolver por deducción lo que no requería al cliente (decisión
      #45): temperaturas M1002/M1039, `id_lugar` de 97 visitas,
      `grupo` y `nombre_comun` de las 135 especies.
- [ ] Recoger las respuestas que **solo** puede dar el cliente:
      observador de las 98 visitas, `id_lugar` de V0001, UTM/municipio
      de Lindus y Trona, vocabularios de las tablas nuevas y quinto
      ecosistema. (Opcional: que revise `grupo`/`nombre_comun`.)
- [x] Implementar scripts de importación del histórico 2025
      (`scripts/importar_historico.py` + `scripts/insertar_historico.py`).
- [x] Aplicar `sql/003_esquema_v3.sql` en Supabase BirdLog (DROP+CREATE)
      y reimportar catálogos + histórico (2026-06-10).
- [ ] Diseñar plantillas Plaud para los 4 tipos nuevos
      (fototrampeo, cuaderno_campo, estudio_campo, castor_rastros)
      y su soporte en parser/inserción/dashboard (fase futura).

### Fase 8: App local de pipeline
- [x] Diseño de la app local de pipeline completado (2026-05-03).
      Documento: `docs/PLAN_APP_PIPELINE.md`. Decisiones #31, #32 y #33.
- [x] Implementar Fase A del plan: esqueleto `app_pipeline/` con
      cabecera, `comprobar_entorno()` y botones secundarios (2026-05-03).
- [x] Implementar Fase B del plan: procesado de lote y tarjetas
      verde/amarillo/rojo (2026-05-03).
- [x] Implementar Fase C del plan: pulido, `docs/USO_APP_PIPELINE.md`
      (2026-05-03). README pendiente de sección de arranque.
- [ ] Añadir sección de arranque de `app_pipeline` en `README.md`.
- [ ] Prueba controlada con archivos Plaud reales o sintéticos subidos
      a `01_entrada` de Drive.
- [ ] Limpiar visitas de demo de dev (visitas del 2026-05-03 con
      observaciones "demo del pipeline") si se llegaron a insertar

### Pendiente general
- [ ] Sustituir clave anon en `.env` por `service_role` del proyecto
      BirdLog (Supabase dashboard → Settings → API → service_role).
- [ ] Rellenar `utm_x`/`utm_y` de Lindus y Trona cuando el cliente
      entregue las coordenadas (ETRS89 huso 30N).

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

### Sesión 2026-06-11: Revisión del pipeline — robustez y mensajes claros (completado)
- [x] **Revisión completa del código del pipeline**: parser, inserción,
      backup, orquestador de Drive y app Streamlit. Decisión #47.
- [x] **Backup actualizado al esquema v3**: `TABLAS_BACKUP` exporta las
      15 tablas (antes omitía en silencio `fototrampeo`, `cuaderno_campo`,
      `estudio_campo` y `castor_rastros`). Implementada la **retención de
      30 backups** que estaba especificada (AGENTS.md §6) sin programar.
- [x] **Pausa de Supabase detectada donde ocurre**: la pausa solo aflora
      en la primera consulta (no al crear el cliente); `comprobar_entorno`
      y `procesar_lote` muestran ahora el mensaje de reactivación en vez
      del genérico. `es_error_de_pausa` público en `src/conexion.py`.
- [x] **Fallo al mover en Drive ya no aborta el lote**: si la inserción
      fue bien pero el movimiento falla, resultado OK con aviso visible
      de que el `.txt` sigue en `01_entrada` y hay que moverlo a mano
      para no duplicar (`txt_movido_a="entrada"` en tarjeta, tabla y log).
- [x] **Sin tracebacks en la app**: `procesar_lote` captura cualquier
      excepción y devuelve mensaje claro + detalle técnico.
- [x] **Progreso en vivo**: `procesar_drive(al_procesar=...)` acepta
      callback; la app muestra cada archivo con icono/estado según se
      procesa dentro de `st.status`.
- [x] **Mensajes mejorados**: columna `id_visita` real en la tabla
      resumen (antes siempre "-"); INCOMPLETO → "Falta un dato de
      catálogo"; resumen global con lenguaje claro; cierre Lindus sin
      visita abierta indica procesar antes `INICIO_VISITA_LINDUS`.
- [x] **Tests**: 135 pasan (126 previos + 9 nuevos, incluido
      `tests/test_backup_exportar.py` para un módulo de prioridad alta
      que no tenía cobertura). Smoke test HTTP 200 de la app.
- [x] **Commits**: `8cf605e` (backup v3 + retención), `c3b8f69`
      (robustez pipeline), `7e8af66` (UX app pipeline), `763f458`
      (decisión #47), `c2167dd` (cierre bitácora 2026-06-10 pendiente),
      `d7d2bcf` (rutas de lanzadores a `/home/hermes`).

### Sesión 2026-06-10: Importación histórico 2025 + verificación dashboard (completado)
- [x] **Dashboard verificado con datos reales** (Supabase BirdLog):
      - Inicio: 97 visitas, 134 especies, 10.870 observaciones Lindus,
        "Sin datos" para tablas vacías (correcto), última visita
        11/11/2025, 2 lugares activos, gráfico de actividad jul-nov 2025.
      - Lindus: 10.870 obs, 151.325 individuos, gráfico temporal y
        distribución MIGRADOR/NORTE/LOCAL correctos.
      - Mapa general: Lindus y Trona listados con utm_x/utm_y = None
        (sin mapa dibujado hasta que el cliente aporte UTM — correcto).
      - Cajas nido / Nidos rapaces / Cebos avispones / Mamíferos:
        "Sin datos todavía" (tablas vacías — correcto).
      - Edición / Catálogos: 135 especies cargadas con nombre científico,
        nombre común y grupo. Sin errores en ninguna página.
- [x] **Esquema v3 aplicado** en proyecto Supabase BirdLog
      (`mbphfgmjryyxzjgcwqxo`): 14 tablas con `utm_x`/`utm_y` nullable
      (coords de Lindus/Trona pendientes del cliente — decisión #45).
- [x] **Importación del histórico 2025**: 135 especies, 2 observadores
      (Gabi/Ander), 2 lugares (Lindus LUG01 / Trona LUG02), 97 visitas
      (V0001 omitida), 1.048 meteo, 10.870 lindus.
- [x] **`.env` apuntado** al nuevo proyecto BirdLog
      (`mbphfgmjryyxzjgcwqxo.supabase.co`). Clave anon temporal — sustituir
      por `service_role` (Supabase dashboard → Settings → API).
- [x] **Scripts creados**: `scripts/importar_historico.py` (genera SQL)
      y `scripts/insertar_historico.py` (inserta vía supabase-py, lotes 200).
- [x] **`sql/003_esquema_v3.sql`** actualizado: `utm_x`/`utm_y` nullable.
- [x] 126 tests pasan. Decisión #46 añadida a `docs/DECISIONES.md`.

### Sesión 2026-06-10: Respuestas del cliente aplicadas al Excel (completado)
- [x] **Lectura de `docs/Informe_revision.docx`**: extraídas las
      respuestas que Gabi resaltó en amarillo a las cuestiones del
      informe de revisión.
- [x] **Correcciones aplicadas a `BirdLog_tablas_cliente_v03.xlsx`**
      (copia de seguridad previa `.bak_20260610_163659.xlsx`):
      - Meteo 3.3: 11 valores corregidos (presiones a hPa con decimal,
        humedades reales, `temperatura` M0588 sin la nota "+V593").
      - Meteo 3.4: bloque V0043 (M0464–M0478) reordenado, presión
        movida de `humedad_relativa` a `presion_atm`; humedad vacía.
      - Especies 3.2: las 21 entradas `revisar` SI→NO (aceptadas todas).
      - UTM 3.5: columnas `datum` (ETRS89) y `huso` (30N, Navarra)
        añadidas a las 6 hojas con coordenadas.
      - TOTAL y 3 columnas Lindus: confirmados, sin cambio (fórmula
        viva conservada).
- [x] **Valores deducibles resueltos (decisión #45)**, sin inventar:
      - Temperaturas M1002→6.8 y M1039→9.5 (mismo patrón de decimal).
      - `visitas.id_lugar`: 97 de 98 derivadas de `meteo` (59 Lindus /
        38 Trona); V0001 queda vacía (sin meteo) para el cliente.
      - `especies.grupo` (135) por taxonomía y `nombre_comun` (135)
        por nomenclatura estándar.
- [x] **Decisión #44 y #45** añadidas en `docs/DECISIONES.md`.
- [x] **Docs actualizados**: `docs/REVISION_EXCEL_CLIENTE_V03.md`
      (sección 0 de estado resuelto) y `docs/Revisar con GABI.md`
      (respuestas rellenadas y pendientes marcados).
- [x] Verificado en el Excel que los cambios persistieron y que la
      fórmula `total` (`=N(F2)+N(G2)+N(H2)`) sigue intacta.

### Sesión 2026-06-10: Revisión del Excel del cliente y esquema v3 (completado)
- [x] **Revisión de `docs/BirdLog_tablas_cliente_v03.xlsx`**: 14 hojas,
      histórico Lindus 2025 (10.903 observaciones, 1.048 meteo,
      98 visitas) y 4 tipos de registro nuevos.
- [x] **Decisión #40**: se mantiene la estructura v2 (observador,
      `tipo_visita`, `visitas.id_lugar`, lugares normalizados, IDs
      enteros) frente a la estructura del Excel.
- [x] **Decisión #41 / esquema v3**: `sql/003_esquema_v3.sql` con
      `fototrampeo`, `cuaderno_campo`, `estudio_campo` (solo
      detecciones) y `castor_rastros`; campos nuevos en
      `nidos_rapaces` y `cebos_avispones`; CHECKs ampliados.
      **No aplicado aún en Supabase dev** (dev sigue en v2).
- [x] **Decisión #42**: `meteorologia` mantiene los 9 campos Plaud y
      añade conteos de personas + campos históricos opcionales.
- [x] **Decisión #43**: reglas de limpieza del histórico (sin
      autocorregir valores medidos; rumbos de viento normalizados;
      fila Lindus mixta L002724 se parte en dos).
- [x] **Documentación**: `docs/modelo_datos.md` a 14 tablas,
      `AGENTS.md`/`CLAUDE.md` actualizados,
      `docs/REVISION_EXCEL_CLIENTE_V03.md` creado con la lista de
      correcciones para el cliente.
- [x] **Seguridad**: `docs/*.xlsx` añadido a `.gitignore` — el Excel
      con observaciones reales queda fuera de git (decisión #9).
- [x] **Cierre Lindus (decisión #39)** commiteado: las observaciones
      del inicio se conservan y se combinan con las del cierre.
- [x] Comprobaciones: `pytest` 126/126, diffs revisados sin secretos
      ni datos reales.
- [x] Commits: `ac8b169 fix(pipeline): conservar observaciones al
      cerrar visita Lindus` y `a9c8f66 feat(sql): esquema v3 tras
      revisión del Excel del cliente`.

### Sesión 2026-05-04: Reprocesado de observaciones Lindus (completado)
- [x] **Recuperación de errores Lindus**: `OBSERVACIONES_LINDUS` puede
      añadirse a una única visita Lindus existente para la fecha, aunque
      la visita ya tenga `hora_fin`.
- [x] **Errores claros**: si no existe visita Lindus para la fecha, el
      mensaje pide procesar primero `INICIO_VISITA_LINDUS`; si hay varias,
      no se elige automáticamente.
- [x] **Sin deduplicación biológica**: se permite reprocesar contenido
      idéntico porque dos observaciones iguales pueden ser reales; queda
      pendiente una deduplicación futura por archivo/hash.
- [x] **Documentación y decisión**: `docs/USO_APP_PIPELINE.md` actualizado
      y decisión #38 añadida.

### Sesión 2026-05-04: Orden lógico de lotes Lindus en Drive (completado)
- [x] **Orden de procesado Lindus**: cuando llegan varios `.txt` Lindus
      juntos, el pipeline los ordena por fecha y tipo lógico:
      inicio, observaciones y cierre.
- [x] **Observaciones múltiples**: varias `OBSERVACIONES_LINDUS` quedan
      entre inicio y cierre, con orden estable por metadatos de Drive o
      nombre.
- [x] **Cierre sin inicio**: `FIN_VISITA_LINDUS` no crea visita nueva; si
      no hay visita abierta, falla con mensaje claro y el archivo va a
      errores.
- [x] **Documentación y decisión**: `docs/USO_APP_PIPELINE.md` actualizado
      y decisión #37 añadida.

### Sesión 2026-05-04: Diagnóstico detallado de errores del pipeline (completado)
- [x] **Errores de validación detallados**: el pipeline acumula campos
      obligatorios ausentes, valores cerrados inválidos y meteorología
      incompleta antes de fallar.
- [x] **Errores de catálogo/FK detallados**: lugares, especies y
      observadores no resueltos indican catálogo, campo Plaud, valor
      recibido, motivo y sugerencia.
- [x] **Advertencias de estructura**: texto antes de `TIPO_REGISTRO` se
      ignora si no bloquea el parseo y queda registrado como advertencia.
- [x] **App pipeline**: registro, resumen y detalle desplegable muestran
      diagnósticos múltiples sin traceback técnico visible.
- [x] **Caso de referencia**: prueba local de Nidos rapaces cubre
      `HORA_FIN` ausente, `HORA_METEO` ausente, `OESTE` como viento
      inválido y título narrativo inicial.

### Sesión 2026-05-04: Guía de campo Plaud y prueba Mamíferos puentes (completado)
- [x] **Guía de campo Plaud**: añadida documentación para el observador
      en `docs/GUIA_CAMPO_PLAUD.docx` y `docs/GUIA_CAMPO_PLAUD.html`.
- [x] **Formatos disponibles**: la guía queda disponible en DOCX y HTML.
- [x] **Pruebas reales**: Mamíferos puentes funciona correctamente de
      momento con pruebas reales.
- [x] **Próxima tarea**: continuar pruebas reales con Nidos rapaces,
      Cebos avispones, Cajas nido y Lindus.

### Sesión 2026-05-03: Robustez para fechas y lugares Plaud reales (completado)
- [x] **Fechas tolerantes**: `normalizar_registro()` acepta `YYYY-MM-DD` y
      `DD/MM/YYYY`; internamente deja `YYYY-MM-DD`.
- [x] **Error claro de fecha**: formatos fuera de esos dos se rechazan con
      mensaje que indica los formatos permitidos.
- [x] **Lugares tolerantes a mayúsculas/minúsculas**: `resolver_lugar()`
      prueba primero coincidencia exacta y luego case-insensitive, sin
      resolver si hay varias coincidencias posibles.
- [x] **Payload final limpio**: test de inserción con cliente falso confirma
      que una visita de mamíferos con `03/05/2026` y `puente de aranzadi`
      acaba con fecha `2026-05-03` e `id_lugar` resuelto antes de escribir.
- [x] **Documentación y decisión**: `docs/formato_plaud.md` y decisión #36
      actualizadas.

### Sesión 2026-05-03: Errores de procesamiento sin crash de interfaz (completado)
- [x] **Crash corregido**: `render_resumen_global()` importaba `ESTADO_OK`
      e `ESTADO_INCOMPLETO`, pero usaba `ESTADO_ERROR` sin importarlo.
- [x] **Estados cubiertos**: resumen global probado para OK, ERROR,
      INCOMPLETO y PENDIENTE.
- [x] **Log de errores**: el registro de procesamiento muestra el mensaje
      real del error y el movimiento a `errores`, sin traceback de Streamlit.
- [x] **Diagnóstico Mamíferos puentes**: el `.txt` real falla primero por
      `FECHA: 03/05/2026`; el parser/validador esperan `YYYY-MM-DD`.
      Además, `lugar_puente` en minúsculas no resolvería contra
      `Puente de Aranzadi` si el catálogo está capitalizado así.

### Sesión 2026-05-03: Alineación vertical del panel principal (completado)
- [x] **Panel derecho**: añadido un espaciador superior mínimo para que
      resumen, registro y resultados respiren mejor y queden alineados con
      el contenido del panel izquierdo.

### Sesión 2026-05-03: Distribución operativa de app pipeline (completado)
- [x] **Layout en dos columnas**: panel izquierdo compacto para identidad,
      estado del sistema y acciones; panel derecho ancho para resumen,
      registro y resultados.
- [x] **Registro de procesamiento**: bloque de log ampliado a altura fija
      grande, con scroll interno y estilo de consola legible.
- [x] **Resumen por archivo**: tabla ajustada a columnas operativas
      (`archivo`, `estado`, `id_visita`, `backup`, `movimiento_drive`,
      `mensaje`) y detalles largos en desplegables.
- [x] **Documentación**: `docs/USO_APP_PIPELINE.md` actualizada con la nueva
      distribución visual.

### Sesión 2026-05-03: Autoarranque del dashboard desde app pipeline (completado)
- [x] **Botón "Abrir dashboard"**: queda siempre activo en la app pipeline.
      Si `http://127.0.0.1:8999` ya responde, abre el navegador.
      Si no responde, lanza `scripts/abrir_dashboard.sh`, espera el arranque
      y abre el navegador.
- [x] **Sin duplicados**: antes de arrancar se comprueba si el dashboard
      responde por HTTP o si el puerto 8999 ya está ocupado.
- [x] **Apertura de navegador única**: cuando la app pipeline lanza
      `scripts/abrir_dashboard.sh`, el script no abre otra pestaña extra;
      la apertura queda controlada por la app pipeline.
- [x] **Documentación**: `docs/USO_APP_PIPELINE.md` actualizada con el nuevo
      comportamiento y fallback al icono **BirdLog Dashboard**.

### Sesión 2026-05-03: UX de app pipeline y lanzadores (completado)
- [x] **Dashboard desde app pipeline**: si el dashboard está activo, el
      botón lo abre; si no, la app indica usar el icono **BirdLog Dashboard**
      y muestra el comando manual en un desplegable.
- [x] **Registro de procesamiento**: añadida sección amplia con mensajes
      del pipeline, estado por archivo, inserción, backup, movimiento de
      carpeta, tabla resumen y detalles desplegables.
- [x] **Navegador automático**: `scripts/abrir_app_pipeline.sh` abre
      `http://localhost:8502` con `xdg-open` tras arrancar Streamlit y evita
      copias repetidas mediante lock temporal.
- [x] **Lanzador de dashboard**: añadidos `scripts/abrir_dashboard.sh` y
      `scripts/BirdLog_Dashboard.desktop` para abrir el dashboard en `8999`.
- [x] **Documentación**: `docs/USO_APP_PIPELINE.md` y decisión #35
      actualizadas.

### Sesión 2026-05-03: Configuración por perfiles para app pipeline (completado)
- [x] **Diagnóstico aplicado**: `DRIVE_FOTOS_ID` ya no bloquea la app
      pipeline Plaud. La causa era la validación global de `cargar_config()`.
- [x] **Perfiles de configuración**: añadidos perfiles dashboard, Drive,
      pipeline Plaud y fotos en `src/config.py`. `cargar_config()` queda
      como compatibilidad histórica.
- [x] **Pipeline Plaud**: `app_pipeline/lib/orquestador.py`,
      `src/pipeline.py` y `src/drive/cliente.py` usan perfiles mínimos.
- [x] **Fotos**: `src/fotos/sincronizar.py` valida `DRIVE_FOTOS_ID` solo
      en el flujo de sincronización de fotos.
- [x] **Documentación**: `docs/USO_APP_PIPELINE.md`,
      `docs/PLAN_APP_PIPELINE.md` y decisión #34 actualizados.

### Sesión 2026-05-03: Mejoras de branding y UX en app pipeline (completado)
- [x] **Branding unificado**: `page_icon` del dashboard cambiado de 🌿 a 🦅
      (`dashboard/app.py`); emoji 🦅 añadido al título del sidebar
      (`dashboard/lib/ui.py`). App pipeline ya usaba 🦅.
- [x] **Botón "Abrir dashboard"**: ahora comprueba con socket si el dashboard
      está corriendo en puerto 8999. Si sí → botón activo. Si no → botón
      deshabilitado + caption con el comando de arranque.
- [x] **Mensajes de Drive/config simplificados**: se distinguen tres casos
      (config faltante, Drive inaccesible, Supabase inaccesible). Mensaje
      principal corto y legible; detalle técnico en expander desplegable.
- [x] Comprobaciones: `py_compile` OK, imports OK, HTTP 200 en 8503 y 8999,
      `pytest` 80/80, SQL/.env sin cambios, `git diff --check` limpio.

### Sesión 2026-05-03: Lanzador de escritorio para app pipeline (completado)
- [x] **Script de arranque**: `scripts/abrir_app_pipeline.sh` — activa
      `.venv`, comprueba que Streamlit existe, arranca en puerto 8502 con
      mensajes de error claros si falta el entorno.
- [x] **Archivo `.desktop`**: `scripts/BirdLog_Pipeline.desktop` —
      lanzador para Ubuntu/GNOME que abre `gnome-terminal` con el script.
- [x] **Icono en Escritorio**: copiado a `~/Escritorio/BirdLog_Pipeline.desktop`
      y marcado como de confianza con `gio set ... metadata::trusted true`.
- [x] **Documentación actualizada**: `docs/USO_APP_PIPELINE.md` — nueva
      sección «Arrancar desde icono de escritorio» con instrucciones para
      primer uso, alternativa manual y cómo cerrar la app.
- [x] Comprobaciones: `bash -n` OK, permisos OK, rutas correctas,
      `pytest` 80/80, sin cambios en SQL ni `.env`, `git diff --check`
      limpio, sin secretos en diff.

### Sesión 2026-05-03: Implementación de app pipeline (completado)
- [x] **App pipeline implementada**: `app_pipeline/app.py` (Streamlit,
      puerto 8502), `app_pipeline/lib/estados.py` (dataclasses
      `ResultadoArchivo` y `EstadoEntorno`), `app_pipeline/lib/enlaces.py`,
      `app_pipeline/lib/orquestador.py` (funciones `comprobar_entorno` y
      `procesar_lote` wrapeando `src.pipeline.procesar_drive`),
      `app_pipeline/lib/ui.py` (componentes visuales: cabecera, tarjetas
      verde/amarillo/rojo, tabla resumen).
- [x] **Funcionalidades**: botón "Procesar grabaciones de Plaud" con
      spinner `st.status`, caché de 30 s del estado de entorno, tarjetas
      expandibles por archivo con estado de color, indicaciones de
      resolución de catálogos faltantes, advertencia si ENTORNO=prod.
- [x] **Tests**: `tests/test_app_pipeline_orquestador.py` con 19 tests
      (clasificación de errores, traducción de resultados, procesar_lote
      con monkeypatch, comprobar_entorno con monkeypatch).
- [x] **Documentación**: `docs/USO_APP_PIPELINE.md` (guía para el
      observador: arranque, colores, errores frecuentes, cómo reprocesar).
- [x] Comprobaciones: `py_compile` OK (7 archivos nuevos), `pytest` 80/80,
      HTTP 200 en `localhost:8502`, `git diff --check` limpio,
      sin cambios en SQL ni `.env`, sin secretos en diff.

### Sesión 2026-05-03: Diseño de app local de pipeline (completado)
- [x] **Diagnóstico del pipeline actual**: revisión de `src/pipeline.py`,
      `src/drive/`, `src/parser/`, `src/insercion/`, `src/backup/` y
      `src/config.py`. Inventario de funciones públicas, carpetas Drive
      (`01_entrada`, `02_procesados`, `03_errores`, `Backups`, `Fotos`)
      y variables `.env` necesarias.
- [x] **Diseño de la app**: arquitectura propuesta en
      `app_pipeline/` (separada del dashboard); pantalla única con
      cabecera, tres botones grandes ("Procesar grabaciones de Plaud",
      "Abrir dashboard", "Abrir Claude.ai") y bloque de resultados con
      tabla y tarjetas verde/amarillo/rojo/gris.
- [x] **Decisión de herramienta**: Streamlit en app separada, mismo
      stack que el dashboard. Justificación y alternativas descartadas
      en `docs/PLAN_APP_PIPELINE.md` §8.
- [x] **Plan por fases**: Fase A (esqueleto + `comprobar_entorno`),
      Fase B (procesado de lote y tarjetas), Fase C (pulido y
      documentación de uso), Fase D opcional (granularidad de etapas).
- [x] **Documentación creada**: `docs/PLAN_APP_PIPELINE.md`.
- [x] **Decisiones añadidas**: #31 (app pipeline separada del dashboard),
      #32 (Streamlit como herramienta), #33 (la app pipeline es el
      único punto de control para procesar Plaud desde Drive).
- [x] Comprobaciones: `git diff --check` limpio, sin cambios en SQL ni
      `.env`, sin secretos en diff.

### Sesión 2026-05-03: Limpieza de artefactos de demo (completado)
- [x] **Archivos eliminados**: `demo.py` (315 líneas, script ad hoc con
      dry-run y confirmación `INSERTAR`) y `demo/` (7 archivos `.txt`:
      `01_inicio_lindus.txt` … `07_mamiferos_puente.txt`).
- [x] **Correcciones reales conservadas**:
      - `src/insercion/catalogos.py`: `resolver_especie` insensible a
        mayúsculas (prueba exacto y luego `.capitalize()`).
      - `src/insercion/escritura.py`: `observaciones_puente` se combina
        con `observaciones_visita` usando ` | ` antes de insertar en
        `visitas.observaciones` (ya no se descarta silenciosamente).
- [x] **Tests conservados** (61 pasan):
      - `test_resolver_especie_tolera_minusculas_si_bd_tiene_mayuscula_inicial`
      - `test_resolver_especie_tolera_minusculas_en_nombre_cientifico`
      - `test_insertar_mamiferos_puente_no_descarta_observaciones_puente`
- [x] Comprobaciones: `pytest` (61 OK), `git diff --check` limpio, sin
      cambios en SQL ni `.env`, sin secretos en diff.
- [x] Decisión técnica añadida: #30 — pipeline sin `demo.py`.
- [x] Commit: `chore(pipeline): eliminar archivos de demo`.

### Sesión 2026-05-03: Diagnóstico y preparación de la demo del pipeline (completado)
- [x] **Diagnóstico completo del pipeline**: revisión de `src/`, `tests/`,
      `docs/formato_plaud.md` y ejemplos Plaud. Pipeline de extremo a extremo
      implementado y funcional.
- [x] **Fase A — Verificación de catálogos en Supabase dev**: todos los
      observadores (`Gabi`, `Ander`) y lugares necesarios existen.
      `BAR01`, `Nido Rapaz Prueba 1` y `Puente Prueba 1` no existen; se
      sustituyeron en los archivos de demo por `CAJA_NIDO_TEST_01 [SINTETICO_TEST]`,
      `AREATZEA1` y `Puente de Aranzadi`.
- [x] **Fase B — Bug `observaciones_puente`**: el campo se parseaba
      correctamente pero `_fila_visita` en `escritura.py` lo descartaba
      silenciosamente. Corregido: se combina con `observaciones_visita`
      usando ` | ` como separador.
- [x] **Fase B — Bug case-sensitivity de especies**: la BD guarda nombres
      con primera letra en mayúscula (`"Milano negro"`) pero Plaud transcribe
      en minúsculas (`"milano negro"`). `resolver_especie` fallaba
      silenciosamente para todos los tipos con especies (Lindus, cajas nido,
      nidos rapaces, mamíferos puentes). Corregido: se prueba exacto y luego
      `.capitalize()`.
- [x] **Fase C — Script `demo.py`**: script en raíz con `--dry-run`, verificación
      de catálogos en modo lectura, resumen previo y confirmación explícita
      `INSERTAR` antes de tocar la BD.
- [x] **Fase C — Archivos `demo/`**: 7 archivos `.txt` con lugares reales
      de Supabase dev, fecha 2026-05-03 y observaciones "demo del pipeline".
      Todos los dry-runs pasan.
- [x] **Tests**: +3 nuevos tests (capitalización de especies ×2 y preservación
      de `observaciones_puente`). Total: 61 tests pasando.
- [x] Comprobaciones finales: `pytest` (61 OK), `git diff --check` limpio,
      sin cambios en SQL ni `.env`, sin secretos en diff.
- [x] Commit: `56e64f4 feat(pipeline): preparar demo del pipeline para el observador`.

### Sesión 2026-05-03: Revisión visual/funcional del dashboard (completado)
- [x] **Revisión completa de las 9 páginas**: Inicio, Visitas, Mapa general,
      Lindus, Cajas nido, Nidos rapaces, Cebos avispones, Mamíferos puentes,
      Edición / Catálogos.
- [x] **Patrón maestro-detalle aplicado** en las 4 páginas de consulta que
      aún usaban `st.selectbox` + JSON crudo: Cajas nido, Nidos rapaces,
      Cebos avispones y Mamíferos puentes. Ahora todas las páginas de consulta
      biológica tienen tabla seleccionable por clic de fila (API nativa
      `on_select="rerun"` + `selection_mode="single-row"`) y panel de detalle
      con ficha legible: etiquetas humanas, sin NULL/None/NaN visibles, sin
      `[SINTETICO_TEST]`, sección "Meteorología de la visita" y botón
      "Ver visita" que navega a la página Visitas.
- [x] **Bug precarga en Edición/Catálogos corregido**: al editar un registro
      el formulario aparecía vacío. Causa raíz: los widgets del formulario
      usaban `key = f"{tabla}_{campo}"` sin incluir el ID del registro, por
      lo que Streamlit mantenía el valor anterior de `session_state` al
      cambiar de registro. Solución: añadir `prefijo_key` a `_formulario` y
      `_widget_campo` con esquema `edit_{tabla}_{id_registro}_{campo}`. Alta
      y edición ya no comparten keys.
- [x] **Datos sintéticos**: se mantienen en Supabase dev sin modificar.
- [x] Comprobaciones finales: `py_compile` (20 archivos), imports (10 páginas),
      `pytest` (58 tests OK), `streamlit run`, HTTP 200, sin cambios en SQL
      ni `.env`, `git diff --check` limpio, sin secretos en diff.
- [x] Commits creados:
      `ec46307 style(dashboard): mejorar detalle de cajas nido`,
      `a4990ce style(dashboard): mejorar detalle de nidos rapaces`,
      `dff201e style(dashboard): mejorar detalle de cebos avispones`,
      `1ee49a6 style(dashboard): mejorar detalle de mamiferos puentes`,
      `08035ac fix(dashboard): precargar valores al editar registros`.

### Sesión 2026-05-02: Página Visitas y navegación relacional (completado)
- [x] **Página Visitas** (`dashboard/paginas/02_visitas.py`) creada con
      listado, filtros, panel de detalle, meteorología asociada y resumen de
      registros por tipo. Caso LINDUS implementado completamente; resto de
      tipos de visita preparados como pendiente.
- [x] **Navegación actualizada a 9 páginas**: Inicio, Visitas, Mapa general,
      Lindus, Cajas nido, Nidos rapaces, Cebos avispones, Mamíferos puentes,
      Edición / Catálogos.
- [x] **Patrón relacional Visitas ↔ Lindus**: desde el detalle de una
      observación Lindus se puede navegar a la visita correspondiente (botón
      "Ver visita"); la sección de meteorología en Lindus pasa a llamarse
      "Meteorología de la visita"; el panel de detalle Lindus incluye bloque
      Visita.
- [x] Comprobaciones reportadas: `py_compile` OK, imports OK, 58 tests
      pasando, Streamlit OK, HTTP 200, sin cambios en SQL, `.env` ni secretos.
- [x] Commit creado:
      `c8dcc9a feat(dashboard): añadir pagina visitas y navegacion con Lindus`.

### Sesión 2026-05-02: Corrección de títulos y pulido Lindus (completado)
- [x] **Bug títulos**: diagnóstico técnico del bug en que "Inicio" aparecía
      en todas las páginas. Causa raíz: `st.radio` sin `key` reiniciaba al
      índice 0 en cada rerun interactivo. Solución: sustituir por botones
      individuales con `st.session_state["pagina_activa"]` y `st.rerun()` en
      `dashboard/lib/ui.py`; centralizar `encabezado_pagina(pagina)` en
      `dashboard/app.py`; eliminar cabecera propia de las 8 páginas.
- [x] **Detalle Lindus**: reemplazar el volcado JSON crudo (`st.write({...})`)
      por ficha estructurada con layout maestro-detalle —tabla a la izquierda
      (3/5), tarjeta legible a la derecha (2/5)—, sin tipos Python internos
      (`Timestamp(...)`, `np.int64(...)`). Meteorología asociada renderizada
      con columnas renombradas.
- [x] **Selección desde tabla Lindus**: eliminar `st.selectbox("Ver detalle")`
      redundante; tabla con `on_select="rerun"` + `selection_mode="single-row"`
      (API nativa de Streamlit ≥ 1.35); formato DD/MM/YYYY en fechas, HH:MM en
      horas, sin marcadores `[SINTETICO_TEST]`, altura 420 px, índice oculto.
- [x] Tests actualizados en `tests/test_dashboard_titulos.py`: 4 tests que
      verifican que las páginas no pintan cabecera propia, que `app.py` la
      centraliza, y que la navegación usa botones en vez de radio.
- [x] Comprobaciones realizadas: `pytest` (58 tests OK), `py_compile` de todas
      las páginas, arranque del dashboard, revisión de secretos en diff.
- [x] Commits creados:
      `c29a98e fix(dashboard): corregir titulo activo por pagina`,
      `0380f5f style(dashboard): mejorar detalle de observaciones lindus`,
      `5889f3f style(dashboard): seleccionar observaciones lindus desde tabla`.

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
- Migración del histórico: en gran parte desbloqueada (2026-06-10).
  **Resuelto por el cliente** (decisión #44): 11 valores de meteo +
  bloque V0043, especies aceptadas, UTM ETRS89/30N. **Resuelto por
  deducción** (decisión #45): temperaturas M1002/M1039, `id_lugar` de
  97 visitas, `grupo`/`nombre_comun` de especies. **Aún pendiente del
  cliente** (no deducible): observador de las 98 visitas, `id_lugar`
  de V0001, UTM/municipio de Lindus y Trona, vocabularios de tablas
  nuevas y quinto ecosistema.
- Vocabularios cerrados pendientes con el cliente:
  `fototrampeo.tipo_media`, `estudio_campo.deteccion/migracion/altura`,
  `castor_rastros.tipo_rastro/intensidad_rastro/reciente_antiguo`.

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
- `dashboard/paginas/02_visitas.py`: listado de visitas con filtros, panel
  de detalle, meteorología asociada, resumen de registros por tipo y
  navegación relacional hacia la página de origen (Lindus implementado;
  resto pendiente).
- `dashboard/paginas/03_lindus.py`: consulta Lindus con filtros, métricas,
  gráficos, tabla seleccionable (click directo en fila), ficha de detalle
  maestro-detalle con bloque Visita y botón "Ver visita", meteorología
  ("Meteorología de la visita") y fotos Drive.
- `tests/test_dashboard_titulos.py`: tests que verifican la navegación por
  botones, el título centralizado en `app.py` y que las páginas no pintan
  cabecera propia.
- `dashboard/paginas/04_cajas_nido.py`: consulta de cajas nido con métricas,
  gráficos, mapa, tabla seleccionable por clic de fila, ficha detalle
  maestro-detalle con bloque Visita y botón "Ver visita", y fotos.
- `dashboard/paginas/05_nidos_rapaces.py`: histórico de nidos rapaces con
  tabla seleccionable, ficha detalle maestro-detalle con texto de revisión
  completo, bloque Visita y botón "Ver visita", mapa y fotos.
- `dashboard/paginas/06_cebos_avispones.py`: seguimiento de cebos con
  acumulados calculados, composición, mapa, tabla seleccionable, ficha
  detalle maestro-detalle con sección de capturas, bloque Visita y
  botón "Ver visita".
- `dashboard/paginas/07_mamiferos_puentes.py`: consulta de mamíferos en
  puentes con filtros, gráficos, mapa, tabla seleccionable, ficha detalle
  maestro-detalle con valores humanizados (PRESENTE/AUSENTE/POSIBLE,
  evidencias), bloque Visita y botón "Ver visita".
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
- `sql/002_esquema_v2.sql`: esquema v2 (10 tablas). Es el que está
  aplicado actualmente en Supabase dev.
- `sql/003_esquema_v3.sql`: esquema v3 definitivo (14 tablas) tras la
  revisión del Excel del cliente. DROP+CREATE; pendiente de aplicar
  en Supabase dev junto con la migración del histórico.
- `docs/REVISION_EXCEL_CLIENTE_V03.md`: correcciones de datos que
  debe responder el cliente y reglas del futuro script de
  importación del histórico 2025.
- `docs/BirdLog_tablas_cliente_v03.xlsx`: Excel del cliente con el
  histórico real. **Fuera de git** (`docs/*.xlsx` en `.gitignore`).
- `scripts/importar_historico.py`: genera SQL INSERT desde el Excel
  (auditoría y reimportaciones). Usa `openpyxl`; salida a stdout.
- `scripts/insertar_historico.py`: inserta meteo y lindus en Supabase
  BirdLog via `supabase-py` por lotes de 200. Requiere clave anon o
  service_role con permisos de INSERT en el proyecto.
- `docs/Revisar con GABI.md`: cuestionario para el cliente con las
  preguntas que bloquean la migración (meteo errónea, especies,
  UTM, visitas 2025, vocabularios nuevos, quinto ecosistema).
  Actualizado 2026-06-10 con las respuestas ya recibidas.
- `docs/Informe_revision.docx`: informe de revisión del Excel enviado
  al cliente; Gabi respondió resaltando en amarillo (meteo, especies,
  UTM, 3 columnas vs campo único). Fuente de la decisión #44.
- `docs/modelo_datos.md`: descripción completa de las 14 tablas (v3)
  con todos los campos, tipos y valores cerrados.
- `docs/formato_plaud.md`: plantillas Plaud definitivas v1.1 y formato
  estructurado esperado para los `.txt`. Revisado 2026-06-10 con los
  campos nuevos del esquema v3 (conteos de personas en meteo Lindus,
  trampa/UTM en cebos, cría en nidos rapaces) y la lista de las 4
  plantillas futuras pendientes de vocabulario.
- `docs/SEGURIDAD.md`: reglas de seguridad y manejo de credenciales.
- `docs/DECISIONES.md`: historial de decisiones técnicas tomadas.
- `docs/USO_DASHBOARD.md`: guía de uso local del dashboard para el
  observador, incluyendo arranque, páginas, filtros, fotos, edición,
  borrado seguro y errores de Supabase.
- `docs/PLAN_APP_PIPELINE.md`: diseño completo de la app local del
  pipeline Plaud → Supabase (arquitectura, pantalla, estados de
  resultado, decisiones de herramienta, riesgos y plan por fases).
- `docs/USO_APP_PIPELINE.md`: guía de uso de la app pipeline para el
  observador (arranque, colores, errores frecuentes, reproceso de
  archivos fallidos).
- `app_pipeline/app.py`: app Streamlit del pipeline (puerto 8502).
  Cabecera de estado, botón "Procesar", tarjetas de resultado y
  botones "Abrir dashboard" y "Abrir Claude.ai".
- `app_pipeline/lib/estados.py`: dataclasses `ResultadoArchivo` y
  `EstadoEntorno`; constantes de estado (OK/ERROR/INCOMPLETO/PENDIENTE).
- `app_pipeline/lib/enlaces.py`: URLs de dashboard y Claude.ai.
- `app_pipeline/lib/orquestador.py`: `comprobar_entorno()` y
  `procesar_lote()` wrapeando `src.pipeline.procesar_drive`.
- `app_pipeline/lib/ui.py`: componentes visuales Streamlit (cabecera,
  tabla resumen, tarjetas expandibles).
- `tests/test_app_pipeline_orquestador.py`: tests del orquestador
  (clasificación de errores, traducción de resultados, excepciones del
  lote, pausa, callback de progreso, monkeypatch).
- `tests/test_backup_exportar.py`: tests del backup CSV (tablas del
  esquema v3 incluidas y retención de 30 carpetas sin tocar otros
  archivos).
- `scripts/abrir_app_pipeline.sh`: script de arranque de la app pipeline
  (activa venv, comprueba Streamlit, arranca en puerto 8502).
- `scripts/BirdLog_Pipeline.desktop`: lanzador de escritorio para Ubuntu/
  GNOME. Copia fuente; el icono activo está en `~/Escritorio/`.
- `.env.example`: plantilla de variables de entorno (sin valores reales).
- `diagrama_relaciones_v2.html`: diagrama visual de relaciones entre tablas.
---

## Handoff

**Estado a 2026-06-11**: histórico 2025 importado en Supabase BirdLog,
dashboard verificado con datos reales y código del pipeline revisado y
robustecido (decisión #47). 135 tests pasan.

**Supabase BirdLog** (`mbphfgmjryyxzjgcwqxo`, EU-West-3):
- Esquema v3 activo (14 tablas). `.env` apunta a este proyecto.
- Datos: 135 especies, 2 observadores, 2 lugares, 97 visitas, 1.048 meteo,
  10.870 lindus. Tablas vacías: cajas_nido, nidos_rapaces, cebos_avispones,
  mamiferos_puentes, fototrampeo, cuaderno_campo, estudio_campo,
  castor_rastros, fotos.
- **CRÍTICO**: `.env` usa clave **anon** JWT (INSERT/UPDATE/DELETE
  concedidos a `anon`). Sustituir por `service_role` antes de procesar
  datos reales con el pipeline.

**Dashboard** (`localhost:8999`, `.venv/bin/python3 -m streamlit run
dashboard/app.py --server.port 8999`):
- Todas las páginas verificadas con datos reales el 2026-06-10.
- Mapa sin puntos: utm_x/utm_y de Lindus y Trona son NULL (pendiente del
  cliente).

**App pipeline** (`localhost:8502`, scripts/abrir_app_pipeline.sh):
- Funcional y revisada (2026-06-11): progreso en vivo por archivo, sin
  tracebacks, pausa de Supabase detectada en consulta, aviso claro si
  Drive no mueve un `.txt`, backup de las 15 tablas v3 con retención 30.
- Pendiente: prueba real con `.txt` en `01_entrada` de Drive.

**Próximas tareas (en orden)**:
1. Sustituir clave anon en `.env` por `service_role` (Supabase →
   Settings → API → service_role key).
2. Prueba real del pipeline con Nidos rapaces, Cebos, Cajas nido y Lindus.
3. Recoger del cliente: observador de las 98 visitas, `id_lugar` de V0001,
   UTM/municipio de Lindus y Trona, vocabularios de tablas nuevas, quinto
   ecosistema de cajas_nido.

**Pendientes técnicos menores**:
- Añadir sección de arranque de `app_pipeline` en `README.md`.
- Limpiar visitas de demo en Supabase dev (2026-05-03) si existen.
- `DRIVE_FOTOS_ID` no está en `.env` — añadir cuando se reactive fotos.
