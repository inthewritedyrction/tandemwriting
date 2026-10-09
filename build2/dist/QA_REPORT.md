# Build 2 — FTE / Remnia Companion · QA Report

**File:** `Tandem_Companion_Build2_FTE.pdf` · 268 pages · US Letter (612 × 792 pt) · assembled 2026-10-09
**Source build:** `build2/`. Rebuild with:

```
python3 tools/build.py && node tools/print.mjs && python3 tools/qa.py && python3 tools/lineage_report.py
```

**Companion report:** `LINEAGE_RECONSTRUCTION_REPORT.md` covers the lineage sources, conflicts, and rejected claims.

## Result

| Check | Result |
| --- | --- |
| Pagination | **Pass.** 268 pages. Every section starts on a fresh page. All 276 printed page references land on the right page (0 wrong). Working sections count their own pages: IV.10 your pages 1–11, lineage record 1–48, IV.25 working pages 1–23. |
| Footer safe zone | **Pass.** 0 elements below y = 960 px (the bottom inch) on any page. 79 footers use the planned second row inside the safe zone. These are mostly working pages, where MS CHECK shares the footer with a long breadcrumb. Type never shrinks. |
| Clipping / overlap | **Pass.** 0 margin overruns, 0 clipped cells, chips, prompts or genealogy nodes, 0 oversize blocks, 0 orphaned captions, 0 empty pages. Tables split between rows and repeat their header row. A person's header row in the ledger never ends a page. |
| Writing space | **Pass.** 369 writing areas (1,609 ruled lines at a 30 px pitch), 0 below their minimum. The smallest prompt has 5 lines. The working sections alone hold 897 lines. Every Part IV OPEN DEVELOPMENT box has a ruled working space and decision row. Nothing was shrunk to fit. |
| Status / source treatment | **Pass.** Every status prints as a shape + word badge, grayscale-safe. Genealogy boxes use shape + letter, with a key on the page. Provenance prints as SOURCE lines and right-column provenance. |
| Content integrity | **Pass.** 2,558 Content Master units checked against the rendered page text and the PDF text layer: **0 missing**. The two design notes (II.13, II.16) are production instructions and don't print. |
| Corrections | **Pass.** 12 logged corrections. Each replacement prints, and each replaced text is gone, except the one that appends a note. Details below. |
| Instructed page fixes | **Pass.** IV.10 failure-beat prompt replaced. The old “chs. 30–39 rewrite” prompt is gone. “Check the five layers in IV.11 (Biological, Legal, Recorded, Public, Succession)” prints; “four lanes” is gone. There are no “[Stage 3 · source pending]” placeholders. Zephyr’s registration prints as CONFLICT. “Seventeen” is no longer attached to the TCDs. |
| Lineage checks | **Pass.** Parent/child consistency, duplicates and name variants, succession vs biology, provenance, no silent promotion, graphic vs record. Every record claim and every node conflict ID is present in the printed pages. See the lineage report, section 8. |
| Random claim check | **Pass, 15 / 15.** Seeded sample (seed 20261009) of TCD-citing claims from Parts I, II and IV, each checked against the audit’s ruling text. Listed below. |
| PDF | **Pass.** Searchable text (59,073 words; no text-less pages). Fonts are embedded TrueType only: Atkinson Hyperlegible, Barlow Condensed and JetBrains Mono. No Type 3 fonts and no system fallbacks. |

## Corrections applied

All are logged in `src/corrections.json` with the exact text found and replaced. Author rulings without a TCD number are also listed in Appendix A.

**Author corrections, 2026-10-09**

- **A-2026-10-09-IV2 (IV.2).** The opening sentence now reads: “Remnia is an empire on its own continental landmass, separated from Somnoria by ocean; the Crown sits at the highest public civil/dynastic level of the Remnian sovereignty structure. [CANON] TCD-025, TCD-041. The Beta gives it seventeen provinces and confirms the count in three places …(CURRENT DRAFTED TEXT).”
  - A status box at the top of IV.2 shows the same split.
  - *Note:* TCD-041’s own text does say “Remnia is a centralized empire with overlapping centers of authority,” so “centralized” would be supported if cited to TCD-041. The approved sentence was used as written, without it.
- **A-2026-10-09-IV3 (IV.3).** The Military row’s ruled column no longer carries a CANON badge. It now says the military isn’t placed by TCD-041, which rules the layered sovereignty framework, and that the structure is CURRENT DRAFTED TEXT (the Old Prosperity command table that follows).

