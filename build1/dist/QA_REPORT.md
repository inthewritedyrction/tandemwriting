# Build 1 — 3SL Companion · QA Report

**File:** `Tandem_Companion_Build1_3SL.pdf` · 159 pages · US Letter (612 × 792 pt) · assembled 2026-10-09
**Source build:** `build1/` (rebuild with `python3 tools/build.py && node tools/print.mjs && python3 tools/qa.py`)

## Result

| Check | Result |
| --- | --- |
| Pagination | **Pass.** 159 pages, every section starts on a fresh page, and all 192 printed page references land on the right page (0 wrong). Section folios read `III.8 / 2 · 68`; the working section counts `1 OF 13` … `13 OF 13`. |
| Footer safe zone | **Pass.** 0 elements below y = 960 px (the bottom inch) on any page. Footers sit wholly inside the safe zone. 156 of the 158 footers fit on one line; the two queue pages (110–111) use the planned second footer row, still inside the safe zone. The title page has no footer. |
| Clipping / overlap | **Pass.** 0 margin overruns, 0 horizontally clipped cells or prompts, 0 oversize blocks, 0 orphaned captions or subheads, 0 empty pages. Tables split between rows, and the header row repeats on every continuation page. |
| Writing space | **Pass.** 266 writing areas (905 ruled lines at a 30 px / 7.9 mm pitch), 0 below their minimum. The smallest prompt has 5 lines (E1 Title, up from 2). Item A has 4 pages and Item D a full page. Nothing was shrunk to fit. |
| Status / source treatment | **Pass.** Every status marker prints as a shape + word badge (grayscale-safe), with the marker words kept. Provenance prints as SOURCE lines and right-column provenance; see-also chips carry page numbers. The 2026-10-09 tier ruling is applied in III.3 and on the III.20 working pages (details below). |
| Content integrity | **Pass.** 1,818 Content Master units (paragraphs, table cells, list items, callout bodies, source lines, references) checked against both the rendered page text and the PDF text layer: **0 missing**. |
| Random claim check | **Pass, 15 / 15.** Seeded sample (seed 20261009) of claims citing a TCD, each checked against the audit's ruling text. Results are listed below. |
| PDF | **Pass.** Text is searchable and selectable (36,730 words extracted; no text-less pages). Fonts are embedded TrueType only: Atkinson Hyperlegible, Barlow Condensed, and JetBrains Mono (static instances, so there are no Type 3 fonts and no system fallbacks). |

## Author correction applied

The ruling of 2026-10-09 on Underside tier status is logged in `src/corrections.json` and in Appendix A under "Author rulings without a TCD number".

- **III.3:**
  - A status box shows the three ruled lines: CANON (TCD-025 / TCD-026), DRAFTED (3SL ch. 10), SUPPORTED (3SL Full Worldbuilding).
  - The OPEN DEVELOPMENT "Fixed" line no longer lists the nine-tier count as fixed. It now reads: *"Crownlight and Dawnveil surface-level; fully underground by Ironcross; the attachment off Zenithia's side (TCD-025, TCD-026). Not ruled: the nine-tier count and order are CURRENT DRAFTED TEXT (ch. 10)."* This is the only change to Content Master wording.
- **III.20 working queue, row C:** marked CANON, DRAFTED and SUPPORTED.
- **III.20 Item C page:** carries the same three lines plus OPEN.

## Assembly decisions you should know about

None of these changes canon or status. Each one keeps a page consistent with the locked copy.

1. **III.20 Item A beat numbers now match III.15 as printed.** The approved artboards were drawn from the Production Master's 8-beat list. The Content Master's III.15 has 9 beats, because it adds "The gang leader is part of the confrontation." The changes:
   - "eight fixed beats" now reads "nine".
   - A1 now points to Beat 3 (was 2), A2 to Beat 4 (was 3), A3 to Beat 6 (was 5), and A7 to Beat 8 (was 7).
