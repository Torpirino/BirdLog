"""Tests del orden lógico Lindus en el pipeline Drive."""

from dataclasses import make_dataclass
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app_pipeline.lib.estados import ESTADO_OK, ResultadoArchivo
from app_pipeline.lib.ui import _mensajes_registro
from src.insercion.escritura import insertar_registro
from src.pipeline import ordenar_descargas_lindus, procesar_drive
from src.parser.plaud import parsear_txt_plaud

from tests.test_escritura import ClienteFalso


def _descarga(tmp_path: Path, nombre: str, texto: str, indice: int, momento: str = "") -> dict:
    """Crea una descarga local con metadatos Drive falsos."""
    ruta = tmp_path / nombre
    ruta.write_text(texto, encoding="utf-8")
    archivo = {"id": nombre, "name": nombre, "parents": ["entrada"]}
    if momento:
        archivo["createdTime"] = momento
    return {"archivo": archivo, "ruta": ruta, "indice": indice}


def _txt_lindus(tipo: str, fecha: str = "2026-05-04") -> str:
    """TXT mínimo para detectar tipo y fecha Lindus."""
    return f"TIPO_REGISTRO: {tipo}\nTIPO_VISITA: LINDUS\nFECHA: {fecha}\n"


def test_ordena_lindus_desordenados_inicio_observaciones_fin(tmp_path):
    """FIN, OBSERVACIONES, INICIO se reordenan por tipo lógico."""
    descargas = [
        _descarga(tmp_path, "3_fin.txt", _txt_lindus("FIN_VISITA_LINDUS"), 0),
        _descarga(tmp_path, "2_obs.txt", _txt_lindus("OBSERVACIONES_LINDUS"), 1),
        _descarga(tmp_path, "1_inicio.txt", _txt_lindus("INICIO_VISITA_LINDUS"), 2),
    ]

    orden = [d["archivo"]["name"] for d in ordenar_descargas_lindus(descargas)]

    assert orden == ["1_inicio.txt", "2_obs.txt", "3_fin.txt"]


def test_dos_observaciones_quedan_entre_inicio_y_fin_por_hora_drive(tmp_path):
    """Las observaciones mantienen orden estable por createdTime."""
    descargas = [
        _descarga(tmp_path, "fin.txt", _txt_lindus("FIN_VISITA_LINDUS"), 0, "2026-05-04T12:00:00Z"),
        _descarga(tmp_path, "obs_b.txt", _txt_lindus("OBSERVACIONES_LINDUS"), 1, "2026-05-04T10:05:00Z"),
        _descarga(tmp_path, "inicio.txt", _txt_lindus("INICIO_VISITA_LINDUS"), 2, "2026-05-04T09:00:00Z"),
        _descarga(tmp_path, "obs_a.txt", _txt_lindus("OBSERVACIONES_LINDUS"), 3, "2026-05-04T10:00:00Z"),
    ]

    orden = [d["archivo"]["name"] for d in ordenar_descargas_lindus(descargas)]

    assert orden == ["inicio.txt", "obs_a.txt", "obs_b.txt", "fin.txt"]


def test_otros_tipos_conservan_su_posicion_relativa(tmp_path):
    """Los no Lindus no se mueven de su hueco en el lote."""
    caja = "TIPO_REGISTRO: VISITA_CAJA_NIDO\nTIPO_VISITA: CAJA_NIDO\nFECHA: 2026-05-04\n"
    descargas = [
        _descarga(tmp_path, "fin.txt", _txt_lindus("FIN_VISITA_LINDUS"), 0),
        _descarga(tmp_path, "caja.txt", caja, 1),
        _descarga(tmp_path, "inicio.txt", _txt_lindus("INICIO_VISITA_LINDUS"), 2),
    ]

    orden = [d["archivo"]["name"] for d in ordenar_descargas_lindus(descargas)]

    assert orden == ["inicio.txt", "caja.txt", "fin.txt"]


