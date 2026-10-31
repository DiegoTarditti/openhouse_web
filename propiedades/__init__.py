import os

from .fuente import FuenteBase


def crear_fuente() -> FuenteBase:
    """Elige el origen de datos con la variable FUENTE_PROPIEDADES."""
    nombre = os.environ.get("FUENTE_PROPIEDADES", "simulada").strip().lower()
    if nombre == "simulada":
        from .simulados import FuenteSimulada

        return FuenteSimulada()
    raise RuntimeError(
        f"FUENTE_PROPIEDADES='{nombre}' no está disponible todavía "
        "(la integración con Tokko se agrega después)."
    )
