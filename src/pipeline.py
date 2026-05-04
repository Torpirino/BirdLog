"""Orquesta el flujo completo Plaud → Supabase → backup."""

from pathlib import Path
from tempfile import TemporaryDirectory

from src.backup.exportar import hacer_backup
from src.config import cargar_config_pipeline
from src.conexion import get_cliente
from src.diagnosticos import ErrorDetalle, PipelineError, mensaje_pipeline
from src.drive.cliente import get_drive
from src.drive.operaciones import descargar_archivo, listar_txt, mover_archivo
from src.insercion.escritura import insertar_registro
from src.parser.normalizacion import normalizar_registro
from src.parser.plaud import parsear_txt_plaud
from src.parser.validacion import validar_registro_detallado


def procesar_drive() -> list[dict]:
    """Procesa todos los TXT de la carpeta de entrada."""
    config = cargar_config_pipeline()
    cliente = get_cliente()
    drive = get_drive()
    resultados = []
    for archivo in listar_txt(config.DRIVE_ENTRADA_ID, drive):
        resultados.append(_procesar_archivo_drive(archivo, config, cliente, drive))
    return resultados


def _procesar_archivo_drive(archivo: dict, config, cliente, drive) -> dict:
    """Procesa un TXT concreto de Drive."""
    with TemporaryDirectory() as temporal:
        ruta = descargar_archivo(archivo["id"], Path(temporal) / archivo["name"], drive)
        try:
            resumen = procesar_txt_local(ruta, cliente, drive)
        except PipelineError as exc:
            mover_archivo(archivo, config.DRIVE_ERRORES_ID, drive)
            return _resultado_error(archivo, str(exc), exc.errores, exc.fase)
        except ValueError as exc:
            mover_archivo(archivo, config.DRIVE_ERRORES_ID, drive)
            error = _error_generico("parseo", str(exc))
            return _resultado_error(archivo, mensaje_pipeline(archivo["name"], [error]), [error], "parseo")
        mover_archivo(archivo, config.DRIVE_PROCESADOS_ID, drive)
        return {"archivo": archivo["name"], "estado": "procesado", "resumen": resumen}


def procesar_txt_local(ruta: str | Path, cliente, drive=None, drive_backups_id: str | None = None) -> dict:
    """Parsea, valida, inserta y hace backup de un TXT local."""
    archivo = Path(ruta).name
    try:
        registro = normalizar_registro(parsear_txt_plaud(str(ruta)))
    except ValueError as exc:
        raise PipelineError(archivo, "parseo", [_error_generico("parseo", str(exc))]) from exc
    errores = validar_registro_detallado(registro)
    if errores:
        raise PipelineError(archivo, "validación", _con_advertencias(registro, errores))
    try:
        resumen = insertar_registro(registro, cliente)
    except PipelineError as exc:
        raise PipelineError(archivo, exc.fase, _con_advertencias(registro, exc.errores)) from exc
    carpeta_backup = hacer_backup(cliente)
    resumen["backup"] = str(carpeta_backup)
    return resumen


def _con_advertencias(registro: dict, errores: list[ErrorDetalle]) -> list[ErrorDetalle]:
    """Añade advertencias no bloqueantes al diagnóstico de un fallo."""
    advertencias = [
        ErrorDetalle(
            fase="parseo",
            campo="estructura",
            motivo=advertencia,
            sugerencia="elimina títulos o texto narrativo antes de TIPO_REGISTRO",
            accion="advertencia no bloqueante",
            advertencia=True,
        )
        for advertencia in registro.get("_advertencias", [])
    ]
    return [*advertencias, *errores]


def _resultado_error(archivo: dict, mensaje: str, errores: list[ErrorDetalle] | None = None, fase: str = "procesamiento") -> dict:
    """Devuelve un resumen de error de procesamiento."""
    return {
        "archivo": archivo["name"],
        "estado": "error",
        "mensaje": mensaje,
        "fase": fase,
        "errores": [error.a_dict() for error in errores or []],
    }


def _error_generico(fase: str, mensaje: str) -> ErrorDetalle:
    """Convierte un fallo no estructurado en diagnóstico de usuario."""
    return ErrorDetalle(
        fase=fase,
        campo="archivo",
        motivo=mensaje,
        sugerencia="revisa que el TXT siga la plantilla Plaud correspondiente",
    )
