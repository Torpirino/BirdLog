# Revisar con Gabi

Preguntas pendientes para cerrar la base de datos y poder importar
el histórico 2025 del Excel (`BirdLog_tablas_cliente_v03.xlsx`).
Fecha: 2026-06-10.

Cómo usarlo: responde debajo de cada pregunta o en la columna
"Respuesta" de las tablas. Si algo no se sabe, escribir
"desconocido" también es una respuesta válida.

> **Estado 2026-06-10**: Gabi respondió a la parte 1 (meteo), 2.2
> (especies) y 3.1 (UTM) en `docs/Informe_revision.docx`. Respuestas
> aplicadas al Excel (decisión #44).
>
> **Resuelto por deducción (decisión #45)**, revisable pero no
> bloqueante: temperaturas M1002→6.8 y M1039→9.5; `grupo` y
> `nombre_comun` de las 135 especies (§2.1) por taxonomía; `id_lugar`
> de 97 visitas (§4) derivado de `meteo`.
>
> **Aún se necesita a Gabi para**: observador de las visitas 2025 (§4),
> `id_lugar` de V0001 (sin meteo), UTM/municipio de Lindus y Trona
> (§3.2), vocabularios nuevos (§5) y quinto ecosistema (§6). Y, si
> quiere, revisar los `grupo`/`nombre_comun` propuestos.

---

## 1. Meteorología: valores que parecen erróneos

No vamos a corregir ningún valor medido por nuestra cuenta.
Necesitamos que confirmes el valor correcto (o que lo marques como
desconocido y lo dejaremos vacío).

### 1.1 Bloque desplazado del 2025-09-05 (visita V0043)

En las filas **M0464 a M0478** (de 05:50 a 20:30), la columna
`humedad_relativa` contiene valores entre 1026 y 1028.7, que parecen
ser la **presión atmosférica**.

- ¿Confirmas que esos valores son la presión? → Respuesta: **SÍ
  ("así es"). Reordenado: presión movida a `presion_atm`.**
- ¿Tienes la humedad real de ese día en alguna parte (cuaderno,
  app, foto de la estación)? → Respuesta: **No recuperada;
  `humedad_relativa` queda vacía en esas filas.**

### 1.2 Valores sueltos fuera de rango

| Fila | Fecha | Hora | Valor en el Excel | ¿Era esto? | Respuesta |
|---|---|---|---|---|---|
| M0217 | 2025-08-11 | 04:50 | presión 1929.8 | ¿1029.8? | ✅ **1029.8** |
| M0733 | 2025-10-02 | 15:00 | presión 10289 | ¿1028.9? | ✅ **1028.9** |
| M0864 | 2025-10-16 | 16:00 | humedad 786 | ¿78.6? | ✅ **78.6** |
| M0906 | 2025-10-20 | 13:00 | presión 101631 | ¿1016.31? | ✅ **1016.31** |
| M0991 | 2025-10-31 | 12:00 | presión 10191 | ¿1019.1? | ✅ **1019.1** |
| M1002 | 2025-11-02 | 06:45 | temperatura 68 | ¿6.8? | 🟡 **6.8 (deducido, #45; no estaba en el informe)** |
| M1006 | 2025-11-02 | 11:00 | humedad 818 | ¿81.8? | ✅ **81.8** |
| M1039 | 2025-11-10 | 11:00 | temperatura 95 | ¿9.5? | 🟡 **9.5 (deducido, #45; no estaba en el informe)** |
| M1045 | 2025-11-11 | 07:00 | humedad 7302 | ¿73.02? | ✅ **73.2** |

> Además, el informe corrigió estos otros (no estaban en esta tabla):
> M0588 `temperatura` "15,8+V593" → **15.8**; M0651 `humedad` 7.2 →
> **72**; M0743 `humedad` 7.8 → **78**; M0790 `humedad` 18.5 → **78.5**.

---

## 2. Catálogo de especies

### 2.1 Grupo y nombre común

Las 135 especies del Excel vienen sin `nombre_comun` y sin `grupo`.
El grupo es obligatorio para los gráficos del dashboard y solo admite
estos valores: **RAPAZ, PASERIFORME, ACUATICA, INVERTEBRADO,
MAMIFERO, OTRO**.

- ¿Puedes completar las dos columnas en el propio Excel?
  → Respuesta: **Pre-rellenadas por nosotros (decisión #45):
  `nombre_comun` y `grupo` de las 135 por taxonomía. Solo falta que
  las revises.**
- Si prefieres, podemos proponerte nosotros una asignación de grupo
  y tú solo la revisas. ¿Te encaja? → Respuesta: **Hecho. Repartos de
  grupo: RAPAZ 29, PASERIFORME 66, ACUATICA 13, INVERTEBRADO 13,
  OTRO 14 (vencejos, pícidos, palomas, cuco, abejaruco, abubilla).**

### 2.2 Las 21 entradas marcadas "revisar = SI"

La mayoría son rangos tipo "sp." y está bien que existan como
entradas del catálogo (un *Anthus sp* es un dato real). Salvo que
digas lo contrario, las importamos tal cual. Casos concretos:

| Código | Entrada | Pregunta | Respuesta |
|---|---|---|---|
| SP028 | Circus cyaneus / cenizo / papialbo | ¿Se queda como "no determinado entre los tres" o se separa? | |
| SP054 | Falco tinnunculus / Cernícalo Primilla | ¿"No determinado entre vulgar y primilla"? ¿O renombrar? | |
| SP057 | Fringilla coelebs/Fringilla montifringilla | ¿"Fringilla sp" o se mantiene el par? | |
| SP077 | MediumRaptor | ¿Lo renombramos? Propuesta: "Rapaz mediana sp" | |
| SP135 | large larus sp | ¿Lo renombramos? Propuesta: "Larus sp (grande)" | **Se acepta tal cual** |

- ¿Las otras 16 entradas "sp." se quedan tal cual? → Respuesta:
  **SÍ. "Revisadas, son correctas. Las acepto todas a la base de datos,
  son nombres genéricos que suelen identificarse así de forma
  recurrente." `revisar` SI→NO en el Excel.**

---

## 3. Lugares y coordenadas

### 3.1 Huso y datum UTM

Para los mapas necesitamos saber en qué sistema están (y estarán)
las coordenadas UTM.

- ¿Huso 30T y datum ETRS89? (es lo habitual en Navarra)
  → Respuesta: **Datum ETRS89 confirmado. Todos los puntos son de
  Navarra → huso 30N. Columnas `datum` y `huso` añadidas al Excel.**

### 3.2 Lindus y Trona

El Excel solo trae los dos puntos de conteo, sin coordenadas ni
municipio.

- UTM X/Y de Lindus: → Respuesta:
- UTM X/Y de Trona: → Respuesta:
- Municipio de cada uno: → Respuesta:

---

## 4. Visitas históricas 2025

Las 98 visitas del Excel no tienen lugar ni observador asignados.

- ¿Todas las jornadas 2025 fueron en Lindus, o hubo días de Trona?
  Si hubo de Trona, ¿cuáles (fechas)? → Respuesta: **Resuelto por
  deducción (decisión #45): el `id_lugar` ya venía en la hoja `meteo`
  por visita. 59 jornadas en Lindus (LUG01) y 38 en Trona (LUG02).
  Falta solo V0001 (2025-07-16), que no tiene meteo: ¿Lindus o Trona?
  → Respuesta:**
- ¿Quién firma como observador del histórico 2025? (¿Gabi en todas,
  o hay jornadas de otra persona?) → Respuesta: **PENDIENTE — no hay
  dato de observador en el Excel, no se puede deducir.**

---

## 5. Vocabularios de los registros nuevos

Para fototrampeo, cuaderno de campo, estudios de campo y rastros de
castor necesitamos cerrar las listas de valores permitidos (igual
que hicimos con comportamiento MIGRADOR/NORTE/LOCAL). Dinos qué
valores usas tú en campo:

| Campo | Pregunta | Respuesta |
|---|---|---|
| fototrampeo → tipo_media | ¿Vale con FOTO / VIDEO? ¿Algo más? | |
| estudio_campo → deteccion | ¿Cómo registras la detección? (¿visual / oído / ambas?) | |
| estudio_campo → migracion | ¿Qué valores usas? (¿sí/no, dirección...?) | |
| estudio_campo → altura | ¿Metros exactos o bandas (p.ej. 0-25, 25-50...)? Si son bandas, ¿cuáles? | |
| estudio_campo → lado | ¿Qué significa "lado"? (¿izquierda/derecha del transecto?) ¿Qué valores? | |
| castor → tipo_rastro | Lista de tipos (¿roeduras, comederos, huellas, excrementos...?) | |
| castor → intensidad_rastro | ¿Qué escala usas? (¿alta/media/baja?) | |
| castor → reciente_antiguo | ¿Solo RECIENTE / ANTIGUO o hay más matices? | |
| castor → aplicacion | ¿Qué es este campo? (¿una app donde lo registras?) | |

---

## 6. Pendiente antiguo: quinto ecosistema de cajas nido

Tenemos cuatro: ZONA_SALVAJE, ZONA_URBANA, PARQUE_CON_RIO,
PARQUE_URBANO.

- ¿Cuál es el quinto? → Respuesta:

---
