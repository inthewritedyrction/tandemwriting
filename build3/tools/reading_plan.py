"""Build the reading plan that pairs Volume Two with Volume One.

Reads both built volumes (out/workbook.html, out/workbook_v2.html), the {v1:key}
citations in workbook/units_v2, and writes workbook/units_v3/*.tkc. Each day takes
the next stretch of Volume Two, the Volume One sections that stretch cites, and a
steady thread of the Volume One pages nothing cites yet, so both volumes finish
on the same day. Usage: python3 tools/reading_plan.py [pages_per_day]
"""
import html, json, math, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'out'
PACE = int(sys.argv[1]) if len(sys.argv) > 1 else 10
DAYS_PER_WEEK = 5


def read_pages(path):
    s = (OUT / path).read_text()
    pages = []
    for body in re.findall(r'<section class="page([^"]*)">(.*?)</section>', s, re.S):
        cls, body = body
        m = re.search(r'<div class="rh">(.*?)</div>', body)
        rh = html.unescape(re.sub(r'<[^>]+>', '', m.group(1))) if m else ''
        t = ''
        for pat in (r'<h1[^>]*>(.*?)</h1>', r'<div class="big">(.*?)</div>', r'<div class="title">(.*?)</div>'):
            h = re.search(pat, body, re.S)
            if h:
                t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<br>', ' ', re.sub(r'<(?!br)[^>]+>', '', h.group(1))))).strip()
                break
        pages.append({'rh': rh, 'title': t, 'kind': cls.split()[0] if cls.split() else ''})
    return pages


def base(rh):
    for suf in (' · WORKING SPACE', ', CONTINUED'):
        rh = rh.replace(suf, '')
    return rh


v1 = read_pages('workbook.html')
v2 = read_pages('workbook_v2.html')
N1, N2 = len(v1), len(v2)

# Volume One blocks: runs of pages sharing a base running head (a section and its working pages).
# Dividers, notes pages and parts stick to the block that follows or precedes them.
blocks = []
for i, p in enumerate(v1, start=1):
    key = base(p['rh']) or f'__{p["kind"]}'
    if blocks and (blocks[-1]['key'] == key or p['kind'] in ('notes',) or not p['rh']):
        if not p['rh'] and p['kind'] in ('part', 'divider', 'opener') and blocks[-1]['key'] != key:
            blocks.append({'key': key, 'a': i, 'b': i, 'title': p['title']})
        else:
            blocks[-1]['b'] = i
            if not blocks[-1]['title']:
                blocks[-1]['title'] = p['title']
    else:
        blocks.append({'key': key, 'a': i, 'b': i, 'title': p['title']})
# a divider/opener block with no running head merges into the block after it
merged = []
for b in blocks:
    if merged and merged[-1]['key'].startswith('__') and merged[-1]['b'] + 1 == b['a']:
        merged[-1] = {'key': b['key'], 'a': merged[-1]['a'], 'b': b['b'], 'title': b['title'] or merged[-1]['title']}
    else:
        merged.append(b)
blocks = merged
page_block = {}
for bi, b in enumerate(blocks):
    for p in range(b['a'], b['b'] + 1):
        page_block[p] = bi

# Volume One key -> block
refs = json.loads((ROOT / 'workbook' / 'v1_refs.json').read_text())
first = {}
for i, p in enumerate(v1, start=1):
    first.setdefault(p['rh'], i)
key_block = {k: page_block[first[v]] for k, v in refs.items() if v in first}

# Volume Two sections from its anchors, with citations from the unit sources
anch2 = json.loads((OUT / 'anchors_v2.json').read_text())
order = sorted(anch2.items(), key=lambda x: x[1])
NAMES = {}
for f in sorted((ROOT / 'workbook' / 'units_v2').glob('*.tkc')):
    cur = None
    for line in f.read_text().split('\n'):
        m = re.match(r'@\w+.*?id="([^"]+)"', line)
        if m:
            cur = m.group(1)
            NAMES.setdefault(cur, [])
        if cur:
            NAMES[cur] += re.findall(r'\{v1:([\w-]+)\}', line)
