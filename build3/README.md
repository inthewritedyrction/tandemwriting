# The Tandem Companion — Build 3 (TKC)

TKC Volume One, The World Dossier, assembled and print-ready: Parts I–XI plus a canon register.

- `dist/TKC_Volume_One_World_Dossier.pdf`: the print copy (Letter, white page, ITWD pink detailing per the Print Direction), with portrait frames, map and diagram plates, and a working page after every part.
- `volume_one/TKC_Volume_One_World_Dossier.md`: the same volume as plain markdown, for pasting into the Claude Doc or editing.
- `volume_one/II3_Deep_dives.md`, `III_People_of_the_Text.md`, `IV_Jesus_Kingdom_Prayer.md`, `V_Christianity_and_Power.md`: the four sections written in this build, one per pending block in the Claude Doc. `volume_one/parts/` holds their pieces.

## Rebuild

```
python3 tools/pdf2md.py src/intake/TKC_Volume_One_The_World_Dossier_rev15.pdf volume_one/from_doc/rev15.md   # only if the doc export changes
python3 tools/assemble.py                         # rev 15 + the four sections → the volume markdown, canon fixes, plates, register
python3 tools/build_print.py out/toc_pages.json   # markdown → out/volume_one.html
node tools/print.mjs                              # Chromium → dist/*.pdf
python3 tools/toc_pages.py                        # read back where each part landed, then rerun the two lines above
```

Needs Python 3 with `markdown` and `pdfplumber`, and Node with Playwright/Chromium. Fonts (EB Garamond, Cinzel, Jost) are local in `assets/fonts/`.

## Sources in `src/intake/`

| File | What it is |
| --- | --- |
| `TKC_Companion_Final_Rulings.dc.html` | Final Rulings, FR 0–44. Outranks everything. |
| `TKC_Companion_Print_Direction.pdf` | The print look |
| `TKC_Volume_One_The_World_Dossier_rev15.pdf` | The Claude Doc at rev 15 (intro, Parts I–II.2, VI–XI) |
| `TKC_Volume_One_The_World_Dossier.pdf` | An earlier export (world parts only) |
| `Old_Companion_p001-085.pdf`, `p086-170`, `p171-251` | The old Companion (TKC workbook), 251 pages |
| `Writing_Rules.docx`, `Timeline_Updated.docx`, `The_Covenant_Trials_Updated.docx`, `The_Dominions_Update.docx`, `Men_In_The_Covenant_Empire.docx` | Source files, with text extractions in `txt/` |

## The Volume One workbook

`dist/TKC_Volume_One_Workbook.pdf` is the printed workbook: 581 pages at 8.5 × 11, white with the ITWD pink.

- The source is in `workbook/units/*.tkc`, one file per section. They're read in filename order.
- `workbook/wb.py` renders the units to `out/workbook.html`, and `workbook/wb.css` holds every page style.
- `workbook/wb_print.mjs` fills the writing lines and checks every page for overflow. It moves an overflowing prompt onto a facing working page, through `out/continuations.json`, and prints the PDF.
- `workbook/gen_dominions.py` regenerates the Part VII unit.

To rebuild:

```
rm -f out/continuations.json
for i in 1 2 3; do python3 workbook/wb.py && node workbook/wb_print.mjs out/sample.pdf; done
node workbook/wb_print.mjs
```
