"""Pruebas de la web: filtros, páginas, formularios y SEO.

Correr con:  python -m pytest tests -q
"""
import os
import re
import sys

os.environ["ENTORNO"] = "pruebas"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest  # noqa: E402

import consultas  # noqa: E402
from app import create_app, formato_numero  # noqa: E402
from propiedades.fuente import Filtros  # noqa: E402
from propiedades.simulados import FuenteSimulada  # noqa: E402
from routes.publico import _num  # noqa: E402


@pytest.fixture
def app():
    consultas.reiniciar_limites()
    return create_app({"TESTING": True, "SECRET_KEY": "x", "SMTP_HOST": ""})


@pytest.fixture
def cli(app):
    return app.test_client()


def _token(cli, ruta="/contacto"):
    html = cli.get(ruta).get_data(as_text=True)
    return re.search(r'name="csrf" value="([^"]+)"', html).group(1)


# ── Filtros ──────────────────────────────────────────────────────────────────
F = FuenteSimulada()


def test_rural_solo_campos_y_chacras():
    res = F.buscar(Filtros(rural=True))
    assert res.total > 0
    assert all(p.tipo in ("campo", "chacra") for p in res.propiedades)


def test_filtro_hectareas():
    res = F.buscar(Filtros(rural=True, ha_min=100, ha_max=300))
    assert res.total > 0
    assert all(100 <= p.superficie_ha <= 300 for p in res.propiedades)


def test_texto_ignora_tildes_y_mayusculas():
    assert F.buscar(Filtros(texto="CAÑADA")).total == F.buscar(Filtros(texto="canada")).total > 0


def test_precio_y_orden():
    res = F.buscar(Filtros(operacion="venta", orden="precio_asc"))
    precios = [p.precio for p in res.propiedades]
    assert precios == sorted(precios)


def test_orden_hectareas_desc():
    res = F.buscar(Filtros(rural=True, orden="ha_desc"))
    has = [p.superficie_ha for p in res.propiedades]
    assert has == sorted(has, reverse=True)


def test_precio_por_ha_solo_en_venta_rural():
    campo = F.obtener("p001")
    assert campo.precio_por_ha == pytest.approx(3200)
    assert F.obtener("p009").precio_por_ha is None   # arrendamiento
    assert F.obtener("p003").precio_por_ha is None   # departamento


def test_pagina_fuera_de_rango_se_corrige():
    res = F.buscar(Filtros(pagina=999))
    assert res.pagina == res.paginas >= 1


@pytest.mark.parametrize("entrada,esperado", [
    ("1.500.000", 1500000), ("1500000", 1500000), ("12,5", 12.5),
    ("1.234,5", 1234.5), ("12.5", 12.5), ("", None), ("abc", None), ("-3", None),
])
def test_num_tolerante(entrada, esperado):
    assert _num(entrada) == esperado


def test_formato_argentino():
    assert formato_numero(1234567) == "1.234.567"
    assert formato_numero(3200) == "3.200"


# ── Páginas ──────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("ruta", [
    "/", "/propiedades", "/campos", "/nosotros", "/tasaciones", "/publicar",
    "/contacto", "/propiedades?vista=mapa", "/campos?vista=mapa&ha_min=100",
    "/robots.txt", "/sitemap.xml", "/gracias?tipo=tasacion",
])
def test_paginas_responden(cli, ruta):
    assert cli.get(ruta).status_code == 200


def test_ficha_y_redireccion_canonica(cli):
    p = F.obtener("p001")
    r = cli.get(f"/propiedad/{p.slug}")
    assert r.status_code == 200
    html = r.get_data(as_text=True)
    assert "Campo agrícola mixto" in html
    assert "USD 3.200 por hectárea" in html
    assert 'rel="canonical"' in html and "application/ld+json" in html
    r = cli.get("/propiedad/slug-viejo-p001")
    assert r.status_code == 301 and r.headers["Location"].endswith(p.slug)


