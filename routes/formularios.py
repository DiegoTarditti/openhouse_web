from flask import Blueprint, current_app, redirect, render_template, request, url_for

from consultas import TIPOS_CONSULTA, Consulta, enviar, excede_limite, limpiar, validar
from seguridad import csrf_valido

bp = Blueprint("formularios", __name__)

# Página que se vuelve a mostrar (con errores) según el formulario.
_PLANTILLAS = {
    "contacto": "contacto.html",
    "propiedad": "ficha.html",
    "tasacion": "tasaciones.html",
    "publicar": "publicar.html",
}


def _leer(tipo: str) -> Consulta:
    f = request.form
    c = Consulta(
        tipo=tipo,
        nombre=limpiar(f.get("nombre"), 80),
        email=limpiar(f.get("email"), 120),
        telefono=limpiar(f.get("telefono"), 25),
        mensaje=limpiar(f.get("mensaje"), 2000),
    )
    if tipo == "tasacion":
        c.extra = {
            "Tipo de propiedad": limpiar(f.get("tipo_propiedad"), 40),
            "Dirección o zona": limpiar(f.get("direccion"), 120),
            "Superficie": limpiar(f.get("superficie"), 40),
        }
    elif tipo == "publicar":
        c.extra = {
            "Operación": limpiar(f.get("operacion"), 20),
            "Tipo de propiedad": limpiar(f.get("tipo_propiedad"), 40),
            "Ubicación": limpiar(f.get("direccion"), 120),
            "Superficie": limpiar(f.get("superficie"), 40),
        }
    return c


def _fuente():
    return current_app.extensions["fuente"]


def _procesar(tipo: str):
    # El tipo de consulta por propiedad llega por /contacto con propiedad_id.
    prop = None
    if tipo == "contacto" and request.form.get("propiedad_id"):
        prop = _fuente().obtener(limpiar(request.form.get("propiedad_id"), 20))
        if prop is not None:
            tipo = "propiedad"
    c = _leer(tipo)
    if prop is not None:  # los datos de la propiedad salen del servidor, no del form
        c.propiedad_id, c.propiedad_titulo = prop.id, prop.titulo
        c.publication_id = prop.publication_id

    def volver(errores, mensaje_general=""):
        ctx = {"errores": errores, "valores": request.form, "mensaje_general": mensaje_general}
        if prop is not None:
            ctx.update(p=prop, similares=_fuente().similares(prop))
        else:
            ctx["propiedad"] = None
        return render_template(_PLANTILLAS[tipo], **ctx), 400

    # Honeypot: un campo oculto que las personas no llenan. Respondemos como si
    # hubiera salido bien para no darle pistas al bot.
    if request.form.get("sitio_web"):
        return redirect(url_for("formularios.gracias", tipo=tipo))

    if not csrf_valido():
        return volver({}, "La página estuvo abierta demasiado tiempo. Probá de nuevo.")

    ip = request.remote_addr or "?"
    if excede_limite(ip, current_app.config["LIMITE_FORMULARIOS_HORA"]):
        return volver({}, "Enviaste varias consultas seguidas. Esperá un rato o escribinos por WhatsApp.")

    errores = validar(c)
    if errores:
        return volver(errores)

    if not enviar(c, current_app.config):
        return volver({}, "No pudimos enviar tu consulta. Escribinos por WhatsApp y te respondemos enseguida.")
    return redirect(url_for("formularios.gracias", tipo=tipo))


@bp.post("/contacto")
def enviar_contacto():
    return _procesar("contacto")


@bp.post("/tasaciones")
def enviar_tasacion():
    return _procesar("tasacion")


@bp.post("/publicar")
def enviar_publicar():
    return _procesar("publicar")


@bp.get("/gracias")
def gracias():
    tipo = request.args.get("tipo", "contacto")
    if tipo not in TIPOS_CONSULTA:
        tipo = "contacto"
    return render_template("gracias.html", tipo=tipo, tipo_texto=TIPOS_CONSULTA[tipo])
