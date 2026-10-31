"""Formularios de la web: validación, anti-spam y envío de la consulta.

Hoy la consulta sale por correo (o al log si no hay SMTP). La semana que viene
se agrega el envío a Tokko como lead sin tocar las páginas: solo `enviar`.
"""
import logging
import re
import smtplib
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from email.message import EmailMessage

log = logging.getLogger("consultas")

TIPOS_CONSULTA = {
    "contacto": "Consulta general",
    "propiedad": "Consulta por una propiedad",
    "tasacion": "Pedido de tasación",
    "publicar": "Quiero publicar mi propiedad",
}

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]{2,}$")
_TEL_RE = re.compile(r"^[0-9+()\-.\s]{6,25}$")

# Ventana deslizante por IP. Es en memoria: alcanza para un proceso; si se
# corren varios workers, cada uno cuenta aparte.
_envios = defaultdict(deque)


@dataclass
class Consulta:
    tipo: str = "contacto"
    nombre: str = ""
    email: str = ""
    telefono: str = ""
    mensaje: str = ""
    propiedad_id: str = ""
    propiedad_titulo: str = ""
    publication_id: str = ""
    extra: dict = field(default_factory=dict)  # tasación / publicar: tipo, zona, ha…


def limpiar(valor, largo: int) -> str:
    texto = " ".join(str(valor or "").split()) if largo <= 200 else str(valor or "").strip()
    return texto[:largo]


def validar(c: Consulta) -> dict:
    """Devuelve {campo: mensaje}. Vacío si está todo bien."""
    errores = {}
    if len(c.nombre) < 2:
        errores["nombre"] = "Contanos tu nombre."
    if not _EMAIL_RE.match(c.email):
        errores["email"] = "Revisá el correo: parece incompleto."
    if c.telefono and not _TEL_RE.match(c.telefono):
        errores["telefono"] = "El teléfono solo puede llevar números, +, ( ) y guiones."
    if c.tipo in ("contacto", "propiedad") and len(c.mensaje) < 10:
        errores["mensaje"] = "Escribinos un poco más de detalle (mínimo 10 letras)."
    if c.tipo in ("tasacion", "publicar") and not c.telefono:
        errores["telefono"] = "Dejanos un teléfono para coordinar la visita."
    return errores


def excede_limite(ip: str, maximo: int, ahora: float = None) -> bool:
    ahora = ahora if ahora is not None else time.time()
    cola = _envios[ip]
    while cola and ahora - cola[0] > 3600:
        cola.popleft()
    if len(cola) >= maximo:
        return True
    cola.append(ahora)
    return False


def reiniciar_limites():
    _envios.clear()


def armar_correo(c: Consulta, remitente: str, destino: str) -> EmailMessage:
    msg = EmailMessage()
    asunto = TIPOS_CONSULTA.get(c.tipo, "Consulta")
    if c.propiedad_titulo:
        asunto += f": {c.propiedad_titulo}"
    msg["Subject"] = f"[Web] {asunto}"[:200]
    msg["From"] = remitente
    msg["To"] = destino
    msg["Reply-To"] = c.email
    lineas = [
        f"Tipo: {TIPOS_CONSULTA.get(c.tipo, c.tipo)}",
        f"Nombre: {c.nombre}",
        f"Correo: {c.email}",
        f"Teléfono: {c.telefono or '-'}",
    ]
    if c.propiedad_titulo:
        lineas.append(f"Propiedad: {c.propiedad_titulo} ({c.propiedad_id})")
    for clave, valor in c.extra.items():
        if valor:
            lineas.append(f"{clave}: {valor}")
    if c.mensaje:
        lineas += ["", c.mensaje]
    msg.set_content("\n".join(lineas))
    return msg


def enviar(c: Consulta, cfg) -> bool:
    """Entrega la consulta. True si salió (o si quedó en el log por no haber SMTP)."""
    msg = armar_correo(c, cfg["CONSULTAS_REMITENTE"], cfg["CONSULTAS_DESTINO"])
    if not cfg["SMTP_HOST"]:
        log.warning("SMTP no configurado; consulta registrada:\n%s", msg.get_content())
        return True
    try:
        with smtplib.SMTP(cfg["SMTP_HOST"], cfg["SMTP_PORT"], timeout=10) as s:
            s.starttls()
            if cfg["SMTP_USER"]:
                s.login(cfg["SMTP_USER"], cfg["SMTP_PASSWORD"])
            s.send_message(msg)
        return True
    except (smtplib.SMTPException, OSError):
        log.exception("No se pudo enviar la consulta por correo")
        return False
