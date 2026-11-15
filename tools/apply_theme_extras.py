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
    d['sections']['main']['settings']['media_mode'] = '3d'  # all three hardware pages use the 3D viewer with view buttons, film and 写真 (Eli, Nov 16)
    if name == 'product.nano-cortex':
        d['sections']['main']['settings']['acc_note'] = '本体には USB-C ケーブルが付属します（電源アダプターは付属しません）。USB-C ケーブルからの給電でもご使用いただけます。'
    save(name, head, d)
# Quad Cortex: the touchscreen film has a white background baked in around the unit; clip it to the unit's outline
head, d = load('product.quad-cortex')
if 'image_with_text_gqqlkf' in d['sections']:
    d['sections']['image_with_text_gqqlkf']['settings']['clip_white'] = True
    save('product.quad-cortex', head, d)
print('review round 3 ok')

# ---- client review round 4 (Nov 16): follow neuraldsp.com/quad-cortex(-mini) for Neural Capture, I/O and the QC vs mini table ----
import html as _html
def insert_after(d, after, key, sec):
    d['sections'][key] = sec
    if key in d['order']: d['order'].remove(key)
    i = d['order'].index(after) + 1 if after in d['order'] else len(d['order'])
    d['order'].insert(i, key)

CAPV = {'type': 'nd-capture-versions', 'settings': {'eyebrow': '', 'heading': '', 'body': ''},
  'blocks': {
    'v1': {'type': 'version', 'settings': {'title': 'Neural Capture', 'version': 'Version 1', 'color': '#7cc4f5', 'where': 'デバイス上で処理',
      'text': '<p>高速・効率的で、完全にオフライン対応。Neural Capture V1 は本体上で直接動作し、多くのアンプ、キャビネット、オーバードライブペダルに対して正確なキャプチャ結果を提供します。日常的な使用や、透明感のあるゲインステージ、処理負荷を気にせず複雑なプリセットを構築したい場合に最適です。</p>'}},
    'v2': {'type': 'version', 'settings': {'title': 'Neural Capture', 'version': 'Version 2', 'color': '#f5cf3d', 'where': 'クラウドで処理',
      'text': '<p>Neural Capture V2 は Cortex Cloud を使用し、より高解像度なアルゴリズムで Capture を処理します。ファズやコンプレッサー、ダイナミクスの高いチューブアンプなど、タッチへの反応が重要な機材に対して、さらに高い精度を実現。ボリュームノブ操作によるクリーンアップ、アンプのサグやブルーム、速いトランジェント、ブレンドコントロールといった繊細な挙動まで、極めて正確にキャプチャします。</p>'}}},
  'block_order': ['v1', 'v2']}

def versus_from_table_html(h):
    """Turn the old comparison HTML (three <table>s with footnotes between them) into nd-versus blocks."""
    blocks, order = {}, []
    def add(t, st):
        k = f'{t}_{len(order)}'; blocks[k] = {'type': t, 'settings': st}; order.append(k)
    titles = ['CorOS 機能', 'ハードウェア I/O', 'その他']
    parts = re.split(r'(<table.*?</table>)', h, flags=re.S)
    ti = 0
    for part in parts:
        if part.startswith('<table'):
            add('group', {'title': titles[ti] if ti < len(titles) else f'表 {ti+1}'}); ti += 1
            for tr in re.findall(r'<tbody>(.*?)</tbody>', part, re.S)[0].split('</tr>'):
                m = re.search(r'<th>(.*?)</th><td>(.*?)</td><td>(.*?)</td>', tr, re.S)
                if not m: continue
                clean = lambda x: _html.unescape(re.sub(r'<br\s*/?>', '\n', x)).strip()
                add('row', {'label': clean(m.group(1)), 'a': clean(m.group(2)), 'b': clean(m.group(3))})
        elif ti:
            for p in re.findall(r'<p>(\*.*?)</p>', part, re.S):
                add('note', {'text': _html.unescape(p).strip()})
    # numbers updated to the official table (neuraldsp.com/quad-cortex-mini, Nov 2026)
    fix = {'バーチャル・デバイス・ライブラリ': ('200+', '200+'), 'Neural Capture ライブラリ': ('2000+', '2000+'),
           'インパルス・レスポンス（IR）ライブラリ': ('1000+', '1000+'), 'ユーザー・キャプチャ保存数': None,
           '外形寸法': ('22.8 × 11.8 × 6.5 cm（8.9 × 4.6 × 2.5インチ）', '29 × 19.5 × 6.9 cm（11.4 × 7.7 × 2.7インチ）'),
           '電源スイッチ': ('対応', '対応'), 'パラメーター・エンコーダー割り当て': ('対応*', '対応（最大10個同時）')}
    for k in order:
        st = blocks[k]['settings']
        if blocks[k]['type'] != 'row': continue
        if st['label'] == 'ユーザー・キャプチャ保存数': st['label'] = 'ユーザー・キャプチャー保存数'
        if fix.get(st['label']): st['a'], st['b'] = fix[st['label']]
        if st['label'] == '価格': st['a'] = st['b'] = '__drop__'
    order = [k for k in order if blocks[k]['settings'].get('a') != '__drop__']  # price is shown under each photo from the live product
    blocks = {k: blocks[k] for k in order}
    return blocks, order

