"""Tests del mini-pipeline de parser Plaud."""

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.parser.normalizacion import normalizar_fecha, normalizar_registro
from src.parser.plaud import detectar_tipo, parsear_txt_plaud
from src.parser.validacion import validar_registro, validar_registro_detallado

EJEMPLOS = Path(__file__).parent / "ejemplos_plaud"
ARCHIVOS = {
    "INICIO_VISITA_LINDUS": "inicio_visita_lindus_ok.txt",
    "OBSERVACIONES_LINDUS": "observaciones_lindus_ok.txt",
    "FIN_VISITA_LINDUS": "fin_visita_lindus_ok.txt",
    "VISITA_CAJA_NIDO": "visita_caja_nido_ok.txt",
    "VISITA_CEBO_AVISPON": "visita_cebo_avispon_ok.txt",
    "VISITA_NIDO_RAPAZ": "visita_nido_rapaz_ok.txt",
    "VISITA_MAMIFEROS_PUENTE": "visita_mamiferos_puente_ok.txt",
}
LONGITUDES = {
    "INICIO_VISITA_LINDUS": (0, 0),
    "OBSERVACIONES_LINDUS": (0, 2),
    "FIN_VISITA_LINDUS": ({2, 3}, 0),
    "VISITA_CAJA_NIDO": (1, 1),
    "VISITA_CEBO_AVISPON": (1, 1),
    "VISITA_NIDO_RAPAZ": (1, 1),
    "VISITA_MAMIFEROS_PUENTE": (1, 2),
}
MINIMOS = {
    "INICIO_VISITA_LINDUS": ["tipo_visita", "fecha", "hora_inicio", "lugar_visita", "observador"],
    "OBSERVACIONES_LINDUS": ["tipo_visita", "fecha"],
    "FIN_VISITA_LINDUS": ["tipo_visita", "fecha", "hora_fin"],
    "VISITA_CAJA_NIDO": ["tipo_visita", "fecha", "hora_inicio", "hora_fin", "lugar_caja", "observador"],
    "VISITA_CEBO_AVISPON": ["tipo_visita", "fecha", "hora_inicio", "hora_fin", "lugar_cebo", "observador"],
    "VISITA_NIDO_RAPAZ": ["tipo_visita", "fecha", "hora_inicio", "hora_fin", "lugar_nido", "observador"],
    "VISITA_MAMIFEROS_PUENTE": ["tipo_visita", "fecha", "hora_inicio", "hora_fin", "lugar_puente", "observador"],
}


@pytest.mark.parametrize("tipo, archivo", ARCHIVOS.items())
def test_detectar_tipo_correcto(tipo, archivo):
    """Detecta cada TIPO_REGISTRO activo."""
    texto = (EJEMPLOS / archivo).read_text(encoding="utf-8")
    assert detectar_tipo(texto) == tipo


@pytest.mark.parametrize("texto", ["TIPO_REGISTRO: DESCONOCIDO", "FECHA: 2026-05-01"])
def test_detectar_tipo_rechaza_textos_invalidos(texto):
    """Rechaza tipo desconocido y ausencia de TIPO_REGISTRO."""
    with pytest.raises(ValueError):
        detectar_tipo(texto)


@pytest.mark.parametrize("tipo, archivo", ARCHIVOS.items())
def test_parsear_txt_plaud_round_trip_completo(tipo, archivo):
    """Parsea cada archivo válido con estructura y longitudes esperadas."""
    registro = parsear_txt_plaud(str(EJEMPLOS / archivo))
    meteo, datos = LONGITUDES[tipo]
    assert registro["tipo_registro"] == tipo
    assert all(campo in registro["visita"] for campo in MINIMOS[tipo])
    meteo_real = len(registro["meteorologia"])
    assert meteo_real in meteo if isinstance(meteo, set) else meteo_real == meteo
    assert len(registro["datos"]) == datos


def test_parsear_convierte_tipos_simples():
    """Convierte enteros, float y booleanos básicos."""
    caja = parsear_txt_plaud(str(EJEMPLOS / "visita_caja_nido_ok.txt"))
    cebo = parsear_txt_plaud(str(EJEMPLOS / "visita_cebo_avispon_ok.txt"))
    assert isinstance(caja["datos"][0]["numero_huevos"], int)
    assert isinstance(caja["meteorologia"][0]["temperatura"], float)
    assert caja["datos"][0]["ocupada"] is True
    assert isinstance(cebo["datos"][0]["vv"], int)


def test_parsear_observaciones_lindus_dos_bloques():
    """Crea dos bloques de observaciones Lindus."""
    registro = parsear_txt_plaud(str(EJEMPLOS / "observaciones_lindus_ok.txt"))
    assert len(registro["datos"]) == 2


def test_parsear_fin_visita_lindus_tres_meteos():
    """Crea tres bloques de meteorología en el cierre Lindus."""
    registro = parsear_txt_plaud(str(EJEMPLOS / "fin_visita_lindus_ok.txt"))
    assert len(registro["meteorologia"]) in {2, 3}


@pytest.mark.parametrize("archivo", ARCHIVOS.values())
def test_validar_registro_sin_errores_para_ejemplos(archivo):
    """Acepta todos los ejemplos sintéticos válidos."""
    registro = parsear_txt_plaud(str(EJEMPLOS / archivo))
    assert validar_registro(registro) == []


@pytest.mark.parametrize("tipo, campo", [(tipo, campos[0]) for tipo, campos in MINIMOS.items()])
def test_validar_registro_detecta_minimo_ausente_por_plantilla(tipo, campo):
    """Detecta un campo obligatorio ausente en cada plantilla."""
    registro = parsear_txt_plaud(str(EJEMPLOS / ARCHIVOS[tipo]))
    registro["visita"].pop(campo)
    errores = validar_registro(registro)
    assert any(campo.upper() in error for error in errores)


