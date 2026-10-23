"""Convert the live neuraldsp.jp (Reformation theme) templates into JSON templates for the new ND theme.

Every live page is fetched as rendered HTML; each Shopify section is mapped onto one of the new theme's
sections with its Japanese text, links, images and videos carried over verbatim.

usage: python -I convert_live_to_theme.py <live_html_dir> <inventory.json> <theme_dir>
"""
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup, Comment, NavigableString, Tag

LIVE, INV, THEME = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
inv = json.load(open(INV))

SECTION_RE = re.compile(
    r'<(?:div|section)[^>]+id="shopify-section-([^"]+)"[^>]*>(.*?)(?=<(?:div|section)[^>]+id="shopify-section-|</main>)', re.S)

PLUGIN_ART = {
    'gojira': 'https://cdn.shopify.com/s/files/1/0503/9089/2702/files/a-gojira-x-product-card_cfb2c9e8-e68e-493b-b7ff-4ab47441172f.png',
    'cory wong': 'https://cdn.shopify.com/s/files/1/0747/8109/8202/files/cwx-standalone.png?v=1761285119',
    'plini': 'https://cdn.shopify.com/s/files/1/0503/9089/2702/files/plinix-product-card.png',
    'nameless': 'https://cdn.shopify.com/s/files/1/0503/9089/2702/files/nameless-x-product-card_3.png',
    'nolly': 'https://cdn.shopify.com/s/files/1/0503/9089/2702/files/nolly-x-product-card.png',
    'parallax': 'https://cdn.shopify.com/s/files/1/0503/9089/2702/files/parallax-x-product-card.png',
    'soldano': 'https://cdn.shopify.com/s/files/1/0503/9089/2702/files/soldano-slo-100-x-product-card.png',
    'john mayer': 'https://cdn.shopify.com/s/files/1/0503/9089/2702/files/archetype-john-mayer-x-product-card_3cfebe92-ef46-421f-a63d-ad279b159d9e.png',
    'misha': 'https://cdn.shopify.com/s/files/1/0503/9089/2702/files/archetype-misha-mansoor-x-product-card.png',
    'rabea': 'https://cdn.shopify.com/s/files/1/0503/9089/2702/files/archetype-rabea-x-product-card.png',
    'tim henson': 'https://cdn.shopify.com/s/files/1/0503/9089/2702/files/archetype-tim-henson-x-product-card.png',
    'petrucci': 'https://cdn.shopify.com/s/files/1/0503/9089/2702/files/archetype-petrucci-x-product-card.png',
}
LEGAL = {'page-privacy-policy', 'page-terms-of-service', 'page-refund-policy', 'page-cortex-cloud-terms-of-use', 'page-hardware-warranty-policy', 'page-legal-notice'}
ADDONS = ['plugin-addon-' + h for h in ['archetype-john-mayer-x', 'archetype-misha-mansoor-x', 'archetype-tim-henson-x', 'archetype-rabea-x', 'archetype-petrucci-x', 'archetype-gojira-x', 'fortin-nameless-suite-x', 'archetype-nolly-x', 'parallax-x', 'archetype-plini-x', 'soldano-slo-100-x', 'archetype-cory-wong-x']]  # plugin-addons-import.csv
QC_BUNDLES = ['quadcortex-plugin-bundle-' + s for s in ['joh', 'mis', 'tim', 'rab', 'pet', 'goj', 'for', 'nol', 'par', 'pli', 'slo', 'cor']]
MINI_BUNDLES = ['quadcortex-mini-plugin-bundle-' + s for s in ['joh', 'mis', 'tim', 'rab', 'pet', 'goj', 'for', 'nol', 'par', 'pli', 'slo', 'cor']]

ALLOWED = {'p', 'br', 'strong', 'b', 'em', 'i', 'u', 'ul', 'ol', 'li', 'a', 'h2', 'h3', 'h4', 'h5', 'table', 'thead',
           'tbody', 'tr', 'th', 'td', 'img', 'blockquote', 'hr', 'small', 'sup', 'sub', 'figure', 'figcaption', 'video', 'source', 'iframe'}
UNWRAP = {'span', 'div', 'section', 'article', 'font', 'center', 'collapsible-row', 'picture', 'label', 'header', 'footer', 'main', 'nav'}
DROP = {'script', 'style', 'svg', 'noscript', 'form', 'input', 'button', 'select', 'textarea', 'link', 'meta', 'dialog'}


def txt(el):
    if el is None:
        return ''
    return re.sub(r'\s+', ' ', el.get_text(' ', strip=True)).strip()


def full_url(u):
    if not u:
        return ''
    u = u.strip()
    if u.startswith('//'):
        u = 'https:' + u
    u = re.sub(r'([?&])width=\d+&?', r'\1', u).rstrip('?&')
    return u


def link_url(u):
    if not u:
        return ''
    u = u.strip()
    u = re.sub(r'^https?://(www\.)?neuraldsp\.jp(?=/|$)', '', u) or '/'
    return u


def img_src(img):
    for a in ('data-src', 'src'):
        v = img.get(a)
        if v and 'width=20' not in v and not v.startswith('data:'):
            return full_url(v)
    ss = img.get('data-srcset') or img.get('srcset') or ''
    if ss:
        return full_url(ss.split(',')[-1].strip().split(' ')[0])
    return full_url(img.get('src', ''))


def clean(node):
    """Sanitise a fragment to the tags our prose styles handle; keep text verbatim."""
    soup = BeautifulSoup(str(node), 'html.parser')
    for c in soup.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()
    for t in soup.find_all(list(DROP)):
        t.decompose()
    for t in soup.find_all(True):
        if t.name in ('h1',):
            t.name = 'h2'
        if t.name in ('h6',):
            t.name = 'h5'
        if t.name in UNWRAP or t.name not in ALLOWED | UNWRAP:
            # keep block structure: a div with only inline content becomes a paragraph
            if t.name == 'div' and t.find(['p', 'ul', 'ol', 'table', 'h2', 'h3', 'h4', 'div', 'figure', 'video', 'iframe', 'img']) is None and txt(t):
                t.name = 'p'
                t.attrs = {}
                continue
            t.unwrap()
            continue
        keep = {}
        if t.name == 'a' and t.get('href'):
            keep['href'] = link_url(t['href'])
            if keep['href'].startswith('http'):
                keep['target'] = '_blank'
                keep['rel'] = 'noopener'
        if t.name == 'img':
            keep['src'] = img_src(t)
            keep['alt'] = t.get('alt', '')
            keep['loading'] = 'lazy'
        if t.name in ('td', 'th'):
            for a in ('colspan', 'rowspan'):
                if t.get(a):
                    keep[a] = t[a]
        if t.name in ('video', 'source', 'iframe'):
            for a in ('src', 'type', 'autoplay', 'muted', 'loop', 'playsinline', 'controls', 'allow', 'allowfullscreen'):
                if t.get(a) is not None:
                    keep[a] = t[a] if t[a] != '' else ''
        t.attrs = keep
    out = str(soup)
    out = re.sub(r'\s*\n\s*', ' ', out)
    blk = r'(?:p|h[2-5]|li|ul|ol|table|thead|tbody|tr|td|th|br|figure|figcaption|blockquote|hr)'
    out = re.sub(r'\s*(</?' + blk + r'(?=[\s/>])[^>]*>)\s*', r'\1', out)
    out = re.sub(r'<p>\s*(?:&nbsp;|　)?\s*</p>', '', out)
    return out.strip()