# sections: each anchor to the next
secs = []
for i, (aid, a) in enumerate(order):
    b = order[i + 1][1] - 1 if i + 1 < len(order) else N2
    if b < a:
        continue
    secs.append({'id': aid, 'a': a, 'b': b, 'cites': list(dict.fromkeys(NAMES.get(aid, [])))})
p1 = anch2.get('part1', 1)
for sec in secs:
    if sec['a'] < p1:
        sec['cites'] = []
if secs and secs[0]['a'] > 1:
    secs.insert(0, {'id': 'cover', 'a': 1, 'b': secs[0]['a'] - 1, 'cites': []})


def v2_label(a, b):
    ts = []
    for p in range(a, b + 1):
        t = v2[p - 1]['title'] or ''
        rh = v2[p - 1]['rh']
        if rh.startswith('NOTES') or 'WORKING SPACE' in rh:
            continue
        if t and t not in ts:
            ts.append(t)
    who = ''
    rh = next((v2[p - 1]['rh'] for p in range(a, b + 1) if v2[p - 1]['rh'] and 'NOTES' not in v2[p - 1]['rh']), '')
    parts = [x.strip() for x in rh.split('·')]
    if len(parts) >= 2:
        who = parts[1].title() if parts[0] in ('THE PARISH HOUSEHOLD', 'HOUSE AUREM', 'THE COVENANT DAUGHTERS', 'THE HOUSE OF VANE') else parts[0].title()
    text = ', '.join(ts[:3]) + ('…' if len(ts) > 3 else '')
    return (who + ': ' if who and who.lower() not in text.lower() else '') + (text or 'Opening pages')


def v1_label(bi):
    b = blocks[bi]
    t = b['title'] or base(v1[b['a'] - 1]['rh']).split('·')[-1].strip().title()
    return t


# Volume Two in chunks of at most ~5 pages, never splitting below 2
chunks = []
for s in secs:
    n = s['b'] - s['a'] + 1
    k = max(1, math.ceil(n / 5))
    size = math.ceil(n / k)
    per = math.ceil(len(s['cites']) / k) if s['cites'] else 0
    for j in range(k):
        a = s['a'] + j * size
        b = min(s['b'], a + size - 1)
        if a <= b:
            chunks.append({'a': a, 'b': b, 'cites': s['cites'][j * per:(j + 1) * per], 'sec': s['id']})

days_total = math.ceil((N1 + N2) / PACE)
v1_per_day = N1 / days_total
assigned = set()
thread = 0
plan = []
v1_done = 0


def take_block(bi, into):
    global v1_done
    if bi in assigned:
        return
    assigned.add(bi)
    b = blocks[bi]
    into.append(bi)
    v1_done += b['b'] - b['a'] + 1


ci = 0
day = 0
while ci < len(chunks) or len(assigned) < len(blocks):
    day += 1
    v2part = []
    v2pages = 0
    # Volume Two: ration so it spreads across the whole plan
    target2 = round(day * N2 / days_total)
    done2 = sum(c['b'] - c['a'] + 1 for d in plan for c in d['v2'])
    while ci < len(chunks) and (done2 + v2pages < target2 or not v2part):
        c = chunks[ci]
        v2part.append(c)
        v2pages += c['b'] - c['a'] + 1
        ci += 1
        if done2 + v2pages >= target2:
            break
    cited, threaded = [], []
    for c in v2part:
        for k in c['cites']:
            if k in key_block:
                take_block(key_block[k], cited)
    # Volume One thread: fill the day up to the pace
    def today():
        return v2pages + sum(blocks[x]['b'] - blocks[x]['a'] + 1 for x in cited + threaded)
    while thread < len(blocks) and today() < PACE:
        if thread not in assigned:
            nb = blocks[thread]['b'] - blocks[thread]['a'] + 1
            if today() > 0 and today() + nb > PACE + 3:
                break
            take_block(thread, threaded)
        thread += 1
    plan.append({'day': day, 'v2': v2part, 'cited': cited, 'thread': threaded})
    if ci >= len(chunks) and thread >= len(blocks):
        break


