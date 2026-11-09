/* "Find your sound": genre tabs (Progressive / ACG / Versatile / Old school / Bass). Choosing a tab shows only the
   plugins in that genre (featured rows and the grid), counts them, and stops any playing video. */
import { readJSON, reducedMotion } from './core.js';

function hoverTilt(frame) {
  if (!frame || reducedMotion() || !matchMedia('(hover: hover) and (pointer: fine)').matches) return;
  frame.addEventListener('pointermove', (e) => {
    const r = frame.getBoundingClientRect();
    const x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
    frame.style.transform = `perspective(1000px) rotateY(${x * 3}deg) rotateX(${-y * 3}deg)`;
  });
  frame.addEventListener('pointerleave', () => { frame.style.transform = ''; });
}

document.querySelectorAll('[data-plugins]').forEach((root) => {
  const cfg = readJSON(root.querySelector('[data-tones]'));
  const bar = root.querySelector('[data-tone-filter]');
  if (!cfg || !bar) return;
  const rows = [...root.querySelectorAll('.plugin-row')];
  const minis = [...root.querySelectorAll('.mini-card')];
  const count = root.querySelector('[data-tone-count]');
  const empty = root.querySelector('[data-tone-empty]');
  const moreHead = root.querySelector('.more-plugins');
  const total = rows.length + minis.length;
  const fmt = (t, n) => t.replace('{n}', n).replace('{total}', total);
  rows.forEach((r) => hoverTilt(r.querySelector('.plugin-media__frame')));

  const esc = (t) => String(t).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  bar.innerHTML = cfg.tones.map((t, k) => `<button type="button" role="tab" aria-selected="${k === 0}" tabindex="${k === 0 ? 0 : -1}" data-tone="${esc(t.id)}">${esc(t.label)}</button>`).join('');
  const tabs = [...bar.querySelectorAll('[role="tab"]')];
  const ink = document.createElement('i'); ink.className = 'tone__ink'; bar.appendChild(ink);
  const moveInk = (t) => { ink.style.width = `${t.offsetWidth}px`; ink.style.transform = `translateX(${t.offsetLeft}px)`; };

  const apply = (id) => {
    root.querySelectorAll('.nd-yt iframe').forEach((f) => { f.parentElement.classList.remove('is-playing'); f.remove(); });
    const test = (el) => id === 'all' || (el.dataset.tones || '').split(/[\s,]+/).includes(id);
    let n = 0, nMini = 0;
    rows.forEach((r) => { const m = test(r); n += m; r.hidden = !m; r.classList.add('is-in'); });
    minis.forEach((c) => { const m = test(c); n += m; nMini += m; c.hidden = !m; });
    rows.filter((r) => !r.hidden).forEach((r, k) => r.classList.toggle('is-flip', k % 2 === 1));
    if (moreHead) moreHead.hidden = !nMini;
    if (empty) empty.hidden = n > 0;
    tabs.forEach((t) => { const on = t.dataset.tone === id; t.setAttribute('aria-selected', on); t.tabIndex = on ? 0 : -1; if (on) moveInk(t); });
    // the matching plugins rise in one after another
    if (!reducedMotion()) rows.filter((r) => !r.hidden).forEach((r, k) => r.animate([{ opacity: 0, transform: 'translateY(24px)' }, { opacity: 1, transform: 'none' }], { duration: 480, delay: Math.min(k, 5) * 70, easing: 'cubic-bezier(0.22, 1, 0.36, 1)', fill: 'backwards' }));
    count.textContent = id === 'all' ? fmt(cfg.countAll, total) : fmt(cfg.countSome, n);
  };
  tabs.forEach((t, i) => {
    t.addEventListener('click', () => apply(t.dataset.tone));
    t.addEventListener('keydown', (e) => { const k = { ArrowRight: 1, ArrowLeft: -1 }[e.key]; if (k) { e.preventDefault(); const nx = tabs[(i + k + tabs.length) % tabs.length]; nx.focus(); apply(nx.dataset.tone); } });
  });
  rows.forEach((r, k) => r.classList.toggle('is-flip', k % 2 === 1));
  count.textContent = fmt(cfg.countAll, total);
  requestAnimationFrame(() => moveInk(tabs[0])); addEventListener('resize', () => moveInk(tabs.find((t) => t.getAttribute('aria-selected') === 'true') || tabs[0]));

  // 14日間無料体験: open this plugin's download card
  const dlg = root.querySelector('[data-trial-dialog]');
  root.querySelectorAll('[data-trial-open]').forEach((b) => b.addEventListener('click', () => {
    const tpl = document.getElementById(b.dataset.trialOpen);
    if (!dlg || !tpl) return;
    dlg.querySelector('[data-trial-body]').replaceChildren(tpl.content.cloneNode(true));
    dlg.showModal();
  }));
});
