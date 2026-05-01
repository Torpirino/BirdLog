-- ============================================================
-- Sistema de gestión de datos de fauna
-- Esquema v2 — diseño definitivo tras revisión con observador
-- ============================================================
-- INSTRUCCIONES:
-- 1. Primero ejecuta el bloque DROP para borrar las tablas anteriores.
-- 2. Luego ejecuta el bloque CREATE para crear las nuevas.
-- El orden importa por las foreign keys.
-- ============================================================


-- ============================================================
-- PASO 1: BORRAR TABLAS ANTERIORES
-- Ejecuta esto primero si ya tenías tablas de la versión anterior.
-- ============================================================

DROP TABLE IF EXISTS fotos CASCADE;
DROP TABLE IF EXISTS mamiferos_puentes CASCADE;
DROP TABLE IF EXISTS cebos_avispones CASCADE;
DROP TABLE IF EXISTS nidos_rapaces CASCADE;
DROP TABLE IF EXISTS cajas_nido CASCADE;
DROP TABLE IF EXISTS lindus CASCADE;
DROP TABLE IF EXISTS meteorologia CASCADE;
DROP TABLE IF EXISTS visitas CASCADE;
DROP TABLE IF EXISTS sesiones CASCADE;
DROP TABLE IF EXISTS observaciones CASCADE;
DROP TABLE IF EXISTS lugares CASCADE;
DROP TABLE IF EXISTS especies CASCADE;
DROP TABLE IF EXISTS observadores CASCADE;


-- ============================================================
-- PASO 2: CREAR TABLAS NUEVAS
-- ============================================================


-- ------------------------------------------------------------
-- especies
-- ------------------------------------------------------------
CREATE TABLE especies (
    id_especie      INTEGER PRIMARY KEY,
    nombre_cientifico TEXT NOT NULL UNIQUE,
    nombre_comun    TEXT,
    grupo           TEXT CHECK (grupo IN (
                        'RAPAZ',
                        'PASERIFORME',
                        'ACUATICA',
                        'INVERTEBRADO',
                        'MAMIFERO',
                        'OTRO'
                    ))
);


-- ------------------------------------------------------------
-- observadores
-- ------------------------------------------------------------
CREATE TABLE observadores (
    id_observador       INTEGER PRIMARY KEY,
    nombre_observador   TEXT NOT NULL UNIQUE
);


-- ------------------------------------------------------------
-- lugares
-- ------------------------------------------------------------
CREATE TABLE lugares (
    id_lugar        INTEGER PRIMARY KEY,
    nombre_lugar    TEXT NOT NULL UNIQUE,
    tipo_lugar      TEXT NOT NULL CHECK (tipo_lugar IN (
                        'CONTEO_MIGRATORIO',
                        'CAJA_NIDO',
                        'CEBO_AVISPON',
                        'NIDO_RAPAZ',
                        'PUENTE'
                    )),
    municipio       TEXT,
    utm_x           DOUBLE PRECISION NOT NULL,
    utm_y           DOUBLE PRECISION NOT NULL
);

CREATE INDEX idx_lugares_tipo ON lugares(tipo_lugar);
CREATE INDEX idx_lugares_municipio ON lugares(municipio);


-- ------------------------------------------------------------
-- visitas
-- ------------------------------------------------------------
CREATE TABLE visitas (
    id_visita       INTEGER PRIMARY KEY,
    id_lugar        INTEGER NOT NULL REFERENCES lugares(id_lugar),
    id_observador   INTEGER NOT NULL REFERENCES observadores(id_observador),
    tipo_visita     TEXT NOT NULL CHECK (tipo_visita IN (
                        'LINDUS',
                        'CAJA_NIDO',
                        'CEBO_AVISPON',
                        'NIDO_RAPAZ',
                        'MAMIFEROS_PUENTES',
                        'IMPACTO_AMBIENTAL'
                    )),
    fecha           DATE NOT NULL,
    hora_inicio     TIME NOT NULL,
    hora_fin        TIME,
    observaciones   TEXT
);