def size(d):
    return sum(c['b'] - c['a'] + 1 for c in d['v2']) + sum(blocks[x]['b'] - blocks[x]['a'] + 1 for x in d['cited'] + d['thread'])


# merge light neighbouring days so every session is close to a full one
merged_plan = []
for d in plan:
    if merged_plan and size(merged_plan[-1]) + size(d) <= PACE + 2:
        m = merged_plan[-1]
        m['v2'] += d['v2']; m['cited'] += d['cited']; m['thread'] += d['thread']
    else:
        merged_plan.append(d)
for i, d in enumerate(merged_plan, start=1):
    d['day'] = i
plan = merged_plan


def rng(a, b):
    return f'{a}' if a == b else f'{a}–{b}'


def pp(a, b):
    return ('p. ' if a == b else 'pp. ') + rng(a, b)


def merge_ranges(bis):
    out = []
    for bi in sorted(bis, key=lambda x: blocks[x]['a']):
        b = blocks[bi]
        if out and out[-1][1] + 1 == b['a']:
            out[-1] = (out[-1][0], b['b'], out[-1][2] + [bi])
        else:
            out.append((b['a'], b['b'], [bi]))
    return out


def esc(s):
    return html.escape(s, quote=False)


rows = []
for d in plan:
    w = (d['day'] - 1) // DAYS_PER_WEEK + 1
    v2txt = '<br>'.join(f'<b>{pp(c["a"], c["b"])}</b> {esc(v2_label(c["a"], c["b"]))}' for c in d['v2']) or '<span class="dim">Catch up, or reread</span>'
    v1bits = []
    for a, b, bis in merge_ranges(d['cited']):
        names = '; '.join(dict.fromkeys(v1_label(x) for x in bis))
        v1bits.append(f'<b>{pp(a, b)}</b> {esc(names)} <span class="tag">CITED</span>')
    for a, b, bis in merge_ranges(d['thread']):
        names = '; '.join(list(dict.fromkeys(v1_label(x) for x in bis))[:3]) + ('…' if len(bis) > 3 else '')
        v1bits.append(f'<b>{pp(a, b)}</b> {esc(names)}')
    total = sum(c['b'] - c['a'] + 1 for c in d['v2']) + sum(blocks[x]['b'] - blocks[x]['a'] + 1 for x in d['cited'] + d['thread'])
    rows.append((w, d['day'], v2txt, '<br>'.join(v1bits) or '<span class="dim">Nothing new</span>', total))

weeks = (len(plan) + DAYS_PER_WEEK - 1) // DAYS_PER_WEEK
units = ROOT / 'workbook' / 'units_v3'
units.mkdir(exist_ok=True)
for f in units.glob('*.tkc'):
    f.unlink()

