# AGENTS.md — Sistema de gestión de datos de fauna

> Fuente de verdad para Codex y Claude Code. Copia idéntica en
> `CLAUDE.md`. Actualizar con: `cp AGENTS.md CLAUDE.md`

---

## 1. Protocolo de bitácora — OBLIGATORIO

### Al iniciar la sesión
Antes de responder al usuario:
1. Lee `docs/BITACORA.md`.
2. Lee `docs/DECISIONES.md`.
3. Saluda con esta frase exacta:
   > "He leído la bitácora. Estamos en **[fase actual]**,
   > la próxima tarea es **[próxima tarea]**. ¿Seguimos?"

### Durante la sesión
- Marca checkboxes en `BITACORA.md` al completar tareas.
- Anota decisiones técnicas nuevas en `DECISIONES.md`
  inmediatamente, no al final.

### Cuando el usuario diga "rutina de cierre"
1. Mueve tareas terminadas a "Tareas completadas".
2. Actualiza "Estado actual" (fase, fecha, próxima tarea).
3. Anota bloqueos pendientes.
4. Añade archivos nuevos al glosario.
5. Si hay cambio de agente: escribe resumen de handoff detallado.
6. Confirma al usuario qué has actualizado.

---

## 2. El proyecto

### Qué construimos
Sistema interno para recoger datos de fauna con Plaud, insertarlos
en Supabase con backup automático, y visualizarlos en un dashboard
local Streamlit.

### Flujo
```
Plaud (plantilla + vocabulario cerrado)
    → .txt a Drive
Script Python (parsea + resuelve FKs + inserta + backup)
    → Supabase
    → backup CSV local + Drive
Dashboard Streamlit local
```

### Modelo de datos — 14 tablas (v3)
Detalle completo en `docs/modelo_datos.md`.

**Catálogos** (se rellenan una vez):
- `especies` — id_especie, nombre_cientifico, nombre_comun, grupo,
  codigo_origen
- `observadores` — id_observador, nombre_observador
- `lugares` — id_lugar, nombre_lugar, tipo_lugar, municipio,
  utm_x, utm_y, codigo_origen

**Hub central**:
- `visitas` — id_visita, id_lugar(FK), id_observador(FK),
  tipo_visita, fecha, hora_inicio, hora_fin, observaciones,
  codigo_origen
- `meteorologia` — id_meteo, id_visita(FK), hora, temperatura,
  nubosidad, viento_direccion, viento_intensidad,
  precipitacion, visibilidad, presentes, observando, visitantes,
  observaciones + campos históricos opcionales (humedad_relativa,
  presion_atm, precipitacion_tipo, niveles de nubes) +
  codigo_origen

**Tablas específicas** (cuelgan de visitas):
- `lindus` — id_lindus, id_visita(FK), id_especie(FK), hora,
  numero, comportamiento, edad, sexo, plumaje, observaciones,
  especie_texto, codigo_origen
- `cajas_nido` — id_cajanido, id_visita(FK), id_lugar(FK),
  id_especie(FK), ecosistema, especie_arbol, estado_nido,
  ocupada, huevos, pollos + 12 campos IB+ opcionales
- `nidos_rapaces` — id_nido_rapaz, id_visita(FK), id_lugar(FK),
  id_especie(FK), texto_revision, comunicacion_personal,
  descripcion_nido, incuba, numero_pollos, pollos_volados,
  observaciones
- `cebos_avispones` — id_cebo, id_visita(FK), id_lugar(FK),
  vv, crabro, avispa_europea, polilla, mariposa, otros,
  observaciones, numero_trampa, fecha_colocacion, utm_x_nido,
  utm_y_nido
- `mamiferos_puentes` — id_mamifero, id_visita(FK), id_lugar(FK),
  id_especie(FK), presencia, tipo_evidencia, observaciones
- `fototrampeo` — id_fototrampeo, id_visita(FK), id_lugar(FK),
  id_especie(FK), especie_texto, fecha_colocacion, fecha_revision,
  fecha_imagen, tipo_media, numero_imagenes, observaciones
  *(imágenes vía tabla fotos)*