head, mini = load('product.quad-cortex-mini')
old = mini['sections'].get('rich_text_ewyvb6', {}).get('settings', {}).get('html', '')
vblocks, vorder = versus_from_table_html(old)
def versus(heading):
    return {'type': 'nd-versus', 'settings': {'eyebrow': 'Compare', 'heading': heading,
        'product_a': 'quad-cortex-mini', 'image_a': 'mini-top.webp', 'width_a': 22.8,
        'product_b': 'quad-cortex', 'image_b': 'qc-top.webp', 'width_b': 29,
        'feature_label': '機能', 'tax_label': '税込', 'cta_label': '詳しく見る'},
        'blocks': json.loads(json.dumps(vblocks)), 'block_order': list(vorder)}

MINI_HL = [('Quad Cortex の処理能力をそのまま', 'フラッグシップの性能を、コンパクトなボディに。'),
           ('直感的なビジュアル操作', 'グリッド型のシグナルフローを備えた 7インチタッチスクリーン。'),
           ('Neural Capture テクノロジー', '実機のアンプ、キャビネット、ドライブペダル、コンプレッサーを、極めて高精度なデジタルレプリカとして作成・演奏できます。'),
           ('設置面積は 50% 以上コンパクト', 'Quad Cortex のパワーを、どこへでも。')]
# Quad Cortex mini
if vorder:
    insert_after(mini, 'rich_text_w4egmi', 'versus', versus('Quad Cortex と比べる'))
    for k in ('compare', 'rich_text_ewyvb6'):
        if k in mini['sections']: mini['sections'][k]['disabled'] = True  # replaced by "versus"; switch back on in the editor if needed
insert_after(mini, 'rich_text_4vbhpb', 'capture_versions', json.loads(json.dumps(CAPV)))
io = mini['sections']['custom_liquid_tpwyqn']
io['settings'].update(layout='stacked', show_numbers=False, image_asset='mini-rear.webp', image_url='')
for i, (t, x) in enumerate(MINI_HL):
    io['blocks'][f'hl_{i}'] = {'type': 'highlight', 'settings': {'title': t, 'text': x}}
io['block_order'] = [f'hl_{i}' for i in range(len(MINI_HL))] + [b for b in io['block_order'] if not b.startswith('hl_')]
save('product.quad-cortex-mini', head, mini)

# Quad Cortex
head, qc = load('product.quad-cortex')
insert_after(qc, 'rich_text_4vbhpb', 'capture_versions', json.loads(json.dumps(CAPV)))
qc['sections']['custom_liquid_tpwyqn']['settings'].update(layout='stacked', show_numbers=True)
if vorder: insert_after(qc, 'rich_text_dgvea3', 'versus', versus('Quad Cortex mini と比べる'))
save('product.quad-cortex', head, qc)

# Nano keeps its side-by-side list with numbers
head, d = load('product.nano-cortex')
for k, sec in d['sections'].items():
    if sec['type'] == 'nd-numbered': sec['settings'].setdefault('show_numbers', True)
save('product.nano-cortex', head, d)

# comparisons are Quad Cortex and Quad Cortex mini only: Nano hidden in the homepage chooser (switch the block back on to return it)
head, d = load('index')
c = d['sections'].get('compare')
if c and 'm2' in c['blocks']:
    c['blocks']['m2']['disabled'] = True
    c['blocks']['m0']['settings']['recommend_for'] = 'features_yes,features_no,portable_no,price_no'
    c['settings']['body'] = '2つの質問に答えると、Quad Cortex と Quad Cortex mini のどちらがおすすめか分かります。'
