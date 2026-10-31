import hmac
import secrets

from flask import request, session


def csrf_token() -> str:
    if "csrf" not in session:
        session["csrf"] = secrets.token_urlsafe(32)
    return session["csrf"]


def csrf_valido() -> bool:
    enviado = request.form.get("csrf", "")
    esperado = session.get("csrf", "")
    return bool(esperado) and hmac.compare_digest(enviado, esperado)
