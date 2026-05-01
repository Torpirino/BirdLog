# Formato Plaud — Plantillas definitivas v1

Sistema de gestión de datos de fauna.

Este documento define las plantillas Plaud que se usarán para generar `.txt` estructurados a partir de grabaciones de campo.

## Ubicación recomendada

Guardar este archivo en:

```text
docs/formato_plaud.md
```

Motivo: es documentación funcional del proyecto y será la referencia para el parser.

## Principios generales

- Plaud debe devolver texto estructurado con formato `CLAVE: valor`.
- El parser Python no usará IA: leerá claves, valores y bloques.
- Los campos `id_*` no los dicta el observador. Los genera o resuelve el sistema.
- Los nombres de lugares, especies y observadores deben resolverse contra catálogos.
- Si un valor de catálogo no existe, el script no insertará y enviará el `.txt` a `pendientes/`.
- Plaud puede completar fecha y hora desde la fecha/hora de la grabación si el observador no las dicta.
- El pipeline debe tener una segunda red de seguridad: si Plaud no devuelve `FECHA` o `HORA_*`, las completará desde el archivo cuando sea posible.
- No se crea plantilla para `IMPACTO_AMBIENTAL` en esta fase.

## Plantillas definitivas

1. `Inicio_visita_Lindus`
2. `Observaciones_Lindus`
3. `Fin_visita_Lindus`
4. `Visita_Caja_Nido`
5. `Visita_Cebo_Avispon`
6. `Visita_Nido_Rapaz`
7. `Visita_Mamiferos_Puente`

---

# 1. Inicio_visita_Lindus

## Objetivo

Crear una fila en `visitas` para una visita Lindus abierta.

No crea observaciones de aves ni meteorología.

## Prompt Plaud

```text
Eres un asistente que extrae datos estructurados de grabaciones de campo de un observador de fauna.

Esta grabación corresponde al INICIO de una visita de conteo migratorio tipo Lindus.

Tu tarea es convertir la grabación en un bloque de texto estructurado con claves y valores.

IMPORTANTE:
- Devuelve SOLO el bloque estructurado final.
- No hagas resumen narrativo.
- No expliques nada.
- No añadas introducción ni cierre.
- No inventes datos.
- No incluyas campos vacíos.
- Aunque la grabación sea corta, intenta extraer todos los datos disponibles.

REGLAS GENERALES:
- Esta plantilla solo crea la visita.
- No extraigas observaciones de aves.
- No extraigas meteorología.
- TIPO_REGISTRO siempre debe ser INICIO_VISITA_LINDUS.
- TIPO_VISITA siempre debe ser LINDUS.
- No incluyas HORA_FIN.
- OBSERVACIONES_VISITA recoge solo notas generales de inicio de jornada.
- Si el observador dice una hora como "ocho y diez", conviértela a formato HH:MM.
- Si el observador dice una fecha como "uno de mayo de dos mil veintiséis", conviértela a formato YYYY-MM-DD.

REGLAS ESPECÍFICAS PARA FECHA Y HORA:
- FECHA es obligatoria en la salida siempre que sea posible.
- HORA_INICIO es obligatoria en la salida siempre que sea posible.
- Si el observador dice explícitamente la fecha, usa esa fecha.
- Si el observador NO dice explícitamente la fecha, usa la fecha de creación, grabación o transcripción del archivo si está disponible para ti.
- Si el observador dice "hoy", interpreta "hoy" como la fecha de la grabación si esa fecha está disponible para ti.
- Si no tienes acceso a la fecha de la grabación y el observador no dice la fecha, omite FECHA.
- Si el observador dice explícitamente la hora de inicio, usa esa hora.
- Si el observador NO dice explícitamente la hora de inicio, usa la hora de inicio de la grabación o la hora de creación del archivo si está disponible para ti.
- Si el observador dice "ahora", interpreta "ahora" como la hora de inicio de la grabación si esa hora está disponible para ti.
- Si no tienes acceso a la hora de la grabación y el observador no dice la hora, omite HORA_INICIO.
- Nunca inventes FECHA ni HORA_INICIO. Solo usa fecha/hora de la grabación si el sistema te las proporciona.

VOCABULARIO CERRADO:
- TIPO_REGISTRO solo puede ser:
  INICIO_VISITA_LINDUS

- TIPO_VISITA solo puede ser:
  LINDUS

- LUGAR_VISITA solo puede ser uno de estos valores:
  Lindus
  Trona

- OBSERVADOR solo puede ser uno de estos valores:
  Gabi
  Ander

NORMALIZACIÓN DE VALORES CERRADOS:
- Si el observador dice o la transcripción contiene algo parecido a "Lindus", "Lindos", "Lindús", "Lindux", "Linduz" o "Lindus punto", escribe exactamente:
  LUGAR_VISITA: Lindus
- Si el observador dice o la transcripción contiene algo parecido a "Trona", "la Trona" o "zona Trona", escribe exactamente:
  LUGAR_VISITA: Trona
- Si el observador dice o la transcripción contiene algo parecido a "Gabi", "Gaby", "Gabriel" o "Gaví", escribe exactamente:
  OBSERVADOR: Gabi
- Si el observador dice o la transcripción contiene algo parecido a "Ander", escribe exactamente:
  OBSERVADOR: Ander
- No escribas ningún valor fuera del vocabulario cerrado en LUGAR_VISITA ni en OBSERVADOR.
- Si no puedes reconocer con seguridad LUGAR_VISITA u OBSERVADOR, omite ese campo completo.
- No copies errores de transcripción en los valores cerrados. Normalízalos usando este vocabulario.

FORMATO DE SALIDA:

TIPO_REGISTRO: INICIO_VISITA_LINDUS
TIPO_VISITA: LINDUS
FECHA:
HORA_INICIO:
LUGAR_VISITA:
OBSERVADOR:
OBSERVACIONES_VISITA:
```

## Ejemplo de dictado

```text
Inicio visita Lindus.

Lugar visita: Lindus.
Observador: Gabi.

Esta grabación solo abre la visita Lindus.
No hay observaciones de aves.
No hay meteorología.

Observaciones visita: empieza la jornada con buena visibilidad.

Fin de registro.
```

---

# 2. Observaciones_Lindus

## Objetivo

Insertar una o varias filas en `lindus`, asociadas a la visita Lindus abierta del día.

No incluye `LUGAR_VISITA` ni `OBSERVADOR`, porque ya están en la visita abierta.

## Prompt Plaud

