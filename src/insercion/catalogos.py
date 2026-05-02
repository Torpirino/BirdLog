"""Resuelve nombres de catálogo a IDs de Supabase."""


def resolver_lugar(nombre: str, cliente) -> int:
    """Devuelve el id_lugar asociado a un nombre de lugar."""
    return _resolver_unico(
        cliente,
        tabla="lugares",
        columna_id="id_lugar",
        campo="nombre_lugar",
        valor=nombre,
        mensaje=_mensaje_lugar(nombre),
    )


def resolver_observador(nombre: str, cliente) -> int:
    """Devuelve el id_observador asociado a un nombre."""
    return _resolver_unico(
        cliente,
        tabla="observadores",
        columna_id="id_observador",
        campo="nombre_observador",
        valor=nombre,
        mensaje=_mensaje_observador(nombre),
    )


def resolver_especie(nombre: str, cliente) -> int:
    """Devuelve el id_especie buscando por nombre común o científico.

    Prueba primero coincidencia exacta y luego con primera letra en mayúscula,
    para tolerar que Plaud transcriba los nombres en minúsculas.
    """
    for variante in _variantes_especie(nombre):
        por_comun = _buscar(cliente, "especies", "id_especie", "nombre_comun", variante)
        if por_comun is not None:
            return por_comun
        por_cientifico = _buscar(cliente, "especies", "id_especie", "nombre_cientifico", variante)
        if por_cientifico is not None:
            return por_cientifico
    raise ValueError(_mensaje_especie(nombre))


def _variantes_especie(nombre: str) -> list[str]:
    """Devuelve variantes de capitalización: exacta y con primera letra mayúscula."""
    return list(dict.fromkeys([nombre, nombre.capitalize()]))


def _resolver_unico(cliente, tabla: str, columna_id: str, campo: str, valor: str, mensaje: str) -> int:
    """Resuelve un registro único o lanza ValueError."""
    encontrado = _buscar(cliente, tabla, columna_id, campo, valor)
    if encontrado is None:
        raise ValueError(mensaje)
    return encontrado


def _buscar(cliente, tabla: str, columna_id: str, campo: str, valor: str) -> int | None:
    """Ejecuta una búsqueda simple de catálogo."""
    respuesta = cliente.table(tabla).select(columna_id).eq(campo, valor).limit(1).execute()
    filas = getattr(respuesta, "data", None) or []
    if not filas:
        return None
    return filas[0][columna_id]


def _mensaje_lugar(nombre: str) -> str:
    """Construye el mensaje para lugares no encontrados."""
    return (
        f"Lugar no encontrado: '{nombre}'.\n"
        "Da de alta en Supabase (tabla lugares) y añade el nombre al vocabulario del Plaud."
    )


def _mensaje_observador(nombre: str) -> str:
    """Construye el mensaje para observadores no encontrados."""
    return (
        f"Observador no encontrado: '{nombre}'.\n"
        "Da de alta en Supabase (tabla observadores) y añade el nombre al vocabulario del Plaud."
    )


def _mensaje_especie(nombre: str) -> str:
    """Construye el mensaje para especies no encontradas."""
    return (
        f"Especie no encontrada: '{nombre}'.\n"
        "Da de alta en Supabase (tabla especies) y añade el nombre al vocabulario del Plaud."
    )
