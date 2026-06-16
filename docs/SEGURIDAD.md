# Seguridad del proyecto

> Este documento explica cómo se protegen las credenciales y los datos
> del proyecto. Es de **lectura obligatoria** antes de empezar a trabajar
> en el repo, tanto para humanos como para agentes (Codex, Claude Code).

---

## 1. Por qué importa la seguridad aquí

Este sistema gestiona:

- **Datos del observador**: años de trabajo de campo, irreemplazables.
- **Ubicaciones GPS de nidos** de rapaces protegidas. Una filtración no
  es solo un problema técnico: puede facilitar el expolio de nidos.
- **Credenciales** de servicios (Supabase, Google Drive, GitHub) cuyo
  uso indebido puede borrar datos o cobrar dinero.

Por eso las reglas siguientes no son negociables.

---

## 2. Qué NO se sube a git, NUNCA

Lista no exhaustiva de cosas que jamás deben aparecer en un commit:

- Archivos `.env` con valores reales.
- Archivos JSON de credenciales de Google (`*.credentials.json`,
  `service_account.json`).
- Archivos `secrets.toml` o cualquier archivo con secretos.
- Claves de Supabase (`anon` o `service_role`).
- IDs de carpetas privadas de Drive.
- Tokens de cualquier API.
- Passwords.
- URLs con credenciales embebidas (formato `https://user:password@host`).
- CSV con datos reales del observador (nombres de lugares, coordenadas
  GPS de nidos, observaciones reales).
- Archivos de backup (la carpeta `backups/`).
- Volcados de la base de datos de prod.
- Capturas de pantalla con datos sensibles.

---

## 3. Cómo se manejan las credenciales

### 3.1 Archivo `.env`

Vive en la raíz del repo, en local. **Está en `.gitignore`**: git lo
ignora completamente.

Variables que contiene:
- `ENTORNO=dev` o `ENTORNO=prod`
- `SUPABASE_DEV_URL`, `SUPABASE_DEV_KEY`
- `SUPABASE_PROD_URL`, `SUPABASE_PROD_KEY`
- `GOOGLE_DRIVE_CREDENTIALS_PATH` (ruta al JSON de service account)
- `GOOGLE_DRIVE_CARPETA_FOTOS_ID`
- `GOOGLE_DRIVE_CARPETA_BACKUPS_ID`

### 3.2 Archivo `.env.example`

Vive en el repo (es el único que sí se sube a git). Contiene los nombres
de las variables pero **sin valores reales** — sólo la estructura. Sirve
para que cualquiera que clone el repo sepa qué variables tiene que
rellenar en su propio `.env`.

### 3.3 Credenciales de Google Drive

El JSON de service account de Google se guarda **fuera del repo**. Lo
recomendado:

```
~/.config/sistema-fauna/google-credentials.json
```

Y se referencia en `.env` con la ruta absoluta.

---

## 4. Antes de hacer un commit

**Cualquier agente** (Codex, Claude Code) o humano debe verificar antes:

### Checklist

1. ¿El diff contiene algún archivo en la lista del punto 2?
2. ¿Hay alguna línea con cadenas que parezcan claves
   (caracteres aleatorios largos, `eyJ...`, `sk-...`, `pk-...`,
   `AIza...`)?
3. ¿Hay URLs con credenciales embebidas?
4. ¿Hay rutas absolutas con información del usuario
   (`/home/[nombre real]/...`, `C:\Users\[nombre real]\...`)?
5. ¿Hay datos reales de observaciones?

Si la respuesta a cualquiera es sí: **detenerse y preguntar al usuario**.
No comitear automáticamente.

### Comando manual de verificación

```bash
git diff --cached
```

Mira el diff antes de cada `git commit` y compáralo con la lista.

---

## 5. Si una credencial se filtra accidentalmente

Sucede. Procedimiento:

1. **Rotar la clave inmediatamente** desde el panel de origen:
   - Supabase: Settings → API → Reset.
   - Google Drive: revocar el service account y crear uno nuevo.
   - GitHub tokens: Settings → Developer settings → revocar.
2. Actualizar el `.env` local con la clave nueva.
3. Si la clave llegó a hacerse `push` a GitHub: **borrar el commit del
   historial** con `git filter-branch` o BFG Repo-Cleaner. Que el
   histórico de git no se libra: aunque se borre en el último commit,
   sigue ahí accesible.
4. Avisar a quien tenga clonado el repo (si aplica) para que actualice
   su copia.

---

## 6. Repositorio privado

El repo es **privado en GitHub**. Aunque pareciera que estando privado
se puede ser más laxo, **no es así**:

- Los repos privados se hacen accidentalmente públicos a veces (cambios
  de configuración, cambios de organización, traspasos).
- Las claves filtradas en repos privados ya están filtradas a quien
  haya accedido alguna vez al repo (colaboradores, herramientas de CI,
  compañías de seguridad que escanean GitHub).
- La regla "los secretos no entran en git" es la misma sin importar
  privacidad.

---

## 7. Datos del observador

Los CSV con datos reales (10.000+ filas de observaciones, ubicaciones
de nidos) no se suben al repo. Su lugar:

- **Supabase** (entorno `prod`): datos vivos del sistema.
- **Backup local**: en `backups/` del ordenador del observador.
- **Backup Drive**: en `Backups Sistema Fauna/` de su Drive.

Los datos en el repo son sólo:

- Esquema SQL (estructura de tablas, sin datos).
- Datos de prueba sintéticos cuando hagan falta para tests.
- Catálogos genéricos sin información sensible (nombre científico de
  especies, estructura de tablas).

---

## 8. Acceso a Supabase

### Claves

Supabase da dos claves:
- **`anon` key**: pública, lectura limitada por políticas RLS.
- **`service_role` key**: acceso completo, salta todas las restricciones.

El sistema usa **`service_role` solo en el script Python local** (que
corre en el ordenador del observador). Nunca expuesta al exterior.

### Separación dev/prod

Las claves dev y prod son distintas. Mezclarlas equivale a operar contra
la BD equivocada. La variable `ENTORNO` en `.env` controla cuál se usa.

---

## 9. Rutina de seguridad recomendada

- **Mensual**: revisar accesos en Supabase y GitHub. Eliminar lo que ya
  no se use.
- **Trimestral**: rotar las claves `service_role` de Supabase aunque no
  se hayan filtrado. Es buena higiene.
- **Tras cada cambio importante**: verificar que `.gitignore` está al
  día.
- **Tras cada incidente**: anotar qué pasó en una nota a mano (no en el
  repo) para no repetirlo.