2. **The Item C tier table lists the nine tiers from III.3.** The approved artboard had a "Halflight" row. Halflight is a transfer station between Ashvein and Shadowmere, not a tier.
3. **Item D (crossing placement) has its own page**, per the known-issues list. The queue's "→ VII.12" pointer now points to Appendix A, because VII.12 resolves to III.20 itself in this volume.
4. **Design notes don't print.** The "(Design note: …)" lines in II.2 and II.16 are treated as production instructions.
   - II.2 keeps a placeholder schematic frame, per your answer.
   - II.16's four-band table carries the timeline. No drawn diagram was added.
5. **Writing space added without new prompts:**
   - a ruled working space plus a decision row under each of the 9 Part III OPEN DEVELOPMENT boxes;
   - blank rows on 12 tracker tables;
   - ruled NOTES fills where a Part III section ends with room to spare.

   Leftover space on a page always goes to that page's writing areas.
6. **One record diagram.** The III.3 vertical cross-section is drawn in relative order only, with no depths and no scale. The surface transition is marked OPEN.
7. **Volume apparatus written for this build.** It makes no canon claims:
   - title page;
   - About This Volume;
   - Contents;
   - the Continuity Room concordance lead, plus its "3SL information in this volume" column;
   - the one-line appendix intros.
8. **References outside the volume carry a dagger (†)** and print as dashed chips: IV.2, IV.5, IV.22, IV.24, V.4, V.16, V.17, VI.2, VI.3, VI.13, II.6, Part IV and Part V.
   - VII.1–VII.12 (as cited) and IV.14, IV.15 and IV.17 resolve to the 3SL Continuity Room concordance (p. 123).
9. **Appendices are 3SL slices.** They cover what this volume cites:
   - A: 50 TCDs, plus the two rulings that have no TCD number;
   - B: 14 conflicts;
   - C: 6 source files;
   - E: 16 of the 18 terms.

## Random claim check (seed 20261009)

| # | Page | Section | Claim (abridged) | Ruling(s) | Result |
| --- | --- | --- | --- | --- | --- |
| 1 | 102 | III.18 | Tiran: London Town's Bishop; advises and operationalizes the forfeit | TCD-042, TCD-052 | Pass |
| 2 | 34 | II.5 | All four traditions draw from one primordial substrate; distinct systems | TCD-035 | Pass |
| 3 | 62 | III.6 | Don't assume the NEUTRAL TRANSIT station is the TCD-027 crossing; no route has every capability | TCD-017, TCD-027 | Pass |
| 4 | 27 | II.2 | The four lands occupy multiple major landmasses in one world | TCD-025 | Pass |
| 5 | 40 | II.16 | 3SL climax: Remy's death, catastrophic Fire, Tiran's cleanup | TCD-002, TCD-063 | Pass |
| 6 | 18 | I.5 | The Sanctum's likely "Dyad" label for Katherine is incomplete | TCD-049 | Pass |
| 7 | 31 | II.4 | Awareness of other lands varies by nation, class, institution… | TCD-016 | Pass |
| 8 | 102 | III.18 | 3SL ends about two years before FTE/ADST | TCD-013 | Pass |
| 9 | 80 | III.11 | The tether is never evidence of consent | TCD-044 | Pass |
| 10 | 35 | II.5 | The Sanctum, within its semi-autonomous magical-regulation domain | TCD-041 | Pass |
| 11 | 18 | I.5 | Six knowledge levels; none implies another | TCD-016 | Pass |
| 12 | 102 | III.18 | Silas/Isola explicitly romantic, not a settled couple, separate paths; tether open | TCD-044 | Pass |
| 13 | 35 | II.5 | Seal Song ≠ Drowned Canticle; Dren compatibility ≠ Leviathan identity | TCD-028, TCD-064 | Pass |
| 14 | 40 | II.16 | Elias's years-long double life as Thorne; compromise of research and dream functioning | TCD-032, TCD-062 | Pass |
| 15 | 38 | II.14 | No echo from Selah's Prayer to Katherine's; shared ancestry, not causation | TCD-023, TCD-048 | Pass |

## Carried forward, not resolved

- Part III's own source note still prints as written: the placements in chs. 16, 18, 20 and 22 are "by sequence and should be verified in a single full read."
- The known-issues entries for IV.10 in `docs/production-rules.md` belong to FTE and are outside Build 1.
- The editable deliverable is the HTML/CSS source build that generated the PDF (`build1/`). No separate DOCX was produced.
