-- ============================================================
-- Sistema de gestión de datos de fauna
-- Esquema v3 — tras revisión del Excel del cliente v03
-- (decisiones #40, #41, #42 y #43)
-- ============================================================
-- Cambios respecto a v2:
--   * 4 tablas nuevas: fototrampeo, cuaderno_campo,
--     estudio_campo y castor_rastros.
--   * meteorologia: conteos de personas, observaciones y campos
--     históricos opcionales (humedad, presión, niveles de nubes).
--   * nidos_rapaces: descripcion_nido, incuba, numero_pollos,
--     pollos_volados.
--   * cebos_avispones: numero_trampa, fecha_colocacion y UTM del
--     nido de avispón localizado.
--   * lindus: especie_texto (traza de la transcripción original).
--   * codigo_origen en las tablas que reciben el histórico 2025
--     (especies, lugares, visitas, meteorologia, lindus) para
--     trazar la migración desde el Excel (V0001, SP001...).
--   * CHECKs ampliados: visitas.tipo_visita y lugares.tipo_lugar.
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
DROP TABLE IF EXISTS castor_rastros CASCADE;
DROP TABLE IF EXISTS estudio_campo CASCADE;
DROP TABLE IF EXISTS cuaderno_campo CASCADE;
DROP TABLE IF EXISTS fototrampeo CASCADE;
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
    id_especie      INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre_cientifico TEXT NOT NULL UNIQUE,
    nombre_comun    TEXT,
    grupo           TEXT CHECK (grupo IN (
                        'RAPAZ',
                        'PASERIFORME',
                        'ACUATICA',
                        'INVERTEBRADO',
                        'MAMIFERO',
                        'OTRO'
                    )),
    codigo_origen   TEXT UNIQUE  -- id del Excel del cliente (SP001...)
);


-- ------------------------------------------------------------
-- observadores
-- ------------------------------------------------------------
CREATE TABLE observadores (
    id_observador       INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre_observador   TEXT NOT NULL UNIQUE
);


-- ------------------------------------------------------------
-- lugares
-- ------------------------------------------------------------
CREATE TABLE lugares (
    id_lugar        INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre_lugar    TEXT NOT NULL UNIQUE,
    tipo_lugar      TEXT NOT NULL CHECK (tipo_lugar IN (
                        'CONTEO_MIGRATORIO',
                        'CAJA_NIDO',
                        'CEBO_AVISPON',
                        'NIDO_RAPAZ',
                        'PUENTE',
                        'FOTOTRAMPEO',
                        'ESTUDIO_CAMPO',
                        'OTRO'
                    )),
    municipio       TEXT,
    utm_x           DOUBLE PRECISION NOT NULL,
    utm_y           DOUBLE PRECISION NOT NULL,
    codigo_origen   TEXT UNIQUE  -- id del Excel del cliente (LUG01...)
);

CREATE INDEX idx_lugares_tipo ON lugares(tipo_lugar);
CREATE INDEX idx_lugares_municipio ON lugares(municipio);


-- ------------------------------------------------------------
-- visitas
-- ------------------------------------------------------------
CREATE TABLE visitas (
    id_visita       INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_lugar        INTEGER NOT NULL REFERENCES lugares(id_lugar),
    id_observador   INTEGER NOT NULL REFERENCES observadores(id_observador),
    tipo_visita     TEXT NOT NULL CHECK (tipo_visita IN (
                        'LINDUS',
                        'CAJA_NIDO',
                        'CEBO_AVISPON',
                        'NIDO_RAPAZ',
                        'MAMIFEROS_PUENTES',
                        'IMPACTO_AMBIENTAL',
                        'FOTOTRAMPEO',
                        'CUADERNO_CAMPO',
                        'CASTOR_RASTROS'
                    )),
    fecha           DATE NOT NULL,
    hora_inicio     TIME NOT NULL,
    hora_fin        TIME,
    observaciones   TEXT,
    codigo_origen   TEXT UNIQUE  -- id del Excel del cliente (V0001...)
);

CREATE INDEX idx_visitas_fecha ON visitas(fecha);
CREATE INDEX idx_visitas_lugar ON visitas(id_lugar);
CREATE INDEX idx_visitas_tipo ON visitas(tipo_visita);


