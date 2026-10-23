/* Product page: 3D/photo media, description toggle, variant options, multi-plugin picker, accessories,
   live total, add to cart (all items in one /cart/add.js call), buy now (→ checkout), sticky bar.

   Plugins: when "add-on" products are set up (data-multi="true") customers can pick several plugins and the cart
   gets hardware + one add-on per plugin. Otherwise the store's bundle products are used: one plugin per order. */
import { cartAdd, money } from './core.js';

const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

/* ---------- photos: direction-aware glide with depth, like the 3D camera moves ---------- */
function initGallery(root) {
  const g = $('[data-gallery]', root);
  if (!g) return;
  const slides = $$('.gallery__slide', g);
  const thumbs = $$('[data-thumb]', g);
  const main = $('.gallery__main', g);
  let i = 0;
  const show = (n) => {
    if (!slides.length) return;
    n = (n + slides.length) % slides.length;
    if (n === i) return;
    const dir = n > i ? 1 : -1;
    const from = slides[i], to = slides[n];
    i = n;
    thumbs.forEach((t, k) => t.setAttribute('aria-current', String(k === i)));
    from.querySelectorAll('video').forEach((v) => v.pause());
    slides.forEach((sl) => sl.getAnimations().forEach((a) => a.finish()));
    from.classList.remove('is-active');
    to.classList.add('is-active');
    if (reduce) return;
    from.animate([{ opacity: 1, transform: 'none' }, { opacity: 0, transform: `translateX(${-dir * 9}%) scale(0.96)` }], { duration: 420, easing: 'cubic-bezier(0.65, 0, 0.35, 1)' });
    to.animate([{ opacity: 0, transform: `translateX(${dir * 9}%) scale(0.96)` }, { opacity: 1, transform: 'none' }], { duration: 520, easing: 'cubic-bezier(0.22, 1, 0.36, 1)', delay: 60, fill: 'backwards' });
  };
  thumbs.forEach((t) => t.addEventListener('click', () => show(+t.dataset.thumb)));
  $('[data-gallery-prev]', g)?.addEventListener('click', () => show(i - 1));
  $('[data-gallery-next]', g)?.addEventListener('click', () => show(i + 1));
  main?.addEventListener('keydown', (e) => { if (e.key === 'ArrowRight') show(i + 1); if (e.key === 'ArrowLeft') show(i - 1); });
  let sx = 0, sy = 0, id = null;
  main?.addEventListener('pointerdown', (e) => { if (e.target.closest('button,video')) return; sx = e.clientX; sy = e.clientY; id = e.pointerId; });
  main?.addEventListener('pointerup', (e) => {
    if (e.pointerId !== id) return;
    id = null;
    const dx = e.clientX - sx, dy = e.clientY - sy;
    if (Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy) * 1.2) show(i + (dx < 0 ? 1 : -1));
  });

  // 写真 tab on 3D product pages: photos open over the 3D stage; any 3D view button closes them
  const photosBtn = $('.nd-viewer__btn--photos', root);
  const setPhotos = (open) => {
    if (open) root.dispatchEvent(new CustomEvent('nd:media', { detail: 'photos' }));
    g.hidden = !open;
    $('[data-pdp-media]', root)?.classList.toggle('is-photos', open);
    if (open) $$('[data-view]', root).forEach((b) => b.setAttribute('aria-pressed', 'false'));
    $$('[data-photos-toggle]', root).forEach((x) => x.setAttribute('aria-expanded', String(open)));
    photosBtn?.setAttribute('aria-pressed', String(open));
    if (open) main?.focus();
  };
  $$('[data-photos-toggle]', root).forEach((b) => b.addEventListener('click', () => setPhotos(g.hidden)));
  if (g.classList.contains('gallery--overlay')) {
    $$('[data-view]', root).forEach((b) => b.addEventListener('click', () => setPhotos(false)));
    root.addEventListener('nd:media', (e) => { if (e.detail !== 'photos' && !g.hidden) setPhotos(false); });
  }
}

/* フル動画: the YouTube film takes the 3D stage's place (like a canvas turning into the full video);
   any view button or 写真 swaps back and stops it */