def sections_of(path):
    fn = LIVE / ('p_' + re.sub(r'[^a-z0-9]+', '_', path.lower()).strip('_') + '.html')
    if path == '/':
        fn = LIVE / 'home.html'
    h = fn.read_text(encoding='utf-8', errors='ignore')
    out = []
    for sid, body in SECTION_RE.findall(h):
        if 'sections--' in sid:
            continue
        out.append((sid.split('__')[-1], BeautifulSoup(body, 'html.parser')))
    return out


# ---------------------------------------------------------------- converters
def first_heading(b, levels=('h1', 'h2', 'h3', 'h4')):
    for h in b.find_all(list(levels)):
        if txt(h):
            return h
    return None


def buttonish_links(b):
    res = []
    for a in b.find_all('a'):
        label = txt(a)
        if not label or not a.get('href'):
            continue
        cls = ' '.join(a.get('class', []))
        if 'button' in cls or 'btn' in cls or a.find_parent(['strong']) or a.find('strong') or label in ('詳しく見る', '詳細を見る', 'ダウンロード', 'アカウントを登録', '全デバイスリスト') or label.startswith('▶'):
            res.append((label, link_url(a['href'])))
    return res


def first_media(b):
    v = b.find('video')
    if v:
        src = v.get('src') or (v.find('source') or {}).get('src')
        if src:
            return {'video_url': full_url(src)}
    for f in b.find_all('iframe'):
        m = re.search(r'(?:youtube(?:-nocookie)?\.com/embed/)([\w-]{11})', f.get('src', ''))
        if m:
            return {'youtube_id': m.group(1)}
    for el in b.find_all(style=True):
        m = re.search(r"background-image:\s*url\(['\"]?([^'\")]+)", el['style'])
        if m:
            return {'image_url': full_url(m.group(1))}
    for img in b.find_all('img'):
        s = img_src(img)
        if s and 'separator' in s:
            continue
        if s and ('/files/' in s or 'cdn.shopify.com' in s):
            return {'image_url': s, 'image_alt': img.get('alt', '')}
    return {}


def body_without(b, remove_nodes):
    soup = BeautifulSoup(str(b), 'html.parser')
    for t in soup.find_all(list(DROP)):
        t.decompose()
    for sel in remove_nodes:
        for t in soup.select(sel):
            t.decompose()
    return soup


def to_feature(b, layout='media-right', heading_levels=('h1', 'h2', 'h3', 'h4')):
    s = {'layout': layout}
    media = first_media(b)
    s.update(media)
    soup = body_without(b, ['img', 'video', 'iframe', 'figure'])
    h = first_heading(soup, heading_levels)
    if h:
        s['heading'] = txt(h)
        h.decompose()
    links = buttonish_links(soup)
    for i, (label, href) in enumerate(links[:2]):
        key = 'button' if i == 0 else 'button2'
        s[key + '_label'] = label
        s[key + '_url'] = href
    for a in soup.find_all('a'):
        if (txt(a), link_url(a.get('href', ''))) in links[:2]:
            # remove the whole paragraph if the link is its only content
            p = a.find_parent('p')
            (p if p is not None and txt(p) == txt(a) else a).decompose()
    body = clean(soup)
    if body:
        s['body'] = body
    if not media:
        s['layout'] = 'center'
    return {'type': 'nd-feature', 'settings': s}


def conv_hero(b):
    s = {'show_buy': bool(b.select('.hero-buy-now-button, [data-variant-id]')) or '購入する' in txt(b)}
    v = b.find('video')
    if v:
        src = v.get('src') or (v.find('source') or {}).get('src')
        if src:
            s['video_url'] = full_url(src)
    img = b.find('img')
    if img:
        s['image_url'] = img_src(img)
    h = first_heading(b)
    if h:
        s['title'] = txt(h)
    subs = [txt(p) for p in b.find_all('p') if txt(p)]
    if subs:
        s['subtitle'] = '\n'.join(subs)
    for a in b.find_all('a'):
        if 'youtube' in a.get('href', '') or txt(a).startswith('▶'):
            s['film_url'] = a['href']
            s['film_label'] = txt(a)
        elif txt(a) and txt(a) != '購入する' and not s.get('button_label'):
            s['button_label'] = txt(a)
            s['button_url'] = link_url(a['href'])
    # labels like "Windows / macOS" shown as plain spans
    extra = [txt(x) for x in b.find_all(['span', 'li']) if txt(x) in ('Windows', 'macOS')]
    if extra and 'subtitle' in s:
        s['subtitle'] += '\n' + ' / '.join(dict.fromkeys(extra))
    return {'type': 'nd-hero', 'settings': s}


def conv_awards(b):
    blocks = {}
    for i, item in enumerate(b.select('.nd-accoladeStrip__item')):
        lines = [txt(p) for p in item.select('p')]
        blocks[f'award_{i}'] = {'type': 'award', 'settings': {'image_url': img_src(item.find('img')), 'line1': lines[0] if lines else '', 'line2': lines[1] if len(lines) > 1 else ''}}
    return {'type': 'nd-awards', 'blocks': blocks, 'block_order': list(blocks)}


def conv_faq(b):
    head = b.select_one('.section-header--content') or b
    h = first_heading(head)
    sub = txt(head.select_one('.rte')) if head.select_one('.rte') else ''
    s = {'eyebrow': '', 'heading': ''}
    if h and sub:
        s['eyebrow'], s['heading'] = txt(h), sub
    elif h:
        s['heading'] = txt(h)
    blocks = {}
    for i, d in enumerate(b.find_all('details')):
        q = txt(d.find('summary'))
        content = d.select_one('.accordion__content, .collapsible__content') or d
        a = clean(content) if content is not d else ''
        blocks[f'qa_{i}'] = {'type': 'qa', 'settings': {'question': q, 'answer': a}}
    return {'type': 'nd-faq', 'settings': s, 'blocks': blocks, 'block_order': list(blocks)}


