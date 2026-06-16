# Hoja-guía — Lindus (conteo migratorio)

Tabla destino: `visitas` + `meteorologia` + `lindus`.
Reglas de formato y validación: `docs/Guias/formato-guias.md`.

Una jornada Lindus se compone de **tres partes**: inicio (abre la
visita), observaciones (filas de aves) y fin (cierra la visita y registra
meteorología). `hora_fin` queda en blanco hasta el cierre.

Reglas clave: `comportamiento` ∈ {`MIGRADOR`, `NORTE`, `LOCAL`};
`especie` en singular del catálogo; `lugar_visita` ∈ catálogo
(`Lindus`, `Trona`); `observador` ∈ catálogo (`Gabi`, `Ander`).

## 1. Inicio de visita

| tipo_visita | fecha | hora_inicio | lugar_visita | observador | observaciones_visita |
|---|---|---|---|---|---|
| LINDUS |  |  |  |  |  |

## 2. Observaciones (una fila por especie + comportamiento)

| especie | hora | numero | comportamiento | edad | sexo | plumaje | observaciones |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |

## 3. Fin de visita

| tipo_visita | fecha | hora_fin | observaciones_visita |
|---|---|---|---|
| LINDUS |  |  |  |

## Meteorología (una fila por hora)

| hora | temperatura | nubosidad | viento_direccion | viento_intensidad | precipitacion | visibilidad | presentes | observando | visitantes | observaciones |
|---|---|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |  |  |  |
