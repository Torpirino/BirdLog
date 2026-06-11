"""Tests del backup CSV local (sin Supabase real)."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.backup.exportar import RETENCION_BACKUPS, TABLAS_BACKUP, hacer_backup


class ConsultaFalsa:
    """Consulta mínima que devuelve una tabla vacía."""

    def select(self, _columnas):
        return self

    def range(self, _inicio, _fin):
        return self

    def execute(self):
        class Respuesta:
            data = []

        return Respuesta()


class ClienteFalso:
    """Cliente Supabase falso que registra las tablas consultadas."""

    def __init__(self):
        self.tablas_consultadas = []

    def table(self, tabla):
        self.tablas_consultadas.append(tabla)
        return ConsultaFalsa()


def test_backup_incluye_todas_las_tablas_v3(tmp_path):
    """El backup exporta todas las tablas del esquema v3, incluidas las 4 nuevas."""
    cliente = ClienteFalso()

    carpeta = hacer_backup(cliente, carpeta_base=str(tmp_path))

    for tabla in ("fototrampeo", "cuaderno_campo", "estudio_campo", "castor_rastros"):
        assert tabla in TABLAS_BACKUP
        assert (carpeta / f"{tabla}.csv").exists()
    assert cliente.tablas_consultadas == TABLAS_BACKUP


def test_backup_aplica_retencion_de_carpetas(tmp_path):
    """Las carpetas más antiguas se eliminan al superar la retención."""
    for dia in range(1, RETENCION_BACKUPS + 5):
        (tmp_path / f"backup_2025-01-{dia:02d}").mkdir()

    hacer_backup(ClienteFalso(), carpeta_base=str(tmp_path))

    carpetas = sorted(ruta.name for ruta in tmp_path.glob("backup_*"))
    assert len(carpetas) == RETENCION_BACKUPS
    # Sobreviven las más recientes; las primeras de enero desaparecen.
    assert "backup_2025-01-01" not in carpetas
    assert carpetas[-1].startswith("backup_")


def test_backup_no_borra_otros_archivos(tmp_path):
    """La retención solo toca carpetas backup_*, nunca otros contenidos."""
    (tmp_path / "edicion_traza.log").write_text("traza", encoding="utf-8")
    (tmp_path / "notas").mkdir()

    hacer_backup(ClienteFalso(), carpeta_base=str(tmp_path))

    assert (tmp_path / "edicion_traza.log").exists()
    assert (tmp_path / "notas").exists()