function initFilm(root) {
  const btn = $('[data-film]', root);
  const stage = $('[data-film-stage]', root);
  if (!btn || !stage) return;
  const media = $('[data-pdp-media]', root);
  const set = (open) => {
    if (open) root.dispatchEvent(new CustomEvent('nd:media', { detail: 'film' }));
    btn.setAttribute('aria-pressed', String(open));
    media.classList.toggle('is-film', open);
    stage.hidden = !open;
    if (open) {
      $$('[data-view]', root).forEach((b) => b.setAttribute('aria-pressed', 'false'));
      stage.innerHTML = `<iframe src="https://www.youtube-nocookie.com/embed/${btn.dataset.film}?autoplay=1&rel=0&hl=ja&playsinline=1" title="${btn.textContent.trim()}" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen></iframe>`;
    } else stage.innerHTML = '';
  };
  btn.addEventListener('click', () => set(btn.getAttribute('aria-pressed') !== 'true'));
  $$('[data-view]', root).forEach((b) => b.addEventListener('click', () => set(false)));
  root.addEventListener('nd:media', (e) => { if (e.detail !== 'film' && btn.getAttribute('aria-pressed') === 'true') set(false); });
}

function initCollapse(root) {
  const box = $('[data-collapsible]', root);
  if (!box) return;
  const inner = $('.buy__desc-inner', box);
  const btn = $('[data-collapse-toggle]', box);
  requestAnimationFrame(() => { if (inner.scrollHeight <= inner.clientHeight + 4) { btn.hidden = true; box.classList.add('is-open'); } });
  btn.addEventListener('click', () => {
    const open = box.classList.toggle('is-open');
    btn.textContent = open ? btn.dataset.less : btn.dataset.more;
  });
}

