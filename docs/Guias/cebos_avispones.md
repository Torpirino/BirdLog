# Hoja-guía — Cebo de avispón

Tabla destino: `visitas` + `meteorologia` (opcional) + `cebos_avispones`.
Reglas de formato y validación: `docs/Guias/formato-guias.md`.

Una hoja = **un** cebo. `lugar_cebo` es el nombre exacto del catálogo
(`Cebo avispón 1`...). Debe haber **al menos una captura o una nota** en
`observaciones`. Capturas como enteros (`vv` = Vespa velutina, `crabro` =
Vespa crabro). `fecha_colocacion` en `YYYY-MM-DD`. `utm_x_nido`/
`utm_y_nido` solo si se localiza un nido de velutina (enteros, ETRS89/30N).

## Visita

| tipo_visita | fecha | hora_inicio | hora_fin | lugar_cebo | observador | observaciones_visita |
|---|---|---|---|---|---|---|
| CEBO_AVISPON |  |  |  |  |  |  |

## Meteorología (opcional)

| hora | temperatura | nubosidad | viento_direccion | viento_intensidad | precipitacion | visibilidad | observaciones |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |

## Cebo de avispón

| vv | crabro | avispa_europea | polilla | mariposa | otros | numero_trampa | fecha_colocacion | utm_x_nido | utm_y_nido | observaciones |
|---|---|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |  |  |
