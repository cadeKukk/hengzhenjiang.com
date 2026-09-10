#!/usr/bin/env python3
"""Build the portfolio.

  python3 draft/build.py

Produces:
  site/index.html  + site/assets/...   (deployed to Vercel; images as files)
  draft/index.html                     (single file with images inlined; used for the Claude artifact)

Source of truth is draft/index.template.html (English) + draft/i18n.zh.json (Chinese).
Field-note photos are listed in ROW1/ROW2 below. Derived images are committed under site/assets and
draft/img; the original gallery (current-site/public/assets/gallery-v2) is only needed to add new photos.
"""
import base64, json, pathlib, re, shutil, subprocess, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import collabs
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
DRAFT, SITE = ROOT / 'draft', ROOT / 'site'
GALLERY = ROOT / 'current-site' / 'public' / 'assets' / 'gallery-v2'
IMG = DRAFT / 'img'            # hero, portrait (already prepared)
NOTES_DIR = SITE / 'assets' / 'notes'
NOTES_DIR.mkdir(parents=True, exist_ok=True)
COLLABS_DIR = SITE / 'assets' / 'collabs'
RESUME_SRC = ROOT / 'source' / 'resume'   # drop updated PDFs here with these exact names
RESUMES = {'Hengzhen_Jiang_Resume_EN.pdf': 'Hengzhen_Jiang_Resume_EN.pdf', 'Hengzhen_Jiang_Resume_ZH.pdf': 'Hengzhen_Jiang_Resume_ZH.pdf'}
LIVE = 'https://hengzhen-jiang.vercel.app/'   # absolute base used by the single-file artifact build

# (gallery number, caption). Captions describe what is visible, nothing more.
ROW1 = [('003', 'Hilltop over the bay'), ('005', 'Frozen fountain'), ('007', 'Pineapple fountain'),
        ('013', 'Cypress swamp, kayaks'), ('015', 'Two chairs, one horizon'), ('019', 'A polaroid at the shore'),
        ('024', 'Chena River, snow road'), ('034', 'Blossoms on campus'), ('037', 'Lake at dusk'),
        ('040', 'Home game'), ('042', 'Duke wins'), ('043', 'Sunset over the surf')]
ROW2 = [('046', 'Bonfire night'), ('048', 'Boats at golden hour'), ('049', 'First snow'),
        ('051', 'Orange canopy'), ('054', 'A smile in the snow'), ('058', 'Colourful street, winter'),
        ('063', 'Sunrise, one tree'), ('027', 'Concert lights'), ('009', 'Bridge at dusk'),
        ('074', 'Sunset over the clouds'), ('076', 'Walking the shoreline'), ('035', 'Palm cove')]

def ffmpeg(src, dst, vf, q):
    if not src.exists():
        if dst.exists(): return
        raise SystemExit(f'missing source {src} and no cached output {dst}')
    if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime: return
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(src), '-vf', vf, '-q:v', str(q), str(dst)], check=True)

def data_uri(p, mime='image/jpeg'):
    return f'data:{mime};base64,' + base64.b64encode(p.read_bytes()).decode()

def prepare_notes():
    out = {}
    for n, cap in ROW1 + ROW2:
        src = GALLERY / f'gallery-{n}.jpg'
        card = NOTES_DIR / f'n{n}.jpg'; full = NOTES_DIR / f'n{n}-full.jpg'; inline = DRAFT / 'img' / f'n{n}-inline.jpg'
        ffmpeg(src, card, 'scale=640:480:force_original_aspect_ratio=increase,crop=640:480', 5)
        ffmpeg(src, full, "scale='min(1400,iw)':-2", 4)
        ffmpeg(src, inline, "scale='min(560,iw)':-2", 7)
        out[n] = dict(card=card, full=full, inline=inline, cap=cap)
    return out

def card_html(i, n, cap, src, full):
    return (f'<button class="note" type="button" data-i="{i}" data-n="{int(n)}" data-title="{cap}" data-full="{full}">'
            f'<div class="card"><h4>Note {int(n)}<span>{cap}</span></h4><hr><span class="idx">Field note {int(n)} / 76</span>'
            f'<div class="imgwrap"><img src="{src}" alt="{cap}" loading="lazy" decoding="async"></div>'
            f'<div class="ft"><span>by Hengzhen</span><span>2024—26</span></div></div></button>')

