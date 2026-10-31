"""Propiedades de ejemplo para desarrollar la web sin la API de Tokko.

Son datos inventados. Se reemplazan cuando se conecte la fuente real.
"""
from .fuente import FuenteBase
from .modelo import Propiedad


def _fotos(tipo: str, semilla: str, cantidad: int = 5) -> tuple:
    return tuple(f"/placeholder/{tipo}/{semilla}-{i}.svg" for i in range(1, cantidad + 1))


_DATOS = (
    Propiedad(
        id="p001", titulo="Campo agrícola mixto", operacion="venta", tipo="campo",
        localidad="Cañada de Gómez", zona="Zona rural", precio=576000,
        superficie_ha=180, lat=-32.8167, lng=-61.3989, destacada=True,
        descripcion=(
            "Campo de 180 hectáreas de aptitud agrícola mixta, con excelente aptitud "
            "para soja, maíz y trigo. Lotes parejos, sin anegamientos, con acceso "
            "por camino consolidado a 6 km de la ruta nacional 9. Casco con casa de "
            "capataz, galpón de 300 m² y silos."
        ),
        ficha=(("Aptitud", "Agrícola mixta"), ("Índice productivo", "Alto"),
               ("Agua", "Perforación y aguada"), ("Acceso", "Camino consolidado"),
               ("Mejoras", "Casa de capataz, galpón, silos")),
        fotos=_fotos("campo", "p001"), publication_id="sim_p001",
    ),
    Propiedad(
        id="p002", titulo="Chacra con casco y monte", operacion="venta", tipo="chacra",
        localidad="Roldán", zona="Zona rural", precio=410000,
        superficie_ha=22, lat=-32.8975, lng=-60.9053, destacada=True,
        descripcion=(
            "Chacra de 22 hectáreas con casco histórico, monte de eucaliptos y "
            "arboleda añosa. Ideal para vivienda de fin de semana, producción "
            "intensiva o emprendimiento turístico, a 25 minutos de Rosario."
        ),
        ficha=(("Aptitud", "Mixta y recreativa"), ("Agua", "Pozo y red"),
               ("Acceso", "Ruta asfaltada"), ("Mejoras", "Casco 220 m², monte, galpón")),
        fotos=_fotos("chacra", "p002"), publication_id="sim_p002",
    ),
    Propiedad(
        id="p003", titulo="Departamento 2 ambientes con balcón", operacion="venta",
        tipo="departamento", localidad="Rosario", zona="Centro", precio=78000,
        superficie_total_m2=58, superficie_cubierta_m2=52, ambientes=2, dormitorios=1,
        banios=1, lat=-32.9468, lng=-60.6393, destacada=True,
        descripcion=(
            "Luminoso dos ambientes al frente con balcón, cocina separada y "
            "baño completo. Edificio con ascensor y portería, a pasos del "
            "peatonal Córdoba."
        ),
        ficha=(("Antigüedad", "12 años"), ("Expensas", "$ 85.000"), ("Orientación", "Norte")),
        fotos=_fotos("departamento", "p003"), publication_id="sim_p003",
    ),
    Propiedad(
        id="p004", titulo="Casa 3 dormitorios con patio", operacion="venta", tipo="casa",
        localidad="Rosario", zona="Fisherton", precio=165000,
        superficie_total_m2=300, superficie_cubierta_m2=140, ambientes=5, dormitorios=3,
        banios=2, cocheras=2, lat=-32.9255, lng=-60.7390, destacada=True,
        descripcion=(
            "Casa en dos plantas sobre lote de 300 m². Living comedor, cocina "
            "integrada, tres dormitorios, dos baños, patio con parrilla y "
            "cochera para dos autos."
        ),
        ficha=(("Antigüedad", "8 años"), ("Calefacción", "Losa radiante"), ("Parrilla", "Sí")),
        fotos=_fotos("casa", "p004"), publication_id="sim_p004",
    ),
    Propiedad(
        id="p005", titulo="Campo ganadero con aguadas", operacion="venta", tipo="campo",
        localidad="San Javier", zona="Zona rural", precio=1050000,
        superficie_ha=420, lat=-30.5833, lng=-59.9333, destacada=True,
        descripcion=(
            "Campo ganadero de 420 hectáreas sobre albardones y pastizales "
            "naturales, con tres aguadas permanentes y alambrados en buen "
            "estado. Capacidad estimada de 450 madres."
        ),
        ficha=(("Aptitud", "Ganadera"), ("Agua", "Aguadas permanentes"),
               ("Acceso", "Camino de tierra"), ("Mejoras", "Corrales, manga, casa")),
        fotos=_fotos("campo", "p005"), publication_id="sim_p005",
    ),
    Propiedad(
        id="p006", titulo="Campo agrícola de primera", operacion="venta", tipo="campo",
        localidad="Carcarañá", zona="Zona rural", precio=1420000,
        superficie_ha=310, lat=-32.8500, lng=-60.8167, destacada=False,
        descripcion=(
            "310 hectáreas de suelos clase I y II, en una de las mejores zonas "
            "agrícolas del sur de Santa Fe. Sin mejoras importantes, listo "
            "para sembrar."
        ),
        ficha=(("Aptitud", "Agrícola"), ("Índice productivo", "Muy alto"),
               ("Agua", "Perforación"), ("Acceso", "Ruta provincial")),
        fotos=_fotos("campo", "p006"), publication_id="sim_p006",
    ),
    Propiedad(
        id="p007", titulo="Fracción para tambo", operacion="venta", tipo="campo",
        localidad="Casilda", zona="Zona rural", precio=720000,
        superficie_ha=95, lat=-33.0442, lng=-61.1683, destacada=False,
        descripcion=(
            "95 hectáreas con instalaciones de tambo, sala de ordeñe para 24 "
            "bajadas y alfalfares implantados. Tambo en funcionamiento."
        ),
        ficha=(("Aptitud", "Tambera"), ("Agua", "Perforación y molino"),
               ("Mejoras", "Sala de ordeñe, tinglado, casa")),
        fotos=_fotos("campo", "p007"), publication_id="sim_p007",
    ),
    Propiedad(
        id="p008", titulo="Chacra de 8 hectáreas", operacion="venta", tipo="chacra",
        localidad="Funes", zona="Zona rural", precio=260000,
        superficie_ha=8, lat=-32.9167, lng=-60.8167, destacada=False,
        descripcion=(
            "Chacra de 8 hectáreas a minutos del acceso a Funes, con casa "
            "principal, casa de huéspedes y pileta. Apta para proyecto "
            "residencial o turístico."
        ),
        ficha=(("Aptitud", "Mixta"), ("Agua", "Red y pozo"), ("Mejoras", "Dos casas, pileta")),
        fotos=_fotos("chacra", "p008"), publication_id="sim_p008",
    ),
    Propiedad(
        id="p009", titulo="Campo en arrendamiento por campaña", operacion="alquiler",
        tipo="campo", localidad="Firmat", zona="Zona rural", precio=450,
        moneda="USD", superficie_ha=240, lat=-33.4575, lng=-61.4833,
        descripcion=(
            "240 hectáreas disponibles para arrendamiento. Valor expresado "
            "en dólares por hectárea y por año; se acepta pago en quintales "
            "de soja."
        ),
        ficha=(("Aptitud", "Agrícola"), ("Modalidad", "Arrendamiento anual"),
               ("Valor", "USD 450 por ha")),
        fotos=_fotos("campo", "p009"), publication_id="sim_p009",
    ),
    Propiedad(
        id="p010", titulo="Local comercial sobre avenida", operacion="alquiler",
        tipo="local", localidad="Rosario", zona="Echesortu", precio=1250,
        superficie_total_m2=110, superficie_cubierta_m2=110,
        banios=1, lat=-32.9383, lng=-60.6718,
        descripcion=(
            "Local a la calle de 110 m² con vidriera amplia, depósito y baño. "
            "Excelente exposición y alto tránsito peatonal."
        ),
        ficha=(("Contrato", "3 años"), ("Actualización", "Semestral")),
        fotos=_fotos("local", "p010"), publication_id="sim_p010",
    ),
    Propiedad(
        id="p011", titulo="Departamento 3 ambientes a estrenar", operacion="venta",
        tipo="departamento", localidad="Rosario", zona="Pichincha", precio=112000,
        superficie_total_m2=78, superficie_cubierta_m2=70, ambientes=3, dormitorios=2,
        banios=2, cocheras=1, lat=-32.9345, lng=-60.6463,
        descripcion=(
            "Departamento a estrenar con amenities: SUM, pileta y solárium. "
            "Cochera cubierta incluida. Entrega inmediata."
        ),
        ficha=(("Estado", "A estrenar"), ("Amenities", "SUM, pileta, solárium")),
        fotos=_fotos("departamento", "p011"), publication_id="sim_p011",
    ),
    Propiedad(
        id="p012", titulo="Casa quinta con pileta", operacion="alquiler", tipo="casa",
        localidad="Funes", zona="Kentucky", precio=1800, moneda="USD",
        superficie_total_m2=1200, superficie_cubierta_m2=210, ambientes=6, dormitorios=4,
        banios=3, cocheras=3, lat=-32.9230, lng=-60.8120,
        descripcion=(
            "Casa en barrio abierto sobre lote de 1.200 m² con pileta, quincho "
            "y parque parquizado. Cuatro dormitorios, tres baños."
        ),
        ficha=(("Contrato", "2 años"), ("Pileta", "Sí"), ("Quincho", "Sí")),
        fotos=_fotos("casa", "p012"), publication_id="sim_p012",
    ),
    Propiedad(
        id="p013", titulo="Lote en barrio cerrado", operacion="venta", tipo="lote",
        localidad="Roldán", zona="Barrio cerrado", precio=58000,
        superficie_total_m2=850, lat=-32.8941, lng=-60.9012,
        descripcion=(
            "Lote de 850 m² en barrio cerrado con seguridad las 24 horas, "
            "espacios verdes y club house. Servicios al pie."
        ),
        ficha=(("Servicios", "Luz, agua, cloacas, gas"), ("Barrio", "Cerrado")),
        fotos=_fotos("lote", "p013"), publication_id="sim_p013",
    ),
)


class FuenteSimulada(FuenteBase):
    def todas(self) -> list:
        return list(_DATOS)
