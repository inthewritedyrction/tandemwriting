"""TKC Volume One workbook renderer.

Reads workbook/units/*.tkc in name order and writes out/workbook.html.
Usage: python3 workbook/wb.py

Markup (one page per "@" line):
  @cover | @divider | @part | @opener | @page | @essay | @notes   key="value" ...
  common keys: rh (running head), m (margin refs, ";"-separated), see (cross-reference), id (anchor)
Blocks:
  # Title            lede: / drop: / k: / kp: / q: text | REF / pull: / corr: / note:
  rec:  (Label | value rows)        tab: / tabrl:  (pipe rows, first is header)
  box: T / boxthin: T / empire: T / contested: T / cols: (|| splits) / side: / review: T | aside / plate: kind  ... /end
  prompt: TEXT | N|fill     lines: N|fill     decided     fields: A, B, C (inside review)
  - item / 1. item        anything else is a paragraph (consecutive lines join)
"""
import html
import json
import re
import shlex
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = ROOT / 'out'

LABELS = ['INTERPRETATION', 'CONTESTED', 'INFERENCE', 'POSSIBLE', 'OPEN QUESTION', 'CONFLICT',
          'SUPERSEDED', 'DECIDED', 'RESEARCH']
TAG = (r'(?:TL|TR|TR-orig|DOM|MEN|CR|DR3|AM|Ruling|WR(?: \d+(?:–\d+)?)?|'
       r'FR(?: \d+(?:–\d+)?(?:, \d+(?:–\d+)?)*)?|FR, closing note)')


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<em>\1</em>', s)
    lab = '|'.join(re.escape(l) for l in LABELS)
    s = re.sub(rf'(^|\. |\? |: |\(|<strong>|— )({lab}):', lambda m: f'{m.group(1)}<span class="lab">{m.group(2)}</span>', s)
    s = re.sub(rf'\(((?:{TAG})(?:, (?:{TAG}))*)\)', lambda m: f'(<span class="tag">{m.group(1)}</span>)', s)
    return s


def plain(s):
    """The text a reader sees for a prompt label, for matching."""
    s = re.sub(r'\*+', '', s)
    return re.sub(r'\s+', ' ', s).strip().upper()


def parse_attrs(line):
    head, _, rest = line[1:].partition(' ')
    attrs = {}
    for tok in shlex.split(rest):
        k, _, v = tok.partition('=')
        attrs[k] = v
    return head, attrs


