"""Helpers de edición, validación y borrado seguro."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from dashboard.lib.conexion import get_cliente
from dashboard.lib.consultas import ID_TABLA


VALORES_CERRADOS = {
    ("especies", "grupo"): ["RAPAZ", "PASERIFORME", "ACUATICA", "INVERTEBRADO", "MAMIFERO", "OTRO"],
    ("lugares", "tipo_lugar"): ["CONTEO_MIGRATORIO", "CAJA_NIDO", "CEBO_AVISPON", "NIDO_RAPAZ", "PUENTE"],
    ("visitas", "tipo_visita"): [
        "LINDUS",
        "CAJA_NIDO",
        "CEBO_AVISPON",
        "NIDO_RAPAZ",
        "MAMIFEROS_PUENTES",
        "IMPACTO_AMBIENTAL",
    ],
    ("lindus", "comportamiento"): ["MIGRADOR", "NORTE", "LOCAL"],
    ("cajas_nido", "ecosistema"): ["ZONA_SALVAJE", "ZONA_URBANA", "PARQUE_CON_RIO", "PARQUE_URBANO"],
    ("cajas_nido", "estado_nido"): ["POCAS_HIERBAS", "MUCHAS_HIERBAS", "CASI_TERMINADO", "TERMINADO"],
    ("cajas_nido", "orientacion_caja"): ["N", "NE", "E", "SE", "S", "SW", "W", "NW"],
    ("mamiferos_puentes", "presencia"): ["PRESENTE", "AUSENTE", "POSIBLE"],
    ("mamiferos_puentes", "tipo_evidencia"): ["HUELLA", "EXCREMENTO", "MADRIGUERA", "AVISTAMIENTO"],
}

OBLIGATORIOS = {
    "especies": ["nombre_cientifico"],
    "observadores": ["nombre_observador"],
    "lugares": ["nombre_lugar", "tipo_lugar", "utm_x", "utm_y"],
    "visitas": ["id_lugar", "id_observador", "tipo_visita", "fecha", "hora_inicio"],
    "meteorologia": ["id_visita", "hora"],
    "lindus": ["id_visita", "id_especie", "hora", "numero", "comportamiento"],
    "cajas_nido": ["id_visita", "id_lugar", "ecosistema", "especie_arbol", "estado_nido", "ocupada"],
    "nidos_rapaces": ["id_visita", "id_lugar", "texto_revision"],
    "cebos_avispones": ["id_visita", "id_lugar", "vv"],
    "mamiferos_puentes": ["id_visita", "id_lugar", "id_especie", "presencia"],
    "fotos": ["url_drive"],
}

ORDEN_TABLAS = [
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
    "fotos",
]

CAMPOS_TABLA = {
    "especies": ["nombre_cientifico", "nombre_comun", "grupo"],
    "observadores": ["nombre_observador"],
    "lugares": ["nombre_lugar", "tipo_lugar", "municipio", "utm_x", "utm_y"],
    "visitas": ["id_lugar", "id_observador", "tipo_visita", "fecha", "hora_inicio", "hora_fin", "observaciones"],
    "meteorologia": [
        "id_visita",
        "hora",
        "temperatura",
        "nubosidad",
        "viento_direccion",
        "viento_intensidad",
        "precipitacion",
        "visibilidad",
    ],
    "lindus": ["id_visita", "id_especie", "hora", "numero", "comportamiento", "edad", "sexo", "plumaje", "observaciones"],
    "cajas_nido": [
        "id_visita",
        "id_lugar",
        "id_especie",
        "ecosistema",
        "especie_arbol",
        "estado_nido",
        "ocupada",
        "numero_huevos",
        "numero_pollos",
        "observaciones",
        "orientacion_caja",
        "huevos_caliente_frio",
        "peso_pollos",
        "longitud_tarso",
        "numero_anilla",
        "distancia_rio",
        "distancia_peatonal",
        "distancia_carretera",
        "cobertura_vegetal",
        "cobertura_arboles",
        "cobertura_matorral",
        "cobertura_pastizal",
    ],
    "nidos_rapaces": ["id_visita", "id_lugar", "id_especie", "texto_revision", "comunicacion_personal"],
    "cebos_avispones": ["id_visita", "id_lugar", "vv", "crabro", "avispa_europea", "polilla", "mariposa", "otros", "observaciones"],
    "mamiferos_puentes": ["id_visita", "id_lugar", "id_especie", "presencia", "tipo_evidencia", "observaciones"],
    "fotos": ["id_visita", "tabla_origen", "id_origen", "url_drive", "descripcion", "fecha_subida"],
}

TIPOS_CAMPO = {
    "fecha": "date",
    "fecha_subida": "date",
    "hora": "time",
    "hora_inicio": "time",
    "hora_fin": "time",
    "ocupada": "bool",
    "utm_x": "float",
    "utm_y": "float",
    "temperatura": "float",
    "peso_pollos": "float",
    "longitud_tarso": "float",
    "distancia_rio": "float",
    "distancia_peatonal": "float",
    "distancia_carretera": "float",
    "cobertura_vegetal": "float",
    "cobertura_arboles": "float",
    "cobertura_matorral": "float",
    "cobertura_pastizal": "float",
    "nubosidad": "int",
    "numero": "int",
    "numero_huevos": "int",
    "numero_pollos": "int",
    "vv": "int",
    "crabro": "int",
    "avispa_europea": "int",
    "polilla": "int",
    "mariposa": "int",
    "otros": "int",
    "id_lugar": "fk",
    "id_especie": "fk",
    "id_observador": "fk",
    "id_visita": "fk",
    "id_origen": "int",
}

DEPENDENCIAS_BORRADO = {
    "especies": [("lindus", "id_especie"), ("cajas_nido", "id_especie"), ("nidos_rapaces", "id_especie"), ("mamiferos_puentes", "id_especie")],
    "observadores": [("visitas", "id_observador")],
    "lugares": [("visitas", "id_lugar"), ("cajas_nido", "id_lugar"), ("nidos_rapaces", "id_lugar"), ("cebos_avispones", "id_lugar"), ("mamiferos_puentes", "id_lugar")],
    "visitas": [("meteorologia", "id_visita"), ("lindus", "id_visita"), ("cajas_nido", "id_visita"), ("nidos_rapaces", "id_visita"), ("cebos_avispones", "id_visita"), ("mamiferos_puentes", "id_visita"), ("fotos", "id_visita")],
}


@dataclass(frozen=True)
class ResultadoValidacion:
    """Resultado de validar un registro editable."""

    ok: bool
    errores: list[str]


def validar_registro(tabla: str, datos: dict[str, Any]) -> ResultadoValidacion:
    """Valida obligatorios y valores cerrados."""
    errores = _errores_obligatorios(tabla, datos)
    errores.extend(_errores_valores_cerrados(tabla, datos))
    return ResultadoValidacion(not errores, errores)


def limpiar_payload(tabla: str, datos: dict[str, Any]) -> dict[str, Any]:
    """Elimina id vacío y valores vacíos antes de enviar a Supabase."""
    id_columna = ID_TABLA.get(tabla)
    limpio = {clave: valor for clave, valor in datos.items() if valor not in ("", None)}
    if id_columna in limpio and not limpio[id_columna]:
        limpio.pop(id_columna)
    return limpio


def crear_registro(tabla: str, datos: dict[str, Any]) -> dict[str, Any]:
    """Inserta un registro validado en Supabase."""
    payload = limpiar_payload(tabla, datos)
    _asegurar_valido(tabla, payload)
    preparar_backup_y_traza("crear", tabla, None, payload)
    return get_cliente().table(tabla).insert(payload).execute().data


def actualizar_registro(tabla: str, id_registro: int, datos: dict[str, Any]) -> dict[str, Any]:
    """Actualiza un registro por su clave primaria."""
    id_columna = _id_columna(tabla)
    payload = limpiar_payload(tabla, datos)
    _asegurar_valido(tabla, payload)
    preparar_backup_y_traza("editar", tabla, id_registro, payload)
    return get_cliente().table(tabla).update(payload).eq(id_columna, id_registro).execute().data


def borrar_registro_seguro(tabla: str, id_registro: int, confirmacion: str) -> dict[str, Any]:
    """Borra un registro solo si la confirmación escrita es exacta."""
    if confirmacion != "BORRAR":
        raise ValueError("Para borrar debes escribir exactamente BORRAR.")
    id_columna = _id_columna(tabla)
    preparar_backup_y_traza("borrar", tabla, id_registro, {})
    return get_cliente().table(tabla).delete().eq(id_columna, id_registro).execute().data


def resumen_registro(tabla: str, registro: dict[str, Any], max_campos: int = 10) -> str:
    """Prepara un resumen breve para confirmaciones."""
    id_columna = _id_columna(tabla)
    partes = [f"{tabla} ({id_columna}={registro.get(id_columna, '')})"]
    for clave in _campos_resumen(tabla, registro)[:max_campos]:
        partes.append(f"{clave}: {registro.get(clave)}")
    return " | ".join(partes)


def opciones_valor_cerrado(tabla: str, campo: str) -> list[str]:
    """Devuelve valores cerrados para un campo editable."""
    return VALORES_CERRADOS.get((tabla, campo), [])


def campos_editables(tabla: str) -> list[str]:
    """Devuelve campos editables de una tabla."""
    return CAMPOS_TABLA.get(tabla, [])


def tipo_campo(campo: str) -> str:
    """Devuelve tipo de widget sugerido."""
    return TIPOS_CAMPO.get(campo, "text")


def campos_obligatorios(tabla: str) -> list[str]:
    """Devuelve campos obligatorios."""
    return OBLIGATORIOS.get(tabla, [])


def dependencias_registro(tabla: str, id_registro: int, tablas: dict[str, Any]) -> list[str]:
    """Comprueba dependencias cargadas que podrían bloquear un borrado."""
    dependencias = []
    for tabla_dep, campo in DEPENDENCIAS_BORRADO.get(tabla, []):
        df = tablas.get(tabla_dep)
        if df is not None and not df.empty and campo in df.columns:
            total = int((df[campo] == id_registro).sum())
            if total:
                dependencias.append(f"{tabla_dep}.{campo}: {total} registro(s)")
    return dependencias


def preparar_backup_y_traza(accion: str, tabla: str, id_registro: int | None, payload: dict[str, Any]) -> Path | None:
    """Hace backup local reutilizando el módulo existente y escribe una traza mínima."""
    carpeta_backup = None
    try:
        from src.backup.exportar import hacer_backup

        carpeta_backup = hacer_backup(get_cliente())
    finally:
        _registrar_traza(accion, tabla, id_registro, payload, carpeta_backup)
    return carpeta_backup


def _asegurar_valido(tabla: str, payload: dict[str, Any]) -> None:
    """Lanza error si el payload no cumple mínimos."""
    resultado = validar_registro(tabla, payload)
    if not resultado.ok:
        raise ValueError("; ".join(resultado.errores))


def _errores_obligatorios(tabla: str, datos: dict[str, Any]) -> list[str]:
    """Valida campos obligatorios."""
    errores = []
    for campo in OBLIGATORIOS.get(tabla, []):
        valor = datos.get(campo)
        if valor is None or valor == "":
            errores.append(f"Falta el campo obligatorio: {campo}")
    return errores


def _errores_valores_cerrados(tabla: str, datos: dict[str, Any]) -> list[str]:
    """Valida campos con vocabulario cerrado."""
    errores = []
    for (tabla_valor, campo), opciones in VALORES_CERRADOS.items():
        valor = datos.get(campo)
        if tabla_valor == tabla and valor not in (None, "") and valor not in opciones:
            errores.append(f"{campo} debe ser uno de: {', '.join(opciones)}")
    return errores


def _id_columna(tabla: str) -> str:
    """Devuelve clave primaria de una tabla editable."""
    if tabla not in ID_TABLA:
        raise ValueError(f"Tabla no editable: {tabla}")
    return ID_TABLA[tabla]


def _campos_resumen(tabla: str, registro: dict[str, Any]) -> list[str]:
    """Prioriza campos comprensibles para resumen."""
    preferidos = [
        ID_TABLA.get(tabla, ""),
        "fecha",
        "nombre_lugar",
        "nombre_cientifico",
        "nombre_comun",
        "nombre_observador",
        "tipo_visita",
        "tipo_lugar",
        "id_visita",
        "id_lugar",
        "id_especie",
        "id_observador",
    ]
    vistos = []
    for campo in preferidos + list(registro):
        if campo and campo in registro and campo not in vistos:
            vistos.append(campo)
    return vistos


def _registrar_traza(
    accion: str, tabla: str, id_registro: int | None, payload: dict[str, Any], carpeta_backup: Path | None
) -> None:
    """Registra una traza local mínima de operaciones de edición."""
    ruta = Path("backups") / "edicion_traza.log"
    ruta.parent.mkdir(parents=True, exist_ok=True)
    payload_seguro = {clave: ("<valor largo>" if len(str(valor)) > 120 else valor) for clave, valor in payload.items()}
    linea = {
        "fecha_hora": datetime.now().isoformat(timespec="seconds"),
        "accion": accion,
        "tabla": tabla,
        "id_registro": id_registro,
        "payload": payload_seguro,
        "backup": str(carpeta_backup) if carpeta_backup else "no disponible",
    }
    with ruta.open("a", encoding="utf-8") as archivo:
        archivo.write(f"{linea}\n")
