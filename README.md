# Sistema de gestión de datos de fauna

Sistema interno para recoger, almacenar y visualizar datos de
observación de fauna. Pensado para un único usuario (un observador de
campo).

## Flujo

```
Plaud (graba audio + plantilla)
    → exporta .txt a Drive
Script Python (parsea + inserta + hace backup automático)
    → Supabase
Dashboard Streamlit local
```

Los datos se respaldan automáticamente en tres sitios: Supabase + copia
local + Google Drive.

## Estado actual

El proyecto está en construcción. Ver `docs/BITACORA.md` para el estado
y la próxima tarea.

## Documentación clave

- **`AGENTS.md`** — Guía para agentes (Codex, Claude Code) que trabajen
  en este repo. Léelo antes de tocar nada.
- **`docs/SEGURIDAD.md`** — Reglas de seguridad y manejo de credenciales.
  **Lectura obligatoria.**
- **`docs/PRINCIPIOS.md`** — Principios del proyecto.
- **`docs/DECISIONES.md`** — Decisiones técnicas tomadas.
- **`docs/BITACORA.md`** — Estado vivo del proyecto.
- **`docs/modelo_datos.md`** — Modelo de datos detallado.

## Antes de tocar nada

1. Lee `AGENTS.md` (o `CLAUDE.md`, son idénticos).
2. Lee `docs/SEGURIDAD.md`.
3. Copia `.env.example` a `.env` y rellena los valores reales con tus
   credenciales (nunca subas el `.env` a git).

## Instalación

(Pendiente: se documentará cuando el proyecto esté en una fase con
algo que instalar.)

## Licencia

Privado. Uso interno.