def conv_columns(b):
    head = b.select_one('.section-header--content')
    s = {'columns': 3}
    if head:
        h = first_heading(head)
        if h and txt(h):
            s['heading'] = txt(h)
        rte = head.select_one('.rte')
        if rte and txt(rte):
            s['body'] = clean(rte)
    cols = b.select('.multicolumn__column') or b.select('[class*="column"]')
    blocks = {}
    for i, c in enumerate(cols):
        st = {}
        img = c.find('img')
        if img:
            st['image_url'] = img_src(img)
        h = c.find(['h3', 'h4', 'h2'])
        if h:
            st['title'] = txt(h)
        rte = c.select_one('.rte')
        if rte:
            links = rte.find_all('a')
            if len(links) == 1 and txt(rte) == txt(links[0]):
                st['link_label'], st['link_url'] = txt(links[0]), link_url(links[0].get('href'))
            elif txt(rte):
                st['text'] = clean(rte)
        if not st.get('link_url'):
            a = c.find('a', href=True)
            if a:
                st['link_url'] = link_url(a['href'])
        if st:
            blocks[f'column_{i}'] = {'type': 'column', 'settings': st}
    s['columns'] = max(1, min(4, len(blocks) if len(blocks) in (2, 3, 4) else 3))
    return {'type': 'nd-columns', 'settings': s, 'blocks': blocks, 'block_order': list(blocks)}


def conv_stats(b):
    lines = [l for l in (x.strip() for x in b.get_text('\n').split('\n')) if l]
    blocks, heading, link = {}, [], None
    i = 0
    while i < len(lines):
        if re.fullmatch(r'[\d,]+\+?', lines[i]) and i + 1 < len(lines):
            blocks[f'stat_{len(blocks)}'] = {'type': 'stat', 'settings': {'value': lines[i], 'label': lines[i + 1]}}
            i += 2
            continue
        if not blocks:
            heading.append(lines[i])
        i += 1
    a = b.find('a', href=True)
    s = {'heading': '\n'.join(heading)}
    if a:
        s['link_label'], s['link_url'] = txt(a), link_url(a['href'])
    return {'type': 'nd-stats', 'settings': s, 'blocks': blocks, 'block_order': list(blocks)}


def conv_numbered(b):
    soup = body_without(b, [])
    media = first_media(b)
    lines = [l for l in (x.strip() for x in soup.get_text('\n').split('\n')) if l]
    heading, sub, items = '', '', []
    i = 0
    while i < len(lines) and not re.fullmatch(r'\d{1,2}', lines[i]):
        if not heading:
            heading = lines[i]
        else:
            sub = (sub + ' ' + lines[i]).strip()
        i += 1
    while i < len(lines):
        if re.fullmatch(r'\d{1,2}', lines[i]):
            items.append({'number': lines[i], 'lines': []})
        elif items:
            items[-1]['lines'].append(lines[i])
        i += 1
    blocks = {}
    for k, it in enumerate(items):
        ls = it['lines']
        title, rest = '', ls
        if ls and (ls[0].endswith('：') or ls[0].endswith(':')) :
            title, rest = ls[0].rstrip('：:'), ls[1:]
        elif ls and '：' in ls[0] and len(ls) == 1:
            title, rest = ls[0].split('：', 1)[0], [ls[0].split('：', 1)[1].strip()]
        elif ls and ':' in ls[0] and len(ls[0].split(':', 1)[0]) < 40:
            title, rest = ls[0].split(':', 1)[0], [ls[0].split(':', 1)[1].strip()] + ls[1:]
        elif ls:
            title, rest = ls[0], ls[1:]
        text = ''.join(f'<p>{r}</p>' for r in [' '.join(rest).strip()] if r)
        blocks[f'item_{k}'] = {'type': 'item', 'settings': {'number': it['number'], 'title': title, 'text': text}}
    s = {'heading': heading, 'subheading': sub}
    if media.get('image_url'):
        s['image_url'] = media['image_url']
    return {'type': 'nd-numbered', 'settings': s, 'blocks': blocks, 'block_order': list(blocks)}


def conv_specs(b):
    blocks = {}
    modal = b.select_one('.modal-body, .modal-content, [id*=modal] .modal-body')
    modal_html = clean(modal) if modal else ''
    for a in b.find_all('a', href=True):
        if a.find_parent(class_=re.compile('grid-item|responsive-grid')) is not None or 'grid-item' in ' '.join(a.get('class', [])):
            continue
        if txt(a):
            st = {'label': txt(a.find(['h3', 'h2'])) or txt(a), 'url': link_url(a['href'])}
            st.update({k: v for k, v in first_media(a).items() if k in ('image_url', 'video_url')})
            blocks[f'card_{len(blocks)}'] = {'type': 'card', 'settings': st}
    for el in b.select('.grid-item, .responsive-grid > *, [class*="card"]'):
        label = txt(el.find(['h3', 'h2', 'span']))
        if not label:
            continue
        st = {'label': label}
        m = first_media(el)
        st.update({k: v for k, v in m.items() if k in ('image_url', 'video_url')})
        if el.name == 'a' and el.get('href'):
            st['url'] = link_url(el['href'])
        elif el.get('id') == 'open-modal' or 'modal' in ' '.join(el.get('class', [])) or label == 'ハードウェア仕様':
            st['modal_html'] = modal_html
        blocks[f'card_{len(blocks)}'] = {'type': 'card', 'settings': st}
    if not any(bk['settings'].get('modal_html') for bk in blocks.values()) and modal_html:
        blocks[f'card_{len(blocks)}'] = {'type': 'card', 'settings': {'label': 'ハードウェア仕様', 'modal_html': modal_html}}
    return {'type': 'nd-specs', 'blocks': blocks, 'block_order': list(blocks)}


def conv_trial(b):
    title = b.select_one('.ndsp-modal__title')
    img = b.select_one('.ndsp-modal__hero')
    return {'type': 'nd-trial', 'settings': {
        'title': re.sub(r'\s*\n\s*', '\n', title.get_text('\n', strip=True)) if title else '',
        'image_url': img_src(img) if img else '',
        'subline': txt(b.select_one('.ndsp-modal__subline')) or '14日間無料体験',
        'description': txt(b.select_one('.ndsp-modal__desc')),
        'placeholder': (b.select_one('input[type=email]') or {}).get('placeholder', 'メールアドレスを入力する'),
        'submit': txt(b.select_one('.ndsp-submit')) or '無料体験する',
    }}