-- ------------------------------------------------------------
-- meteorologia
-- 1 visita → N filas (una por hora en Lindus/Trona)
-- 1 visita → 1 fila para el resto de estudios
-- Los 9 campos de captura Plaud se mantienen; el bloque de campos
-- históricos solo lo rellena la importación del Excel 2025.
-- ------------------------------------------------------------
CREATE TABLE meteorologia (
    id_meteo            INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_visita           INTEGER NOT NULL REFERENCES visitas(id_visita),
    hora                TIME NOT NULL,
    temperatura         DOUBLE PRECISION,
    nubosidad           INTEGER CHECK (nubosidad BETWEEN 0 AND 8),
    viento_direccion    TEXT,
    viento_intensidad   TEXT,
    precipitacion       TEXT,
    visibilidad         TEXT,
    -- Conteos de personas en el punto de observación
    presentes           INTEGER,
    observando          INTEGER,
    visitantes          INTEGER,
    observaciones       TEXT,
    -- Campos históricos (importación Lindus 2025; el Plaud no los dicta)
    humedad_relativa    DOUBLE PRECISION,
    presion_atm         DOUBLE PRECISION,
    precipitacion_tipo  TEXT,
    mar_nubes_cobertura INTEGER,
    mar_nubes_altura    DOUBLE PRECISION,
    nubes_n1_cobertura  INTEGER,
    nubes_n1_altura     DOUBLE PRECISION,
    nubes_n1_tipo       TEXT,
    nubes_n2_cobertura  INTEGER,
    nubes_n2_tipo       TEXT,
    codigo_origen       TEXT UNIQUE  -- id del Excel del cliente (M0001...)
);

CREATE INDEX idx_meteo_visita ON meteorologia(id_visita);


-- ------------------------------------------------------------
-- lindus
-- Conteos migratorios en Lindus y Trona
-- ------------------------------------------------------------
CREATE TABLE lindus (
    id_lindus       INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
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
    observaciones   TEXT,
    especie_texto   TEXT,        -- texto original transcrito (traza)
    codigo_origen   TEXT UNIQUE  -- id del Excel del cliente (L000001...)
);

CREATE INDEX idx_lindus_visita ON lindus(id_visita);
CREATE INDEX idx_lindus_especie ON lindus(id_especie);
CREATE INDEX idx_lindus_comportamiento ON lindus(comportamiento);


-- ------------------------------------------------------------
-- cajas_nido
-- ------------------------------------------------------------
CREATE TABLE cajas_nido (
    id_cajanido             INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
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
    id_nido_rapaz           INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_visita               INTEGER NOT NULL REFERENCES visitas(id_visita),
    id_lugar                INTEGER NOT NULL REFERENCES lugares(id_lugar),
    id_especie              INTEGER REFERENCES especies(id_especie),
    texto_revision          TEXT NOT NULL,
    comunicacion_personal   TEXT,
    descripcion_nido        TEXT,
    incuba                  BOOLEAN,
    numero_pollos           INTEGER,
    pollos_volados          INTEGER
);

CREATE INDEX idx_nidos_visita ON nidos_rapaces(id_visita);
CREATE INDEX idx_nidos_lugar ON nidos_rapaces(id_lugar);


-- ------------------------------------------------------------
-- cebos_avispones
-- La UTM de la trampa vive en lugares (el cebo es el lugar).
-- utm_x_nido/utm_y_nido localizan el nido de avispón si se encuentra.
-- ------------------------------------------------------------
CREATE TABLE cebos_avispones (
    id_cebo             INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_visita           INTEGER NOT NULL REFERENCES visitas(id_visita),
    id_lugar            INTEGER NOT NULL REFERENCES lugares(id_lugar),
    vv                  INTEGER NOT NULL,
    crabro              INTEGER,
    avispa_europea      INTEGER,
    polilla             INTEGER,
    mariposa            INTEGER,
    otros               INTEGER,
    observaciones       TEXT,
    numero_trampa       TEXT,
    fecha_colocacion    DATE,
    utm_x_nido          DOUBLE PRECISION,
    utm_y_nido          DOUBLE PRECISION
);

CREATE INDEX idx_cebos_visita ON cebos_avispones(id_visita);
CREATE INDEX idx_cebos_lugar ON cebos_avispones(id_lugar);