class Block:
    """Turns the body lines of one page into HTML."""

    def __init__(self, lines):
        self.lines = lines
        self.i = 0

    def until_end(self):
        out = []
        depth = 0
        while self.i < len(self.lines):
            l = self.lines[self.i]
            self.i += 1
            if re.match(r'^(box|boxthin|empire|contested|cols|side|review|plate|calls):', l):
                depth += 1
            if l.strip() == '/end':
                if depth == 0:
                    return out
                depth -= 1
            out.append(l)
        return out

    def render(self, ctx=None):
        out, para = [], []

        def flush():
            if para:
                out.append(f'<p>{inline(" ".join(para))}</p>')
                para.clear()

        while self.i < len(self.lines):
            l = self.lines[self.i]
            self.i += 1
            s = l.strip()
            if not s:
                flush()
                continue
            m = re.match(r'^(\w+):\s?(.*)$', s)
            key, val = (m.group(1), m.group(2)) if m else (None, None)
            if s.startswith('<'):
                flush(); out.append(s)
            elif s.startswith('# '):
                flush(); out.append(f'<h1>{inline(s[2:])}</h1>')
            elif s == 'status':
                flush(); out.append('<div class="status"><span class="ck">POSSIBLE</span><span class="ck">OPEN QUESTION</span><span class="ck">DECIDED</span><span class="f">LOG NO.</span><span class="f">DATE</span></div>')
            elif s == 'decided':
                flush(); out.append('<div class="decided"><span>DECIDED</span><span class="d">DATE</span></div>')
            elif s.startswith('- '):
                flush()
                items = [s[2:]]
                while self.i < len(self.lines) and self.lines[self.i].strip().startswith('- '):
                    items.append(self.lines[self.i].strip()[2:]); self.i += 1
                out.append('<ul>' + ''.join(f'<li>{inline(x)}</li>' for x in items) + '</ul>')
            elif re.match(r'^\d+\. ', s):
                flush()
                items = [re.sub(r'^\d+\. ', '', s)]
                while self.i < len(self.lines) and re.match(r'^\d+\. ', self.lines[self.i].strip()):
                    items.append(re.sub(r'^\d+\. ', '', self.lines[self.i].strip())); self.i += 1
                out.append('<ol>' + ''.join(f'<li>{inline(x)}</li>' for x in items) + '</ol>')
            elif key == 'lede':
                flush(); out.append(f'<p class="lede">{inline(val)}</p>')
            elif key == 'drop':
                flush(); out.append(f'<p class="drop">{inline(val)}</p>')
            elif key in ('k', 'kp'):
                flush(); out.append(f'<div class="k{" pink" if key == "kp" else ""}">{inline(val)}</div>')
            elif key == 'q':
                flush(); t, _, r = val.partition(' | ')
                out.append(f'<div class="q"><div class="t">{inline(t)}</div><div class="r">{inline(r)}</div></div>')
            elif key == 'pull':
                flush(); out.append(f'<div class="pull">{inline(val)}</div>')
            elif key == 'corr':
                flush(); out.append(f'<div class="corr"><span class="lab">CORRECTION TO THE OLD COMPANION</span> {inline(val)}</div>')
            elif key == 'note':
                flush(); out.append(f'<div class="cnote"><b>CONTENT NOTE</b> &nbsp;{inline(val)}</div>')
            elif key == 'small':
                flush(); out.append(f'<p class="small">{inline(val)}</p>')
            elif key in ('rec',):
                flush()
                rows = []
                while self.i < len(self.lines) and self.lines[self.i].strip() and ' | ' in self.lines[self.i] \
                        and not re.match(r'^(\w+):\s', self.lines[self.i].strip().split(' | ')[0] + ' '):
                    a, _, b = self.lines[self.i].strip().partition(' | ')
                    rows.append(f'<div class="row"><div class="l">{inline(a)}</div><div class="v">{inline(b)}</div></div>')
                    self.i += 1
                out.append('<div class="record">' + ''.join(rows) + '</div>')
            elif key in ('tab', 'tabrl'):
                flush()
                rows = []
                while self.i < len(self.lines) and self.lines[self.i].strip().startswith('|'):
                    cells = [c.strip() for c in self.lines[self.i].strip().strip('|').split('|')]
                    rows.append(cells); self.i += 1
                hdr = ''.join(f'<th>{inline(c)}</th>' for c in rows[0])
                body = ''
                for r in rows[1:]:
                    tds = ''
                    for j, c in enumerate(r):
                        cls = ' class="rl"' if (key == 'tabrl' and j == 0) else (' class="blank"' if c == '_' else '')
                        tds += f'<td{cls}>{"" if c == "_" else inline(c)}</td>'
                    body += f'<tr>{tds}</tr>'
                out.append(f'<table><thead><tr>{hdr}</tr></thead><tbody>{body}</tbody></table>')
            elif key in ('box', 'boxthin', 'empire', 'contested'):
                flush()
                inner = Block(self.until_end()).render()
                cls = {'box': 'box', 'boxthin': 'box thin', 'empire': 'empire', 'contested': 'contested'}[key]
                title = f'<div class="k">{inline(val)}</div>' if val else ''
                out.append(f'<div class="{cls}">{title}{inner}</div>')
            elif key == 'cols':
                flush()
                body = self.until_end()
                parts, cur = [], []
                for x in body:
                    if x.strip() == '||':
                        parts.append(cur); cur = []
                    else:
                        cur.append(x)
                parts.append(cur)
                out.append('<div class="cols">' + ''.join(f'<div>{Block(p).render()}</div>' for p in parts) + '</div>')
            elif key == 'review':
                flush()
                t, _, aside = val.partition(' | ')
                body = self.until_end()
                fields = [x for x in body if x.strip().startswith('fields:')]
                text = [x for x in body if not x.strip().startswith('fields:')]
                fl = [f.strip() for f in fields[0].split(':', 1)[1].split(',')] if fields else ['DECISION', 'DATE']
                out.append(f'<div class="review"><div class="top"><div class="k" style="margin:0">{inline(t)}</div><i>{inline(aside)}</i></div>'
                           f'<p>{inline(" ".join(x.strip() for x in text if x.strip()))}</p>'
                           '<div class="fields">' + ''.join(f'<span>{inline(f)}</span>' for f in fl) + '</div></div>')
            elif key == 'prompt':
                flush()
                t, _, n = val.rpartition(' | ')
                t = t or val
                n = n if n else '4'
                mnum = re.match(r'^(\d+) · (.*)$', t)
                label = f'<span class="n">{mnum.group(1)} ·</span> {inline(mnum.group(2))}' if mnum else inline(t)
                if n.strip() == 'fill':
                    out.append(f'<div class="prompt fill"><div class="k">{label}</div><div class="lines"></div></div>')
                else:
                    out.append(f'<div class="prompt"><div class="k">{label}</div><div class="lines">' + '<i></i>' * int(n) + '</div></div>')
            elif key == 'lines':
                flush()
                if val.strip() == 'fill':
                    out.append('<div class="fill"><div class="lines"></div></div>')
                else:
                    out.append('<div class="lines">' + '<i></i>' * int(val) + '</div>')
            elif key == 'side' and ctx is not None:
                flush(); ctx['side'] = self.until_end()
            elif key == 'plate' and ctx is not None:
                flush(); ctx['plate'] = (val, self.until_end())
            elif key == 'calls':
                flush()
                body = self.until_end()
                parts, cur = [], []
                for x in body:
                    if x.strip() == '||':
                        parts.append(cur); cur = []
                    else:
                        cur.append(x)
                parts.append(cur)
                out.append('<div class="calls">' + ''.join(f'<div>{Block(p).render()}</div>' for p in parts) + '</div>')
            elif key == 'tk':
                flush(); out.append(f'<div class="tk">{inline(val)}</div>')
            elif key == 'big':
                flush(); out.append(f'<div class="big">{inline(val)}</div>')
            else:
                para.append(s)
        flush()
        return ''.join(out)


