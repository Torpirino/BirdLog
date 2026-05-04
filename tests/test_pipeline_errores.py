"""Tests de diagnósticos del pipeline sin Drive ni Supabase real."""

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.diagnosticos import PipelineError
from src.pipeline import procesar_txt_local


def test_pipeline_caso_real_nido_rapaz_devuelve_error_multiple(tmp_path):
    """El caso real de nidos rapaces acumula todos los problemas de validación."""
    ruta = tmp_path / "nido_rapaz_real.txt"
    ruta.write_text(
        "Revisión nido rapaz Areaxea\n\n"
        "TIPO_REGISTRO: VISITA_NIDO_RAPAZ\n"
        "TIPO_VISITA: NIDO_RAPAZ\n"
        "FECHA: 2026-05-04\n"
        "HORA_INICIO: 20:26\n"
        "LUGAR_NIDO: Areaxea 1\n"
        "OBSERVADOR: Gabi\n"
        "OBSERVACIONES_VISITA: revisión hecha desde distancia segura.\n\n"
        "---METEOROLOGIA---\n"
        "TEMPERATURA: 18\n"
        "NUBOSIDAD: 4\n"
        "VIENTO_DIRECCION: OESTE\n"
        "VIENTO_INTENSIDAD: FLOJO\n"
        "PRECIPITACION: NULA\n"
        "VISIBILIDAD: BUENA\n\n"
        "---NIDO_RAPAZ---\n"
        "ESPECIE: Milano real\n"
        "TEXTO_REVISION: adulto posado cerca del nido sin molestias aparentes.\n"
        "OBSERVACIONES_NIDO: prueba real del pipeline de nidos rapaces.\n",
        encoding="utf-8",
    )

    with pytest.raises(PipelineError) as excinfo:
        procesar_txt_local(ruta, cliente=object())

    errores = excinfo.value.errores
    campos = [error.campo for error in errores]

    assert "estructura" in campos
    assert "hora_fin" in campos
    assert "hora_meteo" in campos
    assert "viento_direccion" in campos
    assert "OESTE" in str(excinfo.value)
    assert "usar W para oeste" in str(excinfo.value)
    assert "no insertado; movido a errores; sin backup" in str(excinfo.value)
