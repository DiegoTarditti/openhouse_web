from datetime import date

from flask import Blueprint, Response, current_app, url_for

from config import SITIO

bp = Blueprint("seo", __name__)


def _absoluta(ruta: str) -> str:
    return SITIO["url"] + ruta


@bp.route("/robots.txt")
def robots():
    texto = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /gracias\n"
        "Disallow: /contacto\n"
        f"Sitemap: {_absoluta('/sitemap.xml')}\n"
    )
    return Response(texto, mimetype="text/plain")


@bp.route("/sitemap.xml")
def sitemap():
    hoy = date.today().isoformat()
    fijas = [
        ("publico.inicio", 1.0), ("publico.listado", 0.9), ("publico.campos", 0.9),
        ("publico.nosotros", 0.5), ("publico.tasaciones", 0.6), ("publico.publicar", 0.6),
    ]
    urls = [(_absoluta(url_for(ep)), prio) for ep, prio in fijas]
    for p in current_app.extensions["fuente"].todas():
        urls.append((_absoluta(url_for("publico.ficha", slug=p.slug)), 0.8))
    filas = "".join(
        f"<url><loc>{u}</loc><lastmod>{hoy}</lastmod><priority>{prio}</priority></url>"
        for u, prio in urls
    )
    xml = ('<?xml version="1.0" encoding="UTF-8"?>'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + filas + "</urlset>")
    return Response(xml, mimetype="application/xml")
