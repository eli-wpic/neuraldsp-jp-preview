// Refresh local preview data from the live store's public JSON (read-only GETs).
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const DATA = path.join(path.dirname(fileURLToPath(import.meta.url)), 'data');
const BASE = 'https://neuraldsp.jp';
const get = async (u, type = 'json') => { const r = await fetch(BASE + u, { headers: { 'User-Agent': 'theme-preview' } }); if (!r.ok) throw new Error(u + ' ' + r.status); return type === 'json' ? r.json() : r.text(); };
fs.mkdirSync(DATA, { recursive: true });
const { products } = await get('/products.json?limit=250');
for (const p of products) {
  const j = await get(`/products/${p.handle}.js`);
  fs.writeFileSync(path.join(DATA, p.handle + '.json'), JSON.stringify(j));
}
const { collections } = await get('/collections.json?limit=250');
const colls = [];
for (const c of collections) {
  const { products: cp } = await get(`/collections/${c.handle}/products.json?limit=250`);
  colls.push({ handle: c.handle, title: c.title, description: c.description || '', image: c.image?.src || null, products: cp.map((p) => p.handle) });
}
fs.writeFileSync(path.join(DATA, 'collections.json'), JSON.stringify(colls));
fs.writeFileSync(path.join(DATA, 'news.atom'), await get('/blogs/news.atom', 'text'));
console.log(`products ${products.length}, collections ${colls.length}, fetched ${new Date().toISOString()}`);
