"""Tests de inserción con mocks, sin base de datos real."""

from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.insercion.escritura import insertar_registro
from src.diagnosticos import PipelineError
from src.parser.normalizacion import normalizar_registro
from src.parser.plaud import parsear_txt_plaud
from src.parser.validacion import validar_registro

EJEMPLOS = Path(__file__).parent / "ejemplos_plaud"


class Respuesta:
    """Respuesta mínima compatible con supabase-py."""

    def __init__(self, data):
        self.data = data


class TablaFalsa:
    """Simula una tabla Supabase encadenable."""

    def __init__(self, cliente, nombre):
        self.cliente = cliente
        self.nombre = nombre
        self.filtros = []
        self.operacion = "select"
        self.payload = None
        self.columnas = "*"

    def select(self, columnas):
        self.columnas = columnas
        return self

    def eq(self, campo, valor):
        self.filtros.append((campo, valor))
        return self

    def is_(self, campo, valor):
        self.filtros.append((campo, None if valor == "null" else valor))
        return self

    def limit(self, _cantidad):
        return self

    def insert(self, payload):
        self.operacion = "insert"
        self.payload = payload
        return self

    def update(self, payload):
        self.operacion = "update"
        self.payload = payload
        return self

    def execute(self):
        if self.operacion == "insert":
            return self._insertar()
        if self.operacion == "update":
            return self._actualizar()
        return Respuesta(self._seleccionar())

    def _seleccionar(self):
        filas = self.cliente.datos.get(self.nombre, [])
        for campo, valor in self.filtros:
            filas = [fila for fila in filas if fila.get(campo) == valor]
        if self.columnas == "*":
            return filas
        columnas = [columna.strip() for columna in self.columnas.split(",")]
        return [{columna: fila[columna] for columna in columnas} for fila in filas]

    def _insertar(self):
        filas = self.payload if isinstance(self.payload, list) else [self.payload]
        guardadas = []
        for fila in filas:
            guardada = dict(fila)
            self.cliente.contadores[self.nombre] = self.cliente.contadores.get(self.nombre, 0) + 1
            campo_id = self.cliente.ids.get(self.nombre)
            if campo_id:
                guardada[campo_id] = self.cliente.contadores[self.nombre]
            self.cliente.datos.setdefault(self.nombre, []).append(guardada)
            guardadas.append(guardada)
        return Respuesta(guardadas)

    def _actualizar(self):
        filas = self.cliente.datos.get(self.nombre, [])
        actualizadas = []
        for fila in filas:
            if all(fila.get(campo) == valor for campo, valor in self.filtros):
                fila.update(self.payload)
                actualizadas.append(fila)
        return Respuesta(actualizadas)


class ClienteFalso:
    """Cliente Supabase en memoria para escritura."""

    ids = {"visitas": "id_visita", "meteorologia": "id_meteo", "lindus": "id_lindus", "cajas_nido": "id_cajanido"}

    def __init__(self):
        self.contadores = {"visitas": 100, "meteorologia": 200, "lindus": 300, "cajas_nido": 400}
        self.datos = {
            "lugares": [{"id_lugar": 1, "nombre_lugar": "BAR01"}, {"id_lugar": 2, "nombre_lugar": "Lindus"}],
            "observadores": [{"id_observador": 7, "nombre_observador": "Gabi"}],
            "especies": [
                {"id_especie": 11, "nombre_comun": "carbonero común", "nombre_cientifico": "Parus major"},
                {"id_especie": 14, "nombre_comun": "Carbonero común", "nombre_cientifico": "Parus major"},
                {"id_especie": 12, "nombre_comun": "milano negro", "nombre_cientifico": "Milvus migrans"},
                {"id_especie": 15, "nombre_comun": "Milano negro", "nombre_cientifico": "Milvus migrans"},
                {"id_especie": 13, "nombre_comun": "milano real", "nombre_cientifico": "Milvus milvus"},
                {"id_especie": 16, "nombre_comun": "Milano real", "nombre_cientifico": "Milvus milvus"},
            ],
            "visitas": [
                {
                    "id_visita": 50,
                    "tipo_visita": "LINDUS",
                    "fecha": "2026-05-01",
                    "hora_fin": None,
                    "id_lugar": 2,
                    "id_observador": 7,
                }
            ],
        }

    def table(self, nombre):
        return TablaFalsa(self, nombre)