def conv_newsletter(b, style):
    s = {'style': style}
    h = first_heading(b)
    if h:
        s['heading'] = txt(h)
    paras = []
    for p in b.find_all('p'):
        if p.find_parent('form') is None and txt(p):
            paras.append(p)
    if paras:
        s['body'] = ''.join(clean(p) for p in paras)
    tags = b.select_one('input[name="contact[tags]"]')
    if tags:
        s['tags'] = tags.get('value', '')
    btn = b.select_one('form button, form [type=submit]')
    if btn and txt(btn):
        s['submit'] = txt(btn)
    if style == 'popup':
        trig = [txt(x) for x in b.find_all(['button', 'a', 'h2', 'h3']) if 'メルマガに登録' in txt(x)]
        s['popup_button'] = trig[0] if trig else 'メルマガに登録する'
        if s.get('heading') == s.get('popup_button'):
            pass
    return {'type': 'nd-newsletter', 'settings': s}


def conv_campaign(b):
    img = b.find('img')
    src = b.find('source')
    a = b.find('a', href=True)
    return {'type': 'nd-campaign', 'settings': {
        'image_url': img_src(img) if img else '', 'mobile_image_url': full_url(src.get('srcset', '')) if src else '',
        'alt': img.get('alt', '') if img else '', 'url': link_url(a['href']) if a else '', 'button_label': txt(a) if a else ''}}


def conv_video_grid(b):
    blocks = {}
    for tile in b.select('.left, .right-top-container, .right-bottom-container'):
        st = {}
        v = tile.find('video')
        if v and v.get('src'):
            st['video_url'] = full_url(v['src'])
        img = tile.find('img')
        if img and not st:
            st['image_url'] = img_src(img)
        st['title'] = txt(tile.find(['h1', 'h2']))
        st['text'] = txt(tile.find('p'))
        a = tile.find('a', href=True)
        if a:
            st['link_label'], st['link_url'] = txt(a), link_url(a['href'])
        blocks[f'tile_{len(blocks)}'] = {'type': 'tile', 'settings': st}
    return {'type': 'nd-video-grid', 'blocks': blocks, 'block_order': list(blocks)}


def conv_video(b):
    m = first_media(b)
    h = first_heading(b)
    s = {}
    if 'youtube_id' in m:
        s['youtube_id'] = m['youtube_id']
    elif 'video_url' in m:
        s['video_url'] = m['video_url']
    else:
        yt = re.search(r'(?:youtube(?:-nocookie)?\.com/(?:embed/|watch\?v=)|youtu\.be/)([\w-]{11})', str(b))
        if yt:
            s['youtube_id'] = yt.group(1)
    if h:
        s['heading'] = txt(h)
    return {'type': 'nd-video', 'settings': s} if s.get('youtube_id') or s.get('video_url') else None


def conv_html(b, heading=True, width='narrow'):
    soup = body_without(b, [])
    s = {'width': width}
    if heading:
        h = first_heading(soup, ('h1', 'h2'))
        if h and len(txt(h)) < 60:
            s['heading'] = txt(h)
            h.decompose()
    s['html'] = clean(soup)
    return {'type': 'nd-html', 'settings': s} if txt(soup) or soup.find(['img', 'video', 'iframe']) else None


def is_numbered(b):
    lines = [l for l in (x.strip() for x in b.get_text('\n').split('\n')) if l]
    nums = [l for l in lines if re.fullmatch(r'\d{1,2}', l)]
    return len(nums) >= 3 and nums[:3] == ['1', '2', '3']


def convert_section(key, b, page_type, side):
    text = txt(b)
    k = key.lower()
    if k.startswith('spacer') or k.startswith('main-collection') or k == 'product-grid':
        return None
    if k == 'main-product':
        return 'MAIN_PRODUCT'
    if k == 'main' or k == 'main-page':
        return {'type': 'main-page', 'settings': {}}
    if 'newsletter_popup' in k:
        return conv_newsletter(b, 'popup')
    if k.startswith('email_signup'):
        return conv_newsletter(b, 'inline')
    if k.startswith('featured_blog'):
        h = first_heading(b)
        return {'type': 'nd-blog-posts', 'settings': {'blog': 'news', 'heading': txt(h) if h else 'Latest News'}}
    if 'stars:' in text and '%' in text:
        return {'type': 'apps', 'settings': {}, 'blocks': {}, 'block_order': [], 'note': 'reviews app'}
    if b.select('.nd-accoladeStrip'):
        return conv_awards(b)
    if b.select('.ndsp-modal'):
        return conv_trial(b)
    if b.select('.campaign-mv'):
        return conv_campaign(b)
    if b.select('.video-grid'):
        return conv_video_grid(b)
    if k.startswith('collapsible_content'):
        return conv_faq(b)
    if k.startswith('multicolumn'):
        return conv_columns(b)
    if (b.select('#open-modal, .modal') and 'ハードウェア仕様' in text) or k in ('custom_liquid_ewjyyk', 'custom_liquid_wu4vmx'):
        return conv_specs(b)
    if (b.find('video') or b.find('img')) and (b.select('.hero-buy-now-button') or '▶ フル動画を見る' in text) and len(text) < 260:
        return conv_hero(b)
    if re.search(r'\b\d{2,4}\+', text) and 'アンプ' in text and len(text) < 200:
        return conv_stats(b)
    if is_numbered(b):
        return conv_numbered(b)
    if k.startswith('video') or k.endswith('video_yt'):
        return conv_video(b)
    if k.startswith('background_video'):
        m = first_media(b)
        return {'type': 'nd-feature', 'settings': {'layout': 'media', **m}} if m else None
    if k.startswith('single_image') or (not text and (b.find('img') or b.find('video'))):
        m = first_media(b)
        if not m:
            return None
        a = b.find('a', href=True)
        s = {'layout': 'media', **m}
        srcs = [img_src(i) for i in b.find_all('img')]
        pc = next((u for u in srcs if re.search(r'[-_](pc|desktop|dt)\b', u)), None)
        sp = next((u for u in srcs if re.search(r'[-_](sp|mobile|mb)\b', u)), None)
        if pc and sp:
            s['image_url'], s['mobile_image_url'] = pc, sp
        if a:
            s['link_url'] = link_url(a['href'])
        return {'type': 'nd-feature', 'settings': s}
    if not text:
        return None
    if k.startswith('image_with_text') or k.endswith('two_col_overview'):
        return to_feature(b, side)
    if k.startswith('rich_text'):
        if page_type in LEGAL or len(text) > 1500 or b.find('table'):
            return conv_html(b, width='wide' if b.find('table') else 'narrow')
        return to_feature(b, side)
    # custom liquid and anything else
    if b.find('table') or len(text) > 1500:
        return conv_html(b, width='wide')
    return to_feature(b, side)


