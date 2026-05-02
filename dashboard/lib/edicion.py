"""Helpers de edición, validación y borrado seguro."""

from dataclasses import dataclass
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
    return get_cliente().table(tabla).insert(payload).execute().data


def actualizar_registro(tabla: str, id_registro: int, datos: dict[str, Any]) -> dict[str, Any]:
    """Actualiza un registro por su clave primaria."""
    id_columna = _id_columna(tabla)
    payload = limpiar_payload(tabla, datos)
    _asegurar_valido(tabla, payload)
    return get_cliente().table(tabla).update(payload).eq(id_columna, id_registro).execute().data


def borrar_registro_seguro(tabla: str, id_registro: int, confirmacion: str) -> dict[str, Any]:
    """Borra un registro solo si la confirmación escrita es exacta."""
    if confirmacion != "BORRAR":
        raise ValueError("Para borrar debes escribir exactamente BORRAR.")
    id_columna = _id_columna(tabla)
    return get_cliente().table(tabla).delete().eq(id_columna, id_registro).execute().data


def resumen_registro(tabla: str, registro: dict[str, Any], max_campos: int = 8) -> str:
    """Prepara un resumen breve para confirmaciones."""
    id_columna = _id_columna(tabla)
    partes = [f"{tabla} ({id_columna}={registro.get(id_columna, '')})"]
    for clave, valor in list(registro.items())[:max_campos]:
        partes.append(f"{clave}: {valor}")
    return " | ".join(partes)


def opciones_valor_cerrado(tabla: str, campo: str) -> list[str]:
    """Devuelve valores cerrados para un campo editable."""
    return VALORES_CERRADOS.get((tabla, campo), [])


def _asegurar_valido(tabla: str, payload: dict[str, Any]) -> None:
    """Lanza error si el payload no cumple mínimos."""
    resultado = validar_registro(tabla, payload)
    if not resultado.ok:
        raise ValueError("; ".join(resultado.errores))


def _errores_obligatorios(tabla: str, datos: dict[str, Any]) -> list[str]:
    """Valida campos obligatorios."""
    return [f"Falta el campo obligatorio: {campo}" for campo in OBLIGATORIOS.get(tabla, []) if not datos.get(campo)]


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
