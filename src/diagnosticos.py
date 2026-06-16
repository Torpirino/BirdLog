"""Diagnósticos legibles para errores de validación y carga."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ErrorDetalle:
    """Describe un problema concreto detectado durante la validación o carga."""

    fase: str
    campo: str
    motivo: str
    valor: object | None = None
    sugerencia: str = ""
    accion: str = "no insertado; movido a errores; sin backup"
    contexto: str = ""
    valores_aceptados: tuple[object, ...] = ()
    advertencia: bool = False

    def a_dict(self) -> dict:
        """Convierte el diagnóstico en dict serializable para la app."""
        return {
            "fase": self.fase,
            "campo": self.campo,
            "valor": self.valor,
            "motivo": self.motivo,
            "sugerencia": self.sugerencia,
            "accion": self.accion,
            "contexto": self.contexto,
            "valores_aceptados": list(self.valores_aceptados),
            "advertencia": self.advertencia,
        }

    @classmethod
    def desde_dict(cls, datos: dict) -> "ErrorDetalle":
        """Reconstruye un diagnóstico desde su representación en dict."""
        return cls(
            fase=datos.get("fase", ""),
            campo=datos.get("campo", ""),
            valor=datos.get("valor"),
            motivo=datos.get("motivo", ""),
            sugerencia=datos.get("sugerencia", ""),
            accion=datos.get("accion", ""),
            contexto=datos.get("contexto", ""),
            valores_aceptados=tuple(datos.get("valores_aceptados", ())),
            advertencia=bool(datos.get("advertencia", False)),
        )

    def texto(self) -> str:
        """Devuelve una línea clara para logs y mensajes."""
        partes = []
        if self.campo:
            partes.append(self.campo.upper())
        if self.contexto:
            partes.append(f"en {self.contexto}")
        if self.valor not in (None, ""):
            partes.append(f"recibió {self.valor!r}")
        if self.motivo:
            partes.append(self.motivo)
        texto = " - ".join(partes) if partes else self.motivo
        if self.valores_aceptados:
            aceptados = ", ".join(str(valor) for valor in self.valores_aceptados)
            texto += f". Valores aceptados: {aceptados}"
        if self.sugerencia:
            texto += f". Sugerencia: {self.sugerencia}"
        if self.accion:
            texto += f". Acción realizada: {self.accion}"
        return texto


class ErrorCarga(ValueError):
    """Error de validación o carga con diagnósticos estructurados."""

    def __init__(self, archivo: str, fase: str, errores: list[ErrorDetalle]):
        self.archivo = archivo
        self.fase = fase
        self.errores = errores
        super().__init__(mensaje_error(archivo, errores))


def mensaje_error(archivo: str, errores: list[ErrorDetalle]) -> str:
    """Construye el mensaje principal de error."""
    if not errores:
        return f"El archivo {archivo} no se pudo procesar."
    detalle = "\n".join(f"- {error.texto()}" for error in errores)
    return f"El archivo {archivo} no es válido:\n{detalle}"
