"""Valida registros Plaud ya parseados."""

from datetime import datetime

from src.diagnosticos import ErrorDetalle

FORMATOS_HORA = {"hora_inicio", "hora_fin", "hora_meteo", "hora"}
COMPORTAMIENTOS = {"MIGRADOR", "NORTE", "LOCAL"}
PRESENCIAS = {"PRESENTE", "AUSENTE", "POSIBLE"}
TIPOS_EVIDENCIA = {"HUELLA", "EXCREMENTO", "MADRIGUERA", "AVISTAMIENTO"}
ECOSISTEMAS = {"ZONA_SALVAJE", "ZONA_URBANA", "PARQUE_CON_RIO", "PARQUE_URBANO"}
ESTADOS_NIDO = {"POCAS_HIERBAS", "MUCHAS_HIERBAS", "CASI_TERMINADO", "TERMINADO"}
ORIENTACIONES = {"N", "NE", "E", "SE", "S", "SW", "W", "NW"}
VIENTO_DIRECCIONES = {"N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"}
VIENTO_INTENSIDADES = {"CALMA", "FLOJO", "BRISA", "MODERADO", "FUERTE"}
PRECIPITACIONES = {"NULA", "LEVE", "MODERADA", "FUERTE", "NIEVE", "NIEBLA"}
VISIBILIDADES = {"BUENA", "REGULAR", "MALA"}
SUGERENCIAS_VALORES = {
    ("viento_direccion", "NORTE"): "usar N para norte",
    ("viento_direccion", "SUR"): "usar S para sur",
    ("viento_direccion", "ESTE"): "usar E para este",
    ("viento_direccion", "OESTE"): "usar W para oeste",
    ("viento_direccion", "NORESTE"): "usar NE para noreste",
    ("viento_direccion", "NOROESTE"): "usar NW para noroeste",
    ("viento_direccion", "SURESTE"): "usar SE para sureste",
    ("viento_direccion", "SUROESTE"): "usar SW para suroeste",
}

MINIMOS_VISITA = {
    "INICIO_VISITA_LINDUS": ["tipo_visita", "fecha", "hora_inicio", "lugar_visita", "observador"],
    "OBSERVACIONES_LINDUS": ["tipo_visita", "fecha"],
    "FIN_VISITA_LINDUS": ["tipo_visita", "fecha", "hora_fin"],
    "VISITA_CAJA_NIDO": ["tipo_visita", "fecha", "hora_inicio", "hora_fin", "lugar_caja", "observador"],
    "VISITA_CEBO_AVISPON": ["tipo_visita", "fecha", "hora_inicio", "hora_fin", "lugar_cebo", "observador"],
    "VISITA_NIDO_RAPAZ": ["tipo_visita", "fecha", "hora_inicio", "hora_fin", "lugar_nido", "observador"],
    "VISITA_MAMIFEROS_PUENTE": ["tipo_visita", "fecha", "hora_inicio", "hora_fin", "lugar_puente", "observador"],
}


def validar_registro(registro: dict) -> list[str]:
    """Devuelve una lista de errores concretos del registro."""
    return [error.texto() for error in validar_registro_detallado(registro)]


def validar_registro_detallado(registro: dict) -> list[ErrorDetalle]:
    """Devuelve errores de validación con campo, valor y sugerencia."""
    errores = []
    tipo = registro.get("tipo_registro")
    visita = registro.get("visita", {})
    _validar_minimos(tipo, visita, errores)
    _validar_bloques_tipo(tipo, registro, errores)
    _validar_formatos(registro, errores)
    return errores


def _validar_minimos(tipo: str, visita: dict, errores: list[ErrorDetalle]) -> None:
    """Comprueba tipo de registro y campos mínimos de visita."""
    if not tipo:
        errores.append(_faltante("tipo_registro", "visita"))
        return
    for campo in MINIMOS_VISITA.get(tipo, []):
        if _falta(visita, campo):
            errores.append(_faltante(campo, "visita"))


