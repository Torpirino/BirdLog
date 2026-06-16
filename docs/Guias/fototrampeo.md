# Hoja-guía — Fototrampeo *(borrador)*

Tabla destino: `visitas` + `fototrampeo`.
Reglas de formato y validación: `docs/Guias/formato-guias.md`.

> **Borrador.** El vocabulario cerrado de `tipo_media` está pendiente de
> confirmar con el cliente. Hasta
> entonces `tipo_media` se trata como texto libre. Las imágenes/vídeos
> se registran en la tabla `fotos` (`tabla_origen = 'fototrampeo'`), no
> en esta hoja.

`lugar` ∈ catálogo `lugares` (tipo `FOTOTRAMPEO`). `especie` en singular
del catálogo; si no se identifica, usar `especie_texto`. Fechas en
`YYYY-MM-DD`.

## Visita

| tipo_visita | fecha | hora_inicio | hora_fin | lugar | observador | observaciones_visita |
|---|---|---|---|---|---|---|
| FOTOTRAMPEO |  |  |  |  |  |  |

## Fototrampeo

| especie | especie_texto | fecha_colocacion | fecha_revision | fecha_imagen | tipo_media | numero_imagenes | observaciones |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |
