import hashlib

from flask import Blueprint, Response, abort, current_app, redirect, render_template, request, url_for

from propiedades.fuente import ORDENES, Filtros
from propiedades.modelo import OPERACIONES, TIPOS, id_desde_slug

bp = Blueprint("publico", __name__)

MAX_MARCADORES = 300


def _fuente():
    return current_app.extensions["fuente"]


def _num(valor, entero: bool = False):
    """Número tolerante: acepta '1.500.000', '1500000', '12,5'. None si no es número."""
    if valor is None:
        return None
    t = str(valor).strip().replace(" ", "")
    if not t:
        return None
    if "," in t:
        t = t.replace(".", "").replace(",", ".")
    elif t.count(".") > 1 or (t.count(".") == 1 and len(t.rsplit(".", 1)[1]) == 3):
        t = t.replace(".", "")
    try:
        n = float(t)
    except ValueError:
        return None
    if n < 0 or n != n or n == float("inf"):
        return None
    return int(n) if entero else n


def leer_filtros(args, forzar_rural: bool = False) -> Filtros:
    operacion = args.get("operacion", "")
    tipo = args.get("tipo", "")
    orden = args.get("orden", "recientes")
    return Filtros(
        operacion=operacion if operacion in OPERACIONES else "",
        tipo=tipo if tipo in TIPOS else "",
        rural=forzar_rural,
        texto=(args.get("q", "") or "").strip()[:80],
        precio_min=_num(args.get("precio_min")),
        precio_max=_num(args.get("precio_max")),
        ha_min=_num(args.get("ha_min")),
        ha_max=_num(args.get("ha_max")),
        dormitorios_min=_num(args.get("dorm"), entero=True),
        orden=orden if orden in ORDENES else "recientes",
        pagina=_num(args.get("pagina"), entero=True) or 1,
    )


def _filtros_activos(f: Filtros) -> bool:
    return any((f.operacion, f.tipo, f.texto, f.precio_min, f.precio_max,
                f.ha_min, f.ha_max, f.dormitorios_min))


def _marcador(p) -> dict:
    return {
        "id": p.id, "titulo": p.titulo, "lat": p.lat, "lng": p.lng,
        "url": url_for("publico.ficha", slug=p.slug),
        "precio": f"{p.moneda} {p.precio:,.0f}".replace(",", ".") if p.precio else "Consultar",
        "ubicacion": p.ubicacion, "tipo": p.tipo_etiqueta, "rural": p.es_rural,
        "foto": p.fotos[0] if p.fotos else "",
    }


@bp.route("/")
def inicio():
    fuente = _fuente()
    return render_template(
        "inicio.html",
        destacadas=fuente.destacadas(4),
        rurales=[p for p in fuente.todas() if p.es_rural and p.operacion == "venta"][:3],
    )


def _listado(forzar_rural: bool, plantilla: str, **extra):
    filtros = leer_filtros(request.args, forzar_rural=forzar_rural)
    fuente = _fuente()
    res = fuente.buscar(filtros)
    # Si piden una página que no existe, volver a la última válida.
    if filtros.pagina != res.pagina:
        args = {**request.args.to_dict(), "pagina": res.pagina}
        return redirect(url_for(request.endpoint, **args))
    marcadores = [
        _marcador(p) for p in fuente.coincidencias(filtros) if p.tiene_mapa
    ][:MAX_MARCADORES]
    return render_template(
        plantilla, res=res, f=filtros, marcadores=marcadores,
        hay_filtros=_filtros_activos(filtros),
        vista="mapa" if request.args.get("vista") == "mapa" else "lista",
        **extra,
    )


@bp.route("/propiedades")
def listado():
    return _listado(False, "listado.html", rural=False)


@bp.route("/campos")
def campos():
    return _listado(True, "listado.html", rural=True)


@bp.route("/propiedad/<slug>")
def ficha(slug):
    prop = _fuente().obtener(id_desde_slug(slug))
    if prop is None:
        abort(404)
    if prop.slug != slug:  # URL vieja o mal escrita: ir a la canónica
        return redirect(url_for("publico.ficha", slug=prop.slug), code=301)
    return render_template("ficha.html", p=prop, similares=_fuente().similares(prop))


@bp.route("/nosotros")
def nosotros():
    return render_template("nosotros.html")


@bp.route("/tasaciones")
def tasaciones():
    return render_template("tasaciones.html")


@bp.route("/publicar")
def publicar():
    return render_template("publicar.html")


@bp.route("/contacto")
def contacto():
    return render_template("contacto.html", propiedad=None)


