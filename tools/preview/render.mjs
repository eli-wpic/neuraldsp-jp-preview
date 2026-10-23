// Minimal local Shopify renderer for visual QA of the theme (not shipped).
// Renders JSON templates through liquidjs with real neuraldsp.jp product data.
import { Liquid } from 'liquidjs';
import fs from 'node:fs';
import path from 'node:path';

const THEME = process.argv[2];
const OUT = process.argv[3];
const DATA = path.join(path.dirname(new URL(import.meta.url).pathname), 'data');
const ja = JSON.parse(fs.readFileSync(path.join(THEME, 'locales/ja.json'), 'utf8'));

const stripComment = (s) => s.replace(/^\s*\/\*[\s\S]*?\*\/\s*/, '');
const readJSON = (p) => JSON.parse(stripComment(fs.readFileSync(p, 'utf8')));

/* ---------- data ---------- */
const products = {};
function mkImage(src, w = 1600, h = 1000, alt = '') { return src ? { src: src.startsWith('//') ? 'https:' + src : src, width: w, height: h, alt, __img: true } : null; }
function loadProduct(handle) {
  if (products[handle]) return products[handle];
  const f = path.join(DATA, handle + '.json');
  if (!fs.existsSync(f)) return null;
  const j = JSON.parse(fs.readFileSync(f, 'utf8'));
  const media = (j.media || []).map((m) => ({ media_type: m.media_type, alt: m.alt, preview_image: mkImage(m.preview_image?.src || m.src, m.width, m.height), src: m.src, __img: true, ...mkImage(m.preview_image?.src || m.src, m.width, m.height) }));
  const variants = j.variants.map((v) => ({ ...v, title: v.title, options: [v.option1, v.option2, v.option3].filter(Boolean) }));
  const p = {
    id: j.id, title: j.title, handle: j.handle, url: '/products/' + j.handle, price: j.price, available: j.available,
    description: j.description, media, featured_media: media[0] || null, variants,
    selected_or_first_available_variant: variants.find((v) => v.available) || variants[0],
    has_only_default_variant: variants.length === 1 && variants[0].title === 'Default Title',
    options_with_values: j.options.map((o, i) => ({ name: o.name, values: o.values, selected_value: variants[0].options[i] })),
    metafields: { custom: {} }, __product: true,
  };
  products[handle] = p;
  return p;
}
fs.readdirSync(DATA).filter((f) => f.endsWith('.json') && f !== 'collections.json').forEach((f) => loadProduct(f.replace('.json', '')));
const collList = JSON.parse(fs.readFileSync(path.join(DATA, 'collections.json'), 'utf8'));
const mkColl = (c) => { const ps = c.products.map(loadProduct).filter(Boolean); return { title: c.title, handle: c.handle, url: '/collections/' + c.handle, description: c.description, image: c.image ? mkImage(c.image) : null, products: ps, products_count: ps.length, all_products_count: ps.length, sort_options: [], sort_by: '', default_sort_by: 'manual' }; };
const collections = Object.fromEntries(collList.map((c) => [c.handle, mkColl(c)]));
collections.all = mkColl({ handle: 'all', title: 'すべての製品', description: '', products: Object.keys(products) });
const unesc = (t) => String(t || '').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&amp;/g, '&');
const atom = fs.readFileSync(path.join(DATA, 'news.atom'), 'utf8');
const articles = [...atom.matchAll(/<entry>[\s\S]*?<\/entry>/g)].map((m) => {
  const e = m[0];
  const content = unesc((e.match(/<content[^>]*>([\s\S]*?)<\/content>/) || [])[1]);
  const img = (content.match(/<img[^>]*src="([^"]+)"/) || [])[1];
  const live = (e.match(/<link[^>]*href="([^"]+)"/) || [])[1] || '';
  const handle = decodeURIComponent(live.split('/').pop());
  return { title: unesc((e.match(/<title>([\s\S]*?)<\/title>/) || [])[1]), handle, url: '/blogs/news/' + encodeURIComponent(handle), published_at: (e.match(/<published>([^<]+)/) || [])[1], author: unesc((e.match(/<name>([^<]+)/) || [])[1]), content, excerpt: '', image: img ? mkImage(img.startsWith('//') ? 'https:' + img : img) : null, tags: [] };
});
const blogs = { news: { title: 'Latest News', handle: 'news', url: '/blogs/news', articles, articles_count: articles.length } };

