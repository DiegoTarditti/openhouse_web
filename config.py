import os

# Datos de la inmobiliaria: se muestran en la web. Los valores por defecto son
# de ejemplo y se pisan con variables de entorno cuando estén confirmados.
SITIO = {
    "nombre": os.environ.get("SITIO_NOMBRE", "Open House"),
    "slogan": "Inmobiliaria en Rosario y zona rural santafesina",
    "url": os.environ.get("SITIO_URL", "http://localhost:5070").rstrip("/"),
    "direccion": os.environ.get("SITIO_DIRECCION", "Córdoba 1234, Rosario, Santa Fe"),
    "telefono": os.environ.get("SITIO_TELEFONO", "+54 341 555-0123"),
    "whatsapp": os.environ.get("SITIO_WHATSAPP", "5493415550123"),
    "email": os.environ.get("SITIO_EMAIL", "hola@openhouse.com.ar"),
    "horario": os.environ.get("SITIO_HORARIO", "Lunes a viernes de 9 a 18 hs"),
}


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    # Correo saliente de las consultas. Sin SMTP_HOST las consultas se
    # registran en el log (útil en desarrollo).
    SMTP_HOST = os.environ.get("SMTP_HOST", "")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USER = os.environ.get("SMTP_USER", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
    CONSULTAS_DESTINO = os.environ.get("CONSULTAS_DESTINO", SITIO["email"])
    CONSULTAS_REMITENTE = os.environ.get("CONSULTAS_REMITENTE", SMTP_USER or SITIO["email"])
    # Tope de envíos de formulario por IP y por hora (anti-spam).
    LIMITE_FORMULARIOS_HORA = int(os.environ.get("LIMITE_FORMULARIOS_HORA", "8"))
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("ENTORNO", "desarrollo") == "produccion"
    JSON_AS_ASCII = False