def _validar_bloques_tipo(tipo: str, registro: dict, errores: list[ErrorDetalle]) -> None:
    """Aplica reglas de número y mínimos de bloques por plantilla."""
    datos = registro.get("datos", [])
    meteo = registro.get("meteorologia", [])
    _validar_meteorologia_generica(meteo, errores)
    if tipo == "OBSERVACIONES_LINDUS":
        _validar_lista_minima(datos, ["especie", "hora", "numero", "comportamiento"], "observacion", errores)
    if tipo == "FIN_VISITA_LINDUS":
        _validar_lista_minima(meteo, [], "meteorologia", errores, permite_vacia=True)
    if tipo == "VISITA_CAJA_NIDO":
        _validar_unico(datos, ["ecosistema", "especie_arbol", "estado_nido", "ocupada"], "caja_nido", errores)
    if tipo == "VISITA_CEBO_AVISPON":
        _validar_cebo(datos, errores)
    if tipo == "VISITA_NIDO_RAPAZ":
        _validar_unico(datos, ["texto_revision"], "nido_rapaz", errores)
    if tipo == "VISITA_MAMIFEROS_PUENTE":
        _validar_lista_minima(datos, ["especie", "presencia"], "mamifero", errores)


def _validar_lista_minima(
    lista: list,
    campos: list[str],
    nombre: str,
    errores: list[ErrorDetalle],
    permite_vacia=False,
) -> None:
    """Valida una lista de bloques con campos obligatorios."""
    if not lista and not permite_vacia:
        errores.append(
            ErrorDetalle(
                fase="validación",
                campo=nombre,
                contexto=nombre,
                motivo=f"al menos un bloque {nombre} requerido",
                sugerencia="revisa que Plaud haya incluido el marcador de bloque correcto",
            )
        )
    for indice, bloque in enumerate(lista, start=1):
        for campo in campos:
            if _falta(bloque, campo):
                errores.append(_faltante(campo, f"{nombre} {indice}"))


def _validar_unico(lista: list, campos: list[str], nombre: str, errores: list[ErrorDetalle]) -> None:
    """Valida que exista exactamente un bloque con mínimos."""
    if len(lista) != 1:
        errores.append(
            ErrorDetalle(
                fase="validación",
                campo=nombre,
                contexto=nombre,
                motivo=f"debe haber exactamente un bloque {nombre}",
                valor=len(lista),
                sugerencia="usa una grabación por visita y conserva el marcador de bloque esperado",
            )
        )
        return
    for campo in campos:
        if _falta(lista[0], campo):
            errores.append(_faltante(campo, f"{nombre} 1"))


def _validar_cebo(datos: list, errores: list[ErrorDetalle]) -> None:
    """Valida el bloque único de cebo de avispón."""
    capturas = {"vv", "crabro", "avispa_europea", "polilla", "mariposa", "otros"}
    if len(datos) != 1:
        errores.append(
            ErrorDetalle(
                fase="validación",
                campo="cebo_avispon",
                contexto="cebo_avispon",
                motivo="debe haber exactamente un bloque cebo_avispon",
                valor=len(datos),
                sugerencia="usa una grabación por cebo y conserva el marcador ---CEBO_AVISPON---",
            )
        )
        return
    if not capturas.intersection(datos[0]) and _falta(datos[0], "observaciones_cebo"):
        errores.append(_faltante("capturas u observaciones_cebo", "cebo_avispon 1"))


def _validar_meteorologia_generica(meteo: list[dict], errores: list[ErrorDetalle]) -> None:
    """Valida mínimos comunes de cada bloque meteorológico incluido."""
    for indice, bloque in enumerate(meteo, start=1):
        if _falta(bloque, "hora_meteo"):
            errores.append(_faltante("hora_meteo", f"meteorologia {indice}"))


def _validar_formatos(registro: dict, errores: list[ErrorDetalle]) -> None:
    """Valida fechas, horas y valores cerrados en todo el registro."""
    for contexto, bloque in _iter_bloques(registro):
        _validar_fecha_horas(contexto, bloque, errores)
        _validar_nubosidad(contexto, bloque, errores)
        _validar_cerrado(contexto, bloque, errores)


