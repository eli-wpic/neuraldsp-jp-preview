import { themeCheckRun } from '@shopify/theme-check-node';
const root = process.argv[2];
const res = await themeCheckRun(root, undefined, () => {});
const offenses = res.offenses || res;
const sev = ['error', 'warning', 'info'];
const byFile = {};
for (const o of offenses) {
  const f = o.uri.replace('file://', '').replace(encodeURI(root), '').replace(root, '');
  (byFile[f] ||= []).push(`${sev[o.severity] || o.severity} ${o.check}: ${o.message.slice(0, 160)} @${o.start?.line ?? ''}`);
}
let n = 0;
for (const [f, list] of Object.entries(byFile)) { console.log(f); list.forEach((l) => { console.log('   ', l); n++; }); }
console.log('TOTAL', n, 'errors', offenses.filter((o) => o.severity === 0).length);
