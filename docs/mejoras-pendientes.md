# Pendientes — web Open House

## Semana del 2026-11-02: integración con Tokko
Necesita la **API key de la inmobiliaria** (administrador: tokkobroker.com → Mi empresa → Permisos). Docs: https://developers.tokkobroker.com

- [ ] Con la key, mirar el playground (`/api/playground`) y confirmar: campos de una propiedad, **hectáreas en campos**, precio por ha, coordenadas, fotos, paginación y filtros que acepta el servidor.
- [ ] `propiedades/tokko.py`: `FuenteTokko(FuenteBase)` que implemente `todas()` y mapee a `Propiedad`. Activar con `FUENTE_PROPIEDADES=tokko` y `TOKKO_API_KEY`.
- [ ] Caché de la respuesta (unos minutos) para no consultar la API en cada visita; definir qué pasa si Tokko no responde (mostrar la última copia).
- [ ] Consultas como lead: `POST http://tokkobroker.com/portals/simple_portal/api/v1/contact/` con `publication_id` (ya viaja en `Consulta.publication_id`). Verificar si responde por HTTPS. Mantener el correo como respaldo.
- [ ] Reemplazar las imágenes de ejemplo por las fotos de Tokko; revisar `og:image` y JSON-LD.
- [ ] Ubicación de campos: confirmar si la coordenada es exacta o aproximada (hoy el mapa de la ficha rural dibuja un área de 3 km).
- [ ] Tokko no documenta webhooks: definir cada cuánto se refresca el catálogo.

## Contenido y datos que tiene que confirmar la inmobiliaria
- [ ] Dirección, teléfono, WhatsApp, mail y horario reales (hoy son de ejemplo, en `config.py` / variables `SITIO_*`).
- [ ] Cifras del inicio (850+ operaciones, 15 años) y texto de "Nosotros" (matrícula, equipo, historia).
- [ ] Logo definitivo y dominio.
- [ ] Qué hace "Publicar propiedad": hoy es un formulario que llega por mail.

## Antes de publicar
- [ ] Elegir hosting (Render) y cargar variables: `ENTORNO=produccion`, `SECRET_KEY`, `SITIO_URL`, SMTP y `CONSULTAS_DESTINO`.
- [ ] Probar el envío real de correo (hoy sin SMTP las consultas solo van al log).
- [ ] Google Search Console: subir `/sitemap.xml`. Google Analytics o similar si lo piden.
- [ ] Revisar contraste y navegación por teclado con las fotos reales.
- [ ] Anti-spam: el límite por IP es en memoria (por proceso). Si se usan varios workers, pasar a un contador compartido.

## Posibles mejoras
- Favoritos y comparador de campos (se dejaron afuera a pedido).
- Búsquedas guardadas con aviso por mail.
- Blog o notas de mercado rural (SEO).
- Filtros rurales específicos (aptitud, agua) una vez que se vea qué trae Tokko.