CREATE INDEX idx_visitas_fecha ON visitas(fecha);
CREATE INDEX idx_visitas_lugar ON visitas(id_lugar);
CREATE INDEX idx_visitas_tipo ON visitas(tipo_visita);


-- ------------------------------------------------------------
-- meteorologia
-- 1 visita → N filas (una por hora en Lindus/Trona)
-- 1 visita → 1 fila para el resto de estudios
-- ------------------------------------------------------------
CREATE TABLE meteorologia (
    id_meteo            INTEGER PRIMARY KEY,
    id_visita           INTEGER NOT NULL REFERENCES visitas(id_visita),
    hora                TIME NOT NULL,
    temperatura         DOUBLE PRECISION,
    nubosidad           INTEGER CHECK (nubosidad BETWEEN 0 AND 8),
    viento_direccion    TEXT,
    viento_intensidad   TEXT,
    precipitacion       TEXT,
    visibilidad         TEXT
);

CREATE INDEX idx_meteo_visita ON meteorologia(id_visita);


-- ------------------------------------------------------------
-- lindus
-- Conteos migratorios en Lindus y Trona
-- ------------------------------------------------------------
CREATE TABLE lindus (
    id_lindus       INTEGER PRIMARY KEY,
    id_visita       INTEGER NOT NULL REFERENCES visitas(id_visita),
    id_especie      INTEGER NOT NULL REFERENCES especies(id_especie),
    hora            TIME NOT NULL,
    numero          INTEGER NOT NULL,
    comportamiento  TEXT NOT NULL CHECK (comportamiento IN (
                        'MIGRADOR',
                        'NORTE',
                        'LOCAL'
                    )),
    edad            TEXT,
    sexo            TEXT,
    plumaje         TEXT,
    observaciones   TEXT
);

CREATE INDEX idx_lindus_visita ON lindus(id_visita);
CREATE INDEX idx_lindus_especie ON lindus(id_especie);
CREATE INDEX idx_lindus_comportamiento ON lindus(comportamiento);


-- ------------------------------------------------------------
-- cajas_nido
-- ------------------------------------------------------------
CREATE TABLE cajas_nido (
    id_cajanido             INTEGER PRIMARY KEY,
    id_visita               INTEGER NOT NULL REFERENCES visitas(id_visita),
    id_lugar                INTEGER NOT NULL REFERENCES lugares(id_lugar),
    id_especie              INTEGER REFERENCES especies(id_especie),
    ecosistema              TEXT NOT NULL CHECK (ecosistema IN (
                                'ZONA_SALVAJE',
                                'ZONA_URBANA',
                                'PARQUE_CON_RIO',
                                'PARQUE_URBANO'
                                -- Quinto ecosistema pendiente de confirmar
                            )),
    especie_arbol           TEXT NOT NULL,
    estado_nido             TEXT NOT NULL CHECK (estado_nido IN (
                                'POCAS_HIERBAS',
                                'MUCHAS_HIERBAS',
                                'CASI_TERMINADO',
                                'TERMINADO'
                            )),
    ocupada                 BOOLEAN NOT NULL,
    numero_huevos           INTEGER,
    numero_pollos           INTEGER,
    observaciones           TEXT,
    -- Campos proyecto IB+ (opcionales)
    orientacion_caja        TEXT CHECK (orientacion_caja IN (
                                'N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'
                            )),
    huevos_caliente_frio    TEXT,
    peso_pollos             DOUBLE PRECISION,
    longitud_tarso          DOUBLE PRECISION,
    numero_anilla           TEXT,
    distancia_rio           DOUBLE PRECISION,
    distancia_peatonal      DOUBLE PRECISION,
    distancia_carretera     DOUBLE PRECISION,
    cobertura_vegetal       DOUBLE PRECISION,
    cobertura_arboles       DOUBLE PRECISION,
    cobertura_matorral      DOUBLE PRECISION,
    cobertura_pastizal      DOUBLE PRECISION
);

CREATE INDEX idx_cajas_visita ON cajas_nido(id_visita);
CREATE INDEX idx_cajas_lugar ON cajas_nido(id_lugar);