front = f'''@cover
<div class="t1">THY<br>KINGDOM<br>COME</div>
<div class="orn">✥</div>
<div class="s1">VOLUMES ONE AND TWO</div>
<div class="s2">The Reading Plan</div>
<div class="s3">Which part of Volume One goes with which part of Volume Two, day by day, at {PACE} pages a day.</div>
<div class="s4">DANY · OCTOBER 2026</div>

@essay rh="THE READING PLAN · HOW IT WORKS"
# How the plan works
drop: Volume Two is the spine. You work through the people in story order, the Parish household first, then House Aurem, the twelve Covenant Daughters, the House of Vane and the 39th Trial. Each day pairs a stretch of Volume Two with the Volume One pages that stretch actually cites, so the scripture and the world are open beside the character they belong to.
Volume One pages marked CITED are the ones a Volume Two page sends you to by number. Everything else in Volume One runs alongside as a steady thread in book order, starting with Bible 101 and the sixty-six books, so the scripture study is spread across the whole plan instead of piled at the front. Both volumes finish on the same day.
A day is {PACE} pages, counting the writing pages. Some days run a little over because a dossier cites a long section, and the next day runs light to make up for it. Pages are counted from the full books, which match the split print files.
k: Recommended pace
{PACE} pages a day, five days a week, is about {math.ceil(len(plan) / DAYS_PER_WEEK)} weeks. Keep the other two days for the manuscript, or for catching up. The plan is {len(plan)} sessions in all, Volume One's {N1} pages and Volume Two's {N2}.
side:
k: The paces
stext: Light · 6 pages a day · about {math.ceil((N1 + N2) / 6 / DAYS_PER_WEEK)} weeks
stext: Recommended · {PACE} pages a day · about {math.ceil(len(plan) / DAYS_PER_WEEK)} weeks
stext: Intensive · 15 pages a day · about {math.ceil((N1 + N2) / 15 / DAYS_PER_WEEK)} weeks
k: Changing pace
stext: Doing two rows in a sitting is the intensive pace. Splitting a row over two sittings is the light one. The order still holds.
marg
/end
'''
(units / '00_front.tkc').write_text(front)

# the alignment map: each Volume Two dossier and the Volume One sections it cites
amap = ['@page rh="THE READING PLAN · THE ALIGNMENT MAP · 1" m="VOL. II → VOL. I"', '# What goes with what',
        'Each Volume Two section, and the Volume One sections it cites. Use this when you want to work one person all the way through instead of following the daily plan.',
        '<table class="amap"><tr><th>Volume Two</th><th>Volume One</th></tr>']
count, pg = 0, 1
LABEL = {}
for s in secs:
    if not s['cites']:
        continue
    lab = v2_label(s['a'], s['a'])
    bis = list(dict.fromkeys(key_block[k] for k in s['cites'] if k in key_block))
    v1s = '; '.join(f'{v1_label(bi)} ({rng(blocks[bi]["a"], blocks[bi]["b"])})' for bi in sorted(bis, key=lambda x: blocks[x]['a']))
    amap.append(f'<tr><td><b>{pp(s["a"], s["b"])}</b> {esc(lab)}</td><td>{esc(v1s)}</td></tr>')
    count += 1
    if count % 9 == 0:
        pg += 1
        amap += ['</table>', '', f'@page rh="THE READING PLAN · THE ALIGNMENT MAP · {pg}" m="VOL. II → VOL. I"', '# What goes with what, continued',
                 '<table class="amap"><tr><th>Volume Two</th><th>Volume One</th></tr>']
amap.append('</table>')
(units / '10_map.tkc').write_text('\n'.join(amap) + '\n')

# the day-by-day plan, one week to a page with room for notes under it
out = []
for wk in range(1, weeks + 1):
    out.append(f'@page rh="THE READING PLAN · DAY BY DAY · WEEK {wk} OF {weeks}" m="{PACE} PAGES A DAY; CHECK THE BOX WHEN DONE"')
    out.append(f'# Week {wk}')
    out.append('<table class="plan"><tr><th class="d">Day</th><th>Volume Two</th><th>Volume One</th><th class="n">Pages</th><th class="c">Done</th></tr>')
    for w, dnum, a, b, total in rows:
        if w == wk:
            out.append(f'<tr><td class="d">{dnum}</td><td>{a}</td><td>{b}</td><td class="n">{total}</td><td class="c"><span class="box"></span></td></tr>')
    out.append('</table>')
    out.append('prompt: This week, what I found and what moved in the manuscript | rest')
    out.append('')
(units / '20_plan.tkc').write_text('\n'.join(out) + '\n')

(units / '90_notes.tkc').write_text('@notes rh="THE READING PLAN · NOTES" m="NOTES" prompt="Where I am, and what I changed"\n')
print(f'{len(plan)} days, {weeks} weeks, {len(blocks)} Volume One blocks, all assigned: {len(assigned) == len(blocks)}')
