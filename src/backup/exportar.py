"""Exporta tablas de Supabase a CSV local."""

from csv import DictWriter
from datetime import date
from pathlib import Path
from shutil import rmtree

# Todas las tablas del esquema v3 (sql/003_esquema_v3.sql).
TABLAS_BACKUP = [
    "especies",
    "observadores",
    "lugares",
    "visitas",
    "meteorologia",
    "lindus",
    "cajas_nido",
    "nidos_rapaces",
    "cebos_avispones",
    "mamiferos_puentes",
    "fototrampeo",
    "cuaderno_campo",
    "estudio_campo",
    "castor_rastros",
    "fotos",
]
RETENCION_BACKUPS = 30


def hacer_backup(cliente, carpeta_base: str = "backups") -> Path:
    """Exporta todas las tablas a CSV y devuelve la carpeta creada."""
    carpeta = Path(carpeta_base) / f"backup_{date.today().isoformat()}"
    carpeta.mkdir(parents=True, exist_ok=True)
    for tabla in TABLAS_BACKUP:
        filas = _leer_tabla(cliente, tabla)
        _escribir_csv(carpeta / f"{tabla}.csv", filas)
    _aplicar_retencion(Path(carpeta_base))
    return carpeta


def _aplicar_retencion(carpeta_base: Path, maximo: int = RETENCION_BACKUPS) -> None:
    """Conserva solo los backups más recientes (por nombre de fecha)."""
    carpetas = sorted(ruta for ruta in carpeta_base.glob("backup_*") if ruta.is_dir())
    for antigua in carpetas[:-maximo]:
        rmtree(antigua, ignore_errors=True)


def _leer_tabla(cliente, tabla: str) -> list[dict]:
    """Lee una tabla completa desde Supabase."""
    filas = []
    inicio = 0
    tamano = 1000
    while True:
        consulta = cliente.table(tabla).select("*")
        if not hasattr(consulta, "range"):
            return getattr(consulta.execute(), "data", None) or []
        respuesta = consulta.range(inicio, inicio + tamano - 1).execute()
        lote = getattr(respuesta, "data", None) or []
        filas.extend(lote)
        if len(lote) < tamano:
            return filas
        inicio += tamano


def _escribir_csv(ruta: Path, filas: list[dict]) -> None:
    """Escribe filas como CSV aunque la tabla esté vacía."""
    campos = sorted({clave for fila in filas for clave in fila})
    with ruta.open("w", encoding="utf-8", newline="") as archivo:
        if not campos:
            return
        writer = DictWriter(archivo, fieldnames=campos)
        writer.writeheader()
        writer.writerows(filas)