def test_fin_lindus_sin_visita_abierta_no_crea_visita():
    """FIN_VISITA_LINDUS no crea visita si no hay inicio abierto."""
    cliente = ClienteFalso()
    cliente.datos["visitas"] = []
    registro = {
        "tipo_registro": "FIN_VISITA_LINDUS",
        "visita": {"tipo_visita": "LINDUS", "fecha": "2026-05-04", "hora_fin": "12:00"},
        "meteorologia": [],
        "datos": [],
    }

    with pytest.raises(ValueError, match="No hay visita Lindus abierta para cerrar en la fecha 2026-05-04"):
        insertar_registro(registro, cliente)

    assert cliente.datos["visitas"] == []


def test_observaciones_lindus_sin_visita_abierta_mantiene_error_claro():
    """OBSERVACIONES_LINDUS sigue fallando si no hay visita abierta."""
    cliente = ClienteFalso()
    cliente.datos["visitas"] = []
    registro = {
        "tipo_registro": "OBSERVACIONES_LINDUS",
        "visita": {"tipo_visita": "LINDUS", "fecha": "2026-05-04"},
        "meteorologia": [],
        "datos": [{"especie": "Milano negro", "hora": "10:00", "numero": 1, "comportamiento": "MIGRADOR"}],
    }

    with pytest.raises(ValueError, match="No hay visita Lindus abierta para añadir observaciones en la fecha 2026-05-04"):
        insertar_registro(registro, cliente)


def test_procesar_drive_devuelve_resultados_en_orden_lindus(monkeypatch, tmp_path):
    """El reporting recibe resultados en el orden real de procesamiento."""
    import src.pipeline as pipeline

    Config = make_dataclass("Config", [("DRIVE_ENTRADA_ID", str), ("DRIVE_ERRORES_ID", str), ("DRIVE_PROCESADOS_ID", str)])
    archivos = [
        {"id": "fin", "name": "fin.txt", "parents": ["entrada"], "createdTime": "2026-05-04T12:00:00Z"},
        {"id": "obs", "name": "obs.txt", "parents": ["entrada"], "createdTime": "2026-05-04T10:00:00Z"},
        {"id": "inicio", "name": "inicio.txt", "parents": ["entrada"], "createdTime": "2026-05-04T09:00:00Z"},
    ]
    textos = {
        "fin": _txt_lindus("FIN_VISITA_LINDUS"),
        "obs": _txt_lindus("OBSERVACIONES_LINDUS"),
        "inicio": _txt_lindus("INICIO_VISITA_LINDUS"),
    }
    procesados = []

    def descargar(archivo_id, destino, _drive):
        ruta = Path(destino)
        ruta.write_text(textos[archivo_id], encoding="utf-8")
        return ruta

    def procesar_local(ruta, _cliente, _drive):
        procesados.append(Path(ruta).name)
        return {"id_visita": len(procesados), "backup": "/tmp/backup"}

    monkeypatch.setattr(pipeline, "cargar_config_pipeline", lambda: Config("entrada", "errores", "procesados"))
    monkeypatch.setattr(pipeline, "get_cliente", lambda: object())
    monkeypatch.setattr(pipeline, "get_drive", lambda: object())
    monkeypatch.setattr(pipeline, "listar_txt", lambda _carpeta, _drive: archivos)
    monkeypatch.setattr(pipeline, "descargar_archivo", descargar)
    monkeypatch.setattr(pipeline, "procesar_txt_local", procesar_local)
    monkeypatch.setattr(pipeline, "mover_archivo", lambda *_args: None)

    resultados = procesar_drive()

    assert procesados == ["inicio.txt", "obs.txt", "fin.txt"]
    assert [r["archivo"] for r in resultados] == procesados


def test_registro_pipeline_refleja_orden_recibido():
    """El registro mantiene el orden de resultados ya ordenado por pipeline."""
    resultados = [
        ResultadoArchivo("inicio.txt", ESTADO_OK, "Backup", "visita id=1", "procesados", True, True),
        ResultadoArchivo("obs.txt", ESTADO_OK, "Backup", "visita id=1", "procesados", True, True),
        ResultadoArchivo("fin.txt", ESTADO_OK, "Backup", "visita id=1", "procesados", True, True),
    ]

    mensajes = "\n".join(_mensajes_registro(resultados))

    assert mensajes.index("Archivo: inicio.txt") < mensajes.index("Archivo: obs.txt")
    assert mensajes.index("Archivo: obs.txt") < mensajes.index("Archivo: fin.txt")
