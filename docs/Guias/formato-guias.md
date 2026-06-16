# Formato de las hojas-guía — reglas de campos y validación

Sistema de gestión de datos de fauna (BirdLog).

Este documento es la **referencia de formato** para las hojas-guía
tabulares con las que el observador recoge los datos de campo. El agente
lee estas hojas, valida cada campo contra estas reglas y el modelo de
datos (`docs/modelo_datos.md`) y, solo cuando todo es correcto y Javi lo
autoriza, inserta en Supabase.

Las plantillas concretas (una tabla por tipo de visita/observación) viven
junto a este archivo, en `docs/Guias/`:

| Plantilla | Tabla destino |
|---|---|
| `lindus.md` | `visitas` + `meteorologia` + `lindus` |
| `cajas_nido.md` | `visitas` + `meteorologia` + `cajas_nido` |
| `nidos_rapaces.md` | `visitas` + `meteorologia` + `nidos_rapaces` |
| `cebos_avispones.md` | `visitas` + `meteorologia` + `cebos_avispones` |
| `mamiferos_puentes.md` | `visitas` + `meteorologia` + `mamiferos_puentes` |
| `fototrampeo.md` | `visitas` + `fototrampeo` |
| `cuaderno_campo.md` | `visitas` + `cuaderno_campo` |
| `estudio_campo.md` | `visitas` (IMPACTO_AMBIENTAL) + `meteorologia` + `estudio_campo` |
| `castor_rastros.md` | `visitas` + `castor_rastros` |

> **De dónde llegan los datos.** Lindus llega normalmente como hoja-guía
> tabular. El resto de tipos puede llegar por hoja-guía o por
> Telegram/voz; en ese caso el agente reconstruye la misma estructura de
> campos antes de validar. Sea cual sea el origen, **las reglas de este
> documento se aplican igual**: el agente nunca inserta nada que no las
> cumpla.

---

## Principios generales

- Cada hoja-guía produce una o varias filas con la forma `CAMPO → valor`.
  Las cabeceras de las tablas de las plantillas usan los **nombres reales
  de columna** del modelo de datos; el observador rellena debajo.
- Los nombres de campo se mantienen exactamente como están definidos
  (`fecha`, `hora_inicio`, `lugar_visita`...). No se traducen ni se
  inventan campos.
- Los campos `id_*` no los rellena el observador: los genera o resuelve
  el sistema (resolución de FKs contra los catálogos).
- Los nombres de lugares, especies y observadores deben **resolverse
  contra los catálogos** de Supabase. El sistema tolera diferencias
  simples de mayúsculas/minúsculas, pero no nombres ambiguos ni valores
  que no existan en el catálogo.
- Si un valor de catálogo no existe, el agente **no inserta nada**: avisa
  con los pasos a seguir (dar de alta el lugar/especie/observador en
  Supabase y añadirlo al vocabulario de la hoja-guía).
- `fecha` y `fecha_colocacion` se escriben en formato `YYYY-MM-DD`
  (ej. `2026-05-03`). El sistema tolera `DD/MM/YYYY` y normaliza a ISO,
  pero el formato preferido es `YYYY-MM-DD`.
