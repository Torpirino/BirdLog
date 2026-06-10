# Revisión de `BirdLog_tablas_cliente_v03.xlsx`

Fecha de revisión: 2026-06-10.
Resultado de diseño: decisiones #40–#44 y esquema `sql/003_esquema_v3.sql`.

Este documento recoge los problemas de **datos** detectados en el
Excel, separados en dos bloques: lo que debe corregir/confirmar el
cliente y lo que resolverá el script de importación.

---

## 0. Respuestas del cliente (2026-06-10) — RESUELTO en el Excel

Gabi respondió en `docs/Informe_revision.docx` (resaltado en amarillo).
Aplicado sobre `BirdLog_tablas_cliente_v03.xlsx` (decisión #44):

- ✅ **Meteo 11 valores**: corregidos con el dato real (ver 1.1).
- ✅ **Bloque V0043 (M0464–M0478)**: reordenado, presión movida a
  `presion_atm`, `humedad_relativa` vacía.
- ✅ **Especies (21 entradas `revisar`)**: aceptadas todas como
  correctas; `revisar` SI→NO en el Excel.
- ✅ **UTM**: sistema del proyecto = **ETRS89, huso 30N** (todo Navarra);
  columnas `datum` y `huso` añadidas a las hojas con UTM.
- ✅ **TOTAL** confirmado como suma de los 3 campos; **3 columnas**
  `migrador`/`direccion_norte`/`local` se mantienen (origen Trektellen.nl).
- 🟡 **Deducido sin cliente (decisión #45)**: `M1002`→6.8 y `M1039`→9.5
  (mismo patrón de decimal); `visitas.id_lugar` de 97 visitas derivado
  de `meteo` (59 Lindus / 38 Trona); `grupo` y `nombre_comun` de las 135
  especies por taxonomía estándar. Revisables por el cliente, no bloquean.
- ⚠️ **Pendiente del cliente (no deducible)**: observador de las 98
  visitas; UTM X/Y y municipio de Lindus y Trona; `id_lugar` de V0001
  (sin meteo); vocabularios de las tablas nuevas; quinto ecosistema.

---

## 1. Para el cliente (Gabi)

### 1.1 Meteo: 24 filas con valores imposibles

No se autocorrigen (principio: los datos son sagrados; el importador
no inventa valores medidos). Indicar el valor correcto o marcar como
desconocido.

**Bloque desplazado V0043 (2025-09-05)** — ya señalado en el propio
`informe_revision` del Excel: en M0464–M0478 la columna `humedad`
contiene valores ~1026–1029, que parecen ser la presión. Afecta a
15 filas; falta saber dónde quedó la humedad real.

| id_meteo | fecha | hora | problema |
|---|---|---|---|
| M0464–M0478 | 2025-09-05 | 05:50–20:30 | humedad = 1026–1028.7 (¿presión desplazada?) |

**Valores sueltos fuera de rango** (9 filas):

| id_meteo | fecha | hora | problema | posible causa |
|---|---|---|---|---|
| M0217 | 2025-08-11 | 04:50 | presión = 1929.8 | ¿1029.8? |
| M0733 | 2025-10-02 | 15:00 | presión = 10289 | coma decimal (¿1028.9?) |
| M0864 | 2025-10-16 | 16:00 | humedad = 786 | coma decimal (¿78.6?) |
| M0906 | 2025-10-20 | 13:00 | presión = 101631 | coma decimal (¿1016.31?) |
| M0991 | 2025-10-31 | 12:00 | presión = 10191 | coma decimal (¿1019.1?) |
| M1002 | 2025-11-02 | 06:45 | temperatura = 68 | ¿6.8? |
| M1006 | 2025-11-02 | 11:00 | humedad = 818 | ¿81.8? |
| M1039 | 2025-11-10 | 11:00 | temperatura = 95 | ¿9.5? |
| M1045 | 2025-11-11 | 07:00 | humedad = 7302 | ¿73.02? |

Las "posibles causas" son hipótesis: debe confirmarlas quien tomó
el dato, no se aplicarán automáticamente.

### 1.2 Especies: completar catálogo

- Las 135 especies vienen **sin `nombre_comun` y sin `grupo`**.
  `grupo` (RAPAZ/PASERIFORME/ACUATICA/INVERTEBRADO/MAMIFERO/OTRO)
  es valor cerrado de la BD y eje de los gráficos del dashboard:
  hay que rellenarlo antes o justo después de importar.
- Las 21 entradas marcadas `revisar=SI` son rangos taxonómicos o
  textos a confirmar. Se importarán como entradas válidas del
  catálogo salvo indicación en contra:

  `SP003 Accipiter sp`, `SP005 Aguilucho sp`, `SP007 Alaudidea`,
  `SP009 Anthus sp`, `SP017 Bombus sp`,
  `SP028 Circus cyaneus / cenizo / papialbo`, `SP035 Columba sp`,
  `SP043 Dendrocopos sp`, `SP048 Emberiza sp`,
  `SP054 Falco tinnunculus / Cernícalo Primilla`,
  `SP057 Fringilla coelebs/Fringilla montifringilla`,
  `SP059 Fringilla sp`, `SP066 Hirundinidea`, `SP077 MediumRaptor`,
  `SP091 Passeriforme`, `SP103 Pieris species`, `SP110 Rapaz sp`,
  `SP120 Sturnus sp`, `SP128 Turdus sp`,
  `SP134 halcón no identificado`, `SP135 large larus sp`.

  Dudas concretas: `SP028` y `SP054` y `SP057` mezclan dos taxones
  en una entrada — ¿se mantienen como "no determinado entre X e Y"
  o se separan? `SP077 MediumRaptor` y `SP135 large larus sp`
  convendría renombrarlos a algo consistente.

### 1.3 Lugares y visitas

- La hoja `lugares` solo trae Lindus y Trona, sin UTM ni municipio.
  Falta definir **huso UTM y datum** (ETRS89/WGS84), ya marcado
  como pendiente en su informe, y aportar coordenadas.
- La hoja `visitas` no trae `id_lugar` en ninguna de las 98 filas.
  ¿Todas las visitas 2025 son de Lindus (LUG01) o hay jornadas de
  Trona (LUG02)? Hace falta asignarlo para importar.
- No hay observador en el Excel: se asignará el observador
  correspondiente (catálogo `observadores`) al importar. Confirmar
  quién firma el histórico 2025.

---

## 2. Para el script de importación (no requiere al cliente)

- **Direcciones de viento** (33 variantes en meteo): normalizar a
  los 16 rumbos en convención inglesa (la misma que
  `cajas_nido.orientacion_caja`):
  - Traducción español → inglés: `O→W`, `NO→NW`, `NNO→NNW`,
    `ONO→WNW`, `OSO→WSW`, `SO→SW`, `SSO→SSW` (48 filas).
  - Valores compuestos/ambiguos → `viento_direccion = NULL` y el
    literal pasa a `observaciones` de la fila de meteo (13 filas):
    `E/SE`, `N/NO`, `N/SO`, `NW-S`, `S N`, `S/O`, `S/SE`, `SE N`,
    `SO/NE`, `SWE N`.
- **Comportamiento Lindus**: pivotar `migrador`/`direccion_norte`/
  `local` a filas `comportamiento` + `numero`. Única fila mixta:
  `L002724` (2025-09-06 07:09, *Pernis apivorus*, 3 migrador +
  1 local) → se parte en dos filas. `total` no se importa
  (calculado).
- **`especie_texto`** de Lindus se conserva como traza junto al
  `id_especie` resuelto.
- **`codigo_origen`**: guardar los ids del Excel (`V0001`, `SP001`,
  `M0001`, `L000001`, `LUG01`) en la columna `codigo_origen` de
  cada tabla para poder auditar la migración.
- **Meteo**: `total_nubes_suma` → `nubosidad`; `fecha` e `id_lugar`
  no se importan (se derivan de la visita); el resto de columnas
  históricas van a los campos opcionales del esquema v3.

---

## 3. Estado

- Esquema v3 creado (`sql/003_esquema_v3.sql`), **sin aplicar** en
  Supabase dev (dev sigue en v2 con datos).
- Script de importación del histórico: pendiente de implementar.
- Vocabularios pendientes con el cliente: `fototrampeo.tipo_media`,
  `estudio_campo.deteccion/migracion/altura`,
  `castor_rastros.tipo_rastro/intensidad_rastro/reciente_antiguo`.
