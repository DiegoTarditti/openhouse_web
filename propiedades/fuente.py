"""Fuente de propiedades: búsqueda y filtros sobre cualquier origen de datos.

`FuenteBase` define lo que necesita la web. `FuenteSimulada` sirve datos de
ejemplo; la fuente de Tokko se agrega después implementando `todas()`.
"""
from dataclasses import dataclass, field
from typing import Optional

from .modelo import Propiedad, TIPOS_RURALES

POR_PAGINA = 12

ORDENES = {
    "recientes": "Más recientes",
    "precio_asc": "Menor precio",
    "precio_desc": "Mayor precio",
    "ha_desc": "Mayor superficie (ha)",
}


@dataclass
class Filtros:
    operacion: str = ""
    tipo: str = ""
    rural: bool = False          # atajo: campos y chacras
    texto: str = ""              # zona, localidad o palabra del título
    precio_min: Optional[float] = None
    precio_max: Optional[float] = None
    ha_min: Optional[float] = None
    ha_max: Optional[float] = None
    dormitorios_min: Optional[int] = None
    orden: str = "recientes"
    pagina: int = 1


@dataclass
class Resultado:
    propiedades: list
    total: int
    pagina: int
    paginas: int
    filtros: Filtros = field(default_factory=Filtros)


class FuenteBase:
    """Las fuentes solo tienen que devolver todas las propiedades publicadas."""

    def todas(self) -> list:
        raise NotImplementedError

    def obtener(self, id_: str) -> Optional[Propiedad]:
        return next((p for p in self.todas() if p.id == id_), None)

    def destacadas(self, limite: int = 8) -> list:
        return [p for p in self.todas() if p.destacada][:limite]

    def similares(self, prop: Propiedad, limite: int = 4) -> list:
        candidatas = [
            p for p in self.todas()
            if p.id != prop.id and p.operacion == prop.operacion
            and p.es_rural == prop.es_rural
        ]
        candidatas.sort(key=lambda p: (p.localidad != prop.localidad, p.tipo != prop.tipo))
        return candidatas[:limite]

    def contar_rurales(self) -> int:
        return sum(1 for p in self.todas() if p.es_rural)

    def coincidencias(self, f: Filtros) -> list:
        """Todas las propiedades que cumplen, ordenadas (sin paginar)."""
        return _ordenar([p for p in self.todas() if _cumple(p, f)], f.orden)

    def buscar(self, f: Filtros) -> Resultado:
        items = self.coincidencias(f)
        total = len(items)
        paginas = max(1, -(-total // POR_PAGINA))
        pagina = min(max(1, f.pagina), paginas)
        desde = (pagina - 1) * POR_PAGINA
        return Resultado(items[desde:desde + POR_PAGINA], total, pagina, paginas, f)


def _normalizar(txt: str) -> str:
    import unicodedata

    t = unicodedata.normalize("NFKD", txt or "").encode("ascii", "ignore").decode()
    return t.lower().strip()


def _cumple(p: Propiedad, f: Filtros) -> bool:
    if f.operacion and p.operacion != f.operacion:
        return False
    if f.rural and p.tipo not in TIPOS_RURALES:
        return False
    if f.tipo and p.tipo != f.tipo:
        return False
    if f.texto:
        pajar = _normalizar(" ".join((p.titulo, p.zona, p.localidad, p.provincia)))
        if not all(palabra in pajar for palabra in _normalizar(f.texto).split()):
            return False
    if f.precio_min is not None and (p.precio is None or p.precio < f.precio_min):
        return False
    if f.precio_max is not None and (p.precio is None or p.precio > f.precio_max):
        return False
    if f.ha_min is not None and (p.superficie_ha is None or p.superficie_ha < f.ha_min):
        return False
    if f.ha_max is not None and (p.superficie_ha is None or p.superficie_ha > f.ha_max):
        return False
    if f.dormitorios_min is not None and (p.dormitorios or 0) < f.dormitorios_min:
        return False
    return True


def _ordenar(items: list, orden: str) -> list:
    # Sin precio al final, en cualquier orden por precio.
    if orden == "precio_asc":
        return sorted(items, key=lambda p: (p.precio is None, p.precio or 0))
    if orden == "precio_desc":
        return sorted(items, key=lambda p: (p.precio is None, -(p.precio or 0)))
    if orden == "ha_desc":
        return sorted(items, key=lambda p: (p.superficie_ha is None, -(p.superficie_ha or 0)))
    return list(items)  # "recientes": el orden en que la fuente las entrega