const P = (h) => ({ title: (loadProduct(h) || {}).title || h, url: '/products/' + h, type: 'product_link', object: loadProduct(h), links: [] });
const bundleLinks = (pre) => ['joh', 'mis', 'tim', 'rab', 'pet', 'goj', 'for', 'nol', 'par', 'pli', 'slo', 'cor'].map((s) => { const l = P(pre + s); l.title = (l.object?.title || '').replace(/^Quad Cortex( mini)? \+ /, ''); return l; });
const linklists = {
  'main-menu': { links: [
    P('nano-cortex'), P('quad-cortex'), P('quad-cortex-mini'),
    { title: 'Quad Cortex + Plugin', url: '/pages/quad-cortex-and-plugin-bundle', links: bundleLinks('quadcortex-plugin-bundle-') },
    { title: 'Quad Cortex mini + Plugin', url: '/pages/quad-cortex-mini-plugin', links: bundleLinks('quadcortex-mini-plugin-bundle-') },
    { title: 'Accessory', url: '/pages/accessory', links: [P('gig-case'), { ...P('quad-cortex-psu'), title: '電源アダプター' }] },
    { title: 'Cortex Cloud', url: '/pages/neuraldsp-account', links: [] },
  ] },
};

/* ---------- engine ---------- */
const engine = new Liquid({ root: [path.join(THEME, 'snippets')], extname: '.liquid', strictFilters: false, strictVariables: false, jsTruthy: false });
const yen = (c) => '¥' + Math.round(Number(c || 0) / 100).toLocaleString('ja-JP');
const kw = (args) => Object.fromEntries(args.filter(Array.isArray));
const imgSrc = (o, w) => {
  if (!o) return '';
  const s = typeof o === 'string' ? o : o.src || o.preview_image?.src || '';
  if (!s) return '';
  if (!/cdn\.shopify\.com|\/cdn\/shop\//.test(s)) return s; // only Shopify's CDN resizes
  return s + (s.includes('?') ? '&' : '?') + 'width=' + (w || 1200);
};
engine.registerFilter('asset_url', (n) => '/assets/' + n);
engine.registerFilter('stylesheet_tag', (u) => `<link rel="stylesheet" href="${u}">`);
engine.registerFilter('image_url', (o, ...a) => imgSrc(o, kw(a).width));
engine.registerFilter('image_tag', (u, ...a) => { const k = kw(a); return `<img src="${u}" alt="${(k.alt ?? '').toString().replace(/"/g, '&quot;')}" loading="${k.loading || 'lazy'}"${k.class ? ` class="${k.class}"` : ''}${k.width ? ` width="${k.width}"` : ''}${k.height ? ` height="${k.height}"` : ''}>`; });
engine.registerFilter('money', yen);
engine.registerFilter('money_without_trailing_zeros', yen);
engine.registerFilter('money_without_currency', (c) => Math.round(c / 100).toLocaleString('ja-JP'));
engine.registerFilter('t', (key, ...a) => {
  let v = key.split('.').reduce((o, k) => (o ? o[k] : undefined), ja) ?? key;
  const k = kw(a); for (const [n, val] of Object.entries(k)) v = String(v).replace(new RegExp(`{{\\s*${n}\\s*}}`, 'g'), val);
  return v;
});
engine.registerFilter('json', (v) => JSON.stringify(v ?? null, (k, val) => (k === 'object' ? undefined : val)));
engine.registerFilter('handleize', (s) => String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''));
engine.registerFilter('payment_type_svg_tag', (t) => `<svg viewBox="0 0 38 24" width="38" height="24"><rect width="38" height="24" rx="4" fill="#2a2e33"/><text x="19" y="15" font-size="7" fill="#aaa" text-anchor="middle">${t}</text></svg>`);
engine.registerFilter('default_errors', () => 'error');
engine.registerFilter('payment_button', () => '');
engine.registerFilter('video_tag', () => '<video></video>');
engine.registerFilter('external_video_tag', () => '');
engine.registerFilter('media_tag', () => '');
engine.registerFilter('format_address', () => '');
engine.registerFilter('newline_to_br', (s) => String(s ?? '').replace(/\n/g, '<br />'));

