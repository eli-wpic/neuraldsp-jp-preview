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

# mini page: the visual comparison (same as the homepage, without the chooser) before the full table, which sits behind a button
head, m = load('product.quad-cortex-mini')
_, home = load('index')
if 'compare' not in m['order'] and 'compare' in home['sections'] and 'rich_text_ewyvb6' in m['order']:
    comp = json.loads(json.dumps(home['sections']['compare']))
    comp['settings'].update(show_chooser=False, eyebrow='Compare', heading='Quad Cortex mini と比べる', body='')
    m['sections']['compare'] = comp
    m['order'].insert(m['order'].index('rich_text_ewyvb6'), 'compare')
    m['sections']['rich_text_ewyvb6']['settings']['collapsed_label'] = '詳しい比較表を見る（機能・入出力）'
    save('product.quad-cortex-mini', head, m)

# product pages end the same way: no closing photo on the mini page, no 製品アップデート button anywhere
for f in sorted(T.glob('product.*.json')):
    head, d = load(f.stem)
    changed = False
    if f.stem == 'product.quad-cortex-mini' and 'single_image_g7kzr7' in d['order']:
        d['order'].remove('single_image_g7kzr7'); d['sections'].pop('single_image_g7kzr7', None); changed = True
    for k in d['order']:
        sec = d['sections'][k]
        if sec['type'] != 'nd-specs':
            continue
        drop = [b for b, blk in sec.get('blocks', {}).items() if '製品アップデート' in blk.get('settings', {}).get('label', '')]
        for b in drop:
            sec['blocks'].pop(b); sec['block_order'] = [x for x in sec.get('block_order', []) if x != b]; changed = True
    if changed:
        save(f.stem, head, d)
        print('cleaned', f.stem)

# ---- client review round (Nov 2026) ----
GENRES = {'pli': 'progressive,versatile', 'goj': 'acg', 'cor': 'versatile,oldschool', 'joh': 'oldschool,versatile',
          'mis': 'progressive,acg', 'tim': 'progressive,acg', 'rab': 'acg,versatile', 'pet': 'progressive,versatile',
          'nol': 'progressive', 'slo': 'oldschool', 'for': 'acg', 'par': 'bass'}
for name in ('index', 'page.quadcortex-plugin-bundle', 'page.quadcortex-mini-plugin-bundle'):
    head, d = load(name)
    sec = d['sections'].get('plugins')
    if sec:
        for b in sec['blocks'].values():
            code = b['settings'].get('product', '')[-3:]
            if code in GENRES:
                b['settings']['tones'] = GENRES[code]
        st = sec['settings']
        for k in ('tone_clean', 'tone_crunch', 'tone_highgain', 'tone_ambient', 'tone_map'):
            st.pop(k, None)
    if name != 'index' and 'main' in d['sections']:
        d['sections']['main'].setdefault('settings', {}).update(
            title_override='プラグインセット',
            subtitle='プラグインは Quad Cortex または Quad Cortex mini とのセットでのみご購入いただけます。お好きなプラグインを選び、本体と一緒にお求めください。')
    save(name, head, d)

# comparison: front-facing photos for every product
FRONT = {'quad-cortex': 'qc-photo-1.webp', 'quad-cortex-mini': 'mini-photo-2.webp', 'nano-cortex': 'nano-photo-1.webp'}
for name in ('index', 'product.quad-cortex-mini'):
    head, d = load(name)
    if 'compare' in d['sections']:
        for b in d['sections']['compare']['blocks'].values():
            b['settings']['image_asset'] = FRONT.get(b['settings'].get('product'), '')
        save(name, head, d)

# Cortex Control / Cloud: still picture behind the title (a muted YouTube loop shows a bot check in some browsers); the film still plays on click
for name in ('page.cortex-control', 'page.neuraldsp-account'):
    head, d = load(name)
    hero = next((k for k in d['order'] if d['sections'][k]['type'] == 'nd-hero'), None)
    if hero:
        hs = d['sections'][hero]['settings']
        hs.pop('bg_youtube', None)
        hs['bg_image_url'] = 'https://cdn.shopify.com/s/files/1/0747/8109/8202/files/hero_1_7da1ff2b-0c59-4f40-ba10-c336e631ad91.webp?v=1743734645'
        save(name, head, d)

# PSU pages: choose between the Quad Cortex PSU and the mini PSU
for name in ('product.psu', 'product.mini-psu'):
    head, d = load(name)
    d['sections']['main']['settings'].update(hardware_choices=['quad-cortex-psu', 'quad-cortex-mini-psu'], hardware_heading='タイプを選ぶ',
        hardware_sub='どちらの電源アダプターも Quad Cortex・Quad Cortex mini・Nano Cortex でご使用いただけます。',
        soon_label='Quad Cortex mini 電源アダプター（PSU）', soon_image='minipsu-photo-1.webp')
    save(name, head, d)

# Gig Case: real photos instead of renders
head, d = load('product.gig-case')
# five distinct real photos: angled with strap, front, open with a Quad Cortex, packed with cables, side
d['sections']['main']['settings']['photo_assets'] = ','.join(f'gigcase-photo-{i}.webp' for i in (10, 1, 4, 6, 11))
save('product.gig-case', head, d)

# Nano Cortex signal chain: vertical tabs (category list → devices + chain picture) instead of one long text block
head, d = load('product.nano-cortex')
if 'custom_liquid_qmu8mb' in d['sections'] and d['sections']['custom_liquid_qmu8mb']['type'] == 'nd-feature':
    src = d['sections']['custom_liquid_qmu8mb']['settings']
    parts = re.split(r'<h2>(.*?)</h2>', src.get('body', ''))
    chunks = [(src.get('heading', 'Neural Capture'), parts[0])] + list(zip(parts[1::2], parts[2::2]))
    link = re.search(r'<p>\s*<a href="([^"]+)"[^>]*>\s*([^<]+?)\s*</a>\s*</p>\s*$', chunks[-1][1])
    if link:
        chunks[-1] = (chunks[-1][0], chunks[-1][1][:link.start()])
    img = {'Neural Capture': 'capture', 'Impulse Responses': 'cab', 'Pre Effects': 'pre', 'Post Effects': 'post', 'EQ（イコライザー）': 'eq', 'インプットゲート': 'input-gate'}
    base = 'https://cdn.shopify.com/s/files/1/0747/8109/8202/files/nc-{}-chain.webp'
    blocks = {}
    for i, (label, body) in enumerate(chunks):
        st = {'label': label.strip(), 'body': body.strip()}
        if label.strip() in img:
            st['image_url'] = base.format(img[label.strip()])
        blocks[f'tab_{i}'] = {'type': 'tab', 'settings': st}
    d['sections']['custom_liquid_qmu8mb'] = {'type': 'nd-tabs', 'settings': {'heading': 'シグナルチェーン',
        **({'link_label': link.group(2), 'link_url': link.group(1)} if link else {})}, 'blocks': blocks, 'block_order': list(blocks)}
    save('product.nano-cortex', head, d)

# menu: the page covers Cortex Control and Cortex Cloud
p = THEME / 'sections' / 'header-group.json'
s = p.read_text()
p.write_text(s.replace('"label": "Cortex Cloud"', '"label": "Cortex Control / Cloud"'))
print('review round ok')