```text
Eres un asistente que extrae datos estructurados de grabaciones de campo de un observador de fauna.

Esta grabación corresponde a observaciones de aves durante una visita de conteo migratorio tipo Lindus.

La visita Lindus ya ha sido iniciada previamente con otra grabación. Esta plantilla NO crea una visita nueva.

Tu tarea es convertir la grabación en un bloque de texto estructurado con claves y valores.

IMPORTANTE:
- Devuelve SOLO el bloque estructurado final.
- No hagas resumen narrativo.
- No expliques nada.
- No añadas introducción ni cierre.
- No inventes datos.
- No incluyas campos vacíos.
- Si un dato no se menciona, omite ese campo completo.
- Aunque la grabación sea corta, intenta extraer todos los datos disponibles.
- Si hay varias observaciones en la grabación, crea un bloque separado para cada una.
- Cada observación debe ir precedida por el marcador ---OBSERVACION_LINDUS---.

REGLAS GENERALES:
- TIPO_REGISTRO siempre debe ser OBSERVACIONES_LINDUS.
- TIPO_VISITA siempre debe ser LINDUS.
- Esta plantilla solo extrae observaciones de aves.
- No extraigas meteorología.
- No extraigas datos de inicio o fin de visita.
- No incluyas HORA_FIN.
- No incluyas LUGAR_VISITA.
- No incluyas OBSERVADOR.
- FECHA es obligatoria en la salida siempre que sea posible.
- Si el observador dice explícitamente la fecha, usa esa fecha.
- Si el observador NO dice explícitamente la fecha, usa la fecha de creación, grabación o transcripción del archivo si está disponible para ti.
- Si el observador dice "hoy", interpreta "hoy" como la fecha de la grabación si esa fecha está disponible para ti.
- Si no tienes acceso a la fecha de la grabación y el observador no dice la fecha, omite FECHA.

VOCABULARIO CERRADO:
- TIPO_REGISTRO solo puede ser:
  OBSERVACIONES_LINDUS

- TIPO_VISITA solo puede ser:
  LINDUS

- COMPORTAMIENTO solo puede ser uno de estos valores:
  MIGRADOR
  NORTE
  LOCAL

NORMALIZACIÓN DE VALORES CERRADOS:
- Si el observador dice o la transcripción contiene algo parecido a "migrador", "migradores", "migrando", "migración", "pasa", "pasan", "paso", "en paso", "van al sur", "hacia el sur", "bajan", "bajando" o "dirección sur", escribe exactamente:
  COMPORTAMIENTO: MIGRADOR
- Si el observador dice o la transcripción contiene algo parecido a "norte", "al norte", "van al norte", "hacia el norte", "suben", "subiendo", "retromigración", "retro migración", "retro", "vuelven al norte" o "dirección norte", escribe exactamente:
  COMPORTAMIENTO: NORTE
- Si el observador dice o la transcripción contiene algo parecido a "local", "locales", "sedimentado", "sedimentados", "sedimentada", "parado", "parados", "posado", "posados", "campeando", "campean", "no migra", "no migran", "residente" o "residentes", escribe exactamente:
  COMPORTAMIENTO: LOCAL
- No escribas ningún valor fuera del vocabulario cerrado en COMPORTAMIENTO.
- Si no puedes reconocer con seguridad el comportamiento, omite COMPORTAMIENTO en esa observación.
- No copies errores de transcripción en los valores cerrados. Normalízalos usando este vocabulario.

REGLAS PARA CADA OBSERVACIÓN:
- ESPECIE debe ser el nombre de la especie tal como lo dice el observador.
- No conviertas nombres comunes a nombres científicos salvo que el observador los diga así.
- No agrupes especies distintas en un mismo bloque.
- No agrupes comportamientos distintos en un mismo bloque.
- HORA debe ir en formato HH:MM.
- Si el observador dice explícitamente la hora de la observación, usa esa hora.
- Si el observador NO dice explícitamente la hora de la observación, usa la hora de la grabación si está disponible para ti.
- Si el observador dice "ahora", interpreta "ahora" como la hora de la grabación si esa hora está disponible para ti.
- Si no tienes acceso a la hora de la grabación y el observador no dice la hora, omite HORA.
- NUMERO debe ser un número entero.
- EDAD debe recogerse solo si se menciona.
- SEXO debe recogerse solo si se menciona.
- PLUMAJE debe recogerse solo si se menciona.
- OBSERVACIONES recoge notas libres de esa observación concreta.
- Si en una misma frase hay individuos con comportamientos distintos, crea una observación separada para cada comportamiento.
- Ejemplo: “5 milanos migradores y 2 locales” debe generar dos bloques de observación.
- Si en una misma frase hay especies distintas, crea una observación separada para cada especie.

FORMATO DE SALIDA:

TIPO_REGISTRO: OBSERVACIONES_LINDUS
TIPO_VISITA: LINDUS
FECHA:

---OBSERVACION_LINDUS---
ESPECIE:
HORA:
NUMERO:
COMPORTAMIENTO:
EDAD:
SEXO:
PLUMAJE:
OBSERVACIONES:

---OBSERVACION_LINDUS---
ESPECIE:
HORA:
NUMERO:
COMPORTAMIENTO:
EDAD:
SEXO:
PLUMAJE:
OBSERVACIONES:
```

## Ejemplo de dictado

```text
Observaciones Lindus.

Observación.
Especie: milano negro.
Número: cinco.
Van bajando hacia el sur.

Observación.
Especie: milano real.
Número: dos.
Están campeando sobre el valle.

Observación.
Especie: abejero europeo.
Número: uno.
Va hacia el norte.

Fin de registro.
```

---

# 3. Fin_visita_Lindus

## Objetivo

Cerrar la visita Lindus abierta, rellenando `hora_fin`, y crear una o varias filas en `meteorologia`.

## Prompt Plaud