const passTag = (name, open, close) => engine.registerTag(name, {
  parse(token, remain) { this.args = token.args; this.tpl = []; const stream = this.liquid.parser.parseStream(remain).on(`tag:end${name}`, () => stream.stop()).on('template', (t) => this.tpl.push(t)).on('end', () => { throw new Error(`${name} not closed`); }); stream.start(); },
  * render(ctx, emitter) { emitter.write(open(this.args)); yield this.liquid.renderer.renderTemplates(this.tpl, ctx, emitter); emitter.write(close); },
});
passTag('form', (args) => { const c = (args.match(/class:\s*'([^']+)'/) || [])[1]; const id = (args.match(/id:\s*'([^']+)'/) || [])[1]; return `<form method="post" action="#"${c ? ` class="${c}"` : ''}${id ? ` id="${id}"` : ''}${/data-buy-form/.test(args) ? ' data-buy-form' : ''}${/data-nd-newsletter/.test(args) ? ' data-nd-newsletter' : ''}>`; }, '</form>');
engine.registerTag('paginate', {
  parse(token, remain) { this.tpl = []; const stream = this.liquid.parser.parseStream(remain).on('tag:endpaginate', () => stream.stop()).on('template', (t) => this.tpl.push(t)); stream.start(); },
  * render(ctx, emitter) { ctx.push({ paginate: { pages: 1, current_page: 1 } }); yield this.liquid.renderer.renderTemplates(this.tpl, ctx, emitter); ctx.pop(); },
});
engine.registerTag('schema', { parse(token, remain) { const stream = this.liquid.parser.parseStream(remain).on('tag:endschema', () => stream.stop()); stream.start(); }, render() { return ''; } });
engine.registerTag('sections', {
  parse(token) { this.name = token.args.replace(/['"]/g, '').trim(); },
  * render(ctx) { return renderGroup(this.name, ctx.getAll()); },
});

/* ---------- sections ---------- */
function schemaOf(src) { const m = src.match(/{%-?\s*schema\s*-?%}([\s\S]*?){%-?\s*endschema\s*-?%}/); return m ? JSON.parse(m[1]) : {}; }
function resolveSetting(def, val) {
  if (val === undefined) val = def?.default;
  if (!def) return val;
  if (def.type === 'product') return val ? loadProduct(val) : null;
  if (def.type === 'product_list') { const arr = (val || []).map(loadProduct).filter(Boolean); arr.count = arr.length; return arr; }
  if (def.type === 'collection') return val || '';
  if (def.type === 'image_picker') return null;
  return val ?? '';
}
function settingsFor(defs = [], vals = {}) {
  const out = {};
  for (const d of defs) if (d.id) out[d.id] = resolveSetting(d, vals[d.id]);
  for (const [k, v] of Object.entries(vals)) if (!(k in out)) out[k] = v;
  return out;
}
async function renderSection(id, conf, globals) {
  const file = path.join(THEME, 'sections', conf.type + '.liquid');
  let src = fs.readFileSync(file, 'utf8').replace(/{%-?\s*render block\s*-?%}/g, '');
  const schema = schemaOf(src);
  const settings = settingsFor(schema.settings, conf.settings || {});
  const blocks = (conf.block_order || Object.keys(conf.blocks || {})).map((bid) => {
    const b = conf.blocks[bid];
    const def = (schema.blocks || []).find((x) => x.type === b.type) || {};
    return { id: bid, type: b.type, settings: settingsFor(def.settings, b.settings || {}), shopify_attributes: '' };
  });
  if (process.env.MOCK_ADDONS && conf.type === 'main-product' && settings.bundles?.length && globals.product) {
    const base = globals.product.selected_or_first_available_variant.price;
    settings.addons = settings.bundles.map((b) => { const short = b.title.replace(globals.product.title + ' + ', ''); const v = b.selected_or_first_available_variant; return { title: short + '（追加プラグイン）', selected_or_first_available_variant: { ...v, id: v.id + 1, price: v.price - base } }; });
    settings.addons.count = settings.addons.length;
  }
  const section = { id, settings, blocks };
  try {
    const html = await engine.parseAndRender(src, { ...globals, section });
    return `<div id="shopify-section-${id}" class="shopify-section">${html}</div>`;
  } catch (e) {
    return `<pre style="color:#f66;padding:20px">SECTION ${conf.type} ERROR: ${e.message}</pre>`;
  }
}
async function renderGroup(name, globals) {
  const g = readJSON(path.join(THEME, 'sections', name + '.json'));
  let html = '';
  for (const id of g.order) html += await renderSection(id, g.sections[id], globals);
  return html;
}

async function renderPage(tplName, outFile, extra = {}) {
  const tpl = readJSON(path.join(THEME, 'templates', tplName + '.json'));
  const globals = {
    shop: { name: 'Neural DSP 日本公式オンラインストア', enabled_payment_types: ['visa', 'master', 'american_express', 'jcb', 'apple_pay', 'google_pay', 'shopify_pay'], customer_accounts_enabled: true, domain: 'neuraldsp.jp' },
    routes: { root_url: '/', cart_url: '/cart', cart_add_url: '/cart/add', search_url: '/search', account_url: '/account', all_products_collection_url: '/collections/all', account_register_url: '/account/register' },
    request: { host: 'localhost', locale: { iso_code: 'ja' }, page_type: tplName.split('.')[0] },
    cart: { item_count: 0, currency: { iso_code: 'JPY' } },
    localization: { available_countries: [], available_languages: [] },
    settings: {}, linklists, collections, blogs, all_products: products,
    template: { name: tplName.split('.')[0], suffix: tplName.split('.')[1] || '' },
    canonical_url: '/', page_title: extra.title || 'Neural DSP Japan', ...extra,
  };
  let main = '';
  for (const id of tpl.order) main += await renderSection(id, tpl.sections[id], globals);
  let layout = fs.readFileSync(path.join(THEME, 'layout/theme.liquid'), 'utf8').replace(/{%\s*render 'meta-tags'\s*%}/, '');
  layout = layout.replace('{{ content_for_header }}', '').replace('{{ content_for_layout }}', '%%MAIN%%');
  let html = await engine.parseAndRender(layout, globals);
  html = html.replace('%%MAIN%%', main);
  fs.mkdirSync(path.dirname(path.join(OUT, outFile)), { recursive: true });
  fs.writeFileSync(path.join(OUT, outFile), html);
  const errs = (html.match(/SECTION [\w-]+ ERROR: [^<]*/g) || []);
  console.log(outFile, html.length, errs.length ? errs : 'ok');
}

/* every page the live store has: products, pages, collections, blog + articles, and the system templates */
const INV = JSON.parse(fs.readFileSync(path.join(THEME, '..', 'site', 'live-content-inventory.json'), 'utf8'));
const hasTpl = (t) => fs.existsSync(path.join(THEME, 'templates', t + '.json'));
const tplFor = (url, base) => { const t = (INV[url]?.template || '').replace(/^(product|page|collection|blog|article)-/, '$1.'); return t && hasTpl(t) ? t : base; };
const cleanTitle = (t) => String(t || '').split('–')[0].replace(/\s+/g, ' ').trim();
const pages = [['index', 'index.html']];
for (const h of Object.keys(products)) pages.push([tplFor('/products/' + h, 'product'), `products/${h}.html`, { product: products[h], title: products[h].title }]);
for (const url of Object.keys(INV).filter((u) => u.startsWith('/pages/'))) {
  const v = INV[url], t = tplFor(url, 'page');
  const text = (v.sections || []).filter((x) => x.section === 'main').flatMap((x) => x.text || []);
  const content = t === 'page' ? text.slice(1).map((p) => `<p>${p}</p>`).join('') : '';
  pages.push([t, `${url.slice(1)}.html`, { page: { title: cleanTitle(v.title) || text[0] || url, content }, title: cleanTitle(v.title), form: {} }]);
}
pages.push(['list-collections', 'collections.html', { title: 'コレクション' }]);
for (const c of Object.values(collections)) pages.push(['collection', `collections/${c.handle}.html`, { collection: c, title: c.title }]);
pages.push(['blog', 'blogs/news.html', { blog: blogs.news, title: blogs.news.title }]);
for (const ar of articles) pages.push(['article', `blogs/news/${ar.handle}.html`, { blog: blogs.news, article: ar, title: ar.title }]);
pages.push(['search', 'search.html', { search: { performed: false, results: [], results_count: 0, terms: '' }, title: '検索' }]);
pages.push(['cart', 'cart.html', { title: 'カート' }]);
pages.push(['404', '404.html', { title: 'ページが見つかりません' }]);
const only = process.argv[4];
for (const [t, o, x] of pages) if (!only || o.includes(only)) await renderPage(t, o, x);
