"""Convert a Claude Docs PDF export of the World Dossier back into markdown.

Usage: python3 pdf2md.py <in.pdf> <out.md>

Headings are recognized by font size, bold lead-ins by the Semibold face,
lists by indent, and tables with pdfplumber. Tables that continue across a
page break (repeated header row) are merged.
"""
import re
import sys

import pdfplumber

BODY_X = 54.0
RIGHT_FULL = 500  # a line ending past this x was wrapped, not ended


def face(ch):
    name = ch['fontname'].split('+')[-1]
    return ('b' if 'Semibold' in name else '') + ('i' if 'Italic' in name else '')


def styled(line):
    """Text of a line, with **bold** and *italic* spans. pdfplumber's chars
    carry no spaces, so the line's text is walked against them."""
    chars = [c for c in line['chars'] if c['text'].strip()]
    seq, i = [], 0
    for t in line['text']:
        if t.isspace():
            seq.append({'text': t, 'fontname': seq[-1]['fontname'] if seq else ''})
        else:
            while i < len(chars) and chars[i]['text'] != t:
                i += 1
            seq.append({'text': t, 'fontname': chars[i]['fontname'] if i < len(chars) else ''})
            i += 1
    out, cur, buf = [], None, []

    def flush():
        if not buf:
            return
        t = ''.join(buf)
        lead = t[:len(t) - len(t.lstrip())]
        trail = t[len(t.rstrip()):]
        core = t.strip()
        if core and cur == 'b':
            core = f'**{core}**'
        elif core and cur == 'i':
            core = f'*{core}*'
        elif core and cur == 'bi':
            core = f'***{core}***'
        out.append(lead + core + trail)

    for ch in seq:
        f = face(ch)
        if f != cur:
            flush()
            buf, cur = [], f
        buf.append(ch['text'])
    flush()
    s = ''.join(out)
    return re.sub(r'\*\*\s*\*\*', ' ', s)


def size(line):
    return round(line['chars'][0]['size'], 1)


def is_chrome(line):
    return 'DejaVu' in line['chars'][0]['fontname']


def in_box(line, box):
    x0, top, x1, bottom = box
    return line['top'] >= top - 1 and line['bottom'] <= bottom + 1 and line['x0'] >= x0 - 1


def cell(t):
    t = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1-\2', (t or '').strip())
    return re.sub(r'\s*\n\s*', ' ', t).replace('|', '/')


def items_for(pdf):
    """Yield ('line', dict) and ('table', rows) in reading order, page by page."""
    for page in pdf.pages:
        tables = page.find_tables()
        boxes = [t.bbox for t in tables]
        seq = []
        for t, b in zip(tables, boxes):
            rows = [[cell(c) for c in row] for row in t.extract()]
            keep = [j for j in range(len(rows[0])) if any(r[j] for r in rows)]
            rows = [[r[j] for j in keep] for r in rows if any(r)]
            seq.append((b[1], 'table', rows))
        for l in page.extract_text_lines(return_chars=True):
            if is_chrome(l) or any(in_box(l, b) for b in boxes):
                continue
            seq.append((l['top'], 'line', l))
        seq.sort(key=lambda s: s[0])
        yield 'page', None
        for _, kind, obj in seq:
            yield kind, obj


def convert(path):
    pdf = pdfplumber.open(path)
    blocks = []          # finished blocks (strings)
    para = None          # current paragraph dict
    last_table = None    # header of the last emitted table, for merging
    prev_line = None
    page_break = False

    def end_para():
        nonlocal para
        if para:
            blocks.append(para['text'])
            para = None

    for kind, obj in items_for(pdf):
        if kind == 'page':
            page_break = True
            continue
        if kind == 'table':
            rows = obj
            if last_table is not None and rows and rows[0] == last_table[0] and para is None \
                    and blocks and blocks[-1].startswith('|'):
                blocks[-1] += '\n' + '\n'.join('| ' + ' | '.join(r) + ' |' for r in rows[1:])
            else:
                end_para()
                head = rows[0]
                md = ['| ' + ' | '.join(head) + ' |', '|' + ' --- |' * len(head)]
                md += ['| ' + ' | '.join(r) + ' |' for r in rows[1:]]
                blocks.append('\n'.join(md))
                last_table = rows
            prev_line, page_break = None, False
            continue

        l = obj
        sz = size(l)
        text = styled(l).strip()
        if sz >= 20:
            end_para(); blocks.append('# ' + text); prev_line = None; page_break = False; continue
        if sz >= 16:
            end_para(); blocks.append('## ' + text); prev_line = None; page_break = False; continue
        if sz >= 13:
            end_para(); blocks.append('### ' + text); prev_line = None; page_break = False; continue
        whole_bold = all(face(c) == 'b' for c in l['chars'] if c['text'].strip())
        if whole_bold and l['x1'] < 420 and not re.search(r'[.!?]$', l['chars'][-1]['text'] + text[-1:]) \
                and l['x0'] < BODY_X + 2:
            # a standalone bold line is a minor heading (II.2 book titles, For TKC)
            end_para(); blocks.append('#### ' + text.strip('*')); prev_line = None; page_break = False; continue

        x0 = l['x0']
        m = re.match(r'^(\d+)\.\s', text)
        numbered = bool(m) and x0 < 66 and int(m.group(1)) < 100
        indented = x0 > 64
        gap = (l['top'] - prev_line['bottom']) if (prev_line and not page_break) else None
        continues = False
        if para is not None:
            if page_break:
                same_kind = (para['kind'] == 'bullet') == indented or (para['kind'] == 'num' and indented)
                continues = prev_line is not None and prev_line['x1'] > RIGHT_FULL and not numbered \
                    and same_kind and not text.startswith('**')
            else:
                continues = gap is not None and gap < 6 and not numbered
                if para['kind'] == 'bullet' and indented and gap is not None and gap >= 2.5 and \
                        (l['top'] - prev_line['top']) > 19.5:
                    continues = False
        if continues:
            sep = '' if para['text'].endswith('-') and not para['text'].endswith(' -') else ' '
            para['text'] += sep + text
        else:
            end_para()
            if numbered:
                para = {'kind': 'num', 'text': text}
            elif indented:
                para = {'kind': 'bullet', 'text': '- ' + text}
            else:
                para = {'kind': 'p', 'text': text}
        prev_line, page_break = l, False
    end_para()

    # numbered items and bullets need no blank line between siblings
    out = []
    for b in blocks:
        if out and ((re.match(r'^\d+\.\s', b) and re.match(r'^\d+\.\s', out[-1].split('\n')[-1])) or
                    (b.startswith('- ') and out[-1].split('\n')[-1].startswith('- '))):
            out[-1] += '\n' + b
        else:
            out.append(b)
    return '\n\n'.join(out) + '\n'


if __name__ == '__main__':
    md = convert(sys.argv[1])
    open(sys.argv[2], 'w').write(md)