# ---------------------------------------------------------------- main product settings per template
def main_product_settings(tpl, path):
    s = {'show_bundles': False, 'show_accessories': False, 'show_trial': False}
    if tpl == 'product-quad-cortex':
        s.update(show_bundles=True, bundles=QC_BUNDLES, addons=ADDONS, show_accessories=True, accessories=['gig-case', 'quad-cortex-psu'])
    elif tpl == 'product-quad-cortex-mini':
        s.update(show_bundles=True, bundles=MINI_BUNDLES, addons=ADDONS, show_accessories=True, accessories=['quad-cortex-psu'])
    elif tpl == 'product-nano-cortex':
        s.update(show_accessories=True, accessories=['quad-cortex-psu'])
    elif 'bundle' in path:
        s.update(show_trial=True)
    return s


def build(path, info):
    tpl = info['template']
    sections, order = {}, []
    side = 'media-right'
    has_trial = False
    for i, (key, b) in enumerate(sections_of(path)):
        conv = convert_section(key, b, tpl, side)
        if conv is None:
            continue
        sid = re.sub(r'[^a-z0-9_]', '_', key.lower())[:40] or f's{i}'
        if conv == 'MAIN_PRODUCT':
            conv = {'type': 'main-product', 'settings': main_product_settings(tpl, path), 'blocks': {}, 'block_order': []}
            sid = 'main'
        if conv.get('type') == 'nd-trial':
            has_trial = True
        if conv.get('type') == 'nd-feature' and conv['settings'].get('layout') in ('media-left', 'media-right'):
            side = 'media-left' if side == 'media-right' else 'media-right'
        conv.pop('note', None)
        while sid in sections:
            sid += '_x'
        sections[sid] = conv
        order.append(sid)
    if 'main' in sections and has_trial:
        sections['main']['settings']['show_trial'] = True
    # The live trial pop-up was copied from the Cory Wong page onto every bundle page; use this page's plugin.
    hero = next((v for v in sections.values() if v.get('type') == 'nd-hero'), None)
    trial = next((v for v in sections.values() if v.get('type') == 'nd-trial'), None)
    if hero and trial and ' + ' in hero['settings'].get('title', ''):
        plugin = hero['settings']['title'].split(' + ', 1)[1].strip()
        trial['settings']['title'] = f'{plugin}を\nダウンロードする'
        art = next((u for k, u in PLUGIN_ART.items() if k in plugin.lower()), None)
        if art:
            trial['settings']['image_url'] = art
    return {'sections': sections, 'order': order}


def build_contact():
    return {'sections': {'main': {'type': 'main-page', 'settings': {}}, 'form': {'type': 'contact-form', 'settings': {}}}, 'order': ['main', 'form']}


VIEWERS = {
    'product-quad-cortex': {'model': 'qc', 'heading': 'Quad Cortex®', 'view_labels': '全体,タッチスクリーン,フットスイッチ,入力と出力,正面',
        'view_captions': '世界最高峰のフロア型アンプモデラー|巨大な 7 インチタッチスクリーンを搭載した Quad Cortex は、驚くほど直感的に操作できます。|11基のステンレス製ストンプ＋ロータリーアクチュエーター：スイッチ操作と回転制御が可能。|入力と出力|Quad Cortex®'},
    'product-quad-cortex-mini': {'model': 'mini', 'heading': 'Quad Cortex mini', 'view_labels': '全体,上面,入力と出力,正面',
        'view_captions': '妥協ゼロ。ただ、コンパクト。|7インチのマルチタッチ・ディスプレイと、4つのステンレス製ロータリーフットスイッチ|入力と出力：シンプルな接続。自由なセットアップ。|小さなボディ。大きなサウンド。'},
    'product-nano-cortex': {'model': 'nano', 'heading': 'Nano Cortex', 'view_labels': '全体,上面,入力と出力,側面',
        'view_captions': 'あなたのトーン。あなたのリグ。どこでもプレイ|コントロール|入力と出力|Nano Cortexは、2つのスタンダードなストンプボックスペダルを並べた幅と同じで、重さはわずか620g（1.36lbs）。'},
}


