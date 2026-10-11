#!/usr/bin/env python3
"""Builds the Remnian Lineage Map from settled.py.

  python3 lineage_map/build_map.py   -> dist/Remnian_Lineage_Map.html
  node tools/print_map.mjs           -> dist/Remnian_Lineage_Map.pdf

The two family charts are laid out by hand (x, y per box) so the print stays stable.
"""
import html
from pathlib import Path

import settled as S

ROOT = Path(__file__).resolve().parent.parent
E = html.escape

W, H = 170, 0  # default box width; height comes from the line count
LINE = 16


# ------------------------------------------------------------------ chart model
class Chart:
    def __init__(self, width, height):
        self.width, self.height = width, height
        self.boxes, self.links = {}, []

    def box(self, key, x, y, lines, house, w=W, eyes=None, style=""):
        h = 30 + LINE * (len(lines) - 1) + (LINE if eyes else 0)
        self.boxes[key] = dict(x=x, y=y, w=w, h=h, lines=lines, house=house, eyes=eyes, style=style)

    def b(self, k):
        return self.boxes[k]


def cx(b):
    return b["x"] + b["w"] / 2


def svg_box(b):
    x, y, w, h = b["x"], b["y"], b["w"], b["h"]
    cls = "box " + b["style"]
    out = [f'<g class="{cls}">',
           f'<rect class="card" x="{x}" y="{y}" width="{w}" height="{h}" rx="3"/>',
           f'<rect class="band h-{b["house"]}" x="{x}" y="{y}" width="{w}" height="5" rx="1.5"/>']
    ty = y + 24
    for i, ln in enumerate(b["lines"]):
        c = "nm" if i == 0 else ("dt" if i == 1 else "ln")
        out.append(f'<text class="{c}" x="{x + 10}" y="{ty}">{E(ln)}</text>')
        ty += LINE + (2 if i == 0 else 0)
    if b["eyes"]:
        col, label = b["eyes"]
        out.append(f'<circle class="eye e-{col}" cx="{x + 15}" cy="{ty - 4}" r="4.5"/>')
        out.append(f'<text class="ln" x="{x + 25}" y="{ty}">{E(label)}</text>')
    out.append("</g>")
    return "\n".join(out)


def couple(ch, a, b, kind="m"):
    """Horizontal link between two boxes in the same row. kind: m (marriage), affair, legal."""
    A, B = ch.b(a), ch.b(b)
    y = A["y"] + 34
    x1, x2 = A["x"] + A["w"], B["x"]
    if kind == "m":
        ch.links.append(f'<path class="lk" d="M{x1} {y - 2}H{x2}M{x1} {y + 2}H{x2}"/>')
    else:
        ch.links.append(f'<path class="lk {kind}" d="M{x1} {y}H{x2}"/>')
    return ((x1 + x2) / 2, y)


def descend(ch, origin, kids, bus_y, kind=""):
    """origin: (x, y) point on a couple link, or a box key. Draws a drop to a bus, then to each child."""
    if isinstance(origin, str):
        o = ch.b(origin)
        ox, oy = cx(o), o["y"] + o["h"]
    else:
        ox, oy = origin
    xs = [cx(ch.b(k)) for k in kids]
    lo, hi = min(xs + [ox]), max(xs + [ox])
    d = [f"M{ox} {oy}V{bus_y}", f"M{lo} {bus_y}H{hi}"]
    for k in kids:
        c = ch.b(k)
        d.append(f"M{cx(c)} {bus_y}V{c['y']}")
    ch.links.append(f'<path class="lk {kind}" d="{"".join(d)}"/>')


def label(ch, x, y, text, cls="cap"):
    ch.links.append(f'<text class="{cls}" x="{x}" y="{y}">{E(text)}</text>')


def render(ch, title):
    parts = [f'<svg class="chart" viewBox="0 0 {ch.width} {ch.height}" role="img" aria-label="{E(title)}" '
             f'xmlns="http://www.w3.org/2000/svg">', *ch.links, *(svg_box(b) for b in ch.boxes.values()), "</svg>"]
    return "\n".join(parts)


