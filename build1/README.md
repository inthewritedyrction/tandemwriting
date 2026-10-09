# The Tandem Companion — Build 1 (3SL / Underside)

The standalone *3 Shadowmere Lane* Companion. The print PDF and the QA report are in `dist/`; everything that generates them is in this folder.

## Rebuild

```
python3 tools/build.py      # copy → out/book.html (blocks tagged for the paginator)
node tools/print.mjs        # Chromium: paginate, run layout QA, print dist/*.pdf
python3 tools/qa.py         # content-integrity, references, writing space, claim sample
```

You need Python 3 and Node with Playwright/Chromium. Fonts are local, in `assets/fonts/`.

## What's where

| Path | What it is |
| --- | --- |
| `src/content_master.md` | Locked Stage 3 copy (export of *The Tandem Companion — Content Master*, Sep 26, 2026) |
| `src/production_master.md` | Production rules, page types, Part VII purposes, A7 terminology |
| `src/audit.md` | Tandem Source Authority Audit — Working Record (appendix slices, claim check) |
| `src/corrections.json` | Explicit author corrections applied to the copy, quoted exactly |
| `src/approved_canvas/` | The approved Direction C artboards this build follows |
| `tools/build.py` | Parses Parts I, II (3SL selection) and III; III.20 working pages; Continuity Room concordance; appendices |
| `tools/book.css` | Direction C styles; 30 px handwriting pitch; 96 px footer safe zone |
| `tools/paginate.js` | Flows blocks into Letter pages; splits tables with repeated headers; fills writing space; numbers pages; layout QA |
| `tools/print.mjs` | Renders and prints the PDF; also saves `out/book.paginated.html` |
| `tools/qa.py` | Post-print QA → `out/qa_data.json` |
| `dist/` | `Tandem_Companion_Build1_3SL.pdf`, `QA_REPORT.md` |

To change copy, edit the Content Master and re-export it, or log an author correction in `src/corrections.json`. Layout never edits copy.
