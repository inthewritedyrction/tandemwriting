#!/usr/bin/env python3
"""Post-print QA for Build 2 (FTE). Reads out/layout_qa.json (from the paginator),
out/source_text.json (every printed Content Master unit), the PDF, and the
audit; writes out/qa_data.json and prints a summary. The human-readable
report (dist/QA_REPORT.md) is written by tools/report.py from these results."""
import json
import random
import re
import subprocess
import sys
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
L = json.loads((ROOT / "out" / "layout_qa.json").read_text())
SRC = json.loads((ROOT / "out" / "source_text.json").read_text())
PDF = ROOT / "dist" / "Tandem_Companion_Build2_FTE.pdf"
CORR = json.loads((ROOT / "src" / "corrections.json").read_text())
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tools")]
import lineage as LIN  # noqa: E402
import lineage_qa  # noqa: E402
AUDIT = (ROOT / "src" / "audit.md").read_text()


def norm(s):
    s = unicodedata.normalize("NFKC", s).lower().replace("†", "")
    return re.sub(r"\s+", "", s)


dom_pages = L["bookText"]
dom = norm("".join(dom_pages))
pdf_text = subprocess.run(["pdftotext", "-raw", str(PDF), "-"], capture_output=True, text=True).stdout
pdf_pages = pdf_text.split("\f")
pdf = norm(pdf_text)

# ---- 1. content integrity: every printed Content Master unit is in the book (DOM) and in the PDF text layer
units = [(sec, t) for sec, t in SRC if t.strip() and not sec.endswith("#designnote")]
missing_dom, missing_pdf = [], []
for sec, t in units:
    n = norm(t)
    if sec.endswith("#label"):
        n = norm((t.split("—")[-1] if "—" in t else t).rstrip(":").rstrip("."))
    if n and n not in dom:
        missing_dom.append((sec, t))
    if n and n not in pdf:
        missing_pdf.append((sec, t))
design_notes = [(sec, t) for sec, t in SRC if sec.endswith("#designnote")]

# ---- 2. status markers: every marker in the printed source copy is rendered as a badge
src_sel = "\n".join(t for s, t in SRC if not s.endswith("#ref"))
marker_counts = {w: len(re.findall(r"\b" + re.escape(w) + r"\b", src_sel)) for w in
                 ["CANON", "CURRENT DRAFTED TEXT", "SUPPORTED", "POSSIBLE", "OPEN", "CONFLICT", "RESEARCH", "LEGACY"]}

# ---- 3. logged corrections and the instructed page fixes
def strip_md(t):
    t = t.replace("\\[", "[").replace("\\]", "]")
    t = re.sub(r"\[(C|X|\?|P)\]", lambda m: {"C": "CANON", "X": "CONFLICT", "?": "OPEN", "P": "POSSIBLE"}[m.group(1)], t)
    return re.sub(r"[*|]", "", re.sub(r"^>\s*", "", t))
corrections = []
for c in CORR["corrections"]:
    rep_n = norm(strip_md(c["replace"]))
    find_n = norm(strip_md(c["find"]))
    corrections.append({"id": c["id"], "section": c["section"], "replacement_printed": rep_n in dom, "old_text_absent": (find_n not in dom) if find_n not in rep_n else None})
fixes = {
    "failure_beat_prompt": norm("Where in the Challenge Six climax does the Frost configuration fail? Name the chapter and what the scene is fighting over when it happens.") in dom,
    "old_rewrite_prompt_absent": norm("Where in the chs. 30–39 rewrite") not in dom,
    "five_layers_prompt": norm("Check the five layers in IV.11 (Biological, Legal, Recorded, Public, Succession)") in dom,
    "four_lanes_absent": norm("four lanes") not in dom,
    "no_stage3_placeholders": "[stage3" not in dom and "sourcepending" not in dom,
    "zephyr_registration_conflict": norm("Flamer (Placements) vs a Frost emblem older than the Flamer marks") in dom,
    "iv2_seventeen_not_on_tcds": norm("Remnia is a centralized empire of seventeen provinces") not in dom,
}
# ---- 4. writing space
w = L["writing"]
below = [x for x in L["issues"] if x["type"] == "writing-below-min"]
by_kind = Counter(x["kind"] for x in w)
lines_total = sum(x["lines"] for x in w)
work = [x for x in w if x["sec"] in ("IV.10W", "IV.11R", "IV.25W")]
smallest_prompt = min((x["lines"] for x in w if x["kind"] in ("wb", "wr") and x["min"] >= 5), default=None)

# ---- 5. references
refs = L["refs"]
outside = Counter(refs["outside"])
ref_bad = [r for r in L["refCheck"] if not r["ok"]]