# 3D story heroes (same experience as the homepage Quad Cortex); copy is the live page's own wording
LIST = lambda items: '<ul class="chapter__list">' + ''.join(f'<li><b>{a}</b>{b}</li>' for a, b in items) + '</ul>'
STORIES = {
    'product-quad-cortex': {'model': 'qc', 'c0_eyebrow': 'Neural DSP ／ Quad Cortex®', 'c0_title': 'Quad\nCortex', 'c0_lead': '世界最高峰のフロア型アンプモデラー',
        'c0_body': 'Quad Cortex® は、Neural DSP が開発した最先端のフロア型アンプモデラー & マルチエフェクターです。',
        'c1_label': 'タッチスクリーン', 'c1_title': 'モデラーの新たな\n可能性を切り拓く', 'c1_body': '<p>巨大な 7 インチタッチスクリーンを搭載した Quad Cortex は、驚くほど直感的に操作できます。どれほど複雑なシグナルパスも、手間なく構築可能です。</p>',
        'c2_label': 'フットスイッチ', 'c2_title': '11基のステンレス製\nストンプ＋ロータリー\nアクチュエーター', 'c2_body': '<p>スイッチ操作と回転制御が可能。従来のフットスイッチ＆ノブのような操作感ながら、壊れにくい設計。</p>',
        'c3_label': '入力と出力', 'c3_title': '入力と出力', 'c3_body': LIST([('デュアルコンボ入力', 'TS、TRS、XLR対応、可変インピーダンス＆レベルコントロール内蔵、マイクプリアンプ搭載、ファンタム電源対応。'), ('デュアルエフェクトループ', '外部のモノラル/ステレオエフェクトをシグナルチェーンに組み込むのに最適。'), ('XLR 出力ジャック', '2つのモノラル・バランスXLR出力ジャック。'), ('USB', '超低遅延オーディオ伝送、ファームウェア更新、MIDI通信などに対応。')]),
        'c4_label': '選ぶ', 'c4_body': '7インチのタッチディスプレイと圧倒的な処理能力により、自由かつ直感的なトーン設計を実現します。'},
    'product-quad-cortex-mini': {'model': 'mini', 'c0_eyebrow': 'Neural DSP ／ Quad Cortex mini', 'c0_title': 'Quad Cortex\nmini', 'c0_lead': '妥協ゼロ。ただ、コンパクト。',
        'c0_body': 'Quad Cortex mini は、Neural DSP が誇るフラッグシップ Quad Cortex の体験を、コンパクトで使いやすいフォーマットに凝縮した次世代フロア型アンプモデラー＆マルチエフェクターです。',
        'c1_label': 'The Grid', 'c1_title': 'リグ全体を\nひと目で把握。', 'c1_body': '<p>The Grid は、Quad Cortex mini の中核となるビジュアル・ワークスペースです。複雑なセットアップでも読みやすく。シンプルなアイデアはそのままシンプルに。</p>',
        'c2_label': 'フットスイッチ', 'c2_title': 'タッチスクリーン &\nロータリーフットスイッチ', 'c2_body': '<p>7インチのマルチタッチ・ディスプレイと、4つのステンレス製ロータリーフットスイッチを組み合わせることで、指先でも足元でも、反応の良い直感的な操作が可能です。</p>',
        'c3_label': '入力と出力', 'c3_title': 'シンプルな接続。\n自由なセットアップ。', 'c3_body': LIST([('INPUT 2 / CAPTURE INPUT', '専用のレベルコントロールとファンタム電源を備えた、コンボXLR／1/4インチ TRS入力。'), ('DUAL EFFECTS LOOPS', 'SEND 1/2 および RETURN 1/2 は、それぞれ 1/4インチ TRS 端子を共有しています。'), ('XLR OUTPUTS', '2系統のモノラル・バランスXLR出力。'), ('USB-C', 'マルチチャンネル（8イン／8アウト）USBオーディオインターフェースとして使用可能。')]),
        'c4_label': '選ぶ', 'c4_body': '小さなボディ。大きなサウンド。'},
    'product-nano-cortex': {'model': 'nano', 'c0_eyebrow': 'Neural DSP ／ Nano Cortex®', 'c0_title': 'Nano\nCortex', 'c0_lead': 'あなたのトーン。あなたのリグ。どこでもプレイ',
        'c0_body': 'Nano Cortex® は、Neural DSP が開発した手のひらサイズのデジタルアンプ & エフェクトプロセッサーです。',
        'c1_label': 'コントロール', 'c1_title': '手のひらに収まる、\n超強力なリグ', 'c1_body': LIST([('Bass, Mid, Treble', 'トーンを調整するためのコントロール。'), ('Gain', 'Neural Captureに適用されるサチュレーションのレベルを調整します。'), ('Capture', 'Neural Captureプロセスを開始します。')]),
        'c2_label': 'フットスイッチ', 'c2_title': '軽快に移動、\n圧倒的なサウンド', 'c2_body': '<p>Nano Cortexは、2つのスタンダードなストンプボックスペダルを並べた幅と同じで、重さはわずか620g（1.36lbs）。ギグバッグやバックパックに簡単に収まります。</p>',
        'c3_label': '入力と出力', 'c3_title': '入力と出力', 'c3_body': LIST([('1/4" instrument input', 'ギターやベース用。'), ('Dual 1/4" TRS outputs', 'スタジオモニター、PAシステム、FRFRキャビネット用のステレオ出力。'), ('USB-C', '録音や電源供給に対応。'), ('Capture input (XLR & TS)', 'Neural Captureを作成するための入力端子。')]),
        'c4_label': '選ぶ', 'c4_body': '300種類の高品質IR、25種類のプリセットキャプチャーを搭載。'},
}
ACC_HEROES = {
    'product-gig-case': {'title': 'Gig Case', 'subtitle': 'Neural DSP Quad Cortex 専用\nQuad Cortexをしっかりと保護するために特別に設計されています。精密成形された型で、Quad Cortexをしっかりと固定し、衝撃や天候から守ります。', 'asset_image': 'gigcase-hero.webp'},
    'product-psu': {'title': '電源アダプター（PSU）', 'subtitle': 'Quad Cortex用電源アダプターです。Nano Cortex・Quad Cortex Miniでもご使用いただけます。', 'asset_image': 'psu-hero.webp'},
}


def _plain(html):
    return re.sub(r'\s+', ' ', BeautifulSoup(html or '', 'html.parser').get_text(' ', strip=True)).strip()


def add_story(tpl, data):
    """Hardware + bundle pages open on the buy section with the 3D model (same camera moves as the homepage)."""
    st = STORIES.get(tpl)
    main = data['sections'].get('main')
    if st and main:
        hero = next((data['sections'][k] for k in data['order'] if data['sections'][k]['type'] == 'nd-hero'), None)
        if hero and hero['settings'].get('film_url'):
            st = {**st, 'film_url': hero['settings']['film_url']}
        # drop the old video hero and photo-only sections above the buy box: the 3D sits beside the buy panel now
        pre = data['order'][:data['order'].index('main')]
        for k in pre:
            if data['sections'][k]['type'] in ('nd-hero', 'nd-feature'):
                data['order'].remove(k); del data['sections'][k]
        labels = ['全体', st['c1_label'], st['c2_label'], st['c3_label'], '正面']
        titles = [st['c0_lead'], st['c1_title'].replace('\n', ''), st['c2_title'].replace('\n', ''), st['c3_title'].replace('\n', ''), st['c4_body']]
        caps = [st['c0_body'], _plain(st['c1_body']), _plain(st['c2_body']), _plain(st['c3_body'])[:120], '']
        titles = [t.replace('&\n', '& ').replace('\n', '') for t in titles]
        film = next((data['sections'][k]['settings'] for k in pre if k in data['sections'] and data['sections'][k]['type'] == 'nd-hero'), {})
        main['settings'].update(media_mode='3d', model=st['model'], view_labels=','.join(labels), view_titles='|'.join(titles), view_captions='|'.join(caps))
        if st.get('film_url'):
            main['settings'].update(film_url=st['film_url'], film_label='▶ フル動画を見る')
        # buy section first
        data['order'].remove('main'); data['order'].insert(0, 'main')
    elif main and ('quadcortex' in tpl or 'quad-cortex-mini-' in tpl or 'archetype' in tpl):
        model = 'mini' if 'mini' in tpl else 'qc'
        main['settings'].update(media_mode='3d', model=model, view_labels='全体,タッチスクリーン,フットスイッチ,入力と出力,正面', view_titles='', view_captions='')
    acc = ACC_HEROES.get(tpl)
    if acc:
        pre = [k for k in data['order'][:data['order'].index('main')]]
        for k in pre:
            del data['sections'][k]
        data['order'] = [k for k in data['order'] if k not in pre]
        data['sections']['hero'] = {'type': 'nd-hero', 'settings': {**acc, 'show_buy': True, 'buy_label': '購入する', 'overlay': 0, 'button_label': '詳しく見る', 'button_url': '#buy'}}
        data['order'].insert(0, 'hero')