function init(root) {
  const data = JSON.parse($('[data-product-json]', root).textContent);
  const S = data.strings;
  const state = {
    variant: data.variants.find((v) => String(v.id) === $('[data-variant-input]', root).value) || data.variants[0],
    plugs: [], acc: new Set(), qty: 1,
  };

  initGallery(root);
  initFilm(root);
  initCollapse(root);

  /* variant options */
  $$('[data-option]', root).forEach((sel) => sel.addEventListener('change', () => {
    const chosen = $$('[data-option]', root).map((x) => x.value);
    const v = data.variants.find((vv) => vv.options.every((o, k) => o === chosen[k]));
    if (v) { state.variant = v; const u = new URL(location.href); u.searchParams.set('variant', v.id); history.replaceState(null, '', u); render(); }
  }));

  /* plugins */
  const plugBox = $('[data-plugs]', root);
  const plugs = plugBox ? $$('[data-plug]', plugBox) : [];
  const multi = plugBox?.dataset.multi === 'true';
  const plugCount = $('[data-plug-count]', root);
  let warnTimer;
  plugs.forEach((cb) => cb.addEventListener('change', () => {
    if (!multi && cb.checked && plugs.some((o) => o !== cb && o.checked)) {
      plugs.forEach((o) => { if (o !== cb) o.checked = false; });
      plugCount.textContent = S.oneOnly;
      plugCount.classList.add('is-warn');
      clearTimeout(warnTimer);
      warnTimer = setTimeout(() => { plugCount.classList.remove('is-warn'); render(); }, 2200);
    }
    state.plugs = plugs.filter((o) => o.checked);
    render();
  }));
  // the list shows 6 plugins until "show all" (or a preselected plugin further down) opens it
  const plugMore = $('[data-plugs-more]', root);
  const openPlugs = (open) => {
    plugBox?.classList.toggle('is-open', open);
    if (plugMore) { plugMore.dataset.more ??= plugMore.textContent; plugMore.textContent = open ? plugMore.dataset.less : plugMore.dataset.more; }
  };
  plugMore?.addEventListener('click', () => openPlugs(!plugBox.classList.contains('is-open')));
  const wanted = new URLSearchParams(location.search).get('plugin');
  if (wanted) {
    wanted.split(',').forEach((w) => {
      const hit = plugs.find((o) => o.value === w || o.value.endsWith('-' + w) || o.dataset.short.toLowerCase().includes(w.toLowerCase()));
      if (hit && !hit.disabled && (multi || !plugs.some((o) => o.checked))) hit.checked = true;
    });
    state.plugs = plugs.filter((o) => o.checked);
    if (plugs.slice(3).some((o) => o.checked)) openPlugs(true);
  }

  /* accessories */
  $$('[data-acc] input', root).forEach((cb) => cb.addEventListener('change', () => { cb.checked ? state.acc.add(cb) : state.acc.delete(cb); render(); }));

  /* quantity */
  $$('[data-qty]', root).forEach((q) => q.addEventListener('click', (e) => {
    const b = e.target.closest('button');
    if (!b) return;
    state.qty = Math.max(1, Math.min(10, state.qty + (b.dataset.step === '+' ? 1 : -1)));
    render();
  }));

  /* purchase */
  const accItems = () => [...state.acc].map((cb) => ({ id: +cb.value, quantity: 1 }));
  const items = () => {
    const p = state.plugs;
    if (!p.length) return [{ id: state.variant.id, quantity: state.qty }, ...accItems()];
    if (!multi) return [{ id: +p[0].dataset.bundleVariant, quantity: state.qty }, ...accItems()];
    return [{ id: state.variant.id, quantity: state.qty }, ...p.map((cb) => ({ id: +cb.dataset.addonVariant, quantity: state.qty })), ...accItems()];
  };
  const err = $('[data-error]', root);
  const go = async (checkout, btn) => {
    btn.disabled = true;
    err.hidden = true;
    try {
      await cartAdd(items());
      location.href = checkout ? '/checkout' : window.ndTheme.routes.cart;
    } catch (e) {
      err.textContent = e.message || window.ndTheme.strings.addError;
      err.hidden = false;
      btn.disabled = false;
    }
  };
  $('[data-buy-form]', root).addEventListener('submit', (e) => { e.preventDefault(); go(false, $('[data-add]', root)); });
  $$('[data-buy-now]', root).forEach((b) => b.addEventListener('click', () => go(true, b)));

  function render() {
    const p = state.plugs;
    const plugSum = p.reduce((t, cb) => t + +cb.dataset.price, 0);
    const unit = !p.length ? state.variant.price : (multi ? state.variant.price + plugSum : +p[0].dataset.bundlePrice);
    const accSum = [...state.acc].reduce((t, cb) => t + +cb.dataset.accPrice, 0);
    const total = unit * state.qty + accSum;
    const names = p.map((cb) => cb.dataset.short);

    $('[data-unit-price]', root).innerHTML = `<span class="yen">${money(unit)}</span>`;
    $('[data-unit-note]', root).textContent = p.length ? S.setTaxLabel : S.taxLabel;
    $$('[data-total]', root).forEach((el) => (el.textContent = money(total)));
    $('[data-total-break]', root).textContent = [
      `${S.base} ${money(state.variant.price)}${state.qty > 1 ? ` × ${state.qty}` : ''}`,
      ...p.map((cb) => `${cb.dataset.short} ${money(+cb.dataset.price)}${state.qty > 1 ? ` × ${state.qty}` : ''}`),
      ...[...state.acc].map((cb) => `${cb.dataset.accName} ${money(+cb.dataset.accPrice)}`),
    ].join(' ＋ ');
    $$('[data-qty] output', root).forEach((o) => (o.textContent = state.qty));
    $('[data-sticky-title]', root).textContent = names.length ? `${data.title} + ${names.join(' + ')}` : data.title;
    $('[data-sticky-meta]', root).textContent = state.acc.size ? `${[...state.acc].map((cb) => cb.dataset.accName).join('・')} ${S.selected}` : S.noAccessories;
    if (plugCount && !plugCount.classList.contains('is-warn')) plugCount.textContent = names.length ? S.plugCount.replace('{n}', names.length) : S.plugNone;
    $('[data-variant-input]', root).value = !p.length || multi ? state.variant.id : p[0].dataset.bundleVariant;
    const avail = state.variant.available && p.every((cb) => !cb.disabled);
    $$('[data-add], [data-buy-now]', root).forEach((x) => (x.disabled = !avail));
    const u = new URL(location.href);
    if (p.length) u.searchParams.set('plugin', p.map((cb) => cb.value).join(','));
    else u.searchParams.delete('plugin');
    history.replaceState(null, '', u);
  }
  render();

  /* sticky bar when the main CTA leaves the viewport */
  const bar = $('[data-sticky]', root);
  const cta = $('.buy__cta', root);
  if (bar && cta) new IntersectionObserver(([en]) => {
    const show = !en.isIntersecting && en.boundingClientRect.top < 0;
    bar.classList.toggle('is-in', show);
    bar.inert = !show;
  }).observe(cta);
}

document.querySelectorAll('[data-product-form]').forEach(init);
