"""Tests de presentación de resultados en la app pipeline."""

from __future__ import annotations

from pathlib import Path
import sys

RAIZ_PROYECTO = Path(__file__).resolve().parents[1]
if str(RAIZ_PROYECTO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROYECTO))

from app_pipeline.lib import ui
from app_pipeline.lib.estados import (
    ESTADO_ERROR,
    ESTADO_INCOMPLETO,
    ESTADO_OK,
    ESTADO_PENDIENTE,
    ResultadoArchivo,
)


def _resultado(estado: str, mensaje: str = "mensaje de prueba") -> ResultadoArchivo:
    """Construye un resultado mínimo para tests de UI."""
    return ResultadoArchivo(
        nombre=f"{estado.lower()}.txt",
        estado=estado,
        etapa="Validación",
        mensaje=mensaje,
        txt_movido_a="errores" if estado != ESTADO_OK else "procesados",
        insertado_supabase=estado == ESTADO_OK,
        backup_creado=estado == ESTADO_OK,
    )


def test_render_resumen_global_muestra_ok_en_verde(monkeypatch):
    """Un resultado correcto pinta el resumen en verde."""
    llamadas = []
    monkeypatch.setattr(ui.st, "success", lambda texto, **_: llamadas.append(("success", texto)))

    ui.render_resumen_global([_resultado(ESTADO_OK)])

    assert llamadas == [("success", "1 grabación procesada correctamente.")]


def test_render_resumen_global_muestra_error_en_rojo(monkeypatch):
    """Un resultado con error pinta el resumen en rojo y no lanza NameError."""
    llamadas = []
    monkeypatch.setattr(ui.st, "error", lambda texto, **_: llamadas.append(("error", texto)))

    ui.render_resumen_global([_resultado(ESTADO_ERROR)])

    assert llamadas == [("error", "1 con error.")]


def test_render_resumen_global_muestra_incompleto_en_amarillo(monkeypatch):
    """Un resultado incompleto pinta el resumen en amarillo."""
    llamadas = []
    monkeypatch.setattr(ui.st, "warning", lambda texto, **_: llamadas.append(("warning", texto)))

    ui.render_resumen_global([_resultado(ESTADO_INCOMPLETO)])

    assert llamadas == [("warning", "1 con un dato de catálogo pendiente.")]


def test_render_resumen_global_muestra_pendiente_en_info(monkeypatch):
    """Un resultado pendiente queda cubierto como estado conocido."""
    llamadas = []
    monkeypatch.setattr(ui.st, "info", lambda texto, **_: llamadas.append(("info", texto)))

    ui.render_resumen_global([_resultado(ESTADO_PENDIENTE)])

    assert llamadas == [("info", "1 sin procesar.")]


def test_tabla_resumen_incluye_mensaje_de_error_y_movimiento(monkeypatch):
    """El resumen por archivo muestra el mensaje real del error y el movimiento a errores."""
    resultado = _resultado(
        ESTADO_ERROR,
        "El archivo mamiferos.txt no es válido:\n- FECHA inválida en visita: 03/05/2026",
    )
    capturadas = []
    monkeypatch.setattr(ui.st, "dataframe", lambda df, **_: capturadas.append(df))

    ui._tabla_resumen([resultado])

    fila = capturadas[0].iloc[0]
    assert fila["archivo"] == "error.txt"
    assert "Error" in fila["estado"]
    assert fila["movimiento_drive"] == "errores"
    assert "FECHA inválida" in fila["mensaje"]


def test_lineas_diagnostico_desglosan_fase_campo_valor_y_accion():
    """El detalle por archivo desglosa fase, campo, valor, motivo y acción."""
    diagnostico = {
        "fase": "validación",
        "campo": "viento_direccion",
        "valor": "OESTE",
        "motivo": "valor cerrado no válido",
        "accion": "no insertado; movido a errores; sin backup",
        "valores_aceptados": ["N", "W"],
        "sugerencia": "usar W para oeste",
    }

    lineas = "\n".join(ui._lineas_diagnostico(diagnostico))

    assert "Fase: validación" in lineas
    assert "Campo: viento_direccion" in lineas
    assert "Valor recibido: 'OESTE'" in lineas
    assert "Acción realizada: no insertado; movido a errores; sin backup" in lineas
    assert "Valores aceptados: N, W" in lineas
    assert "Sugerencia: usar W para oeste" in lineas
