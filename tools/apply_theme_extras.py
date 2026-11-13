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
          'product.psu': ('psu', 4)}
# review: each product offers only its own PSU (Nano uses the Quad Cortex PSU; it ships with a USB-C cable only)
ACCESSORIES = {'product.quad-cortex': ['gig-case', 'quad-cortex-psu'],
               'product.quad-cortex-mini': ['quad-cortex-mini-psu'],
               'product.nano-cortex': ['quad-cortex-psu']}
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
psu['sections']['main']['settings']['photo_assets'] = ','.join(f'minipsu-photo-{i}.webp' for i in (1, 2, 4, 5, 7))
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
p.write_text(s.replace('"label": "Cortex Cloud"', '"label": "Cortex Control"').replace('"label": "Cortex Control / Cloud"', '"label": "Cortex Control"'))
print('review round ok')

# Quad Cortex: the full film Shopify already hosts plays in place (no YouTube embed needed)
head, d = load('product.quad-cortex')
d['sections']['main']['settings']['film_mp4'] = 'https://cdn.shopify.com/videos/c/o/v/850a2016b0514a52a3e5448579317965.mp4'
save('product.quad-cortex', head, d)
# mini PSU: five distinct photos (no repeats)
head, d = load('product.mini-psu')
d['sections']['main']['settings']['photo_assets'] = ','.join(f'minipsu-photo-{i}.webp' for i in (1, 2, 4, 5, 7))
save('product.mini-psu', head, d)

# ---- client review round 2 (Nov 2026) ----
# Cortex Control hidden for now: menu tab, homepage section, Quad Cortex page section.
# "disabled": true is Shopify's own hide switch, so each one comes back with the eye icon in the theme editor (or by deleting the flag).
for name, key in (('index', 'cortex_control'), ('product.quad-cortex', 'custom_liquid_aieqim')):
    head, d = load(name)
    if key in d['sections']:
        d['sections'][key]['disabled'] = True
        save(name, head, d)
MANUALS = ('Quad Cortex マニュアル|https://neuraldsp.com/manual/quad-cortex\n'
           'Quad Cortex mini マニュアル|https://neuraldsp.com/manual/quad-cortex-mini\n'
           'Nano Cortex マニュアル|https://neuraldsp.com/manual/nano-cortex')
for grp in ('header-group', 'footer-group'):
    p = THEME / 'sections' / f'{grp}.json'
    g = json.loads(p.read_text())
    sec = next(iter(g['sections'].values()))
    for b in sec['blocks'].values():
        st = b['settings']
        if grp == 'header-group' and st.get('url') == '/pages/neuraldsp-account':
            b['disabled'] = True
        if grp == 'footer-group':
            if st.get('title') == 'コミュニティ':
                b['disabled'] = True  # community column hidden (review); unhide in the editor if wanted
            if st.get('title') == 'サポート':
                st['links'] = re.sub(r'^ユーザーマニュアル\|[^\n]*', MANUALS, st['links'], flags=re.M)
            if st.get('title') == '製品':  # the Cortex Cloud link goes to the hidden Cortex Control / Cloud page
                st['links'] = '\n'.join(l for l in st['links'].split('\n') if not l.endswith('/pages/neuraldsp-account'))
    if grp == 'footer-group':
        sec['settings']['legal'] = ('Neural DSP®, Neural Capture®, Capture®, Quad Cortex®, Archetype®, Algorithmically Perfect®, and Nameless® '
                                    'are registered trademarks of Neural DSP Technologies Oy.')
    p.write_text(json.dumps(g, ensure_ascii=False, indent=2))
# plugin list: no download note under the buttons
for name in ('index', 'page.quadcortex-plugin-bundle', 'page.quadcortex-mini-plugin-bundle'):
    head, d = load(name)
    if 'plugins' in d['sections']:
        d['sections']['plugins']['settings']['trial_note'] = ''
        save(name, head, d)
# Nano Cortex: 360° film centred on white; the Yo Onitan sound demo hidden
head, d = load('product.nano-cortex')
if 'custom_liquid_d6ym6c' in d['sections']:
    d['sections']['custom_liquid_d6ym6c']['settings'].update(layout='media', light=True)
if 'video_89yj6x' in d['sections']:
    d['sections']['video_89yj6x']['disabled'] = True
save('product.nano-cortex', head, d)
# shopping guide: smaller type, left-aligned
head, d = load('page.shopping-guide')
for k, sec in d['sections'].items():
    if sec['type'] in ('nd-faq', 'main-page'):
        sec.setdefault('settings', {})['compact'] = True
save('page.shopping-guide', head, d)
print('review round 2 ok')

# ---- client review round 3 (Nov 2026) ----
# hardware pages: photos are the key visual (the 3D viewer stays in the theme: set Left column back to "3D model + photos" to return it)
for name in ('product.quad-cortex', 'product.quad-cortex-mini', 'product.nano-cortex'):
    head, d = load(name)
    d['sections']['main']['settings']['media_mode'] = '3d' if name == 'product.quad-cortex' else 'gallery'  # Quad Cortex keeps the 3D viewer (Eli, Nov 13)
    if name == 'product.nano-cortex':
        d['sections']['main']['settings']['acc_note'] = '本体には USB-C ケーブルが付属します（電源アダプターは付属しません）。USB-C ケーブルからの給電でもご使用いただけます。'
    save(name, head, d)
# Quad Cortex: the touchscreen film has a white background baked in around the unit; clip it to the unit's outline
head, d = load('product.quad-cortex')
if 'image_with_text_gqqlkf' in d['sections']:
    d['sections']['image_with_text_gqqlkf']['settings']['clip_white'] = True
    save('product.quad-cortex', head, d)
print('review round 3 ok')