- Las horas se escriben en formato `HH:MM` (ej. `10:00`).
- Las coordenadas UTM se escriben como números enteros en metros (X e Y).
  El sistema de referencia del proyecto es único y fijo: **ETRS89,
  huso 30N** (decisión #44; todos los puntos están en Navarra). El
  observador NO escribe huso ni datum; el sistema los conoce.
- No se rellenan celdas con datos inventados. Si un dato no se conoce, se
  deja en blanco (y el agente decidirá si bloquea o no según las reglas
  de campos obligatorios).
- `IMPACTO_AMBIENTAL` / estudio de campo se modela como una visita
  `IMPACTO_AMBIENTAL` + meteorología + filas de `estudio_campo`.

---

## Campos obligatorios por tipo

El agente bloquea la inserción si falta alguno de estos campos. Coinciden
con `MINIMOS_VISITA` en `src/parser/validacion.py`.

| Tipo de registro | Campos de visita obligatorios | Bloque mínimo |
|---|---|---|
| `INICIO_VISITA_LINDUS` | `tipo_visita`, `fecha`, `hora_inicio`, `lugar_visita`, `observador` | — |
| `OBSERVACIONES_LINDUS` | `tipo_visita`, `fecha` | ≥1 observación con `especie`, `hora`, `numero`, `comportamiento` |
| `FIN_VISITA_LINDUS` | `tipo_visita`, `fecha`, `hora_fin` | meteorología opcional (cada bloque exige `hora`) |
| `VISITA_CAJA_NIDO` | `tipo_visita`, `fecha`, `hora_inicio`, `hora_fin`, `lugar_caja`, `observador` | 1 caja con `ecosistema`, `especie_arbol`, `estado_nido`, `ocupada` |
| `VISITA_CEBO_AVISPON` | `tipo_visita`, `fecha`, `hora_inicio`, `hora_fin`, `lugar_cebo`, `observador` | 1 cebo con al menos una captura o `observaciones` |
| `VISITA_NIDO_RAPAZ` | `tipo_visita`, `fecha`, `hora_inicio`, `hora_fin`, `lugar_nido`, `observador` | 1 nido con `texto_revision` |
| `VISITA_MAMIFEROS_PUENTE` | `tipo_visita`, `fecha`, `hora_inicio`, `hora_fin`, `lugar_puente`, `observador` | ≥1 mamífero con `especie`, `presencia` |

> En Lindus, `hora_fin` queda en blanco mientras la jornada está abierta
> y se rellena al cerrar la visita (`FIN_VISITA_LINDUS`). Las
> observaciones del inicio se conservan y se combinan con las del cierre
> (decisión #39).

Las plantillas `fototrampeo`, `cuaderno_campo`, `estudio_campo` y
`castor_rastros` todavía no tienen sus vocabularios cerrados confirmados
por el cliente; sus campos cerrados se validan como texto libre hasta que
se cierren (ver «Vocabularios pendientes»).

---

## Valores cerrados (CHECK constraints)

El agente rechaza cualquier valor fuera de estas listas. Se escriben
**en mayúsculas y exactamente** como aparecen aquí.

| Campo | Valores aceptados |
|---|---|
| `tipo_visita` | `LINDUS`, `CAJA_NIDO`, `CEBO_AVISPON`, `NIDO_RAPAZ`, `MAMIFEROS_PUENTES`, `IMPACTO_AMBIENTAL`, `FOTOTRAMPEO`, `CUADERNO_CAMPO`, `CASTOR_RASTROS` |
| `comportamiento` (lindus) | `MIGRADOR`, `NORTE`, `LOCAL` |
| `ecosistema` (cajas_nido) | `ZONA_SALVAJE`, `ZONA_URBANA`, `PARQUE_CON_RIO`, `PARQUE_URBANO` *(quinto pendiente)* |
| `estado_nido` (cajas_nido) | `POCAS_HIERBAS`, `MUCHAS_HIERBAS`, `CASI_TERMINADO`, `TERMINADO` |
| `orientacion_caja` (cajas_nido) | `N`, `NE`, `E`, `SE`, `S`, `SW`, `W`, `NW` |
| `ocupada` (cajas_nido) | `true`, `false` |
| `presencia` (mamiferos_puentes) | `PRESENTE`, `AUSENTE`, `POSIBLE` |
| `tipo_evidencia` (mamiferos_puentes) | `HUELLA`, `EXCREMENTO`, `MADRIGUERA`, `AVISTAMIENTO` |
| `incuba` (nidos_rapaces) | `true`, `false` |
| `nubosidad` (meteorologia) | entero `0`–`8` |
| `viento_direccion` (meteorologia) | `N`, `NNE`, `NE`, `ENE`, `E`, `ESE`, `SE`, `SSE`, `S`, `SSW`, `SW`, `WSW`, `W`, `WNW`, `NW`, `NNW` |
| `viento_intensidad` (meteorologia) | `CALMA`, `FLOJO`, `BRISA`, `MODERADO`, `FUERTE` |
| `precipitacion` (meteorologia) | `NULA`, `LEVE`, `MODERADA`, `FUERTE`, `NIEVE`, `NIEBLA` |
| `visibilidad` (meteorologia) | `BUENA`, `REGULAR`, `MALA` |

### Catálogos (resolución contra Supabase, no son CHECK)

- `observador`: `Gabi`, `Ander` (tabla `observadores`).
- `lugar_visita` / `lugar_caja` / `lugar_cebo` / `lugar_nido` /
  `lugar_puente`: nombre o código exacto de la tabla `lugares`
  (p. ej. `Lindus`, `Trona`, `BAR01`, `Cebo avispón 1`).
- `especie`: nombre del catálogo `especies` (en **singular**).

---

## Normalización que aplica el observador al rellenar

El observador escribe ya el valor cerrado o de catálogo correcto. Estas
son las equivalencias más útiles para no equivocarse:

**Direcciones de viento** (convención inglesa, sin espacios):
norte → `N`, sur → `S`, este → `E`, oeste → `W`, noreste → `NE`,
noroeste → `NW`, sureste → `SE`, suroeste → `SW`.

**Precipitación**: sin lluvia / no llueve / nula → `NULA`. Nunca se
escribe `SIN LLUVIA`; el valor correcto es `NULA`. Llovizna / lluvia
débil → `LEVE`.

**Nubosidad**: despejado → `0`; cielo cubierto → `8`.

**Especies**: siempre en **singular** y tal como figuran en el catálogo
(`milano real`, no `milanos reales`; `carbonero común`, no `carboneros
comunes`). Para mamíferos se usa el nombre común del catálogo
(`Nutria paleártica`, `Visón europeo`, `Garduña`, `Castor europeo`,
`Tejón europeo`).

**Códigos de caja**: compactos, en mayúsculas, sin espacios y con número
de dos dígitos cuando el catálogo lo usa así (`BAR01`, no `bar 1`).

**Cebos de avispón**: nombre exacto del catálogo (`Cebo avispón 1`).

`especie_texto` (y campos `_texto` análogos) guardan el nombre tal como
lo escribió el observador; `id_especie` resuelto contra el catálogo es el
dato bueno. Sirven de traza de auditoría.

---

## Cómo valida el agente (antes de insertar)

1. **Estructura y mínimos**: comprueba `tipo_visita`/`tipo_registro` y
   los campos obligatorios de la tabla anterior. Si falta alguno, avisa
   y no inserta.
2. **Formatos**: fechas `YYYY-MM-DD` (tolera `DD/MM/YYYY`), horas
   `HH:MM`, `nubosidad` entre 0 y 8, UTM enteros.
3. **Valores cerrados**: cada campo cerrado debe estar en su lista; si
   no, avisa con el valor recibido y los valores aceptados.
4. **Resolución de catálogos (FKs)**: lugares, especies y observadores
   deben existir. Si alguno no existe, **no inserta nada** y devuelve los
   pasos para darlo de alta (Supabase + vocabulario de la hoja-guía).
5. **Autorización**: solo cuando todo es correcto y Javi lo autoriza, el
   agente inserta en Supabase y hace el backup correspondiente.

Estas reglas están implementadas y cubiertas por tests en
`src/parser/validacion.py`, `src/parser/normalizacion.py` y
`src/insercion/` (parser/validación reutilizables independientes del
origen de los datos).

---

## Meteorología (bloque común)

Varios tipos llevan meteorología asociada. En Lindus/Trona se registra
una fila por hora; en el resto, una fila por visita (opcional). Columnas:

`hora` *(obligatoria si hay bloque)*, `temperatura` (número sin
unidades), `nubosidad` (0–8), `viento_direccion`, `viento_intensidad`,
`precipitacion`, `visibilidad`, `presentes`, `observando`, `visitantes`
(conteos de personas del protocolo Lindus, enteros), `observaciones`.

Los campos históricos del Excel 2025 (`humedad_relativa`, `presion_atm`,
niveles de nubes...) no se rellenan en campo: solo los completa la
importación del histórico.

---

## Vocabularios pendientes con el cliente

Las plantillas de los 4 tipos nuevos del esquema v3 existen como
borrador, pero sus vocabularios cerrados están **pendientes de confirmar
con el cliente** (`docs/Revisar con GABI.md` §5). Hasta entonces esos
campos se tratan como texto libre y no como valor cerrado:

| Plantilla | Campos sin vocabulario cerrado |
|---|---|
| `fototrampeo.md` | `tipo_media` |
| `estudio_campo.md` | `deteccion`, `migracion`, `altura`, lados |
| `castor_rastros.md` | `tipo_rastro`, `intensidad_rastro`, `reciente_antiguo`, `aplicacion` |
| `cuaderno_campo.md` | — (campos libres) |

Además sigue pendiente el **quinto ecosistema** de `cajas_nido`.
