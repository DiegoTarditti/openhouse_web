/* Mapas con Leaflet + OpenStreetMap. Los textos se arman con textContent
   (nunca innerHTML) porque vienen de una fuente externa. */
(function () {
  if (typeof L === 'undefined') return;

  var TILES = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
  var ATRIB = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>';
  var COLOR_URBANO = '#0E5C6B', COLOR_RURAL = '#8A6C1E';

  function crearMapa(el) {
    var mapa = L.map(el, { scrollWheelZoom: false });
    L.tileLayer(TILES, { maxZoom: 18, attribution: ATRIB }).addTo(mapa);
    // La rueda hace zoom solo después de hacer clic, para no trabar el scroll de la página.
    mapa.on('focus', function () { mapa.scrollWheelZoom.enable(); });
    mapa.on('blur', function () { mapa.scrollWheelZoom.disable(); });
    return mapa;
  }

  function popup(m) {
    var caja = document.createElement('div');
    caja.className = 'mapa-popup';
    if (m.foto) {
      var img = document.createElement('img');
      img.src = m.foto; img.alt = ''; img.loading = 'lazy';
      caja.appendChild(img);
    }
    var t = document.createElement('strong'); t.textContent = m.titulo; caja.appendChild(t);
    var u = document.createElement('span'); u.textContent = m.ubicacion; caja.appendChild(u);
    var p = document.createElement('span'); p.textContent = m.precio; caja.appendChild(p);
    var a = document.createElement('a'); a.href = m.url; a.textContent = 'Ver ficha →'; caja.appendChild(a);
    return caja;
  }

  // Listado: un punto por propiedad.
  var contenedor = document.getElementById('mapa');
  var datos = document.getElementById('datos-mapa');
  if (contenedor && datos) {
    var marcadores = [];
    try { marcadores = JSON.parse(datos.textContent); } catch (e) { marcadores = []; }
    var mapa = crearMapa(contenedor);
    var puntos = [];
    marcadores.forEach(function (m) {
      var color = m.rural ? COLOR_RURAL : COLOR_URBANO;
      L.circleMarker([m.lat, m.lng], {
        radius: 9, color: '#fff', weight: 2, fillColor: color, fillOpacity: 0.95
      }).addTo(mapa).bindPopup(popup(m));
      puntos.push([m.lat, m.lng]);
    });
    if (puntos.length) mapa.fitBounds(puntos, { padding: [40, 40], maxZoom: 13 });
    else mapa.setView([-32.95, -60.65], 8);
  }

  // Ficha: una sola ubicación. Si es aproximada, se dibuja un área en vez de un punto.
  var ficha = document.getElementById('mapa-ficha');
  if (ficha) {
    var lat = parseFloat(ficha.dataset.lat), lng = parseFloat(ficha.dataset.lng);
    if (isFinite(lat) && isFinite(lng)) {
      var m2 = crearMapa(ficha);
      if (ficha.dataset.aprox === '1') {
        // Hay que fijar una vista antes de agregar la capa: sin centro ni zoom Leaflet no puede proyectarla.
        m2.setView([lat, lng], 11);
        L.circle([lat, lng], { radius: 3000, color: COLOR_RURAL, weight: 2, fillOpacity: 0.15 }).addTo(m2);
      } else {
        L.circleMarker([lat, lng], { radius: 10, color: '#fff', weight: 3, fillColor: COLOR_URBANO, fillOpacity: 1 }).addTo(m2);
        m2.setView([lat, lng], 15);
      }
    }
  }
})();
