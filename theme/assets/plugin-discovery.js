/* "Find your sound": tone slider. Click a label, drag the thumb between stops, or use arrow keys.
   Choosing a tone hides the plugins that don't match (featured rows and the grid), counts what's left,
   and stops any playing video. "すべて" shows everything again. */
import { readJSON, reducedMotion } from './core.js';

class ToneRail {
  constructor(root, tones, onChange) {
    this.root = root; this.tones = tones; this.onChange = onChange; this.i = 0;
    const esc = (t) => String(t).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
    root.innerHTML = `
      <div class="rail__track" data-track>
        <div class="rail__ticks" aria-hidden="true">${tones.map((_, k) => (k ? '<i class="minor"></i><i class="minor"></i><i class="minor"></i>' : '') + '<i></i>').join('')}</div>
        <div class="rail__fill" aria-hidden="true"></div>
        <span class="rail__thumb" aria-hidden="true"></span>
      </div>
      <div class="rail__labels" role="radiogroup" aria-label="${esc(root.closest('.tone')?.querySelector('b')?.textContent || '')}">
        ${tones.map((t, k) => `<button type="button" role="radio" aria-checked="${k === 0}" tabindex="${k === 0 ? 0 : -1}" data-i="${k}"><span>${esc(t.label)}</span></button>`).join('')}
      </div>`;
    this.track = root.querySelector('[data-track]');
    this.thumb = root.querySelector('.rail__thumb');
    this.fill = root.querySelector('.rail__fill');
    this.btns = [...root.querySelectorAll('[role="radio"]')];
    this.place(0);
    this.bind();
  }
  pct(i) { return (i / (this.tones.length - 1)) * 100; }
  place(i, raw) { const p = raw ?? this.pct(i); this.thumb.style.left = `${p}%`; this.fill.style.width = `${p}%`; }
  set(i, focus) {
    i = Math.max(0, Math.min(this.tones.length - 1, i));
    const changed = i !== this.i;
    this.i = i; this.place(i);
    this.btns.forEach((b, k) => { b.setAttribute('aria-checked', String(k === i)); b.tabIndex = k === i ? 0 : -1; });
    if (focus) this.btns[i].focus();
    if (changed) this.onChange(this.tones[i]);
  }
  bind() {
    this.btns.forEach((b) => b.addEventListener('click', () => this.set(+b.dataset.i)));
    this.root.querySelector('[role="radiogroup"]').addEventListener('keydown', (e) => {
      const map = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 };
      if (e.key in map) { e.preventDefault(); this.set(this.i + map[e.key], true); }
      if (e.key === 'Home') { e.preventDefault(); this.set(0, true); }
      if (e.key === 'End') { e.preventDefault(); this.set(this.tones.length - 1, true); }
    });
    let id = null, sx = 0, sy = 0, mode = null;
    const toPct = (x) => { const r = this.track.getBoundingClientRect(); return Math.max(0, Math.min(100, ((x - r.left) / r.width) * 100)); };
    const nearest = (p) => Math.round((p / 100) * (this.tones.length - 1));
    this.track.addEventListener('pointerdown', (e) => { id = e.pointerId; sx = e.clientX; sy = e.clientY; mode = 'pending'; });
    this.track.addEventListener('pointermove', (e) => {
      if (e.pointerId !== id) return;
      if (mode === 'pending') {
        const dx = Math.abs(e.clientX - sx), dy = Math.abs(e.clientY - sy);
        if (dx > 4 && dx > dy) { mode = 'drag'; this.track.setPointerCapture(id); this.root.classList.add('is-dragging'); }
        else if (dy > 8) { mode = null; id = null; return; } else return;
      }
      const p = toPct(e.clientX);
      this.place(0, p);
      const n = nearest(p);
      this.btns.forEach((b, k) => b.setAttribute('aria-checked', String(k === n)));
    });
    this.track.addEventListener('pointerup', (e) => {
      if (e.pointerId !== id) return;
      this.root.classList.remove('is-dragging'); id = null; mode = null;
      this.set(nearest(toPct(e.clientX)));
      this.place(this.i);
    });
    this.track.addEventListener('pointercancel', () => { this.root.classList.remove('is-dragging'); id = null; mode = null; this.place(this.i); });
  }
}

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

  const apply = (tone) => {
    const id = tone.id;
    root.querySelectorAll('.nd-yt iframe').forEach((f) => { f.parentElement.classList.remove('is-playing'); f.remove(); });
    const test = (el) => id === 'all' || (el.dataset.tones || '').split(/[\s,]+/).includes(id);
    let n = 0, nMini = 0;
    rows.forEach((r) => { const m = test(r); n += m; r.hidden = !m; r.classList.add('is-in'); });
    minis.forEach((c) => { const m = test(c); n += m; nMini += m; c.hidden = !m; });
    rows.filter((r) => !r.hidden).forEach((r, k) => r.classList.toggle('is-flip', k % 2 === 1));
    if (moreHead) moreHead.hidden = !nMini;
    if (empty) empty.hidden = n > 0;
    count.textContent = id === 'all' ? fmt(cfg.countAll, total) : fmt(cfg.countSome, n);
  };
  rows.forEach((r, k) => r.classList.toggle('is-flip', k % 2 === 1));
  new ToneRail(bar, cfg.tones, apply);

  // 14日間無料体験: open this plugin's download card
  const dlg = root.querySelector('[data-trial-dialog]');
  root.querySelectorAll('[data-trial-open]').forEach((b) => b.addEventListener('click', () => {
    const tpl = document.getElementById(b.dataset.trialOpen);
    if (!dlg || !tpl) return;
    dlg.querySelector('[data-trial-body]').replaceChildren(tpl.content.cloneNode(true));
    dlg.showModal();
  }));
  count.textContent = fmt(cfg.countAll, total);
});