# ── Imágenes de ejemplo (se reemplazan por las fotos de Tokko) ───────────────

_PALETAS = (
    ("#BFD8DC", "#E9EFE6", "#7FA37A", "#C9B26B"),
    ("#F1D9B5", "#F6EEDD", "#8DA760", "#B8924A"),
    ("#C8D5E6", "#EAEFF2", "#6E9A7C", "#D2BE7E"),
    ("#E4C9B8", "#F3E8DC", "#9CAF72", "#BE9B5A"),
)


def _svg_paisaje(tipo: str, semilla: str) -> str:
    h = int(hashlib.sha1(semilla.encode()).hexdigest(), 16)
    cielo, claro, verde, oro = _PALETAS[h % len(_PALETAS)]
    base = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" '
            f'preserveAspectRatio="xMidYMid slice">'
            f'<defs><linearGradient id="c" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{cielo}"/><stop offset="1" stop-color="{claro}"/>'
            f'</linearGradient></defs><rect width="800" height="600" fill="url(#c)"/>')
    desplaza = 40 + (h >> 4) % 120
    if tipo in ("campo", "chacra"):
        franjas = "".join(
            f'<path d="M0 {330 + i * 55} Q 400 {300 + i * 55 - desplaza // 4} 800 {330 + i * 55} '
            f'V {385 + i * 55} H0Z" fill="{verde if i % 2 == 0 else oro}" opacity="{0.55 + i * 0.1:.2f}"/>'
            for i in range(5)
        )
        arbol = (f'<rect x="{560 + desplaza}" y="262" width="8" height="70" fill="#6B5A3E"/>'
                 f'<circle cx="{564 + desplaza}" cy="252" r="34" fill="#5E8560"/>')
        return base + '<circle cx="640" cy="110" r="42" fill="#FFF6D6" opacity=".85"/>' + franjas + arbol + "</svg>"
    if tipo == "departamento":
        torres = "".join(
            f'<rect x="{80 + i * 105}" y="{170 + (i * 37 + h) % 90}" width="90" '
            f'height="{430 - 170 - (i * 37 + h) % 90}" fill="{"#5F7F86" if i % 2 else "#7E9AA0"}"/>'
            for i in range(7)
        )
        ventanas = "".join(
            f'<rect x="{96 + i * 105 + c * 26}" y="{200 + r * 36 + (i * 37 + h) % 90}" '
            f'width="14" height="20" fill="#F3E6B5" opacity=".8"/>'
            for i in range(7) for r in range(5) for c in range(3)
        )
        return base + torres + ventanas + f'<rect y="540" width="800" height="60" fill="{verde}"/></svg>'
    if tipo == "local":
        return (base + '<rect x="120" y="190" width="560" height="350" fill="#6F8A91"/>'
                f'<rect x="120" y="190" width="560" height="52" fill="{oro}"/>'
                '<rect x="160" y="280" width="300" height="260" fill="#CFE0E3"/>'
                '<rect x="500" y="300" width="140" height="240" fill="#4A6169"/>'
                f'<rect y="540" width="800" height="60" fill="#9AA3A0"/></svg>')
    if tipo == "lote":
        return (base + f'<rect y="380" width="800" height="220" fill="{verde}"/>'
                '<path d="M120 560 L300 400 L700 400 L690 560Z" fill="none" stroke="#6B5A3E" '
                'stroke-width="5" stroke-dasharray="14 10"/>'
                f'<circle cx="240" cy="360" r="40" fill="{verde}"/>'
                '<rect x="236" y="380" width="8" height="40" fill="#6B5A3E"/></svg>')
    # casa
    return (base + f'<rect y="440" width="800" height="160" fill="{verde}"/>'
            '<rect x="230" y="270" width="340" height="190" fill="#EFE7D6"/>'
            '<path d="M200 275 L400 150 L600 275Z" fill="#B4684A"/>'
            '<rect x="370" y="360" width="60" height="100" fill="#7A5B3C"/>'
            '<rect x="270" y="320" width="64" height="56" fill="#9FC3CC"/>'
            '<rect x="466" y="320" width="64" height="56" fill="#9FC3CC"/></svg>')


@bp.route("/placeholder/<tipo>/<semilla>.svg")
def placeholder(tipo, semilla):
    if tipo not in TIPOS:
        abort(404)
    resp = Response(_svg_paisaje(tipo, semilla), mimetype="image/svg+xml")
    resp.headers["Cache-Control"] = "public, max-age=604800"
    return resp
