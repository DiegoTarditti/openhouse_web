## Reglas de trabajo

1. **Commit y push solo cuando Diego lo pida** ("subí", "dale"). Antes de subir, correr las pruebas.
2. **Prueba antes de decir listo**: correr `python -m pytest tests -q` y mostrar la salida; para cambios visuales, una captura.
3. **Avisar antes de endurecer producción**: si un cambio exige tocar variables de Render, decirlo *antes* de subir.
4. **Responder en español rioplatense**, sin jerga o explicándola. Diego no es programador de oficio.
5. Al cerrar una tarea, actualizar `docs/mejoras-pendientes.md`. Leerlo al empezar la sesión.

---

# Open House — web pública

Sitio de la inmobiliaria (venta y alquiler, con foco en campos y chacras de Santa Fe). Repo `DiegoTarditti/openhouse_web`. Es **independiente** de la app de administración (`openhouse`): repos, bases y deploy separados; esta web no tiene login ni base de datos.

## Stack y estructura

- `Flask` + `Jinja2` (HTML renderizado en el servidor, por SEO), CSS propio sin framework, JS sin dependencias salvo Leaflet (mapas, OpenStreetMap, sin key). `gunicorn app:app` en producción.
- `app.py` fábrica `create_app`; `config.py` datos del sitio y SMTP (todo por variables de entorno, ver `.env.example`); `seguridad.py` CSRF; `consultas.py` validación, anti-spam y envío de formularios.
- `propiedades/`: **la web solo conoce `Propiedad` (`modelo.py`)**. `fuente.py` filtra/ordena/pagina sobre cualquier origen; `simulados.py` son datos inventados; `crear_fuente()` elige el origen con `FUENTE_PROPIEDADES`.
- `routes/`: `publico.py` (páginas + imágenes de ejemplo), `formularios.py` (POST), `seo.py` (robots, sitemap). `templates/`, `static/`.
- `docs/boceto/index.html` es el diseño original "Litoral Moderno" (referencia, no se sirve).

## Cosas que no se deducen leyendo el código

- **Puerto 5070 en desarrollo**: Chromium bloquea el 5060 (`ERR_UNSAFE_PORT`) y el 5000 es de AppFarmWeb.
- **La API key de Tokko nunca va al navegador**: Tokko la recibe en la URL, así que toda llamada sale del servidor.
- **Los datos de una consulta por propiedad salen del servidor**, no del formulario (`routes/formularios.py`): el cliente solo manda `propiedad_id`.
- **Los macros de Jinja se importan `with context`** (necesitan `csrf_token`); sin eso la página falla.
- **Sin `SECRET_KEY` la web no arranca en producción** (`ENTORNO=produccion`). Es a propósito; Render tiene que tenerla cargada antes del primer deploy.
- Las fotos son URLs (hoy `/placeholder/...svg`, luego las de Tokko). **El sitio no guarda archivos en el servidor.**
- Listados filtrados o paginados llevan `noindex`; las fichas tienen URL canónica y datos estructurados (JSON-LD).
- Leaflet se carga de unpkg con SRI (hash verificado). Si se cambia la versión, recalcular el hash.

## Cómo probar

- Local: `python app.py` → http://127.0.0.1:5070
- Pruebas: `python -m pytest tests -q` (43 chequeos: filtros, páginas, SEO, formularios, anti-spam, CSRF).
- Lint: `python -m ruff check .`
