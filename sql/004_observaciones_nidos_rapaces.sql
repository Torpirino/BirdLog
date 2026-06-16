-- Migración aditiva sobre el esquema v3 (decisión #48).
-- La plantilla hoja-guía Visita_Nido_Rapaz dicta OBSERVACIONES_NIDO, pero
-- nidos_rapaces era la única tabla específica sin columna observaciones
-- y el dato se perdía en silencio. sql/003_esquema_v3.sql ya incluye la
-- columna para entornos nuevos; este archivo la añade a los existentes.

ALTER TABLE nidos_rapaces ADD COLUMN IF NOT EXISTS observaciones TEXT;
