#!/usr/bin/env python3
"""Build 2 — standalone For Their Entertainment / Remnia Companion.

Reads the locked copy (src/content_master.md), the production rules
(src/production_master.md), the source-authority audit (src/audit.md) and
the Remnian lineage working record (src/lineage.py, a derived record built
from the evidence), applies the logged corrections (src/corrections.json),
and writes out/book.html: every printed block in reading order, tagged for
the paginator (tools/paginate.js). Layout and apparatus only: no canon is
authored here. Working-page prompts, the concordance lead, and the record
apparatus are volume apparatus and are listed as such in the QA report.
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
OUT = ROOT / "out"

CM = (SRC / "content_master.md").read_text()
PM = (SRC / "production_master.md").read_text()
AUDIT = (SRC / "audit.md").read_text()
CORR = json.loads((SRC / "corrections.json").read_text())
sys.path.insert(0, str(SRC))
import lineage as LIN  # noqa: E402

BUILD_DATE = "2026-10-09"

# ---------------------------------------------------------------- scope
PART_II_SCOPE = ["II.2", "II.4", "II.5", "II.6", "II.13", "II.14", "II.15", "II.16"]

STATIONS = {"SPINE": (0, "#2B2B2B"), "3SL": (1, "#74399A"), "FTE": (2, "#B8332A"),
            "ADST": (3, "#2C63C4"), "TSWK": (4, "#0E7F74"), "CONTINUITY": (5, "#C46F0D")}

# Page-type kind lines (from Production Master "Treatment" + V5 catalog)
KIND = {
    "I.1": "ORIENTATION", "I.2": "RULE", "I.3": "SOURCE AUTHORITY", "I.4": "STATUS KEY",
    "I.5": "EXPLAINER", "I.6": "PROTOCOL", "I.7": "CHECKLIST",
    "II.2": "SCHEMATIC", "II.4": "EXPLAINER · LADDER", "II.5": "EXPLAINER · TABLE", "II.6": "EXPLAINER · NOT THE SAME AS",
    "II.13": "COMPARISON · VARIANT TEXTS", "II.14": "EXPLAINER · CAN/CANNOT", "II.15": "MISREADING TABLE", "II.16": "TIMELINE",
    "IV.1": "STATUS & PROVENANCE SHEET", "IV.2": "PLACE DOSSIER", "IV.3": "POWER MAP", "IV.4": "INSTITUTION DOSSIER",
    "IV.5": "FACTION TABLE", "IV.6": "SYSTEM EXPLAINER", "IV.7": "CHALLENGE TABLE", "IV.8": "RULES TABLE",
    "IV.9": "DOSSIER · PROTAGONIST", "IV.10": "COMPARISON SPREAD", "IV.11": "LINEAGE · FIVE LAYERS",
    "IV.12": "CONCEALMENT MATRIX", "IV.13": "EVIDENCE CHAIN", "IV.14": "DOSSIER · PROTAGONIST", "IV.15": "LEVERAGE LEDGER",
    "IV.16": "MECHANICS EXPLAINER", "IV.17": "PERFORMANCE RECORD", "IV.18": "CAST TABLE", "IV.19": "DOSSIER · ARC WORKSHEET",
    "IV.20": "CAUSAL CHAIN", "IV.21": "PLOT STATE", "IV.22": "KNOWLEDGE LEDGER", "IV.23": "CONNECTION TABLE",
    "IV.24": "ENDGAME PACKET", "IV.25": "OPEN DEVELOPMENT",
    "IV.10W": "YOUR PAGES", "IV.11R": "WORKING RECORD", "IV.25W": "WORKING PAGES", "CR": "CONCORDANCE",
}
DISP = {"IV.10W": "IV.10", "IV.11R": "IV.11", "IV.25W": "IV.25", "CR": "VII·FTE"}
PART_NAME = {"I": "PART I · HOW THIS COMPANION WORKS",
             "II": "PART II · THE SHARED TANDEM SPINE",
             "IV": "PART IV · FOR THEIR ENTERTAINMENT / REMNIA"}

# Tracker tables that arrive half-filled get blank rows (V9: the writer extends).
BLANK_ROWS = {
    ("IV.2", "place"): 3, ("IV.9", "moment"): 3, ("IV.12", "person or body"): 3, ("IV.13", "point"): 3,
    ("IV.14", "chapter"): 3, ("IV.18", "name"): 2, ("IV.19", "thread"): 3, ("IV.21", "ch."): 4,
    ("IV.22", "who"): 4, ("IV.23", "connection"): 2, ("IV.24", "choice"): 3,
}
# Writing-application tables: the empty column is the writing space.
ANSWER_HEADERS = {"your answer for the next severance", "your answer"}

LINE = 30  # handwriting line pitch, px (production rules floor)


def esc(s):
    return html.escape(s, quote=False)


def escx(s):
    """Escape for body text: arrows print in the mono face (the text faces have no arrow glyphs)."""
    return esc(s).replace("→", '<span class="ar">→</span>').replace("↔", '<span class="ar">↔</span>')


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
CM_TITLES["IV.10W"] = "Your Pages: Katherine’s Elemental Anatomy"
CM_TITLES["IV.11R"] = "Record: Remnian Imperial + Royal Lineage"
CM_TITLES["IV.25W"] = "Working Pages: FTE Open Development"
CM_TITLES["CR"] = "Continuity Room: FTE Concordance"


def in_scope(code):
    p = code.split(".")[0]
    return p in ("I", "IV") or code in PART_II_SCOPE


# Codes that resolve inside this volume to the FTE Continuity Room concordance.
CONCORDANCE = ["VII.1", "VII.2", "VII.5", "VII.7", "VII.8", "VII.10", "VII.12", "Part VII",
               "III.3", "III.13", "III.14", "III.15", "III.16", "III.18", "III.20", "Part III"]


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
    s = s.replace("→", '<span class="ar">→</span>').replace("↔", '<span class="ar">↔</span>')
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
        h = f'<div class="lg od"{attrs(sec, keep_next="1" if sec.startswith("IV.") else None)}><span class="lt">{lt}</span><div class="og">{"".join(cells)}</div></div>'
        emit(h)
        if sec.startswith("IV."):
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
NO_TCD_RULINGS = [
    ("2026-09-26", "TCD-058 clarified: Heart’s Mirror", "Heart’s Mirror may foreshadow Katherine’s hidden ancestral capacity through Fire imagery, fear, symbolic or ambiguous memory, lineage recognition, or other Mirror-generated material. Her Fire doesn’t become objectively active during Challenge Five or its aftermath; she leaves the Mirror still operating through her Frost-dominant configuration. Material inside the Mirror isn’t automatically an objective recovered memory. Her first objective Fire manifestation stays in the Challenge Six climax, after her established Frost pathway catastrophically fails or becomes unavailable.", "IV.10 · IV.24 · IV.25 · IV.10 working pages"),
    ("2026-10-09", "IV.2 status: Remnia at a glance", "CANON — TCD-025 / TCD-041: Remnia is an empire on its own continental landmass, separated from Somnoria by ocean; the Crown sits at the highest public civil/dynastic level of the Remnian sovereignty structure. CURRENT DRAFTED TEXT — FTE Beta: Remnia has seventeen provinces. “Seventeen” is not attached to the TCDs.", "IV.2"),
    ("2026-10-09", "IV.3 status: the military", "The military structure is CURRENT DRAFTED TEXT, not TCD-041 canon. TCD-041 is the layered sovereignty framework.", "IV.3"),
    ("2026-10-09", "Lineage anchor restated", "TCD-040 is the locked anchor: Tobias is the biological father of Katherine (with Michelle) and of Melena (with Lucia); they are paternal half-sisters. It doesn’t make Katherine legally acknowledged, a Lockwood by law, a princess, publicly known, or an heir. TCD-059 governs concealment only. (Restates existing rulings; no new canon.)", "IV.11 · IV.11 record"),
]


def front_matter():
    meta("TITLE", "FTE", "", "", folio="")
    emit(f'<div class="titlepg"{attrs("TITLE", newpage="1")}>'
         '<div class="tk">THE TANDEM COMPANION · BUILD 2</div>'
         '<div class="tt">For Their Entertainment</div><div class="ts">Remnia</div>'
         '<div class="tsub">Standalone FTE Companion · Reference, Working Pages, and the Remnian Lineage Record</div>'
         '<div class="tmeta">'
         '<div><b>AUTHORED COPY</b>The Tandem Companion — Content Master, Stage 3 · Sep 26, 2026</div>'
         '<div><b>PRODUCTION SYSTEM</b>The Tandem Companion — Production Master · Direction C</div>'
         '<div><b>SOURCE AUTHORITY</b>Tandem Source Authority Audit — Working Record · Sep 26, 2026</div>'
         '<div><b>AUTHOR RULINGS</b>TCD-001–064 · TCD-058 clarification (2026-09-26) · IV.2 / IV.3 status corrections (2026-10-09)</div>'
         '<div><b>LINEAGE RECORD</b>Rebuilt from evidence, 2026-10-09. A derived record, not a source.</div>'
         f'<div><b>ASSEMBLED</b>{BUILD_DATE}</div>'
         '</div></div>')

    meta("ABOUT", "FTE", "BUILD 2 › ABOUT THIS VOLUME", "ABOUT THIS VOLUME", folio="ABOUT")
    opener("ABOUT", "B2", "VOLUME NOTE · BUILD 2", "About This Volume", "What this standalone volume holds, and how to read its references.", "FTE")
    for p in [
        "This is Build 2 of the Tandem Companion: a standalone working volume for <i>For Their Entertainment</i> and Remnia. "
        "It carries Part I (how the Companion works) in full, the Part II sections FTE depends on, and all of Part IV, with working pages for IV.10 and IV.25 "
        "and a rebuilt working record of the Remnian imperial and royal lineage after IV.11. "
        "The copy is the locked Stage 3 Content Master; this volume lays it out and adds working pages. It doesn’t add canon.",
        "Some pages point to sections that live only in the full Tandem Companion. Two conventions keep those pointers honest:",
    ]:
        emit(f'<p{attrs("ABOUT")}>{p}</p>')
    emit(f'<ul class="lst"{attrs("ABOUT")}>'
         '<li><b>Continuity Room and 3SL pointers resolve here.</b> References to VII.1, VII.2, VII.5, VII.7, VII.8, VII.10, VII.12 and Part VII, and to the 3SL sections III.3, III.13–III.16, III.18, III.20 and Part III, '
         'lead to the FTE Continuity Room concordance near the end of this volume, which names where the FTE information already sits in these pages.</li>'
         '<li><b>Everything else outside the volume carries a dagger (†).</b> A reference marked † is to a section of the full Tandem Companion that isn’t printed here.</li>'
         '<li><b>Page numbers.</b> “See also” chips give the page where each in-volume section starts.</li></ul>')
    emit(f'<div class="sh cap"{attrs("ABOUT", keep_next="1")}>Corrections applied in this volume</div>')
    emit(f'<p{attrs("ABOUT")}>Two author status corrections post-date the Content Master and are applied where the claims appear (IV.2, IV.3). '
         'The lineage reconstruction also corrected one status and several source attributions in IV.11, IV.12 and IV.22; each is logged in the QA report with the exact text it replaces. '
         'Rulings without a TCD number are listed in Appendix A.</p>')
    emit(f'<div class="lg rul"{attrs("ABOUT")}><span class="lt">AUTHOR CORRECTION · 2026-10-09 · IV.2 AND IV.3</span>'
         f'<div class="rr">{badge("c", "CANON")}<div>Remnia is an empire on its own continental landmass, separated from Somnoria by ocean; the Crown sits at the highest public civil/dynastic level of the Remnian sovereignty structure.</div><div class="pv">TCD-025 · TCD-041</div></div>'
         f'<div class="rr">{badge("d", "DRAFTED")}<div>Remnia has seventeen provinces.</div><div class="pv">FTE Beta (ch. 2 and two further passages; IV.2)</div></div>'
         f'<div class="rr">{badge("d", "DRAFTED")}<div>The military structure (the Legion, the Vanguard, the En Guard). TCD-041 is the layered sovereignty framework, not the military’s place in it.</div><div class="pv">FTE Beta chs. 1, 5, 26</div></div>'
         '</div>')
    emit(f'<div class="sh cap"{attrs("ABOUT", keep_next="1")}>The lineage record</div>')
    emit(f'<p{attrs("ABOUT")}>The pages after IV.11 rebuild the Remnian imperial and royal lineage from the sources, claim by claim. Each claim carries its source and the status that source earns. '
         'Biology, legal family status, the public record, titles and succession are kept in separate layers. The record is a derived working record, not a new source, and it settles nothing the rulings leave open. '
         'The unaudited <i>Imperial Lineage</i> was used only for comparison.</p>')
    emit(f'<div class="sh cap"{attrs("ABOUT", keep_next="1")}>What isn’t in this volume</div>')
    emit(f'<p{attrs("ABOUT")}>Part III and Parts V–VII (3SL, ADST, TSWK and the full Continuity Room); the Part II sections FTE doesn’t stand on (II.1, II.3, II.7–II.12); '
         'and Appendix D. The appendices printed here are FTE slices: the rulings, conflicts, sources and terms this volume cites.</p>')

    meta("TOC", "FTE", "BUILD 2 › CONTENTS", "CONTENTS", folio="CONTENTS")
    opener("TOC", "B2", "CONTENTS · BUILD 2", "Contents", "", "FTE")
    emit(f'<div id="toc-src"{attrs("TOC")}></div>')


# ---------------------------------------------------------------- parts
def divider(part, codes, intro_lines, note=None):
    sec = f"PART-{part}"
    station = "FTE" if part == "IV" else "SPINE"
    meta(sec, station, f"{station} › PART {part}", f"PART {part}", folio=f"PART {part}")
    big = f'<div class="pnum">{part}</div>'
    title = PARTS[part]["title"]
    emit(f'<div class="dv"{attrs(sec, newpage="1")}>{big}<div><div class="kind">PART {part} · BUILD 2</div><h1 class="pt">{esc(title)}</h1></div></div>')
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
    station = "FTE" if part == "IV" else "SPINE"
    crumb = f"{station} › {code} {s['title'].upper()}"
    meta(code, station, crumb, f"{code} · {s['title'].upper()}", notes=(part == "IV"), part=part)
    deck = PME.get(code, ("", "", ""))[1]
    deck = re.sub(r"\*", "", deck)
    opener(code, code, f"{KIND.get(code, '')} · {PART_NAME[part]}", s["title"], deck, station)
    blocks = parse_blocks(s["lines"])
    if code == "IV.2":
        emit(f'<div class="lg rul"{attrs(code)}><span class="lt">STATUS · AUTHOR CORRECTION 2026-10-09</span>'
             f'<div class="rr">{badge("c", "CANON")}<div>An empire on its own continental landmass, separated from Somnoria by ocean; the Crown at the highest public civil/dynastic level of the sovereignty structure.</div><div class="pv">TCD-025 · TCD-041</div></div>'
             f'<div class="rr">{badge("d", "DRAFTED")}<div>Seventeen provinces.</div><div class="pv">FTE Beta</div></div></div>')
    render_blocks(code, blocks)


# ---------------------------------------------------------------- shared working-page helpers (approved Direction C pages)
def wq(sec, badges_html, head, prompt, tied, min_lines, weight=1, decision=True, anchor=None):
    a = f' data-wanchor="{anchor}"' if anchor else ""
    return (f'<div class="wb"{attrs(sec, flex=weight)}{a}><div class="wq"><div class="g">{badges_html}</div>'
            f'<div><div class="sh">{head}</div><div class="pt">{prompt}</div></div><div class="pv">{tied}</div></div>'
            f'<div class="rl" data-min="{min_lines}" style="height:{min_lines * LINE}px"></div>{ds_row() if decision else ""}</div>')


def fixed_row(sec, badges_html, label, text, pv, keep=False):
    lab = f'<div class="sh">{label}</div>' if label else ""
    return f'<div class="fixed"{attrs(sec, keep_next="1" if keep else None)}><div class="g">{badges_html}</div><div>{lab}<div class="pt">{text}</div></div><div class="pv">{pv}</div></div>'


def wopener(sec, kicker, title, deck="", anchor=None, crumb=None, spread=None, station="FTE"):
    disp = DISP.get(sec, sec)
    opener(sec, disp, kicker, title, deck, station)
    extra = ""
    if anchor:
        extra += f' data-anchor="{anchor}"'
    if crumb:
        extra += f' data-crumb="{esc(crumb)}"'
    if spread:
        extra += f' data-spread="{spread}"'
    OUTPUT[-1] = OUTPUT[-1].replace('data-newpage="1"', 'data-newpage="1"' + extra, 1)


def rlines(n):
    return f'<div class="rl" data-min="{n}" style="height:{n * LINE}px"></div>'


def ckbox(*labels):
    return "".join(f'<span class="ck"><b></b>{l}</span>' for l in labels)


def flow(boxes):
    """Expression diagram: boxes joined by arrows (grayscale: border weight/style carries meaning)."""
    out = []
    for k, (t, style) in enumerate(boxes):
        if k:
            out.append('<span class="fa ar">→</span>')
        out.append(f'<div class="nb {style}">{t}</div>')
    return f'<div class="flow">{"".join(out)}</div>'


EXPR = [("Ancestral capacity", ""), ("Organized around Frost", ""), ("Frost configuration fails", "dash"), ("Reroutes to Fire", "heavy")]


# ---------------------------------------------------------------- IV.10 · your pages (approved artboards W-ref-IV10, W-IV10-2 … 6)
def iv10_working():
    W = "IV.10W"
    meta(W, "FTE", "FTE › IV.10 · YOUR PAGES", "IV.10 · YOUR PAGES", work=True, folio="IV.10·W")
    B = badge
    K = 'YOUR PAGES · <span class="wn"></span> · KATHERINE’S ELEMENTAL ANATOMY'

    # 1 · Reference: Katherine vs Zephyr
    wopener(W, K.replace("YOUR PAGES ·", "YOUR PAGES · REFERENCE ·"), "Katherine vs Zephyr", "Replace the Dyad label with the ruled anatomy.", anchor="W10-1", crumb="FTE › IV.10 · REFERENCE")
    def cell(st, txt, pv=""):
        b = B(*st) if st else ""
        pvh = f'<div class="pv">{pv}</div>' if pv else ""
        return f'<div class="kc">{b}<div>{txt}</div>{pvh}</div>'
    blank = f'<td class="wcell">{rlines(2)}</td>'
    rows = [
        ("CLASSIFICATION", cell(("c", "CANON"), "One less-specialized ancestral capacity", "TCD-049 · TCD-058"),
         f'<td>{cell(("c", "CANON"), "Modern Fire/Frost Dyad", "TCD-049")}</td>'),
        ("DOMINANT", cell(("c", "CANON"), "Frost, from childhood", "TCD-058"), blank),
        ("FIRE", cell(("c", "CANON"), "Rerouted expression after catastrophic Frost failure, in the Challenge Six climax", "TCD-058 · author ruling 2026-09-26"),
         f'<td>{cell(("c", "CANON"), "One of two modern channels", "TCD-049")}{cell(("s", "SUPPORTED"), "Since thirteen, after a training accident", "FTE 31–39")}</td>'),
        ("ON-PAGE BASELINE", cell(("d", "DRAFTED"), "The Examination: severe Fire trauma still producing Frost", "Beta ch. 7"),
         f'<td>{cell(("d", "DRAFTED"), "Tundra: “orange fire edged with blue” in one hand, something else in the other; Melena sees both elements (ch. 18); Katherine sees them (ch. 17)", "Beta chs. 17–18")}</td>'),
        ("SUPPRESSION", cell(("c", "CANON"), "No established magical suppression", "TCD-058"), blank),
        ("SANCTUM’S LABEL", cell(("c", "CANON"), "“Dyad”: the Sanctum’s incomplete diagnosis", "TCD-049"),
         f'<td>{cell(("c", "CANON"), "“Dyad”: correct", "TCD-049")}</td>'),
        ("REGISTERED AS", cell(("d", "DRAFTED"), "Frost", "Beta"),
         f'<td>{cell(("x", "CONFLICT"), "Flamer (Placements) vs a Frost emblem older than the Flamer marks (31–39 ch. 38)", "49th Placements · FTE 31–39")}</td>'),
        ("OPEN", cell(("o", "OPEN"), "Objective name; exact climax failure beat; later switching and simultaneous use; costs; inheritance side"), blank),
    ]
    tr = "".join(f'<tr><td class="kf">{f}</td><td>{k}</td>{z}</tr>' for f, k, z in rows)
    emit(f'<table class="tb kz"{attrs(W, split="1")}><colgroup><col style="width:128px"><col><col style="width:262px"></colgroup>'
         f'<thead><tr><th></th><th>KATHERINE NICHOLAS</th><th>ZEPHYR</th></tr></thead><tbody>{tr}</tbody></table>')
    emit(f'<p class="kzn"{attrs(W)}>Zephyr’s column is filled only where a source speaks (IV.10, IV.9). Ruled cells are yours: fill them from the controlling source on the next page.</p>')
    emit(f'<div class="xd"{attrs(W)}>{flow(EXPR)}</div>')
    emit(f'<div class="lg rul"{attrs(W)}><span class="lt">{B("c", "CANON")} WHAT’S RULED</span>'
         '<p>The Sanctum would call Katherine a Dyad. It’d be wrong. Zephyr is a modern Fire/Frost Dyad; Katherine is one older, less-specialized capacity that organized itself around Frost. '
         'Fire isn’t a second channel waiting behind a door. It’s where the capacity reroutes when the Frost configuration fails.</p>'
         '<div class="pv">TCD-036 · 049 · 058 · DRAFTED: FTE Official Beta Reader Copy · RECORD: Katherine Elemental Classification + Expression Architecture</div></div>')
    emit(wq(W, B("o", "OPEN"), "QUESTION TO CARRY INTO THE DRAFT",
            "Where does the Frost configuration fail on the page, and what does the reader see before Fire arrives?",
            'TIED TO<br>Open · exact climax failure beat<br><span class="chip" data-wref="W10-3"></span>', 6, 2, decision=False))

    # 2 · The Record
    wopener(W, K, "The Record", anchor="W10-2", crumb="FTE › IV.10 · YOUR PAGES")
    emit(wq(W, B("d", "DRAFTED"), "1 · THE BASELINE ON THE PAGE", "List every drafted moment where Frost holds under pressure, with chapter. Start with the Beta Examination.",
            "TIED TO<br>Beta Examination: severe Fire trauma still producing Frost", 0, 0, decision=False).replace('<div class="rl" data-min="0" style="height:0px"></div>', ""))
    tr = "".join(f'<tr class="blank"><td>{rlines(2)}</td><td>{rlines(2)}</td><td>{rlines(2)}</td></tr>' for _ in range(8))
    emit(f'<table class="tb wt"{attrs(W, split="1")}><colgroup><col style="width:64px"><col><col style="width:220px"></colgroup>'
         f'<thead><tr><th>CH.</th><th>MOMENT</th><th>WHAT IT SHOWS</th></tr></thead><tbody>{tr}</tbody></table>')
    emit(wq(W, '<span class="tf">TO FILL</span>', "2 · COMPLETE ZEPHYR’S COLUMN",
            "Fill the fields the reference page leaves open, from the controlling source. Mark each claim’s status and cite the chapter. Registration is a live conflict: record the evidence, not a guess.",
            'TIED TO<br>Zephyr column <span class="chip" data-wref="W10-1"></span>', 0, 0, decision=False).replace('<div class="rl" data-min="0" style="height:0px"></div>', ""))
    zrows = [("DOMINANT", ""), ("SUPPRESSION", ""),
             ("REGISTERED AS", f'{B("x", "CONFLICT")} <span class="pv">Placements: Flamer · 31–39 ch. 38: Frost emblem older</span>'),
             ("OPEN", "")]
    tr = "".join(f'<tr><td class="kf">{f}</td><td>{pre}{rlines(3)}</td><td class="st">{ckbox("C", "D", "S")}</td><td>{rlines(1)}</td></tr>' for f, pre in zrows)
    emit(f'<table class="tb wt"{attrs(W, split="1")}><colgroup><col style="width:132px"><col><col style="width:132px"><col style="width:64px"></colgroup>'
         f'<thead><tr><th>FIELD</th><th>ZEPHYR</th><th>STATUS</th><th>CH.</th></tr></thead><tbody>{tr}</tbody></table>')
    emit(f'<div class="src"{attrs(W)}><span class="srl">SOURCE</span><span class="srt">FTE Official Beta Reader Copy · FTE Elemental Factions · 49th Placements</span></div>')
    emit(f'<div class="wb"{attrs(W, flex=1)}><div class="sh">NOTES · THE RECORD</div>{rlines(0)}</div>')

    # 3 · The Failure Beat (spread with 4)
    wopener(W, K.replace("KATHERINE’S", "SPREAD WITH THE NEXT PAGE · KATHERINE’S"), "The Failure Beat", anchor="W10-3", crumb="FTE › IV.10 · YOUR PAGES · SPREAD →", spread="left")
    emit(f'<div class="fixed"{attrs(W)}><div class="g">{B("c", "CANON")}</div><div><div class="sh">WHAT’S RULED</div>{flow(EXPR)}</div>'
         f'<div class="pv">TCD-049 · TCD-058<br>author ruling 2026-09-26<br><span class="chip" data-wref="W10-1"></span></div></div>')
    emit(wq(W, B("o", "OPEN"), "1 · WHERE IN THE CLIMAX",
            "Where in the Challenge Six climax does the Frost configuration fail? Name the chapter and what the scene is fighting over when it happens.",
            'TIED TO<br>TCD-058 · author ruling 2026-09-26<br><span class="chip" data-ref="IV.24">IV.24</span>', 6, 2))
    emit(wq(W, B("o", "OPEN"), "2 · BEFORE FIRE ARRIVES",
            "What does the reader see before Fire arrives? Build the failure from the Frost side: what holds, what slips, what breaks.",
            "TIED TO<br>Frost configuration fails → reroutes to Fire", 6, 3))
    # 4 · Draft the Beat
    wopener(W, K.replace("KATHERINE’S", "SPREAD WITH THE PREVIOUS PAGE · KATHERINE’S"), "Draft the Beat", anchor="W10-4", crumb="FTE › IV.10 · YOUR PAGES · ← SPREAD", spread="right")
    emit(wq(W, B("c", "CANON"), "3 · WHAT THE BEAT MUST NOT IMPLY",
            "Fire isn’t a second channel waiting behind a door. No established magical suppression is lifting. Note any drafted line that implies either.",
            'TIED TO<br>TCD-049 · TCD-058<br>Suppression row <span class="chip" data-wref="W10-1"></span>', 5, 1, decision=False))

    emit(wq(W, B("o", "OPEN"), "4 · THE BEAT, IN SCENE ORDER",
            "Draft or outline the failure beat here, from the last moment Frost holds to the first moment Fire answers.",
            "TIED TO<br>Open · exact climax failure beat", 9, 3, decision=False))
    emit(f'<div class="lg drc"{attrs(W)}><span class="lt">DECISION RECORD</span>'
         f'<div class="dr1"><div class="sh">STATUS&nbsp; {ckbox("C", "P", "?", "X", "R")}</div><div class="fl">DECIDED<u></u></div><div class="fl">LOG NO.<u></u></div><div class="fl">DATE<u></u></div></div>'
         f'<div class="dr2">{ckbox("SAFE TO DEFER")}<div class="fl">DECIDE BY<u></u></div><div class="fl">AFFECTED PAGES<u></u></div></div>'
         '<p>When drafted prose deliberately changes an entry, the entry changes.</p></div>')

    # 5 · Open Anatomy
    wopener(W, K, "Open Anatomy", anchor="W10-5", crumb="FTE › IV.10 · YOUR PAGES")
    emit(wq(W, B("o", "OPEN"), "5 · OBJECTIVE NAME", "The Sanctum’s label is incomplete. What is the capacity actually called, and who in the story could know that name?",
            "TIED TO<br>Open · objective name", 5, 2))
    emit(wq(W, B("o", "OPEN"), "6 · LATER SWITCHING AND SIMULTANEOUS USE",
            "After the reroute, can she move between Frost and Fire, or hold both at once? What would the page have to show first for either to read as earned?",
            "TIED TO<br>Open · later switching and simultaneous use", 5, 3))
    emit(wq(W, B("o", "OPEN"), "7 · COSTS", "What does the reroute cost her, and when does the reader first see the cost?", "TIED TO<br>Open · costs", 5, 2))

    # 6 · Label and Lineage
    wopener(W, K, "Label and Lineage", anchor="W10-6", crumb="FTE › IV.10 · YOUR PAGES · SEE ALSO IV.5")
    emit(wq(W, B("c", "CANON"), "8 · WHO REPEATS THE LABEL",
            "The Sanctum’s “Dyad” is an incomplete diagnosis. Who in FTE repeats it, and where does the text let it stand uncorrected?",
            'TIED TO<br>TCD-049 · TCD-058<br><span class="chip" data-ref="II.6">II.6</span><span class="chip" data-ref="II.15">II.15</span>', 6, 3, decision=False))
    emit(wq(W, B("o", "OPEN"), "9 · INHERITANCE SIDE",
            "Which side of her lineage carries the ancestral capacity? Check the five layers in IV.11 (Biological, Legal, Recorded, Public, Succession) before deciding.",
            'TIED TO<br>Open · inheritance side<br><span class="chip" data-ref="IV.11">IV.11</span><span class="chip" data-ref="IV.11R">IV.11R</span>', 5, 2))
    emit(f'<div class="wb nb2"{attrs(W, flex=2)}><div class="wq"><div class="g"><span class="sh">NOTES</span></div><div><div class="sh">WHAT THIS ENTRY STARTED AND DIDN’T FINISH</div>'
         '<div class="pt">Carry anything unresolved to the Open Canon Queue with a date.</div></div><div class="pv"><span class="chip" data-ref="VII.12">VII.12</span></div></div>'
         f'{rlines(4)}</div>')


# ---------------------------------------------------------------- IV.11 record · Remnian imperial + royal lineage (src/lineage.py)
ST_WORD = {"c": "CANON", "d": "DRAFTED", "s": "SUPPORTED", "p": "POSSIBLE", "o": "OPEN", "x": "CONFLICT", "l": "LEGACY"}
GENEALOGY_IDS = {}


def srcs_label(srcs):
    return " · ".join(LIN.SOURCES[s][0] if s in LIN.SOURCES else s for s in srcs)


MK_LETTER = {"c": "C", "d": "D", "s": "S", "p": "P", "o": "O", "x": "X", "l": "L"}


def mk(st):
    return f'<span class="mk {st}"><i></i>{MK_LETTER[st]}</span>'


def person_lcs(pid):
    ids = set()
    for c in LIN.PERSONS[pid]["claims"]:
        ids |= set(re.findall(r"LC-\d{2}", c[2] + " " + c[5]))
    return sorted(ids)


# panel geometry: pid -> (x, y, w, h, display name, [(line, status)], style)
IMPERIAL = {
    "caliane": (0, 0, 150, 112, "Caliane Azira Hastings", [("F2025 only; line not stated", "l")], "alt"),
    "eden": (240, 0, 180, 112, "Eden Genesis", [("Founding Empress", "l"), ("Precedes Aracelia", "s")], ""),
    "richard": (0, 140, 146, 96, "Richard Hastings", [("Great-uncle of Elias", "s")], ""),
    "aracelia": (160, 140, 160, 96, "Aracelia", [("Empress at FTE", "d"), ("b. 2038", "s")], ""),
    "jackson": (332, 140, 116, 96, "Jackson Harper", [("Lucia’s father", "l")], "leg"),
    "alistair_l": (462, 140, 210, 96, "Alistair & Rowena Lockwood", [("Tobias’s parents", "s")], ""),
    "lucia": (160, 272, 160, 140, "Lucia Hastings-Lockwood", [("Crown Princess", "s"), ("b. 2047 or 2055", "x")], ""),
    "tobias": (380, 272, 140, 140, "Tobias Lockwood", [("Prince Consort", "s"), ("Dead before FTE", "s")], ""),
    "michelle": (540, 272, 132, 140, "Michelle Nicholas", [("Former En Guard Captain", "d")], ""),
    "elias": (0, 452, 120, 132, "Elias Lockwood", [("Crown Prince", "c"), ("Missing at FTE", "c")], ""),
    "melena": (128, 452, 120, 132, "Melena Lockwood", [("2nd in line", "d"), ("Flamer", "d")], ""),
    "cordelia": (256, 452, 120, 132, "Cordelia Lockwood", [("3rd in line", "s"), ("Frost", "d")], ""),
    "louis": (384, 452, 112, 132, "Louis Lockwood", [("4th in line", "s")], ""),
    "katherine": (520, 452, 152, 132, "Katherine Nicholas", [("Registered Frost", "d"), ("Not in the recorded line", "o")], ""),
    "ethan": (520, 628, 152, 126, "Ethan", [("Medina or Nicholas", "x"), ("Bio. father: superseded", "l")], "sup"),
}
LONDON = {
    "samantha": (100, 0, 170, 84, "Samantha Kinross", [("First Queen; TLE only", "l")], "leg"),
    "edward": (330, 0, 180, 84, "Edward Kinross", [("King; “Edward XVIII”", "s")], ""),
    "nathaniel": (0, 130, 150, 108, "Nathaniel Kinross", [("King 2058–2090", "s"), ("Abdicated", "s")], ""),
    "dalia": (190, 130, 170, 108, "Dalia", [("Queen from 2090", "s"), ("b. 2038", "s")], ""),
    "david": (400, 130, 128, 108, "David Augustine", [("Prince Consort", "s")], ""),
    "william": (540, 130, 132, 108, "King William", [("WTR, instead of David", "x")], "alt"),
    "maxim": (0, 300, 104, 120, "Maxim", [("Crown Prince", "s"), ("Terrain", "d")], ""),
    "minho": (113, 300, 104, 120, "Minho", [("Gave up claim", "s"), ("Blocker", "d")], ""),
    "zephyr": (226, 300, 104, 120, "Zephyr", [("Fire/Frost Dyad", "c"), ("Twin of Zoe", "s")], ""),
    "zoe": (339, 300, 104, 120, "Zoe", [("Twin of Zephyr", "s"), ("BSS only", "s")], ""),
    "sebastian": (452, 300, 104, 120, "Sebastian", [("Gave up claim", "s"), ("Flamer", "d")], ""),
    "orion": (568, 300, 104, 120, "Orion", [("b. 2090", "s"), ("BSS only", "s")], ""),
    "arielle": (0, 460, 200, 84, "Arielle Monet Kinross", [("The Princess Royal", "s"), ("Parent not named · O-05", "o")], ""),
}
LINE_STYLE = {"c": 'stroke-width="4"', "d": 'stroke-width="2"', "s": 'stroke-width="2" stroke-dasharray="7 4"',
              "l": 'stroke-width="1.75" stroke-dasharray="1.5 4" stroke-linecap="round"', "x": 'stroke-width="2" stroke-dasharray="7 4"', "p": 'stroke-width="1.75" stroke-dasharray="1.5 4" stroke-linecap="round"'}
XM = '<span class="sc x"><i></i></span>'


def gnode(pid, spec):
    x, y, w, h, name, lines, style = spec
    lcs = person_lcs(pid)
    GENEALOGY_IDS[pid] = lcs
    body = "".join(f'<div class="gl">{mk(st)}<span>{esc(t)}</span></div>' for t, st in lines)
    cx = f'<div class="gx">{XM}<span>LC-{" · ".join(x[3:] for x in lcs)}</span></div>' if lcs else ""
    tag = {"alt": "ALTERNATIVE", "leg": "EARLIER POOL ONLY", "sup": "SUPERSEDED LINK"}.get(style, "")
    tg = f'<div class="gt2">{tag}</div>' if tag else ""
    return (f'<div class="gn {style}" data-pid="{pid}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">{tg}'
            f'<div class="gnm">{esc(name)}</div>{body}{cx}</div>')


def seg(x1, y1, x2, y2, st):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#1a1a1a" {LINE_STYLE[st]}/>'


def poly(points, st):
    pts = " ".join(f"{a},{b}" for a, b in points)
    return f'<polyline points="{pts}" fill="none" stroke="#1a1a1a" {LINE_STYLE[st]}/>'


def elabel(x, y, text, cls=""):
    return f'<span class="el {cls}" style="left:{x}px;top:{y}px">{text}</span>'


def bot(spec):
    x, y, w, h = spec[:4]
    return x + w / 2, y + h


def topc(spec):
    x, y, w, h = spec[:4]
    return x + w / 2, y


def genealogy_imperial(sec):
    N = IMPERIAL
    svg, labels = [], []
    def edge(a, b, st, lab=None, dx=0, lx=None):
        (x1, y1), (x2, y2) = bot(N[a]), topc(N[b])
        svg.append(seg(x1 + dx, y1, x2, y2, st))
        if lab:
            labels.append(elabel(lx if lx is not None else (x1 + dx + x2) / 2 + 6, (y1 + y2) / 2 - 9, lab))
    edge("eden", "aracelia", "s", f"{XM} LC-04 · LC-05")
    edge("eden", "richard", "l", None, -40)
    edge("aracelia", "lucia", "s", f"{XM} LC-03", lx=166)
    edge("jackson", "lucia", "l")
    edge("alistair_l", "tobias", "s", f"{XM} LC-14")
    uy = N["lucia"][1] + 46
    bus = N["elias"][1] - 22
    svg.append(seg(320, uy, 380, uy, "s")); labels.append(elabel(331, uy - 20, "m.", "sm"))
    svg.append(seg(520, uy, 540, uy, "c")); labels.append(elabel(492, N["tobias"][1] + N["tobias"][3] + 4, "TCD-040", "sm"))
    mx = topc(N["melena"])[0]
    svg.append(poly([(346, uy), (346, bus - 8), (mx, bus - 8), (mx, N["melena"][1])], "c"))
    for pid in ("elias", "cordelia", "louis"):
        cx = topc(N[pid])[0]
        svg.append(poly([(354, uy), (354, bus), (cx, bus), (cx, N[pid][1])], "s"))
    kx = topc(N["katherine"])[0]
    svg.append(poly([(530, uy), (530, bus), (kx, bus), (kx, N["katherine"][1])], "c"))
    by = N["melena"][1] + N["melena"][3]
    svg.append(poly([(mx, by), (mx, by + 22), (560, by + 22), (560, by)], "c"))
    labels.append(elabel(210, by + 26, f'PATERNAL HALF-SISTERS · {badge("c", "CANON")} TCD-040', "hs"))
    ex = 650
    svg.append(seg(ex, N["ethan"][1], ex, by, "l"))
    labels.append(elabel(566, by + 22, "× SUPERSEDED", "sm sup"))
    nodes = "".join(gnode(p, N[p]) for p in N)
    H = 756
    legend = genealogy_legend(0, 636, 500)
    return (f'<div class="gtree"{attrs(sec)} style="height:{H}px"><svg width="672" height="{H}" viewBox="0 0 672 {H}">{"".join(svg)}</svg>'
            f'{nodes}{"".join(labels)}{legend}</div>')


def genealogy_london(sec):
    N = LONDON
    svg, labels = [], []
    def edge(a, b, st, lab=None, ox=0):
        (x1, y1), (x2, y2) = bot(N[a]), topc(N[b])
        svg.append(seg(x1 + ox, y1, x2, y2, st))
        if lab:
            labels.append(elabel((x1 + x2) / 2 + 8, (y1 + y2) / 2 - 9, lab))
    edge("edward", "dalia", "s", f"{XM} LC-12", 12)
    edge("samantha", "dalia", "l", None, 12)
    edge("edward", "nathaniel", "s", None, -12)
    edge("samantha", "nathaniel", "l", None, -12)
    uy = N["dalia"][1] + 46
    svg.append(seg(360, uy, 400, uy, "x")); labels.append(elabel(360, uy - 22, f"m. {XM}", "sm"))
    bus = N["maxim"][1] - 22
    for pid in ("maxim", "minho", "zephyr", "zoe", "sebastian", "orion"):
        x2, y2 = topc(N[pid])
        svg.append(poly([(380, uy), (380, bus), (x2, bus), (x2, y2)], "s"))
    labels.append(elabel(388, N["dalia"][1] + N["dalia"][3] + 6, f"{XM} LC-19: order of succession", "sm"))
    nodes = "".join(gnode(p, N[p]) for p in N)
    H = 626
    legend = genealogy_legend(220, 456, 452)
    return (f'<div class="gtree"{attrs(sec)} style="height:{H}px"><svg width="672" height="{H}" viewBox="0 0 672 {H}">{"".join(svg)}</svg>'
            f'{nodes}{"".join(labels)}{legend}</div>')


def genealogy_legend(x, y, w):
    def sample(st):
        return f'<svg width="44" height="10"><line x1="0" y1="5" x2="44" y2="5" stroke="#1a1a1a" {LINE_STYLE[st]}/></svg>'
    rows = [(sample("c"), "CANON link (ruling)"), (sample("d"), "DRAFTED link"), (sample("s"), "SUPPORTED link"),
            (sample("l"), "LEGACY / earlier pool only"), ('<span class="sc x"><i></i></span>', "LC-nn: conflict, see D")]
    keys = "".join(f'<div>{a}<span>{b}</span></div>' for a, b in rows)
    marks = " ".join(mk(k) for k in "cdspoxl")
    return (f'<div class="glg" style="left:{x}px;top:{y}px;width:{w}px"><div class="sh">KEY</div><div class="glk">{keys}</div>'
            f'<div class="glm">{marks}<span>status of each line in a box</span></div>'
            '<div class="glm"><span class="bx alt"></span><span>alternative person</span><span class="bx leg"></span><span>earlier pool only</span></div></div>')


def ledger_rows():
    order = ["eden", "caliane", "aracelia", "jackson", "richard", "alexandria", "lucia",
             "alistair_l", "rowena", "tobias", "celeste_aunt", "elias", "melena", "cordelia", "louis",
             "michelle", "ethan", "katherine",
             "samantha", "edward", "nathaniel", "dalia", "david", "william", "maxim", "minho", "zephyr", "zoe", "sebastian", "orion", "arielle"]
    assert set(order) == set(LIN.PERSONS), set(LIN.PERSONS) ^ set(order)
    layer_order = {"BIO": 0, "LEGAL": 1, "PUBLIC": 2, "TITLE": 3, "SUCC": 4}
    layer_name = {"BIO": "BIOLOGICAL", "LEGAL": "LEGAL FAMILY", "PUBLIC": "PUBLIC / RECORDED", "TITLE": "TITLE", "SUCC": "SUCCESSION"}
    out = []
    for pid in order:
        p = LIN.PERSONS[pid]
        var = f' <span class="pv">· also {escx("; ".join(p["variants"]))}</span>' if p["variants"] else ""
        out.append(f'<tr class="ph" data-keep-next="1"><td colspan="5"><span class="tm">{escx(p["name"])}</span> <span class="pv">HOUSE · {escx(p["house"])}</span>{var}</td></tr>')
        for c in sorted(p["claims"], key=lambda c: layer_order[c[0]]):
            out.append(f'<tr><td><span class="lyr">{layer_name[c[0]]}</span><br>{escx(c[1])}</td><td>{escx(c[2])}</td>'
                       f'<td class="st">{badge(c[3], ST_WORD[c[3]])}</td><td><span class="pv">{escx(srcs_label(c[4]))}</span></td><td><span class="pv">{escx(c[5])}</span></td></tr>')
    return "".join(out)


def lineage_record():
    R = "IV.11R"
    meta(R, "FTE", "FTE › IV.11 · LINEAGE RECORD", "IV.11 · LINEAGE RECORD", work=True, folio="IV.11·R")
    K0 = 'WORKING RECORD · <span class="wn"></span> · '
    K = K0 + 'REMNIAN IMPERIAL + ROYAL LINEAGE'
    wopener(R, K, "Remnian Lineage: The Working Record", "Rebuilt from the evidence, 2026-10-09. A derived record, not a source.", anchor="LR-0", crumb="FTE › IV.11 · LINEAGE RECORD")
    for t in [
        "This record rebuilds the Remnian imperial and royal lineage from the sources, claim by claim. Each line names the source it comes from and carries the status that source earns under the authority order: rulings, then the Beta, then current author decisions, development, reference, shared lore, supporting artifacts, and legacy. "
        "It isn’t a source itself, and it settles nothing a ruling leaves open.",
        "Five layers stay apart, as IV.11 requires: biological, legal family status, public and recorded, title, and succession. A parent never fills a succession slot, and a title never proves a parent. "
        "Where two sources disagree, both stay on the page with their sources, and the disagreement gets a number (LC-nn) and a working block in lane D.",
    ]:
        emit(f'<p{attrs(R)}>{t}</p>')
    emit(f'<div class="lg tcd"{attrs(R)}><span class="lt">LOCKED ANCHOR · {badge("c", "CANON")} TCD-040</span>'
         '<p>Tobias Lockwood is the biological father of Katherine (with Michelle Nicholas) and of Melena (with Lucia Hastings-Lockwood). Katherine and Melena are paternal half-sisters.</p>'
         '<p>That doesn’t make Katherine legally acknowledged, a Lockwood by law, a princess, publicly known, or an heir. TCD-059 governs the concealment only.</p></div>')
    emit(f'<div class="lg gr"{attrs(R)}><span class="lt">GUARDRAIL</span><div class="gt">Agreement between two weak sources isn’t canon. Two timelines that agree are still two timelines.</div></div>')
    emit(f'<div class="sh cap"{attrs(R, keep_next="1")}>In this record</div>')
    toc = [("A", "Genealogy spread: the imperial line; London Town", "LR-A"), ("B", "Lineage ledger, by person and layer; collateral lines; name checks", "LR-B"),
           ("C", "Succession lane: current and historical, kept apart from the tree", "LR-C"), ("D", "Open and conflict lane: the conflict ledger, then working space for each decision", "LR-D")]
    emit(f'<table class="tb fc"{attrs(R, split="1")}><colgroup><col style="width:40px"><col><col style="width:80px"></colgroup><thead><tr><th></th><th>PART</th><th>PAGE</th></tr></thead><tbody>'
         + "".join(f'<tr><td>{a}</td><td>{b}</td><td><span class="chip" data-wref="{c}"></span></td></tr>' for a, b, c in toc) + '</tbody></table>')

    emit(f'<div class="sh cap"{attrs(R, keep_next="1")}>Source key · authority treatment in this record</div>')
    tr = "".join(f'<tr><td><span class="cd">{escx(v[0])}</span></td><td><b>{escx(v[1])}</b><br><span class="pv">{escx(v[3])}</span></td><td>{escx(v[2])}</td></tr>' for k, v in LIN.SOURCES.items())
    tr += '<tr><td><span class="cd">TCD-nnn</span></td><td><b>Canon Decision Log rulings</b><br><span class="pv">Audit, Sep 26, 2026 (Appendix A).</span></td><td>Highest authority. The only route to CANON.</td></tr>'
    emit(f'<table class="tb ap"{attrs(R, split="1")}><colgroup><col style="width:78px"><col style="width:250px"><col></colgroup>'
         f'<thead><tr><th>LABEL</th><th>FILE · AVAILABILITY</th><th>AUTHORITY IN THIS RECORD</th></tr></thead><tbody>{tr}</tbody></table>')
    emit(f'<p class="kzn"{attrs(R)}>Status words: DRAFTED = CURRENT DRAFTED TEXT; LEGACY = LEGACY / SUPERSEDED. In the genealogy, each line in a box carries a status letter: '
         + " ".join(mk(k) for k in "cdspoxl") + '.</p>')
    # A · genealogy spread
    wopener(R, K0 + "A · GENEALOGY · SPREAD →", "The Imperial Line", "", anchor="LR-A", crumb="FTE › IV.11 RECORD · A · GENEALOGY · SPREAD →", spread="left")
    emit(genealogy_imperial(R))
    wopener(R, K0 + "A · GENEALOGY · ← SPREAD · KINROSS AND AUGUSTINE", "London Town", "", anchor="LR-A2", crumb="FTE › IV.11 RECORD · A · ← SPREAD")
    emit(genealogy_london(R))
    emit(f'<p class="kzn"{attrs(R)}>The tree shows parentage only. Who rules and who is next is in lane C, and nothing in the tree is evidence for it. '
         'Collateral lines that only the earlier timeline records (Eden’s other children, Lucia’s sisters, Dalia’s sisters) are in the ledger, not the tree.</p>')

    # B · ledger
    wopener(R, K0 + "B · LINEAGE LEDGER", "Lineage Ledger", "Every claim, by person and layer, with its source and status.", anchor="LR-B", crumb="FTE › IV.11 RECORD · B · LEDGER")
    emit(f'<table class="tb lg2"{attrs(R, split="1")}><colgroup><col style="width:118px"><col><col style="width:104px"><col style="width:84px"><col style="width:118px"></colgroup>'
         f'<thead><tr><th>LAYER · FIELD</th><th>CLAIM</th><th>STATUS</th><th>SOURCE</th><th>NOTE</th></tr></thead><tbody>{ledger_rows()}</tbody></table>')
    emit(f'<div class="sh cap"{attrs(R, keep_next="1")}>Collateral lines · kept, not charted</div>')
    tr = "".join(f'<tr><td>{escx(n)}</td><td>{escx(t)}</td><td class="st">{badge(st, ST_WORD[st])}</td><td><span class="pv">{escx(srcs_label(s))}</span></td></tr>' for n, t, st, s in LIN.COLLATERAL)
    emit(f'<table class="tb fc"{attrs(R, split="1")}><colgroup><col style="width:170px"><col><col style="width:104px"><col style="width:84px"></colgroup>'
         f'<thead><tr><th>PERSON</th><th>WHAT THE SOURCE SAYS</th><th>STATUS</th><th>SOURCE</th></tr></thead><tbody>{tr}</tbody></table>')
    emit(f'<div class="sh cap"{attrs(R, keep_next="1")}>Duplicate-person and name-variant checks</div>')
    tr = "".join(f'<tr><td><span class="cd">{i}</span><br>{escx(n)}</td><td>{escx(f)}</td><td>{escx(d)}</td></tr>' for i, n, f, d in LIN.NAME_CHECKS)
    emit(f'<table class="tb"{attrs(R, split="1")}><colgroup><col style="width:104px"><col><col style="width:220px"></colgroup>'
         f'<thead><tr><th>CHECK</th><th>WHAT THE SOURCES NAME</th><th>HOW THE RECORD TREATS IT</th></tr></thead><tbody>{tr}</tbody></table>')

    # C · succession lane
    wopener(R, K0 + "C · SUCCESSION LANE", "Succession Lane", "Positions, and the act or law behind each. Not the family tree.", anchor="LR-C", crumb="FTE › IV.11 RECORD · C · SUCCESSION")
    emit(f'<div class="lg gr"{attrs(R)}><span class="lt">GUARDRAIL</span><div class="gt">A place in a line needs a law or an act. A parent isn’t one.</div></div>')
    def lane(title, rows, heads):
        emit(f'<div class="sh cap"{attrs(R, keep_next="1")}>{title}</div>')
        tr = "".join(f'<tr><td class="cd">{escx(a)}</td><td><b>{escx(b)}</b></td><td>{escx(c)}</td><td class="st">{badge(st, ST_WORD[st])}</td><td><span class="pv">{escx(srcs_label(s))}</span></td></tr>' for a, b, c, st, s in rows)
        tr += "".join('<tr class="blank">' + "".join(f'<td>{rlines(2)}</td>' for _ in range(5)) + "</tr>" for _ in range(2))
        emit(f'<table class="tb sl"{attrs(R, split="1")}><colgroup><col style="width:74px"><col style="width:150px"><col><col style="width:104px"><col style="width:84px"></colgroup>'
             f'<thead><tr>{"".join(f"<th>{h}</th>" for h in heads)}</tr></thead><tbody>{tr}</tbody></table>')
    lane("Current · the imperial throne, at FTE’s opening", LIN.SUCC_CURRENT_IMPERIAL, ["POSITION", "PERSON", "BASIS", "STATUS", "SOURCE"])
    lane("Current · London Town, at FTE’s opening", LIN.SUCC_CURRENT_LONDON, ["POSITION", "PERSON", "BASIS", "STATUS", "SOURCE"])
    lane("Historical · how the lines got here, as the sources tell it", LIN.SUCC_HISTORY, ["WHEN", "THRONE", "WHAT CHANGED", "STATUS", "SOURCE"])

    # D · open and conflict lane
    wopener(R, K0 + "D · OPEN AND CONFLICT LANE", "Conflict Ledger", "Where the sources disagree, and what would settle it.", anchor="LR-D", crumb="FTE › IV.11 RECORD · D · CONFLICT LEDGER")
    tr = ""
    for cid, claim, a, b, hi, st, stt, change in LIN.CONFLICTS:
        tr += (f'<tr><td><span class="cd">{cid}</span><br><b>{escx(claim)}</b></td><td>{escx(a)}</td><td>{escx(b)}</td><td>{escx(hi)}</td>'
               f'<td class="st">{badge(st, ST_WORD[st])}<br><span class="pv">{escx(stt)}</span></td><td>{escx(change)}</td></tr>')
    emit(f'<table class="tb cl"{attrs(R, split="1")}><colgroup><col style="width:100px"><col><col><col style="width:112px"><col style="width:100px"><col style="width:112px"></colgroup>'
         f'<thead><tr><th>CLAIM</th><th>SOURCE A</th><th>SOURCE B</th><th>HIGHER-AUTHORITY EVIDENCE</th><th>CURRENT STATUS</th><th>WHAT WOULD NEED TO CHANGE</th></tr></thead><tbody>{tr}</tbody></table>')
    emit(f'<div class="sh cap"{attrs(R, keep_next="1")}>Old claims rejected or downgraded</div>')
    tr = "".join(f'<tr><td><span class="cd">{i}</span></td><td>{escx(c)}</td><td><span class="pv">{escx(s)}</span></td><td>{escx(w)}</td><td><span class="pv">{escx(o)}</span></td></tr>' for i, c, s, w, o in LIN.REJECTED)
    emit(f'<table class="tb"{attrs(R, split="1")}><colgroup><col style="width:52px"><col><col style="width:96px"><col style="width:180px"><col style="width:110px"></colgroup>'
         f'<thead><tr><th>ID</th><th>CLAIM</th><th>SOURCE</th><th>WHY</th><th>NOW</th></tr></thead><tbody>{tr}</tbody></table>')

    # D · working space, one block per decision
    wopener(R, K0 + "D · OPEN AND CONFLICT LANE", "Decisions the Record Can’t Make", "Each conflict and open item, with room to work it out. Rulings go to Appendix A with a log number.", anchor="LR-D2", crumb="FTE › IV.11 RECORD · D · DECISIONS")
    by = {c[0]: c for c in LIN.CONFLICTS}
    for did, prompt, lines in LIN.DECISIONS:
        if did in by:
            c = by[did]
            head, st, tied = f"{did} · {c[1].upper()}", c[5], f"TIED TO<br>{escx(c[6])}"
        else:
            o = next(o for o in LIN.OPEN_ITEMS if o[0] == did)
            head, st, tied = f"{did} · {o[1].upper()}", o[3], f"TIED TO<br>{escx(srcs_label(o[4]))}"
        emit(wq(R, badge(st, ST_WORD[st]), escx(head), escx(prompt), tied, lines, 2 if lines >= 6 else 1, anchor=f"LR-{did}"))


# ---------------------------------------------------------------- IV.25 · working pages
BLOCKERS = [
    ("W25-1", "Katherine’s decisive act", "The Decisive Act", ["Katherine's decisive act"], [
        ("THE ACT ITSELF", "What does Katherine do for Melena in the climax that creates the decisive state? Name the action and the moment, and keep it inside her own moral arc, not only sisterhood (TCD-050).", "TIED TO<br>TCD-042 · TCD-050", 8),
        ("IS IT A PRAYER?", "Is the act a Prayer, or something else? If it’s a Prayer, square it with what the Prayer can and can’t do.", "TIED TO<br>TCD-048 · TCD-057", 6)]),
    ("W25-2", "Melena’s investigation", "Melena’s Investigation", ["Melena's investigation"], [
        ("FIRST CLUE", "What is Melena’s first clue, where does she find it, and in which chapter?", "TIED TO<br>TCD-050 · IV.13", 8),
        ("EVIDENCE BEFORE THE DUEL", "List what she holds by the Duel. For each item: what it suggests, and what it can’t prove.", "TIED TO<br>TCD-050: suspicion, not proof", 8),
        ("WHAT SHADOWMERE GAVE HER", "What does she already know from Shadowmere and Lucia’s trail that points toward Katherine?", "TIED TO<br>IV.13 · IV.14", 6)]),
    ("W25-3", "Challenge Six rules", "Challenge Six Rules", ["Challenge Six rules"], [
        ("KILL POLICY", "What does the Sanctum actually allow in a bout, and what does it say in public?", "TIED TO<br>TCD-007 · IV.7", 8),
        ("BOUT ORDER", "List the bouts in order: who fights whom, and why the Sanctum sets it that way.", "TIED TO<br>IV.6 roster", 8),
        ("YIELD RULES", "How does a bout end short of death, and who can call it?", "TIED TO<br>IV.7", 6)]),
    ("W25-4", "Challenge Seven", "Challenge Seven", ["Challenge Seven"], [
        ("WHAT IT WOULD HAVE BEEN", "What would Challenge Seven have demanded? It has to be something Melena chooses to stop from happening.", "TIED TO<br>TCD-007 · TCD-042", 14)]),
    ("W25-5", "The Prayer for Atlas", "The Prayer for Atlas", ["The Prayer for Atlas"], [
        ("TIMING", "When does Katherine perform the Prayer for Atlas? The candidate scene puts it at the end of Challenge Four (Chapter 29.docx).", "TIED TO<br>TCD-009 · IV.17", 7),
        ("COST", "What does the Prayer cost the caster?", "TIED TO<br>IV.17", 6),
        ("MARKS", "Does it leave marks, and where?", "TIED TO<br>IV.17 · IV.5", 6),
        ("BROADCAST", "Does the broadcast show it? Who sees it, and what does the Sanctum learn?", "TIED TO<br>IV.4 · IV.24", 7)]),
    ("W25-5b", "Atlas’s injury", "Atlas’s Injury", ["Atlas's injury"], [
        ("PATHOLOGY", "Is Atlas’s injury acute Element Rot or its own pathology? What is its anatomy?", "TIED TO<br>TCD-051 · IV.16", 7),
        ("PROGRESSION", "Why does it keep progressing after synchronization ends, and what does the Prayer change?", "TIED TO<br>TCD-051 · IV.16", 7)]),
    ("W25-6", "Forfeit procedure", "Forfeit Procedure", ["Forfeit procedure"], [
        ("MAXIM’S RESPONSE", "What does Maxim say and do when Melena brings him the choice? He is alive and conscious, and he authorizes.", "TIED TO<br>TCD-042 · TCD-052", 8),
        ("PUBLIC PROCEDURE", "How is a forfeit made official on the board, in front of the cameras?", "TIED TO<br>IV.8 · IV.20", 6),
        ("EMERGENCY AUTHORITY", "Under what authority does a King forfeit mid-Challenge, and who could contest it?", "TIED TO<br>IV.3 · IV.20", 6)]),
    ("W25-7", "Verification", "Verification", ["Verification"], [
        ("WHICH RECORD", "Which record verifies the paternity, who made it, and where is it kept? The Sanctum keeps the records (TCD-059).", "TIED TO<br>TCD-050 · TCD-059", 8),
        ("WHO AUTHENTICATES", "Who authenticates it, and why is their word enough?", "TIED TO<br>TCD-050 · IV.13", 7)]),
]
GROUPED = [
    ("W25-G1", "Melena, Caelum, Minho", [
        ("How Melena classifies Shadowmere", "INSIDE OR OUTSIDE", "In Melena’s head, is Shadowmere inside Remnia, outside it, or no place a map would name?", "TIED TO<br>IV.2 knowledge flag", 6),
        ("Caelum's mind-presence", "MECHANISM AND RANGE", "How does Caelum’s presence reach Melena’s mind, and how far does it carry? It’s Nightmare magic; he isn’t Nightmare.", "TIED TO<br>TCD-031 · IV.15", 6),
        ("Minho", "ARC, KNOWLEDGE, FATE", "What does Minho want in FTE, what does he know about Katherine, and where does he end? His death isn’t assumed.", "TIED TO<br>TCD-009 · IV.19", 8)]),
    ("W25-G2", "Challenges, titles, calendar, Board", [
        ("Challenge Three's result; Challenge Four's name", "RESULT AND NAME", "Who wins Challenge Three? What is Challenge Four’s canon name? (“The Conduit Trials” is a working title.)", "TIED TO<br>TCD-008 · IV.7", 5),
        ("\"Regnant\"; Rovencia; Easton/Estonian", "TITLE AND PLACES", "Is “Regnant” a real Remnian title? Is Rovencia a province? Easton or “Estonian”?",
         "TIED TO<br>IV.2 · IV.3. New evidence: BSS and TLE use “Regnant” for faction leaders; TLE lists Rovencia among seventeen provinces (SUPPORTED / LEGACY)", 6),
        ("Calendar", "THE ER CALENDAR", "What year is FTE in ER, what is the “49th,” and where does Year 847 sit?",
         "TIED TO<br>TCD-010. TLE makes 2038 Year 13 ER but dates other births “2024 ER”; BSS runs to 2096", 6),
        ("Conqueror bylaws; Board seat", "POWERS AND BENEFITS", "What can a Conqueror do with the one-year Board seat, and what does it give Old Prosperity?", "TIED TO<br>TCD-034 · IV.8", 6),
        ("The Imperial Lineage", "AUDIT STATUS", "Give The Imperial Lineage an audit status.", "TIED TO<br>This volume uses it for comparison only; every claim the Content Master quotes from it is in BSS (record, R-12)", 4)]),
]
REDIRECT = {
    "Frost failure and Fire": ("W10-3", "IV.10 your pages"),
    "Initial publicity of Katherine's birth": ("LR-LC-08", "Lineage record, LC-08"),
    "Remnian knowledge of other lands": ("LR-LC-10", "Lineage record, LC-10"),
    "Melena's eyes": ("LR-LC-01", "Lineage record, LC-01"),
    "Melena's age": ("LR-LC-15", "Lineage record, LC-15"),
    "Zenithia's leadership; London Town's royal house": ("LR-LC-11", "Lineage record, LC-11, LC-20"),
    "Aracelia's name": ("LR-LC-02", "Lineage record, LC-02"),
    "Zephyr's birth registration": ("W10-2", "IV.10 your pages"),
}


def iv25_working():
    W = "IV.25W"
    meta(W, "FTE", "FTE › IV.25 · WORKING PAGES", "IV.25 · WORKING PAGES", work=True, folio="IV.25·W")
    B = badge
    rows = table_rows_after("IV.25", None)
    where = {}
    for anc, _, _, items, _ in BLOCKERS:
        for it in items:
            where[it] = anc
    for anc, _, blocks in GROUPED:
        for it, *_ in blocks:
            where[it] = anc
    for it, (anc, _) in REDIRECT.items():
        where[it] = anc
    K = 'WORKING PAGES · <span class="wn"></span> · FTE OPEN DEVELOPMENT'
    wopener(W, K + " · THE QUEUE", "FTE Open Development", "Every open FTE item, with somewhere to work on it.", anchor="W25-Q", crumb="FTE › IV.25 · THE QUEUE")
    emit(f'<div class="qgr"{attrs(W)}><div class="lg gr"><span class="lt">GUARDRAIL</span><div class="gt">Blockers get their own pages. Everything else waits until a scene needs it.</div></div>'
         '<div class="pv"><b>OPEN STAYS OPEN.</b><br>The queue repeats IV.25’s Fixed and Decide-by columns. Tick a box only when the prose or a ruling decides it.</div></div>')
    tr = ""
    for r in rows:
        item, fixed, und, by = r
        it = plain(item)
        anc = where.get(it)
        if not anc:
            raise SystemExit(f"IV.25 item without a working page: {it}")
        fx = inline(fixed) if fixed.strip() not in ("—", "") else '<span class="pv">—</span>'
        blk = " blk" if any(it in b[3] for b in BLOCKERS) or anc == "W10-3" else ""
        tr += (f'<tr class="q{blk}"><td><span class="it">{inline(item)}</span>{"<br><span class=\'bk\'>BLOCKS THE DUEL</span>" if blk else ""}</td>'
               f'<td>{fx}</td><td><span class="pv">{inline(by)}</span></td><td>{ckbox("")}</td><td>{ckbox("")}</td><td><span class="chip" data-wref="{anc}"></span></td></tr>')
    emit(f'<table class="qt"{attrs(W, split="1")}><colgroup><col style="width:150px"><col><col style="width:128px"><col style="width:54px"><col style="width:54px"><col style="width:72px"></colgroup>'
         f'<thead><tr><th>ITEM</th><th>WHAT’S FIXED</th><th>DECIDE BY</th><th>SAFE TO DEFER</th><th>DECIDED</th><th>WORK ON</th></tr></thead><tbody>{tr}</tbody></table>')
    emit(f'<div class="sh cap"{attrs(W, keep_next="1")}>ADDED IN DRAFTING · NAME IT, DATE IT, GIVE IT A PAGE</div>')
    add = "".join(f'<tr class="add"><td class="w"></td><td class="w"></td><td class="w"></td><td>{ckbox("")}</td><td>{ckbox("")}</td><td class="w"></td></tr>' for _ in range(5))
    emit(f'<table class="qt"{attrs(W, split="1")}><colgroup><col style="width:150px"><col><col style="width:128px"><col style="width:54px"><col style="width:54px"><col style="width:72px"></colgroup>'
         f'<thead><tr><th>ITEM</th><th>WHAT’S FIXED</th><th>DECIDE BY</th><th>SAFE TO DEFER</th><th>DECIDED</th><th>WORK ON</th></tr></thead><tbody>{add}</tbody></table>')
    emit(f'<div class="sh endl"{attrs(W)}><span>RESOLVED ITEMS MOVE TO APPENDIX A WITH A LOG NO.</span><span class="chip" data-ref="Appendix A">Appendix A</span></div>')

    byitem = {plain(r[0]): r for r in rows}
    for anc, label, title, items, prompts in BLOCKERS:
        spread = None  # a blocker runs over as many pages of its own as its prompts need
        wopener(W, K + f" · BLOCKER{' · SPREAD' if spread else ''}", title, anchor=anc, crumb=f"FTE › IV.25 · BLOCKER · {label.upper()}", spread=spread)
        for it in items:
            r = byitem[it]
            emit(fixed_row(W, B("c", "CANON"), f"FIXED · {plain(r[0]).upper()}", inline(r[1]), f'UNDECIDED<br>{inline(r[2])}<br>DECIDE BY<br>{inline(r[3])}', keep=True))
        for k, (head, prompt, tied, n) in enumerate(prompts):
            if spread and k == 2:
                wopener(W, K + " · BLOCKER · SPREAD", title + " (continued)", crumb=f"FTE › IV.25 · BLOCKER · {label.upper()} · ← SPREAD", spread="right")
            emit(wq(W, B("o", "OPEN"), head, prompt, tied, min(n, 7) if spread else n, 3 if n >= 8 else 2))
    for anc, title, blocks in GROUPED:
        wopener(W, K, title, anchor=anc, crumb=f"FTE › IV.25 · {title.upper()}")
        for it, head, prompt, tied, n in blocks:
            r = byitem[it]
            fx = inline(r[1]) if r[1].strip() != "—" else "Nothing fixed."
            emit(fixed_row(W, B("c", "CANON") if "TCD" in r[1] else B("o", "OPEN"), f"{plain(r[0]).upper()} · FIXED", fx, f"DECIDE BY<br>{inline(r[3])}", keep=True))
            emit(wq(W, B("o", "OPEN"), head, prompt, tied, n, 2 if n >= 6 else 1))


# ---------------------------------------------------------------- continuity room (FTE concordance)
CONC_ROWS = [
    ("VII.1", ["II.16", "IV.21", "IV.11R"], "FTE row of the four-band table (II.16); plot state (IV.21); the dated succession history in the lineage record, lane C; the FTE bands tracker on the following page."),
    ("VII.2", ["IV.15", "IV.22", "IV.23"], "Caelum’s exchanges as cross-book transfers (IV.15); the knowledge ledger (IV.22); cross-book connections (IV.23)."),
    ("VII.5", ["II.4", "IV.22"], "The knowledge levels (II.4); FTE’s dated seed ledger (IV.22); the FTE knowledge tracker in this section."),
    ("VII.7", ["II.14", "IV.17"], "The Elders’ Prayer can/can’t frame (II.14); the FTE candidate checked against the rulings (IV.17)."),
    ("VII.8", ["II.13", "IV.7"], "The Shattered Veil and its descendant texts (II.13); Challenge Two and the Breathbound Law on the page (IV.7)."),
    ("VII.10", ["IV.14", "IV.12", "IV.11R"], "Remy’s death as Melena remembers it (IV.14); Katherine’s lineage: truth versus Crown, Sanctum and public records (IV.12 and the lineage record)."),
    ("VII.12", ["IV.25", "IV.25W", "IV.11R"], "Every open FTE item (IV.25) and its working pages; the lineage decisions (lineage record, lane D); the IV.10 your-pages carry their own open items."),
    ("Part VII", ["CR"], "This concordance stands in for Part VII in this volume."),
    ("III.3", ["IV.2", "II.2"], "What FTE needs from the Underside’s geography: Shadowmere on Remnia’s Zenithia side (IV.2 places table; II.2)."),
    ("III.13", ["IV.18", "IV.14"], "Tiran and Maven as FTE carries them (IV.18; IV.14)."),
    ("III.14", ["IV.14", "IV.15"], "Melena’s two years in Shadowmere as FTE inherits them (IV.14); Caelum’s report of Tiran and Maven (IV.15)."),
    ("III.15", ["IV.14"], "The Remy memory in FTE, and the ruled objective event it must stay compatible with (IV.14)."),
    ("III.16", ["II.14", "IV.17"], "Selah’s performance as the Prayer’s other, independent instance (II.14; IV.17)."),
    ("III.18", ["IV.14", "II.16"], "Melena’s state entering FTE and the two-year interval (IV.14; II.16)."),
    ("III.20", ["IV.11R", "IV.14"], "3SL open items that touch FTE: Melena’s eye colour (lineage record, LC-01); Remy-death specifics (IV.14)."),
    ("Part III", ["CR"], "Part III isn’t printed in this volume; this concordance names where FTE carries what it needs from 3SL."),
]


def continuity_room():
    C = "CR"
    meta(C, "CONTINUITY", "CONTINUITY › FTE CONCORDANCE", "CONTINUITY ROOM · FTE CONCORDANCE", folio="CR")
    opener(C, "VII·FTE", "CONCORDANCE · CONTINUITY ROOM · FTE SLICE", "Continuity Room: FTE Concordance",
           "Where this volume carries the FTE information behind each Continuity Room and 3SL pointer.", "CONTINUITY")
    emit(f'<p{attrs(C)}>The full Companion’s Continuity Room (Part VII) and the 3SL dossier (Part III) aren’t printed in this volume. '
         'Every page here that points into them resolves to this table. The middle column is the Production Master’s description of the full section; '
         'the right column names where the FTE information already sits in these pages.</p>')
    rows = ""
    for code, where, what in CONC_ROWS:
        content = PME.get(code, ("", "", ""))[2] if code.count(".") else ("Part VII — the Continuity Room." if code == "Part VII" else "Part III — the 3SL dossier.")
        title = section_title(code) if code.count(".") else ""
        chips = "".join(f'<span class="chip" data-ref="{w}">{DISP.get(w, w)}</span>' for w in where if w != "CR")
        rows += (f'<tr><td><span class="cd">{code}</span><br><span class="tm">{esc(title)}</span></td>'
                 f'<td>{inline(content, refs=False)}</td><td>{esc(what)}<div class="chips">{chips}</div></td></tr>')
    emit(f'<table class="tb cc"{attrs(C, split="1")}><colgroup><col style="width:150px"><col><col style="width:236px"></colgroup>'
         f'<thead><tr><th>FULL COMPANION SECTION</th><th>WHAT IT HOLDS (PRODUCTION MASTER)</th><th>FTE INFORMATION IN THIS VOLUME</th></tr></thead><tbody>{rows}</tbody></table>')

    band_rows = [r for r in II16_ROWS if r[0] in ("FTE", "ADST")]
    emit(f'<div class="sh cap" data-sec="{C}" data-newpage-soft="1" data-keep-next="1">VII.1 · FTE BANDS · Record: Tandem Master Synchronization Timeline <span class="chip" data-ref="II.16">II.16</span></div>')
    emit(f'<p{attrs(C, keep_next="1")}>FTE and ADST rows reproduced from II.16 (the two books run concurrently). The working columns take dates and anchors as drafting fixes them.</p>')
    tr = ""
    for r in band_rows:
        for band, val in zip(["Background activation", "Narrative opening", "Climax", "Resolution"], r[1:5]):
            tr += f'<tr><td>{inline(r[0])}</td><td>{band}</td><td>{inline(val)}</td><td>{rlines(2)}</td></tr>'
    emit(f'<table class="tb fc"{attrs(C, split="1")}><colgroup><col style="width:80px"><col style="width:124px"><col><col style="width:190px"></colgroup>'
         f'<thead><tr><th>BOOK</th><th>BAND</th><th>AS RULED / OPEN (II.16)</th><th>WORKING DATE · ANCHOR · CH.</th></tr></thead><tbody>{tr}</tbody></table>')

    emit(f'<div class="sh cap" data-sec="{C}" data-keep-next="1">VII.5 · FTE KNOWLEDGE SEED · Record: Knowledge of the Other Lands Matrix <span class="chip" data-ref="IV.22">IV.22</span></div>')
    emit(f'<p{attrs(C, keep_next="1")}>FTE rows reproduced from IV.22. Every row is dated to where it’s shown; blank rows extend the matrix as drafting adds knowledge.</p>')
    tr = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in IV22_ROWS)
    tr += "".join('<tr class="blank">' + "".join(f'<td>{rlines(2)}</td>' for _ in range(5)) + "</tr>" for _ in range(6))
    emit(f'<table class="tb fc"{attrs(C, split="1")}><thead><tr><th>WHO</th><th>WHEN</th><th>KNOWS OR BELIEVES</th><th>LANE</th><th>STATUS</th></tr></thead><tbody>{tr}</tbody></table>')


def table_rows_after(code, caption_start):
    blocks = parse_blocks(SEC_BY_CODE[code]["lines"])
    for k, (t, v) in enumerate(blocks):
        if t == "table" and (caption_start is None or (k > 0 and blocks[k - 1][0] in ("sub", "p") and caption_start in blocks[k - 1][1])):
            return v[1:]
    raise SystemExit(f"table not found {code} {caption_start}")


II16_ROWS = table_rows_after("II.16", "Four bands per book")
IV22_ROWS = table_rows_after("IV.22", "Seed ledger")


# ---------------------------------------------------------------- appendices (FTE slices from the audit)
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


NEW_FILES = {  # audit inventory row prefix -> lineage source key
    "FTE 2025 FINAL": "F2025", "FTE Remnian Timeline Before Story Start": "BSS",
    "FTE Remnian Timeline Early": "TLE", "Full 4 Series Flesh Out": "F4",
}
VIA_CM = {"FTE Official Beta Reader Copy", "Chapter 29", "FTE 31-39", "The Challenges FTE Year", "49th Chess Tournament Placements",
          "FTE Elemental Factions", "Welcome to Remnia", "Character Bible"}


def inv_key(fname):
    return re.sub(r"\(\d+\)", "", re.sub(r"\.(docx|xlsx|xlsm|pdf)$", "", fname)).strip()


def appendices(volume_text):
    vt = volume_text.lower()
    # A — every TCD cited (volume + record + B/C slices)
    hc_ids = [h for h in HC if "FTE" in HC[h][2]] + cited(r"HC-\d{3}", volume_text)
    hc_ids = sorted(set(hc_ids), key=lambda x: int(x[3:]))
    inv_all = []
    for hdr in ("## Source Inventory — 3 Shadowmere Lane", "## Source Inventory — For Their Entertainment", "## Source Inventory — A Dream So Twisted",
                "## Source Inventory — The Sea Will Keep", "## Source Inventory — Shared Tandem"):
        inv_all += audit_table(hdr)[1:]
    # files the Part IV source note names only as absent from the Content Master's Project are not "used"
    vt = re.sub(r"Files the audit inventories but that aren.t in this Project:.*?not the file\.", " ", volume_text, flags=re.S).lower()
    used = []
    for r in inv_all:
        k = inv_key(plain(r[0]))
        hit = k in NEW_FILES or k.lower() in vt or k.replace("-", "–").lower() in vt or (k == "Chapter 29" and "chapter 29.docx" in vt) \
            or (k == "49th Chess Tournament Placements" and "placements" in vt)
        if hit:
            used.append(r)
    slice_text = volume_text + " ".join(" ".join(HC[h]) for h in hc_ids) + " ".join(" ".join(r) for r in used)
    tcd_ids = set(cited(r"TCD-\d{3}", slice_text)) | tcd_range_expand(slice_text)
    tcd_ids = sorted((t for t in tcd_ids if t in TCD), key=lambda x: int(x[4:]))

    A = "APP-A"
    meta(A, "SPINE", "APPENDIX A › CANON DECISION LOG · FTE SLICE", "APPENDIX A · CANON DECISION LOG · FTE SLICE", folio="A")
    opener(A, "A", "APPENDIX · STATUS &amp; PROVENANCE SHEET", "Canon Decision Log: FTE Slice",
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
    nt = list(NO_TCD_RULINGS)
    if re.search(r"nine[- ]tier|tiers?\b", volume_text, re.I) and "III.3" in volume_text:
        nt.append(("2026-10-09", "Underside tier status", "CANON — TCD-025 / TCD-026: the Underside is vertically tiered and attached to Zenithia’s side of Remnia; Crownlight and Dawnveil are surface/above-ground tiers; the nation is fully underground by Ironcross. DRAFTED — 3SL ch. 10: nine tiers. SUPPORTED — 3SL Full Worldbuilding. The nine-tier count is not ruled canon.", "Cited via the concordance (III.3)"))
    tr = "".join(f'<tr><td><span class="pv">{d}</span></td><td><b>{esc(t)}</b></td><td>{esc(r)}</td><td><span class="pv">APPLIED IN</span> {a}</td></tr>' for d, t, r, a in nt)
    emit(f'<table class="tb ap"{attrs(A, split="1")}><colgroup><col style="width:86px"><col style="width:132px"><col><col style="width:200px"></colgroup>'
         f'<thead><tr><th>DATE</th><th>TOPIC</th><th>AUTHOR RULING</th><th>WHERE</th></tr></thead><tbody>{tr}</tbody></table>')
    emit(f'<div class="sh cap"{attrs(A, keep_next="1")}>Logged in drafting · resolved IV.25 and lineage items · asking a question assigns no TCD number</div>')
    tr = "".join('<tr class="blank">' + "".join(f'<td>{rlines(2)}</td>' for _ in range(4)) + "</tr>" for _ in range(10))
    emit(f'<table class="tb ap"{attrs(A, split="1")}><colgroup><col style="width:86px"><col style="width:132px"><col><col style="width:200px"></colgroup>'
         f'<thead><tr><th>LOG NO.</th><th>ITEM</th><th>DECISION AS MADE IN PROSE OR RULED</th><th>DATE · CH. · PAGES TO UPDATE</th></tr></thead><tbody>{tr}</tbody></table>')

    B_ = "APP-B"
    meta(B_, "SPINE", "APPENDIX B › HIGH-IMPACT CONFLICT REGISTER · FTE SLICE", "APPENDIX B · CONFLICT REGISTER · FTE SLICE", folio="B")
    opener(B_, "B", "APPENDIX · STATUS &amp; PROVENANCE SHEET", "High-Impact Conflict Register: FTE Slice",
           "Every FTE conflict in the audit’s register, plus the lineage conflicts the reconstruction found.", "SPINE")
    emit(f'<p{attrs(B_)}>Rows reproduced from the audit’s High-Impact Conflict Register: every entry whose books include FTE, and every entry cited elsewhere in this volume ({len(hc_ids)} rows).</p>')
    tr = "".join(f'<tr><td><span class="cd">{r[0]}</span></td><td><b>{inline(r[1], refs=False)}</b><br><span class="pv">{inline(r[2], refs=False)}</span></td><td>{inline(r[3], refs=False)}</td><td>{inline(r[4], refs=False)}</td></tr>' for r in (HC[h] for h in hc_ids))
    emit(f'<table class="tb ap"{attrs(B_, split="1")}><colgroup><col style="width:72px"><col style="width:150px"><col><col style="width:170px"></colgroup>'
         f'<thead><tr><th>ID</th><th>TOPIC · BOOKS</th><th>CONFLICT</th><th>PRIORITY / STATUS</th></tr></thead><tbody>{tr}</tbody></table>')
    emit(f'<div class="sh cap"{attrs(B_, keep_next="1")}>Lineage conflicts found in the reconstruction (2026-10-09) <span class="chip" data-wref="LR-D"></span></div>')
    emit(f'<p{attrs(B_)}>Not yet in the audit. Each is worked in full in the lineage record, lane D, with both sources quoted.</p>')
    tr = "".join(f'<tr><td><span class="cd">{c[0]}</span></td><td><b>{esc(c[1])}</b></td><td>{esc(c[4])}</td><td>{badge(c[5], ST_WORD[c[5]])}<br><span class="pv">{esc(c[6])}</span></td></tr>' for c in LIN.CONFLICTS)
    emit(f'<table class="tb ap"{attrs(B_, split="1")}><colgroup><col style="width:72px"><col style="width:150px"><col><col style="width:170px"></colgroup>'
         f'<thead><tr><th>ID</th><th>CLAIM</th><th>HIGHER-AUTHORITY EVIDENCE</th><th>STATUS</th></tr></thead><tbody>{tr}</tbody></table>')

    C_ = "APP-C"
    meta(C_, "SPINE", "APPENDIX C › SOURCE AUTHORITY INVENTORY · FTE SLICE", "APPENDIX C · SOURCE INVENTORY · FTE SLICE", folio="C")
    opener(C_, "C", "APPENDIX · STATUS &amp; PROVENANCE SHEET", "Source Authority Inventory: FTE Slice",
           "Every source this volume uses, with how this build could reach it.", "SPINE")
    emit(f'<p{attrs(C_)}>Rows reproduced from the audit’s Source Inventory for every file this volume cites ({len(used)} rows). The right column says how Build 2 reached each file. '
         'Files marked “through the Content Master” weren’t available to this build: their facts are taken as the Content Master records them. '
         'The four files supplied on 2026-10-09 carry their treatment in the lineage record. The reconstructed lineage itself is a derived record, not a source, and isn’t listed.</p>')
    tr = ""
    for r in used:
        k = inv_key(plain(r[0]))
        if k in NEW_FILES:
            how = f'<b>Supplied 2026-10-09.</b> {esc(LIN.SOURCES[NEW_FILES[k]][2])}'
        elif any(k.startswith(v) for v in VIA_CM):
            how = "Through the Content Master"
        else:
            how = "Cited by the Content Master; not consulted in this build"
        tr += (f'<tr><td><b>{inline(r[0], refs=False)}</b><br><span class="pv">{inline(r[1], refs=False)} · {inline(r[2], refs=False)}</span></td>'
               f'<td>{inline(r[3], refs=False)}<br><span class="pv">DOMAINS</span> {inline(r[4], refs=False)}</td><td>{inline(r[5], refs=False)}</td>'
               f'<td>{inline(r[6], refs=False)}<br><span class="pv">BUILD 2</span> {how}</td></tr>')
    tr += ('<tr><td><b>The Imperial Lineage</b><br><span class="pv">FTE/Shared · genealogy as news bulletins</span></td><td>Not in the audit’s inventory.</td><td>UNAUDITED</td>'
           '<td>Comparison only; nothing imported. Every claim the Content Master quotes from it is in the Remnian Timeline Before Story Start.<br><span class="pv">BUILD 2</span> Not available; quoted by the Content Master</td></tr>')
    emit(f'<table class="tb ap"{attrs(C_, split="1")}><colgroup><col style="width:150px"><col style="width:170px"><col style="width:100px"><col></colgroup>'
         f'<thead><tr><th>FILE · BOOK · TYPE</th><th>GENERATION · DOMAINS</th><th>STATUS</th><th>KNOWN CONFLICT · BUILD 2 ACCESS</th></tr></thead><tbody>{tr}</tbody></table>')

    E_ = "APP-E"
    meta(E_, "SPINE", "APPENDIX E › TERMINOLOGY REGISTER · FTE SLICE", "APPENDIX E · TERMINOLOGY REGISTER · FTE SLICE", folio="E")
    opener(E_, "E", "APPENDIX · TERMINOLOGY REGISTER", "Terminology Register: FTE Slice",
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
    return tcd_ids, hc_ids, keep, used


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
            note="This volume prints the Part II sections FTE stands on. II.1, II.3, and II.7–II.12 are in the full Tandem Companion.")
    for c in PART_II_SCOPE:
        content_section(c); order.append(c)
    iv_codes = []
    for s in SECS:
        if s["part"] == "IV":
            iv_codes.append(s["code"])
            if s["code"] == "IV.10":
                iv_codes.append("IV.10W")
            if s["code"] == "IV.11":
                iv_codes.append("IV.11R")
            if s["code"] == "IV.25":
                iv_codes.append("IV.25W")
    divider("IV", iv_codes + ["CR"], PARTS["IV"]["lines"])
    for s in SECS:
        if s["part"] == "IV":
            content_section(s["code"]); order.append(s["code"])
            if s["code"] == "IV.10":
                iv10_working()
            elif s["code"] == "IV.11":
                lineage_record()
            elif s["code"] == "IV.25":
                iv25_working()
    continuity_room()
    printed = "\n".join(t for _, t in QA_SOURCE_TEXT) + "\n".join(o for o in OUTPUT if 'data-sec="TITLE"' not in o and 'data-sec="ABOUT"' not in o)
    tcd_ids, hc_ids, terms, used = appendices(re.sub(r"<[^>]+>", " ", printed))

    titles = {c: ref_title(c) for c in set(re.findall(r"(?:VII|VI|IV|V|III|II|I)\.\d+", PM + CM))}
    titles.update({k: CM_TITLES[k] for k in ("IV.10W", "IV.11R", "IV.25W", "CR")})
    titles.update({"Appendix A": "Canon Decision Log", "Appendix B": "High-Impact Conflict Register", "Appendix C": "Source Authority Inventory",
                   "Appendix D": "Full 4 Series Flesh Out Claim-Level Survival Pass", "Appendix E": "Terminology Register",
                   "Part III": "3 Shadowmere Lane / The Underside", "Part VII": "The Continuity Room", "Part V": "A Dream So Twisted / Somnoria", "Part VI": "The Sea Will Keep"})
    in_volume = {s["code"] for s in SECS if in_scope(s["code"])} | {"IV.10W", "IV.11R", "IV.25W", "CR", "Appendix A", "Appendix B", "Appendix C", "Appendix E", "Part I", "Part II", "Part IV"}
    anchor = {c: c for c in in_volume}
    anchor.update({"Appendix A": "APP-A", "Appendix B": "APP-B", "Appendix C": "APP-C", "Appendix E": "APP-E",
                   "Part I": "PART-I", "Part II": "PART-II", "Part IV": "PART-IV"})
    for c in CONCORDANCE:
        anchor[c] = "CR"
    toc = [("FRONT", None, [("ABOUT", "About This Volume")]),
           ("PART I", "PART-I", [(c, CM_TITLES[c]) for c in order if c.startswith("I.")]),
           ("PART II", "PART-II", [(c, CM_TITLES[c]) for c in PART_II_SCOPE]),
           ("PART IV", "PART-IV", [(c, CM_TITLES[c]) for c in iv_codes]),
           ("CONTINUITY ROOM · FTE", None, [("CR", "Continuity Room: FTE Concordance")]),
           ("APPENDICES · FTE SLICES", None, [("APP-A", "A · Canon Decision Log"), ("APP-B", "B · High-Impact Conflict Register"),
                                               ("APP-C", "C · Source Authority Inventory"), ("APP-E", "E · Terminology Register")])]
    data = {"secmeta": SECMETA, "titles": titles, "anchor": anchor, "toc": toc, "concordance": CONCORDANCE, "disp": DISP,
            "counts": {"tcd": len(tcd_ids), "hc": len(hc_ids), "terms": len(terms), "sources": len(used)}, "tcd_ids": tcd_ids, "hc_ids": hc_ids}
    page = (ROOT / "tools" / "shell.html").read_text()
    page = page.replace("<!--BLOCKS-->", "\n".join(OUTPUT)).replace("/*DATA*/null", json.dumps(data, ensure_ascii=False))
    (OUT / "book.html").write_text(page)
    (OUT / "source_text.json").write_text(json.dumps(QA_SOURCE_TEXT, ensure_ascii=False))
    (OUT / "genealogy_ids.json").write_text(json.dumps(GENEALOGY_IDS, ensure_ascii=False))
    (OUT / "apparatus.json").write_text(json.dumps({"sources_used": [plain(r[0]) for r in used], "tcd_ids": tcd_ids, "hc_ids": hc_ids,
                                                     "terms": [plain(r[0]) for r in terms]}, ensure_ascii=False, indent=1))
    print(f"blocks: {len(OUTPUT)}  sections: {len(SECMETA)}  TCD cited: {len(tcd_ids)}  HC: {len(hc_ids)}  terms: {len(terms)}  sources: {len(used)}")


if __name__ == "__main__":
    main()
