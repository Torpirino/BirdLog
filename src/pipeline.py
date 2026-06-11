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

PRIORIDAD_LINDUS = {
    "INICIO_VISITA_LINDUS": 1,
    "OBSERVACIONES_LINDUS": 2,
    "FIN_VISITA_LINDUS": 3,
}


def procesar_drive(al_procesar=None) -> list[dict]:
    """Procesa todos los TXT de la carpeta de entrada.

    `al_procesar(resultado)` se invoca tras cada archivo para poder
    informar del progreso sin esperar al final del lote.
    """
    config = cargar_config_pipeline()
    cliente = get_cliente()
    drive = get_drive()
    resultados = []
    archivos = listar_txt(config.DRIVE_ENTRADA_ID, drive)
    with TemporaryDirectory() as temporal:
        descargas = _descargar_lote(archivos, Path(temporal), drive)
        for descarga in ordenar_descargas_lindus(descargas):
            resultado = _procesar_descarga_drive(descarga, config, cliente, drive)
            resultados.append(resultado)
            if al_procesar is not None:
                al_procesar(resultado)
    return resultados


def _descargar_lote(archivos: list[dict], carpeta_temporal: Path, drive) -> list[dict]:
    """Descarga todos los archivos para poder ordenarlos antes de insertar."""
    descargas = []
    for indice, archivo in enumerate(archivos):
        ruta = descargar_archivo(archivo["id"], carpeta_temporal / archivo["name"], drive)
        descargas.append({"archivo": archivo, "ruta": ruta, "indice": indice})
    return descargas


def _procesar_descarga_drive(descarga: dict, config, cliente, drive) -> dict:
    """Procesa un TXT ya descargado y mueve el archivo de Drive."""
    archivo = descarga["archivo"]
    try:
        resumen = procesar_txt_local(descarga["ruta"], cliente, drive)
    except PipelineError as exc:
        movido = _mover_seguro(archivo, config.DRIVE_ERRORES_ID, drive)
        return _resultado_error(archivo, str(exc), exc.errores, exc.fase, movido)
    except ValueError as exc:
        movido = _mover_seguro(archivo, config.DRIVE_ERRORES_ID, drive)
        error = _error_generico("parseo", str(exc))
        return _resultado_error(archivo, mensaje_pipeline(archivo["name"], [error]), [error], "parseo", movido)
    movido = _mover_seguro(archivo, config.DRIVE_PROCESADOS_ID, drive)
    resultado = {"archivo": archivo["name"], "estado": "procesado", "resumen": resumen, "movido": movido}
    if not movido:
        resumen["aviso"] = AVISO_NO_MOVIDO_PROCESADO
    return resultado


AVISO_NO_MOVIDO_PROCESADO = (
    "Los datos SÍ se insertaron, pero el archivo no se pudo mover en Drive "
    "y sigue en 01_entrada. Muévelo a mano a 02_procesados antes de volver "
    "a procesar, o los datos se duplicarán."
)


def _mover_seguro(archivo: dict, carpeta_destino: str, drive) -> bool:
    """Mueve el archivo en Drive sin tumbar el lote si Drive falla."""
    try:
        mover_archivo(archivo, carpeta_destino, drive)
        return True
    except Exception:
        return False


def ordenar_descargas_lindus(descargas: list[dict]) -> list[dict]:
    """Ordena solo los TXT Lindus, dejando los demás en sus posiciones."""
    metadatos = [_metadatos_orden(descarga) for descarga in descargas]
    lindus_ordenados = sorted(
        [meta for meta in metadatos if meta["es_lindus"]],
        key=_clave_lindus,
    )
    iter_lindus = iter(lindus_ordenados)
    ordenados = []
    for meta in metadatos:
        ordenados.append(next(iter_lindus)["descarga"] if meta["es_lindus"] else meta["descarga"])
    return ordenados


def _metadatos_orden(descarga: dict) -> dict:
    """Lee tipo y fecha sin insertar para decidir el orden del lote."""
    try:
        registro = normalizar_registro(parsear_txt_plaud(str(descarga["ruta"])))
    except ValueError:
        return {"descarga": descarga, "es_lindus": False, "fecha": "", "prioridad": 99, "estable": _clave_estable(descarga)}
    tipo = registro.get("tipo_registro", "")
    visita = registro.get("visita", {})
    es_lindus = tipo in PRIORIDAD_LINDUS or visita.get("tipo_visita") == "LINDUS"
    return {
        "descarga": descarga,
        "es_lindus": es_lindus,
        "fecha": visita.get("fecha", ""),
        "prioridad": PRIORIDAD_LINDUS.get(tipo, 99),
        "estable": _clave_estable(descarga),
    }


def _clave_lindus(meta: dict) -> tuple:
    """Clave fecha → prioridad lógica → orden estable."""
    return (meta["fecha"], meta["prioridad"], meta["estable"])


def _clave_estable(descarga: dict) -> tuple:
    """Usa hora de Drive si existe y nombre como desempate estable."""
    archivo = descarga["archivo"]
    momento = archivo.get("createdTime") or archivo.get("modifiedTime") or ""
    return (momento, archivo.get("name", ""), descarga.get("indice", 0))


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
    except ValueError as exc:
        raise PipelineError(archivo, "inserción Supabase", [_error_generico("inserción Supabase", str(exc))]) from exc
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


def _resultado_error(archivo: dict, mensaje: str, errores: list[ErrorDetalle] | None = None, fase: str = "procesamiento", movido: bool = True) -> dict:
    """Devuelve un resumen de error de procesamiento."""
    if not movido:
        mensaje += (
            "\nAviso: el archivo no se pudo mover en Drive y sigue en "
            "01_entrada; muévelo a mano a 03_errores."
        )
    return {
        "archivo": archivo["name"],
        "estado": "error",
        "mensaje": mensaje,
        "fase": fase,
        "errores": [error.a_dict() for error in errores or []],
        "movido": movido,
    }


def _error_generico(fase: str, mensaje: str) -> ErrorDetalle:
    """Convierte un fallo no estructurado en diagnóstico de usuario."""
    return ErrorDetalle(
        fase=fase,
        campo="archivo",
        motivo=mensaje,
        sugerencia="revisa que el TXT siga la plantilla Plaud correspondiente",
    )