# --------------------------------------------------------------- chart one
def imperial():
    ch = Chart(1720, 680)
    G0, G1, G2, G3 = 34, 190, 372, 560
    ch.box("eden", 352, G0, ["Eden Genesis Caliane Azira", "Founding Empress · d. c. 2080",
                             "m. Stephen Abraham Hastings", "Emperor Consort"], "hastings", w=250)
    # Eden's children
    ch.box("richard", 20, G1, ["Richard Hastings", "b. 2024", "Displaced Crown Prince", "m. Princess Ember"], "hastings")
    ch.box("madeleine", 205, G1, ["Madeleine Beatrix", "b. 2028", "m. Lord Felix D'Arcy", "Verdant branch"], "hastings")
    ch.box("victoria", 390, G1, ["Victoria Cassiopeia", "b. 2035", "Flamer", "m. Lord Adrian Wells"], "hastings")
    ch.box("alexandria", 575, G1, ["Alexandria Melena", "b. 2038 · Duchess of Alleia", "Aracelia's younger twin",
                                   "m. Lord Clyde Hastings"], "hastings")
    ch.box("aracelia", 760, G1, ["Aracelia Hastings", "b. 2038 · Empress c. 2080", "Frost",
                                 "m. Duke Jackson Harper", "of Zenithia, 2060"], "hastings", w=220)
    descend(ch, "eden", ["richard", "madeleine", "victoria", "alexandria", "aracelia"], G1 - 26)
    # Lockwood and Nicholas, Tobias's parents' generation
    ch.box("sawyer", 1070, G1, ["Sawyer & Rowena Lockwood", "b. c. 2007 · c. 2010",
                                "Duke and Duchess", "Lockwood Manor, Highcrest"], "lockwood", w=220)
    ch.box("celeste", 1430, G1, ["Celeste Nicholas", "born Lockwood · d. before 2076",
                                 "Sawyer's sister", "m. into the Nicholas house"], "nicholas", w=220)
    sx, cxx = cx(ch.b("sawyer")), cx(ch.b("celeste"))
    ch.links.append(f'<path class="lk sib" d="M{sx} {G1}V{G1 - 22}H{cxx}V{G1}"/>')
    label(ch, (sx + cxx) / 2, G1 - 30, "siblings · parents not named", "cap mid")
    # cousins' lists
    ch.box("c_rich", 20, G2, ["Olympia, Estelle", "b. 2058, 2059"], "hastings", style="list")
    ch.box("c_mad", 205, G2, ["Aveline, Isabella,", "Arabella", "b. 2060, 2063, 2064"], "hastings", style="list")
    ch.box("c_vic", 390, G2, ["Fiona", "b. 2065"], "hastings", style="list")
    ch.box("c_alex", 575, G2, ["Amalia, Evangeline", "b. 2062, 2063", "Clyde d. Nov 2096"], "hastings", style="list")
    for p, c in [("richard", "c_rich"), ("madeleine", "c_mad"), ("victoria", "c_vic"), ("alexandria", "c_alex")]:
        descend(ch, p, [c], G2 - 22)
    ch.box("sisters", 760, G2, ["Charlotte, Elaine,", "Arianne", "b. 2055 (Lucia's twin),", "2056, 2066"],
           "hastings", w=150, style="list")
    ch.box("lucia", 925, G2, ["Lucia Hastings-Lockwood", "26 Oct 2055 – 7 Sept 2094", "Crown Princess · Frost",
                              "car accident at 38"], "hastings", eyes=("gold", "Hastings gold eyes"))
    descend(ch, "aracelia", ["sisters", "lucia"], G2 - 22)
    ch.box("tobias", 1125, G2, ["Tobias Lockwood", "2 Aug 2035 – c. Mar 2095", "Prince Consort · Fire",
                                "godfather to Zoe, Orion"], "lockwood", eyes=("emerald", "Lockwood emerald eyes"))
    descend(ch, "sawyer", ["tobias"], G2 - 22)
    ch.box("michelle", 1325, G2, ["Michelle Nicholas", "b. c. 2050", "Conqueror c. 2070",
                                  "Lieutenant, En Guard"], "nicholas")
    ch.box("ethan", 1525, G2, ["Ethan Nicholas", "b. 18 Nov 2035", "Head of the Nicholas house",
                               "Tobias's first cousin"], "nicholas", w=180)
    descend(ch, "celeste", ["ethan"], G2 - 22)
    m_lt = couple(ch, "lucia", "tobias")
    m_tm = couple(ch, "tobias", "michelle", "affair")
    m_me = couple(ch, "michelle", "ethan")
    # the children
    kids = [("elias", "Elias Lockwood", "b. 3 Oct 2073", "Crown Prince · missing", ("gold", "Hastings gold eyes")),
            ("melena", "Melena Lockwood", "b. 9 Sept 2076", "Duchess of Rovencia · Fire", ("emerald", "Lockwood emerald eyes")),
            ("cordelia", "Cordelia Lockwood", "b. 2 Sept 2079", "Frost · Sawyer's ward", ("gold", "amber (Hastings) eyes")),
            ("louis", "Louis Lockwood", "b. 14 May 2081", "Richard's ward", None)]
    for i, (k, n, b, r, e) in enumerate(kids):
        ch.box(k, 620 + i * 178, G3, [n, b, r], "lockwood", w=164, eyes=e)
    descend(ch, m_lt, [k for k, *_ in kids], G3 - 30)
    ch.box("katherine", 1360, G3, ["Katherine Nicholas", "b. 14 July 2076", "Old Prosperity · Frost",
                                   "unacknowledged at FTE"], "nicholas", w=180, style="hidden")
    kx = cx(ch.b("katherine"))
    ch.links.append(f'<path class="lk" d="M{m_tm[0]} {m_tm[1]}V{G3 - 16}H{kx - 30}V{G3}"/>')
    ch.links.append(f'<path class="lk legal" d="M{m_me[0]} {m_me[1]}V{G3 - 16}H{kx + 30}V{G3}"/>')
    label(ch, m_tm[0] + 6, G3 - 22, "father", "cap")
    label(ch, m_me[0] + 6, G3 - 22, "father on record", "cap")
    for i, (cls, txt) in enumerate([("", "parent and child"), ("double", "marriage"), ("affair", "Tobias and Michelle"),
                                    ("legal", "legal father only"), ("sib", "siblings")]):
        x = 20 + i * 190
        y = ch.height - 20
        if cls == "double":
            ch.links.append(f'<path class="lk" d="M{x} {y - 6}h34M{x} {y - 2}h34"/>')
        else:
            ch.links.append(f'<path class="lk {cls}" d="M{x} {y - 4}h34"/>')
        label(ch, x + 42, y, txt, "cap")
    return ch


