/* Shared theme behaviour: cart API, money, header, dialogs, lazy YouTube, buy-now buttons,
   newsletter tagging, trial form, section reveals. */

export const reducedMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const yenFmt = new Intl.NumberFormat('ja-JP');
/** cents (Shopify) → "¥279,000" */
export const money = (cents) => `¥${yenFmt.format(Math.round(cents / 100))}`;

export async function cartAdd(items) {
  const res = await fetch(window.ndTheme.routes.cartAdd, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({ items }),
  });
  const json = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(json.description || json.message || window.ndTheme.strings.addError);
  refreshCount();
  return json;
}

async function refreshCount() {
  try {
    const cart = await fetch('/cart.js').then((r) => r.json());
    document.querySelectorAll('[data-cart-count]').forEach((el) => { el.textContent = cart.item_count; el.hidden = !cart.item_count; });
  } catch { /* non-critical */ }
}

/* Header ------------------------------------------------------------ */
function initHeader() {
  document.querySelectorAll('[data-mega-trigger]').forEach((trigger) => {
    const mega = document.getElementById(trigger.getAttribute('aria-controls'));
    const item = trigger.closest('.nav__item');
    let t;
    const open = (v) => {
      clearTimeout(t);
      if (v) document.querySelectorAll('[data-mega-trigger][aria-expanded="true"]').forEach((o) => { if (o !== trigger) { o.setAttribute('aria-expanded', 'false'); document.getElementById(o.getAttribute('aria-controls'))?.classList.remove('is-open'); } });
      trigger.setAttribute('aria-expanded', String(v));
      mega.classList.toggle('is-open', v);
    };
    trigger.addEventListener('click', () => open(trigger.getAttribute('aria-expanded') !== 'true'));
    if (matchMedia('(hover: hover)').matches) {
      item.addEventListener('pointerenter', () => open(true));
      item.addEventListener('pointerleave', () => (t = setTimeout(() => open(false), 140)));
    }
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && mega.classList.contains('is-open')) { open(false); trigger.focus(); } });
    document.addEventListener('click', (e) => { if (!item.contains(e.target)) open(false); });
  });
  const toggle = document.querySelector('[data-menu-toggle]');
  const mobile = document.getElementById('MobileNav');
  if (toggle && mobile) {
    const set = (v) => { toggle.setAttribute('aria-expanded', String(v)); mobile.classList.toggle('is-open', v); document.body.style.overflow = v ? 'hidden' : ''; };
    toggle.addEventListener('click', () => set(toggle.getAttribute('aria-expanded') !== 'true'));
    mobile.addEventListener('click', (e) => { if (e.target.closest('a')) set(false); });
  }
}

/* Dialogs (spec sheets, newsletter pop-up, trial) -------------------- */
function initDialogs() {
  document.addEventListener('click', (e) => {
    const opener = e.target.closest('[data-dialog-open]');
    if (opener) {
      const d = document.getElementById(opener.dataset.dialogOpen);
      if (d?.showModal) { e.preventDefault(); d.showModal(); d.querySelector('input,button:not([data-dialog-close])')?.focus(); }
      return;
    }
    if (e.target.closest('.trial-cta')) { e.preventDefault(); document.getElementById('TrialDialog')?.showModal(); return; }
    if (e.target.closest('[data-dialog-close]')) e.target.closest('dialog')?.close();
    else if (e.target.tagName === 'DIALOG') e.target.close(); // backdrop click
  });
}

/* Lazy YouTube ------------------------------------------------------- */
function initYouTube() {
  document.addEventListener('click', (e) => {
    const box = e.target.closest('.nd-yt');
    if (!box || box.querySelector('iframe')) return;
    document.querySelectorAll('.nd-yt iframe').forEach((f) => { f.parentElement.classList.remove('is-playing'); f.remove(); });
    document.querySelectorAll('audio, video:not([autoplay])').forEach((m) => m.pause());
    const f = document.createElement('iframe');
    f.src = `https://www.youtube-nocookie.com/embed/${box.dataset.yt}?autoplay=1&rel=0&hl=ja`;
    f.allow = 'autoplay; encrypted-media; picture-in-picture; fullscreen';
    f.allowFullscreen = true;
    f.title = box.querySelector('img')?.alt || 'YouTube';
    box.classList.add('is-playing');
    box.appendChild(f);
  });
}

/* Buy-now buttons outside the product form (heroes) ------------------ */
function initBuyNow() {
  document.addEventListener('click', async (e) => {
    const b = e.target.closest('[data-buy-now]');
    if (!b || b.closest('[data-product-form]') || !b.dataset.buyNow) return;
    b.disabled = true;
    try { await cartAdd([{ id: +b.dataset.buyNow, quantity: 1 }]); location.href = '/checkout'; }
    catch (err) { b.disabled = false; alert(err.message); }
  });
}

/* Newsletter: birthday / gender → customer tags (same scheme as the live store) */
function initNewsletter() {
  document.querySelectorAll('[data-nd-newsletter]').forEach((form) => {
    form.addEventListener('submit', () => {
      const tags = form.querySelector('[data-nl-tags]');
      const base = (tags.value || '').split(',').map((s) => s.trim()).filter(Boolean);
      const g = form.querySelector('[data-nl-gender]:checked');
      const b = form.querySelector('[data-nl-birthday]');
      if (g) base.push(`gender_${g.value}`);
      if (b && b.value) base.push(`birthday_${b.value}`);
      tags.value = [...new Set(base)].join(', ');
    });
  });
  const story = document.querySelector('[data-qc3d]');
  if (story && 'IntersectionObserver' in window) {
    new IntersectionObserver(([e]) => document.body.classList.toggle('in-3d', e.isIntersecting)).observe(story);
  }
  // re-open the pop-up after a successful/failed post so the visitor sees the message
  if (/customer_posted=true|form_type=customer/.test(location.search + location.hash)) {
    document.querySelector('.nd-nl--popup')?.showModal?.();
  }
}

