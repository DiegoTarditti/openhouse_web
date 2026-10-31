import logging
import os
from urllib.parse import urlencode

from flask import Flask, render_template, request
from werkzeug.middleware.proxy_fix import ProxyFix

from config import SITIO, Config
from propiedades import crear_fuente
from propiedades.fuente import ORDENES
from propiedades.modelo import OPERACIONES, TIPOS
from seguridad import csrf_token


def formato_numero(valor, decimales: int = 0) -> str:
    """Formato argentino: 1.234.567 (y 1.234,5 con decimales)."""
    if valor is None:
        return ""
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def formato_precio(prop) -> str:
    if not prop.precio:
        return "Consultar"
    return f"{prop.moneda} {formato_numero(prop.precio)}"


def formato_ha(valor) -> str:
    if valor is None:
        return ""
    return f"{formato_numero(valor, 0 if float(valor).is_integer() else 1)} ha"


def create_app(config_extra: dict = None, fuente=None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_extra:
        app.config.update(config_extra)

    produccion = os.environ.get("ENTORNO", "desarrollo") == "produccion"
    if not app.config.get("SECRET_KEY"):
        if produccion:
            raise RuntimeError("Falta la variable SECRET_KEY: la web no arranca sin ella.")
        app.config["SECRET_KEY"] = "solo-desarrollo"
    if produccion:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    logging.basicConfig(level=logging.INFO)
    app.extensions["fuente"] = fuente or crear_fuente()

    # ── Filtros y datos globales de las plantillas ───────────────────────────
    app.jinja_env.filters["numero"] = formato_numero
    app.jinja_env.filters["precio"] = formato_precio
    app.jinja_env.filters["ha"] = formato_ha

    @app.context_processor
    def globales():
        return {
            "sitio": SITIO,
            "operaciones": OPERACIONES,
            "tipos": TIPOS,
            "ordenes": ORDENES,
            "csrf_token": csrf_token,
            "url_con": url_con,
            "cant_campos": app.extensions["fuente"].contar_rurales(),
        }

    # ── Rutas ────────────────────────────────────────────────────────────────
    from routes.publico import bp as publico
    from routes.formularios import bp as formularios
    from routes.seo import bp as seo

    app.register_blueprint(publico)
    app.register_blueprint(formularios)
    app.register_blueprint(seo)

    @app.after_request
    def cabeceras(resp):
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        resp.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        if request.endpoint == "static":
            resp.headers.setdefault("Cache-Control", "public, max-age=86400")
        return resp

    @app.errorhandler(404)
    def no_encontrada(_e):
        return render_template("error.html", codigo=404,
                               titulo="No encontramos esa página",
                               detalle="Puede que la propiedad ya no esté publicada."), 404

    @app.errorhandler(500)
    def error_interno(_e):
        return render_template("error.html", codigo=500,
                               titulo="Algo salió mal de nuestro lado",
                               detalle="Probá de nuevo en unos minutos."), 500

    return app


def url_con(**cambios) -> str:
    """URL actual con parámetros cambiados (para paginado y orden)."""
    params = {k: v for k, v in request.args.items() if k != "pagina"}
    for clave, valor in cambios.items():
        if valor in (None, ""):
            params.pop(clave, None)
        else:
            params[clave] = valor
    qs = urlencode(params)
    return request.path + (f"?{qs}" if qs else "")


app = create_app() if os.environ.get("ENTORNO") != "pruebas" else None

if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", "5070"))
    app.run(host="127.0.0.1", port=puerto, debug=True)
