"""Modelo de propiedad que usa toda la web.

Es independiente de la fuente: hoy sale de datos simulados y la semana que
viene de la API de Tokko. Las páginas solo conocen esta clase.
"""
from dataclasses import dataclass
from typing import Optional

OPERACIONES = {"venta": "Venta", "alquiler": "Alquiler"}

TIPOS = {
    "departamento": "Departamento",
    "casa": "Casa",
    "local": "Local comercial",
    "lote": "Lote",
    "campo": "Campo",
    "chacra": "Chacra",
}
TIPOS_RURALES = ("campo", "chacra")


@dataclass(frozen=True)
class Propiedad:
    id: str
    titulo: str
    operacion: str
    tipo: str
    localidad: str
    zona: str = ""
    provincia: str = "Santa Fe"
    descripcion: str = ""
    precio: Optional[float] = None
    moneda: str = "USD"
    lat: Optional[float] = None
    lng: Optional[float] = None
    superficie_ha: Optional[float] = None
    superficie_total_m2: Optional[float] = None
    superficie_cubierta_m2: Optional[float] = None
    ambientes: Optional[int] = None
    dormitorios: Optional[int] = None
    banios: Optional[int] = None
    cocheras: Optional[int] = None
    fotos: tuple = ()
    # Pares (etiqueta, valor) para la tabla de datos: aptitud, agua, mejoras…
    ficha: tuple = ()
    destacada: bool = False
    # Id que usa Tokko para asociar una consulta a la publicación.
    publication_id: str = ""

    @property
    def es_rural(self) -> bool:
        return self.tipo in TIPOS_RURALES

    @property
    def slug(self) -> str:
        return f"{_slugify(self.titulo)}-{self.id}"

    @property
    def tipo_etiqueta(self) -> str:
        return TIPOS.get(self.tipo, self.tipo.title())

    @property
    def operacion_etiqueta(self) -> str:
        return OPERACIONES.get(self.operacion, self.operacion.title())

    @property
    def ubicacion(self) -> str:
        partes = [p for p in (self.zona, self.localidad) if p]
        return ", ".join(partes)

    @property
    def precio_por_ha(self) -> Optional[float]:
        if self.es_rural and self.operacion == "venta" and self.precio and self.superficie_ha:
            return self.precio / self.superficie_ha
        return None

    @property
    def tiene_mapa(self) -> bool:
        return self.lat is not None and self.lng is not None


def _slugify(texto: str) -> str:
    import re
    import unicodedata

    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    t = re.sub(r"[^a-zA-Z0-9]+", "-", t).strip("-").lower()
    return t or "propiedad"


def id_desde_slug(slug: str) -> str:
    """El id es lo que sigue al último guion: 'casa-3-dorm-p012' -> 'p012'."""
    return slug.rsplit("-", 1)[-1]