def test_ficha_inexistente_404(cli):
    assert cli.get("/propiedad/nada-p999").status_code == 404
    assert cli.get("/no-existe").status_code == 404


def test_filtros_basura_no_rompen(cli):
    r = cli.get("/propiedades?precio_min=abc&ha_max=--&dorm=x&pagina=-4&orden=hack&tipo=zzz")
    assert r.status_code == 200


def test_listado_filtrado_no_se_indexa(cli):
    assert 'noindex' in cli.get("/propiedades?tipo=casa").get_data(as_text=True)
    assert 'noindex' not in cli.get("/propiedades").get_data(as_text=True)


def test_xss_en_busqueda_se_escapa(cli):
    html = cli.get('/propiedades?q=<script>alert(1)</script>').get_data(as_text=True)
    assert "<script>alert(1)</script>" not in html


def test_placeholder_svg(cli):
    r = cli.get("/placeholder/campo/p001-1.svg")
    assert r.status_code == 200 and r.mimetype == "image/svg+xml"
    assert cli.get("/placeholder/zzz/a.svg").status_code == 404


def test_sitemap_incluye_fichas(cli):
    xml = cli.get("/sitemap.xml").get_data(as_text=True)
    assert xml.count("<url>") >= 6 + len(F.todas())
    assert "campo-agricola-mixto-p001" in xml


# ── Formularios ──────────────────────────────────────────────────────────────
VALIDO = {"nombre": "Ana Pérez", "email": "ana@example.com",
          "telefono": "341 555-0000", "mensaje": "Quiero más información, gracias."}


def test_contacto_ok(cli, caplog):
    caplog.set_level("WARNING")
    r = cli.post("/contacto", data={**VALIDO, "csrf": _token(cli)})
    assert r.status_code == 302 and "/gracias" in r.headers["Location"]
    assert "ana@example.com" in caplog.text


def test_consulta_por_propiedad_usa_datos_del_servidor(cli, caplog):
    caplog.set_level("WARNING")
    r = cli.post("/contacto", data={**VALIDO, "csrf": _token(cli), "propiedad_id": "p001"})
    assert r.status_code == 302
    assert "Campo agrícola mixto" in caplog.text


def test_sin_csrf_se_rechaza(cli):
    cli.get("/contacto")
    r = cli.post("/contacto", data=VALIDO)
    assert r.status_code == 400


def test_validacion_muestra_errores_y_conserva_valores(cli):
    datos = {**VALIDO, "email": "mal", "csrf": _token(cli)}
    r = cli.post("/contacto", data=datos)
    html = r.get_data(as_text=True)
    assert r.status_code == 400
    assert "Revisá el correo" in html and 'value="Ana Pérez"' in html


def test_honeypot_descarta_sin_enviar(cli, caplog):
    caplog.set_level("WARNING")
    r = cli.post("/contacto", data={**VALIDO, "csrf": _token(cli), "sitio_web": "http://spam"})
    assert r.status_code == 302
    assert "ana@example.com" not in caplog.text


def test_limite_por_ip(cli):
    tok = _token(cli)
    for _ in range(8):
        assert cli.post("/contacto", data={**VALIDO, "csrf": tok}).status_code == 302
    assert cli.post("/contacto", data={**VALIDO, "csrf": tok}).status_code == 400


def test_tasacion_exige_telefono(cli):
    datos = {"nombre": "Luis", "email": "l@example.com", "csrf": _token(cli, "/tasaciones")}
    assert cli.post("/tasaciones", data=datos).status_code == 400
    ok = cli.post("/tasaciones", data={**datos, "telefono": "3415550000"})
    assert ok.status_code == 302


def test_encabezados_mail_no_se_inyectan():
    c = consultas.Consulta(nombre="Ana\r\nBcc: x@y.z", email="a@b.cc", mensaje="hola hola hola")
    c.nombre = consultas.limpiar(c.nombre, 80)
    msg = consultas.armar_correo(c, "web@x.com", "info@x.com")
    assert "\n" not in msg["Subject"] and "Bcc" not in msg