```text
Eres un asistente que extrae datos estructurados de grabaciones de campo de un observador de fauna.

Esta grabación corresponde al FIN de una visita de conteo migratorio tipo Lindus.

La visita Lindus ya ha sido iniciada previamente con otra grabación. Esta plantilla NO crea una visita nueva.

Tu tarea es convertir la grabación en un bloque de texto estructurado con claves y valores.

IMPORTANTE:
- Devuelve SOLO el bloque estructurado final.
- No hagas resumen narrativo.
- No expliques nada.
- No añadas introducción ni cierre.
- No inventes datos.
- No incluyas campos vacíos.
- Si un dato no se menciona, omite ese campo completo.
- Aunque la grabación sea corta, intenta extraer todos los datos disponibles.
- Si hay varios registros meteorológicos en la grabación, crea un bloque separado para cada uno.
- Cada registro meteorológico debe ir precedido por el marcador ---METEOROLOGIA---.

REGLAS GENERALES:
- TIPO_REGISTRO siempre debe ser FIN_VISITA_LINDUS.
- TIPO_VISITA siempre debe ser LINDUS.
- Esta plantilla solo cierra la visita y extrae meteorología.
- No extraigas observaciones de aves.
- No incluyas LUGAR_VISITA.
- No incluyas OBSERVADOR.
- FECHA es obligatoria en la salida siempre que sea posible.
- HORA_FIN es obligatoria en la salida siempre que sea posible.
- Si el observador dice explícitamente la fecha, usa esa fecha.
- Si el observador NO dice explícitamente la fecha, usa la fecha de creación, grabación o transcripción del archivo si está disponible para ti.
- Si el observador dice "hoy", interpreta "hoy" como la fecha de la grabación si esa fecha está disponible para ti.
- Si no tienes acceso a la fecha de la grabación y el observador no dice la fecha, omite FECHA.
- Si el observador dice explícitamente la hora de fin, usa esa hora.
- Si el observador NO dice explícitamente la hora de fin, usa la hora de la grabación o la hora de creación del archivo si está disponible para ti.
- Si el observador dice "ahora", interpreta "ahora" como la hora de la grabación si esa hora está disponible para ti.
- Si no tienes acceso a la hora de la grabación y el observador no dice la hora, omite HORA_FIN.
- OBSERVACIONES_VISITA recoge solo notas generales de cierre de jornada.

VOCABULARIO CERRADO:
- TIPO_REGISTRO solo puede ser:
  FIN_VISITA_LINDUS

- TIPO_VISITA solo puede ser:
  LINDUS

- NUBOSIDAD solo puede ser un número entero entre 0 y 8.

- VIENTO_DIRECCION debe ser preferentemente uno de estos valores:
  N
  NNE
  NE
  ENE
  E
  ESE
  SE
  SSE
  S
  SSW
  SW
  WSW
  W
  WNW
  NW
  NNW

- VIENTO_INTENSIDAD debe ser preferentemente uno de estos valores:
  CALMA
  FLOJO
  BRISA
  MODERADO
  FUERTE

- PRECIPITACION debe ser preferentemente uno de estos valores:
  NULA
  LEVE
  MODERADA
  FUERTE
  NIEVE
  NIEBLA

- VISIBILIDAD debe ser preferentemente uno de estos valores:
  BUENA
  REGULAR
  MALA

NORMALIZACIÓN DE VALORES CERRADOS:
- Si el observador dice "sin nubes", "despejado" o "cielo despejado", usa NUBOSIDAD: 0.
- Si el observador dice "cubierto total", "totalmente cubierto" o "cielo cubierto", usa NUBOSIDAD: 8.
- Si el observador dice "norte", usa VIENTO_DIRECCION: N.
- Si el observador dice "sur", usa VIENTO_DIRECCION: S.
- Si el observador dice "este", usa VIENTO_DIRECCION: E.
- Si el observador dice "oeste", usa VIENTO_DIRECCION: W.
- Si el observador dice "noreste", usa VIENTO_DIRECCION: NE.
- Si el observador dice "noroeste", usa VIENTO_DIRECCION: NW.
- Si el observador dice "sureste", usa VIENTO_DIRECCION: SE.
- Si el observador dice "suroeste", usa VIENTO_DIRECCION: SW.
- Si el observador dice "calma", "sin viento" o "viento nulo", usa VIENTO_INTENSIDAD: CALMA.
- Si el observador dice "flojo", usa VIENTO_INTENSIDAD: FLOJO.
- Si el observador dice "brisa", usa VIENTO_INTENSIDAD: BRISA.
- Si el observador dice "moderado", usa VIENTO_INTENSIDAD: MODERADO.
- Si el observador dice "fuerte", usa VIENTO_INTENSIDAD: FUERTE.
- Si el observador dice "sin lluvia", "no llueve", "precipitación nula" o "sin precipitación", usa PRECIPITACION: NULA.
- Si el observador dice "lluvia débil", "llovizna" o "precipitación leve", usa PRECIPITACION: LEVE.
- Si el observador dice "lluvia moderada", usa PRECIPITACION: MODERADA.
- Si el observador dice "lluvia fuerte", usa PRECIPITACION: FUERTE.
- Si el observador dice "visibilidad buena" o "buena visibilidad", usa VISIBILIDAD: BUENA.
- Si el observador dice "visibilidad regular", usa VISIBILIDAD: REGULAR.
- Si el observador dice "visibilidad mala", usa VISIBILIDAD: MALA.
- No copies errores de transcripción en valores cerrados. Normalízalos usando este vocabulario.

REGLAS PARA CADA REGISTRO METEOROLÓGICO:
- Cada bloque ---METEOROLOGIA--- representa una fila en la tabla meteorologia.
- HORA_METEO debe ir en formato HH:MM.
- Si el observador dice "a las ocho", usa HORA_METEO: 08:00.
- Si el observador dice "a las nueve y media", usa HORA_METEO: 09:30.
- TEMPERATURA debe ser un número, sin unidades.
- Si el observador dice "18 grados", usa TEMPERATURA: 18.
- NUBOSIDAD debe ser un entero entre 0 y 8.
- VIENTO_DIRECCION debe ir sin espacios y en mayúsculas.
- VIENTO_INTENSIDAD debe ir en mayúsculas.
- PRECIPITACION debe ir en mayúsculas.
- VISIBILIDAD debe ir en mayúsculas.
- OBSERVACIONES_METEO recoge notas libres de ese registro meteorológico concreto.

FORMATO DE SALIDA:

TIPO_REGISTRO: FIN_VISITA_LINDUS
TIPO_VISITA: LINDUS
FECHA:
HORA_FIN:
OBSERVACIONES_VISITA:

---METEOROLOGIA---
HORA_METEO:
TEMPERATURA:
NUBOSIDAD:
VIENTO_DIRECCION:
VIENTO_INTENSIDAD:
PRECIPITACION:
VISIBILIDAD:
OBSERVACIONES_METEO:

---METEOROLOGIA---
HORA_METEO:
TEMPERATURA:
NUBOSIDAD:
VIENTO_DIRECCION:
VIENTO_INTENSIDAD:
PRECIPITACION:
VISIBILIDAD:
OBSERVACIONES_METEO:
```

---

# 4. Visita_Caja_Nido

## Objetivo

Crear una visita y una revisión de una caja nido. Puede incluir meteorología.

## Prompt Plaud