def render_side(lines):
    out = []
    i = 0
    while i < len(lines):
        s = lines[i].strip(); i += 1
        if not s:
            continue
        key, _, val = s.partition(': ')
        if s.startswith('chips:'):
            out.append('<div class="chips">' + ''.join(f'<span>{inline(c.strip())}</span>' for c in s[6:].split(',')) + '</div>')
        elif key == 'k':
            out.append(f'<div class="k">{inline(val)}</div>')
        elif key == 'kp':
            out.append(f'<div class="k pink">{inline(val)}</div>')
        elif key == 'stext':
            out.append(f'<div class="stext">{inline(val)}</div>')
        elif key == 'sbox':
            t, _, v = val.partition(' | ')
            out.append(f'<div class="sbox"><div class="k">{inline(t)}</div>{inline(v)}</div>')
        elif s == 'marg':
            out.append('<div class="k pink">MARGINALIA</div><div class="fill"><div class="lines"></div></div>')
        elif key == 'see':
            out.append(f'<div class="see"><span class="orn">✥</span> <em>See also:</em> {inline(val)}</div>')
    return ''.join(out)


def render_plate(kind, lines):
    kind = kind.strip()
    get = lambda k: [l.strip()[len(k) + 1:].strip() for l in lines if l.strip().startswith(k + ':')]
    if kind == 'quote':
        pk = get('pk'); pq = get('pq'); pr = get('pr')
        return ('<div class="plate quote"><div class="in">'
                + (f'<div class="pk">{inline(pk[0])}</div>' if pk else '')
                + ''.join(f'<div class="pq">{inline(x)}</div>' for x in pq)
                + '<div class="po">✥</div>'
                + (f'<div class="pr">{inline(pr[0])}</div>' if pr else '') + '</div></div>')
    if kind == 'doc':
        dh = get('dh'); out = ['<div class="plate doc"><div class="in">']
        if dh:
            a, _, b = dh[0].partition(' | ')
            out.append(f'<div class="dh"><b>{inline(a)}</b><span>{inline(b)}</span></div>')
        for x in get('dsub'):
            out.append(f'<div class="dsub">{inline(x)}</div>')
        for l in lines:
            s = l.strip()
            if s.startswith('df:'):
                a, _, b = s[3:].strip().partition(' | ')
                out.append(f'<div class="df"><div class="fl">{inline(a)}</div><div class="fv">{inline(b)}</div></div>')
            elif s.startswith('dnote:'):
                out.append(f'<div class="dnote">{inline(s[6:].strip())}</div>')
        for x in get('stamp'):
            out.append(f'<div class="stamp">{inline(x)}</div>')
        out.append('</div></div>')
        return ''.join(out)
    # frame: an empty frame to draw or paste into
    cap = kind.partition('|')[2].strip()
    return f'<div class="plate frame"><div class="in"><div class="cap">{inline(cap)}</div></div></div>'


def margin_html(attrs, page_kind):
    refs = [r.strip() for r in attrs.get('m', '').split(';') if r.strip()]
    see = attrs.get('see')
    h = ''.join(f'<div class="ref">{inline(r)}</div>' for r in refs)
    if see:
        h += f'<div class="see"><span class="orn">✥</span> <em>See also:</em> {inline(see)}</div>'
    return f'<div class="margin">{h}</div>'


