#!/usr/bin/env python3
"""Build 1 — standalone 3 Shadowmere Lane / Underside Companion.

Reads the locked copy (src/content_master.md), the production rules
(src/production_master.md) and the source-authority audit (src/audit.md),
applies the logged author corrections (src/corrections.json), and writes
out/book.html: every printed block in reading order, tagged for the
paginator (tools/paginate.js). Layout only — no copy is authored here
except volume apparatus (title page, contents, scope note, concordance
lead), which is marked as such in the QA report.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
OUT = ROOT / "out"

CM = (SRC / "content_master.md").read_text()
PM = (SRC / "production_master.md").read_text()
AUDIT = (SRC / "audit.md").read_text()
CORR = json.loads((SRC / "corrections.json").read_text())

BUILD_DATE = "2026-10-09"

# ---------------------------------------------------------------- scope
PART_II_SCOPE = ["II.2", "II.3", "II.4", "II.5", "II.14", "II.16"]

STATIONS = {"SPINE": (0, "#2B2B2B"), "3SL": (1, "#74399A"), "FTE": (2, "#B8332A"),
            "ADST": (3, "#2C63C4"), "TSWK": (4, "#0E7F74"), "CONTINUITY": (5, "#C46F0D")}

# Page-type kind lines (from Production Master "Treatment" + V5 catalog)
KIND = {
    "I.1": "ORIENTATION", "I.2": "RULE", "I.3": "SOURCE AUTHORITY", "I.4": "STATUS KEY",
    "I.5": "EXPLAINER", "I.6": "PROTOCOL", "I.7": "CHECKLIST",
    "II.2": "SCHEMATIC", "II.3": "EXPLAINER", "II.4": "EXPLAINER · LADDER",
    "II.5": "EXPLAINER · TABLE", "II.14": "EXPLAINER · CAN/CANNOT", "II.16": "TIMELINE",
    "III.1": "STATUS & PROVENANCE SHEET", "III.2": "CANON SNAPSHOT", "III.3": "EXPLAINER · CROSS-SECTION",
    "III.4": "PLACE DOSSIER", "III.5": "FACTION TABLE", "III.6": "ROUTE ENTRIES",
    "III.7": "REFERENCE TABLE", "III.8": "EXPLAINER", "III.9": "DOSSIER · PROTAGONIST",
    "III.10": "DOSSIER · PROTAGONIST", "III.11": "MECHANICS EXPLAINER", "III.12": "TWO-LANE PROGRESSION",
    "III.13": "CAST TABLE", "III.14": "PAIRED DOSSIER", "III.15": "BEAT SHEET + MEMORY TRANSLATION",
    "III.16": "PERFORMANCE RECORD", "III.17": "TRACKER", "III.18": "HANDOFF TABLE",
    "III.19": "DRAFT-FORWARD PACKET", "III.20": "OPEN DEVELOPMENT",
    "III.20W": "WORKING PAGES · ITEMS A–E", "CR": "CONCORDANCE",
}
DISP = {"III.20W": "III.20", "CR": "VII·3SL"}
PART_NAME = {"I": "PART I · HOW THIS COMPANION WORKS",
             "II": "PART II · THE SHARED TANDEM SPINE",
             "III": "PART III · 3 SHADOWMERE LANE / THE UNDERSIDE"}

# Tracker tables that arrive half-filled get blank rows (V9: the writer extends).
BLANK_ROWS = {
    ("III.2", "planted pressure"): 2, ("III.4", "place"): 2, ("III.6", "route"): 3,
    ("III.6", "character"): 2, ("III.9", "knowledge"): 3, ("III.11", "person"): 2,
    ("III.12", "ch."): 4, ("III.13", "character"): 3, ("III.17", "drafted facts (chs. 1–22)"): 3,
    ("III.17", "character"): 2, ("III.19", "choice"): 3, ("III.20", "item"): 4,
}
# Writing-application tables: the empty column is the writing space.
ANSWER_HEADERS = {"your answer for the next severance", "your answer"}

LINE = 30  # handwriting line pitch, px (production rules floor)


def esc(s):
    return html.escape(s, quote=False)


# ---------------------------------------------------------------- titles / purposes
def pm_entries():
    """code -> (title, purpose, content) from the Production Master TOC."""
    out = {}
    for m in re.finditer(r"^\*\*((?:I|II|III|IV|V|VI|VII)\.\d+) ([^*]+)\*\*\n\n((?:- .*\n)+)", PM, re.M):
        code, title, body = m.group(1), m.group(2).strip(), m.group(3)
        pur = re.search(r"- \*\*Purpose:\*\* (.*)", body)
        con = re.search(r"- \*\*Content:\*\* (.*)", body)
        out[code] = (title, pur.group(1).strip() if pur else "", con.group(1).strip() if con else "")
    return out


PME = pm_entries()


def section_title(code):
    return PME.get(code, ("", "", ""))[0].replace("\\", "")


# ---------------------------------------------------------------- slicing the Content Master
def apply_corrections(text):
    for c in CORR["corrections"]:
        if c["find"] not in text:
            raise SystemExit(f"correction anchor not found: {c['id']}")
        text = text.replace(c["find"], c["replace"], 1)
    return text


CMX = apply_corrections(CM)


def cm_sections():
    """Return ordered list of (part, code, title, lines) plus part intros."""
    lines = CMX.split("\n")
    parts, secs = {}, []
    cur_part, cur = None, None
    for ln in lines:
        m2 = re.match(r"^## Part (I|II|III|IV|V|VI|VII) — (.*)", ln)
        m3 = re.match(r"^### ((?:I|II|III|IV|V|VI|VII)\.\d+) (.*)", ln)
        if m2:
            cur_part = m2.group(1)
            parts[cur_part] = {"title": m2.group(2).strip(), "lines": []}
            cur = None
            continue
        if m3:
            cur = {"part": cur_part, "code": m3.group(1), "title": m3.group(2).strip(), "lines": []}
            secs.append(cur)
            continue
        if cur is None and cur_part:
            parts[cur_part]["lines"].append(ln)
        elif cur is not None:
            cur["lines"].append(ln)
    return parts, secs


PARTS, SECS = cm_sections()
SEC_BY_CODE = {s["code"]: s for s in SECS}
CM_TITLES = {s["code"]: s["title"] for s in SECS}
CM_TITLES["III.20W"] = "III.20 Working Section: Items A–E"
CM_TITLES["CR"] = "Continuity Room: 3SL Concordance"


def in_scope(code):
    p = code.split(".")[0]
    return p in ("I", "III") or code in PART_II_SCOPE


# Codes that resolve inside this volume to the Continuity Room concordance.
CONCORDANCE = ["VII.1", "VII.2", "VII.3", "VII.4", "VII.5", "VII.7", "VII.10", "VII.12", "IV.14", "IV.15", "IV.17"]


def ref_title(code):
    return CM_TITLES.get(code) or section_title(code) or ""


# ---------------------------------------------------------------- inline markdown
BADGES = [
    (r"\\\[C\\\] CANON", "c", "CANON"), (r"\\\[C\\\]", "c", "CANON"),
    (r"\\\[\?\\\] OPEN", "o", "OPEN"), (r"\\\[\?\\\]", "o", "OPEN"),
    (r"\\\[P\\\] POSSIBLE", "p", "POSSIBLE"), (r"\\\[P\\\]", "p", "POSSIBLE"),
    (r"\\\[X\\\] CONFLICT", "x", "CONFLICT"), (r"\\\[X\\\]", "x", "CONFLICT"),
    (r"(?:&#91;|\\\[)R\\\] RESEARCH", "r", "RESEARCH"),
    (r"CURRENT DRAFTED TEXT", "d", "CURRENT DRAFTED TEXT"),
    (r"SUPPORTED / PROVISIONAL", "s", "SUPPORTED / PROVISIONAL"),
    (r"\bSUPPORTED\b(?! /)", "s", "SUPPORTED"),
    (r"LEGACY / SUPERSEDED", "l", "LEGACY / SUPERSEDED"),
    (r"\bDRAFTED\b(?= —| ·|$)", "d", "DRAFTED"),
]
REF_RE = re.compile(r"(?<![\w.§/-])((?:VII|VI|IV|V|III|II|I)\.\d+)(?![\d\w])")
PART_RE = re.compile(r"\bPart (VII|VI|IV|V|III|II|I)\b")
APP_RE = re.compile(r"\bAppendix ([A-E])\b")


def badge(cls, word):
    return f'<span class="sc {cls}"><i></i>{word}</span>'


def inline(s, refs=True):
    s = s.replace("&#91;", "\\[")
    tokens = []

    def tok(html_):
        tokens.append(html_)
        return f"\x01{len(tokens) - 1}\x02"

    # status markers (on the raw markdown, before escaping)
    for pat, cls, word in BADGES:
        s = re.sub(pat, lambda m, c=cls, w=word: tok(badge(c, w)), s)
    s = s.replace("\\[", "[").replace("\\]", "]")
    if refs:
        def ref_sub(m):
            pre = s[max(0, m.start() - 18):m.start()]
            if re.search(r"(Production Master|Master Instructions|Architecture) $", pre):
                return m.group(0)
            return tok(f'<span class="xr" data-ref="{m.group(1)}">{m.group(1)}</span>')
        s = REF_RE.sub(ref_sub, s)
        s = PART_RE.sub(lambda m: tok(f'<span class="xr" data-ref="Part {m.group(1)}">Part {m.group(1)}</span>'), s)
        s = APP_RE.sub(lambda m: tok(f'<span class="xr" data-ref="Appendix {m.group(1)}">Appendix {m.group(1)}</span>'), s)
    s = esc(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", s)
    # unmatched italic toggles from split source lines
    s = re.sub(r"(?<=\s)\*(?=[\w(])", "", s)
    s = re.sub(r"(?<=[\w).;])\*(?=\s|$)", "", s)
    s = re.sub(r"^\*|\*$", "", s)
    s = re.sub(r"\x01(\d+)\x02", lambda m: tokens[int(m.group(1))], s)
    s = s.replace("→", '<span class="ar">→</span>')
    return s


def plain(s):
    """Plain text of a markdown fragment (for QA comparison)."""
    t = re.sub(r"<[^>]+>", "", inline(s, refs=False))
    return html.unescape(t)


# ---------------------------------------------------------------- block parsing
def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", line)]


def parse_blocks(lines):
    blocks, i = [], 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1
            continue
        if ln.startswith(">"):
            q = []
            while i < len(lines) and lines[i].startswith(">"):
                q.append(lines[i][1:].lstrip())
                i += 1
            blocks.append(("quote", q))
            continue
        if ln.startswith("|"):
            t = []
            while i < len(lines) and lines[i].startswith("|"):
                t.append(lines[i])
                i += 1
            rows = [split_row(r) for r in t if not re.match(r"^\|\s*-{3}", r)]
            blocks.append(("table", rows))
            continue
        if re.match(r"^- \[ \] ", ln):
            items = []
            while i < len(lines) and re.match(r"^- \[ \] ", lines[i]):
                items.append(lines[i][6:])
                i += 1
            blocks.append(("check", items))
            continue
        if ln.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(lines[i][2:])
                i += 1
            blocks.append(("ul", items))
            continue
        if re.match(r"^\d+\. ", ln):
            items = []
            while i < len(lines) and re.match(r"^\d+\. ", lines[i]):
                items.append(re.sub(r"^\d+\. ", "", lines[i]))
                i += 1
            blocks.append(("ol", items))
            continue
        if ln.startswith("*Source —"):
            blocks.append(("source", ln))
            i += 1
            continue
        if ln.startswith("See also:"):
            blocks.append(("seealso", ln))
            i += 1
            continue
        if re.match(r"^\*\*[^*]+\*\*$", ln.strip()):
            blocks.append(("sub", ln.strip()[2:-2]))
            i += 1
            continue
        blocks.append(("p", ln))
        i += 1
    return blocks


# ---------------------------------------------------------------- HTML emitters
OUTPUT = []
QA_SOURCE_TEXT = []  # (sec, plain text) of every Content Master block that prints


def emit(h):
    OUTPUT.append(h)


def attrs(sec, **kw):
    a = f' data-sec="{sec}"'
    for k, v in kw.items():
        if v is None or v is False:
            continue
        a += f' data-{k.replace("_", "-")}="{v}"'
    return a


def ds_row():
    return ('<div class="ds"><span class="ck"><b></b>SAFE TO DEFER</span><span class="fl">DECIDE BY<u></u></span>'
            '<span class="ck"><b></b>DECIDED</span><span class="fl">LOG<u></u></span><span class="fl">DATE<u></u></span></div>')


def writable(sec, label, min_lines, weight=1, decision=True, label_html=None, extra_cls=""):
    lab = label_html if label_html is not None else f'<div class="sh">{esc(label)}</div>'
    return (f'<div class="wr {extra_cls}"{attrs(sec, flex=weight)}>{lab}'
            f'<div class="rl" data-min="{min_lines}" style="height:{min_lines * LINE}px"></div>'
            f'{ds_row() if decision else ""}</div>')


def callout(sec, q):
    """Blockquote callouts: GUARDRAIL, NOT THE SAME AS, OPEN DEVELOPMENT, etc."""
    paras, cur = [], []
    for l in q:
        if l.strip() == "":
            if cur:
                paras.append(" ".join(cur))
                cur = []
        else:
            cur.append(l)
    if cur:
        paras.append(" ".join(cur))
    for p_ in paras:
        body_ = re.sub(r"^\*\*[^*]+\*\*\s*(?:—\s*)?", "", p_)
        lab_ = re.match(r"^\*\*([^*]+)\*\*", p_)
        if lab_:
            QA_SOURCE_TEXT.append((sec + "#label", plain(lab_.group(1))))
        if body_.strip():
            QA_SOURCE_TEXT.append((sec, plain(body_)))
    first = paras[0]
    m = re.match(r"^\*\*(.+?)\*\*\s*(?:—\s*)?(.*)$", first)
    label, rest = (m.group(1), m.group(2)) if m else ("", first)
    label_plain = plain(label)
    up = label_plain.upper()
    if up.startswith("OPEN DEVELOPMENT"):
        title = label_plain.split("—", 1)[1].strip() if "—" in label_plain else ""
        cells = []
        for p in paras[1:]:
            mm = re.match(r"^\*\*(Fixed|Undecided|Why it matters|Decide by):\*\*\s*(.*)$", p)
            if mm:
                cells.append(f'<div><b>{mm.group(1).upper()}</b>{inline(mm.group(2))}</div>')
            else:
                cells.append(f'<div class="full">{inline(p)}</div>')
        lt = f'OPEN DEVELOPMENT{" · " + esc(title.upper()) if title else ""} · {badge("o", "OPEN")}'
        h = f'<div class="lg od"{attrs(sec, keep_next="1" if sec.startswith("III.") else None)}><span class="lt">{lt}</span><div class="og">{"".join(cells)}</div></div>'
        emit(h)
        if sec.startswith("III."):
            emit(writable(sec, f"WORKING SPACE · {title.upper()}", 6, weight=2))
        return
    if up.startswith("TANDEM CANON DECISION"):
        body = "".join(f"<p>{inline(p)}</p>" for p in paras[1:])
        emit(f'<div class="lg tcd"{attrs(sec)}><span class="lt">{esc(up)}</span>{body}</div>')
        return
    kind = "gr"
    if up.startswith("NOT THE SAME AS"):
        kind = "nsa"
    elif "CONFLICT" in up:
        kind = "cf"
    elif "FLAG" in up or "NOTE" in up:
        kind = "nt"
    lt = esc(label_plain.split("—")[0].strip().upper()) if kind != "cf" else badge("x", "CONFLICT") + esc(re.sub(r"^CONFLICT\s*", "", label_plain).split("—")[0].strip().upper())
    sub = label_plain.split("—", 1)[1].strip() if "—" in label_plain else ""
    body = ""
    if sub:
        body += f'<div class="gh">{esc(sub)}</div>'
    if rest:
        body += f'<p>{inline(rest)}</p>'
    for p in paras[1:]:
        body += f'<p>{inline(p)}</p>'
    if kind == "gr" and not sub and len(paras) == 1 and len(rest) < 120:
        body = f'<div class="gt">{inline(rest)}</div>'
    emit(f'<div class="lg {kind}"{attrs(sec)}><span class="lt">{lt}</span>{body}</div>')


def table_html(sec, rows, caption=None):
    head, body = rows[0], rows[1:]
    hl = [plain(h).lower() for h in head]
    for r_ in rows:
        for c_ in r_:
            if plain(c_).strip():
                QA_SOURCE_TEXT.append((sec + ("#th" if r_ is rows[0] else ""), plain(c_)))
    cap = (caption or "").lower()
    answer_cols = [k for k, h in enumerate(hl) if h in ANSWER_HEADERS]
    status_cols = [k for k, h in enumerate(hl) if h == "status"]
    beat = sec == "III.15" and cap == "beat sheet"
    short_first = all(len(plain(r[0])) <= 34 for r in body if r and r[0])
    cls = "tb" + (" fc" if short_first and len(head) > 1 else "") + (" beat" if beat else "")
    nblank = 0
    for (s, h0), n in BLANK_ROWS.items():
        if s == sec and hl[0] == h0:
            nblank = n
    th = "".join(f"<th>{inline(h, refs=False)}</th>" for h in head)
    if beat:
        th = "<th>STATUS</th><th>#</th><th>FIXED BEAT</th><th>OPEN CHOICES · DRAFTING SPACE</th>"
    trs = []
    for r in body:
        r = r + [""] * (len(head) - len(r))
        if beat:
            num, beat_t, status, openc = r
            st = inline(status)
            gutter = f'<td class="g">{st}</td>'
            trs.append(f'<tr>{gutter}<td class="n">{inline(num)}</td><td class="x">{inline(beat_t)}</td>'
                       f'<td class="dr">{inline(openc)}<div class="rl" data-min="3" style="height:{3 * LINE}px"></div></td></tr>')
            continue
        tds = []
        for k, c in enumerate(r):
            if k in answer_cols:
                tds.append(f'<td class="ans"><div class="rl" data-min="4" style="height:{4 * LINE}px"></div></td>')
            elif k in status_cols:
                tds.append(f'<td class="st">{inline(c)}</td>')
            else:
                tds.append(f"<td>{inline(c)}</td>")
        trs.append("<tr>" + "".join(tds) + "</tr>")
    for _ in range(nblank):
        trs.append('<tr class="blank">' + "".join('<td><div class="rl" data-min="2" style="height:60px"></div></td>' for _ in head) + "</tr>")
    cg = ""
    if answer_cols:
        ws = []
        for k, h in enumerate(hl):
            ws.append("" if k in answer_cols else ("84px" if h in ("law",) else ("" if k == 0 else "60px")))
        if len(head) == 3:
            ws = ["300px", "84px", ""]
        elif len(head) == 2:
            ws = ["300px", ""]
        cg = "<colgroup>" + "".join(f'<col style="width:{w}">' if w else "<col>" for w in ws) + "</colgroup>"
    return f'<table class="{cls}"{attrs(sec, split="1")}>{cg}<thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table>'


def see_also(sec, line):
    for r_ in line.split(":", 1)[1].split(","):
        QA_SOURCE_TEXT.append((sec + "#ref", r_.strip().rstrip(".")))
    refs = [r.strip().rstrip(".") for r in line.split(":", 1)[1].split(",")]
    chips = "".join(f'<span class="chip" data-ref="{esc(r)}">{esc(r)}</span>' for r in refs)
    emit(f'<div class="seealso"{attrs(sec)}><span class="sal">SEE ALSO</span>{chips}</div>')


def source_line(sec, line):
    QA_SOURCE_TEXT.append((sec, plain(re.sub(r"^\*Source — ", "*", line.strip()))))
    body = line.strip()
    body = re.sub(r"^\*Source — ", "*", body)
    emit(f'<div class="src"{attrs(sec)}><span class="srl">SOURCE</span><span class="srt">{inline(body)}</span></div>')


DESIGN_NOTE = re.compile(r"\s*\*\(Design note: [^)]*\)\*")


def render_blocks(sec, blocks):
    pending_caption = None
    for k, (typ, val) in enumerate(blocks):
        if typ == "p":
            dn = DESIGN_NOTE.search(val)
            if dn:
                QA_SOURCE_TEXT.append((sec + "#designnote", plain(dn.group(0))))
                val = DESIGN_NOTE.sub("", val)
                if not val.strip():
                    continue
            QA_SOURCE_TEXT.append((sec, plain(val)))
            if sec == "II.2" and val.startswith("**Schematic, not a map.**"):
                emit(f'<p{attrs(sec, keep_next="1")}>{inline(val)}</p>')
                emit(f'<div class="placeholder"{attrs(sec)}><span class="lt">SCHEMATIC · PLACEHOLDER</span>'
                     '<div class="phx">Relative-position schematic pending review of Danyelle’s canonical Remnia map.'
                     '<br>No coastlines, scale, compass, or place names are drawn in this volume.</div></div>')
                continue
            emit(f"<p{attrs(sec)}>{inline(val)}</p>")
        elif typ == "sub":
            QA_SOURCE_TEXT.append((sec, plain(val)))
            pending_caption = plain(val)
            emit(f'<div class="sh cap"{attrs(sec, keep_next="1")}>{inline(val)}</div>')
            continue
        elif typ == "table":
            emit(table_html(sec, val, pending_caption))
        elif typ == "quote":
            callout(sec, val)
        elif typ in ("ul", "ol"):
            for x_ in val:
                QA_SOURCE_TEXT.append((sec, plain(x_)))
            tag = typ
            emit(f'<{tag} class="lst"{attrs(sec)}>' + "".join(f"<li>{inline(x)}</li>" for x in val) + f"</{tag}>")
        elif typ == "check":
            for x_ in val:
                QA_SOURCE_TEXT.append((sec, plain(x_)))
            emit(f'<ul class="chk"{attrs(sec)}>' + "".join(f"<li><span class=\"bx\"></span><span>{inline(x)}</span></li>" for x in val) + "</ul>")
        elif typ == "source":
            source_line(sec, val)
        elif typ == "seealso":
            see_also(sec, val)
        pending_caption = None if typ != "sub" else pending_caption


def opener(sec, code_disp, kind, title, deck, station, extra=""):
    color = STATIONS[station][1]
    d = f'<div class="deck">{esc(deck)}</div>' if deck else ""
    emit(f'<div class="hd"{attrs(sec, newpage="1")}><div class="code" style="color:{color}">{esc(code_disp)}</div>'
         f'<div><div class="kind">{kind}</div><h1 class="t">{esc(title)}</h1>{d}</div></div>{extra}')


SECMETA = {}


def meta(sec, station, crumb, running, notes=False, work=False, folio=None, part=None):
    SECMETA[sec] = {"station": STATIONS[station][0], "color": STATIONS[station][1], "crumb": crumb,
                    "running": running, "notes": notes, "work": work, "folio": folio or sec, "part": part}


# ---------------------------------------------------------------- front matter (volume apparatus)
def front_matter():
    meta("TITLE", "3SL", "", "", folio="")
    emit(f'<div class="titlepg"{attrs("TITLE", newpage="1")}>'
         '<div class="tk">THE TANDEM COMPANION · BUILD 1</div>'
         '<div class="tt">3 Shadowmere Lane</div><div class="ts">The Underside</div>'
         '<div class="tsub">Standalone 3SL Companion · Reference + Working Pages</div>'
         '<div class="tmeta">'
         '<div><b>AUTHORED COPY</b>The Tandem Companion — Content Master, Stage 3 · Sep 26, 2026</div>'
         '<div><b>PRODUCTION SYSTEM</b>The Tandem Companion — Production Master · Direction C</div>'
         '<div><b>SOURCE AUTHORITY</b>Tandem Source Authority Audit — Working Record · Sep 26, 2026</div>'
         '<div><b>AUTHOR RULINGS</b>TCD-001–064 · Graveshand five laws (2026-08-22) · Underside tier status (2026-10-09)</div>'
         f'<div><b>ASSEMBLED</b>{BUILD_DATE}</div>'
         '</div></div>')

    meta("ABOUT", "3SL", "BUILD 1 › ABOUT THIS VOLUME", "ABOUT THIS VOLUME", folio="ABOUT")
    opener("ABOUT", "B1", "VOLUME NOTE · BUILD 1", "About This Volume", "What this standalone volume holds, and how to read its references.", "3SL")
    for p in [
        "This is Build 1 of the Tandem Companion: a standalone working volume for <i>3 Shadowmere Lane</i> and the Underside. "
        "It carries Part I (how the Companion works) in full, the Part II sections a 3SL scene stands on, and all of Part III. "
        "The copy is the locked Stage 3 Content Master; this volume lays it out and adds working pages. It doesn’t add canon.",
        "Some pages point to sections that live only in the full Tandem Companion. Two conventions keep those pointers honest:",
    ]:
        emit(f'<p{attrs("ABOUT")}>{p}</p>')
    emit(f'<ul class="lst"{attrs("ABOUT")}>'
         '<li><b>Continuity Room pointers resolve here.</b> References to VII.1, VII.2, VII.3, VII.4, VII.5, VII.7, VII.10 and VII.12, and to the FTE sections IV.14, IV.15 and IV.17, '
         'lead to the 3SL Continuity Room concordance near the end of this volume, which names where the 3SL information already sits in these pages.</li>'
         '<li><b>Everything else outside the volume carries a dagger (†).</b> A reference marked † is to a section of the full Tandem Companion that isn’t printed here.</li>'
         '<li><b>Page numbers.</b> “See also” chips give the page where each in-volume section starts.</li></ul>')
    emit(f'<div class="sh cap"{attrs("ABOUT", keep_next="1")}>Author correction applied in this volume</div>')
    emit(f'<p{attrs("ABOUT")}>One author ruling post-dates the Content Master and is applied wherever the claim appears (III.3; III.20 working pages): '
         'the Underside tier status. It is logged in Appendix A under “Author rulings without a TCD number.”</p>')
    emit(f'<div class="lg rul"{attrs("ABOUT")}><span class="lt">AUTHOR RULING · 2026-10-09 · UNDERSIDE TIER STATUS</span>'
         + "".join(f'<div class="rr">{badge(c, w)}<div>{t}</div><div class="pv">{pv}</div></div>' for c, w, t, pv in RULING_TIERS) +
         '</div>')
    emit(f'<div class="sh cap"{attrs("ABOUT", keep_next="1")}>What isn’t in this volume</div>')
    emit(f'<p{attrs("ABOUT")}>Parts IV–VII (FTE, ADST, TSWK and the full Continuity Room), the Part II sections that don’t bear on 3SL (II.1, II.6–II.13, II.15), '
         'and Appendix D. The appendices printed here are 3SL slices: the rulings, conflicts, sources and terms this volume cites.</p>')

    meta("TOC", "3SL", "BUILD 1 › CONTENTS", "CONTENTS", folio="CONTENTS")
    opener("TOC", "B1", "CONTENTS · BUILD 1", "Contents", "", "3SL")
    emit(f'<div id="toc-src"{attrs("TOC")}></div>')


RULING_TIERS = [
    ("c", "CANON", "The Underside is vertically tiered and attached to Zenithia’s side of Remnia; Crownlight and Dawnveil are surface/above-ground tiers; the nation is fully underground by Ironcross.", "TCD-025 · TCD-026"),
    ("d", "DRAFTED", "The Underside has nine tiers; Halflight’s old route board lists all nine in order.", "3SL ch. 10"),
    ("s", "SUPPORTED", "Tier functions and other worldbuilding detail where not independently drafted or ruled.", "3SL Full Worldbuilding"),
]


# ---------------------------------------------------------------- parts
def divider(part, codes, intro_lines, note=None):
    sec = f"PART-{part}"
    station = "3SL" if part == "III" else "SPINE"
    meta(sec, station, f"{'3SL' if part == 'III' else 'SPINE'} › PART {part}", f"PART {part}", folio=f"PART {part}")
    big = f'<div class="pnum">{part}</div>'
    title = PARTS[part]["title"]
    emit(f'<div class="dv"{attrs(sec, newpage="1")}>{big}<div><div class="kind">PART {part} · BUILD 1</div><h1 class="pt">{esc(title)}</h1></div></div>')
    blocks = parse_blocks(intro_lines)
    render_blocks(sec, blocks)
    rows = "".join(
        f'<tr><td><span class="nd"></span></td><td class="cd">{DISP.get(c, c)}</td><td class="ti">{esc(CM_TITLES.get(c, c))}</td>'
        f'<td><span class="chip">{esc(KIND.get(c, ""))}</span></td><td class="pgn" data-pref="{c}"></td></tr>' for c in codes)
    emit(f'<table class="sr"{attrs(sec, split="1")}><thead><tr><th></th><th>§</th><th>SECTION</th><th>PAGE TYPE</th><th>PAGE</th></tr></thead><tbody>{rows}</tbody></table>')
    if note:
        emit(f'<p class="dvn"{attrs(sec)}>{note}</p>')
    if part == "II":
        emit(f'<div class="lg gr"{attrs(sec)}><span class="lt">GUARDRAIL</span><div class="gt">No symmetry assumed across the four lands.</div></div>')


def content_section(code):
    s = SEC_BY_CODE[code]
    part = s["part"]
    station = "3SL" if part == "III" else "SPINE"
    crumb = f"{'3SL' if part == 'III' else 'SPINE'} › {code} {s['title'].upper()}"
    meta(code, station, crumb, f"{code} · {s['title'].upper()}", notes=(part == "III"), part=part)
    deck = PME.get(code, ("", "", ""))[1]
    deck = re.sub(r"\*", "", deck)
    opener(code, code, f"{KIND.get(code, '')} · {PART_NAME[part]}", s["title"], deck, station)
    blocks = parse_blocks(s["lines"])
    if code == "III.3":
        emit(f'<div class="lg rul"{attrs(code)}><span class="lt">STATUS · AUTHOR RULING 2026-10-09</span>'
             + "".join(f'<div class="rr">{badge(c, w)}<div>{t}</div><div class="pv">{pv}</div></div>' for c, w, t, pv in RULING_TIERS) +
             '</div>')
    render_blocks(code, blocks)
    if code == "III.3":
        cross_section(code)


def cross_section(sec):
    """III.3 Treatment: vertical cross-section diagram (relative only)."""
    tiers = ["Crownlight", "Dawnveil", "Ironcross", "Stoneveil", "Lowtorch", "Ashvein", "Shadowmere", "Gravebend", "Nightroot"]
    rows = ""
    for n, t in enumerate(tiers, 1):
        ground = "surf" if n <= 2 else "under"
        rows += f'<div class="xs-row {ground}"><span class="xs-n">{n}</span><span class="xs-t">{t}</span></div>'
        if n == 2:
            rows += ('<div class="xs-tr"><span>SURFACE TRANSITION · somewhere between Dawnveil and Ironcross</span>'
                     f'{badge("o", "OPEN")}</div>')
    emit(f'<div class="sh cap"{attrs(sec, keep_next="1")}>Record · Vertical Underside Cross-Section (relative order only)</div>')
    emit(f'<div class="xs"{attrs(sec)}><div class="xs-stack">{rows}</div><div class="xs-key">'
         f'<div>{badge("c", "CANON")} Crownlight and Dawnveil surface/above-ground; fully underground by Ironcross; attached off Zenithia’s side. <span class="pv">TCD-025 · TCD-026</span></div>'
         f'<div>{badge("d", "DRAFTED")} Nine tiers in this order. <span class="pv">3SL ch. 10</span></div>'
         f'<div>{badge("o", "OPEN")} Depths, elevations, tier boundaries, and where the descent goes underground. Not to scale; no depths are implied.</div>'
         '</div></div>')


# ---------------------------------------------------------------- III.20 working section (approved Direction C pages)
def wq(sec, badges_html, head, prompt, tied, min_lines, weight=1, decision=True):
    return (f'<div class="wb"{attrs(sec, flex=weight)}><div class="wq"><div class="g">{badges_html}</div>'
            f'<div><div class="sh">{head}</div><div class="pt">{prompt}</div></div><div class="pv">{tied}</div></div>'
            f'<div class="rl" data-min="{min_lines}" style="height:{min_lines * LINE}px"></div>{ds_row() if decision else ""}</div>')


def fixed_row(sec, badges_html, label, text, pv):
    lab = f'<div class="sh">{label}</div>' if label else ""
    return f'<div class="fixed"{attrs(sec)}><div class="g">{badges_html}</div><div>{lab}<div class="pt">{text}</div></div><div class="pv">{pv}</div></div>'


def working_section():
    W = "III.20W"
    meta(W, "3SL", "3SL › III.20 · WORKING SECTION", "III.20 · WORKING SECTION", work=True, folio="III.20")
    B = badge
    ck = '<span class="ckb"></span>'
    # 1 · The queue
    opener(W, "III.20", 'WORKING SECTION · <span class="wn"></span> · OPEN DEVELOPMENT · THE QUEUE', "3SL Open Development", "", "3SL")
    emit(f'<div class="qgr"{attrs(W)}><div class="lg gr"><span class="lt">GUARDRAIL</span><div class="gt">An open question that doesn’t touch the next scene doesn’t stop drafting.</div></div>'
         '<div class="pv"><b>OPEN STAYS OPEN.</b><br>Each item gets its own working pages. Set a Decide-by only when drafting forces one.</div></div>')
    items = [
        ("A · Remy-death specifics", B("c", "CANON"), "TCD-002 · 009 · 063", "W-A"),
        ("B · Romance specifics", B("c", "CANON"), "TCD-044", "W-B"),
        ("C · Tier depths", B("c", "CANON") + B("d", "DRAFTED") + B("s", "SUPPORTED"), "TCD-025 · 026 · 3SL ch. 10 · 3SL Full Worldbuilding", "W-C"),
        ("D · Crossing placement", B("c", "CANON"), "TCD-017 · 027", "W-D"),
        ("E · Next Shadowmere book", B("c", "CANON"), "II.16 · III.18", "W-E"),
    ]
    rows = "".join(f'<tr><td><span class="it">{n}</span></td><td><div class="fx">{b}<span class="pv">{pv}</span></div></td>'
                   f'<td class="w"></td><td>{ck}</td><td>{ck}</td><td><span class="chip" data-wref="{w}"></span></td></tr>' for n, b, pv, w in items)
    emit(f'<table class="qt"{attrs(W, split="1")}><colgroup><col style="width:150px"><col style="width:156px"><col><col style="width:54px"><col style="width:54px"><col style="width:76px"></colgroup>'
         f'<thead><tr><th>ITEM</th><th>WHAT’S FIXED</th><th>DECIDE BY</th><th>SAFE TO DEFER</th><th>DECIDED</th><th>WORK ON</th></tr></thead><tbody>{rows}</tbody></table>')
    emit(f'<div class="sh cap"{attrs(W, keep_next="1")}>ADDED IN DRAFTING · NAME IT, DATE IT, GIVE IT A PAGE</div>')
    add = "".join(f'<tr class="add"><td class="w"><span class="it">{L} ·</span></td><td class="w"></td><td class="w"></td><td>{ck}</td><td>{ck}</td><td class="w"></td></tr>' for L in "FGHIJK")
    emit(f'<table class="qt"{attrs(W, split="1")}><colgroup><col style="width:150px"><col style="width:156px"><col><col style="width:54px"><col style="width:54px"><col style="width:76px"></colgroup>'
         f'<thead><tr><th>ITEM</th><th>WHAT’S FIXED</th><th>DECIDE BY</th><th>SAFE TO DEFER</th><th>DECIDED</th><th>WORK ON</th></tr></thead><tbody>{add}</tbody></table>')
    emit(f'<div class="sh endl"{attrs(W)}><span>RESOLVED ITEMS MOVE TO APPENDIX A WITH A LOG NO.</span><span class="chip" data-ref="Appendix A">Appendix A</span></div>')

    # Item A · the scene
    opener(W, "III.20", 'WORKING SECTION · <span class="wn"></span> · ITEM A', "Remy’s Death: The Scene", "", "3SL", "")
    OUTPUT[-1] = OUTPUT[-1].replace('data-newpage="1"', 'data-newpage="1" data-anchor="W-A"')
    emit(fixed_row(W, B("c", "CANON"), "FIXED", "The nine fixed beats in III.15. Work inside them; nothing here moves a fixed beat.",
                   'TCD-002 · 009 · 063<br><span class="chip" data-ref="III.15">III.15</span>'))
    emit(wq(W, B("o", "OPEN"), "A1 · EXACT RESCUE ACTION", "Beat 3 is fixed: Remy deliberately intervenes to protect her. What exactly does he do, and what does it cost him in the moment?", "TIED TO<br>Beat 3", 10, 3))
    emit(wq(W, B("o", "OPEN") + B("p", "POSSIBLE"), "A2 · WEAPON AND WOUND", "Beat 4: the gang leader mortally wounds him. Beta’s machete/major-artery detail is a compatible candidate only. Keep it, change it, or replace it, and say why.", "TIED TO<br>Beat 4 · Beta candidate", 8, 2))
    emit(wq(W, B("o", "OPEN"), "A3 · FINAL WORDS", "Beat 6: he dies. Does he speak? Draft the words, or the silence, and note what Melena carries of it into FTE.", 'TIED TO<br>Beat 6 · Memory Translation, <span class="xr" data-ref="VII.10">VII.10</span>', 8, 2))
    opener(W, "III.20", 'WORKING SECTION · <span class="wn"></span> · ITEM A', "Remy’s Death: Around the Scene", "", "3SL")
    emit(wq(W, B("o", "OPEN"), "A4 · ATTACKER MOTIVE", "The gang leader is the climax antagonist. Why does he act at this moment, and does anyone on the page ever learn why?", "TIED TO<br>III.13 · gang leader’s motive", 6, 2))
    emit(wq(W, B("o", "OPEN"), "A5 · WITNESSES", "Who sees Remy die? List each witness, where they stand, and what they saw versus what they were told.", 'TIED TO<br>III.15 open · witnesses<br><span class="chip" data-ref="VII.5">VII.5</span>', 8, 2))
    emit(wq(W, B("o", "OPEN"), "A6 · ATTACKER FATE", "What happens to the gang leader after Remy dies?", "TIED TO<br>III.13 · gang leader’s fate", 5, 1))
    emit(wq(W, B("c", "CANON"), "A7 · FIRE/COLLAPSE PROPORTIONS", "Beat 8: blaze/collapse is not the fatal mechanism. How much of the scene does it take, and what does it destroy?", "TIED TO<br>Beat 8 · TCD-063", 6, 1))

    # Item B
    opener(W, "III.20", 'WORKING SECTION · <span class="wn"></span> · ITEM B · SILAS AND ISOLA', "Romance Specifics", "", "3SL")
    OUTPUT[-1] = OUTPUT[-1].replace('data-newpage="1"', 'data-newpage="1" data-anchor="W-B"')
    emit(fixed_row(W, B("c", "CANON"), "FIXED · THE RULED LANDING", "Explicit, mutual, consensual physical romance before the end, without a settled public-couple ending.",
                   'TCD-044<br><span class="chip" data-ref="III.12">III.12</span><span class="chip" data-ref="III.11">III.11</span>'))
    emit(f'<div class="lg gr"{attrs(W)}><span class="lt">GUARDRAIL</span><div class="gt">The tether is never evidence of romance or consent.</div></div>')
    emit(wq(W, B("o", "OPEN"), "B1 · CONSENT REPAIR", "The voluntary track runs through acknowledgment of the violation and choices restored. What does repair look like on the page, and where does it happen?", "TIED TO<br>III.12 · consent repair", 10, 3))
    emit(wq(W, B("o", "OPEN"), "B2 · FIRST MAJOR ROMANTIC SCENE · INITIATOR · INTIMACY LEVEL", "Where does the first major romantic scene fall, who initiates, and how far does the page go?", "TIED TO<br>III.12 · first scene, initiator, intimacy level", 10, 3))
    emit(wq(W, B("o", "OPEN"), "B3 · FINAL RELATIONSHIP LANGUAGE", "No settled public-couple ending. What do they call what they are by the last page?", "TIED TO<br>III.12 · final language", 6, 1))

    # Item C
    opener(W, "III.20", 'WORKING SECTION · <span class="wn"></span> · ITEM C', "Tiers and the Crossing", "", "3SL")
    OUTPUT[-1] = OUTPUT[-1].replace('data-newpage="1"', 'data-newpage="1" data-anchor="W-C"')
    rows = "".join(f'<div class="fx2">{B(c, w)}<div>{t}</div><div class="pv">{pv}</div></div>' for c, w, t, pv in [
        ("c", "CANON", "The Underside is vertically tiered and attached to the Zenithia side of Remnia. Crownlight and Dawnveil are above-ground/surface tiers, and the nation is fully underground by Ironcross.", "TCD-025 · TCD-026"),
        ("d", "DRAFTED", "The Underside has nine tiers; Halflight’s old route board lists all nine in order.", "3SL ch. 10"),
        ("s", "SUPPORTED", "Tier functions and other worldbuilding detail where not independently drafted or ruled.", "3SL Full Worldbuilding"),
        ("o", "OPEN", "Exact elevations and depths; tier boundaries.", ""),
    ])
    emit(f'<div class="it2"{attrs(W)}><div class="ith"><span>C · Tier depths</span><span class="chip" data-ref="III.3">III.3</span></div>{rows}</div>')
    tiers = [("Crownlight", "Surface-level"), ("Dawnveil", "Surface-level"), ("Ironcross", "Fully subterranean by this tier"),
             ("Stoneveil", "Underground"), ("Lowtorch", "Underground"), ("Ashvein", "Underground"), ("Shadowmere", "Underground"),
             ("Gravebend", "Underground"), ("Nightroot", "Underground")]
    tr = "".join(f'<tr><td>{n}. {t}</td><td>{s}</td><td><div class="rl" data-min="2" style="height:60px"></div></td><td></td></tr>' for n, (t, s) in enumerate(tiers, 1))
    emit(f'<table class="tb wt fc"{attrs(W, split="1")}><colgroup><col style="width:138px"><col style="width:150px"><col><col style="width:96px"></colgroup>'
         f'<thead><tr><th>TIER (DRAFTED ORDER)</th><th>SURFACE / UNDERGROUND</th><th>DEPTH, BOUNDARY, WHAT THE DRAFT NEEDS</th><th>ON-PAGE CH.</th></tr></thead><tbody>{tr}</tbody></table>')
    emit(f'<div class="wb"{attrs(W, flex=1)}><div class="rl" data-min="0" style="height:0px"></div>{ds_row()}</div>')

    # Item D
    opener(W, "III.20", 'WORKING SECTION · <span class="wn"></span> · ITEM D', "Tiers and the Crossing", "", "3SL")
    OUTPUT[-1] = OUTPUT[-1].replace('data-newpage="1"', 'data-newpage="1" data-anchor="W-D"')
    rows = "".join(f'<div class="fx2">{B(c, w)}<div>{t}</div><div class="pv">{pv}</div></div>' for c, w, t, pv in [
        ("c", "CANON", "The current Remnia–Underside crossing near the London Town / Old Prosperity / Alea no-man’s-land. Routes are physical-magical transit through real passages; never portals.", "TCD-017 · TCD-027"),
        ("o", "OPEN", "Crossing coordinate; arrival tier (Shadowmere Tier 7 is unconfirmed); the unresolved transit route at the manuscript stop point.", ""),
    ])
    emit(f'<div class="it2"{attrs(W)}><div class="ith"><span>D · Crossing placement</span><span><span class="chip" data-ref="II.3">II.3</span><span class="chip" data-ref="III.6">III.6</span></span></div>{rows}</div>')
    emit(wq(W, "", "WHERE IT COMES OUT, AND HOW THEY GET THROUGH IT AT THE STOP POINT", "", "", 14, 1))

    # Item E
    opener(W, "III.20", 'WORKING SECTION · <span class="wn"></span> · ITEM E · PLOT ARCHITECTURE', "The Next Shadowmere Book", "", "3SL")
    OUTPUT[-1] = OUTPUT[-1].replace('data-newpage="1"', 'data-newpage="1" data-anchor="W-E"')
    emit(fixed_row(W, B("c", "CANON"), "", "TSWK and the next Shadowmere book in a rolling handoff directly after, overlapping substantially.", "II.16 · TCD-013 · 014 · 024 · 054"))
    emit(fixed_row(W, B("o", "OPEN"), "", "Next Shadowmere title and plot engine.", "III.18"))
    emit(wq(W, B("o", "OPEN"), "E1 · TITLE", "The pattern is 3 / 5 / 7. List candidates.", "TIED TO<br>II.16 · title pattern", 5, 1, decision=False))
    emit(wq(W, B("o", "OPEN"), "E2 · PLOT ENGINE", "What pressure drives the next book? It opens in the rolling window beside TSWK, so start from what 3SL leaves unresolved.", "TIED TO<br>III.18 · plot engine", 10, 3))
    emit(f'<div class="sh cap"{attrs(W, keep_next="1")}>E3 · WHAT 3SL HANDS FORWARD <span class="chip" data-ref="III.18">III.18</span></div>')
    tr = "".join(f'<tr><td>{t}</td><td><div class="rl" data-min="2" style="height:60px"></div></td><td></td></tr>' for t in [
        "Melena’s state entering FTE", "Tiran’s aftermath function", "Silas and Isola’s separate immediate paths", "The two-year interval", "", ""])
    emit(f'<table class="tb wt fc"{attrs(W, split="1")}><colgroup><col style="width:200px"><col><col style="width:190px"></colgroup>'
         f'<thead><tr><th>THREAD</th><th>3SL END STATE</th><th>PICKED UP WHERE</th></tr></thead><tbody>{tr}</tbody></table>')


# ---------------------------------------------------------------- continuity room (3SL concordance)
CONC_ROWS = [
    ("VII.1", ["II.16", "III.18"], "3SL and next-Shadowmere rows of the four-band table (II.16); the handoff table (III.18); the 3SL bands tracker on the following page."),
    ("VII.2", ["III.17", "II.4"], "Knowledge ledger by chapter (III.17); drafted cross-land knowledge (II.4)."),
    ("VII.3", ["III.13", "III.14"], "Supporting cast table (III.13); Melena and Remy (III.14)."),
    ("VII.4", ["III.6", "II.3"], "Drafted routes by class and who knows routes (III.6); the one confirmed crossing (II.3)."),
    ("VII.5", ["II.4", "III.6", "III.17"], "Seed knowledge table (II.4); route knowledge (III.6); knowledge ledger (III.17); the 3SL knowledge tracker in this section."),
    ("VII.7", ["II.14", "III.16"], "The Elders’ Prayer can/can’t table and the two performances (II.14); Selah’s performance record (III.16)."),
    ("VII.10", ["III.15", "III.14"], "Continuity translation for Remy’s death (III.15); what 3SL owes FTE (III.14)."),
    ("VII.12", ["III.20"], "Every open 3SL item (III.20 reference table) and the working queue (III.20 working section)."),
    ("IV.14", ["III.14", "III.15", "III.18"], "Melena in Shadowmere; her FTE memory of Remy’s death; her state entering FTE."),
    ("IV.15", ["III.14", "III.18"], "Caelum’s report of Tiran and Maven (III.14); Caelum’s alliance leverage as handed forward (III.18)."),
    ("IV.17", ["II.14", "III.16"], "The Prayer’s two independent performances (II.14); Selah’s 3SL performance (III.16)."),
]


def continuity_room():
    C = "CR"
    meta(C, "CONTINUITY", "CONTINUITY › 3SL CONCORDANCE", "CONTINUITY ROOM · 3SL CONCORDANCE", folio="CR")
    opener(C, "VII·3SL", "CONCORDANCE · CONTINUITY ROOM · 3SL SLICE", "Continuity Room: 3SL Concordance",
           "Where this volume carries the 3SL information behind each Continuity Room pointer.", "CONTINUITY")
    emit(f'<p{attrs(C)}>The full Companion’s Continuity Room (Part VII) and the FTE dossier (Part IV) aren’t printed in this volume. '
         'Every page here that points into them resolves to this table. The middle column is the Production Master’s description of the full section; '
         'the right column names where the 3SL information already sits in these pages.</p>')
    rows = ""
    for code, where, what in CONC_ROWS:
        content = PME.get(code, ("", "", ""))[2]
        chips = "".join(f'<span class="chip" data-ref="{w}">{w}</span>' for w in where)
        rows += (f'<tr><td><span class="cd">{code}</span><br><span class="tm">{esc(section_title(code))}</span></td>'
                 f'<td>{inline(content, refs=False)}</td><td>{esc(what)}<div class="chips">{chips}</div></td></tr>')
    emit(f'<table class="tb cc"{attrs(C, split="1")}><colgroup><col style="width:150px"><col><col style="width:236px"></colgroup>'
         f'<thead><tr><th>FULL COMPANION SECTION</th><th>WHAT IT HOLDS (PRODUCTION MASTER)</th><th>3SL INFORMATION IN THIS VOLUME</th></tr></thead><tbody>{rows}</tbody></table>')

    # VII.1 · 3SL bands tracker — rows reproduced from II.16
    band_rows = [r for r in II16_ROWS if r[0] in ("3SL", "Next Shadowmere book")]
    emit(f'<div class="sh cap" data-sec="{C}" data-newpage-soft="1" data-keep-next="1">VII.1 · 3SL BANDS · Record: Tandem Master Synchronization Timeline <span class="chip" data-ref="II.16">II.16</span></div>')
    emit(f'<p{attrs(C, keep_next="1")}>Rows reproduced from II.16. The working columns take dates and anchors as drafting fixes them.</p>')
    tr = ""
    for r in band_rows:
        for band, val in zip(["Background activation", "Narrative opening", "Climax", "Resolution"], r[1:5]):
            tr += f'<tr><td>{inline(r[0])}</td><td>{band}</td><td>{inline(val)}</td><td><div class="rl" data-min="2" style="height:60px"></div></td></tr>'
    emit(f'<table class="tb fc"{attrs(C, split="1")}><colgroup><col style="width:118px"><col style="width:124px"><col><col style="width:170px"></colgroup>'
         f'<thead><tr><th>BOOK</th><th>BAND</th><th>AS RULED / OPEN (II.16)</th><th>WORKING DATE · ANCHOR · CH.</th></tr></thead><tbody>{tr}</tbody></table>')

    # VII.5 · 3SL knowledge seed — rows reproduced from II.4
    emit(f'<div class="sh cap" data-sec="{C}" data-keep-next="1">VII.5 · 3SL KNOWLEDGE SEED · Record: Knowledge of the Other Lands Matrix <span class="chip" data-ref="II.4">II.4</span></div>')
    emit(f'<p{attrs(C, keep_next="1")}>3SL rows reproduced from II.4. Every row is dated to its chapter; blank rows extend the matrix as drafting adds knowledge.</p>')
    tr = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in II4_ROWS if r[1].startswith("3SL"))
    tr += "".join('<tr class="blank">' + "".join('<td><div class="rl" data-min="2" style="height:60px"></div></td>' for _ in range(5)) + "</tr>" for _ in range(6))
    emit(f'<table class="tb fc"{attrs(C, split="1")}><thead><tr><th>CHARACTER</th><th>CHAPTER</th><th>KNOWLEDGE ON-PAGE</th><th>LEVEL</th><th>STATUS</th></tr></thead><tbody>{tr}</tbody></table>')


def table_rows_after(code, caption_start):
    blocks = parse_blocks(SEC_BY_CODE[code]["lines"])
    for k, (t, v) in enumerate(blocks):
        if t == "table" and (caption_start is None or (k > 0 and blocks[k - 1][0] in ("sub", "p") and caption_start in blocks[k - 1][1])):
            return v[1:]
    raise SystemExit(f"table not found {code} {caption_start}")


II16_ROWS = table_rows_after("II.16", "Four bands per book")
II4_ROWS = table_rows_after("II.4", "What the drafted pages already establish")


# ---------------------------------------------------------------- appendices (3SL slices from the audit)
def audit_table(header_prefix):
    lines = AUDIT.split("\n")
    out, on = [], False
    for ln in lines:
        if ln.startswith(header_prefix):
            on = True
            continue
        if on:
            if ln.startswith("## ") or ln.startswith("### "):
                break
            if ln.startswith("|") and not re.match(r"^\|\s*-{3}", ln) and not ln.startswith("|---"):
                out.append(split_row(ln))
    return out


TCD = {r[0]: r for r in audit_table("## Canon Decision Log")[1:] if r[0].startswith("TCD-")}
HC = {r[0]: r for r in audit_table("## High-Impact Conflict Register")[1:] if r[0].startswith("HC-")}


def cited(pattern, text):
    return sorted(set(re.findall(pattern, text)), key=lambda x: int(x.split("-")[1]))


def tcd_range_expand(text):
    out = set()
    for a, b in re.findall(r"TCD-(\d{3})[–-](?:TCD-)?(\d{3})", text):
        for n in range(int(a), int(b) + 1):
            out.add(f"TCD-{n:03d}")
    return out


def appendices(volume_text):
    # Appendix A — every TCD cited in the volume (and in the B/C slices it prints)
    hc_ids = [h for h in HC if "3SL" in HC[h][2]] + cited(r"HC-\d{3}", volume_text)
    hc_ids = sorted(set(hc_ids), key=lambda x: int(x[3:]))
    inv = audit_table("## Source Inventory — 3 Shadowmere Lane")[1:]
    fte = [r for r in audit_table("## Source Inventory — For Their Entertainment")[1:] if r[0].startswith("FTE Official Beta")]
    shared = [r for r in audit_table("## Source Inventory — Shared Tandem")[1:] if r[0].startswith("Novel Constraints")]
    inv_rows = inv + fte + shared
    slice_text = volume_text + " ".join(" ".join(HC[h]) for h in hc_ids) + " ".join(" ".join(r) for r in inv_rows)
    tcd_ids = set(cited(r"TCD-\d{3}", slice_text)) | tcd_range_expand(slice_text)
    tcd_ids = sorted((t for t in tcd_ids if t in TCD), key=lambda x: int(x[4:]))

    A = "APP-A"
    meta(A, "SPINE", "APPENDIX A › CANON DECISION LOG · 3SL SLICE", "APPENDIX A · CANON DECISION LOG · 3SL SLICE", folio="A")
    opener(A, "A", "APPENDIX · STATUS &amp; PROVENANCE SHEET", "Canon Decision Log: 3SL Slice",
           "Every author ruling this volume cites, reproduced from the audit’s Canon Decision Log.", "SPINE")
    emit(f'<p{attrs(A)}>{len(tcd_ids)} rulings are cited in this volume. Each row is reproduced from the Tandem Source Authority Audit — Working Record (Sep 26, 2026). '
         'Rulings this volume doesn’t cite appear in the full Companion’s Appendix A.</p>')
    tr = ""
    for t in tcd_ids:
        r = TCD[t]
        tr += (f'<tr><td><span class="cd">{r[0]}</span><br><span class="pv">{inline(r[5], refs=False)}</span></td>'
               f'<td><b>{inline(r[1], refs=False)}</b><br><span class="pv">{inline(r[2], refs=False)}</span></td>'
               f'<td>{inline(r[4], refs=False)}</td>'
               f'<td><span class="pv">SUPERSEDES</span> {inline(r[6], refs=False)}<br><span class="pv">DOWNSTREAM</span> {inline(r[7], refs=False)}</td></tr>')
    emit(f'<table class="tb ap"{attrs(A, split="1")}><colgroup><col style="width:86px"><col style="width:132px"><col><col style="width:200px"></colgroup>'
         f'<thead><tr><th>ID · DATE</th><th>TOPIC · BOOKS</th><th>AUTHOR RULING</th><th>SUPERSEDES · DOWNSTREAM</th></tr></thead><tbody>{tr}</tbody></table>')
    emit(f'<div class="sh cap"{attrs(A, keep_next="1")}>Author rulings without a TCD number</div>')
    nt = [("2026-08-22", "Graveshand and Severance: the five laws", "Approved as the working continuity baseline for Graveshand and Severance (connection required; understanding required; every ending leaves remains; remains can follow the connection home; the body imitates the ending).", "III.8"),
          ("2026-10-09", "Underside tier status", "CANON — TCD-025 / TCD-026: the Underside is vertically tiered and attached to Zenithia’s side of Remnia; Crownlight and Dawnveil are surface/above-ground tiers; the nation is fully underground by Ironcross. DRAFTED — 3SL ch. 10: the Underside has nine tiers; the route board lists all nine in order. SUPPORTED — 3SL Full Worldbuilding: tier functions and other worldbuilding detail where not independently drafted or ruled. The nine-tier count is not promoted to ruled canon.", "III.3 · III.20")]
    tr = "".join(f'<tr><td><span class="pv">{d}</span></td><td><b>{esc(t)}</b></td><td>{esc(r)}</td><td><span class="pv">APPLIED IN</span> {a}</td></tr>' for d, t, r, a in nt)
    emit(f'<table class="tb ap"{attrs(A, split="1")}><colgroup><col style="width:86px"><col style="width:132px"><col><col style="width:200px"></colgroup>'
         f'<thead><tr><th>DATE</th><th>TOPIC</th><th>AUTHOR RULING</th><th>WHERE</th></tr></thead><tbody>{tr}</tbody></table>')
    emit(f'<div class="sh cap"{attrs(A, keep_next="1")}>Logged in drafting · resolved III.20 items · asking a question assigns no TCD number</div>')
    tr = "".join('<tr class="blank">' + "".join('<td><div class="rl" data-min="2" style="height:60px"></div></td>' for _ in range(4)) + "</tr>" for _ in range(8))
    emit(f'<table class="tb ap"{attrs(A, split="1")}><colgroup><col style="width:86px"><col style="width:132px"><col><col style="width:200px"></colgroup>'
         f'<thead><tr><th>LOG NO.</th><th>III.20 ITEM</th><th>DECISION AS MADE IN PROSE OR RULED</th><th>DATE · CH. · PAGES TO UPDATE</th></tr></thead><tbody>{tr}</tbody></table>')

    B_ = "APP-B"
    meta(B_, "SPINE", "APPENDIX B › HIGH-IMPACT CONFLICT REGISTER · 3SL SLICE", "APPENDIX B · CONFLICT REGISTER · 3SL SLICE", folio="B")
    opener(B_, "B", "APPENDIX · STATUS &amp; PROVENANCE SHEET", "High-Impact Conflict Register: 3SL Slice",
           "Conflicts that touch 3SL, plus every conflict this volume cites.", "SPINE")
    emit(f'<p{attrs(B_)}>Rows reproduced from the audit’s High-Impact Conflict Register. Included: every register entry whose books include 3SL, and every entry cited elsewhere in this volume ({len(hc_ids)} rows).</p>')
    tr = "".join(f'<tr><td><span class="cd">{r[0]}</span></td><td><b>{inline(r[1], refs=False)}</b><br><span class="pv">{inline(r[2], refs=False)}</span></td><td>{inline(r[3], refs=False)}</td><td>{inline(r[4], refs=False)}</td></tr>' for r in (HC[h] for h in hc_ids))
    emit(f'<table class="tb ap"{attrs(B_, split="1")}><colgroup><col style="width:72px"><col style="width:150px"><col><col style="width:170px"></colgroup>'
         f'<thead><tr><th>ID</th><th>TOPIC · BOOKS</th><th>CONFLICT</th><th>PRIORITY / STATUS</th></tr></thead><tbody>{tr}</tbody></table>')

    C_ = "APP-C"
    meta(C_, "SPINE", "APPENDIX C › SOURCE AUTHORITY INVENTORY · 3SL SLICE", "APPENDIX C · SOURCE INVENTORY · 3SL SLICE", folio="C")
    opener(C_, "C", "APPENDIX · STATUS &amp; PROVENANCE SHEET", "Source Authority Inventory: 3SL Slice",
           "The 3SL files, plus the two non-3SL files Part III leans on.", "SPINE")
    emit(f'<p{attrs(C_)}>Rows reproduced from the audit’s Source Inventory: all four 3SL files, the FTE Beta (which controls Melena’s FTE memory of Shadowmere), and <i>Novel Constraints</i> (named in Part III’s source note). '
         'TKC files have zero Tandem authority and are listed only in the full Companion.</p>')
    tr = "".join(f'<tr><td><b>{inline(r[0], refs=False)}</b><br><span class="pv">{inline(r[1], refs=False)} · {inline(r[2], refs=False)}</span></td>'
                 f'<td>{inline(r[3], refs=False)}<br><span class="pv">DOMAINS</span> {inline(r[4], refs=False)}</td><td>{inline(r[5], refs=False)}</td><td>{inline(r[6], refs=False)}</td></tr>' for r in inv_rows)
    emit(f'<table class="tb ap"{attrs(C_, split="1")}><colgroup><col style="width:150px"><col style="width:180px"><col style="width:104px"><col></colgroup>'
         f'<thead><tr><th>FILE · BOOK · TYPE</th><th>GENERATION · DOMAINS</th><th>STATUS</th><th>KNOWN HIGH-IMPACT CONFLICT</th></tr></thead><tbody>{tr}</tbody></table>')

    E_ = "APP-E"
    meta(E_, "SPINE", "APPENDIX E › TERMINOLOGY REGISTER · 3SL SLICE", "APPENDIX E · TERMINOLOGY REGISTER · 3SL SLICE", folio="E")
    opener(E_, "E", "APPENDIX · TERMINOLOGY REGISTER", "Terminology Register: 3SL Slice",
           "Print version of Production Control A7, limited to the terms this volume uses.", "SPINE")
    a7 = re.search(r"### A7\.[^\n]*\n\n[^\n]*\n\n((?:\|[^\n]*\n)+)", PM).group(1).strip().split("\n")
    a7 = [split_row(r) for r in a7 if not re.match(r"^\|\s*-{3}", r)][1:]
    keep = []
    for r in a7:
        term = plain(r[0])
        keys = [k.strip() for k in re.split(r"[/(]", term) if k.strip()]
        keys = [re.sub(r"\)$", "", k) for k in keys]
        if any(re.search(r"\b" + re.escape(k.split(" (")[0]) + r"\b", volume_text, re.I) for k in keys):
            keep.append(r)
    emit(f'<p{attrs(E_)}>These terms carry rulings; drafters use them exactly. {len(keep)} of the register’s {len(a7)} terms appear in this volume.</p>')
    tr = "".join(f'<tr><td><b>{inline(r[0], refs=False)}</b></td><td>{inline(r[1], refs=False)}</td><td><span class="pv">{inline(r[2], refs=False)}</span></td></tr>' for r in keep)
    emit(f'<table class="tb fc"{attrs(E_, split="1")}><colgroup><col style="width:170px"><col><col style="width:140px"></colgroup>'
         f'<thead><tr><th>TERM</th><th>REQUIRED USAGE</th><th>GOVERNING RULING</th></tr></thead><tbody>{tr}</tbody></table>')
    return tcd_ids, hc_ids, keep


# ---------------------------------------------------------------- assemble
def main():
    OUT.mkdir(exist_ok=True)
    front_matter()
    order = []
    divider("I", [s["code"] for s in SECS if s["part"] == "I"], PARTS["I"]["lines"])
    for s in SECS:
        if s["part"] == "I":
            content_section(s["code"]); order.append(s["code"])
    divider("II", PART_II_SCOPE, PARTS["II"]["lines"],
            note="This volume prints the Part II sections a 3SL scene stands on. II.1, II.6–II.13, and II.15 are in the full Tandem Companion.")
    for c in PART_II_SCOPE:
        content_section(c); order.append(c)
    divider("III", [s["code"] for s in SECS if s["part"] == "III"] + ["III.20W", "CR"], PARTS["III"]["lines"])
    for s in SECS:
        if s["part"] == "III":
            content_section(s["code"]); order.append(s["code"])
            if s["code"] == "III.20":
                working_section()
    continuity_room()
    volume_text = CMX  # citations are taken from the printed copy only
    printed = "\n".join(t for _, t in QA_SOURCE_TEXT) + "\n".join(o for o in OUTPUT if 'data-sec="TITLE"' not in o and 'data-sec="ABOUT"' not in o)
    tcd_ids, hc_ids, terms = appendices(re.sub(r"<[^>]+>", " ", printed))

    titles = {c: ref_title(c) for c in set(re.findall(r"(?:VII|VI|IV|V|III|II|I)\.\d+", PM + CM))}
    titles.update({"III.20W": CM_TITLES["III.20W"], "CR": CM_TITLES["CR"], "Appendix A": "Canon Decision Log", "Appendix B": "High-Impact Conflict Register",
                   "Appendix C": "Source Authority Inventory", "Appendix D": "Full 4 Series Flesh Out Claim-Level Survival Pass", "Appendix E": "Terminology Register"})
    in_volume = {s["code"] for s in SECS if in_scope(s["code"])} | {"III.20W", "CR", "Appendix A", "Appendix B", "Appendix C", "Appendix E", "Part I", "Part II", "Part III"}
    anchor = {c: c for c in in_volume}
    anchor.update({"Appendix A": "APP-A", "Appendix B": "APP-B", "Appendix C": "APP-C", "Appendix E": "APP-E",
                   "Part I": "PART-I", "Part II": "PART-II", "Part III": "PART-III"})
    for c in CONCORDANCE:
        anchor[c] = "CR"
    toc = [("FRONT", None, [("ABOUT", "About This Volume")]),
           ("PART I", "PART-I", [(c, CM_TITLES[c]) for c in order if c.startswith("I.")]),
           ("PART II", "PART-II", [(c, CM_TITLES[c]) for c in PART_II_SCOPE]),
           ("PART III", "PART-III", [(c, CM_TITLES[c]) for c in order if c.startswith("III.")] + [("III.20W", "III.20 Working Section · Items A–E")]),
           ("CONTINUITY ROOM · 3SL", None, [("CR", "Continuity Room: 3SL Concordance")]),
           ("APPENDICES · 3SL SLICES", None, [("APP-A", "A · Canon Decision Log"), ("APP-B", "B · High-Impact Conflict Register"),
                                               ("APP-C", "C · Source Authority Inventory"), ("APP-E", "E · Terminology Register")])]
    data = {"secmeta": SECMETA, "titles": titles, "anchor": anchor, "toc": toc, "concordance": CONCORDANCE,
            "counts": {"tcd": len(tcd_ids), "hc": len(hc_ids), "terms": len(terms)}, "tcd_ids": tcd_ids, "hc_ids": hc_ids}
    page = (ROOT / "tools" / "shell.html").read_text()
    page = page.replace("<!--BLOCKS-->", "\n".join(OUTPUT)).replace("/*DATA*/null", json.dumps(data, ensure_ascii=False))
    (OUT / "book.html").write_text(page)
    (OUT / "source_text.json").write_text(json.dumps(QA_SOURCE_TEXT, ensure_ascii=False))
    print(f"blocks: {len(OUTPUT)}  sections: {len(SECMETA)}  TCD cited: {len(tcd_ids)}  HC: {len(hc_ids)}  terms: {len(terms)}")


if __name__ == "__main__":
    main()