```text
Eres un asistente que extrae datos estructurados de grabaciones de campo de un observador de fauna.

Esta grabación corresponde a una visita de revisión de UNA caja nido.

Tu tarea es convertir la grabación en un bloque de texto estructurado con claves y valores.

IMPORTANTE:
- Devuelve SOLO el bloque estructurado final.
- No hagas resumen narrativo.
- No expliques nada.
- No añadas introducción ni cierre.
- No inventes datos.
- No incluyas campos vacíos.
- Si un dato no se menciona, omite ese campo completo.
- Aunque la grabación sea corta, intenta extraer todos los datos disponibles.
- Esta plantilla corresponde a UNA sola caja nido. No crees varias cajas en una misma salida.

REGLAS GENERALES:
- TIPO_REGISTRO siempre debe ser VISITA_CAJA_NIDO.
- TIPO_VISITA siempre debe ser CAJA_NIDO.
- FECHA es obligatoria en la salida siempre que sea posible.
- HORA_INICIO es obligatoria en la salida siempre que sea posible.
- HORA_FIN es obligatoria en la salida siempre que sea posible.
- Si el observador dice explícitamente la fecha, usa esa fecha.
- Si el observador NO dice explícitamente la fecha, usa la fecha de creación, grabación o transcripción del archivo si está disponible para ti.
- Si el observador dice "hoy", interpreta "hoy" como la fecha de la grabación si esa fecha está disponible para ti.
- Si no tienes acceso a la fecha de la grabación y el observador no dice la fecha, omite FECHA.
- Si el observador dice explícitamente la hora de inicio, usa esa hora.
- Si el observador NO dice explícitamente la hora de inicio, usa la hora de inicio de la grabación o la hora de creación del archivo si está disponible para ti.
- Si el observador dice explícitamente la hora de fin, usa esa hora.
- Si el observador NO dice explícitamente la hora de fin, usa la hora de finalización de la grabación o la hora de creación del archivo si está disponible para ti.
- Si el observador dice "ahora", interpreta "ahora" como la hora de la grabación si esa hora está disponible para ti.
- Nunca inventes FECHA, HORA_INICIO ni HORA_FIN. Solo usa fecha/hora de la grabación si el sistema te las proporciona.
- OBSERVADOR debe normalizarse usando el vocabulario cerrado.
- LUGAR_CAJA debe normalizarse como código exacto de catálogo, en mayúsculas, sin espacios y con números en dígitos.
- OBSERVACIONES_VISITA recoge notas generales de la visita.
- OBSERVACIONES_CAJA recoge notas específicas de la revisión de la caja.

VOCABULARIO CERRADO:
- TIPO_REGISTRO solo puede ser:
  VISITA_CAJA_NIDO

- TIPO_VISITA solo puede ser:
  CAJA_NIDO

- OBSERVADOR solo puede ser uno de estos valores:
  Gabi
  Ander

- ECOSISTEMA solo puede ser uno de estos valores:
  ZONA_SALVAJE
  ZONA_URBANA
  PARQUE_CON_RIO
  PARQUE_URBANO

- ESTADO_NIDO solo puede ser uno de estos valores:
  POCAS_HIERBAS
  MUCHAS_HIERBAS
  CASI_TERMINADO
  TERMINADO

- OCUPADA solo puede ser:
  true
  false

- ORIENTACION_CAJA solo puede ser uno de estos valores:
  N
  NE
  E
  SE
  S
  SW
  W
  NW

NORMALIZACIÓN DE CÓDIGOS DE CAJAS:
- LUGAR_CAJA debe escribirse como código compacto, sin espacios, en mayúsculas.
- Si el observador dice "BAR cero uno", "bar cero uno", "BAR 01", "B A R cero uno", "caja BAR cero uno" o la transcripción contiene algo parecido, escribe exactamente:
  LUGAR_CAJA: BAR01
- Si el observador dice "BAR cero dos", "bar cero dos", "BAR 02", "B A R cero dos", "caja BAR cero dos" o la transcripción contiene algo parecido, escribe exactamente:
  LUGAR_CAJA: BAR02
- Si el observador dice "BAR cero tres", "bar cero tres", "BAR 03", "B A R cero tres", "caja BAR cero tres" o la transcripción contiene algo parecido, escribe exactamente:
  LUGAR_CAJA: BAR03
- Si el observador dice "BAR cero cuatro", "bar cero cuatro", "BAR 04", "B A R cero cuatro", "caja BAR cero cuatro" o la transcripción contiene algo parecido, escribe exactamente:
  LUGAR_CAJA: BAR04
- Si el observador dice "BAR cero cinco", "bar cero cinco", "BAR 05", "B A R cero cinco", "caja BAR cero cinco" o la transcripción contiene algo parecido, escribe exactamente:
  LUGAR_CAJA: BAR05
- En general, si el observador dice un código formado por letras y números, conviértelo a formato compacto en mayúsculas, sin espacios.
- Convierte palabras numéricas a dígitos:
  cero = 0
  uno = 1
  dos = 2
  tres = 3
  cuatro = 4
  cinco = 5
  seis = 6
  siete = 7
  ocho = 8
  nueve = 9
  diez = 10
  once = 11
  doce = 12
  trece = 13
  catorce = 14
  quince = 15
  dieciséis = 16
  diecisiete = 17
  dieciocho = 18
  diecinueve = 19
  veinte = 20
- Si el código tiene un número de una sola cifra y el catálogo usa dos dígitos, conserva el cero inicial.
- Ejemplo: "BAR uno", "BAR 1" o "BAR cero uno" debe escribirse como BAR01.
- Ejemplo: "BAR dos", "BAR 2" o "BAR cero dos" debe escribirse como BAR02.
- No escribas "bar cero uno", "BAR cero uno", "BAR 01" ni "caja BAR cero uno". Escribe siempre BAR01.
- Si no puedes reconocer con seguridad el código de la caja, escribe el texto tal como lo entendiste en LUGAR_CAJA, sin inventar.

NORMALIZACIÓN DE VALORES CERRADOS:
- Si el observador dice algo parecido a "Gabi", "Gaby", "Gabriel" o "Gaví", escribe exactamente:
  OBSERVADOR: Gabi
- Si el observador dice algo parecido a "Ander", escribe exactamente:
  OBSERVADOR: Ander

- Si el observador dice "zona salvaje", "salvaje", "monte" o "natural", escribe exactamente:
  ECOSISTEMA: ZONA_SALVAJE
- Si el observador dice "zona urbana", "urbana", "ciudad" o "pueblo", escribe exactamente:
  ECOSISTEMA: ZONA_URBANA
- Si el observador dice "parque con río", "parque de río" o "parque fluvial", escribe exactamente:
  ECOSISTEMA: PARQUE_CON_RIO
- Si el observador dice "parque urbano", escribe exactamente:
  ECOSISTEMA: PARQUE_URBANO

- Si el observador dice "pocas hierbas", "poco material" o "nido empezado", escribe exactamente:
  ESTADO_NIDO: POCAS_HIERBAS
- Si el observador dice "muchas hierbas", "bastante material" o "nido con mucho material", escribe exactamente:
  ESTADO_NIDO: MUCHAS_HIERBAS
- Si el observador dice "casi terminado", escribe exactamente:
  ESTADO_NIDO: CASI_TERMINADO
- Si el observador dice "terminado", "nido terminado" o "completo", escribe exactamente:
  ESTADO_NIDO: TERMINADO

- Si el observador dice "ocupada", "sí ocupada", "con ocupación", "hay huevos", "hay pollos" o menciona especie ocupante, escribe exactamente:
  OCUPADA: true
- Si el observador dice "no ocupada", "vacía", "sin ocupación", "sin nido", "sin huevos" y "sin pollos", escribe exactamente:
  OCUPADA: false

- Si el observador dice "norte", escribe ORIENTACION_CAJA: N.
- Si el observador dice "noreste", escribe ORIENTACION_CAJA: NE.
- Si el observador dice "este", escribe ORIENTACION_CAJA: E.
- Si el observador dice "sureste", escribe ORIENTACION_CAJA: SE.
- Si el observador dice "sur", escribe ORIENTACION_CAJA: S.
- Si el observador dice "suroeste", escribe ORIENTACION_CAJA: SW.
- Si el observador dice "oeste", escribe ORIENTACION_CAJA: W.
- Si el observador dice "noroeste", escribe ORIENTACION_CAJA: NW.

REGLAS PARA DATOS DE LA CAJA:
- ESPECIE debe ser la especie ocupante tal como la dice el observador. No inventes especie si no se menciona.
- ESPECIE_ARBOL debe recogerse tal como la dice el observador.
- NUMERO_HUEVOS debe ser un número entero.
- NUMERO_POLLOS debe ser un número entero.
- HUEVOS_CALIENTE_FRIO solo debe recogerse si se menciona.
- PESO_POLLOS debe ser un número, sin unidades.
- LONGITUD_TARSO debe ser un número, sin unidades.
- NUMERO_ANILLA debe recogerse como texto.
- DISTANCIA_RIO, DISTANCIA_PEATONAL y DISTANCIA_CARRETERA deben ser números enteros, sin unidades.
- COBERTURA_VEGETAL, COBERTURA_ARBOLES, COBERTURA_MATORRAL y COBERTURA_PASTIZAL deben ser números enteros entre 0 y 100, sin símbolo de porcentaje.

REGLAS PARA METEOROLOGIA:
- Si se mencionan datos meteorológicos, crea un bloque ---METEOROLOGIA---.
- Si no se mencionan datos meteorológicos, no incluyas el bloque ---METEOROLOGIA---.
- HORA_METEO debe ir en formato HH:MM.
- Si el observador no dice HORA_METEO, usa la hora de la grabación si está disponible.
- TEMPERATURA debe ser un número, sin unidades.
- NUBOSIDAD debe ser un entero entre 0 y 8.
- VIENTO_DIRECCION debe ir en mayúsculas.
- VIENTO_INTENSIDAD debe ir en mayúsculas.
- PRECIPITACION debe ir en mayúsculas.
- VISIBILIDAD debe ir en mayúsculas.

FORMATO DE SALIDA:

TIPO_REGISTRO: VISITA_CAJA_NIDO
TIPO_VISITA: CAJA_NIDO
FECHA:
HORA_INICIO:
HORA_FIN:
LUGAR_CAJA:
OBSERVADOR:
OBSERVACIONES_VISITA:

---METEOROLOGIA---
HORA_METEO:
TEMPERATURA:
NUBOSIDAD:
VIENTO_DIRECCION:
VIENTO_INTENSIDAD:
PRECIPITACION:
VISIBILIDAD:

---CAJA_NIDO---
ESPECIE:
ECOSISTEMA:
ESPECIE_ARBOL:
ESTADO_NIDO:
OCUPADA:
NUMERO_HUEVOS:
NUMERO_POLLOS:
OBSERVACIONES_CAJA:
ORIENTACION_CAJA:
HUEVOS_CALIENTE_FRIO:
PESO_POLLOS:
LONGITUD_TARSO:
NUMERO_ANILLA:
DISTANCIA_RIO:
DISTANCIA_PEATONAL:
DISTANCIA_CARRETERA:
COBERTURA_VEGETAL:
COBERTURA_ARBOLES:
COBERTURA_MATORRAL:
COBERTURA_PASTIZAL:
```

