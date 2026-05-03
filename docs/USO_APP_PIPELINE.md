# Guía de uso — App Pipeline Plaud

> Guía para el observador. Sin tecnicismos.

---

## ¿Qué es esta app?

Es la pantalla desde la que procesas las grabaciones del Plaud.
Con un solo clic, la app:

1. Descarga los archivos `.txt` que el Plaud dejó en Google Drive.
2. Los procesa y los inserta en la base de datos (Supabase).
3. Crea un backup local con todos los datos.
4. Mueve cada archivo a la carpeta correcta según el resultado.

Es independiente del dashboard. El dashboard sirve para **consultar**
los datos. Esta app sirve para **introducirlos**.

---

## Cómo arrancar la app

### Desde el icono del Escritorio (recomendado)

Haz doble clic en el icono **BirdLog Pipeline** del Escritorio.
Se abrirá una terminal con el servidor y el navegador se abrirá
automáticamente en `http://localhost:8502`.

Ver sección [«Arrancar desde icono de escritorio»](#arrancar-desde-icono-de-escritorio)
para más detalles.

### Desde terminal

Abre una terminal en la carpeta del proyecto y ejecuta:

```bash
cd ~/Documentos/BirdLog
source .venv/bin/activate
streamlit run app_pipeline/app.py --server.port 8502
```

Se abrirá en el navegador en `http://localhost:8502`.

---

## Arrancar desde icono de escritorio

### Dónde está el icono

El icono **BirdLog Pipeline** está en el Escritorio de Ubuntu.
El archivo original se encuentra en:

```
~/Documentos/BirdLog/scripts/BirdLog_Pipeline.desktop
```

Si necesitas copiar el icono de nuevo al Escritorio:

```bash
cp ~/Documentos/BirdLog/scripts/BirdLog_Pipeline.desktop ~/Escritorio/
chmod +x ~/Escritorio/BirdLog_Pipeline.desktop
gio set ~/Escritorio/BirdLog_Pipeline.desktop metadata::trusted true
```

### Qué hacer si Ubuntu pide confiar en el lanzador

La primera vez que uses el icono, Ubuntu puede mostrar
un aviso de seguridad con el texto **"Este archivo de aplicación
no es de confianza"**.

Opciones:

1. **Haz clic derecho sobre el icono → «Permitir ejecutar»**
   (en GNOME 42+, «Allow Launching»). El icono pasa a ser ejecutable.
2. O ejecuta este comando en una terminal:
   ```bash
   gio set ~/Escritorio/BirdLog_Pipeline.desktop metadata::trusted true
   ```

Tras confirmar la confianza, el doble clic funcionará directamente.

### Cómo arrancar manualmente si el icono falla

Si el icono no responde, abre una terminal y ejecuta:

```bash
bash ~/Documentos/BirdLog/scripts/abrir_app_pipeline.sh
```

El script muestra mensajes claros si falta el entorno virtual
o Streamlit no está instalado.

### Cómo cerrar la app

Cierra la ventana de terminal que se abrió al pulsar el icono.
Streamlit se detiene automáticamente.

El navegador puede quedar abierto en la página — no pasa nada,
simplemente ciérrala o déjala.

---

## Pantalla principal

La pantalla tiene tres partes:

### 1. Cabecera de estado

Muestra si todo está listo para procesar:

- **Verde** (tres bloques verdes): entorno OK, Drive accesible, Supabase
  conectado. Puedes procesar.
- **Rojo**: hay un problema. Lee el mensaje y sigue los pasos que
  aparecen debajo.

### 2. Botones

- **▶ Procesar grabaciones de Plaud** — lanza el procesado de todos
  los archivos nuevos que haya en la carpeta `01_entrada` de Drive.
  Solo aparece activo cuando la cabecera es verde.
- **📊 Abrir dashboard** — abre el dashboard en una pestaña nueva
  (`http://127.0.0.1:8999`). Asegúrate de tenerlo arrancado primero.
- **💬 Abrir Claude.ai** — abre Claude.ai en una pestaña nueva.
  Útil para consultar documentación del sistema o resolver dudas.
  **Claude no accede a Supabase directamente** desde aquí.

### 3. Resultados del procesado

Aparecen tras pulsar el botón de procesamiento. Muestran el estado
de cada archivo procesado.

---

## Qué significan los colores

| Color | Significado | Qué hacer |
|-------|-------------|-----------|
| 🟢 Verde | Procesado correctamente. Datos en Supabase y backup creado. | Nada. Todo correcto. |
| 🟡 Amarillo | Falta un dato de catálogo (lugar, especie u observador desconocido). | Ver abajo: «Qué hacer con un error amarillo». |
| 🔴 Rojo | Error de validación o fallo técnico. | Ver abajo: «Qué hacer con un error rojo». |

---

## Qué hacer con un error amarillo (catálogo no encontrado)

Significa que en el archivo `.txt` hay un nombre que no está en
la base de datos. Por ejemplo, una especie nueva o un lugar
que no se había registrado antes.

Pasos:

1. Lee el mensaje del error — te dice exactamente qué falta
   (p.ej. "Especie no encontrada: 'Milano negro'").
2. Entra en el dashboard → página **Edición / Catálogos**.
3. Da de alta el nombre que falta (especie, lugar u observador).
4. Añade ese nombre al vocabulario cerrado del Plaud para futuras
   grabaciones.
5. En Google Drive, mueve el archivo desde la carpeta `03_errores`
   a la carpeta `01_entrada`.
6. Vuelve a la app pipeline y pulsa **Procesar grabaciones de Plaud**.

---

## Qué hacer con un error rojo (validación o técnico)

Significa que el archivo `.txt` tiene un error de formato o que
algo falló al guardarlo en Supabase.

Pasos:

1. Lee el mensaje — indica qué campo falta o qué salió mal.
2. Si el error es de campo faltante: revisa la plantilla del Plaud
   y vuelve a grabar la visita.
3. Si el error es de Supabase o Drive: ve a la sección de
   «Problemas frecuentes» más abajo.
4. El archivo ha quedado en la carpeta `03_errores` de Drive.
   Una vez resuelto el problema, muévelo a `01_entrada` y vuelve
   a procesar.

---

## Cómo abrir el dashboard

El dashboard es una app separada que debes arrancar aparte:

```
streamlit run dashboard/app.py --server.port 8999
```

Después pulsa el botón **📊 Abrir dashboard** en la app pipeline,
o abre `http://127.0.0.1:8999` directamente en el navegador.

---

## Advertencias sobre entornos

La app muestra en la cabecera el entorno activo (`dev`).

- **dev**: entorno de pruebas. Los datos que insertes aquí son de
  desarrollo.
- Si aparece un aviso de **ENTORNO PROD**, estás trabajando con los
  datos reales. Procede con cuidado.

---

## Problemas frecuentes

### «Falta configuración»

Para procesar grabaciones Plaud, la app necesita:

- `ENTORNO`
- la URL y clave de Supabase del entorno activo
- `GOOGLE_CREDENTIALS_PATH`
- `DRIVE_ENTRADA_ID`
- `DRIVE_PROCESADOS_ID`
- `DRIVE_ERRORES_ID`

La carpeta de fotos (`DRIVE_FOTOS_ID`) pertenece a la sincronización
de fotos y no bloquea el procesado de grabaciones Plaud.

### «No se pudo acceder a Google Drive»

1. Comprueba que el archivo de credenciales existe y está en la ruta
   indicada en `.env` (`GOOGLE_CREDENTIALS_PATH`).
2. Comprueba que las carpetas de Drive están compartidas con la cuenta
   de servicio `birdlog-drive`.
3. Si el problema persiste, consulta a Claude.ai con el mensaje exacto
   del error.

### «El proyecto Supabase está pausado»

El plan gratuito pausa el proyecto tras 7 días sin actividad.

1. Entra en [supabase.com](https://supabase.com).
2. Abre el proyecto `fauna-dev`.
3. Pulsa **Restore** y espera unos segundos.
4. Recarga la app pipeline.

### «No había grabaciones nuevas en Drive»

La carpeta `01_entrada` de Drive está vacía. El Plaud todavía no
ha sincronizado los archivos, o ya se procesaron antes.

### «Aún no has procesado ninguna grabación en esta sesión»

Mensaje inicial. Pulsa el botón **▶ Procesar grabaciones de Plaud**
para empezar.

---

## Qué hacer con los archivos en 03_errores

Los archivos en la carpeta `03_errores` de Drive son grabaciones
que no se han podido procesar. No se han borrado: están ahí para
que puedas corregir el problema y reprocesarlos.

Cuando hayas resuelto el problema (dato de catálogo añadido,
error corregido), mueve el archivo a la carpeta `01_entrada`
y pulsa de nuevo **Procesar grabaciones de Plaud**.