-- ------------------------------------------------------------
-- mamiferos_puentes
-- ------------------------------------------------------------
CREATE TABLE mamiferos_puentes (
    id_mamifero     INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
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
-- fototrampeo (nueva en v3)
-- Evento de colocación/revisión de cámara de fototrampeo.
-- Las imágenes van en la tabla fotos con
-- tabla_origen = 'fototrampeo' e id_origen = id_fototrampeo.
-- ------------------------------------------------------------
CREATE TABLE fototrampeo (
    id_fototrampeo      INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_visita           INTEGER NOT NULL REFERENCES visitas(id_visita),
    id_lugar            INTEGER NOT NULL REFERENCES lugares(id_lugar),
    id_especie          INTEGER REFERENCES especies(id_especie),
    especie_texto       TEXT,
    fecha_colocacion    DATE,
    fecha_revision      DATE,
    fecha_imagen        DATE,
    tipo_media          TEXT,  -- vocabulario pendiente con el cliente
    numero_imagenes     INTEGER,
    observaciones       TEXT
);

CREATE INDEX idx_fototrampeo_visita ON fototrampeo(id_visita);
CREATE INDEX idx_fototrampeo_lugar ON fototrampeo(id_lugar);


-- ------------------------------------------------------------
-- cuaderno_campo (nueva en v3)
-- Observaciones sueltas tipo cuaderno de campo. id_lugar es
-- opcional porque pueden ocurrir fuera de los puntos del catálogo;
-- en ese caso el sitio se describe en observaciones.
-- ------------------------------------------------------------
CREATE TABLE cuaderno_campo (
    id_cuaderno     INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_visita       INTEGER NOT NULL REFERENCES visitas(id_visita),
    id_lugar        INTEGER REFERENCES lugares(id_lugar),
    id_especie      INTEGER REFERENCES especies(id_especie),
    especie_texto   TEXT,
    numero          INTEGER,
    observaciones   TEXT
);

CREATE INDEX idx_cuaderno_visita ON cuaderno_campo(id_visita);


-- ------------------------------------------------------------
-- estudio_campo (nueva en v3)
-- Detecciones de estudios de impacto ambiental. La sesión
-- (punto, horas, meteo) se registra como visita de tipo
-- IMPACTO_AMBIENTAL + fila en meteorologia; aquí solo va el
-- detalle por detección.
-- ------------------------------------------------------------
CREATE TABLE estudio_campo (
    id_estudio          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_visita           INTEGER NOT NULL REFERENCES visitas(id_visita),
    id_especie          INTEGER REFERENCES especies(id_especie),
    especie_texto       TEXT,
    numero              INTEGER,
    deteccion           TEXT,  -- vocabulario pendiente con el cliente
    hora_observacion    TIME,
    distancia_inicial   DOUBLE PRECISION,
    lado_inicial        TEXT,
    distancia_minima    DOUBLE PRECISION,
    lado_minima         TEXT,
    distancia_final     DOUBLE PRECISION,
    lado_final          TEXT,
    vuelo_sobre         BOOLEAN,
    direccion_vuelo     TEXT,
    migracion           TEXT,  -- vocabulario pendiente con el cliente
    altura              TEXT,  -- banda o metros; pendiente con el cliente
    observaciones       TEXT
);

CREATE INDEX idx_estudio_visita ON estudio_campo(id_visita);
CREATE INDEX idx_estudio_especie ON estudio_campo(id_especie);


-- ------------------------------------------------------------
-- castor_rastros (nueva en v3)
-- Rastros de castor en transectos de río. Las fotos van en la
-- tabla fotos con tabla_origen = 'castor_rastros'.
-- ------------------------------------------------------------
CREATE TABLE castor_rastros (
    id_castor_rastro    INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_visita           INTEGER NOT NULL REFERENCES visitas(id_visita),
    id_lugar            INTEGER NOT NULL REFERENCES lugares(id_lugar),
    id_especie          INTEGER REFERENCES especies(id_especie),
    tipo_rastro         TEXT NOT NULL,  -- vocabulario pendiente con el cliente
    intensidad_rastro   TEXT,           -- vocabulario pendiente con el cliente
    reciente_antiguo    TEXT,           -- vocabulario pendiente con el cliente
    aplicacion          TEXT,
    observaciones       TEXT
);

CREATE INDEX idx_castor_visita ON castor_rastros(id_visita);
CREATE INDEX idx_castor_lugar ON castor_rastros(id_lugar);


-- ------------------------------------------------------------
-- fotos
-- ------------------------------------------------------------
CREATE TABLE fotos (
    id_foto         INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
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
-- UNION ALL SELECT 'fototrampeo',     COUNT(*) FROM fototrampeo
-- UNION ALL SELECT 'cuaderno_campo',  COUNT(*) FROM cuaderno_campo
-- UNION ALL SELECT 'estudio_campo',   COUNT(*) FROM estudio_campo
-- UNION ALL SELECT 'castor_rastros',  COUNT(*) FROM castor_rastros
-- UNION ALL SELECT 'fotos',           COUNT(*) FROM fotos;