# ---- 6. random claim check (seeded): sentences that cite a TCD, drawn from Parts I–III pages
SEED = 20261009
TCD = {}
for ln in AUDIT.split("\n"):
    m = re.match(r"^\| (TCD-\d{3}) \| ([^|]*)\| ([^|]*)\| ([^|]*)\| ([^|]*)\|", ln)
    if m:
        TCD[m.group(1)] = (m.group(2).strip(), m.group(5).strip())
page_norm = [norm(t) for t in dom_pages]
cands = []
for sec, t in units:
    if "#" in sec or not re.match(r"^(I|II|IV)\.\d+$", sec):
        continue
    ids = re.findall(r"TCD-\d{3}", t)
    if not ids or not (60 < len(t) < 480) or re.match(r"^\s*(TCD-|Audit|Production Master|3SL draft|FTE Beta)", t):
        continue
    n = norm(t)
    pg = next((k + 1 for k, pn in enumerate(page_norm) if n in pn), None)
    cands.append((pg, sec, t.strip(), sorted(set(ids))))
random.seed(SEED)
sample = random.sample(cands, 15)
claims = [{"page": n, "section": sec, "claim": c, "rulings": [{"id": i, "topic": TCD.get(i, ("?", ""))[0], "ruling": TCD.get(i, ("", "?"))[1]} for i in ids]} for n, sec, c, ids in sample]

# ---- 7. PDF facts
info = subprocess.run(["pdfinfo", str(PDF)], capture_output=True, text=True).stdout
fonts = subprocess.run(["pdffonts", str(PDF)], capture_output=True, text=True).stdout
font_names = sorted({re.sub(r"^[A-Z]+\+", "", l.split()[0]) for l in fonts.split("\n")[2:] if l.strip()})
font_types = sorted({" ".join(l.split()[1:3]) for l in fonts.split("\n")[2:] if l.strip()})
pages_pdf = int(re.search(r"Pages:\s+(\d+)", info).group(1))
size = re.search(r"Page size:\s+([^\n]+)", info).group(1)
empty_text_pages = [i + 1 for i, t in enumerate(pdf_pages[:pages_pdf]) if len(t.strip()) < 20]

# ---- 8. lineage: data checks, graphic vs record, every record claim printed
gid = json.loads((ROOT / "out" / "genealogy_ids.json").read_text())
lq = lineage_qa.run(gid)
rec_text = norm("".join(t for t, sec in zip(dom_pages, L["pageSecs"]) if sec == "IV.11R"))
rec_missing = []
for p in LIN.P:
    for c in p["claims"]:
        if norm(c[2]) not in rec_text:
            rec_missing.append((p["name"], c[2]))
for c in LIN.CONFLICTS:
    for part in (c[1], c[2], c[3], c[4], c[7]):
        if norm(part) not in rec_text:
            rec_missing.append((c[0], part[:60]))
node_missing = []
for pid, ids in gid.items():
    for x in ids:
        if norm(x[3:]) not in rec_text:
            node_missing.append((pid, x))
lineage = {"data_checks": {k: v for k, v in lq.items()}, "record_claims_missing": rec_missing, "node_ids_missing": node_missing}

out = {
    "pages_dom": L["pages"], "pages_pdf": pages_pdf, "page_size": size,
    "layout_issues": L["issues"], "flags": L["flags"], "footer_two_row_pages": L["footerRows"],
    "section_pages": L["sectionPages"],
    "units_checked": len(units), "missing_dom": missing_dom, "missing_pdf": missing_pdf, "design_notes": design_notes,
    "marker_counts_source": marker_counts, "corrections": corrections, "fixes": fixes, "lineage": lineage,
    "writing": {"areas": len(w), "by_kind": by_kind, "lines_total": lines_total, "below_min": below, "smallest_prompt_lines": smallest_prompt,
                "working_section_lines": sum(x["lines"] for x in work), "working_section_pages": {k: L["sectionPages"].get(k) for k in ("IV.10W", "IV.11R", "IV.25W")}},
    "refs": {"page_refs_checked": len(L["refCheck"]), "page_refs_wrong": ref_bad, "outside_volume": outside,
             "resolved_chips": len(refs["resolved"])},
    "claims": claims, "fonts": font_names, "font_types": font_types, "empty_text_pages": empty_text_pages,
    "pdf_words": len(pdf_text.split()),
}
(ROOT / "out" / "qa_data.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps({k: (v if not isinstance(v, (list, dict)) or k in ("fixes", "marker_counts_source") else (len(v))) for k, v in out.items()}, ensure_ascii=False, indent=1))
print("missing_dom:", missing_dom[:10])
print("missing_pdf:", missing_pdf[:10])
print("corrections not clean:", [c for c in corrections if not (c["replacement_printed"] and c["old_text_absent"] is not False)])
print("lineage:", {k: (len(v) if isinstance(v, list) else v) for k, v in lq.items()}, "record missing:", rec_missing[:5], "node ids missing:", node_missing)