- `cuaderno_campo` — id_cuaderno, id_visita(FK), id_lugar(FK
  opcional), id_especie(FK), especie_texto, numero, observaciones
- `estudio_campo` — id_estudio, id_visita(FK), id_especie(FK),
  especie_texto, numero, deteccion, hora_observacion, distancias y
  lados (inicial/mínima/final), vuelo_sobre, direccion_vuelo,
  migracion, altura, observaciones *(la sesión es una visita
  IMPACTO_AMBIENTAL + meteorologia)*
- `castor_rastros` — id_castor_rastro, id_visita(FK), id_lugar(FK),
  id_especie(FK), tipo_rastro, intensidad_rastro, reciente_antiguo,
  aplicacion, observaciones
- `fotos` — id_foto, id_visita(FK), tabla_origen, id_origen,
  url_drive, descripcion, fecha_subida *(fase futura)*

**Valores cerrados (CHECK constraints)**:
- `especies.grupo`: RAPAZ, PASERIFORME, ACUATICA, INVERTEBRADO,
  MAMIFERO, OTRO
- `lugares.tipo_lugar`: CONTEO_MIGRATORIO, CAJA_NIDO,
  CEBO_AVISPON, NIDO_RAPAZ, PUENTE, FOTOTRAMPEO, ESTUDIO_CAMPO,
  OTRO
- `visitas.tipo_visita`: LINDUS, CAJA_NIDO, CEBO_AVISPON,
  NIDO_RAPAZ, MAMIFEROS_PUENTES, IMPACTO_AMBIENTAL, FOTOTRAMPEO,
  CUADERNO_CAMPO, CASTOR_RASTROS
- `lindus.comportamiento`: MIGRADOR, NORTE, LOCAL
- `cajas_nido.ecosistema`: ZONA_SALVAJE, ZONA_URBANA,
  PARQUE_CON_RIO, PARQUE_URBANO *(quinto pendiente)*
- `cajas_nido.estado_nido`: POCAS_HIERBAS, MUCHAS_HIERBAS,
  CASI_TERMINADO, TERMINADO
- `cajas_nido.orientacion_caja`: N, NE, E, SE, S, SW, W, NW
- `mamiferos_puentes.presencia`: PRESENTE, AUSENTE, POSIBLE
- `mamiferos_puentes.tipo_evidencia`: HUELLA, EXCREMENTO,
  MADRIGUERA, AVISTAMIENTO
- `meteorologia.nubosidad`: INTEGER entre 0 y 8
- Vocabularios pendientes con el cliente: `fototrampeo.tipo_media`,
  `estudio_campo.deteccion/migracion/altura`,
  `castor_rastros.tipo_rastro/intensidad_rastro/reciente_antiguo`

**SQL**: `sql/003_esquema_v3.sql` (v2 en `sql/002_esquema_v2.sql`,
aún aplicado en Supabase dev)

---

## 3. Stack y convenciones

- Python 3.11+
- `supabase-py`, `pydantic`, `streamlit`, `pytest`,
  `google-api-python-client`
- Naming: `snake_case` para todo Python. Español para dominio,
  inglés para términos técnicos.
- Comentarios en español.
- Cada archivo: una responsabilidad. Funciones < 30 líneas.
- Antes de añadir librería nueva: justificar por qué la estándar
  no vale.

---

## 4. Entornos Supabase

- **dev**: desarrollo y pruebas. Default.
- **prod**: datos reales. Solo con autorización explícita del
  usuario en esa sesión.

Variable `ENTORNO` en `.env` controla cuál se usa.

---

## 5. Seguridad — REGLAS NO NEGOCIABLES

**NUNCA** en git: claves Supabase, credenciales Drive (JSON),
IDs privados de Drive, passwords, tokens, datos reales del
observador (CSV con observaciones).

Todo en `.env` (en `.gitignore`). `.env.example` solo con
plantilla sin valores.

**Antes de proponer cualquier commit**, verificar el diff:
1. ¿Hay `.env`, `*.credentials.json`, `secrets.toml`, claves?
2. ¿Hay URLs con credenciales embebidas?
3. ¿Hay datos reales del observador?