def test_insertar_visita_caja_nido_crea_visita_meteo_y_dato():
    """Inserta una visita de caja nido completa."""
    cliente = ClienteFalso()
    registro = parsear_txt_plaud(str(EJEMPLOS / "visita_caja_nido_ok.txt"))
    resumen = insertar_registro(registro, cliente)
    caja = cliente.datos["cajas_nido"][0]
    assert resumen["id_visita"] == 101
    assert resumen["insertados"] == {"cajas_nido": 1}
    assert cliente.datos["visitas"][-1]["id_lugar"] == 1
    assert cliente.datos["meteorologia"][0]["hora"] == "12:05"
    assert caja["id_especie"] in {11, 14}
    assert "especie" not in caja


def test_insertar_observaciones_lindus_usa_visita_abierta():
    """Inserta observaciones en la visita Lindus abierta del día."""
    cliente = ClienteFalso()
    registro = parsear_txt_plaud(str(EJEMPLOS / "observaciones_lindus_ok.txt"))
    resumen = insertar_registro(registro, cliente)
    assert resumen["id_visita"] == 50
    assert resumen["insertados"] == {"lindus": 2}
    assert resumen["mensaje"] == "Observaciones añadidas a la visita Lindus existente id=50."
    assert [fila["id_especie"] for fila in cliente.datos["lindus"]] in ([12, 13], [15, 16])


def test_insertar_observaciones_lindus_usa_visita_cerrada_unica():
    """Permite recuperar observaciones aunque la visita ya esté cerrada."""
    cliente = ClienteFalso()
    cliente.datos["visitas"][0]["hora_fin"] = "12:30"
    registro = parsear_txt_plaud(str(EJEMPLOS / "observaciones_lindus_ok.txt"))

    resumen = insertar_registro(registro, cliente)

    assert resumen["id_visita"] == 50
    assert "Aviso: la visita ya tenía hora de fin" in resumen["mensaje"]
    assert len(cliente.datos["lindus"]) == 2


def test_insertar_observaciones_lindus_falla_sin_visita_existente():
    """No inserta Lindus si no existe ninguna visita para esa fecha."""
    cliente = ClienteFalso()
    cliente.datos["visitas"] = []
    registro = parsear_txt_plaud(str(EJEMPLOS / "observaciones_lindus_ok.txt"))

    with pytest.raises(
        ValueError,
        match="No existe ninguna visita Lindus para la fecha 2026-05-01",
    ):
        insertar_registro(registro, cliente)

    assert "lindus" not in cliente.datos


def test_insertar_observaciones_lindus_falla_con_varias_visitas():
    """No elige automáticamente si hay varias visitas candidatas."""
    cliente = ClienteFalso()
    cliente.datos["visitas"].append(
        {
            "id_visita": 51,
            "tipo_visita": "LINDUS",
            "fecha": "2026-05-01",
            "hora_fin": None,
            "id_lugar": 2,
            "id_observador": 7,
        }
    )
    registro = parsear_txt_plaud(str(EJEMPLOS / "observaciones_lindus_ok.txt"))

    with pytest.raises(
        ValueError,
        match="Hay varias visitas Lindus para la fecha 2026-05-01",
    ):
        insertar_registro(registro, cliente)

    assert "lindus" not in cliente.datos


def test_insertar_observaciones_lindus_filtra_por_lugar_y_observador_si_vienen():
    """La lógica queda preparada para desambiguar con campos opcionales."""
    cliente = ClienteFalso()
    cliente.datos["lugares"].append({"id_lugar": 3, "nombre_lugar": "Trona"})
    cliente.datos["visitas"].append(
        {
            "id_visita": 51,
            "tipo_visita": "LINDUS",
            "fecha": "2026-05-01",
            "hora_fin": None,
            "id_lugar": 3,
            "id_observador": 7,
        }
    )
    registro = parsear_txt_plaud(str(EJEMPLOS / "observaciones_lindus_ok.txt"))
    registro["visita"]["lugar_visita"] = "Trona"
    registro["visita"]["observador"] = "Gabi"

    resumen = insertar_registro(registro, cliente)

    assert resumen["id_visita"] == 51


def test_insertar_observaciones_lindus_no_deduplica_contenido_biologico():
    """Reprocesar el mismo contenido no se bloquea por deduplicación biológica."""
    cliente = ClienteFalso()
    registro = parsear_txt_plaud(str(EJEMPLOS / "observaciones_lindus_ok.txt"))

    insertar_registro(registro, cliente)
    insertar_registro(registro, cliente)

    assert len(cliente.datos["lindus"]) == 4


