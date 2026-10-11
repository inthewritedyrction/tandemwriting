# The Tandem Companion — Build 2 (For Their Entertainment / Remnia)

The standalone *For Their Entertainment* Companion. The print PDF, the QA report and the Remnian Lineage Reconstruction Report are in `dist/`; everything that generates them is in this folder. It uses the Build 1 engine and production rules (`../docs/production-rules.md`).

## Rebuild

```
python3 tools/build.py            # copy + record → out/book.html (blocks tagged for the paginator)
node tools/print.mjs              # Chromium: paginate, run layout QA, print dist/*.pdf
python3 tools/qa.py               # content integrity, corrections, references, writing space, claim sample, lineage checks
python3 tools/lineage_report.py   # dist/LINEAGE_RECONSTRUCTION_REPORT.md from the record
python3 tools/lineage_qa.py       # lineage data checks on their own (exits non-zero on any failure)
python3 lineage_map/build_map.py  # dist/Remnian_Lineage_Map.html: the settled lineage (2026-10-11)
node tools/print_map.mjs          # dist/Remnian_Lineage_Map.pdf: charts on 11x17 landscape, the rest on letter
```

You need Python 3 and Node with Playwright/Chromium. Fonts are local, in `assets/fonts/`.

## What's where

| Path | What it is |
| --- | --- |
| `src/content_master.md` | Locked Stage 3 copy (Content Master, Sep 26, 2026) |
| `src/production_master.md`, `src/audit.md` | Production rules and the source-authority audit (appendix slices, claim check) |
| `src/corrections.json` | Every change to the copy, quoted exactly: author corrections (A-), status (S-) and provenance (P-) corrections |
| `src/lineage.py` | **The Remnian lineage working record.** Persons and claims in five layers, parent links, the conflict ledger, open items, name checks, rejected claims, succession lanes, lane-D prompts. A derived record, not a source. |
| `src/new/` | The four files supplied 2026-10-09, with plain-text extractions (`tools/docx2txt.py`) |
| `src/approved_canvas/` | The approved Direction C artboards this build follows (IV.10 pages and the page-type templates) |
| `tools/build.py` | Parts I, II (FTE selection) and IV; IV.10 your pages; the IV.11 record; IV.25 working pages; FTE concordance; appendices |
| `tools/book.css`, `tools/paginate.js`, `tools/print.mjs` | Direction C styles, the paginator (spreads, working-section counters, keep-with-next rows), and printing |
| `tools/qa.py`, `tools/lineage_qa.py`, `tools/lineage_report.py` | QA and reports |
| `lineage_map/` | **The settled lineage (2026-10-11).** `settled.py` holds Dany's workbook answers, the four follow-up answers and the 3SL outline check, each line tagged with where it came from; `build_map.py` and `map.css` render the map and charts |
| `dist/` | `Tandem_Companion_Build2_FTE.pdf`, `QA_REPORT.md`, `LINEAGE_RECONSTRUCTION_REPORT.md`, `Remnian_Lineage_Map.html` and `.pdf` |

To change the copy, edit the Content Master and re-export it, or log a correction in `src/corrections.json`. To change the lineage record, edit `src/lineage.py`; `tools/lineage_qa.py` checks it. Layout never edits copy.