def _iter_bloques(registro: dict):
    """Itera visita, meteorología y datos con nombres legibles."""
    yield "visita", registro.get("visita", {})
    for indice, bloque in enumerate(registro.get("meteorologia", []), start=1):
        yield f"meteorologia {indice}", bloque
    for indice, bloque in enumerate(registro.get("datos", []), start=1):
        yield f"observacion {indice}", bloque


def _validar_fecha_horas(contexto: str, bloque: dict, errores: list[ErrorDetalle]) -> None:
    """Valida formato ISO de fecha y HH:MM de horas."""
    if "fecha" in bloque and not _fecha_valida(bloque["fecha"]):
        errores.append(
            ErrorDetalle(
                fase="validación",
                campo="fecha",
                contexto=contexto,
                valor=bloque["fecha"],
                motivo="fecha no válida",
                sugerencia="usa formato YYYY-MM-DD o DD/MM/YYYY",
            )
        )
    for campo in FORMATOS_HORA:
        if campo in bloque and not _hora_valida(bloque[campo]):
            errores.append(
                ErrorDetalle(
                    fase="validación",
                    campo=campo,
                    contexto=contexto,
                    valor=bloque[campo],
                    motivo="hora inválida",
                    sugerencia="usa formato HH:MM",
                )
            )


def _validar_nubosidad(contexto: str, bloque: dict, errores: list[ErrorDetalle]) -> None:
    """Comprueba que nubosidad esté entre 0 y 8."""
    if "nubosidad" in bloque and not 0 <= bloque["nubosidad"] <= 8:
        errores.append(
            ErrorDetalle(
                fase="validación",
                campo="nubosidad",
                contexto=contexto,
                valor=bloque["nubosidad"],
                motivo="valor fuera del rango permitido",
                valores_aceptados=tuple(range(0, 9)),
                sugerencia="usa un entero entre 0 y 8",
            )
        )


def _validar_cerrado(contexto: str, bloque: dict, errores: list[ErrorDetalle]) -> None:
    """Comprueba valores cerrados conocidos."""
    reglas = {
        "comportamiento": COMPORTAMIENTOS,
        "presencia": PRESENCIAS,
        "tipo_evidencia": TIPOS_EVIDENCIA,
        "ecosistema": ECOSISTEMAS,
        "estado_nido": ESTADOS_NIDO,
        "orientacion_caja": ORIENTACIONES,
        "viento_direccion": VIENTO_DIRECCIONES,
        "viento_intensidad": VIENTO_INTENSIDADES,
        "precipitacion": PRECIPITACIONES,
        "visibilidad": VISIBILIDADES,
    }
    for campo, validos in reglas.items():
        if campo in bloque and bloque[campo] not in validos:
            errores.append(
                ErrorDetalle(
                    fase="validación",
                    campo=campo,
                    contexto=contexto,
                    valor=bloque[campo],
                    motivo="valor cerrado no válido",
                    valores_aceptados=tuple(sorted(validos)),
                    sugerencia=_sugerencia_valor(campo, bloque[campo]),
                )
            )


def _faltante(campo: str, contexto: str) -> ErrorDetalle:
    """Crea un diagnóstico de campo obligatorio ausente."""
    return ErrorDetalle(
        fase="validación",
        campo=campo,
        contexto=contexto,
        motivo="campo obligatorio ausente",
        sugerencia="corrige la plantilla o dicta este campo en Plaud",
    )


def _sugerencia_valor(campo: str, valor: object) -> str:
    """Sugiere equivalencias claras sin aceptarlas como valor final."""
    if not isinstance(valor, str):
        return "usa uno de los valores aceptados"
    return SUGERENCIAS_VALORES.get((campo, valor.strip().upper()), "usa uno de los valores aceptados")


def _fecha_valida(valor: str) -> bool:
    """Indica si una fecha usa YYYY-MM-DD."""
    try:
        datetime.strptime(valor, "%Y-%m-%d")
    except ValueError:
        return False
    return True


def _hora_valida(valor: str) -> bool:
    """Indica si una hora usa HH:MM."""
    try:
        datetime.strptime(valor, "%H:%M")
    except ValueError:
        return False
    return True


def _falta(diccionario: dict, campo: str) -> bool:
    """Indica si falta un campo o viene vacío."""
    return campo not in diccionario or diccionario[campo] in {"", None}
