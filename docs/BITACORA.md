# Bitácora del proyecto

> Este archivo es la memoria viva del proyecto. Codex y Claude Code lo
> leen al iniciar cada sesión y lo actualizan cuando el usuario dice
> "rutina de cierre".

---

## Estado actual

- **Fase activa**: Fase 3 — Parser
- **Última sesión**: 2026-05-01
- **Próxima tarea**: Construir mini-pipeline/parser de pruebas para
  `.txt` de Plaud

---

## Tareas en curso

- [ ] (sin tareas en curso)

---

## Tareas pendientes

### Fase 2: Plantilla Plaud
- [ ] Hacer grabaciones reales de prueba (Lindus, cebos avispón, cajas nido)
- [ ] Confirmar con el observador el quinto ecosistema de cajas_nido

### Fase 3: Parser
- [ ] Construir mini-pipeline/parser de pruebas para `.txt` de Plaud
- [ ] Recoger 5-6 .txt de ejemplo de tipos distintos de visita
- [ ] Implementar `src/parser/plaud.py`
- [ ] Tests del parser con los .txt de ejemplo en `tests/ejemplos_plaud/`
- [ ] Implementar notificación cuando un lugar/especie no existe en catálogo

### Fase 4: Resolución de FKs, inserción y backup
- [ ] Implementar `src/insercion/catalogos.py` (nombre → id)
- [ ] Implementar `src/insercion/escritura.py` (insertar respetando FKs)
- [ ] Implementar `src/backup/exportar.py` (CSV de cada tabla)
- [ ] Implementar `src/backup/drive.py` (subir backup a Drive)
- [ ] Tests con BD de desarrollo

### Fase 5: Gestión de fotos
- [ ] Decidir convención de carpetas en Drive
- [ ] Implementar `src/fotos/drive.py`
- [ ] Definir tabla fotos definitivamente con el observador

### Fase 6: Dashboard
- [ ] `dashboard/app.py` con navegación
- [ ] Página Lindus: curvas diarias, decadarios, cruce meteo
- [ ] Página avispones: mapa cebos + acumulado capturas por periodo
- [ ] Página mamíferos: presencia/ausencia por puente y especie
- [ ] Página rapaces: seguimiento de nidos
- [ ] Página cajas nido: éxito reproductor por ecosistema
- [ ] Página explorador: filtros libres
- [ ] Manejo de error de pausa Supabase con mensaje claro al usuario

---

## Tareas completadas

### Diseño de la base de datos (completado)
- [x] Diseño inicial de 11 tablas (v1)
- [x] Revisión con el observador mediante conversación grabada
- [x] Rediseño completo tabla por tabla (v2): 10 tablas definitivas
- [x] SQL de creación generado: `sql/002_esquema_v2.sql`
- [x] Diagrama de relaciones generado: `diagrama_relaciones_v2.html`
- [x] Documentos del proyecto actualizados (v3)

### Fase 2: Plantilla Plaud (completado)
- [x] Diseño de plantillas Plaud definitivas v1
- [x] Listar los campos exactos que devolverá el .txt por tipo de visita
- [x] Definir vocabulario cerrado por campo (lugares, especies frecuentes,
      comportamiento, ecosistema, estado_nido, tipo_evidencia...)
- [x] Documentar el formato exacto en `docs/formato_plaud.md`

### Fase 1: Supabase inicial (completado parcialmente)
- [x] Crear proyecto Supabase dev
- [x] Aplicar esquema v1 (ya obsoleto — aplicar v2)
- [x] Importar datos históricos de Lindus 2025 (10.905 observaciones)
- [x] Importar datos meteorológicos de Lindus (1.083 registros)
- [ ] **Pendiente**: aplicar esquema v2 (borrar tablas v1 y crear v2)
- [ ] **Pendiente**: regenerar y reimportar datos con nueva estructura

---

## Bloqueos / dudas

- Quinto ecosistema de cajas_nido pendiente de confirmar con el observador.

---

## Glosario de archivos clave

- `sql/002_esquema_v2.sql`: esquema definitivo. Incluye DROP de tablas
  anteriores y CREATE de las 10 tablas nuevas. Aplicar en SQL Editor
  de Supabase.
- `docs/modelo_datos.md`: descripción completa de las 10 tablas con
  todos los campos, tipos y valores cerrados.
- `docs/formato_plaud.md`: plantillas Plaud definitivas v1 y formato
  estructurado esperado para los `.txt`.
- `docs/SEGURIDAD.md`: reglas de seguridad y manejo de credenciales.
- `docs/DECISIONES.md`: historial de decisiones técnicas tomadas.
- `.env.example`: plantilla de variables de entorno (sin valores reales).
- `diagrama_relaciones_v2.html`: diagrama visual de relaciones entre tablas.

---

## Handoff

(vacío)