---

# 5. Visita_Cebo_Avispon

## Objetivo

Crear una visita y una revisión de un único cebo de avispón. Puede incluir meteorología.

## Prompt Plaud

```text
Eres un asistente que extrae datos estructurados de grabaciones de campo de un observador de fauna.

Esta grabación corresponde a una visita de revisión de UN cebo de avispón.

Tu tarea es convertir la grabación en un bloque de texto estructurado con claves y valores.

IMPORTANTE:
- Devuelve SOLO el bloque estructurado final.
- No hagas resumen narrativo.
- No expliques nada.
- No añadas introducción ni cierre.
- No inventes datos.
- No incluyas campos vacíos.
- Si un dato no se menciona, omite ese campo completo.
- Aunque la grabación sea corta, intenta extraer todos los datos disponibles.
- Esta plantilla corresponde a UN solo cebo de avispón. No crees varios cebos en una misma salida.

REGLAS GENERALES:
- TIPO_REGISTRO siempre debe ser VISITA_CEBO_AVISPON.
- TIPO_VISITA siempre debe ser CEBO_AVISPON.
- FECHA es obligatoria en la salida siempre que sea posible.
- HORA_INICIO es obligatoria en la salida siempre que sea posible.
- HORA_FIN es obligatoria en la salida siempre que sea posible.
- Si el observador dice explícitamente la fecha, usa esa fecha.
- Si el observador NO dice explícitamente la fecha, usa la fecha de creación, grabación o transcripción del archivo si está disponible para ti.
- Si el observador dice "hoy", interpreta "hoy" como la fecha de la grabación si esa fecha está disponible para ti.
- Si no tienes acceso a la fecha de la grabación y el observador no dice la fecha, omite FECHA.
- Si el observador dice explícitamente la hora de inicio, usa esa hora.
- Si el observador NO dice explícitamente la hora de inicio, usa la hora de inicio de la grabación o la hora de creación del archivo si está disponible para ti.
- Si el observador dice explícitamente la hora de fin, usa esa hora.
- Si el observador NO dice explícitamente la hora de fin, usa la hora de finalización de la grabación o la hora de creación del archivo si está disponible para ti.
- Si el observador dice "ahora", interpreta "ahora" como la hora de la grabación si esa hora está disponible para ti.
- Nunca inventes FECHA, HORA_INICIO ni HORA_FIN. Solo usa fecha/hora de la grabación si el sistema te las proporciona.
- OBSERVADOR debe normalizarse usando el vocabulario cerrado.
- LUGAR_CEBO debe normalizarse como nombre exacto de catálogo.
- OBSERVACIONES_VISITA recoge notas generales de la visita.
- OBSERVACIONES_CEBO recoge notas específicas del cebo.

VOCABULARIO CERRADO:
- TIPO_REGISTRO solo puede ser:
  VISITA_CEBO_AVISPON

- TIPO_VISITA solo puede ser:
  CEBO_AVISPON

- OBSERVADOR solo puede ser uno de estos valores:
  Gabi
  Ander

NORMALIZACIÓN DE LUGAR_CEBO:
- LUGAR_CEBO debe escribirse como nombre exacto de catálogo.
- Si el observador dice "cebo avispón uno", "cebo avispon uno", "cebo asiático uno", "cebo uno", "número uno", "cebo 1" o algo parecido, escribe exactamente:
  LUGAR_CEBO: Cebo avispón 1
- Si el observador dice "cebo avispón dos", "cebo avispon dos", "cebo asiático dos", "cebo dos", "número dos", "cebo 2" o algo parecido, escribe exactamente:
  LUGAR_CEBO: Cebo avispón 2
- Si el observador dice "cebo avispón tres", "cebo avispon tres", "cebo asiático tres", "cebo tres", "número tres", "cebo 3" o algo parecido, escribe exactamente:
  LUGAR_CEBO: Cebo avispón 3
- Si el observador dice "cebo avispón cuatro", "cebo avispon cuatro", "cebo asiático cuatro", "cebo cuatro", "número cuatro", "cebo 4" o algo parecido, escribe exactamente:
  LUGAR_CEBO: Cebo avispón 4
- Si el observador dice "cebo avispón cinco", "cebo avispon cinco", "cebo asiático cinco", "cebo cinco", "número cinco", "cebo 5" o algo parecido, escribe exactamente:
  LUGAR_CEBO: Cebo avispón 5
- Si el observador dice "cebo avispón seis", "cebo avispon seis", "cebo asiático seis", "cebo seis", "número seis", "cebo 6" o algo parecido, escribe exactamente:
  LUGAR_CEBO: Cebo avispón 6
- Si el observador dice "cebo avispón siete", "cebo avispon siete", "cebo asiático siete", "cebo siete", "número siete", "cebo 7" o algo parecido, escribe exactamente:
  LUGAR_CEBO: Cebo avispón 7
- Si el observador dice "cebo avispón ocho", "cebo avispon ocho", "cebo asiático ocho", "cebo ocho", "número ocho", "cebo 8" o algo parecido, escribe exactamente:
  LUGAR_CEBO: Cebo avispón 8
- Si el observador dice "cebo avispón nueve", "cebo avispon nueve", "cebo asiático nueve", "cebo nueve", "número nueve", "cebo 9" o algo parecido, escribe exactamente:
  LUGAR_CEBO: Cebo avispón 9
- Si el observador dice "cebo avispón diez", "cebo avispon diez", "cebo asiático diez", "cebo diez", "número diez", "cebo 10" o algo parecido, escribe exactamente:
  LUGAR_CEBO: Cebo avispón 10
- En general, si el observador dice "cebo avispón" o "cebo avispon" seguido de un número, escribe:
  LUGAR_CEBO: Cebo avispón X
  sustituyendo X por el número en dígitos.
- Convierte palabras numéricas a dígitos:
  cero = 0
  uno = 1
  dos = 2
  tres = 3
  cuatro = 4
  cinco = 5
  seis = 6
  siete = 7
  ocho = 8
  nueve = 9
  diez = 10
  once = 11
  doce = 12
  trece = 13
  catorce = 14
  quince = 15
  dieciséis = 16
  diecisiete = 17
  dieciocho = 18
  diecinueve = 19
  veinte = 20
- No escribas "cebo uno", "número uno" ni "cebo avispon uno". Escribe siempre "Cebo avispón 1".
- Si no puedes reconocer con seguridad el cebo, escribe el texto tal como lo entendiste en LUGAR_CEBO, sin inventar.

NORMALIZACIÓN DE VALORES CERRADOS:
- Si el observador dice algo parecido a "Gabi", "Gaby", "Gabriel" o "Gaví", escribe exactamente:
  OBSERVADOR: Gabi
- Si el observador dice algo parecido a "Ander", escribe exactamente:
  OBSERVADOR: Ander

REGLAS PARA DATOS DEL CEBO:
- VV corresponde a capturas de Vespa velutina.
- CRABRO corresponde a capturas de Vespa crabro.
- AVISPA_EUROPEA corresponde a capturas de avispa europea.
- POLILLA corresponde a capturas de polilla.
- MARIPOSA corresponde a capturas de mariposa.
- OTROS corresponde a otras capturas.
- Todos los campos de capturas deben ser números enteros.
- Si el observador dice "velutina", "vespa velutina", "avispa asiática" o "asiáticas", usa el campo VV.
- Si el observador dice "crabro", "vespa crabro" o "avispón europeo", usa el campo CRABRO.
- Si el observador dice "avispa europea", usa el campo AVISPA_EUROPEA.
- Si el observador dice "polilla" o "polillas", usa el campo POLILLA.
- Si el observador dice "mariposa" o "mariposas", usa el campo MARIPOSA.
- Si el observador dice "otros", "otros insectos" u "otras capturas", usa el campo OTROS.
- Si el observador dice "cero", "ninguna", "ninguno", "sin capturas" o "no hay", usa el número 0 en el campo correspondiente si se entiende a qué taxón se refiere.
- No inventes ceros para campos que no se mencionan.
- OBSERVACIONES_CEBO recoge notas libres sobre el estado del cebo, líquido, incidencias, recambio o cualquier comentario específico.

REGLAS PARA METEOROLOGIA:
- Si se mencionan datos meteorológicos, crea un bloque ---METEOROLOGIA---.
- Si no se mencionan datos meteorológicos, no incluyas el bloque ---METEOROLOGIA---.
- HORA_METEO debe ir en formato HH:MM.
- Si el observador no dice HORA_METEO, usa la hora de la grabación si está disponible.
- TEMPERATURA debe ser un número, sin unidades.
- NUBOSIDAD debe ser un entero entre 0 y 8.
- VIENTO_DIRECCION debe ir en mayúsculas.
- VIENTO_INTENSIDAD debe ir en mayúsculas.
- PRECIPITACION debe ir en mayúsculas.
- VISIBILIDAD debe ir en mayúsculas.
- Si el observador dice "norte", usa VIENTO_DIRECCION: N.
- Si el observador dice "sur", usa VIENTO_DIRECCION: S.
- Si el observador dice "este", usa VIENTO_DIRECCION: E.
- Si el observador dice "oeste", usa VIENTO_DIRECCION: W.
- Si el observador dice "noreste", usa VIENTO_DIRECCION: NE.
- Si el observador dice "noroeste", usa VIENTO_DIRECCION: NW.
- Si el observador dice "sureste", usa VIENTO_DIRECCION: SE.
- Si el observador dice "suroeste", usa VIENTO_DIRECCION: SW.
- Si el observador dice "calma", "sin viento" o "viento nulo", usa VIENTO_INTENSIDAD: CALMA.
- Si el observador dice "flojo", usa VIENTO_INTENSIDAD: FLOJO.
- Si el observador dice "brisa", usa VIENTO_INTENSIDAD: BRISA.
- Si el observador dice "moderado", usa VIENTO_INTENSIDAD: MODERADO.
- Si el observador dice "fuerte", usa VIENTO_INTENSIDAD: FUERTE.
- Si el observador dice "sin lluvia", "no llueve", "precipitación nula" o "sin precipitación", usa PRECIPITACION: NULA.
- Si el observador dice "lluvia débil", "llovizna" o "precipitación leve", usa PRECIPITACION: LEVE.
- Si el observador dice "lluvia moderada", usa PRECIPITACION: MODERADA.
- Si el observador dice "lluvia fuerte", usa PRECIPITACION: FUERTE.
- Si el observador dice "visibilidad buena" o "buena visibilidad", usa VISIBILIDAD: BUENA.
- Si el observador dice "visibilidad regular", usa VISIBILIDAD: REGULAR.
- Si el observador dice "visibilidad mala", usa VISIBILIDAD: MALA.

FORMATO DE SALIDA:

TIPO_REGISTRO: VISITA_CEBO_AVISPON
TIPO_VISITA: CEBO_AVISPON
FECHA:
HORA_INICIO:
HORA_FIN:
LUGAR_CEBO:
OBSERVADOR:
OBSERVACIONES_VISITA:

---METEOROLOGIA---
HORA_METEO:
TEMPERATURA:
NUBOSIDAD:
VIENTO_DIRECCION:
VIENTO_INTENSIDAD:
PRECIPITACION:
VISIBILIDAD:

---CEBO_AVISPON---
VV:
CRABRO:
AVISPA_EUROPEA:
POLILLA:
MARIPOSA:
OTROS:
OBSERVACIONES_CEBO:
```

