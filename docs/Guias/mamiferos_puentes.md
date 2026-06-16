# Hoja-guía — Mamíferos en puentes

Tabla destino: `visitas` + `meteorologia` (opcional) + `mamiferos_puentes`.
Reglas de formato y validación: `docs/Guias/formato-guias.md`.

Una hoja = **un** puente. `lugar_puente` ∈ catálogo `lugares`. Una fila
por especie detectada. Obligatorios de cada detección: `especie`,
`presencia`.

Valores cerrados: `presencia` ∈ {`PRESENTE`, `AUSENTE`, `POSIBLE`};
`tipo_evidencia` ∈ {`HUELLA`, `EXCREMENTO`, `MADRIGUERA`,
`AVISTAMIENTO`}. `especie` en singular del catálogo (mamíferos por
nombre común: `Nutria paleártica`, `Visón europeo`, `Garduña`,
`Castor europeo`, `Tejón europeo`).

## Visita

| tipo_visita | fecha | hora_inicio | hora_fin | lugar_puente | observador | observaciones_visita | observaciones_puente |
|---|---|---|---|---|---|---|---|
| MAMIFEROS_PUENTES |  |  |  |  |  |  |  |

## Meteorología (opcional)

| hora | temperatura | nubosidad | viento_direccion | viento_intensidad | precipitacion | visibilidad | observaciones |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |

## Detecciones de mamíferos (una fila por especie)

| especie | presencia | tipo_evidencia | observaciones |
|---|---|---|---|
|  |  |  |  |
|  |  |  |  |