save('index', head, d)
print('review round 4 ok', len(vorder), 'table blocks')

# the Neural Capture text sections no longer carry the V1/V2 paragraphs and the English V1 card image: the cards below show them
for name in ('product.quad-cortex', 'product.quad-cortex-mini'):
    head, d = load(name)
    f = d['sections'].get('rich_text_4vbhpb')
    if f:
        b = f['settings'].get('body', '')
        if '高速・効率的で' in b:
            f['settings']['body'] = re.sub(r'(<br/>)+</p>', '</p>', b[:b.index('<p>高速・効率的で')])
        if 'capture-v1-img' in f['settings'].get('image_url', ''):
            f['settings']['image_url'] = ''
            f['settings']['layout'] = 'center'
    save(name, head, d)
print('round 4 capture text ok')

# ---- round 5 (Nov 16): hardware sections laid out like neuraldsp.com (heading + yellow separator, photo full width, list in columns) ----
# The old image_url on the Nano controls / I/O and the mini I/O was neuraldsp.jp's yellow heading separator, not a photo.
NANO_CTRL_PINS = {'1': (39.8, 36.8), '2': (75.3, 36.8), '3': (11.5, 16.0), '4': (85.8, 16.0), '5': (31.0, 16.0), '6': (48.6, 16.0),
                  '7': (66.3, 16.0), '8': (9.1, 39.3), '9': (88.1, 39.3), '10': (9.3, 62.6), '11': (88.1, 62.6), '12': (9.0, 87.4)}
NANO_IO_PINS = {'1': (13.6, 67), '2': (27.5, 67), '3': (51.0, 70.8), '4': (60.9, 67), '5': (72.9, 70.3), '6': (80.1, 26.4), '7': (80.5, 72.5), '8': (87.9, 70.3)}
def pins(sec, table):
    for b in sec['block_order']:
        st = sec['blocks'][b]['settings']
        if sec['blocks'][b]['type'] != 'item': continue
        xy = table.get(str(st.get('number', '')))
        if xy: st['x'], st['y'] = str(xy[0]), str(xy[1])
        else: st.pop('x', None); st.pop('y', None)

head, d = load('product.nano-cortex')
c = d['sections']['rich_text_qkpgfd']
c['settings'].update(layout='stacked', head_position='above', separator=True, show_numbers=True, image_url='', image_asset='nano-top.webp', media_max=600)
pins(c, NANO_CTRL_PINS)
io = d['sections']['rich_text_ae8n7g']
io['settings'].update(layout='stacked', head_position='above', separator=True, show_numbers=True, image_url='', image_asset='nano-rear.webp', media_max=820)
pins(io, NANO_IO_PINS)
save('product.nano-cortex', head, d)

head, d = load('product.quad-cortex-mini')
d['sections']['custom_liquid_tpwyqn']['settings'].update(head_position='above', separator=True, image_url='')
save('product.quad-cortex-mini', head, d)

head, d = load('product.quad-cortex')
d['sections']['custom_liquid_tpwyqn']['settings'].update(head_position='below', separator=True)
save('product.quad-cortex', head, d)
print('round 5 hardware sections ok')

# ---- round 6 (Nov 16): campaign off by default (QC opens first), Latest News hidden (switch back on in the editor) ----
head, d = load('index')
q = d['sections'].get('qc3d')
if q:
    for b in q['blocks'].values():
        if b['type'] == 'campaign': b['settings']['enabled'] = False
if 'news' in d['sections']: d['sections']['news']['disabled'] = True
save('index', head, d)
for grp in ('header-group', 'footer-group'):
    p = THEME / 'sections' / f'{grp}.json'
    g = json.loads(p.read_text())
    for sec in g['sections'].values():
        for b in sec.get('blocks', {}).values():
            st = b['settings']
            if st.get('url') == '/blogs/news': b['disabled'] = True
            if isinstance(st.get('links'), str) and '/blogs/news' in st['links']:
                st['links'] = '\n'.join(l for l in st['links'].split('\n') if '/blogs/news' not in l)
    p.write_text(json.dumps(g, ensure_ascii=False, indent=2))