def build():
    units = sorted((HERE / 'units').glob('*.tkc'))
    pages = []  # (kind, attrs, lines)
    for u in units:
        cur = None
        for line in u.read_text().split('\n'):
            if line.startswith('@'):
                kind, attrs = parse_attrs(line)
                cur = (kind, attrs, [])
                pages.append(cur)
            elif cur is not None:
                cur[2].append(line)
    # a dense page whose writing area came out short gets a working page after it
    # (out/continuations.json is written by the print step and keyed by the page's running head + prompt)
    cont_file = OUT / 'continuations.json'
    conts = json.loads(cont_file.read_text()) if cont_file.exists() else []
    if conts:
        want = {(c['rh'], c['prompt']): c.get('mode', 'add') for c in conts}
        expanded = []
        for kind, attrs, lines in pages:
            extra = []
            keep = []
            for l in lines:
                s = l.strip()
                if s.startswith('prompt:') and s.endswith('| fill'):
                    pr = s[7:].rsplit(' | ', 1)[0].strip()
                    mode = want.get((attrs.get('rh', ''), plain(pr)))
                    if mode:
                        extra.append(('page', {'rh': attrs.get('rh', '') + ' · WORKING SPACE', 'm': 'WRITING; FROM THE FACING PAGE'},
                                      [f'prompt: {pr} | fill']))
                        if mode == 'move':
                            continue
                keep.append(l)
            expanded.append((kind, attrs, keep))
            expanded.extend(extra)
        pages = expanded
    anchors = {a['id']: i + 1 for i, (k, a, _) in enumerate(pages) if 'id' in a}

    html_pages = []
    for n, (kind, attrs, lines) in enumerate(pages, start=1):
        parity = 'odd' if n % 2 else 'even'
        rh = f'<div class="rh">{inline(attrs["rh"])}</div>' if attrs.get('rh') else ''
        folio = f'<div class="folio">{n:03d}</div>' if kind not in ('cover', 'part') else ''
        if kind == 'cover':
            body = Block(lines).render()
            html_pages.append(f'<section class="page cover {parity}"><div class="wrap">{body}</div></section>')
            continue
        if kind in ('part', 'divider'):
            a = attrs
            toc = ''
            tl = [l.strip()[4:].strip() for l in lines if l.strip().startswith('toc:')]
            if tl:
                rows = []
                for t in tl:
                    label, _, ref = t.partition(' | ')
                    rows.append(f'<div><span>{inline(label)}</span><span>{anchors.get(ref.strip(), ""):03}</span></div>'
                                if ref.strip() in anchors else f'<div><span>{inline(label)}</span><span></span></div>')
                toc = '<div class="toc">' + ''.join(rows) + '</div>'
            inner = (f'<div class="bar"></div><div class="bar2"></div>'
                     f'<div class="series">{inline(a.get("series", "THY KINGDOM COME · VOLUME ONE"))}</div>'
                     f'<div class="num">{inline(a.get("num", ""))}</div>'
                     f'<div class="kind">{inline(a.get("kind", ""))}</div>'
                     f'<div class="title">{inline(a.get("title", "")).replace("/", "<br>")}</div>'
                     f'<div class="orn">✥</div>'
                     f'<div class="sub">{inline(a.get("sub", ""))}</div>{toc}'
                     + (f'<div class="foot">{inline(a["foot"])}</div>' if a.get('foot') else '<div class="base"></div>'))
            html_pages.append(f'<section class="page divider {parity}"><div class="wrap">{inner}</div>{folio}</section>')
            continue
        ctx = {}
        main = Block(lines).render(ctx)
        if kind == 'opener':
            plate = render_plate(*ctx['plate']) if 'plate' in ctx else render_plate('frame | ', [])
            html_pages.append(f'<section class="page opener {parity}">{rh}<div class="body"><div class="main">'
                              f'<div class="platebox">{plate}</div>{main}</div>{margin_html(attrs, kind)}</div>{folio}</section>')
            continue
        if kind == 'essay':
            side = render_side(ctx.get('side', []))
            html_pages.append(f'<section class="page essay {parity}">{rh}<div class="body"><div class="main">{main}</div>'
                              f'<div class="side">{side}</div></div>{folio}</section>')
            continue
        if kind == 'notes':
            prompt = attrs.get('prompt', 'ANYTHING THIS SPREAD STARTED AND DID NOT FINISH')
            main = f'<div class="prompt fill"><div class="k">{inline(prompt)}</div><div class="lines"></div></div>'
        html_pages.append(f'<section class="page {kind} {parity}">{rh}<div class="body"><div class="main">{main}</div>'
                          f'{margin_html(attrs, kind)}</div>{folio}</section>')

    doc = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>TKC Volume One · The World Dossier</title>'
           '<link rel="stylesheet" href="../workbook/wb.css"></head><body>' + ''.join(html_pages) + '</body></html>')
    OUT.mkdir(exist_ok=True)
    (OUT / 'workbook.html').write_text(doc)
    print(len(html_pages), 'pages')


if __name__ == '__main__':
    build()