**Status and provenance corrections from the lineage reconstruction**

- **S-IV11-lucia-death (IV.11).** Lucia’s cause of death moves from SUPPORTED to CONFLICT. The 31–39 car accident and the Before Story Start “nighttime medical crisis” are now both quoted (record LC-16).
- **P-IV11-eyes, P-IV11-succession, P-IV12-publicity, P-IV22-somnoria (IV.11, IV.12, IV.22).** These claims were attributed to the unaudited *Imperial Lineage*. All of them appear in the audited *Remnian Timeline Before Story Start*, so they now cite it, with the *Imperial Lineage* noted as repeating it. **No status changed:** the IV.12 publicity question stays OPEN, and Duke of Somnoria stays a knowledge flag.
- **P-IV12-audit-sentence (IV.12).** “The audit records a public-scandal framing in the Remnian Timeline Before Story Start, which isn’t in this Project” is now “The audit flags that file’s public-scandal framing as unresolved.” The file is now in the Project.
- **P-IV11-source, P-IV12-source, P-IV22-source.** The source lines name the files used and their treatment.
- **P-IV-source-note (Part IV source note).** A dated Build 2 note says that FTE 2025 FINAL, both Remnian timelines and *Full 4 Series Flesh Out* have since been supplied and are used claim by claim. The original sentence stays.

No other Part IV prose was changed.

## Assembly decisions you should know about

None of these changes canon or status.

1. **IV.10 your pages (approved artboards W-ref-IV10, W-IV10-2 … 6) run 11 pages, not 6.** They flowed forward rather than compress.
   - **Reference page (Katherine vs Zephyr).** The table runs to a second page. The carried question has 6 lines and points to the failure-beat page (the artboard pointed to /2).
   - **Zephyr’s column** is pre-filled only where IV.10 / IV.9 speak:
     - CANON (TCD-049): modern Fire/Frost Dyad; Fire as one of two modern channels; the Sanctum’s “Dyad” is correct.
     - SUPPORTED (31–39): since thirteen.
     - DRAFTED: the tundra chs. 17–18.
     - CONFLICT: registration.
     - Dominant, Suppression and Open stay ruled and blank. Page 2’s “complete Zephyr’s column” table covers exactly those fields, plus registration.
   - **Failure-beat spread.** The Failure Beat and Draft the Beat stay facing (pp. 92–93). Prompt 3 (“what the beat must not imply”) moved to the head of the right-hand page so the left page holds the ruling and prompts 1–2 without overflowing. Prompt 1 is tied to TCD-058 and the 2026-09-26 clarification and points to IV.24. It doesn’t invite Heart’s Mirror placement.
2. **Spreads land on facing pages.** Where the preceding page count would put a spread’s left page on the right, a full ruled NOTES page fills the gap (pp. 91 and 105).
3. **The lineage record (48 pages) follows IV.11.** It has four lanes:
   - A: genealogy spread (pp. 106–107);
   - B: ledger by person and layer, plus collateral lines and name checks;
   - C: succession lane, current and historical, kept separate from the tree;
   - D: the conflict ledger in your six columns, the rejected-claims table, then a ruled working block for each of the 21 conflicts and 5 open items.
4. **IV.25 working pages (23 pages).**
   - The queue repeats IV.25’s Fixed and Decide-by columns and adds SAFE TO DEFER / DECIDED boxes and a WORK ON page reference for every item.
   - The eight Duel blockers each get their own pages: the decisive act, Melena’s investigation, Challenge Six rules, Challenge Seven, the Prayer for Atlas, Atlas’s injury, forfeit procedure, and verification. The Frost failure points to the IV.10 spread instead of duplicating it.
   - Non-blockers are on two grouped pages. Lineage items point to their lane-D blocks.
5. **Prompts written for this volume.** The prompts in lane D and on the IV.25 blocker and grouped pages are apparatus. Each one turns an “Undecided” cell or a logged conflict into a specific question. They state no canon.
   - Two tie-in notes cite the new files as evidence: “Regnant” used for faction leaders in BSS and TLE, and Rovencia in TLE’s seventeen provinces. Both keep their SUPPORTED or LEGACY status.
6. **Writing space added without new prompts:**
   - a ruled working space plus a decision row under every Part IV OPEN DEVELOPMENT box;
   - blank rows on 11 Part IV tracker tables;
   - ruled NOTES fills where a Part IV section ends with room to spare.
