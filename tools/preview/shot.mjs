// Screenshot a local preview page after running a JS snippet: node shot.mjs <url> <out.jpg> [js] [width]
import { spawn } from 'node:child_process';
import fs from 'node:fs';
const [url, out, js = '0', w = '1440'] = process.argv.slice(2);
const port = 9400 + Math.floor(Math.random() * 400);
const chrome = spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', ['--headless=new', `--remote-debugging-port=${port}`, '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--hide-scrollbars', `--user-data-dir=/tmp/nd-shot-${port}`, 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let l; for (let i = 0; i < 60 && !l; i++) { try { l = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json(); } catch { await sleep(200); } }
const ws = new WebSocket(l.find((t) => t.type === 'page').webSocketDebuggerUrl); await new Promise((r) => (ws.onopen = r));
let id = 0; const p = new Map(); ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && p.has(d.id)) { p.get(d.id)(d); p.delete(d.id); } };
const send = (method, params = {}) => new Promise((r) => { const i = ++id; p.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
await send('Emulation.setDeviceMetricsOverride', { width: +w, height: 900, deviceScaleFactor: 1, mobile: +w < 600 });
await send('Page.enable'); await send('Page.navigate', { url }); await sleep(4500);
const r = await send('Runtime.evaluate', { expression: js, awaitPromise: true, returnByValue: true }); await sleep(1800);
if (r.result?.result?.value !== undefined) console.log(JSON.stringify(r.result.result.value));
const s = await send('Page.captureScreenshot', { format: 'jpeg', quality: 70 }); fs.writeFileSync(out, Buffer.from(s.result.data, 'base64'));
ws.close(); chrome.kill();