Si sí a cualquiera: **detener y avisar**. No comitear.

Ver `docs/SEGURIDAD.md` para detalle completo.

---

## 6. Backup

Tras cada inserción significativa o mínimo diariamente:
1. Exportar cada tabla a CSV.
2. Guardar en `backups/backup_YYYY-MM-DD/` local.
3. Subir a Drive en `Backups Sistema Fauna/`.

Retención: últimos 30 backups. Módulo: `src/backup/`.
Función pública: `hacer_backup(entorno)`.

---

## 7. Pausa Supabase

Plan gratuito pausa tras 7 días sin actividad. Aceptamos la
pausa. El sistema detecta errores de conexión por pausa y
muestra mensaje claro: "El proyecto Supabase está pausado.
Reactívalo en supabase.com y vuelve a intentarlo."

---

## 8. Resolución de FKs y lugares/especies nuevos

Cuando el script no encuentra un nombre en el catálogo:
- No inserta nada.
- Muestra mensaje claro con pasos: dar de alta en Supabase y
  añadir al vocabulario del Plaud.
- Deja el .txt en `pendientes/` para reprocesar.

---

## 9. Estructura del repositorio

```
sistema-fauna/
├── AGENTS.md              # Este archivo
├── CLAUDE.md              # Copia idéntica
├── README.md
├── .env.example           # Plantilla sin valores reales
├── .gitignore
├── pyproject.toml
├── docs/
│   ├── BITACORA.md
│   ├── DECISIONES.md
│   ├── PRINCIPIOS.md
│   ├── SEGURIDAD.md
│   ├── modelo_datos.md
│   └── formato_plaud.md   # (pendiente — Fase 2)
├── sql/
│   └── 002_esquema_v2.sql # Esquema definitivo
├── src/
│   ├── config.py          # Carga .env
│   ├── conexion.py        # Cliente Supabase
│   ├── parser/
│   │   └── plaud.py
│   ├── insercion/
│   │   ├── catalogos.py   # nombre → id
│   │   └── escritura.py
│   ├── backup/
│   │   ├── exportar.py
│   │   └── drive.py
│   └── fotos/
│       └── drive.py
├── dashboard/
│   ├── app.py
│   ├── paginas/
│   │   ├── 1_lindus.py
│   │   ├── 2_avispones.py
│   │   ├── 3_mamiferos.py
│   │   ├── 4_rapaces.py
│   │   ├── 5_cajas_nido.py
│   │   └── 6_explorador.py
│   └── lib/
│       ├── consultas.py
│       └── graficos.py
├── tests/
│   ├── test_parser.py
│   ├── test_catalogos.py
│   └── ejemplos_plaud/
└── backups/               # En .gitignore
```

---

## 10. Git

- Rama única: `main`.
- Prefijos: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`,
  `chore:`.
- Commits pequeños y frecuentes.
- Verificar diff antes de cada commit (sección 5).

---

## 11. Tests

Prioridad alta (con tests obligatorios):
- `src/parser/plaud.py`
- `src/insercion/catalogos.py`
- `src/insercion/escritura.py`
- `src/backup/exportar.py`

Prioridad baja (se valida visualmente o se mockea):
- Dashboard, conexión real a Supabase.

---

## 12. Reparto Codex / Claude Code

- **Codex**: la mayoría del código Python. Parser, inserción,
  backup, dashboard.
- **Claude Code**: refactors amplios, revisión de código
  existente, tests, documentación técnica.

---

## 13. Principios

Ver `docs/PRINCIPIOS.md`. Resumen:
1. Simplicidad antes que sofisticación.
2. El observador no programa.
3. Los datos son sagrados.
4. Dev y prod separados.
5. La bitácora es la memoria del proyecto.
6. Los secretos no entran en git.

---

## 14. Si estás bloqueado

Para. Pregunta con este formato:
> **Bloqueado en**: [tarea]
> **El problema**: [qué pasa]
> **He probado**: [qué intenté]
> **Necesito decidir**: [opción A vs B]
