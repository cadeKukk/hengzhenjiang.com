"""Creator-collaboration previews for the Lovart block. Imported by build.py.

Source: next steps/cooperation_content list.docx. Thumbnails were fetched once into
site/assets/collabs/ (YouTube: i.ytimg.com; Instagram: the public /media/ endpoint; TikTok: oEmbed).
"""
import html, pathlib
from PIL import Image

YT = [  # (video id, title, channel, preview start second) title/channel from YouTube oEmbed
    ('eFzla0vR2lY', 'Me vs T-Rex: Pushing Seedance 2.5 to the Limit', 'AIQUEST', 25),
    ('bR0Fh4y-DYE', 'Adiós Diseñadores: Lovart crea tu marca completa con IA', 'Imperator', 40),
    ('w6-iI-BfneI', 'The Brand That Won 4 Decades Without Changing Once', 'Norff', 30),
    ('jsDWuMFgrb4', 'AI Tool for Architects & Designers: Infinite Canvas, Presentation, Video and Image Generations', 'Archi Vlogs', 35),
]
IG = [  # (shortcode, kind) in the order given in the doc
    ('DcLw2HYIWIq', 'Post'), ('DbTEFvjt7ql', 'Post'), ('DbKzOvPI9lj', 'Reel'), ('DcJnn36IJnG', 'Reel'),
    ('Dbx9aI0obCZ', 'Post'), ('Da2VgiijQU3', 'Post'), ('Dam2d5jj3g4', 'Post'), ('Db8dRNeCKuK', 'Reel'),
    ('DbOWQbdioHo', 'Reel'), ('Db5oOQjtu0n', 'Post'), ('DcoLO3XR6oa', 'Reel'), ('DbdOW1OMAsV', 'Reel'),
    ('DcV6ojwIA3e', 'Reel'),
]
TT = [('7677598960650833185', 'rivestudio', 'Rive’s — Branding & Design', 'My favorite part of any branding project, hands down, are the mockups')]
X = [('2085651427473723707', 'ValeriA_Tech')]

def shape(path):
    w, h = Image.open(path).size
    r = h / w
    return 'tall' if r > 1.45 else ('sq' if r > 1.05 else 'wide')

def render(img_src, thumbs_dir):
    """img_src(filename) -> src string for the target build. Returns the strip's inner HTML."""
    out = []
    for vid, title, ch, start in YT:
        t = html.escape(title); c = html.escape(ch)
        out.append(f'<div class="cit yt wide" data-id="{vid}" data-start="{start}" role="button" tabindex="0" aria-label="Play: {t}"><span class="cthumb">'
                   f'<img src="{img_src(f"yt-{vid}.jpg")}" alt="" loading="lazy" decoding="async"><span class="cbadge">YouTube</span><span class="play"></span></span>'
                   f'<div class="ccap"><span class="cplat">YouTube · {c}</span><b>{t}</b></div></div>')
    for code, kind in IG:
        f = f'ig-{code}.jpg'; s = shape(thumbs_dir / f)
        url = f'https://www.instagram.com/{"reel" if kind == "Reel" else "p"}/{code}/'
        out.append(f'<a class="cit ig {s}" href="{url}" target="_blank" rel="noopener"><span class="cthumb">'
                   f'<img src="{img_src(f)}" alt="Instagram {kind.lower()} from a Lovart creator campaign" loading="lazy" decoding="async"><span class="cbadge">Instagram</span><span class="ext">↗</span></span>'
                   f'<div class="ccap"><span class="cplat">Instagram · {kind}</span><b>Open on Instagram</b></div></a>')
    for vid, handle, name, title in TT:
        f = f'tt-{vid}.jpg'
        out.append(f'<a class="cit tt {shape(thumbs_dir / f)}" href="https://www.tiktok.com/@{handle}/video/{vid}" target="_blank" rel="noopener"><span class="cthumb">'
                   f'<img src="{img_src(f)}" alt="TikTok video by {html.escape(name)}" loading="lazy" decoding="async"><span class="cbadge">TikTok</span><span class="ext">↗</span></span>'
                   f'<div class="ccap"><span class="cplat">TikTok · @{handle}</span><b>{html.escape(title)}</b></div></a>')
    for sid, handle in X:
        out.append(f'<a class="cit x sq" href="https://x.com/{handle}/status/{sid}" target="_blank" rel="noopener"><span class="cthumb"><span class="xg">𝕏</span><span class="ext">↗</span></span>'
                   f'<div class="ccap"><span class="cplat">X · @{handle}</span><b>Open the post</b></div></a>')
    return ''.join(out)

def all_files():
    return [f'yt-{v}.jpg' for v, *_ in YT] + [f'ig-{c}.jpg' for c, _ in IG] + [f'tt-{v}.jpg' for v, *_ in TT]