# --------------------------------------------------------------- chart two
def london():
    ch = Chart(1500, 560)
    G0, G1, G2 = 34, 190, 372
    ch.box("sam", 410, G0, ["Samantha Ruby Kinross", "First Queen of London Town",
                            "m. (1) King Edward XVIII, d. c. 2041–45", "m. (2) King Brenton, d. 2058"],
           "london", w=270)
    ch.box("sisters", 20, G1, ["Lauren · Angelica · Fallon", "b. 2024, 2035, 2040",
                               "Lauren gave up her place"], "london", w=210, style="list")
    ch.box("dalia", 400, G1, ["Dalia Lexington", "b. 31 Oct 2038 · Queen 2090",
                              "Duchess of Camor; of Rovencia", "until 2090, then Melena's"], "london", w=220)
    ch.box("david", 650, G1, ["David Augustine", "Prince Consort",
                              "son of Lord Alexander", "Augustine"], "london", w=170)
    ch.box("nathaniel", 980, G1, ["Nathaniel Kinross", "b. 24 Nov 2039",
                                  "King 2058 – June 2090", "birth-order rule"], "london")
    descend(ch, "sam", ["sisters", "dalia", "nathaniel"], G1 - 26)
    m = couple(ch, "dalia", "david")
    kids = [("maxim", ["Maxim", "b. 7 Sept 2072", "Crown Prince · Terrain"], None, ""),
            ("minho", ["Minho", "b. 12 Aug 2074", "gave up his place 2091"], None, "out"),
            ("zephyr", ["Zephyr", "b. 7 Sept 2075, elder", "by six minutes · Dyad"], ("emerald", "emerald eyes"), "out"),
            ("zoe", ["Zoe", "b. 7 Sept 2075", "Tobias's goddaughter"], ("violet", "violet eyes"), ""),
            ("sebastian", ["Sebastian", "b. 15 Aug 2076", "gave up his place 2095"], None, "out"),
            ("orion", ["Orion", "b. 1 Oct 2090", "Tobias's godson"], None, "")]
    for i, (k, lines, e, st) in enumerate(kids):
        ch.box(k, 20 + i * 166, G2, lines, "london", w=154, eyes=e, style=st)
    descend(ch, m, [k for k, *_ in kids], G2 - 30)
    ch.box("arielle", 1030, G2, ["Arielle Kinross", "The Princess Royal", "restored by Dalia"], "london", w=160)
    descend(ch, "nathaniel", ["arielle"], G2 - 22)
    # House Blackwood, kept apart
    ch.box("blackwood", 1245, G1, ["Alistair & Celeste Blackwood", "Duke and Lady, London Town",
                                   "not Celeste Nicholas"], "blackwood", w=225)
    ch.box("tiran", 1272, G2, ["Tiran Lucien Blackwood", "b. 15 April 2072", "second child · Flamer",
                               "ran routes with Remy"], "blackwood")
    descend(ch, "blackwood", ["tiran"], G2 - 22)
    label(ch, 1245, G1 - 14, "HOUSE BLACKWOOD", "cap hd")
    for i, (cls, txt) in enumerate([("out", "gave up their place"), ("double", "marriage")]):
        x, y = 20 + i * 230, ch.height - 20
        if cls == "out":
            ch.links.append(f'<rect class="card out-sw" x="{x}" y="{y - 12}" width="34" height="12" rx="2"/>')
        else:
            ch.links.append(f'<path class="lk" d="M{x} {y - 8}h34M{x} {y - 4}h34"/>')
        label(ch, x + 42, y, txt, "cap")
    return ch