def prepare_collabs():
    """Shrink the fetched thumbnails in place for the site and make small inline copies for the artifact."""
    for name in collabs.all_files():
        f = COLLABS_DIR / name
        im = Image.open(f); w, h = im.size
        if max(w, h) > 800:
            im.thumbnail((800, 800)); im.convert('RGB').save(f, quality=82)
        small = DRAFT / 'img' / f'collab-{name}'
        if not small.exists():
            im2 = Image.open(f); im2.thumbnail((420, 420)); im2.convert('RGB').save(small, quality=70)

def prepare_resumes():
    (SITE / 'assets' / 'resume').mkdir(parents=True, exist_ok=True)
    for src, dst in RESUMES.items():
        shutil.copyfile(RESUME_SRC / src, SITE / 'assets' / 'resume' / dst)

def render(template, notes, inline):
    t = template
    i18n = json.loads((DRAFT / 'i18n.zh.json').read_text()); i18n.pop('_comment', None)
    t = t.replace('{{I18N}}', json.dumps(i18n, ensure_ascii=False))
    if inline:
        t = t.replace('{{COLLABS}}', collabs.render(lambda n: data_uri(DRAFT / 'img' / f'collab-{n}'), COLLABS_DIR))
        t = t.replace('{{BASE}}', LIVE).replace('{{EMBED}}', '0')
        # the artifact viewer never grants download permission: open the PDFs in a new tab there instead
        t = re.sub(r' download="[^"]*"', ' target="_blank" rel="noopener"', t)
    else:
        t = t.replace('{{COLLABS}}', collabs.render(lambda n: f'assets/collabs/{n}', COLLABS_DIR))
        t = t.replace('{{BASE}}', '').replace('{{EMBED}}', '1')
    for key, row, offset in (('{{NOTES_ROW1}}', ROW1, 0), ('{{NOTES_ROW2}}', ROW2, len(ROW1))):
        cards = []
        for k, (n, cap) in enumerate(row):
            m = notes[n]
            if inline:
                d = data_uri(m['inline']); cards.append(card_html(offset + k, n, cap, d, d))
            else:
                cards.append(card_html(offset + k, n, cap, f'assets/notes/{m["card"].name}', f'assets/notes/{m["full"].name}'))
        t = t.replace(key, ''.join(cards))
    fixed = {'{{IMG_DUKE}}': ('duke-px.png', 'image/png'), '{{IMG_PORTRAIT}}': ('portrait.jpg', 'image/jpeg')}
    for key, (name, mime) in fixed.items():
        if inline: t = t.replace(key, data_uri(IMG / name, mime))
        else:
            (SITE / 'assets').mkdir(exist_ok=True)
            (SITE / 'assets' / name).write_bytes((IMG / name).read_bytes())
            t = t.replace(key, f'assets/{name}')
    assert '{{' not in t, 'unresolved placeholder'
    return t

def main():
    template = (DRAFT / 'index.template.html').read_text()
    notes = prepare_notes()
    prepare_collabs(); prepare_resumes()
    site_html = render(template, notes, inline=False)
    # the artifact host wraps the fragment in its own document; the deployed site needs a real one
    head_end = site_html.index('<style>')
    head, body = site_html[:head_end], site_html[head_end:]
    style_end = body.index('</style>') + len('</style>')
    doc = ('<!doctype html>\n<html lang="en">\n<head>\n' + head + body[:style_end] +
           '\n<meta name="theme-color" content="#f5f5f2">\n</head>\n<body>\n' + body[style_end:] + '\n</body>\n</html>\n')
    (SITE / 'index.html').write_text(doc)
    (DRAFT / 'index.html').write_text(render(template, notes, inline=True))
    print('site/index.html', (SITE / 'index.html').stat().st_size, '| draft/index.html', (DRAFT / 'index.html').stat().st_size)

if __name__ == '__main__':
    main()