print('round 6 ok')

# ---- round 7 (Nov 16): what the global pages have and ours didn't ----
sys.path.insert(0, str(Path(__file__).parent))
from nano_faq_ja import NANO_FAQ
COROS_LIST = ('<ul><li>X 対応プラグイン 5 種類が新たに Quad Cortex に対応し、合計 70 種類以上の新しいバーチャルデバイスを追加</li>'
              '<li>すべての Quad Cortex / Quad Cortex mini ユーザー向けに、8 種類の新しいバーチャルデバイス</li>'
              '<li>Device Presets：より速く、より柔軟にリグを組める新しい方法</li>'
              '<li>Neural DSP チームによる 2,000 種類以上のファクトリー Device Presets</li>'
              '<li>お気に入り／最近使った項目メニューを刷新</li></ul>')
def coros(url):
    return {'type': 'nd-update', 'settings': {'badge': 'MAJOR UPDATE', 'heading': 'CorOS 4.1.0 を公開しました', 'youtube_id': 'NSDRgQ0qxz0',
            'list_heading': '4.1.0 の新機能', 'body': COROS_LIST, 'button_label': '変更履歴をすべて見る', 'button_url': url}}
def cols(heading, body, items, n=3):
    blocks = {f'c{i}': {'type': 'column', 'settings': {'title': t, 'text': f'<p>{x}</p>'}} for i, (t, x) in enumerate(items)}
    return {'type': 'nd-columns', 'settings': {'heading': heading, 'body': body, 'columns': n}, 'blocks': blocks, 'block_order': list(blocks)}

# Quad Cortex: global-style CorOS block (with the official first-look video), the four feature cards, Plugin Compatibility
head, d = load('product.quad-cortex')
old = d['sections'].get('custom_liquid_jamdvc')
if old:
    insert_after(d, 'custom_liquid_jamdvc', 'coros_update', coros(old['settings'].get('button_url', '')))
    old['disabled'] = True
cards = [('キャビネットブロック & EQ', '<p><strong>キャビネットブロック</strong></p><p>1,000 種類以上の完璧にキャプチャーされたインパルスレスポンスを収録した、世界でも屈指の IR コレクション。実際のスタジオのように、スピーカーの周りに配置できるバーチャルマイクを備えた唯一の製品です。サードパーティ製 IR も簡単に読み込めます。</p><p><strong>パワフルなパラメトリック EQ</strong></p><p>すべてを指先でコントロール。7 インチのマルチタッチディスプレイを最大限に活かした、直感的で楽しく使えるパラメトリック EQ です。</p>'),
         ('比類のない直感性と柔軟性', '<p><strong>ドラッグ＆ドロップ</strong></p><p>ブロックをドラッグ＆ドロップするだけで、順番やルーティングを数秒で変更できます。</p><p><strong>入力と出力</strong></p><p>ワンスワイプで入出力の設定を確認・調整できます。</p>'),
         ('スイッチングモード', '<p>モードの切り替えはとても簡単。機能へのアクセスやスイッチのカスタマイズも自在です。</p><p><strong>Stomp モード</strong></p><p>アナログのペダルボードのように、リグ内の好きなブロックをフットスイッチに割り当ててオン／オフできます。</p><p><strong>Scene モード</strong></p><p>フットスイッチ 1 つで、リグ内の複数のブロックの設定を瞬時に切り替えられます。</p><p><strong>Preset モード</strong></p><p>8 つのバーチャルリグに瞬時にアクセスできます。</p>'),
         ('コンポーネント', '<p>美しいアルマイト加工のアルミニウム・ユニボディに、色あせないレーザー刻印のグラフィック。マルチタッチディスプレイは、厚さ 1.8mm の化学強化 Corning® 保護ガラスで守られています。</p>')]
pc = {f'k{i}': {'type': 'card', 'settings': {'title': t, 'text': x}} for i, (t, x) in enumerate(cards)}
insert_after(d, 'custom_liquid_cypaxf', 'feature_cards', {'type': 'nd-popcards', 'settings': {'heading': '', 'more_label': '詳しく見る'}, 'blocks': pc, 'block_order': list(pc)})
insert_after(d, 'custom_liquid_tpwyqn', 'plugin_compat', {'type': 'nd-feature', 'settings': {'layout': 'center', 'heading': 'Plugin Compatibility',
    'body': '<p>Neural DSP のプラグインを Quad Cortex に読み込んで、新たな可能性を広げましょう。</p>', 'button_label': '詳しく見る', 'button_url': '/pages/quad-cortex-and-plugin-bundle'}})
