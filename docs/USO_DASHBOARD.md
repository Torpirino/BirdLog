# Uso del dashboard BirdLog

Este documento explica cómo usar el dashboard local de BirdLog. Está pensado
para consultar, revisar y corregir datos de observación de fauna sin publicar
nada en internet.

## Qué es

El dashboard BirdLog es una aplicación local hecha con Streamlit. Se conecta al
Supabase configurado en el proyecto y permite ver visitas, mapas, gráficos,
fotos y tablas de trabajo. También permite añadir, editar y borrar registros
desde la página **Edición / Catálogos**.

El dashboard no oculta coordenadas porque está pensado para uso interno del
observador.

## Cómo arrancarlo

Abre una terminal en la carpeta del proyecto y activa el entorno virtual:

```bash
source .venv/bin/activate
```

Arranca Streamlit:

```bash
streamlit run dashboard/app.py
```

La URL local habitual es:

```text
http://localhost:8501
```

Si ese puerto está ocupado, Streamlit puede abrir otro parecido y lo indicará
en la terminal.

## Variables necesarias

Las credenciales se leen desde `.env`. No hace falta escribirlas en el
dashboard.

No edites `.env` salvo que sepas exactamente qué estás cambiando. No subas
`.env`, credenciales, backups ni datos sensibles a git.

## Páginas del dashboard

### Inicio / Resumen

Muestra una visión rápida del sistema: visitas, última visita, especies,
lugares, observaciones Lindus, cajas ocupadas, capturas de avispones y
mamíferos detectados. También incluye gráficos y últimos registros.

Si todavía no hay datos suficientes, verás mensajes tipo "Sin datos".

### Mapa general

Muestra los lugares en un mapa con capas por tipo: cajas nido, nidos rapaces,
cebos de avispones, puentes y puntos de conteo migratorio. Usa las coordenadas
UTM de la tabla `lugares` y las transforma para el mapa.

Si un lugar no tiene coordenadas válidas, se omite del mapa para no romper la
vista.

### Lindus

Permite consultar observaciones Lindus con filtros por fecha, especie,
comportamiento, observador, lugar, hora y número de individuos. Incluye tabla,
detalle de observación, meteorología asociada y fotos si existen.

### Cajas nido

Permite revisar ocupación, huevos, pollos, estado del nido, ecosistema, árbol,
evolución temporal, mapa de cajas y fotos asociadas.

### Nidos rapaces

Está orientada a leer el histórico de cada nido. Muestra revisiones, ficha
detallada, texto de revisión, comunicación personal, mapa y fotos asociadas.

### Cebos avispones

Muestra totales de `vv`, `crabro` y otras capturas, composición, ranking de
cebos, evolución temporal y acumulados calculados en el dashboard. No se crean
campos nuevos en la base de datos para esos acumulados.

### Mamíferos puentes

Ayuda a ver dónde aparece cada especie de mamífero y con qué evidencia:
huella, excremento, madriguera o avistamiento. Incluye mapa, tabla, ranking de
puentes por diversidad y resumen por presencia.

### Edición / Catálogos

Permite ver, añadir, editar y borrar registros de:

- `especies`
- `observadores`
- `lugares`
- `visitas`
- `meteorologia`
- `lindus`
- `cajas_nido`
- `nidos_rapaces`
- `cebos_avispones`
- `mamiferos_puentes`
- `fotos`

Esta página modifica datos de Supabase. Úsala con calma.

## Cómo usar filtros

Los filtros aparecen en bloques visibles dentro de cada página. Puedes combinar
varios a la vez: fecha, especie, lugar, tipo de visita, comportamiento,
presencia o rangos numéricos.

Si un filtro deja la tabla sin resultados, no significa que haya un error:
simplemente no hay registros que cumplan esa combinación.

## Cómo ver fotos

Cuando un registro tiene fotos asociadas, el dashboard muestra enlaces de
Google Drive. El dashboard no descarga las fotos ni guarda copias nuevas; solo
abre el enlace registrado en la tabla `fotos`.

## Añadir registros

En **Edición / Catálogos**:

1. Selecciona la tabla.
2. Elige la acción **Añadir**.
3. Rellena el formulario.
4. Revisa los campos obligatorios marcados con `*`.
5. Pulsa **Validar y guardar**.

Las claves foráneas se muestran con nombres legibles cuando es posible, por
ejemplo nombre de especie, lugar, observador o visita.

## Editar registros

En **Edición / Catálogos**:

1. Selecciona la tabla.
2. Elige la acción **Editar**.
3. Selecciona el registro.
4. Corrige los campos necesarios.
5. Marca la confirmación.
6. Pulsa **Guardar cambios**.

No se puede cambiar manualmente el ID principal del registro.

## Borrar registros con seguridad

El borrado está protegido para evitar accidentes:

1. Selecciona la tabla.
2. Elige la acción **Borrar**.
3. Selecciona el registro.
4. Lee el resumen mostrado.
5. Revisa el aviso de seguridad.
6. Escribe exactamente `BORRAR`.
7. Pulsa el botón final de borrado.

Antes de borrar, el dashboard intenta crear un backup CSV local en `backups/`
y una traza mínima en `backups/edicion_traza.log`.

No uses el borrado salvo que sea necesario. Si Supabase avisa de dependencias,
no fuerces el borrado desde fuera del dashboard.

## Si Supabase está pausado o no responde

En el plan gratuito Supabase puede pausarse tras varios días sin actividad. Si
el dashboard muestra un mensaje de pausa o conexión fallida:

1. Entra en supabase.com.
2. Reactiva el proyecto.
3. Espera unos minutos.
4. Recarga el dashboard.

Si el error menciona permisos o clave inválida, revisa la configuración de
`.env` sin copiar ni compartir las claves.

Si al añadir un registro aparece un error sobre una columna `id_*` que no se
autogenera, no escribas el ID a mano. La base de datos debe corregirse para que
Supabase genere esos IDs automáticamente.

## Si una página aparece sin datos

Puede ocurrir por tres motivos normales:

- Todavía no hay registros de ese tipo.
- Los filtros activos dejan la tabla vacía.
- Supabase no ha respondido o está pausado.

Prueba a limpiar filtros, revisar la conexión en la barra lateral y confirmar
que los datos existen en Supabase.
