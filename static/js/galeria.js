/* Galería de la ficha: miniaturas + visor a pantalla completa con teclado. */
(function () {
  var principal = document.getElementById('galeria-principal');
  if (!principal) return;
  var fotos = JSON.parse(document.getElementById('datos-fotos').textContent || '[]');
  if (!fotos.length) return;

  var img = principal.querySelector('img');
  var contador = document.getElementById('galeria-contador');
  var minis = Array.prototype.slice.call(document.querySelectorAll('.miniaturas button'));
  var visor = document.getElementById('visor');
  var imgVisor = visor.querySelector('img');
  var actual = 0, ultimoFoco = null;

  function ir(i) {
    actual = (i + fotos.length) % fotos.length;
    img.src = fotos[actual];
    imgVisor.src = fotos[actual];
    if (contador) contador.textContent = (actual + 1) + ' / ' + fotos.length;
    minis.forEach(function (b, n) { b.setAttribute('aria-current', n === actual ? 'true' : 'false'); });
  }
  function abrir() {
    ultimoFoco = document.activeElement;
    visor.classList.add('abierto');
    document.body.style.overflow = 'hidden';
    visor.querySelector('.cerrar').focus();
  }
  function cerrar() {
    visor.classList.remove('abierto');
    document.body.style.overflow = '';
    if (ultimoFoco) ultimoFoco.focus();
  }

  principal.addEventListener('click', abrir);
  minis.forEach(function (b, n) { b.addEventListener('click', function () { ir(n); }); });
  visor.querySelector('.cerrar').addEventListener('click', cerrar);
  visor.querySelector('.ant').addEventListener('click', function () { ir(actual - 1); });
  visor.querySelector('.sig').addEventListener('click', function () { ir(actual + 1); });
  visor.addEventListener('click', function (e) { if (e.target === visor) cerrar(); });
  document.addEventListener('keydown', function (e) {
    if (!visor.classList.contains('abierto')) return;
    if (e.key === 'Escape') cerrar();
    else if (e.key === 'ArrowLeft') ir(actual - 1);
    else if (e.key === 'ArrowRight') ir(actual + 1);
  });
  ir(0);
})();