/* Trial form: open the download page in a new tab -------------------- */
function initTrial() {
  document.querySelectorAll('[data-trial-form]').forEach((f) => f.addEventListener('submit', (e) => {
    e.preventDefault();
    window.open(f.action, '_blank', 'noopener');
    f.closest('dialog')?.close();
  }));
}

/* Hero film: the YouTube film takes over the hero (like a canvas swapping to the full video) */
function initHeroFilm() {
  document.querySelectorAll('[data-hero-film]').forEach((btn) => {
    const hero = btn.closest('[data-hero]');
    const stage = hero?.querySelector('[data-hero-film-stage]');
    if (!stage) return;
    const label = btn.textContent;
    btn.addEventListener('click', () => {
      const open = btn.getAttribute('aria-pressed') !== 'true';
      btn.setAttribute('aria-pressed', String(open));
      btn.textContent = open ? btn.dataset.close : label;
      hero.classList.toggle('is-film', open);
      stage.hidden = !open;
      hero.querySelectorAll('.nd-hero__bg video').forEach((v) => (open ? v.pause() : v.play().catch(() => {})));
      stage.innerHTML = open ? `<iframe src="https://www.youtube-nocookie.com/embed/${btn.dataset.heroFilm}?autoplay=1&rel=0&hl=ja&playsinline=1" title="${label.trim()}" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe>` : '';
    });
  });
}

/* Links that open a sibling page with the same layout (e.g. Quad Cortex ↔ mini on a plugin page)
   keep the visitor at the same spot instead of jumping back to the top */
function initKeepPlace() {
  document.addEventListener('click', (e) => {
    const a = e.target.closest('a[data-keep-place]');
    if (!a || e.metaKey || e.ctrlKey || e.shiftKey) return;
    try { sessionStorage.setItem('nd-keep-place', JSON.stringify({ y: scrollY, to: new URL(a.href, location.href).pathname, t: Date.now() })); } catch { /* storage blocked */ }
  });
  let saved = null;
  try { saved = JSON.parse(sessionStorage.getItem('nd-keep-place') || 'null'); sessionStorage.removeItem('nd-keep-place'); } catch { /* ignore */ }
  if (saved && saved.to === location.pathname && Date.now() - saved.t < 15000) {
    if ('scrollRestoration' in history) history.scrollRestoration = 'manual';
    const go = () => scrollTo({ top: saved.y, behavior: 'instant' });
    go(); requestAnimationFrame(go); addEventListener('load', go, { once: true });
  }
}

/* Accordions: every <details> (FAQs, specs, mobile menu) opens and closes with the same height glide */
function initAccordions(root = document) {
  root.querySelectorAll('details:not([data-acc-ready])').forEach((d) => {
    const sum = d.querySelector(':scope > summary');
    if (!sum) return;
    d.dataset.accReady = '';
    let anim = null;
    sum.addEventListener('click', (e) => {
      if (reducedMotion()) return;
      e.preventDefault();
      const start = d.offsetHeight;
      const opening = !d.open || d.classList.contains('is-closing');
      anim?.cancel();
      d.style.overflow = 'hidden';
      if (opening) { d.open = true; d.classList.remove('is-closing'); }
      else d.classList.add('is-closing');
      const end = opening ? d.scrollHeight : sum.offsetHeight + parseFloat(getComputedStyle(d).borderBottomWidth || 0);
      anim = d.animate({ height: [`${start}px`, `${end}px`] }, { duration: 320, easing: 'cubic-bezier(0.22, 1, 0.36, 1)' });
      anim.onfinish = () => { anim = null; d.style.overflow = ''; if (!opening) { d.open = false; d.classList.remove('is-closing'); } };
    });
  });
}

/* Reveals ------------------------------------------------------------
   Every section below the first fades up once as it enters the viewport (same timing everywhere). */
function tagSections(root = document) {
  const secs = [...root.querySelectorAll('main .shopify-section, #MainContent > .shopify-section')];
  secs.forEach((s, i) => {
    if (i === 0 && root === document) return; // the hero is already on screen
    const el = s.firstElementChild;
    if (el && !el.matches('[data-qc3d], .pdp-wrap, script, style') && !el.classList.contains('reveal')) el.classList.add('reveal');
  });
}
export function observeReveal(root = document) {
  const els = root.querySelectorAll('.reveal:not(.is-in)');
  if (reducedMotion() || !('IntersectionObserver' in window)) { els.forEach((el) => el.classList.add('is-in')); return; }
  const io = new IntersectionObserver((entries) => entries.forEach((en) => { if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); } }), { rootMargin: '0px 0px -8% 0px' });
  els.forEach((el) => io.observe(el));
}

export function readJSON(el) {
  try { return JSON.parse(el.textContent); } catch { return null; }
}

initHeader();
initDialogs();
initYouTube();
initBuyNow();
initNewsletter();
initTrial();
initKeepPlace();
initAccordions();
initHeroFilm();
tagSections();
observeReveal();
document.addEventListener('shopify:section:load', (e) => { initAccordions(e.target); observeReveal(e.target); });