def add_viewer(tpl, data):
    v = VIEWERS.get(tpl)
    if not v or 'main' not in data['order']:
        return
    data['sections']['viewer_3d'] = {'type': 'nd-3d-viewer', 'settings': {'eyebrow': '3D VIEW', 'canvas_label': v['heading'] + ' の3Dモデル。左右にドラッグすると回転します。', **v}}
    data['order'].insert(data['order'].index('main') + 1, 'viewer_3d')


def name_for(tpl):
    if tpl in ('index', 'page', 'collection', 'blog', 'product', '?'):
        return None
    kind, _, suffix = tpl.partition('-')
    if kind not in ('product', 'page'):
        return None
    return f'{kind}.{suffix}'


written = {}
report = []
for path, info in inv.items():
    name = name_for(info['template'])
    if not name or name in written:
        continue
    data = build_contact() if name == 'page.contact' else build(path, info)
    add_story(info['template'], data)
    header = f'/*\n * Generated from the live {path} ({info["template"]}) by tools/convert_live_to_theme.py.\n * Text, links and media are carried over verbatim from neuraldsp.jp.\n */\n'
    (THEME / 'templates' / f'{name}.json').write_text(header + json.dumps(data, ensure_ascii=False, indent=2))
    written[name] = path
    report.append((name, path, [data['sections'][s]['type'] for s in data['order']]))

# ---------------------------------------------------------------- simplified structure
def save(name, data, note):
    (THEME / 'templates' / f'{name}.json').write_text(f'/*\n * {note}\n */\n' + json.dumps(data, ensure_ascii=False, indent=2))


def load_t(name):
    return json.loads(re.sub(r'^/\*.*?\*/\s*', '', (THEME / 'templates' / f'{name}.json').read_text(), flags=re.S))


# 1) FAQ anchors on hardware pages
for n in ('product.quad-cortex', 'product.quad-cortex-mini', 'product.nano-cortex'):
    d = load_t(n)
    for k in d['order']:
        if d['sections'][k]['type'] == 'nd-faq':
            d['sections'][k]['settings']['anchor'] = 'faq'
    save(n, d, f'Generated from the live site (see tools/convert_live_to_theme.py); FAQ anchored at #faq.')

# 2) one plugin page layout for both bundle landing pages
FEATURED = [  # all 12 plugins (each gets a video row; buttons go to the plugin page)
    ('pli', 'Archetype: Plini X', '透明感から、\n歌うリードまで。', 'それを生み出したアーティストと共に、優雅に作り上げられた、真に多用途なプラグイン。', 'PROGRESSIVE / FUSION / AMBIENT', 'clean,crunch,ambient', 'https://cdn.shopify.com/s/files/1/0503/9089/2702/files/plinix-product-card.png', 'iiU1MQy-sUU', 'https://neuraldsp.com/plugins/archetype-plini'),
    ('goj', 'Archetype: Gojira X', '重厚なリフ。\n鮮明な輪郭。', 'メタル界で最も破壊力のあるギタリストの一人、Gojira のジョー・デュプランティエによる、誰もが求めるトーンがすべて詰め込まれています。', 'METAL / HIGH GAIN / EXPERIMENTAL', 'highgain', 'https://cdn.shopify.com/s/files/1/0503/9089/2702/files/a-gojira-x-product-card_cfb2c9e8-e68e-493b-b7ff-4ab47441172f.png', 'MhnkGMBn1tw', 'https://neuraldsp.com/plugins/archetype-gojira'),
    ('cor', 'Archetype: Cory Wong X', 'キレのある、\nクリーントーン。', '完璧なクリーン・トーンやエッジ・オブ・ブレイクアップ・トーンを求めるプレイヤーのために、幅広いサウンドオプションを備えた非常に多用途なプラグイン。', 'FUNK / CLEAN / EDGE OF BREAKUP', 'clean,crunch', 'https://cdn.shopify.com/s/files/1/0503/9089/2702/files/cwx-product-card.png', 'Zy9uFDh9I6o', 'https://neuraldsp.com/plugins/archetype-cory-wong'),
    ('joh', 'Archetype: John Mayer X', '', 'JohnMayerを象徴するクリーントーンから、豊かな倍音を備えたオーバードライブまで幅広く対応。', 'BLUES / POP / CLEAN', 'clean,crunch', 'https://cdn.shopify.com/s/files/1/0503/9089/2702/files/archetype-john-mayer-x-product-card_3cfebe92-ef46-421f-a63d-ad279b159d9e.png?width=800', 'qXxagV9Smcw', 'https://neuraldsp.com/plugins/archetype-john-mayer'),
    ('mis', 'Archetype: Misha Mansoor X', '', 'ハイゲインなモダンメタルトーンからクリアでアーティキュレートなサウンド、GlitchやLaserなどの実験的なエフェクトまで幅広く対応。', 'DJENT / PROGRESSIVE', 'highgain,clean', 'https://cdn.shopify.com/s/files/1/0503/9089/2702/files/archetype-misha-mansoor-x-product-card.png?width=800', 'ZyMbzakf2G8', 'https://neuraldsp.com/plugins/archetype-misha-mansoor'),
    ('tim', 'Archetype: Tim Henson X', '', 'きらびやかなクリーンから温かみのあるクランチ、ヘヴィなリズムやリードまで幅広く対応し、象徴的なMultivoicerによる重層的なハーモニー表現も可能。', 'MATH ROCK / CLEAN / FINGERSTYLE', 'clean,crunch,ambient', 'https://cdn.shopify.com/s/files/1/0503/9089/2702/files/archetype-tim-henson-x-product-card.png?width=800', 'Mz1uL3K75pY', 'https://neuraldsp.com/plugins/archetype-tim-henson'),
    ('rab', 'Archetype: Rabea X', '', 'きらびやかなクリーンからクランチ、力強いモダンハイゲインまで幅広く対応し、革新的なOverlordモノシンセによってギターの表現力をさらに拡張。', 'MODERN METAL / AMBIENT', 'highgain,ambient', 'https://cdn.shopify.com/s/files/1/0503/9089/2702/files/archetype-rabea-x-product-card.png?width=800', 'ZS5Swq-FPy8', 'https://neuraldsp.com/plugins/archetype-rabea'),
    ('pet', 'Archetype: Petrucci X', '', '豊かで明瞭なクリーンから、重厚で力強いリードトーンまで幅広く対応し、4種類のアンプと多彩なエフェクトで自在なサウンドメイクが可能。', 'PROGRESSIVE METAL / LEAD', 'highgain,crunch', 'https://cdn.shopify.com/s/files/1/0503/9089/2702/files/archetype-petrucci-x-product-card.png?width=800', 'XD5mratZFWE', 'https://neuraldsp.com/plugins/archetype-petrucci'),
    ('nol', 'Archetype: Nolly X', '', 'QuadCortex®の高精度モデリングによって、プロレベルのギタートーンと緻密な音作りを実現します。', 'PROGRESSIVE / PRODUCTION', 'highgain,clean', 'https://cdn.shopify.com/s/files/1/0503/9089/2702/files/nolly-x-product-card.png?width=800', 'bpod5JnymrA', 'https://neuraldsp.com/plugins/archetype-nolly'),
    ('slo', 'Soldano SLO-100 X', '', 'クラシックでありながら現代的なハイゲイントーンを備え、アメリカン・ハイゲインの源流を求めるプレイヤーに最適です。', 'ROCK / CLASSIC HIGH GAIN', 'crunch,highgain', 'https://cdn.shopify.com/s/files/1/0503/9089/2702/files/soldano-slo-100-x-product-card.png?width=800', 'hNEJM997cYM', 'https://neuraldsp.com/plugins/soldano-slo-100'),
    ('for', 'Fortin Nameless Suite X', '', '圧倒的な歪みと凶悪なゲインに特化し、メタルからハードロックまで重厚なディストーションを求めるプレイヤーに最適です。', 'METAL / HIGH GAIN', 'highgain', 'https://cdn.shopify.com/s/files/1/0503/9089/2702/files/nameless-x-product-card_3.png?width=800', 'rE7e61rS9pE', 'https://neuraldsp.com/plugins/fortin-nameless-suite'),
    ('par', 'Parallax X', '', 'パラレルプロセッシングにより明瞭さと重厚感を両立し、タイトで存在感のある低域を求めるベーシストに最適です。', 'BASS', 'highgain', 'https://cdn.shopify.com/s/files/1/0503/9089/2702/files/parallax-x-product-card.png?width=800', 'VHpBHTmskDo', 'https://neuraldsp.com/plugins/parallax'),
]
for name, prefix, bundles in (('page.quadcortex-plugin-bundle', 'quadcortex-plugin-bundle-', QC_BUNDLES), ('page.quadcortex-mini-plugin-bundle', 'quadcortex-mini-plugin-bundle-', MINI_BUNDLES)):
    d = load_t(name)
    keep = [k for k in d['order'] if d['sections'][k]['type'] in ('main-page',)]
    tail = [k for k in d['order'] if d['sections'][k]['type'] == 'nd-feature' and 'グローバル' in json.dumps(d['sections'][k], ensure_ascii=False)]
    blocks = {f'plugin_{i}': {'type': 'plugin', 'settings': {'product': prefix + h, 'name': nm, 'headline': hl, 'description': ds, 'genres': g, 'tones': t, 'image_url': img, 'youtube_id': yt, 'plugin_url': u}} for i, (h, nm, hl, ds, g, t, img, yt, u) in enumerate(FEATURED)}
    d['sections']['plugins'] = {'type': 'nd-plugin-discovery', 'settings': {
        'anchor': 'plugins', 'eyebrow': 'Sound Discovery', 'heading': 'あなたの音を、見つけよう。',
        'body': '<p>プラグインは、PC / Mac でギターやベースの音を作るソフトウェアです。対応プラグインは Quad Cortex / Quad Cortex mini にも読み込めます（Nano Cortex は非対応）。</p>',
        'trial_note': '無料体験は PC / Mac 版。neuraldsp.com のダウンロードページからインストールします。',
        'browse_label': 'さらに多くのプラグインをお探しの方へ', 'browse_url': 'https://neuraldsp.com/plugins'},
        'blocks': blocks, 'block_order': list(blocks)}
    d['order'] = keep + ['plugins'] + tail
    save(name, d, 'Simplified: plugin discovery for this hardware (live text for plugin descriptions and the global-store note).')

