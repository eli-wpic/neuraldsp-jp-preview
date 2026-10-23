/* Two-question chooser: highlights the model whose "recommend for" list contains <priority>_<plugins>. */
document.querySelectorAll('[data-compare]').forEach((root) => {
  const form = root.querySelector('[data-chooser]');
  const cols = [...root.querySelectorAll('.compare__col')];
  const out = root.querySelector('[data-chooser-out]');
  form?.addEventListener('change', () => {
    const f = new FormData(form);
    const plugins = f.get('plugins'), priority = f.get('priority');
    const key = plugins && priority ? `${priority}_${plugins}` : null;
    const hit = key ? cols.find((c) => (c.dataset.rec || '').split(',').map((s) => s.trim()).includes(key)) : null;
    cols.forEach((c) => c.classList.toggle('is-rec', c === hit));
    out.textContent = hit ? `${out.dataset.prefix}${hit.dataset.name}` : '';
  });
});