# --------------------------------------------------------------- page
def chip(t):
    name, _ = S.TAGS[t]
    return f'<span class="tag t-{t}">{E(name)}</span>'


def page():
    imp, lon = imperial(), london()
    legend = "".join(f'<li>{chip(k)}<span>{E(v[1])}</span></li>' for k, v in S.TAGS.items())
    houses = [("hastings", "Mignonette, Hastings"), ("lockwood", "Lockwood"), ("nicholas", "Nicholas, Old Prosperity"),
              ("london", "Kinross, Augustine"), ("blackwood", "Blackwood")]
    hkey = "".join(f'<li><i class="sw h-{k}"></i>{E(v)}</li>' for k, v in houses)
    eyes = "".join(f'<li><i class="dot e-{k}"></i>{E(v)}</li>' for k, v in S.EYES.items())

    succ = []
    for realm, head, rows, note in S.SUCCESSION:
        lis = "".join(f'<li><b>{E(n)}</b><span>{E(who)}</span><em>{E(d)}</em></li>' for n, who, d in rows)
        succ.append(f'<div class="realm"><h3>{E(realm)}</h3><p class="sub">{E(head)}</p><ol>{lis}</ol>'
                    f'<p class="note">{E(note)}</p></div>')

    cal = "".join(f'<tr><td class="when">{E(d)}</td><td>{E(w)}</td><td>{chip(t)}</td></tr>' for d, w, t in S.CALENDAR)

    rec = []
    for head, intro, people in S.RECORD:
        ps = []
        for name, life, rows in people:
            rs = "".join(f'<dt>{E(f)}</dt><dd><span>{E(v)}</span>{chip(t)}</dd>' for f, v, t in rows)
            ps.append(f'<article class="person"><h4>{E(name)}</h4><p class="life">{E(life)}</p><dl>{rs}</dl></article>')
        intro_html = f'<p class="intro">{E(intro)}</p>' if intro else ""
        rec.append(f'<section class="house"><h3>{E(head)}</h3>{intro_html}{"".join(ps)}</section>')

    rev = "".join(f'<tr><td class="src">{E(s)}</td><td>{E(o)}</td><td>{E(n)}</td></tr>' for s, o, n in S.REVISIONS)
    chk = "".join(f'<li class="k-{k.lower()}"><span class="verdict">{E(k)}</span><div><b>{E(t)}</b> {E(x)}</div></li>'
                  for k, t, x in S.CHECK_3SL)
    still = "".join(f"<li>{E(x)}</li>" for x in S.STILL_OPEN)

    css = (ROOT / "lineage_map" / "map.css").read_text()
    return f"""<title>Remnian Lineage Map</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&family=Barlow+Condensed:wght@500;600;700&family=JetBrains+Mono:wght@400;600&display=swap">
<style>
{css}
</style>
<main class="wrap">
<header class="mast">
  <p class="eyebrow">For Their Entertainment · 3 Shadowmere Lane · the Remnian lineage</p>
  <h1>Remnian Lineage Map</h1>
  <p class="deck">Settled 11 October 2026 from your answers in the Suggestions Workbook, the four follow-up answers,
  and a check against the 3SL outline. It's a working map, not a manuscript source: where it contradicts a drafted line,
  the line is listed at the end for revision.</p>
  <p class="anchor"><b>The fixed anchor.</b> {E(S.ANCHOR)}</p>
  <div class="keys">
    <div><h2 class="mini">Where each line came from</h2><ul class="legend">{legend}</ul></div>
    <div><h2 class="mini">Houses</h2><ul class="hkey">{hkey}</ul>
         <h2 class="mini">Eyes</h2><ul class="hkey">{eyes}</ul></div>
  </div>
</header>

<section class="sheet" id="imperial">
  <div class="sheet-hd"><span class="code">I</span><div><h2>The imperial house</h2>
  <p>Eden to Lucia's children, with House Lockwood and the Nicholas house of Meridion. Katherine's box is dashed:
  at FTE she isn't acknowledged.</p></div></div>
  <div class="scroller">{render(imp, "Family chart of the imperial house")}</div>
</section>

<section class="sheet" id="london">
  <div class="sheet-hd"><span class="code">II</span><div><h2>London Town, and House Blackwood</h2>
  <p>Kinross becomes Augustine through David. House Blackwood stands apart: its Celeste is not Tobias's aunt.</p></div></div>
  <div class="scroller">{render(lon, "Family chart of London Town and House Blackwood")}</div>
</section>

<section class="block" id="succession">
  <h2>Succession when FTE opens</h2>
  <div class="realms">{"".join(succ)}</div>
</section>

<section class="block" id="calendar">
  <h2>The settled calendar</h2>
  <div class="tscroll"><table class="cal"><thead><tr><th>When</th><th>What happens</th><th>From</th></tr></thead>
  <tbody>{cal}</tbody></table></div>
</section>

<section class="block" id="record">
  <h2>The record, person by person</h2>
  {"".join(rec)}
</section>

<section class="block" id="revisions">
  <h2>Lines in the drafts that now need changing</h2>
  <p class="intro">Each of these is a line in an existing file that the settled lineage contradicts. Nothing here has been edited.</p>
  <div class="tscroll"><table class="rev"><thead><tr><th>File</th><th>It says</th><th>Change to</th></tr></thead>
  <tbody>{rev}</tbody></table></div>
</section>

<section class="block" id="check">
  <h2>Checked against the 3SL outline</h2>
  <ul class="check">{chk}</ul>
</section>

<section class="block" id="open">
  <h2>Still open</h2>
  <ul class="open">{still}</ul>
</section>
</main>
"""


if __name__ == "__main__":
    out = ROOT / "dist" / "Remnian_Lineage_Map.html"
    out.write_text(page())
    print("written", out)
