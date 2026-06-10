# Revisar con Gabi

Preguntas pendientes para cerrar la base de datos y poder importar
el histórico 2025 del Excel (`BirdLog_tablas_cliente_v03.xlsx`).
Fecha: 2026-06-10.

Cómo usarlo: responde debajo de cada pregunta o en la columna
"Respuesta" de las tablas. Si algo no se sabe, escribir
"desconocido" también es una respuesta válida.

---

## 1. Meteorología: valores que parecen erróneos

No vamos a corregir ningún valor medido por nuestra cuenta.
Necesitamos que confirmes el valor correcto (o que lo marques como
desconocido y lo dejaremos vacío).

### 1.1 Bloque desplazado del 2025-09-05 (visita V0043)

En las filas **M0464 a M0478** (de 05:50 a 20:30), la columna
`humedad_relativa` contiene valores entre 1026 y 1028.7, que parecen
ser la **presión atmosférica**.

- ¿Confirmas que esos valores son la presión? → Respuesta:
- ¿Tienes la humedad real de ese día en alguna parte (cuaderno,
  app, foto de la estación)? → Respuesta:

### 1.2 Valores sueltos fuera de rango

| Fila | Fecha | Hora | Valor en el Excel | ¿Era esto? | Respuesta |
|---|---|---|---|---|---|
| M0217 | 2025-08-11 | 04:50 | presión 1929.8 | ¿1029.8? | |
| M0733 | 2025-10-02 | 15:00 | presión 10289 | ¿1028.9? | |
| M0864 | 2025-10-16 | 16:00 | humedad 786 | ¿78.6? | |
| M0906 | 2025-10-20 | 13:00 | presión 101631 | ¿1016.31? | |
| M0991 | 2025-10-31 | 12:00 | presión 10191 | ¿1019.1? | |
| M1002 | 2025-11-02 | 06:45 | temperatura 68 | ¿6.8? | |
| M1006 | 2025-11-02 | 11:00 | humedad 818 | ¿81.8? | |
| M1039 | 2025-11-10 | 11:00 | temperatura 95 | ¿9.5? | |
| M1045 | 2025-11-11 | 07:00 | humedad 7302 | ¿73.02? | |

---

## 2. Catálogo de especies

### 2.1 Grupo y nombre común

Las 135 especies del Excel vienen sin `nombre_comun` y sin `grupo`.
El grupo es obligatorio para los gráficos del dashboard y solo admite
estos valores: **RAPAZ, PASERIFORME, ACUATICA, INVERTEBRADO,
MAMIFERO, OTRO**.

- ¿Puedes completar las dos columnas en el propio Excel?
  → Respuesta:
- Si prefieres, podemos proponerte nosotros una asignación de grupo
  y tú solo la revisas. ¿Te encaja? → Respuesta:

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
| SP135 | large larus sp | ¿Lo renombramos? Propuesta: "Larus sp (grande)" | |

- ¿Las otras 16 entradas "sp." se quedan tal cual? → Respuesta:

---

## 3. Lugares y coordenadas

### 3.1 Huso y datum UTM

Para los mapas necesitamos saber en qué sistema están (y estarán)
las coordenadas UTM.

- ¿Huso 30T y datum ETRS89? (es lo habitual en Navarra)
  → Respuesta:

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
  Si hubo de Trona, ¿cuáles (fechas)? → Respuesta:
- ¿Quién firma como observador del histórico 2025? (¿Gabi en todas,
  o hay jornadas de otra persona?) → Respuesta:

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

## 7. Forma de trabajar a partir de ahora

Importante para no acabar con dos versiones de los datos: el Excel
nos sirve para cargar el histórico 2025 **una sola vez**. A partir
de ahí, los datos nuevos entran por el Plaud → pipeline → Supabase,
y se consultan en el dashboard.

- ¿De acuerdo en no seguir rellenando las hojas del Excel una vez
  importado el histórico? → Respuesta:
