# Hoja-guía — Caja nido

Tabla destino: `visitas` + `meteorologia` (opcional) + `cajas_nido`.
Reglas de formato y validación: `docs/Guias/formato-guias.md`.

Una hoja = **una** caja nido. `lugar_caja` es el código exacto del
catálogo (`BAR01`...). Obligatorios de la caja: `ecosistema`,
`especie_arbol`, `estado_nido`, `ocupada`.

Valores cerrados: `ecosistema` ∈ {`ZONA_SALVAJE`, `ZONA_URBANA`,
`PARQUE_CON_RIO`, `PARQUE_URBANO`}; `estado_nido` ∈ {`POCAS_HIERBAS`,
`MUCHAS_HIERBAS`, `CASI_TERMINADO`, `TERMINADO`}; `ocupada` ∈
{`true`, `false`}; `orientacion_caja` ∈ {N, NE, E, SE, S, SW, W, NW}.

## Visita

| tipo_visita | fecha | hora_inicio | hora_fin | lugar_caja | observador | observaciones_visita |
|---|---|---|---|---|---|---|
| CAJA_NIDO |  |  |  |  |  |  |

## Meteorología (opcional)

| hora | temperatura | nubosidad | viento_direccion | viento_intensidad | precipitacion | visibilidad | observaciones |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |

## Caja nido

| especie | ecosistema | especie_arbol | estado_nido | ocupada | numero_huevos | numero_pollos | observaciones |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |

### Campos opcionales (proyecto IB+)

| orientacion_caja | huevos_caliente_frio | peso_pollos | longitud_tarso | numero_anilla | distancia_rio | distancia_peatonal | distancia_carretera | cobertura_vegetal | cobertura_arboles | cobertura_matorral | cobertura_pastizal |
|---|---|---|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |  |  |  |