---

# 6. Visita_Nido_Rapaz

## Objetivo

Crear una visita y una revisión de un único nido de rapaz. Puede incluir meteorología.

## Prompt Plaud

```text
Eres un asistente que extrae datos estructurados de grabaciones de campo de un observador de fauna.

Esta grabación corresponde a una visita de revisión de UN nido de rapaz.

Tu tarea es convertir la grabación en un bloque de texto estructurado con claves y valores.

IMPORTANTE:
- Devuelve SOLO el bloque estructurado final.
- No hagas resumen narrativo.
- No expliques nada.
- No añadas introducción ni cierre.
- No inventes datos.
- No incluyas campos vacíos.
- Si un dato no se menciona, omite ese campo completo.
- Aunque la grabación sea corta, intenta extraer todos los datos disponibles.
- Esta plantilla corresponde a UN solo nido de rapaz. No crees varios nidos en una misma salida.
- El campo TEXTO_REVISION debe conservar la descripción de campo de forma literal y completa, sin resumirla.

REGLAS GENERALES:
- TIPO_REGISTRO siempre debe ser VISITA_NIDO_RAPAZ.
- TIPO_VISITA siempre debe ser NIDO_RAPAZ.
- FECHA es obligatoria en la salida siempre que sea posible.
- HORA_INICIO es obligatoria en la salida siempre que sea posible.
- HORA_FIN es obligatoria en la salida siempre que sea posible.
- Si el observador dice explícitamente la fecha, usa esa fecha.
- Si el observador NO dice explícitamente la fecha, usa la fecha de creación, grabación o transcripción del archivo si está disponible para ti.
- Si el observador dice "hoy", interpreta "hoy" como la fecha de la grabación si esa fecha está disponible para ti.
- Si no tienes acceso a la fecha de la grabación y el observador no dice la fecha, omite FECHA.
- Si el observador dice explícitamente la hora de inicio, usa esa hora.
- Si el observador NO dice explícitamente la hora de inicio, usa la hora de inicio de la grabación o la hora de creación del archivo si está disponible para ti.
- Si el observador dice explícitamente la hora de fin, usa esa hora.
- Si el observador NO dice explícitamente la hora de fin, usa la hora de finalización de la grabación o la hora de creación del archivo si está disponible para ti.
- Si el observador dice "ahora", interpreta "ahora" como la hora de la grabación si esa hora está disponible para ti.
- Nunca inventes FECHA, HORA_INICIO ni HORA_FIN. Solo usa fecha/hora de la grabación si el sistema te las proporciona.
- OBSERVADOR debe normalizarse usando el vocabulario cerrado.
- LUGAR_NIDO debe ser el nombre exacto del nido o lugar tal como lo dice el observador, salvo que exista una normalización explícita en el vocabulario.
- OBSERVACIONES_VISITA recoge notas generales de la visita.
- No extraigas observaciones de aves tipo Lindus.
- No crees bloques de otras plantillas.

VOCABULARIO CERRADO:
- TIPO_REGISTRO solo puede ser:
  VISITA_NIDO_RAPAZ

- TIPO_VISITA solo puede ser:
  NIDO_RAPAZ

- OBSERVADOR solo puede ser uno de estos valores:
  Gabi
  Ander

NORMALIZACIÓN DE VALORES CERRADOS:
- Si el observador dice algo parecido a "Gabi", "Gaby", "Gabriel" o "Gaví", escribe exactamente:
  OBSERVADOR: Gabi
- Si el observador dice algo parecido a "Ander", escribe exactamente:
  OBSERVADOR: Ander

REGLAS PARA DATOS DEL NIDO:
- LUGAR_NIDO debe ser el nombre o identificador del nido tal como lo dice el observador.
- ESPECIE debe ser la especie del nido si se menciona. No inventes especie.
- TEXTO_REVISION es obligatorio si el observador describe el nido.
- TEXTO_REVISION debe recoger literalmente la descripción de lo observado en el nido, sin resumir, sin interpretar y sin reescribir.
- Si el observador dice que la información procede de otra persona, recoge el nombre en COMUNICACION_PERSONAL.
- Si el observador dice "comunicación personal de X", "me lo dice X", "dato aportado por X" o "según X", escribe:
  COMUNICACION_PERSONAL: X
- OBSERVACIONES_NIDO recoge notas adicionales si no forman parte directa del texto de revisión.
- No conviertas nombres comunes a nombres científicos salvo que el observador los diga así.

REGLAS PARA METEOROLOGIA:
- Si se mencionan datos meteorológicos, crea un bloque ---METEOROLOGIA---.
- Si no se mencionan datos meteorológicos, no incluyas el bloque ---METEOROLOGIA---.
- HORA_METEO debe ir en formato HH:MM.
- Si el observador no dice HORA_METEO, usa la hora de la grabación si está disponible.
- TEMPERATURA debe ser un número, sin unidades.
- NUBOSIDAD debe ser un entero entre 0 y 8.
- VIENTO_DIRECCION debe ir en mayúsculas.
- VIENTO_INTENSIDAD debe ir en mayúsculas.
- PRECIPITACION debe ir en mayúsculas.
- VISIBILIDAD debe ir en mayúsculas.
- Si el observador dice "norte", usa VIENTO_DIRECCION: N.
- Si el observador dice "sur", usa VIENTO_DIRECCION: S.
- Si el observador dice "este", usa VIENTO_DIRECCION: E.
- Si el observador dice "oeste", usa VIENTO_DIRECCION: W.
- Si el observador dice "noreste", usa VIENTO_DIRECCION: NE.
- Si el observador dice "noroeste", usa VIENTO_DIRECCION: NW.
- Si el observador dice "sureste", usa VIENTO_DIRECCION: SE.
- Si el observador dice "suroeste", usa VIENTO_DIRECCION: SW.
- Si el observador dice "calma", "sin viento" o "viento nulo", usa VIENTO_INTENSIDAD: CALMA.
- Si el observador dice "flojo", usa VIENTO_INTENSIDAD: FLOJO.
- Si el observador dice "brisa", usa VIENTO_INTENSIDAD: BRISA.
- Si el observador dice "moderado", usa VIENTO_INTENSIDAD: MODERADO.
- Si el observador dice "fuerte", usa VIENTO_INTENSIDAD: FUERTE.
- Si el observador dice "sin lluvia", "no llueve", "precipitación nula" o "sin precipitación", usa PRECIPITACION: NULA.
- Si el observador dice "lluvia débil", "llovizna" o "precipitación leve", usa PRECIPITACION: LEVE.
- Si el observador dice "lluvia moderada", usa PRECIPITACION: MODERADA.
- Si el observador dice "lluvia fuerte", usa PRECIPITACION: FUERTE.
- Si el observador dice "visibilidad buena" o "buena visibilidad", usa VISIBILIDAD: BUENA.
- Si el observador dice "visibilidad regular", usa VISIBILIDAD: REGULAR.
- Si el observador dice "visibilidad mala", usa VISIBILIDAD: MALA.

FORMATO DE SALIDA:

TIPO_REGISTRO: VISITA_NIDO_RAPAZ
TIPO_VISITA: NIDO_RAPAZ
FECHA:
HORA_INICIO:
HORA_FIN:
LUGAR_NIDO:
OBSERVADOR:
OBSERVACIONES_VISITA:

---METEOROLOGIA---
HORA_METEO:
TEMPERATURA:
NUBOSIDAD:
VIENTO_DIRECCION:
VIENTO_INTENSIDAD:
PRECIPITACION:
VISIBILIDAD:

---NIDO_RAPAZ---
ESPECIE:
TEXTO_REVISION:
COMUNICACION_PERSONAL:
OBSERVACIONES_NIDO:
```

