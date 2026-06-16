# Sistema de gestión de datos de fauna

Sistema interno para recoger, validar y almacenar datos de
observación de fauna. Pensado para un único usuario (un observador de
campo) con un agente que revisa los datos antes de insertarlos.

## Flujo

```
Observador → hojas-guía tabulares (o voz/Telegram)
    → el agente valida campos contra las reglas de las guías
      y el modelo de datos
    → avisa si hay fallos; con autorización inserta en Supabase
    → backup CSV local
```

Las hojas-guía y sus reglas de formato/validación viven en
`docs/Guias/` (una plantilla por tipo de visita/observación).
Los datos se respaldan en CSV local tras cada inserción significativa.

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
- **`docs/Guias/`** — Hojas-guía por tipo de visita y `formato-guias.md`
  con las reglas de campos, valores cerrados y validación.

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
