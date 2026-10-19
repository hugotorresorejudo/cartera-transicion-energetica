// Etiqueta «inferido/editado» en la pestaña Avanzado y composición de ecuaciones con MathJax (copia local, sin red).
window.MathJax = {tex: {inlineMath: [['\\(', '\\)']], displayMath: [['\\[', '\\]']]}, svg: {fontCache: 'global'}, startup: {typeset: false}};
document.addEventListener('input', function (e) {
  var fila = e.target.closest && e.target.closest('.adv-fila');
  if (!fila) return;
  var c = parseFloat(fila.getAttribute('data-central')), v = parseFloat(e.target.value);
  var chip = fila.querySelector('.chip');
  if (!chip || isNaN(v)) return;
  var ed = Math.abs(v - c) > 1e-9 * Math.max(1, Math.abs(c));
  chip.textContent = ed ? 'editado' : 'inferido';
  chip.classList.toggle('chip-editado', ed);
});
function tipografiar() {
  if (window.MathJax && MathJax.typesetPromise) {
    var nodos = document.querySelectorAll('.eq:not([data-ok])');
    if (nodos.length) { nodos.forEach(function (n) { n.setAttribute('data-ok', '1'); }); MathJax.typesetPromise(Array.from(nodos)); }
  }
}
new MutationObserver(tipografiar).observe(document.documentElement, {childList: true, subtree: true});
// Marca la entrada activa de la navegación.
Shiny.addCustomMessageHandler('activo', function (id) {
  document.querySelectorAll('.nav-item a').forEach(function (a) { a.classList.toggle('activo', a.id === id); });
});
