"""Post-processing after convert_live_to_theme.py: settings that come from the theme's own assets, not the live site.
- 写真 uses the transparent photo sets shipped in assets/ (qc/mini/nano/psu/minipsu-photo-N.webp)
- every plugin page offers the same plugin with Quad Cortex or Quad Cortex mini
- both PSUs are offered as accessories on every hardware page (all PSUs work with all hardware)
Usage: python3 tools/apply_theme_extras.py neuraldsp-jp-theme"""
import json, re, sys
from pathlib import Path

THEME = Path(sys.argv[1])
T = THEME / 'templates'
PHOTOS = {'product.quad-cortex': ('qc', 5), 'product.quad-cortex-mini': ('mini', 4), 'product.nano-cortex': ('nano', 5),
          'product.psu': ('psu', 4), 'product.mini-psu': ('minipsu', 9)}
ACCESSORIES = {'product.quad-cortex': ['gig-case', 'quad-cortex-psu', 'quad-cortex-mini-psu'],
               'product.quad-cortex-mini': ['quad-cortex-psu', 'quad-cortex-mini-psu'],
               'product.nano-cortex': ['quad-cortex-psu', 'quad-cortex-mini-psu']}
CODE = {'corywongx': 'cor', 'fortin-nameless-suite-x': 'for', 'gojirax': 'goj', 'misha-mansoor-x': 'mis', 'nollyx': 'nol',
        'parallaxx': 'par', 'petrucci-x': 'pet', 'plinix': 'pli', 'rabea-x': 'rab', 'soldano-slo-100x': 'slo', 'tim-henson-x': 'tim'}


def load(name):
    raw = (T / f'{name}.json').read_text()
    m = re.match(r'^\s*/\*[\s\S]*?\*/\s*', raw)
    head = m.group(0) if m else ''
    return head, json.loads(raw[len(head):])


def save(name, head, data):
    (T / f'{name}.json').write_text(head + json.dumps(data, ensure_ascii=False, indent=2))


for f in sorted(T.glob('product.*.json')):
    name = f.stem
    head, d = load(name)
    main = d['sections'].get('main')
    if not main:
        continue
    st = main.setdefault('settings', {})
    if name in PHOTOS:
        key, n = PHOTOS[name]
        st['photo_assets'] = ','.join(f'{key}-photo-{i}.webp' for i in range(1, n + 1))
    if name in ACCESSORIES:
        st['accessories'] = ACCESSORIES[name]
        st['show_accessories'] = True
    sfx = name.split('.', 1)[1]
    code = None
    if sfx.startswith('quad-cortex-mini-') and len(sfx) == len('quad-cortex-mini-') + 3:
        code = sfx[-3:]
    elif sfx.startswith('quadcortex-'):
        code = CODE.get(sfx[len('quadcortex-'):])
    elif sfx == 'archetype-john-mayer-x':
        code = 'joh'
    if code:
        st['hardware_choices'] = [f'quadcortex-plugin-bundle-{code}', f'quadcortex-mini-plugin-bundle-{code}']
    save(name, head, d)

# template for the new mini PSU product (create the product in Shopify, then assign this template)
head, psu = load('product.psu')
hero = next((k for k in psu['order'] if psu['sections'][k]['type'] == 'nd-hero'), None)
if hero:
    psu['sections'][hero]['settings'].update(title='Quad Cortex mini 電源アダプター（PSU）', asset_image='minipsu-photo-1.webp',
        subtitle='Quad Cortex mini用電源アダプターです。Quad Cortex・Nano Cortexでもご使用いただけます。')
psu['sections']['main']['settings']['photo_assets'] = ','.join(f'minipsu-photo-{i}.webp' for i in range(1, 10))
save('product.mini-psu', '/*\n * Mini PSU: create the product (handle quad-cortex-mini-psu) and assign this template. Hero copy is a draft to confirm.\n */\n', psu)
print('ok')

# plugin pages: the hero is the plugin's video only (no product card picture on top)
for f in sorted(T.glob('product.*.json')):
    head, d = load(f.stem)
    changed = False
    for k in d['order']:
        sec = d['sections'][k]
        if sec['type'] == 'nd-hero' and sec.get('settings', {}).get('video_url') and ('plugin' in json.dumps(sec, ensure_ascii=False).lower() or 'archetype' in json.dumps(sec, ensure_ascii=False).lower() or ' x' in sec['settings'].get('title', '').lower()):
            for key in ('image', 'image_url', 'asset_image'):
                if sec['settings'].pop(key, None) is not None:
                    changed = True
    if changed:
        save(f.stem, head, d)

# Cortex Control / Cortex Cloud: the film loops behind the hero and plays in place (same as product pages)
for name in ('page.cortex-control', 'page.neuraldsp-account'):
    head, d = load(name)
    vid = next((d['sections'][k]['settings'].get('youtube_id') for k in d['order'] if d['sections'][k]['type'] == 'nd-video'), None)
    hero = next((k for k in d['order'] if d['sections'][k]['type'] == 'nd-hero'), None)
    if vid and hero:
        hs = d['sections'][hero]['settings']
        hs.update(bg_youtube=vid, film_url=f'https://youtu.be/{vid}', overlay=hs.get('overlay', 55))
        hs.pop('image_url', None)
        d['order'] = [k for k in d['order'] if d['sections'][k]['type'] != 'nd-video']
        d['sections'] = {k: v for k, v in d['sections'].items() if k in d['order']}
        save(name, head, d)
print('extras ok')

# live legal pages link to Japanese page handles that only work through a redirect; point them at the real pages
for f in list(T.glob('*.json')) + list((THEME / 'sections').glob('*.json')):
    s = f.read_text()
    o = s
    for a, b in (('/pages/返金ポリシー', '/pages/refund-policy'), ('/pages/プライバシーポリシー', '/pages/privacy-policy')):
        s = s.replace(a, b)
    if s != o:
        f.write_text(s)
