#!/usr/bin/env python3
"""Writes dist/LINEAGE_RECONSTRUCTION_REPORT.md from src/lineage.py and out/lineage_qa.json.
The narrative sections are fixed text; every table is generated from the record so the
report can't drift from the printed volume."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tools")]
import lineage as L  # noqa: E402
import lineage_qa  # noqa: E402

ST = {"c": "CANON", "d": "CURRENT DRAFTED TEXT", "s": "SUPPORTED", "p": "POSSIBLE", "o": "OPEN", "x": "CONFLICT", "l": "LEGACY / SUPERSEDED"}


def lab(srcs):
    return ", ".join(L.SOURCES[s][0] if s in L.SOURCES else s for s in srcs)


def cell(t):
    return str(t).replace("|", "\\|").replace("\n", " ")


out = []
w = out.append
w("# Remnian Lineage Reconstruction Report")
w("")
w("**Build 2 · For Their Entertainment / Remnia** · rebuilt 2026-10-09 · record: `build2/src/lineage.py` · printed as the IV.11 record in `Tandem_Companion_Build2_FTE.pdf`")
w("")
w("The Remnian imperial and royal lineage was rebuilt from the evidence, claim by claim. The existing *Imperial Lineage* file wasn't imported; it was used only for comparison (section 4). "
  "The result is a **derived working record, not a source**. It settles nothing a ruling leaves open, and no agreement between two weak sources was promoted to CANON.")
w("")
w("## 1. What the reconstruction could and couldn’t read")
w("")
w("| Label | File | Authority treatment | How this build reached it |")
w("| --- | --- | --- | --- |")
for k, v in L.SOURCES.items():
    w(f"| {v[0]} | {cell(v[1])} | {cell(v[2])} | {cell(v[3])} |")
w("")
w("Limits to know about:")
w("")
w("- **The Beta isn’t in this session.** Every Beta fact in the record (CURRENT DRAFTED TEXT) is taken as the Content Master records it, with its chapter. The same holds for *Welcome to Remnia*, the *Character Bible*, *FTE 31–39*, 3SL, and the *49th Placements*.")
w("- **FTE 2025 FINAL contains the passages the Content Master cites as *FTE 31–39*** (Dalia “one of three people who knew,” the Heart’s Mirror scene with Tobias, Lucia’s car accident). Where a claim appears in both, it keeps the Content Master’s *31–39* status (SUPPORTED). FTE 2025 FINAL never establishes a claim on its own.")
w("- **The uploaded Timeline Early ends in 2066 ER.** The audit’s note that this file’s generation makes Lucia Katherine’s mother or Ethan her father couldn’t be checked against the text. The note stands, and TCD-040 supersedes both.")
w("- **FTE 2025 FINAL and Full 4 Series Flesh Out were searched for every lineage passage**, by name, title, house and succession terms, rather than read end to end. Both Remnian timelines were read in full.")
w("")
w("## 2. Which sources established each branch")
w("")
branches = [
    ("Locked anchor (all branches)", "TCD-040: Tobias is the father of Katherine (with Michelle) and of Melena (with Lucia); paternal half-sisters. TCD-059 owns the concealment layers. TCD-032 makes Elias Crown Prince after Lucia’s death. Nothing else in the record is CANON unless a ruling says so."),
    ("Hastings line: Eden → Aracelia → Lucia", "WTR gives the matrilineal line. TLE supplies Eden’s children (Richard, Madeleine, Victoria, the twins Aracelia and Alexandria), Aracelia’s 2038 birth, and her husband Jackson Harper. BSS agrees on Aracelia’s age (57 in 2095), calls the Lockwood children her grandchildren, and has Richard as their great-uncle. Eden → Aracelia and Aracelia → Lucia are therefore SUPPORTED. Eden’s other children and Jackson Harper are TLE only (LEGACY). The generation count, Eden’s reign and Lucia’s birth year are in conflict (LC-03, LC-04, LC-05)."),
    ("Aracelia herself", "Empress at FTE: Beta (DRAFTED). Styled name: Beta “Aracelia Meson Mignonette,” BSS adds Hastings, 31–39 has Lockwood (LC-02). Frost: TLE only (LEGACY)."),
    ("Alexandria’s branch", "TLE and BSS agree: Duchess of Alleia, husband Lord Clyde Hastings (d. 2096 in BSS), daughters Amalia (2062) and Evangeline (2063). SUPPORTED."),
    ("Lucia", "Mother of Melena: TCD-040. Crown Princess: BSS, CB, WTR (SUPPORTED). Frost: Beta ch. 8 (DRAFTED; the 31–39 Flamer line is a revision flag). Dead before FTE: Beta. Birth year, cause of death and her Duchy of Zenithia are in conflict (LC-03, LC-16, LC-20). Her role in Katherine’s erasure: TCD-059 (CANON); the mechanisms BSS drafts (treason decree, legal action, the ban on London Town) stay SUPPORTED."),
    ("House Lockwood: Alistair, Rowena, Tobias", "Tobias’s parents (Duke Alistair, Duchess Rowena): BSS only (SUPPORTED). Tobias’s 2035 birth at Lockwood Manor, Highcrest: TLE only (LEGACY), and it collides with BSS’s parents’ ages (LC-14). Prince Consort: CB and BSS. Death six months after Lucia: 31–39 (SUPPORTED); BSS never places him after 2081 (LC-17). His element: the Beta implies Fire (Melena “took after their father”); the 31–39 Mirror line (Frost) needs revising (LC-21)."),
    ("Lucia and Tobias’s children", "Melena’s parents: TCD-040. Elias, Cordelia and Louis as Lucia and Tobias’s children: BSS (SUPPORTED), consistent with the Beta’s family. Positions: Elias first (TCD-032), Melena second (Beta), Cordelia third and Louis fourth (BSS). Birth dates are BSS (2073, 2076, 2079, 2081). Melena’s year conflicts with CB’s 2077 (LC-15). Her eyes are the long-standing conflict (LC-01)."),
    ("Michelle and Katherine", "Parentage: TCD-040. Katherine’s full name: Beta, and BSS agrees. Birth year 2076: CB and BSS (SUPPORTED). Both sources put her birth before Melena’s (O-01); that isn’t ruled and has no succession effect by itself. Legal status, public knowledge and succession: OPEN (TCD-040, TCD-059). Ethan: biological father superseded (TCD-040); a naming or social role is POSSIBLE; his surname is in conflict (LC-18)."),
    ("London Town: Kinross and Augustine", "Dalia’s father Edward: TLE and BSS (SUPPORTED); TLE also names a King Brenton (LC-12). Dalia’s 2038 birth: TLE and BSS. Nathaniel king from 2058 (TLE) until his 2090 abdication to Dalia (BSS). Queen Dalia at FTE: BSS and 31–39 (SUPPORTED), against CB’s Crown Princess and WTR’s King William (LC-11). The four Augustine brothers: Beta. Their parentage and birth dates, the twins Zephyr and Zoe, and Orion: BSS. Minho’s and Sebastian’s relinquishments: BSS, with CB and F2025 corroborating Minho. The order of succession is internally inconsistent in BSS (LC-19)."),
]
for b, t in branches:
    w(f"**{b}.** {t}")
    w("")
w("## 3. Remaining conflicts")
w("")
w("| ID | Claim | Source A | Source B | Higher-authority evidence | Current status | What would need to change |")
w("| --- | --- | --- | --- | --- | --- | --- |")
for c in L.CONFLICTS:
    w(f"| {c[0]} | {cell(c[1])} | {cell(c[2])} | {cell(c[3])} | {cell(c[4])} | {cell(c[6])} | {cell(c[7])} |")
w("")
w("**Open items that aren’t conflicts:**")
w("")
for o in L.OPEN_ITEMS:
    w(f"- **{o[0]} · {o[1]}** ({ST[o[3]]}; {lab(o[4])}). {o[2]}")
w("")
w("## 4. Comparison with the unaudited *Imperial Lineage*")
w("")
w("The file isn’t in this session; the comparison uses the Content Master’s quotations of it.")
w("")
w("| Claim the Content Master quotes from it | Found in an audited source? | Treatment |")
w("| --- | --- | --- |")
for a, b, c in L.COMPARE_IL:
    w(f"| {cell(a)} | {cell(b)} | {cell(c)} |")
w("")
w("Every quoted claim appears in BSS, which the audit inventories (Supporting / needs ruling, claim by claim). The record and the corrected Part IV copy cite BSS and mention the *Imperial Lineage* only as repeating it. Its audit status is still open (IV.25).")
w("")
w("## 5. Old claims rejected or downgraded")
w("")
w("| ID | Claim | Source | Why | Now |")
w("| --- | --- | --- | --- | --- |")
for r in L.REJECTED:
    w(f"| {r[0]} | {cell(r[1])} | {cell(r[2])} | {cell(r[3])} | {cell(r[4])} |")
w("")
w("## 6. Duplicate-person and name-variant checks")
w("")
w("| Check | Names | Treatment |")
w("| --- | --- | --- |")
for n in L.NAME_CHECKS:
    w(f"| {n[0]} · {cell(n[1])} | {cell(n[2])} | {cell(n[3])} |")
w("")
w("## 7. Content Master corrections this reconstruction caused")
w("")
corr = json.loads((ROOT / "src" / "corrections.json").read_text())["corrections"]
w("| ID | Section | What changed |")
w("| --- | --- | --- |")
for c in corr:
    if c["id"].startswith(("S-", "P-")):
        w(f"| {c['id']} | {c['section']} | {cell(c['ruling'])} |")
w("")
w("The exact replaced and replacing text for each entry is in `build2/src/corrections.json`.")
w("")
w("## 8. Lineage QA")
w("")
r = lineage_qa.run(json.loads((ROOT / "out" / "genealogy_ids.json").read_text()))
c = r["counts"]
w(f"The record holds {c['persons']} people, {c['claims']} claims, {c['edges']} parent links, {c['conflicts']} conflicts, {c['open_items']} open items, {c['name_checks']} name checks and {c['rejected']} rejected or downgraded claims, plus {len(L.COLLATERAL)} collateral rows.")
w("")
w("| Check | Result |")
w("| --- | --- |")
names = {"parent_child": "Parent/child consistency (edge list vs every Parents and Children claim, both directions)",
         "duplicates": "Duplicate person and shared name variant",
         "succession_vs_biology": "No succession position resting on parentage alone",
         "provenance": "Every claim traced to a known source and a valid status",
         "promotion": "No legacy or supporting claim promoted (CANON needs a ruling; DRAFTED needs the Beta or 3SL)",
         "graphic": "No contradiction erased by the graphic (each charted person’s conflict IDs printed on the node)"}
for k, v in names.items():
    w(f"| {v} | {'Pass' if not r[k] else 'FAIL: ' + '; '.join(r[k])} |")
qa = json.loads((ROOT / "out" / "qa_data.json").read_text()) if (ROOT / "out" / "qa_data.json").exists() else None
if qa:
    lq = qa["lineage"]
    w(f"| Every record claim and conflict field present in the printed record pages | {'Pass' if not lq['record_claims_missing'] else 'FAIL'} |")
    w(f"| Every node conflict ID present in the printed genealogy | {'Pass' if not lq['node_ids_missing'] else 'FAIL'} |")
w("")
(ROOT / "dist" / "LINEAGE_RECONSTRUCTION_REPORT.md").write_text("\n".join(out) + "\n")
print("written", len(out), "lines")