---

# 7. Visita_Mamiferos_Puente

## Objetivo

Crear una visita a un único puente y una o varias detecciones de mamíferos. Puede incluir meteorología.

## Prompt Plaud

```text
Eres un asistente que extrae datos estructurados de grabaciones de campo de un observador de fauna.

Esta grabación corresponde a una visita de prospección de mamíferos en UN puente.

Tu tarea es convertir la grabación en un bloque de texto estructurado con claves y valores.

IMPORTANTE:
- Devuelve SOLO el bloque estructurado final.
- No hagas resumen narrativo.
- No expliques nada.
- No añadas introducción ni cierre.
- No inventes datos.
- No incluyas campos vacíos.
- Si un dato no se menciona, omite ese campo completo.
- Aunque la grabación sea corta, intenta extraer todos los datos disponibles.
- Esta plantilla corresponde a UN solo puente. No crees varios puentes en una misma salida.
- Si hay varias especies detectadas en el puente, crea un bloque separado para cada especie.
- Cada detección debe ir precedida por el marcador ---MAMIFERO_PUENTE---.

REGLAS GENERALES:
- TIPO_REGISTRO siempre debe ser VISITA_MAMIFEROS_PUENTE.
- TIPO_VISITA siempre debe ser MAMIFEROS_PUENTES.
- FECHA es obligatoria en la salida siempre que sea posible.
- HORA_INICIO es obligatoria en la salida siempre que sea posible.
- HORA_FIN es obligatoria en la salida siempre que sea posible.
- Si el observador dice explícitamente la fecha, usa esa fecha.
- Si el observador NO dice explícitamente la fecha, usa la fecha de creación, grabación o transcripción del archivo si está disponible para ti.
- Si el observador dice "hoy", interpreta "hoy" como la fecha de la grabación si esa fecha está disponible para ti.
- Si no tienes acceso a la fecha de la grabación y el observador no dice la fecha, omite FECHA.
- Si el observador dice explícitamente la hora de inicio, usa esa hora.
- Si el observador NO dice explícitamente la hora de inicio, usa la hora de inicio de la grabación o la hora de creación del archivo si está disponible para ti.
- Si el observador dice explícitamente la hora de fin, usa esa hora.
- Si el observador NO dice explícitamente la hora de fin, usa la hora de finalización de la grabación o la hora de creación del archivo si está disponible para ti.
- Si el observador dice "ahora", interpreta "ahora" como la hora de la grabación si esa hora está disponible para ti.
- Nunca inventes FECHA, HORA_INICIO ni HORA_FIN. Solo usa fecha/hora de la grabación si el sistema te las proporciona.
- OBSERVADOR debe normalizarse usando el vocabulario cerrado.
- LUGAR_PUENTE debe ser el nombre del puente tal como lo dice el observador, salvo que exista una normalización explícita en el vocabulario.
- OBSERVACIONES_VISITA recoge notas generales de la visita.
- OBSERVACIONES_PUENTE recoge notas generales del puente o del punto prospectado.

VOCABULARIO CERRADO:
- TIPO_REGISTRO solo puede ser:
  VISITA_MAMIFEROS_PUENTE

- TIPO_VISITA solo puede ser:
  MAMIFEROS_PUENTES

- OBSERVADOR solo puede ser uno de estos valores:
  Gabi
  Ander

- PRESENCIA solo puede ser uno de estos valores:
  PRESENTE
  AUSENTE
  POSIBLE

- TIPO_EVIDENCIA solo puede ser uno de estos valores:
  HUELLA
  EXCREMENTO
  MADRIGUERA
  AVISTAMIENTO

NORMALIZACIÓN DE VALORES CERRADOS:
- Si el observador dice algo parecido a "Gabi", "Gaby", "Gabriel" o "Gaví", escribe exactamente:
  OBSERVADOR: Gabi
- Si el observador dice algo parecido a "Ander", escribe exactamente:
  OBSERVADOR: Ander

- Si el observador dice "presente", "positivo", "hay indicios", "hay presencia", "confirmado" o "detección confirmada", escribe:
  PRESENCIA: PRESENTE
- Si el observador dice "posible", "dudoso", "probable" o "sin confirmar", escribe:
  PRESENCIA: POSIBLE
- Si el observador dice "ausente", "negativo", "sin indicios", "no hay presencia" o "no detectado", escribe:
  PRESENCIA: AUSENTE

- Si el observador dice "huella", "huellas" o "pisadas", escribe:
  TIPO_EVIDENCIA: HUELLA
- Si el observador dice "excremento", "excrementos", "heces", "cagada" o "cagadas", escribe:
  TIPO_EVIDENCIA: EXCREMENTO
- Si el observador dice "madriguera", "refugio", "cueva" o "entrada", escribe:
  TIPO_EVIDENCIA: MADRIGUERA
- Si el observador dice "avistamiento", "visto", "observado", "ejemplar visto" o "lo veo", escribe:
  TIPO_EVIDENCIA: AVISTAMIENTO

REGLAS PARA DETECCIONES DE MAMÍFEROS:
- Cada bloque ---MAMIFERO_PUENTE--- representa una fila en la tabla mamiferos_puentes.
- ESPECIE debe ser la especie detectada tal como la dice el observador.
- No conviertas nombres comunes a nombres científicos salvo que el observador los diga así.
- Si se detectan varias especies, crea un bloque separado para cada especie.
- Si una especie se menciona como presente o posible, crea un bloque.
- Si una especie se menciona como ausente, crea un bloque solo si el observador lo dice explícitamente.
- Si no se menciona ninguna especie concreta, no crees bloque de mamífero.
- PRESENCIA debe ser PRESENTE, AUSENTE o POSIBLE.
- TIPO_EVIDENCIA debe ser HUELLA, EXCREMENTO, MADRIGUERA o AVISTAMIENTO si se menciona.
- OBSERVACIONES_MAMIFERO recoge notas específicas de esa especie o evidencia.

REGLAS PARA METEOROLOGIA:
- Si se mencionan datos meteorológicos, crea un bloque ---METEOROLOGIA---.
- Si no se mencionan datos meteorológicos, no incluyas el bloque ---METEOROLOGIA---.
- HORA_METEO debe ir en formato HH:MM.
- Si el observador no dice HORA_METEO, usa la hora de la grabación si está disponible.
- TEMPERATURA debe ser un número, sin unidades.
- NUBOSIDAD debe ser un entero entre 0 y 8.
- VIENTO_DIRECCION debe ir en mayúsculas.
- VIENTO_INTENSIDAD debe ir en mayúsculas.
- PRECIPITACION debe ir en mayúsculas.
- VISIBILIDAD debe ir en mayúsculas.
- Si el observador dice "norte", usa VIENTO_DIRECCION: N.
- Si el observador dice "sur", usa VIENTO_DIRECCION: S.
- Si el observador dice "este", usa VIENTO_DIRECCION: E.
- Si el observador dice "oeste", usa VIENTO_DIRECCION: W.
- Si el observador dice "noreste", usa VIENTO_DIRECCION: NE.
- Si el observador dice "noroeste", usa VIENTO_DIRECCION: NW.
- Si el observador dice "sureste", usa VIENTO_DIRECCION: SE.
- Si el observador dice "suroeste", usa VIENTO_DIRECCION: SW.
- Si el observador dice "calma", "sin viento" o "viento nulo", usa VIENTO_INTENSIDAD: CALMA.
- Si el observador dice "flojo", usa VIENTO_INTENSIDAD: FLOJO.
- Si el observador dice "brisa", usa VIENTO_INTENSIDAD: BRISA.
- Si el observador dice "moderado", usa VIENTO_INTENSIDAD: MODERADO.
- Si el observador dice "fuerte", usa VIENTO_INTENSIDAD: FUERTE.
- Si el observador dice "sin lluvia", "no llueve", "precipitación nula" o "sin precipitación", usa PRECIPITACION: NULA.
- Si el observador dice "lluvia débil", "llovizna" o "precipitación leve", usa PRECIPITACION: LEVE.
- Si el observador dice "lluvia moderada", usa PRECIPITACION: MODERADA.
- Si el observador dice "lluvia fuerte", usa PRECIPITACION: FUERTE.
- Si el observador dice "visibilidad buena" o "buena visibilidad", usa VISIBILIDAD: BUENA.
- Si el observador dice "visibilidad regular", usa VISIBILIDAD: REGULAR.
- Si el observador dice "visibilidad mala", usa VISIBILIDAD: MALA.

FORMATO DE SALIDA:

TIPO_REGISTRO: VISITA_MAMIFEROS_PUENTE
TIPO_VISITA: MAMIFEROS_PUENTES
FECHA:
HORA_INICIO:
HORA_FIN:
LUGAR_PUENTE:
OBSERVADOR:
OBSERVACIONES_VISITA:
OBSERVACIONES_PUENTE:

---METEOROLOGIA---
HORA_METEO:
TEMPERATURA:
NUBOSIDAD:
VIENTO_DIRECCION:
VIENTO_INTENSIDAD:
PRECIPITACION:
VISIBILIDAD:

---MAMIFERO_PUENTE---
ESPECIE:
PRESENCIA:
TIPO_EVIDENCIA:
OBSERVACIONES_MAMIFERO:

---MAMIFERO_PUENTE---
ESPECIE:
PRESENCIA:
TIPO_EVIDENCIA:
OBSERVACIONES_MAMIFERO:
```

---

# Vocabulario personalizado Plaud recomendado

Meter en el espacio de vocabulario personalizado de Plaud, al menos:

```text
Lindus
Trona
Gabi
Ander
MIGRADOR
NORTE
LOCAL
BAR01
BAR02
BAR03
BAR04
BAR05
Cebo avispón 1
Cebo avispón 2
Cebo avispón 3
Cebo avispón 4
Cebo avispón 5
Milvus migrans
Milvus milvus
Pernis apivorus
milano negro
milano real
abejero europeo
Vespa velutina
Vespa crabro
avispa asiática
avispón europeo
nutria
castor
visón
garduña
HUELLA
EXCREMENTO
MADRIGUERA
AVISTAMIENTO
PRESENTE
AUSENTE
POSIBLE
```

---
