// Visual QA sweep: node qa.mjs <base-url> <pages-file> <widths> [scheme]
// For each page × width: scroll through, then report overflow, clipped boxes, overlapping text, still-hidden content,
// Japanese orphan lines in headings, oversized images. One Chrome for everything.
import { spawn } from 'node:child_process';
import fs from 'node:fs';
const [base, pagesFile, widthsArg = '375,390,768,1024,1440', scheme = 'dark'] = process.argv.slice(2);
const pages = fs.readFileSync(pagesFile, 'utf8').split('\n').map((s) => s.trim()).filter(Boolean);
const widths = widthsArg.split(',').map(Number);
const port = 9800 + Math.floor(Math.random() * 100);
const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', ['--headless=new', `--remote-debugging-port=${port}`, '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--hide-scrollbars', `--user-data-dir=/tmp/nd-qa-${port}`, 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let l; for (let i = 0; i < 60 && !l; i++) { try { l = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json(); } catch { await sleep(200); } }
const ws = new WebSocket(l.find((t) => t.type === 'page').webSocketDebuggerUrl); await new Promise((r) => (ws.onopen = r));
let id = 0; const p = new Map(); ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && p.has(d.id)) { p.get(d.id)(d); p.delete(d.id); } };
const send = (method, params = {}) => new Promise((r) => { const i = ++id; p.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
await send('Page.enable');
const probe = `(async () => {
  const w = (t) => new Promise((r) => setTimeout(r, t));
  try { localStorage.setItem('nd-scheme', '${scheme}'); } catch (e) {}
  document.documentElement.dataset.scheme = '${scheme}';
  const H = () => document.documentElement.scrollHeight;
  for (let y = 0; y < H(); y += Math.round(innerHeight * 0.6)) { scrollTo(0, y); await w(110); }
  scrollTo(0, H()); await w(900); scrollTo(0, 0); await w(300);
  const W = innerWidth, out = { overflow: null, clipped: [], overlap: [], hidden: [], orphan: [], bigimg: [] };
  const name = (e) => { const s = e.closest('.shopify-section'); return (s ? s.id.replace('shopify-section-', '').replace(/^template--\\d+__/, '') : '?') + ' ' + e.tagName.toLowerCase() + (e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\\s+/).slice(0, 2).join('.') : ''); };
  const shown = (e) => { const r = e.getBoundingClientRect(); let L = r.left, R = r.right, T = r.top, B = r.bottom; for (let n = e.parentElement; n && n !== document.body; n = n.parentElement) { const c = getComputedStyle(n); if (c.position === 'fixed' || c.position === 'sticky') return false; if (c.overflow !== 'visible') { const q = n.getBoundingClientRect(); L = Math.max(L, q.left); R = Math.min(R, q.right); T = Math.max(T, q.top); B = Math.min(B, q.bottom); } } return (R - L) * (B - T) > 0.5 * r.width * r.height; };
  const vis = (e) => { const c = getComputedStyle(e); return c.display !== 'none' && c.visibility !== 'hidden' && !e.closest('[hidden], dialog:not([open]), [aria-hidden=true], .visually-hidden') && !(e.closest('details:not([open])') && !e.closest('summary')); };
  if (document.documentElement.scrollWidth > W + 1) {
    const c = []; for (const e of document.querySelectorAll('body *')) { const r = e.getBoundingClientRect(); if (r.right > W + 1 && r.width < W * 1.5 && vis(e)) { let pp = e.parentElement, cl = false; while (pp && pp !== document.body) { if (getComputedStyle(pp).overflowX !== 'visible') { cl = true; break; } pp = pp.parentElement; } if (!cl) c.push(name(e) + ' R=' + Math.round(r.right)); } }
    out.overflow = document.documentElement.scrollWidth + ' > ' + W + ' :: ' + c.slice(0, 3).join(' | ');
  }
  // bordered / rounded boxes cut by an overflow-hidden ancestor
  for (const e of document.querySelectorAll('main *')) {
    const c = getComputedStyle(e); if (!vis(e)) continue;
    const hasBox = parseFloat(c.borderTopWidth) > 0 && c.borderTopStyle !== 'none' || c.outlineStyle !== 'none' && parseFloat(c.outlineWidth) > 0;
    if (!hasBox) continue;
    const r = e.getBoundingClientRect(); if (r.width < 8 || r.height < 8) continue;
    let pp = e.parentElement;
    while (pp && pp !== document.body) { const pc = getComputedStyle(pp); if (pc.overflow !== 'visible' && pc.overflowX !== 'visible') { const pr = pp.getBoundingClientRect(); const pad = parseFloat(c.outlineWidth || 0) + parseFloat(c.outlineOffset || 0);
      if (r.left - pad < pr.left - 0.5 || r.right + pad > pr.right + 0.5 || (r.top - pad < pr.top - 0.5 && pc.overflowY !== 'auto') ) { out.clipped.push(name(e) + ' in ' + name(pp)); } break; } pp = pp.parentElement; }
  }
  // boxes missing one edge: rounded element with a border on some sides but not all (e.g. a highlight box without its bottom line)
  out.edges = [];
  for (const e of document.querySelectorAll('main *')) { const c = getComputedStyle(e); if (!vis(e) || parseFloat(c.borderTopLeftRadius) < 4) continue;
    const w = ['Top','Right','Bottom','Left'].map((k) => c['border' + k + 'Style'] !== 'none' ? parseFloat(c['border' + k + 'Width']) : 0);
    if (w.some((x) => x > 0) && w.some((x) => x === 0) && w.filter((x) => x > 0).length >= 2) out.edges.push(name(e)); }
  out.edges = [...new Set(out.edges)].slice(0, 6);
  // overlapping text blocks (different leaf text elements whose boxes intersect)
  const leaves = [...document.querySelectorAll('main h1, main h2, main h3, main h4, main p, main li, main a, main button, main span, main b, main strong, main small, main time, main label, main dt, main dd')].filter((e) => vis(e) && shown(e) && e.children.length === 0 && e.textContent.trim().length > 1 && parseFloat(getComputedStyle(e).opacity) > 0.05);
  const boxes = leaves.map((e) => [e, e.getBoundingClientRect()]).filter(([, r]) => r.width > 0 && r.height > 0);
  for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
    const [a, ra] = boxes[i], [b, rb] = boxes[j];
    if (a.contains(b) || b.contains(a)) continue;
    const ix = Math.min(ra.right, rb.right) - Math.max(ra.left, rb.left), iy = Math.min(ra.bottom, rb.bottom) - Math.max(ra.top, rb.top);
    if (ix > 6 && iy > 6 && ix * iy > 0.25 * Math.min(ra.width * ra.height, rb.width * rb.height)) { if (out.overlap.length < 8) out.overlap.push(name(a) + ' × ' + name(b) + ' "' + a.textContent.trim().slice(0, 14) + '"/"' + b.textContent.trim().slice(0, 14) + '"'); }
  }
  // content still invisible after scrolling (reveal failed)
  for (const e of document.querySelectorAll('main h1, main h2, main h3, main p, main img, main li, main .btn')) {
    if (!vis(e)) continue; const r = e.getBoundingClientRect(); if (r.width < 4 || r.height < 4) continue;
    let op = 1, n = e; while (n && n !== document.body) { op *= parseFloat(getComputedStyle(n).opacity); n = n.parentElement; }
    if (op < 0.1 && !e.closest('.nd-banner__img, .qc3d__poster, .qc3d, [data-qc3d], .gallery, .pdp-film, .nd-yt')) out.hidden.push(name(e));
  }
  // Japanese orphans: last line of a heading/paragraph holding ≤ 2 characters
  for (const e of document.querySelectorAll('main h1, main h2, main h3, main h4, main p, main li')) {
    if (!vis(e)) continue; const t = e.textContent.trim(); if (!/[぀-ヿ㐀-鿿]/.test(t) || t.length < 6) continue;
    const range = document.createRange(); range.selectNodeContents(e); const rects = [...range.getClientRects()].filter((r) => r.width > 1);
    if (rects.length < 2) continue;
    const lines = {}; rects.forEach((r) => { const k = Math.round(r.top / 4); lines[k] = (lines[k] || 0) + r.width; });
    const keys = Object.keys(lines).map(Number).sort((a, b) => a - b); if (keys.length < 2) continue;
    const fs = parseFloat(getComputedStyle(e).fontSize); const last = lines[keys[keys.length - 1]];
    if (last < fs * 2.3) out.orphan.push(name(e) + ' "' + t.slice(-8) + '"');
  }
  for (const e of document.querySelectorAll('main img, main video')) { if (!vis(e)) continue; const r = e.getBoundingClientRect(); if (W >= 1024 && (r.width > 1000 && !e.closest('.nd-feature--bleed, .nd-band, .qc3d, .nd-banner, .nd-campaign--full, .nd-popcards__card') || r.height > 800)) out.bigimg.push(name(e) + ' ' + Math.round(r.width) + 'x' + Math.round(r.height)); }
  out.clipped = [...new Set(out.clipped)].slice(0, 8); out.hidden = [...new Set(out.hidden)].slice(0, 8); out.orphan = [...new Set(out.orphan)].slice(0, 10); out.bigimg = out.bigimg.slice(0, 5);
  return JSON.stringify(out);
})()`;
for (const pg of pages) for (const w of widths) {
  await send('Emulation.setDeviceMetricsOverride', { width: w, height: w < 600 ? 812 : 900, deviceScaleFactor: 1, mobile: w < 600 });
  await send('Page.navigate', { url: base + pg }); await sleep(3200);
  const r = await send('Runtime.evaluate', { expression: probe, awaitPromise: true, returnByValue: true });
  let o; try { o = JSON.parse(r.result.result.value); } catch { console.log(pg, w, 'ERROR', JSON.stringify(r.result).slice(0, 200)); continue; }
  const issues = Object.entries(o).filter(([k, v]) => v && (Array.isArray(v) ? v.length : true));
  if (issues.length) console.log(`## ${pg || '/'} @${w}\n` + issues.map(([k, v]) => `  ${k}: ${Array.isArray(v) ? v.join('\n      ') : v}`).join('\n'));
}
ws.close(); chrome.kill();
console.log('QA DONE');