-- ------------------------------------------------------------
-- nidos_rapaces
-- ------------------------------------------------------------
CREATE TABLE nidos_rapaces (
    id_nido_rapaz           INTEGER PRIMARY KEY,
    id_visita               INTEGER NOT NULL REFERENCES visitas(id_visita),
    id_lugar                INTEGER NOT NULL REFERENCES lugares(id_lugar),
    id_especie              INTEGER REFERENCES especies(id_especie),
    texto_revision          TEXT NOT NULL,
    comunicacion_personal   TEXT
);

CREATE INDEX idx_nidos_visita ON nidos_rapaces(id_visita);
CREATE INDEX idx_nidos_lugar ON nidos_rapaces(id_lugar);


-- ------------------------------------------------------------
-- cebos_avispones
-- ------------------------------------------------------------
CREATE TABLE cebos_avispones (
    id_cebo         INTEGER PRIMARY KEY,
    id_visita       INTEGER NOT NULL REFERENCES visitas(id_visita),
    id_lugar        INTEGER NOT NULL REFERENCES lugares(id_lugar),
    vv              INTEGER NOT NULL,
    crabro          INTEGER,
    avispa_europea  INTEGER,
    polilla         INTEGER,
    mariposa        INTEGER,
    otros           INTEGER,
    observaciones   TEXT
);

CREATE INDEX idx_cebos_visita ON cebos_avispones(id_visita);
CREATE INDEX idx_cebos_lugar ON cebos_avispones(id_lugar);


-- ------------------------------------------------------------
-- mamiferos_puentes
-- ------------------------------------------------------------
CREATE TABLE mamiferos_puentes (
    id_mamifero     INTEGER PRIMARY KEY,
    id_visita       INTEGER NOT NULL REFERENCES visitas(id_visita),
    id_lugar        INTEGER NOT NULL REFERENCES lugares(id_lugar),
    id_especie      INTEGER NOT NULL REFERENCES especies(id_especie),
    presencia       TEXT NOT NULL CHECK (presencia IN (
                        'PRESENTE',
                        'AUSENTE',
                        'POSIBLE'
                    )),
    tipo_evidencia  TEXT CHECK (tipo_evidencia IN (
                        'HUELLA',
                        'EXCREMENTO',
                        'MADRIGUERA',
                        'AVISTAMIENTO'
                    )),
    observaciones   TEXT
);

CREATE INDEX idx_mam_visita ON mamiferos_puentes(id_visita);
CREATE INDEX idx_mam_lugar ON mamiferos_puentes(id_lugar);
CREATE INDEX idx_mam_especie ON mamiferos_puentes(id_especie);


-- ------------------------------------------------------------
-- fotos (pendiente de definir en su fase)
-- ------------------------------------------------------------
CREATE TABLE fotos (
    id_foto         INTEGER PRIMARY KEY,
    id_visita       INTEGER REFERENCES visitas(id_visita),
    tabla_origen    TEXT,
    id_origen       INTEGER,
    url_drive       TEXT NOT NULL,
    descripcion     TEXT,
    fecha_subida    DATE
);


-- ============================================================
-- VERIFICACIÓN
-- Ejecuta esto después de importar los datos para comprobar
-- que todo está bien.
-- ============================================================

-- SELECT 'especies'          AS tabla, COUNT(*) AS filas FROM especies
-- UNION ALL SELECT 'observadores',    COUNT(*) FROM observadores
-- UNION ALL SELECT 'lugares',         COUNT(*) FROM lugares
-- UNION ALL SELECT 'visitas',         COUNT(*) FROM visitas
-- UNION ALL SELECT 'meteorologia',    COUNT(*) FROM meteorologia
-- UNION ALL SELECT 'lindus',          COUNT(*) FROM lindus
-- UNION ALL SELECT 'cajas_nido',      COUNT(*) FROM cajas_nido
-- UNION ALL SELECT 'nidos_rapaces',   COUNT(*) FROM nidos_rapaces
-- UNION ALL SELECT 'cebos_avispones', COUNT(*) FROM cebos_avispones
-- UNION ALL SELECT 'mamiferos_puentes', COUNT(*) FROM mamiferos_puentes
-- UNION ALL SELECT 'fotos',           COUNT(*) FROM fotos;
