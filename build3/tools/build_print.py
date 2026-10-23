"""Build the printable HTML for TKC Volume One from the assembled markdown.

Usage: python3 tools/build_print.py [toc_pages.json]
Writes out/volume_one.html. print.mjs turns it into the PDF and reports
where each part landed, which feeds the contents page on a second pass.
"""
import html
import json
import re
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'volume_one' / 'TKC_Volume_One_World_Dossier.md'
OUT = ROOT / 'out'
OUT.mkdir(exist_ok=True)

LABELS = ['INTERPRETATION', 'CONTESTED', 'INFERENCE', 'POSSIBLE', 'OPEN QUESTION', 'CONFLICT',
          'SUPERSEDED', 'DECIDED', 'RESEARCH']
TAG = r'(?:TL|TR|TR-orig|DOM|MEN|CR|DR3|AM|Ruling|WR(?: \d+(?:–\d+)?)?|FR(?: \d+(?:–\d+)?(?:, \d+(?:–\d+)?)*)?|FR, closing note|INFERENCE from TL)'

pages = json.loads(Path(sys.argv[1]).read_text()) if len(sys.argv) > 1 and Path(sys.argv[1]).exists() else {}

md_text = SRC.read_text()
title_block, body_md = md_text.split('\n## ', 1)
body_md = '## ' + body_md

html_body = markdown.markdown(body_md, extensions=['tables', 'sane_lists'])


def esc(s):
    return html.escape(s, quote=False)


def portraits(m):
    people = [p.strip() for p in html.unescape(m.group(1)).split('|')]
    n = len(people)
    cls = f'n{n}' if n in (1, 2, 3, 4, 12) else f'n{min(n, 7)}'
    cells = []
    for p in people:
        name, _, role = p.partition(' · ')
        cells.append(f'<div class="portrait"><div class="frame"><div class="in"><span class="word">PORTRAIT</span></div></div>'
                     f'<div class="name">{esc(name)}</div><div class="role">{esc(role)}</div></div>')
    return f'<div class="portraits-head">PORTRAITS</div><div class="portraits {cls}">' + ''.join(cells) + '</div>'


def plate(m):
    title, _, desc = html.unescape(m.group(1)).partition(' · ')
    return (f'<div class="plate"><div class="frame"><div class="in"><span class="word">{esc(title.upper())}</span></div></div>'
            f'<div class="cap"><b>{esc(title)}</b><span>{esc(desc)}</span></div></div>')


html_body = re.sub(r'<p>\[PORTRAITS: (.*?)\]</p>', portraits, html_body)
html_body = re.sub(r'<p>\[PLATE: (.*?)\]</p>', plate, html_body)

# writing pages carry the part they close
out, part = [], ''
for chunk in re.split(r'(<h2>.*?</h2>|<p>\[WRITING PAGE\]</p>)', html_body):
    if chunk.startswith('<h2>'):
        part = re.sub('<.*?>', '', chunk)
        out.append(chunk)
    elif chunk == '<p>[WRITING PAGE]</p>':
        short = part.split('. ', 1)[0] if part.startswith('Part') else part
        out.append(f'<div class="writing"><div class="head">Working pages</div>'
                   f'<div class="portraits-head" style="margin:0 0 6pt">{esc(short.upper())}</div>'
                   '<div class="lines">' + '<i></i>' * 22 + '</div><div class="foot"><span>DECIDED</span><span class="d">DATE</span></div></div>')
    else:
        out.append(chunk)
html_body = ''.join(out)

# part headings get a kicker and an anchor
toc = []


def h2(m):
    text = m.group(1)
    mm = re.match(r'Part ([IVX]+)\. (.*)', text)
    pid = f'p{len(toc)}'
    if mm:
        toc.append((pid, f'PART {mm.group(1)}', mm.group(2)))
        return f'<h2 id="{pid}"><span class="kicker">PART {mm.group(1)}</span>{mm.group(2)}</h2>'
    toc.append((pid, '', text))
    return f'<h2 id="{pid}">{text}</h2>'


html_body = re.sub(r'<h2>(.*?)</h2>', h2, html_body)

# labels at the start of a sentence, and source tags in parentheses
lab_re = '|'.join(re.escape(l) for l in LABELS)
html_body = re.sub(rf'(^|<p>|<li>|<td>|\. |\? |: |\(|<strong>)({lab_re}):', lambda m: f'{m.group(1)}<span class="lab">{m.group(2)}</span>', html_body)
html_body = re.sub(rf'\(((?:{TAG})(?:, (?:{TAG}))*)\)', lambda m: f'(<span class="tag">{m.group(1)}</span>)', html_body)
html_body = re.sub(r'<td>((?:TL|TR|DOM|MEN|CR|DR3|AM|TL, CR|TL, FR [\d–, ]+|TL, AM|TL, Ruling|TR, DOM|FR [\d–, ]+|INFERENCE from TL|CR, MEN, FR 19|CR, DOM|TL, MEN, FR 1|CR, TR, DOM|TL, DOM))</td>',
                   r'<td><span class="tag">\1</span></td>', html_body)
html_body = re.sub(r'<p>(Correction to the old Companion:.*?)</p>', r'<p class="correction">\1</p>', html_body)
html_body = re.sub(r'<p>(Content note:.*?)</p>', r'<p class="contentnote">\1</p>', html_body)
html_body = re.sub(r'(<h[34]>Working questions</h[34]>\s*)<ol>', r'\1<ol class="questions">', html_body)

# contents
items = []
for pid, n, t in toc:
    p = pages.get(pid, '')
    items.append(f'<li><span class="n">{n}</span><span class="t">{esc(t)}</span><span class="p">{p}</span></li>')
toc_html = '<section class="toc"><h2>Contents</h2><ol>' + ''.join(items) + '</ol></section>'

cover = ('<section class="cover"><div class="kicker">THY KINGDOM COME · VOLUME ONE</div>'
         '<h1>The World<br>Dossier</h1><div class="rule"></div>'
         '<div class="sub">The history, institutions, beliefs and places that produced Eden\'s story, and the scripture the Empire inherited.</div>'
         '<div class="by">DANY · OCTOBER 2026</div></section>')

doc = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>TKC Volume One · The World Dossier</title>
<link rel="stylesheet" href="../tools/book.css"></head><body>{cover}{toc_html}<main>{html_body}</main></body></html>'''
(OUT / 'volume_one.html').write_text(doc)
(OUT / 'toc_ids.json').write_text(json.dumps([pid for pid, _, _ in toc]))
print('html written,', len(toc), 'contents entries')