7. **Volume apparatus written for this build:** title page, About This Volume, Contents, the concordance lead and its right-hand column, the record’s introduction and source key, and the one-line appendix intros. None of it makes canon claims.
8. **References outside the volume carry a dagger (†):** III.7, III.8, III.19, V.4, V.16, V.17, VI.2, VI.3, VI.13 and Part V. VII.1, VII.2, VII.5, VII.7, VII.8, VII.10, VII.12, Part VII, III.3, III.13–III.16, III.18, III.20 and Part III resolve to the FTE Continuity Room concordance (p. 216).
9. **Appendices are FTE slices:**
   - A: 60 TCDs cited, plus four rulings without a TCD number: the 2026-09-26 TCD-058 clarification, the 2026-10-09 IV.2 and IV.3 corrections, and the restated lineage anchor.
   - B: 28 register rows, plus the 21 lineage conflicts.
   - C: the 25 sources this volume actually uses, each with how Build 2 reached it, plus the unaudited *Imperial Lineage*.
   - E: the 15 register terms used.
10. **Content Master ambiguity, carried as is.** IV.18 says Dalia appears on the page in *31–39* only, while IV.19 marks “Dalia’s son; brother of …” as CURRENT DRAFTED TEXT and CB. The lineage record keeps Dalia as the sons’ mother at SUPPORTED, the safer reading. The brothers themselves are DRAFTED.
11. **Design notes don’t print.** II.2 keeps the schematic placeholder frame. II.16’s four-band table carries the timeline.

## Sources this build couldn’t read

The FTE Beta, *Welcome to Remnia*, the *Character Bible*, *FTE 31–39*, *Chapter 29.docx*, *The Challenges FTE Year*, the *49th Placements*, the *Elemental Factions* file, the 3SL draft and *The Imperial Lineage* aren’t in this session. Their facts are taken as the Content Master records them. Appendix C marks each one.

The four files supplied on 2026-10-09 were read directly:

- both Remnian timelines in full;
- FTE 2025 FINAL and *Full 4 Series Flesh Out* searched for every lineage passage.

## Random claim check (seed 20261009)

| # | Page | Section | Claim (abridged) | Ruling(s) | Result |
| --- | --- | --- | --- | --- | --- |
| 1 | 47 | II.16 | ADST climax: the organization’s attempted Network rupture; first Convergence threshold, T0 | TCD-056, TCD-060 | Pass |
| 2 | 188 | IV.24 | Katherine Frost-dominant until the climax; Fire only on catastrophic Frost failure | TCD-049, TCD-058 | Pass |
| 3 | 35 | II.6 | Cassius’s Labyrinth scar regulates bond synchronization | TCD-030 | Pass |
| 4 | 77 | IV.8 | Katherine is this Tournament’s Conqueror; Atlas and Tiran draw | TCD-034 | Pass |
| 5 | 29 | II.4 | Awareness of other lands varies by nation, class, institution… | TCD-016 | Pass |
| 6 | 47 | II.16 | 3SL climax: Remy’s death, catastrophic Fire, Tiran’s cleanup | TCD-002, TCD-063 | Pass |
| 7 | 51 | IV.1 | The Beta is the book | TCD-001 | Pass |
| 8 | 32 | II.5 | Six Disciplines SUPPORTED; Graveshand outside them | TCD-004 | Pass |
| 9 | 60 | IV.3 | London Town’s royal house in conflict; the Crown directly controls London Town | TCD-041 | Pass |
| 10 | 81 | IV.9 | She protects first; saves Melena from her own moral arc | TCD-050 | Pass |
| 11 | 69 | IV.6 | “Six challenges” vs the seven-challenge design | TCD-007 | Pass |
| 12 | 155 | IV.13 | Mid-fight magical realization superseded by the staged reveal | TCD-050 | Pass |
| 13 | 188 | IV.24 | Katherine’s reason: her own moral arc, not only sisterhood | TCD-050 | Pass |
| 14 | 18 | I.5 | Melena enters the Duel with suspicion and no proof | TCD-050 | Pass |
| 15 | 188 | IV.24 | Melena suspects first; records prove; Michelle explains | TCD-050 | Pass |

## Carried forward, not resolved

- The Part IV source note still says the Beta was read by chapter map, so placements “should be verified in a full read.”
- The 21 lineage conflicts and 5 open items are unresolved by design. Each has a working block in lane D, and none was settled by the graphic or the ledger.
- The editable deliverable is the HTML/CSS/Python source build that generated the PDF (`build2/`). No separate DOCX was produced.
