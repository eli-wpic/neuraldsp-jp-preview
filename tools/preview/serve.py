"""Local preview server for the rendered theme: Shopify-style URLs (/products/x) map to x.html."""
import http.server, os, sys, urllib.parse
ROOT = sys.argv[1]
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=ROOT, **k)
    def send_head(self):
        path = urllib.parse.unquote(urllib.parse.urlsplit(self.path).path)
        if path in ('', '/'): path = '/index.html'
        fs = os.path.join(ROOT, path.lstrip('/'))
        if (not os.path.exists(fs) or os.path.isdir(fs)) and os.path.exists(fs.rstrip('/') + '.html'):
            path = path.rstrip('/')
            self.path = urllib.parse.quote(path + '.html')
        elif not os.path.exists(fs):
            pages = []
            for d, _, files in os.walk(ROOT):
                for f in files:
                    if f.endswith('.html'):
                        rel = os.path.relpath(os.path.join(d, f), ROOT)[:-5]
                        pages.append('/' if rel == 'index' else '/' + rel)
            body = ('<!doctype html><meta charset=utf-8><body style="font-family:system-ui;background:#0a0b0c;color:#eee;padding:40px">'
                    f'<h2>Local preview: {path} isn\'t rendered</h2><p>Cart, checkout, account and search only work on the real Shopify store. Rendered pages:</p><ul>'
                    + ''.join(f'<li><a style="color:#4ea3ff" href="{p}">{p}</a></li>' for p in sorted(pages)) + '</ul>').encode()
            self.send_response(404); self.send_header('Content-Type', 'text/html; charset=utf-8'); self.send_header('Content-Length', str(len(body))); self.end_headers()
            self.wfile.write(body); return None
        return super().send_head()
http.server.ThreadingHTTPServer(('127.0.0.1', 4322), H).serve_forever()
