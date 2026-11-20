"""Turn the rendered preview (absolute /paths) into a GitHub Pages site under /<repo>/.
Usage: python3 tools/build_pages.py <rendered-preview-dir> docs neuraldsp-jp-preview"""
import re, shutil, sys
from pathlib import Path

src, out, repo = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
base = f'/{repo}/'
if not (src / 'index.html').is_file():
    sys.exit(f'{src} is empty or missing; render the preview first (nothing was changed)')
if out.exists():
    shutil.rmtree(out)
shutil.copytree(src, out)
# root-relative URLs in attributes, inline JSON (&quot; and \") and CSS url(): add the repo prefix
pat = re.compile(r'''(=["']|&quot;|&#34;|\(['"]?|:\s?["'])/(?!/)''')
for f in out.rglob('*.html'):
    s = f.read_text()
    s = pat.sub(lambda m: m.group(1) + base, s)
    # pages that only exist on the real store (help-centre app, customer accounts, policies) open on neuraldsp.jp
    s = re.sub(r'(href=")' + re.escape(base) + r'(a/|account|policies/|checkout)', r'\1https://neuraldsp.jp/\2', s)
    f.write_text(s)
# folders that also have a page of the same name (/blogs/news and /blogs/news/<article>, /collections): Pages needs index.html
for f in list(out.rglob('*.html')):
    d = f.with_suffix('')
    if d.is_dir():
        shutil.copy(f, d / 'index.html')
# retired asset names: old cached pages (browser / Pastel) still ask for them, so serve the replacement under the old name
LEGACY = {'gigcase-hero.webp': 'gigcase-hq-front45.webp', 'gigcase-photo-10.webp': 'gigcase-hq-strap.webp', 'gigcase-photo-1.webp': 'gigcase-hq-front.webp',
    'gigcase-photo-4.webp': 'gigcase-hq-open-full.webp', 'gigcase-photo-6.webp': 'gigcase-hq-open-full.webp', 'gigcase-photo-11.webp': 'gigcase-hq-strap.webp'}
for old, new in LEGACY.items():
    if (out / 'assets' / new).is_file() and not (out / 'assets' / old).exists(): shutil.copy(out / 'assets' / new, out / 'assets' / old)
(out / '.nojekyll').write_text('')
print('pages built:', sum(1 for _ in out.rglob('*.html')))