def test_insertar_caja_no_crea_visita_si_falta_especie():
    """Resuelve FKs antes de insertar para no dejar visitas huérfanas."""
    cliente = ClienteFalso()
    cliente.datos["especies"] = []
    registro = parsear_txt_plaud(str(EJEMPLOS / "visita_caja_nido_ok.txt"))
    visitas_antes = list(cliente.datos["visitas"])
    with pytest.raises(ValueError, match="especie no encontrada"):
        insertar_registro(registro, cliente)
    assert cliente.datos["visitas"] == visitas_antes
    assert "cajas_nido" not in cliente.datos


def test_insertar_nido_rapaz_lugar_no_encontrado_detalla_campo_y_valor():
    """El error de catálogo indica campo Plaud y valor recibido."""
    cliente = ClienteFalso()
    registro = parsear_txt_plaud(str(EJEMPLOS / "visita_nido_rapaz_ok.txt"))
    registro["visita"]["lugar_nido"] = "Areaxea 1"
    visitas_antes = list(cliente.datos["visitas"])

    with pytest.raises(PipelineError) as excinfo:
        insertar_registro(registro, cliente)

    error = excinfo.value.errores[0]
    assert error.fase == "catálogo/FK"
    assert error.campo == "lugar_nido"
    assert error.valor == "Areaxea 1"
    assert "lugar no encontrado" in error.motivo
    assert "lugares" in error.contexto
    assert cliente.datos["visitas"] == visitas_antes


def test_insertar_mamiferos_puente_no_descarta_observaciones_puente():
    """observaciones_puente llega a visitas.observaciones combinada con observaciones_visita."""
    cliente = ClienteFalso()
    cliente.datos["lugares"].append({"id_lugar": 3, "nombre_lugar": "Puente Prueba 1"})
    cliente.datos["lugares"].append({"id_lugar": 4, "nombre_lugar": "Puente de Aranzadi"})
    cliente.datos["especies"] += [
        {"id_especie": 20, "nombre_comun": "nutria", "nombre_cientifico": "Nutria"},
        {"id_especie": 22, "nombre_comun": "Nutria", "nombre_cientifico": "Lutra lutra"},
        {"id_especie": 21, "nombre_comun": "garduña", "nombre_cientifico": "Garduña"},
        {"id_especie": 23, "nombre_comun": "Garduña", "nombre_cientifico": "Martes foina"},
    ]
    registro = parsear_txt_plaud(str(EJEMPLOS / "visita_mamiferos_puente_ok.txt"))
    insertar_registro(registro, cliente)
    obs = cliente.datos["visitas"][-1].get("observaciones") or ""
    assert "Aranzadi" in obs or "barro reciente en ambas orillas" in obs
    assert "prueba real" in obs or "prospección tras lluvia" in obs


def test_insertar_mamiferos_puente_usa_fecha_normalizada_e_id_lugar():
    """El payload final no conserva la fecha ni el lugar imperfectos de Plaud."""
    cliente = ClienteFalso()
    cliente.datos["lugares"].append({"id_lugar": 9, "nombre_lugar": "Puente de Aranzadi"})
    cliente.datos["especies"] += [
        {"id_especie": 20, "nombre_comun": "Nutria", "nombre_cientifico": "Lutra lutra"},
        {"id_especie": 21, "nombre_comun": "Garduña", "nombre_cientifico": "Martes foina"},
    ]
    registro = {
        "tipo_registro": "VISITA_MAMIFEROS_PUENTE",
        "visita": {
            "tipo_visita": "MAMIFEROS_PUENTES",
            "fecha": "03/05/2026",
            "hora_inicio": "10:00",
            "hora_fin": "10:00",
            "lugar_puente": "puente de aranzadi",
            "observador": "Gabi",
        },
        "meteorologia": [],
        "datos": [
            {"especie": "nutria", "presencia": "PRESENTE", "tipo_evidencia": "EXCREMENTO"},
            {"especie": "garduña", "presencia": "POSIBLE", "tipo_evidencia": "HUELLA"},
        ],
    }

    normalizado = normalizar_registro(registro)
    assert normalizado["visita"]["fecha"] == "2026-05-03"
    assert validar_registro(normalizado) == []

    insertar_registro(normalizado, cliente)

    visita_insertada = cliente.datos["visitas"][-1]
    mamiferos_insertados = cliente.datos["mamiferos_puentes"]
    assert visita_insertada["fecha"] == "2026-05-03"
    assert visita_insertada["id_lugar"] == 9
    assert "lugar_puente" not in visita_insertada
    assert all(fila["id_lugar"] == 9 for fila in mamiferos_insertados)
    assert "puente de aranzadi" not in repr(visita_insertada)
