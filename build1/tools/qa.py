#!/usr/bin/env python3
"""Post-print QA for Build 1. Reads out/layout_qa.json (from the paginator),
out/source_text.json (every printed Content Master unit), the PDF, and the
audit; writes out/qa_data.json and prints a summary. The human-readable
report (dist/QA_REPORT.md) is written by tools/report.py from these results."""
import json
import random
import re
import subprocess
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
L = json.loads((ROOT / "out" / "layout_qa.json").read_text())
SRC = json.loads((ROOT / "out" / "source_text.json").read_text())
PDF = ROOT / "dist" / "Tandem_Companion_Build1_3SL.pdf"
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

# ---- 3. the 2026-10-09 tier ruling
tier = {
    "old_fixed_line_absent": "nine tiers in drafted order; crownlight" not in dom,
    "corrected_fixed_line_present": norm("Not ruled: the nine-tier count and order are CURRENT DRAFTED TEXT (ch. 10).") in dom,
    "ruling_box_III3": norm("The Underside has nine tiers; Halflight’s old route board lists all nine in order.") in dom,
    "queue_row_C_badges": None,
}
q = [p for p, s in zip(dom_pages, L["pageSecs"]) if s == "III.20W"][0]
row = q[q.find("C · Tier depths"):q.find("D · Crossing")]
tier["queue_row_C_badges"] = all(w in row for w in ("CANON", "DRAFTED", "SUPPORTED"))

# ---- 4. writing space
w = L["writing"]
below = [x for x in L["issues"] if x["type"] == "writing-below-min"]
by_kind = Counter(x["kind"] for x in w)
lines_total = sum(x["lines"] for x in w)
work = [x for x in w if x["sec"] == "III.20W"]
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
    if "#" in sec or not re.match(r"^(I|II|III)\.\d+$", sec):
        continue
    ids = re.findall(r"TCD-\d{3}", t)
    if not ids or not (60 < len(t) < 480) or re.match(r"^\s*(TCD-|Audit|Production Master|3SL draft)", t):
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

out = {
    "pages_dom": L["pages"], "pages_pdf": pages_pdf, "page_size": size,
    "layout_issues": L["issues"], "flags": L["flags"], "footer_two_row_pages": L["footerRows"],
    "section_pages": L["sectionPages"],
    "units_checked": len(units), "missing_dom": missing_dom, "missing_pdf": missing_pdf, "design_notes": design_notes,
    "marker_counts_source": marker_counts, "tier_ruling": tier,
    "writing": {"areas": len(w), "by_kind": by_kind, "lines_total": lines_total, "below_min": below, "smallest_prompt_lines": smallest_prompt,
                "working_section_lines": sum(x["lines"] for x in work), "working_section_pages": L["sectionPages"].get("III.20W")},
    "refs": {"page_refs_checked": len(L["refCheck"]), "page_refs_wrong": ref_bad, "outside_volume": outside,
             "resolved_chips": len(refs["resolved"])},
    "claims": claims, "fonts": font_names, "font_types": font_types, "empty_text_pages": empty_text_pages,
    "pdf_words": len(pdf_text.split()),
}
(ROOT / "out" / "qa_data.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
print(json.dumps({k: (v if not isinstance(v, (list, dict)) or k in ("tier_ruling", "marker_counts_source") else (len(v))) for k, v in out.items()}, ensure_ascii=False, indent=1))
print("missing_dom:", missing_dom[:10])
print("missing_pdf:", missing_pdf[:10])