save('product.quad-cortex', head, d)

# Quad Cortex mini: CorOS block near the top, and the control details under 速く、直感的な操作性のための設計
head, d = load('product.quad-cortex-mini')
qc_url = old['settings'].get('button_url', '') if old else ''
insert_after(d, 'product_newsletter_popup_qjp3np', 'coros_update', coros(qc_url))
gh = json.dumps(d['sections'].get('rich_text_gh63bm', {}), ensure_ascii=False)
if 'Parameter Focus' not in gh:
    insert_after(d, 'rich_text_gh63bm', 'mini_controls', cols('', '', [
        ('タッチスクリーンとロータリーフットスイッチ', '7 インチのタッチスクリーンと 4 基のステンレス製ロータリーフットスイッチで、音作りでも演奏中でも、指先と足元で反応よく確かな操作が可能です。'),
        ('Parameter Focus System', 'ブロックを選択すると、ロータリーフットスイッチが最も関連性の高いパラメーターに自動で割り当てられます。耳で音を作り込み、すばやく設定を変えられるので、メニュー操作ではなく演奏に集中できます。'),
        ('柔軟なスイッチングモード', '演奏スタイルに合わせて操作方法を選べます。Preset モード：リグ全体を切り替え／Scene モード：1 つのプリセット内でシームレスに変化／Stomp モード：ペダルボード感覚で操作／Hybrid モード：フットスイッチの列ごとにモードを組み合わせ。'),
        ('Gig View', '大きな文字とわかりやすい表示で、ライブに最適な高コントラストのレイアウト。Opposite Page Preview で反対側のページの割り当ても一目で確認でき、曲の途中で迷うことはありません。')], 4))
save('product.quad-cortex-mini', head, d)

# Nano Cortex: NanOS 2.3.0 (was 2.2.0), players and use cases, all 40 FAQs
head, d = load('product.nano-cortex')
o = d['sections'].get('custom_liquid_6hmybr')
if o:
    insert_after(d, 'custom_liquid_6hmybr', 'nanos_update', {'type': 'nd-update', 'settings': {'badge': 'UPDATE', 'heading': 'NanOS 2.3.0 を公開しました',
        'list_heading': '2.3.0 の新機能',
        'body': '<p>新しいエフェクト 5 種類</p><ul><li>Blossom (ST)（Strymon® BigSky® の Bloom モードにインスパイア）</li><li>Shimmer</li><li>Poly Octaver（Electro-Harmonix® POG® にインスパイア）</li><li>Wham（DigiTech® Whammy® にインスパイア）</li><li>Chief OC2（BOSS® OC-2 にインスパイア）</li></ul><p>メトロノーム</p>',
        'button_label': '変更履歴をすべて見る（英語）', 'button_url': 'https://neuraldsp.com/nano-cortex-updates/nanos-2-3-0-is-now-available'}})
    o['disabled'] = True
insert_after(d, 'rich_text_w8yrhb', 'players', cols('あらゆるプレイヤーに。あらゆるセットアップに。',
    '<p>あらゆるレベルのギタリスト、ベーシストのために。経験豊富なプロも、スタジオ中心のクリエイターも、これから始める方も、Nano Cortex なら手間なく世界最高峰のトーンが手に入ります。</p>', [
    ('ツアーミュージシャン', '重いリグはもう必要ありません。スタジオグレードのサウンド、アンプとキャビネットの置き換え、ペダルボードへのシームレスな統合まで、ライブにそのまま使える完全なセットアップがギグバッグに収まります。内蔵の Transpose エフェクトでチューニングを瞬時に変え、FOH や FRFR キャビネットに直接接続して、毎晩どこでも安定したトーンを。'),
    ('スタジオプレイヤー／プロデューサー', 'キャビネットのマイキングも、完璧なテイクを追いかける必要もありません。Nano Cortex は高品質な USB オーディオインターフェース（24bit / 48kHz、4 イン / 3 アウト）としても使え、お気に入りのアンプで録音したり、それをキャプチャーして持ち運んだりできます。クリーンで、速く、静か。現代のセッションのために。'),
    ('これから始める方', 'デジタル機材が初めてでも大丈夫。箱から出してすぐに素晴らしいサウンドを作れ、Cortex Cloud の何千ものトーンを試しながら、高価なペダルやアンプを揃えなくてもリグを広げられます。ヘッドフォンで静かに練習したり、モニターにつないだり。ひらめいたときは、そのまま高音質でコンピューターに録音できます。')]))
