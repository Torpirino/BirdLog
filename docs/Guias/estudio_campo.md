# Hoja-guía — Estudio de campo (impacto ambiental) *(borrador)*

Tabla destino: `visitas` (tipo `IMPACTO_AMBIENTAL`) + `meteorologia` +
`estudio_campo`.
Reglas de formato y validación: `docs/Guias/formato-guias.md`.

> **Borrador.** Los vocabularios cerrados de `deteccion`, `migracion`,
> `altura` y los lados están pendientes de confirmar con el cliente
> pendientes de confirmar con el cliente. Hasta entonces se tratan como texto
> libre.

La **sesión de muestreo** (punto, hora inicio/fin, meteorología) es la
visita `IMPACTO_AMBIENTAL` + su meteorología. La tabla `estudio_campo`
guarda solo el detalle por detección. `especie` en singular del
catálogo; si no se identifica, usar `especie_texto`.

## Visita (sesión de muestreo)

| tipo_visita | fecha | hora_inicio | hora_fin | lugar | observador | observaciones_visita |
|---|---|---|---|---|---|---|
| IMPACTO_AMBIENTAL |  |  |  |  |  |  |

## Meteorología

| hora | temperatura | nubosidad | viento_direccion | viento_intensidad | precipitacion | visibilidad | observaciones |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |

## Detecciones (una fila por detección)

| especie | especie_texto | numero | deteccion | hora_observacion | distancia_inicial | lado_inicial | distancia_minima | lado_minima | distancia_final | lado_final | vuelo_sobre | direccion_vuelo | migracion | altura | observaciones |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