# 3) one Cortex Cloud + Cortex Control page (both URLs show the same content)
acc, cc = load_t('page.neuraldsp-account'), load_t('page.cortex-control')
merged = {'sections': {}, 'order': []}
def take(src, keys, prefix):
    for k in keys:
        merged['sections'][prefix + k] = src['sections'][k]
        merged['order'].append(prefix + k)
take(cc, cc['order'][:1], 'c_')            # Cortex Control hero
take(acc, acc['order'][:1], 'a_')          # NeuralDSP アカウント (register)
take(cc, cc['order'][1:], 'c_')            # video, features, requirements, download
take(acc, acc['order'][2:], 'a_')          # Cortex Cloud
for n in ('page.neuraldsp-account', 'page.cortex-control'):
    save(n, merged, 'Simplified: Cortex Cloud and Cortex Control on one page (all live text kept).')

# 4) FAQ hub on the shopping-guide page
sg = load_t('page.shopping-guide')
cards = {}
for i, (t, u) in enumerate([('Quad Cortex', '/products/quad-cortex#faq'), ('Quad Cortex mini', '/products/quad-cortex-mini#faq'), ('Nano Cortex', '/products/nano-cortex#faq')]):
    cards[f'c{i}'] = {'type': 'column', 'settings': {'title': t, 'text': '<p>よくあるご質問</p>', 'link_label': '詳しく見る', 'link_url': u}}
sg['sections']['product_faqs'] = {'type': 'nd-columns', 'settings': {'heading': 'FAQs', 'columns': 3}, 'blocks': cards, 'block_order': list(cards)}
sg['sections']['support_links'] = {'type': 'nd-columns', 'settings': {'heading': 'サポート', 'columns': 3}, 'blocks': {
    's0': {'type': 'column', 'settings': {'title': 'ユーザーマニュアル', 'link_label': '詳しく見る', 'link_url': '/a/support/getting-started/user-manuals'}},
    's1': {'type': 'column', 'settings': {'title': 'トラブルシューティング', 'link_label': '詳しく見る', 'link_url': '/a/support/support-category/troubleshooting'}},
    's2': {'type': 'column', 'settings': {'title': 'お問い合わせ', 'link_label': '詳しく見る', 'link_url': '/pages/contact'}}},
    'block_order': ['s0', 's1', 's2']}
sg['order'] = sg['order'] + ['product_faqs', 'support_links']
save('page.shopping-guide', sg, 'Simplified: shopping guide + links to every product FAQ + support (live text kept).')

for name, path, types in report:
    print(f'{name:48} <- {path:46} {" ".join(t.replace("nd-", "") for t in types)}')
print(len(written), 'templates written')