insert_after(d, 'players', 'use_cases', cols('1 台で、無限の可能性。',
    '<p>Nano Cortex は、オールインワンのリグであり、アンプとキャビネットの代わりであり、パワフルなマルチエフェクターでもあります。しかもギグバッグに収まるサイズです。</p>', [
    ('どこでも、完全なリグを', 'ステージでも、スタジオでも、リハーサルでも、自宅での曲作りでも、柔軟な入出力を備えた完全なシグナルチェーンを提供します。アンプ不要のギター／ベースリグ一式が、インスピレーションが湧いたその場で使えます。'),
    ('妥協のないアンプ＆キャビネットの置き換え', '重い機材は家に置いていきましょう。お気に入りのアンプやキャビネットの Neural Capture を読み込むことも、自分で作成することもできます。内蔵の IR ローダーで好みのキャビネットに差し替えることも可能。既存のペダルボードに組み込み、PA システムや FRFR キャビネットに直接接続すれば、重い機材を運ぶ手間のない理想的なライブセットアップが完成します。'),
    ('ストンプボックスにも、マルチエフェクターにも', '既存のセットアップに組み込めば、お気に入りのドライブペダルの極めて正確なレプリカを最大 256 個保存できるコンパクトなペダルに。さらに、音作りに使える充実したエフェクトも揃っています。')]))
f = d['sections']['collapsible_content_xx4f6y']
have = {b['settings'].get('question') for b in f['blocks'].values()}
for i, (q, a) in enumerate(NANO_FAQ):
    if q in have: continue
    k = f'faq_{i + 8}'
    f['blocks'][k] = {'type': 'qa', 'settings': {'question': q, 'answer': a}}
    f['block_order'].append(k)
save('product.nano-cortex', head, d)
print('round 7 ok')

# Nano intro: as on neuraldsp.com — heading + first paragraph, the photo, then the Neural Capture paragraphs under it
head, d = load('product.nano-cortex')
sec = d['sections'].get('custom_liquid_hjp4qe')
if sec and '<p>Neural Captureは登場以来' in sec['settings'].get('body', ''):
    b = sec['settings']['body']; i = b.index('<p>Neural Captureは登場以来')
    sec['settings']['body'] = b[:i]
    sec['settings']['body_after'] = ('<p>Neural Captureは登場以来、アンプやキャビネット、ドライブペダルのキャプチャと再現において他に類を見ない精度を実現し、演奏時のリアルさとレスポンスの良さはアーティストやエンジニアから高く評価されてきました。</p>'
                                     '<p>そして今、その革新的なテクノロジーは、いつでもどこでもインスピレーションを形にできる、現場対応型のポータブルユニットに凝縮されています。</p>'
                                     '<p>ポータブルかつプロフェッショナルなトーンの未来へようこそ。</p>')
    sec['settings']['layout'] = 'media-top'
    save('product.nano-cortex', head, d)
print('nano intro ok')

# ---- round 8 (Nov 16): 写真 opens on the front photo; サウンドを聴いて選ぶ goes straight to the plugin list ----
FRONT_FIRST = {'product.quad-cortex': 'qc-photo-1.webp,qc-photo-2.webp,qc-photo-3.webp,qc-photo-4.webp,qc-photo-5.webp',
               'product.quad-cortex-mini': 'mini-photo-2.webp,mini-photo-1.webp,mini-photo-3.webp,mini-photo-4.webp',
               'product.nano-cortex': 'nano-photo-1.webp,nano-photo-2.webp,nano-photo-3.webp,nano-photo-4.webp,nano-photo-5.webp'}
for name, photos in FRONT_FIRST.items():
    head, d = load(name)
    st = d['sections']['main']['settings']
    st['photo_assets'] = photos
    if name == 'product.quad-cortex': st['bundle_help_url'] = '/pages/quad-cortex-and-plugin-bundle#plugins'
    if name == 'product.quad-cortex-mini': st['bundle_help_url'] = '/pages/quad-cortex-mini-plugin#plugins'
    save(name, head, d)