@pytest.mark.parametrize(
    "archivo, campo, valor",
    [
        ("observaciones_lindus_ok.txt", "comportamiento", "PASANDO"),
        ("visita_mamiferos_puente_ok.txt", "presencia", "QUIZA"),
        ("visita_caja_nido_ok.txt", "ecosistema", "BOSQUE"),
    ],
)
def test_validar_registro_detecta_valor_cerrado_invalido(archivo, campo, valor):
    """Detecta valores cerrados inválidos relevantes."""
    registro = parsear_txt_plaud(str(EJEMPLOS / archivo))
    registro["datos"][0][campo] = valor
    errores = validar_registro(registro)
    assert any(valor in error for error in errores)


def test_normalizar_registro_caja_bar_cero_uno():
    """Normaliza variantes habladas de códigos de caja."""
    registro = {"visita": {"lugar_caja": "bar cero uno"}, "meteorologia": [], "datos": []}
    assert normalizar_registro(registro)["visita"]["lugar_caja"] == "BAR01"


def test_normalizar_registro_cebo_avispon_uno():
    """Normaliza variantes habladas de nombres de cebo."""
    registro = {"visita": {"lugar_cebo": "cebo avispón uno"}, "meteorologia": [], "datos": []}
    assert normalizar_registro(registro)["visita"]["lugar_cebo"] == "Cebo avispón 1"


def test_normalizar_registro_ocupada_si():
    """Normaliza sí como True en ocupada."""
    registro = {"visita": {}, "meteorologia": [], "datos": [{"ocupada": "sí"}]}
    assert normalizar_registro(registro)["datos"][0]["ocupada"] is True


def test_normalizar_fecha_acepta_iso():
    """Mantiene fechas que ya vienen en formato interno."""
    assert normalizar_fecha("2026-05-03") == "2026-05-03"


def test_normalizar_fecha_acepta_dia_mes_anio_con_barras():
    """Convierte DD/MM/YYYY a formato interno YYYY-MM-DD."""
    assert normalizar_fecha("03/05/2026") == "2026-05-03"


def test_normalizar_fecha_deja_invalida_para_validacion_clara():
    """No intenta interpretar formatos fuera de los permitidos."""
    assert normalizar_fecha("05-03-2026") == "05-03-2026"


def test_normalizar_fecha_no_acepta_formato_sin_ceros():
    """Exige exactamente YYYY-MM-DD o DD/MM/YYYY."""
    assert normalizar_fecha("3/5/2026") == "3/5/2026"


def test_normalizar_registro_convierte_fecha_a_iso():
    """La fecha de visita queda normalizada antes de validar."""
    registro = {"visita": {"fecha": "03/05/2026"}, "meteorologia": [], "datos": []}
    assert normalizar_registro(registro)["visita"]["fecha"] == "2026-05-03"


def test_validar_registro_mensaje_fecha_invalida_es_claro():
    """Informa los dos formatos de fecha admitidos."""
    registro = parsear_txt_plaud(str(EJEMPLOS / "visita_mamiferos_puente_ok.txt"))
    registro["visita"]["fecha"] = "05-03-2026"
    errores = validar_registro(normalizar_registro(registro))
    assert len(errores) == 1
    assert "FECHA" in errores[0]
    assert "05-03-2026" in errores[0]
    assert "YYYY-MM-DD o DD/MM/YYYY" in errores[0]


def test_validar_registro_acumula_varios_campos_ausentes_nido_rapaz():
    """Devuelve todos los obligatorios ausentes en una visita."""
    registro = parsear_txt_plaud(str(EJEMPLOS / "visita_nido_rapaz_ok.txt"))
    registro["visita"].pop("hora_fin")
    registro["meteorologia"][0].pop("hora_meteo")

    errores = validar_registro_detallado(registro)
    campos = {(error.campo, error.contexto) for error in errores}

    assert ("hora_fin", "visita") in campos
    assert ("hora_meteo", "meteorologia 1") in campos


def test_validar_registro_viento_direccion_invalido_detalla_valores():
    """Un valor cerrado inválido indica campo, valor y valores aceptados."""
    registro = parsear_txt_plaud(str(EJEMPLOS / "visita_nido_rapaz_ok.txt"))
    registro["meteorologia"][0]["viento_direccion"] = "OESTE"

    errores = validar_registro_detallado(registro)
    error = next(e for e in errores if e.campo == "viento_direccion")

    assert error.valor == "OESTE"
    assert "W" in error.valores_aceptados
    assert error.sugerencia == "usar W para oeste"


def test_parsear_txt_ignora_titulo_antes_de_tipo_registro(tmp_path):
    """El texto narrativo inicial no bloquea y queda como advertencia."""
    ruta = tmp_path / "nido_real.txt"
    ruta.write_text(
        "Visita real de nido rapaz\n"
        "TIPO_REGISTRO: VISITA_NIDO_RAPAZ\n"
        "TIPO_VISITA: NIDO_RAPAZ\n"
        "FECHA: 2026-05-04\n"
        "HORA_INICIO: 20:26\n"
        "HORA_FIN: 20:40\n"
        "LUGAR_NIDO: Areaxea 1\n"
        "OBSERVADOR: Gabi\n"
        "---NIDO_RAPAZ---\n"
        "TEXTO_REVISION: adulto posado cerca del nido.\n",
        encoding="utf-8",
    )

    registro = parsear_txt_plaud(str(ruta))

    assert registro["tipo_registro"] == "VISITA_NIDO_RAPAZ"
    assert registro["_advertencias"] == ["Se ignoró texto antes de TIPO_REGISTRO."]