print('round 8 ok')

# ---- round 9: long text runs across the page instead of a narrow column beside a small image ----
head, d = load('product.quad-cortex-mini')
k = d['sections'].get('rich_text_dzy9mb')
if k and '<p>classic' in k['settings'].get('body', ''):
    b = k['settings']['body']; k['settings']['body'] = b[:b.index('<p>classic')]
    k['settings']['layout'] = 'center'; k['settings']['image_url'] = ''
    insert_after(d, 'rich_text_dzy9mb', 'toolkit_stats', {'type': 'nd-stats', 'settings': {'heading': '', 'link_label': '全デバイスリスト', 'link_url': 'https://neuraldsp.com/device-list'},
        'blocks': {'s0': {'type': 'stat', 'settings': {'value': '90+', 'label': 'classic / modern / contemporary を網羅するアンプ・モデル'}},
                   's1': {'type': 'stat', 'settings': {'value': '100+', 'label': '完全なシグナルチェーンを組めるエフェクト＆ユーティリティ'}},
                   's2': {'type': 'stat', 'settings': {'value': '1000+', 'label': '柔軟なマイク配置に対応するキャビネット IR'}}},
        'block_order': ['s0', 's1', 's2']})
k = d['sections'].get('rich_text_krypv3')
if k and '<h2>' in k['settings'].get('body', ''):
    b = k['settings']['body']; k['settings']['body'] = b[:b.index('<h2>')]
    k['settings']['layout'] = 'media-top'
    insert_after(d, 'rich_text_krypv3', 'first_look', cols('', '', [(t, x) for t, x in MINI_HL], 4))
io = d['sections']['custom_liquid_tpwyqn']  # the four highlights now sit under 小さなボディ。大きなサウンド。 — not repeated in 入力と出力
for b in [b for b in io['block_order'] if b.startswith('hl_')]:
    io['blocks'].pop(b, None)
io['block_order'] = [b for b in io['block_order'] if not b.startswith('hl_')]
save('product.quad-cortex-mini', head, d)
print('round 9 ok')

# ---- round 10: QC rear panel = transparent photo + numbered markers (works on dark and white) ----
QC_IO_PINS = {'1': (9.2, 56), '2': (25.7, 33), '3': (37.8, 33), '4': (51.7, 59), '5': (43.9, 71), '6': (69.1, 65), '7': (82.6, 33), '8': (89.4, 74), '10': (43.9, 33)}
head, d = load('product.quad-cortex')
io = d['sections']['custom_liquid_tpwyqn']
io['settings'].update(image_url='', image_asset='qc-rear.webp', media_max=1100, show_numbers=True)
pins(io, QC_IO_PINS)
save('product.quad-cortex', head, d)
print('round 10 ok')

# ---- round 11: Black Friday hero item — follows Theme settings → Colours → campaign (switch + dates) ----
head, d = load('index')
q = d['sections']['qc3d']
if 'bf' not in q['blocks']:
    q['blocks']['bf'] = {'type': 'campaign', 'settings': {'enabled': True, 'follow_site': True, 'dock_label': 'BLACK FRIDAY', 'dock_sub': '期間限定',
        'model': 'qc', 'eyebrow': 'Neural DSP ／ 期間限定キャンペーン', 'title': 'BLACK\nFRIDAY', 'lead': '',
        'button_label': 'キャンペーン対象を見る', 'button_url': '/collections/all'}}
    q['block_order'].insert(0, 'bf')
save('index', head, d)
print('round 11 ok')

# ---- round 12: mini rear panel gets numbered markers too, so hovering a description lights its jack ----
MINI_IO_PINS = {'1': (2.2, 52), '2': (10.2, 70.7), '3': (18.7, 70.7), '4': (27.3, 70.7), '5': (37.0, 58.5), '6': (58.8, 41), '7': (75.9, 41),
                '8': (84.4, 41), '9': (91.7, 41), '10': (58.8, 70.7), '11': (75.9, 70.7), '12': (91.7, 70.7)}
head, d = load('product.quad-cortex-mini')
io = d['sections']['custom_liquid_tpwyqn']
io['settings']['show_numbers'] = True
pins(io, MINI_IO_PINS)
save('product.quad-cortex-mini', head, d)
print('round 12 ok')
